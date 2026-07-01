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

### Local project

```bash
# Copy plugin into project
cp -r debugging-workflow /path/to/your-project/.claude/plugins/

# Or install via Claude Code marketplace
cc --install-plugin debugging-workflow
```

### Test locally

```bash
cc --plugin-dir /path/to/debugging-workflow
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
max_parallel_agents: 5
time_budget_minutes: 5
hypothesis_count: 5
---
```

| Field                 | Type    | Default | Description                                                       |
|-----------------------|---------|---------|-------------------------------------------------------------------|
| `max_parallel_agents` | integer | `5`     | Maximum number of hypothesis agents to spawn concurrently (2–5). |
| `time_budget_minutes` | integer | `5`     | Total time budget; each agent gets `time_budget // 2` iterations. |
| `hypothesis_count`    | integer | `5`     | Number of hypotheses to generate (3–5, clamped to max_parallel_agents). |

A template is at `skills/parallel-debug/examples/debugging-workflow.local.md`.

> This file should not be committed — it's already in `.gitignore` via `.claude/*.local.md`.

---

## Parallel Debug Workflow Steps

1. **Session setup** — Create `.claude/debug-sessions/{id}/`, verify clean working tree, record base SHA
2. **Generate hypotheses** — Produce 2–4 distinct, falsifiable hypotheses using the error message and hypothesis catalog
3. **Create worktrees** — Each hypothesis gets an isolated git worktree and branch
4. **Spawn investigators** — All `hypothesis-investigator` agents launch in parallel; each writes a YAML report
5. **Gate arbitration** — If exactly one hypothesis passes, apply directly; if multiple pass, invoke `hypothesis-arbitrator`
6. **Apply fix** — Cherry-pick the winning diff onto the original branch and re-run tests
7. **Cleanup** — Remove all worktrees and branches; keep YAML reports for audit

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
