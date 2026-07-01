---
name: parallel-debug
description: This skill should be used when the user invokes /debugging-workflow:parallel-debug, asks to "debug in parallel", "try all hypotheses at once", "spawn multiple agents for this bug", "investigate multiple root causes", "parallel hypothesis testing", "parallel investigation", "I can't figure out what's causing this", "investigate from multiple angles", "I have multiple theories about this bug", or reports a complex or intermittent bug where the root cause is unclear and multiple theories need testing simultaneously.
argument-hint: "[error message, stack trace, or bug description]"
allowed-tools: ["Read", "Write", "Edit", "Bash", "Grep", "Glob", "TaskCreate", "TaskUpdate", "Agent"]
license: MIT
---

# Parallel Debug Workflow

This skill is the **orchestrator**. It owns everything the individual agents (`hypothesis-investigator`, `hypothesis-arbitrator`) do not: session setup, isolation, collecting reports, deciding whether arbitration is even needed, applying the final result, and cleaning up afterward.

## When to Use

Use `parallel-debug` when:
- The root cause is genuinely unclear (multiple plausible theories coexist)
- The bug is intermittent or hard to reproduce consistently
- A previous sequential debug pass was inconclusive
- Time pressure demands concurrent investigation over sequential elimination

For bugs with an obvious root cause, a direct sequential investigation is faster and uses fewer resources.

---

## Step 0 — Session setup

1. Create a session directory: `.claude/debug-sessions/{session_id}/` where `session_id` is a short timestamp-based slug (e.g. `20260701-1432`).
2. Confirm the repo has no uncommitted changes on the current branch before proceeding. If it does, ask the user whether to stash them first — do not silently stash or discard user work.
3. Record the base commit SHA in `.claude/debug-sessions/{session_id}/base.txt`. Every investigator worktree and the final merge will be diffed against this SHA.
4. Read `.claude/debugging-workflow.local.md` if it exists. Parse the YAML frontmatter:
   - `max_parallel_agents` — integer 2–5, default `4`
   - `time_budget_minutes` — integer 1–15, default `5`
   - `hypothesis_count` — integer 2–4, default `3`

   Compute the **iteration budget** from `time_budget_minutes` using the table in `references/report-format.md` (default with `time_budget_minutes: 5` → 3 iterations).

---

## Step 1 — Generate hypotheses

Before spawning agents, produce a list of `hypothesis_count` (default: 3) distinct, plausible root-cause hypotheses for the reported bug (based on the error message, stack trace, and a quick read of the relevant code). Each hypothesis gets a short id: `h1`, `h2`, `h3`, ...

Consult `references/hypothesis-catalog.md` to match the error symptom to known patterns and select diverse, falsifiable hypotheses.

If you cannot articulate at least 2 genuinely distinct hypotheses, stop and tell the user: the bug likely has a single identifiable cause — ask them to provide more context or investigate it directly.

---

## Step 2 — Create isolated worktrees

For each hypothesis `hN`:

```bash
git worktree add .claude/debug-sessions/{session_id}/hN -b debug/{session_id}/hN {base_sha}
```

Each `hypothesis-investigator` instance is given exactly one hypothesis and one worktree path. It must never touch files outside its assigned worktree. Launch all instances in parallel (not sequentially).

If worktree creation fails (dirty tree, disk space, etc.), stop before spawning any investigator and report the error — do not partially spawn agents into a broken session state.

---

## Step 3 — Collect reports

Each `hypothesis-investigator` writes its YAML report to `.claude/debug-sessions/{session_id}/hN/report.yaml`.

Spawn all agents in a single message via `subagent_type: "debugging-workflow:hypothesis-investigator"`. Pass each agent a prompt with this structure:

```
Bug description: [full error message and symptom]
File/line: [path:line where error originates]
Language: [detected language — Dart, Rust, TypeScript, Python, Go, etc.]
Hypothesis id: hN
Hypothesis mechanism: [one sentence describing what to test]
Iteration budget: [iteration_budget from Step 0] attempts
Worktree path: .claude/debug-sessions/{session_id}/hN
Report output path: .claude/debug-sessions/{session_id}/hN/report.yaml
```

Wait for all instances to finish. If an agent times out or crashes, treat it as `test_result: not_run` for that hypothesis and proceed with the remaining ones — still clean up its worktree in Step 7. Read all `report.yaml` files into memory before proceeding.

---

## Step 4 — Decide whether arbitration is needed

Do NOT call `hypothesis-arbitrator` unconditionally. Check first:

- **Exactly one report passes** → skip arbitration. Go directly to Step 5 with that hypothesis selected.
- **Zero reports pass** → skip arbitration. Go to Step 6b.
- **Two or more reports pass** → call `hypothesis-arbitrator` (`subagent_type: "debugging-workflow:hypothesis-arbitrator"`) with all passing reports as input.

This gating keeps the common case cheap — arbitration only runs when there is something to arbitrate.

---

## Step 5 — Apply the final result

Based on the outcome (single passing hypothesis from Step 4, or the arbitrator's `ONE_WINNER`/`MERGE_FIXES` decision):

1. Check out the branch the user was originally on.
2. Apply the `final_diff` (or the single winning `fix_diff`) with `git apply`.
3. Re-run the affected test command one more time on the main branch — a diff that passed in an isolated worktree can still fail once merged with the real working tree state. If it fails, revert the apply and escalate to the user with the specific failure — do not retry silently.
4. Report to the user: which hypothesis/hypotheses were applied, and the arbitrator's `reasoning` if arbitration ran.

---

## Step 6a — Escalation (arbitrator returns ESCALATE_TO_USER)

1. Present the conflicting hypotheses to the user: each claim, its evidence, and why they conflict (from `reasoning`).
2. Ask the user to pick one, request a merge attempt anyway, or provide additional context that resolves the ambiguity.
3. Once the user responds, treat it as a new turn. Apply the chosen fix via the Step 5 procedure. If the user provides new information instead of picking, treat it as input to a fresh, narrower investigation rather than looping the same agents on the same evidence.

---

## Step 6b — No hypothesis passed

Report which hypotheses were tried and why each failed (from their `test_result`/evidence). Ask whether to:
- Broaden the hypothesis list and retry
- Investigate the bug manually, starting from the most promising lead
- Provide additional reproduction steps or context

---

## Step 7 — Cleanup (always runs, regardless of outcome)

```bash
for hN in <all hypothesis ids>; do
  git worktree remove .claude/debug-sessions/{session_id}/hN --force
  git branch -D debug/{session_id}/hN
done
```

Run this even on the escalation path, once the user's final choice has been applied. Keep `.claude/debug-sessions/{session_id}/*.yaml` reports on disk for audit purposes — only remove the git worktrees and branches.

---

## Failure modes to handle explicitly

- **Investigator times out or crashes** — treat as `test_result: not_run`, proceed with remaining ones, still clean up its worktree in Step 7.
- **Near-duplicate hypotheses** — if the arbitrator's `reasoning` indicates two hypotheses were the same claim reworded, note this to the user as a process observation, not just a decision.
- **Worktree creation fails** — stop before spawning any investigator and report the error; do not partially spawn agents into a broken session state.

---

## Additional Resources

- **`references/hypothesis-catalog.md`** — Full hypothesis library organized by symptom; used in Step 1
- **`references/report-format.md`** — Evidence report spec and ranking algorithm
- **`examples/debugging-workflow.local.md`** — Complete settings template
- **`../../agents/hypothesis-investigator.md`** — Per-hypothesis investigation agent
- **`../../agents/hypothesis-arbitrator.md`** — Conflict-resolution agent invoked in Step 4 when multiple hypotheses pass
