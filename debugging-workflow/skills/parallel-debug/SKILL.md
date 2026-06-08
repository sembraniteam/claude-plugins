---
name: parallel-debug
description: This skill should be used when the user invokes /debugging-workflow:parallel-debug, asks to "debug in parallel", "try all hypotheses at once", "spawn multiple agents for this bug", "investigate multiple root causes", "parallel hypothesis testing", "parallel investigation", or reports a complex or intermittent bug where the root cause is unclear and multiple theories need testing simultaneously. It should be preferred over the `debug` skill when the bug is hard to diagnose and would benefit from concurrent exploration.
argument-hint: "[error message, stack trace, or bug description]"
allowed-tools: ["Read", "Write", "Edit", "Bash", "Grep", "Glob", "TaskCreate", "TaskUpdate", "Agent"]
license: MIT
---

# Parallel Debug Workflow

Investigate a hard-to-diagnose bug by generating multiple root-cause hypotheses and exploring them concurrently. Each hypothesis-investigator agent must write a failing test before attempting a fix, then iterate until the test passes. Results are ranked by confidence and returned in a structured report.

## When to Use

Use `parallel-debug` instead of `debug` when:
- The root cause is genuinely unclear (multiple plausible theories coexist)
- The bug is intermittent or hard to reproduce consistently
- A previous sequential debug pass was inconclusive
- Time pressure demands concurrent investigation over sequential elimination

For bugs with an obvious root cause, prefer the `debug` skill — it is faster and uses fewer resources.

---

## Step 1: Pre-Flight Setup

Create a `TaskCreate` checklist immediately upon invocation:

1. Read settings and parse bug
2. Generate hypotheses
3. Spawn hypothesis agents (parallel)
4. Collect evidence reports
5. Rank and present results

Read `.claude/debugging-workflow.local.md` from the project root (if it exists). Parse YAML frontmatter for:
- `max_parallel_agents` — integer 2–5, default `5`
- `time_budget_minutes` — integer 1–15, default `5`
- `hypothesis_count` — integer 3–5, default `5`; must be ≤ `max_parallel_agents`

Calculate iteration budget: `max(1, time_budget_minutes // 2)`

---

## Step 2: Parse the Bug

Extract from the user's report:
- **Error type and message** — exact text from the stack trace or log
- **File and line** — where the failure originates
- **Symptom** — what was observed vs. what was expected
- **Context clues** — recent code changes, intermittency, environment-specific behavior

If the description is vague, ask exactly one clarifying question before proceeding: "Which file or function is misbehaving, and what is the exact error or unexpected behavior?"

Run `git diff HEAD --name-only` to identify recently changed files — hypotheses touching these files rank higher.

---

## Step 3: Generate Hypotheses

Read `references/hypothesis-catalog.md` and match the error symptom to the appropriate category. Select `hypothesis_count` distinct hypotheses (3–5). Each hypothesis must:

1. **Name a specific failure mechanism** — not just a category (e.g., `stale-closure-capture`, not "stale state")
2. **Be falsifiable by a test** — a test can either confirm or refute it
3. **Differ meaningfully** from the others — avoid picking five variations of the same root cause

**Prioritization order** (prefer hypotheses that score higher on each criterion):
1. Error message matches a known symptom pattern in the catalog
2. Hypothesis touches a file changed in `git diff`
3. Hypothesis is common in the detected language/framework
4. Intermittent bug → bias toward async/concurrency hypotheses
5. Environment-specific bug → bias toward config/dependency hypotheses

Present hypotheses to the user before spawning agents:

```
## Hypotheses

1. **[hypothesis-slug]** — [One sentence: what mechanism is being tested]
2. **[hypothesis-slug]** — [One sentence]
...

Spawning [N] parallel investigation agents (~[M] minutes each).
```

---

## Step 4: Spawn Parallel Agents

Spawn all hypothesis-investigator agents **in a single message** — all Agent tool calls must be in the same response to run in parallel. Do not send them one at a time.

Use `subagent_type: "debugging-workflow:hypothesis-investigator"` for each agent.

For each hypothesis, pass a prompt with this structure:

```
Bug description: [full error message and symptom]
File/line: [path:line where error originates]
Language: [detected language — Dart, Rust, TypeScript, Python, Go, etc.]

Your hypothesis to investigate:
Name: [hypothesis-slug]
Mechanism: [one sentence describing what you are testing]

Iteration budget: [N] attempts (approximately [M] minutes)

Instructions:
1. Write a minimal failing test that reproduces the bug under this hypothesis
2. Confirm the test fails before touching source code
3. Investigate source code for evidence of the hypothesized mechanism
4. Apply a targeted fix consistent with the hypothesis
5. Iterate until the test passes or the iteration budget is exhausted
6. Return a structured evidence report per the format in your instructions

Do not fix bugs outside the scope of your assigned hypothesis.
```

Spawn up to `max_parallel_agents` agents. If `hypothesis_count` < `max_parallel_agents`, spawn exactly `hypothesis_count` agents.

---

## Step 5: Collect and Rank Results

After all agents complete, collect their evidence reports. Rank using the scoring in `references/report-format.md`:

```
score = (test_final_result × 100) + (confidence × 10) + evidence_count

test_final_result : PASS=3, FAIL=1, ERROR=0
confidence       : High=3, Medium=2, Low=1
evidence_count   : 3 points=3, 2 points=2, 1 point=1
```

Hypotheses with status `CONFIRMED` always rank above `INCONCLUSIVE`, which always rank above `UNCONFIRMED`.

---

## Step 6: Present Ranked Report

Present the final ranked report using the format in `references/report-format.md`. Include:
- All hypotheses ranked from most to the least confirmed
- A clear recommendation section
- A summary table

If multiple hypotheses are confirmed, check whether the fixes conflict (modify the same lines). If they do, note this in the recommendation and suggest applying them sequentially, re-running tests after each.

If no hypothesis was confirmed, recommend either:
- A targeted sequential investigation using the `debug` skill focused on the most promising lead
- Adding instrumentation/logging to narrow the hypothesis space before retrying

---

## Additional Resources

- **`references/hypothesis-catalog.md`** — Full hypothesis library organized by symptom; used in Step 3
- **`references/report-format.md`** — Evidence report spec, ranking algorithm, and iteration budget table
- **`examples/debugging-workflow.local.md`** — Complete settings template with all available options
- **`../debug/references/debugging-patterns.md`** — Root cause patterns by error category (present when the `debug` skill is installed)
- **`../../agents/hypothesis-investigator.md`** — Agent definition used in Step 4

### Related Skills

- Use `debug` for straightforward bugs with a clear root cause — faster and lower cost
- Use `analyze-code` after applying confirmed fixes to run a full static analysis pass
