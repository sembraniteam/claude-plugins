---
name: parallel-debug
description: This skill should be used when the user invokes /debugging-workflow:parallel-debug, asks to "debug in parallel", "try all hypotheses at once", "spawn multiple agents for this bug", "investigate multiple root causes", "parallel hypothesis testing", "parallel investigation", "I can't figure out what's causing this and have a few theories", "investigate from multiple angles", "I have multiple theories about this bug", or reports a complex or intermittent bug where the root cause is unclear and multiple theories need testing simultaneously.
argument-hint: "[error message, stack trace, or bug description]"
allowed-tools: ["Read", "Write", "Edit", "Bash", "Grep", "Glob", "Agent"]
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

1. Create a session directory: `.claude/debug-sessions/{session_id}/` where `session_id` is a short timestamp-based slug (e.g. `20260701-1432`). If the project's `.gitignore` does not already exclude `.claude/debug-sessions/`, tell the user to add it — otherwise session directories and reports show up as untracked files in `git status`. "No uncommitted changes" in step 2 refers only to tracked files; untracked leftover session directories from a prior run do not block a new session, but should still be cleaned up if stale.
2. Confirm the repo has no uncommitted changes to tracked files on the current branch before proceeding. If it does, ask the user whether to stash them first — do not silently stash or discard user work.
3. Record the base commit SHA in `.claude/debug-sessions/{session_id}/base.txt`. Every investigator worktree and the final merge will be diffed against this SHA.
4. Read `.claude/debugging-workflow.local.md` if it exists. Parse the YAML frontmatter:
   - `max_parallel_agents` — integer 2–5, default `4`; caps how many `hypothesis-investigator` agents run concurrently (see the batching rule in Step 3), independent of `hypothesis_count`
   - `time_budget_minutes` — integer 1–15, default `5`, approximate time budget per agent (agents run in parallel, so this is not a total)
   - `hypothesis_count` — integer 2–4, default `3`

   Compute the **iteration budget** from `time_budget_minutes` using the table in `references/report-format.md` (default with `time_budget_minutes: 5` → 3 iterations).

---

## Step 1 — Generate hypotheses

Before spawning agents, produce a list of `hypothesis_count` (default: 3) distinct, plausible root-cause hypotheses for the reported bug (based on the error message, stack trace, and a quick read of the relevant code). Each hypothesis gets a short id: `h1`, `h2`, `h3`, ...

Consult `references/hypothesis-catalog.md` to match the error symptom to known patterns and select diverse, falsifiable hypotheses.

If fewer than 2 genuinely distinct hypotheses can be articulated, stop and tell the user: the bug likely has a single identifiable cause — ask them to provide more context or investigate it directly.

---

## Step 2 — Create isolated worktrees

For each hypothesis `hN`:

```bash
git worktree add .claude/debug-sessions/{session_id}/hN -b debug/{session_id}/hN {base_sha}
```

Each `hypothesis-investigator` instance is given exactly one hypothesis and one worktree path. It must never touch files outside its assigned worktree. See Step 3 for how instances are batched and spawned.

If worktree creation fails (dirty tree, disk space, etc.), stop before spawning any investigator and report the error — do not partially spawn agents into a broken session state.

---

## Step 3 — Collect reports

Each `hypothesis-investigator` writes its YAML report to `.claude/debug-sessions/{session_id}/hN.report.yaml` — a sibling of the `hN/` worktree directory, not inside it. This matters: Step 7 deletes the `hN/` worktree entirely, so a report written inside it would be destroyed before it could be read for audit.

Spawn agents in batches of at most `max_parallel_agents` (from Step 0) — this is that setting's actual effect: capping how many investigators run concurrently, independent of `hypothesis_count`. If `hypothesis_count` ≤ `max_parallel_agents` (the common case), there is only one batch: spawn all agents in a single message via `subagent_type: "debugging-workflow:hypothesis-investigator"`. If `hypothesis_count` > `max_parallel_agents`, spawn the first `max_parallel_agents` hypotheses in one message, wait for that batch to finish, then spawn the remaining hypotheses as the next batch the same way. Pass each agent a prompt with this structure:

```
Bug description: [full error message and symptom]
File/line: [path:line where error originates]
Language: [detected language — Dart, Rust, TypeScript, Python, Go, etc.]
Hypothesis id: hN
Hypothesis mechanism: [one sentence describing what to test]
Iteration budget: [iteration_budget from Step 0] attempts
Worktree path: .claude/debug-sessions/{session_id}/hN
Report output path: .claude/debug-sessions/{session_id}/hN.report.yaml
```

Wait for all instances across all batches to finish. If an agent times out or crashes, no `hN.report.yaml` was ever written for it — synthesize a minimal in-memory record with `test_result: not_run`, `status: unconfirmed`, and the remaining qualitative fields set to "N/A", and proceed with the remaining hypotheses — still clean up its worktree in Step 7. Read all `hN.report.yaml` files into memory before proceeding.

While reading each report, validate it against the schema in the investigator's Phase 4 (`../../agents/hypothesis-investigator.md`): all required fields present, and `status`/`confidence`/`initial_test_result`/`test_result` hold only their documented enum values. A malformed or incomplete report is treated the same as a crashed agent — downgrade it to `status: unconfirmed` / `test_result: not_run` rather than interpreting missing or malformed fields charitably. The orchestrator does not guess at what a broken report meant.

---

## Step 4 — Decide whether arbitration is needed

Do NOT call `hypothesis-arbitrator` unconditionally. A report counts as **passing** for this gate only when all three raw fields hold: `status: confirmed` AND `test_result: pass` AND `initial_test_result: fail`. Check the raw fields directly rather than trusting `status` alone — see `references/report-format.md` ("Status Definitions") for why a report can claim `status: confirmed` or `status: inconclusive` without actually satisfying this pairing. Either case fails this gate exactly like a plain `unconfirmed` report would; flag the inconsistency when presenting results rather than silently correcting or trusting it. Such a report is never auto-applied, but it still appears in the Final Ranked Report. Check first:

- **Exactly one report passes** → skip arbitration. Go directly to Step 5 with that hypothesis selected.
- **Zero reports pass** → skip arbitration. Go to Step 6b (this includes the case where only `inconclusive` and/or `unconfirmed` reports exist).
- **Two or more reports pass** → call `hypothesis-arbitrator` (`subagent_type: "debugging-workflow:hypothesis-arbitrator"`) with all passing reports as input, plus the `base_sha` recorded in Step 0. The arbitrator needs `base_sha` to re-verify each hypothesis's evidence citations against the pre-fix state of the code (see the arbitrator's Step 2) — the worktrees themselves already contain each investigator's applied fix by this point, so reading `worktree_path` directly would show post-fix code, not the buggy pattern the evidence describes.

This gating keeps the common case cheap — arbitration only runs when there is something to arbitrate.

---

## Step 5 — Apply the final result

Based on the outcome (single passing hypothesis from Step 4, or the arbitrator's `ONE_WINNER`/`MERGE_FIXES` decision), identify the winning hypothesis id(s) and look up each one's `commit_sha` from the `hN.report.yaml` already read in Step 3 — investigators commit their fix (source + test) to their own worktree branch, so the commit is the unit of application, not the `fix_diff` text.

1. **Verify the artifacts before trusting them** (see `references/apply-verification.md` for why each check below exists). For each winning hypothesis id:
   - Confirm the commit actually exists: `git cat-file -e <commit_sha>^{commit}`. If it does not resolve, do not cherry-pick it — escalate to the user with the hypothesis id and the fact that its commit reference is invalid.
   - Confirm the commit's actual contents are consistent with the report: `git show --name-only <commit_sha>` should list exactly the paths touched by `fix_diff`, include the report's `test_file`, and contain none of the paths in `side_effects_flagged` — those were deliberately left unstaged by the investigator (see Phase 3 of `../../agents/hypothesis-investigator.md`), so their presence in the commit is a failure, not consistency. `test_scope_files` describes what the test run *exercised*, not what the commit should *contain* (a test can exercise unchanged modules), so it is not part of this check — coverage adequacy against `test_scope_files` is the arbitrator's Step 1 concern *when arbitration runs*. On the single-passing-hypothesis path (no arbitration), nothing re-checks `test_scope_files` plausibility; the spot-check in the next bullet covers citation accuracy instead, which is a related but different guarantee. If any of these don't hold, escalate rather than apply silently.
   - **If this hypothesis reached Step 5 without going through arbitration** (the single-passing-report path from Step 4), spot-check at least one evidence citation yourself: run `git show <base_sha>:<evidence[0].file>` and confirm `evidence[0].excerpt` actually appears at `evidence[0].line`. If the citation doesn't check out, treat the report as unverified: do not apply it, and escalate to the user with what the citation actually showed.
2. Confirm the main working tree is still on the branch the user was originally on — it never left, since all investigation happened in separate worktrees.
3. Record `pre_apply_sha=$(git rev-parse HEAD)` before cherry-picking anything. This is the single rollback point for the rest of this step — use it instead of computing how many commits to unwind, regardless of whether the failure happens on the first cherry-pick, the second (`MERGE_FIXES`), or the test re-run.
4. Cherry-pick the winning commit(s): `git cherry-pick <commit_sha>`. For `MERGE_FIXES` with two selected hypotheses, cherry-pick both SHAs in sequence.
   - If any cherry-pick in the sequence reports a conflict: run `git cherry-pick --abort` (this only cancels the pick currently in progress — it does NOT undo an earlier commit in the same sequence that already applied cleanly), then run `git reset --hard $pre_apply_sha` to return the branch to exactly its pre-apply state. Escalate to the user with the conflicting hypothesis ids — do not hand-resolve the conflict yourself.
5. Re-run the tests one more time on the main branch — a commit that passed in an isolated worktree can still fail once merged with the real working tree state. Since the investigator(s) committed the test file(s) alongside the fix(es), they are now present on the main branch and runnable.
   - **Single hypothesis (Step 4 single-pass or arbitrator `ONE_WINNER`)**: re-run that hypothesis's `test_command`.
   - **`MERGE_FIXES`**: re-run both selected hypotheses' `test_command`s, then the full test suite — two independent fixes can interact even when each `test_command` passes on its own, and the full suite is what actually surfaces that interaction.

   If any test fails, run `git reset --hard $pre_apply_sha` (the same rollback point from step 3, regardless of how many commits were applied) and escalate to the user with the specific failure — do not retry silently.
6. Report to the user using the **Final Ranked Report** format from `references/report-format.md`, built entirely from the `hN.report.yaml` files (including the synthetic records from Step 3) — not from any agent's conversational message. Sort all entries (not just the winner) with the Ranking Algorithm in that file, render the Ranked Results / Summary Table using each entry's `status`, `confidence`, `test_file`/`test_name`, and `fix_summary` fields, and fill in the Recommendation section noting which hypothesis/hypotheses were applied and the arbitrator's `reasoning` if arbitration ran.

---

## Step 6a — Escalation (arbitrator returns ESCALATE_TO_USER)

1. Present the conflicting hypotheses to the user: each claim, its evidence, and why they conflict (from `reasoning`).
2. Ask the user to pick one, request a merge attempt anyway, or provide additional context that resolves the ambiguity.
3. Once the user responds, treat it as a new turn. Apply the chosen fix via the Step 5 procedure. If the user provides new information instead of picking, treat it as input to a fresh, narrower investigation rather than looping the same agents on the same evidence.

---

## Step 6b — No hypothesis passed

Report using the same **Final Ranked Report** format as Step 5 (all hypotheses will rank as INCONCLUSIVE or UNCONFIRMED here) so the user can see which lead came closest, then fill in the "All unconfirmed"/"Inconclusive only" Recommendation variant from `references/report-format.md`. Ask whether to:
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

Run this even on the escalation path, once the user's final choice has been applied. This only removes the `hN/` worktree directories and their branches — the `.claude/debug-sessions/{session_id}/hN.report.yaml` reports live one level up, outside the worktrees, so they survive cleanup on disk for audit purposes. The commits themselves also remain reachable in the repo's object store (via the `commit_sha` recorded in each report) even after the branch ref is deleted, until garbage collected.

---

## Failure modes to handle explicitly

- **Investigator times out or crashes** — treat as `test_result: not_run`, proceed with remaining ones, still clean up its worktree in Step 7.
- **Near-duplicate hypotheses** — if the arbitrator's `reasoning` indicates two hypotheses were the same claim reworded, note this to the user as a process observation, not just a decision.
- **Worktree creation fails** — stop before spawning any investigator and report the error; do not partially spawn agents into a broken session state.

---

## Additional Resources

- **`references/hypothesis-catalog.md`** — Full hypothesis library organized by symptom; used in Step 1
- **`references/report-format.md`** — Evidence report spec and ranking algorithm
- **`references/apply-verification.md`** — Rationale behind the Step 5 artifact-verification checks
- **`examples/debugging-workflow.local.md`** — Complete settings template
- **`../../agents/hypothesis-investigator.md`** — Per-hypothesis investigation agent
- **`../../agents/hypothesis-arbitrator.md`** — Conflict-resolution agent invoked in Step 4 when multiple hypotheses pass
