# debugging-workflow

Systematic debugging plugin for Claude Code. Investigates hard-to-diagnose bugs by generating multiple root-cause hypotheses and exploring them concurrently via autonomous agents.

## Features

- **`/debugging-workflow:parallel-debug`** — Orchestrates the full parallel debug session: session setup, git worktree isolation, agent spawning, arbitration gating, fix application, and cleanup
- **`hypothesis-investigator` agent** — Autonomous per-hypothesis agent: works in an isolated git worktree, writes a failing test, applies a targeted fix, iterates until the test passes, and emits a structured YAML report
- **`hypothesis-arbitrator` agent** — Conflict-resolution agent invoked only when two or more investigators both pass. Re-verifies evidence citations, checks for fix-diff overlap, and returns `ONE_WINNER`, `MERGE_FIXES`, or `ESCALATE_TO_USER`
- **Preflight check** — Runs the project's install step and full test suite once, before any worktree is created, to catch a broken or too-slow test environment before it gets multiplied by `hypothesis_count`
- **Degraded mode** — Optional single-worktree, sequential-hypothesis execution path for low-resource machines

## When to Use

Use `parallel-debug` when:
- The root cause is genuinely unclear (multiple plausible theories coexist)
- The bug is intermittent or hard to reproduce consistently
- A previous debug pass was inconclusive
- Time pressure demands concurrent investigation over sequential elimination

## When NOT to Use

Skip `parallel-debug` when the orchestration overhead outweighs the benefit:

- **The bug is simple.** A single plausible cause, an obvious typo, or a stack trace that points directly at
  the fix. Spinning up 2–4 worktrees for something already explainable is pure overhead — investigate it
  directly.
- **The project has a heavy test environment.** Docker Compose stacks, database migrations, browser/E2E
  suites, or multi-minute builds. Every worktree installs dependencies and runs tests independently, so a slow
  suite gets multiplied by `hypothesis_count`, not divided. Step 0's preflight check exists for exactly this
  case — if it trips (install failure, timeout, or an environment error), take the manual path instead. On a
  genuinely resource-constrained machine that still wants to use the workflow, `degraded_mode` (below) removes
  most of the multiplication instead of removing the workflow entirely.
- **The deadline is tight and closing fast.** Session setup, worktree creation, dependency installs, and agent
  spin-up all happen before the first piece of evidence comes back. A human with a strong existing suspicion
  will usually beat this workflow on wall-clock time for a single fix.
- **This is a production incident.** `parallel-debug` is a development-phase tool, on purpose. It creates local
  git worktrees and branches, applies fixes via cherry-pick, and assumes a normal dev working tree — it was
  never designed to touch a production environment or a live incident, and that's an intentional scope limit,
  not a gap. For an active incident, investigate and patch directly.

## Installation

### Option 1: Install from this repo (marketplace)

```bash
# Add this repo as a marketplace source
/plugin marketplace add sembraniteam/claude-plugins

# Install the plugin
/plugin install debugging-workflow@sembraniteam-claude-plugins
```

### Option 2: Local install (development)

```bash
# Clone the repo
git clone https://github.com/sembraniteam/claude-plugins.git

# Add the local repo as a marketplace
/plugin marketplace add /path/to/claude-plugins

# Install
/plugin install debugging-workflow@sembraniteam-claude-plugins
```

## Usage

### Parallel debug

```
/debugging-workflow:parallel-debug TypeError: Cannot read properties of undefined at auth.ts:87
```

### With vague description

```
/debugging-workflow:parallel-debug My login flow is broken on staging but works locally
```

Claude will generate hypotheses, spawn parallel investigation agents, and return a ranked evidence report.

## Configuration (optional)

Create `.claude/debugging-workflow.local.md` in your project root to customize behavior:

```markdown
---
max_parallel_agents: 4
time_budget_minutes: 5
hypothesis_count: 3
preflight_max_minutes: 5
degraded_mode: false
---
```

| Field                    | Type    | Default | Description                                                                                                                                                                    |
|--------------------------|---------|---------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `max_parallel_agents`    | integer | `4`     | Maximum number of hypothesis agents to spawn concurrently (2–5). Ignored when `degraded_mode: true`.                                                                          |
| `time_budget_minutes`    | integer | `5`     | Approximate time budget *per agent*, in minutes (agents run in parallel, so this is not a total). See `references/report-format.md` for the exact minutes-to-iterations table. |
| `hypothesis_count`       | integer | `3`     | Number of hypotheses to generate (2–4). No hard constraint against `max_parallel_agents`: if it exceeds that cap, investigators run in sequential batches (see "Spawn investigators" below).  |
| `preflight_max_minutes`  | integer | `5`     | Wall-clock cap for the Step 0 preflight test run. If the suite doesn't finish within this window, the session stops before creating any worktree. See `references/resource-constraints.md`.   |
| `degraded_mode`          | boolean | `false` | When `true`, uses a single shared worktree and investigates hypotheses strictly sequentially instead of one worktree per hypothesis — for low-resource machines. See `references/resource-constraints.md`. |

A template is at `skills/parallel-debug/examples/debugging-workflow.local.md`.

> This file should not be committed — it's already in `.gitignore` via `.claude/*.local.md`.

---

## Parallel Debug Workflow Steps

1. **Session setup** — Create `.claude/debug-sessions/{id}/` (add this path to your project's `.gitignore` — it's untracked working state, not source), verify clean working tree (tracked files only), record base SHA
2. **Preflight check** — Run the project's install step and full test suite once on the current branch, capped at `preflight_max_minutes`; stop before creating any worktree if it fails to install, times out, or the test runner errors out (an ordinary test failure is not a stop condition)
3. **Generate hypotheses** — Produce 2–4 distinct, falsifiable hypotheses using the error message and hypothesis catalog
4. **Create worktree(s)** — Standard mode: each hypothesis gets an isolated git worktree and branch. Degraded mode (`degraded_mode: true`): a single shared worktree is created once and reused
5. **Spawn investigators** — Standard mode: `hypothesis-investigator` agents launch in batches of at most `max_parallel_agents` (all at once when `hypothesis_count` fits within that cap, sequential batches otherwise). Degraded mode: agents launch strictly one at a time in the shared worktree, which is reset to a clean state between each. Either way, each installs project dependencies, writes a failing test, applies a fix, commits fix + test together, and writes a YAML report to `{id}/hN.report.yaml` (outside the worktree, so it survives cleanup)
6. **Gate arbitration** — If exactly one hypothesis passes, apply directly; if multiple pass, invoke `hypothesis-arbitrator`
7. **Apply fix** — Cherry-pick the winning commit(s) onto the original branch and re-run tests
8. **Cleanup** — Remove all worktree(s) and branch(es); the `hN.report.yaml` files remain on disk for audit since they were never inside the deleted worktree(s)

## Plugin Structure

```
debugging-workflow/
├── .claude-plugin/
│   └── plugin.json
├── skills/
│   └── parallel-debug/
│       ├── SKILL.md                          # Orchestration workflow
│       ├── examples/
│       │   └── debugging-workflow.local.md   # Settings template
│       └── references/
│           ├── hypothesis-catalog.md         # Hypothesis library by symptom
│           ├── report-format.md              # Evidence report spec and ranking algorithm
│           ├── apply-verification.md         # Rationale behind Step 5 artifact-verification checks
│           └── resource-constraints.md       # Preflight check and degraded_mode mechanics
├── agents/
│   ├── hypothesis-investigator.md            # Per-hypothesis: test → fix → YAML report
│   └── hypothesis-arbitrator.md             # Conflict resolution when multiple fixes pass
└── README.md
```
