---
max_parallel_agents: 4
time_budget_minutes: 5
hypothesis_count: 3
---

# debugging-workflow Settings

Copy this file to `.claude/debugging-workflow.local.md` in your project root.

---

## Settings

**`max_parallel_agents`** (integer, 2–5, default: 4)
Maximum number of hypothesis-investigator agents to spawn concurrently in a single batch.
Reduce to `2` or `3` on slower machines or when API concurrency is limited.

Examples:
- `max_parallel_agents: 2`  — conservative, fewer concurrent agents
- `max_parallel_agents: 4`  — default, balanced parallelism

**`time_budget_minutes`** (integer, 1–15, default: 5)
Approximate time budget per agent in minutes.
Used to compute the iteration budget passed to each agent — see the mapping table in
`references/report-format.md` ("Iteration Budget to Minutes Mapping"), which is the single source of truth.

Examples:
- `time_budget_minutes: 3`   — quick pass
- `time_budget_minutes: 5`   — default
- `time_budget_minutes: 10`  — thorough pass

**`hypothesis_count`** (integer, 2–4, default: 3)
Number of hypotheses to generate and investigate.
When it exceeds `max_parallel_agents`, `SKILL.md` Step 3 runs the investigators in
multiple sequential batches instead of all at once — no hard constraint between the two settings.

Set to `2` for a fast targeted pass when you have a strong hunch.
Set to `4` for maximum coverage on genuinely mysterious bugs.

Examples:
- `hypothesis_count: 2`  — targeted, use when one strong hypothesis already exists
- `hypothesis_count: 3`  — default, balanced coverage
- `hypothesis_count: 4`  — exhaustive, for very unclear root causes
