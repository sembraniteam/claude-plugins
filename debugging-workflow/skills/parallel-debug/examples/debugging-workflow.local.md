---
max_parallel_agents: 4
time_budget_minutes: 5
hypothesis_count: 3
preflight_max_minutes: 5
degraded_mode: false
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

**`preflight_max_minutes`** (integer, default: 5)
Wall-clock cap for the one-time install + full-test-suite run in `SKILL.md` Step 0, before any worktree is
created. If the suite doesn't finish within this window (or fails to install, or the test runner errors out
before producing a normal pass/fail summary), the session stops and recommends manual debugging instead —
see `references/resource-constraints.md`. Raise this for projects with a known-heavy but otherwise healthy
test suite; an ordinary test failure within the window is not a stop condition.

Examples:
- `preflight_max_minutes: 3`   — strict, for projects that should always have a fast suite
- `preflight_max_minutes: 5`   — default
- `preflight_max_minutes: 10`  — generous, for projects with a known-heavy suite (e.g. E2E/browser tests)

**`degraded_mode`** (boolean, default: false)
When `true`, uses a single shared git worktree and investigates hypotheses strictly sequentially instead of
one worktree per hypothesis running with up to `max_parallel_agents` concurrency. `max_parallel_agents` is
ignored in this mode. Trades wall-clock time (roughly `hypothesis_count`x slower than full parallelism) for a
single worktree's disk footprint instead of `hypothesis_count` of them at once — see
`references/resource-constraints.md` for the full mechanics and trade-offs, including why install-time savings
(unlike the disk-footprint reduction) depend on the project's package manager.

Examples:
- `degraded_mode: false`  — default, one worktree per hypothesis, up to `max_parallel_agents` concurrent
- `degraded_mode: true`   — low-RAM/low-disk machines, constrained CI runners
