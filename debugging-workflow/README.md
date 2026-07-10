# debugging-workflow

Systematic debugging plugin for Claude Code. Investigates hard-to-diagnose bugs by generating multiple root-cause hypotheses and exploring them concurrently via autonomous agents.

## Features

- **`/debugging-workflow:parallel-debug`** — Orchestrates the full parallel debug session: session setup, git worktree isolation, agent spawning, arbitration gating, fix application, and cleanup
- **`hypothesis-investigator` agent** — Autonomous per-hypothesis agent: works in an isolated git worktree, writes a failing test, applies a targeted fix, iterates until the test passes, and emits a structured YAML report
- **`hypothesis-arbitrator` agent** — Conflict-resolution agent invoked only when two or more investigators both pass. Re-verifies evidence citations, checks for fix-diff overlap, and returns `ONE_WINNER`, `MERGE_FIXES`, or `ESCALATE_TO_USER`

## When to Use

Use `parallel-debug` when:
- The root cause is genuinely unclear (multiple plausible theories coexist)
- The bug is intermittent or hard to reproduce consistently
- A previous debug pass was inconclusive
- Time pressure demands concurrent investigation over sequential elimination

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
---
```

| Field                 | Type    | Default | Description                                                                                                                                                                    |
|-----------------------|---------|---------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `max_parallel_agents` | integer | `4`     | Maximum number of hypothesis agents to spawn concurrently (2–5).                                                                                                               |
| `time_budget_minutes` | integer | `5`     | Approximate time budget *per agent*, in minutes (agents run in parallel, so this is not a total). See `references/report-format.md` for the exact minutes-to-iterations table. |
| `hypothesis_count`    | integer | `3`     | Number of hypotheses to generate (2–4, clamped to max_parallel_agents).                                                                                                        |

A template is at `skills/parallel-debug/examples/debugging-workflow.local.md`.

> This file should not be committed — it's already in `.gitignore` via `.claude/*.local.md`.

---

## Parallel Debug Workflow Steps

1. **Session setup** — Create `.claude/debug-sessions/{id}/` (add this path to your project's `.gitignore` — it's untracked working state, not source), verify clean working tree (tracked files only), record base SHA
2. **Generate hypotheses** — Produce 2–4 distinct, falsifiable hypotheses using the error message and hypothesis catalog
3. **Create worktrees** — Each hypothesis gets an isolated git worktree and branch
4. **Spawn investigators** — All `hypothesis-investigator` agents launch in parallel; each installs project dependencies in its worktree, writes a failing test, applies a fix, commits fix + test together, and writes a YAML report to `{id}/hN.report.yaml` (outside the worktree, so it survives cleanup)
5. **Gate arbitration** — If exactly one hypothesis passes, apply directly; if multiple pass, invoke `hypothesis-arbitrator`
6. **Apply fix** — Cherry-pick the winning commit(s) onto the original branch and re-run tests
7. **Cleanup** — Remove all worktrees and branches; the `hN.report.yaml` files remain on disk for audit since they were never inside the deleted worktrees

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
│           └── report-format.md              # Evidence report spec and ranking algorithm
├── agents/
│   ├── hypothesis-investigator.md            # Per-hypothesis: test → fix → YAML report
│   └── hypothesis-arbitrator.md             # Conflict resolution when multiple fixes pass
└── README.md
```
