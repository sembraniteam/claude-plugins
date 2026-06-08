---
lint_config_path: ""
skip_verification: false
analyze_command: ""
---

# debugging-workflow Settings

Copy this file to `.claude/debugging-workflow.local.md` in your project root.

For the complete settings template (including `parallel-debug` options), use the template at `../../parallel-debug/examples/debugging-workflow.local.md` instead.

## Settings Reference

**`lint_config_path`** (string, optional)
Path to a custom lint/analysis config file, relative to the project root.
Leave empty to use the project's default config.

Examples by language:
- Dart:       `lint_config_path: "config/analysis_options.yaml"`
- ESLint:     `lint_config_path: ".eslintrc.strict.json"`
- Ruff:       `lint_config_path: "config/ruff.toml"`
- RuboCop:    `lint_config_path: ".rubocop.ci.yml"`
- SwiftLint:  `lint_config_path: ".swiftlint.strict.yml"`

**`skip_verification`** (boolean, optional, default: false)
Set to `true` to skip all static analysis steps.
Useful when you want to run the debug workflow without the verification pass.

**`analyze_command`** (string, optional)
A custom shell command to run instead of the auto-detected analyze tool.
When set, this command is executed as-is for the primary analysis step.

Examples:
- `analyze_command: "make lint"`
- `analyze_command: "./scripts/check.sh"`
- `analyze_command: "pnpm run lint"`
