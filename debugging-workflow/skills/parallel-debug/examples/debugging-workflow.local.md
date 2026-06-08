---
lint_config_path: ""
skip_verification: false
analyze_command: ""
max_parallel_agents: 5
time_budget_minutes: 5
hypothesis_count: 5
---

# debugging-workflow Settings

Copy this file to `.claude/debugging-workflow.local.md` in your project root.

This template includes both the existing settings (used by `debug` and `analyze-code`) and the new settings for `parallel-debug`.

---

## Existing Settings (debug / analyze-code)

**`lint_config_path`** (string, optional)
Path to a custom lint/analysis config file, relative to the project root.
Leave empty to use the project's default config.

Examples:
- Dart:      `lint_config_path: "config/analysis_options.yaml"`
- ESLint:    `lint_config_path: ".eslintrc.strict.json"`
- Ruff:      `lint_config_path: "config/ruff.toml"`

**`skip_verification`** (boolean, optional, default: false)
Set to `true` to skip the static analysis step in the `debug` workflow.

**`analyze_command`** (string, optional)
A custom shell command to run instead of the auto-detected analyze tool.
Example: `analyze_command: "make lint"`

---

## Parallel Debug Settings (parallel-debug)

**`max_parallel_agents`** (integer, 2–5, default: 5)
Maximum number of hypothesis-investigator agents to spawn in parallel.
Reduce to `2` or `3` on slower machines or when API concurrency is limited.

Examples:
- `max_parallel_agents: 3`  — conservative, fewer concurrent agents
- `max_parallel_agents: 5`  — default, maximum parallelism

**`time_budget_minutes`** (integer, 1–15, default: 5)
Approximate time budget per agent in minutes.
Translated to an iteration budget using: `max(1, time_budget_minutes // 2)`.

| Setting value | Iteration budget       |
|---------------|------------------------|
| 1–2           | 1 iteration            |
| 3–4           | 2 iterations           |
| 5–7           | 3 iterations (default) |
| 8–10          | 4 iterations           |
| 11–15         | 5 iterations           |

Examples:
- `time_budget_minutes: 3`   — quick pass, 2 iterations per agent
- `time_budget_minutes: 5`   — default, 3 iterations per agent
- `time_budget_minutes: 10`  — thorough pass, 4 iterations per agent

**`hypothesis_count`** (integer, 3–5, default: 5)
Number of hypotheses to generate and investigate.
Must be ≤ `max_parallel_agents`.

Set to `3` for faster results when you have a strong hunch about the cause.
Set to `5` for maximum coverage on genuinely mysterious bugs.

Examples:
- `hypothesis_count: 3`  — targeted, use when 1–2 strong hypotheses already exist
- `hypothesis_count: 5`  — default, full parallel coverage
