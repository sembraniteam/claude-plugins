---
name: analyze-code
description: This skill should be used when verifying code changes after a bug fix, running static analysis, checking code quality before committing, or when the user asks to "analyze code", "check for errors", "run lint", "verify my changes", "run dart analyze", "run cargo check", "run eslint", "check types", or mentions any language-specific analysis tool. As opposed to runtime errors, crashes, or active bugs, which should use the debug skill.
argument-hint: "[file or directory to analyze — leave blank to analyze entire project]"
license: MIT
allowed-tools: ["Read", "Write", "Bash", "Grep", "Glob"]
---

# Analyze Code

Automatically detect the project language and run the appropriate static analysis, type checking, and formatting tools.

## Settings

Before running any analysis, check for `.claude/debugging-workflow.local.md`. If found, read it with the Read tool and parse the YAML frontmatter:

```
---
lint_config_path: ""       # path to custom lint config, or leave blank
skip_verification: false   # set to true to skip all analysis
analyze_command: ""        # optional override command, e.g. "make lint"
---
```

- **`lint_config_path`**: When set, pass as a config flag to the tool (see table below). Omit the flag entirely if blank or missing.
- **`skip_verification`**: If `true`, skip all analysis and report "Verification skipped (skip_verification: true in settings)".
- **`analyze_command`**: When set, run this instead of the auto-detected tool for the primary analysis step. The formatting check still runs unless `skip_verification` is `true`.

If no settings file exists, proceed with project defaults.

### Lint config path flags by language

| Language               | Flag to use                                             |
|------------------------|---------------------------------------------------------|
| Dart                   | `dart analyze --options <lint_config_path>`             |
| Rust                   | `rustfmt --config-path <lint_config_path>`              |
| TypeScript/JS (ESLint) | `npx eslint --config <lint_config_path>`                |
| Python (Ruff)          | `ruff check --config <lint_config_path>`                |
| Python (Pylint)        | `pylint --rcfile <lint_config_path>`                    |
| Ruby                   | `rubocop --config <lint_config_path>`                   |
| Go                     | (no flag — `go vet` uses standard toolchain config)     |
| Swift                  | `swiftlint lint --config <lint_config_path>`            |

If `analyze_command` is set and non-empty, run that command instead of the auto-detected tool for the primary analysis step. Example: `analyze_command: "make lint"` → run `make lint` and report its output directly.

## Language Detection

Detect the primary language by checking for marker files in priority order — see **`references/language-detection.md`** for the full priority table and Flutter/Dart distinction rules. If no marker file is found, ask the user which language the project uses.

## Run Primary Tool

Run the language's primary analysis command from the project root:

| Language      | Command                                                      |
|---------------|--------------------------------------------------------------|
| Dart (pure)   | `dart analyze`                                               |
| Flutter       | `flutter analyze`                                            |
| Rust          | `cargo check && cargo clippy`                                |
| TypeScript    | `npx tsc --noEmit`                                           |
| JavaScript    | `npx eslint .`                                               |
| Go            | `go vet ./...`                                               |
| Python        | `ruff check .` (or `python -m pylint .` if ruff unavailable) |
| Java/Maven    | `mvn compile -q`                                             |
| Kotlin/Gradle | `./gradlew check`                                            |
| Swift         | `swiftlint lint`                                             |
| Ruby          | `rubocop`                                                    |
| C/C++         | `cmake --build build/` or `make` (whichever applies)         |

## Check Formatting

Run a formatting check (non-destructive) if a formatter is available:

| Language      | Format Check Command                                |
|---------------|-----------------------------------------------------|
| Dart          | `dart format --output=none --set-exit-if-changed .` |
| Rust          | `cargo fmt -- --check`                              |
| TypeScript/JS | `npx prettier --check .`                            |
| Go            | `gofmt -l .`                                        |
| Python        | `ruff format --check .`                             |
| Ruby          | `rubocop --only Layout`                             |

## Interpret Results

After running tools:
- **Zero errors**: Report "Analysis passed — no issues found"
- **Warnings only**: List each warning with file:line and a brief fix suggestion
- **Errors**: List each error with file:line, explain the cause, and propose a fix
- **Tool not found**: Report which tool is missing and suggest how to install it

Report analysis results in this structure:

```
## Analysis Results — [Language]

**Tool**: [command run]
**Status**: ✓ Passed / ✗ Errors / ⚠ Warnings

### Errors (N)
- `path/to/file.dart:42` — [error message]
  → Fix: [suggested fix]

### Warnings (N)
- `path/to/file.dart:17` — [warning message]
  → Fix: [suggested fix]

### Formatting
- [Passed / N files need formatting]
```

If no settings file was found, append to the report:

> **Tip:** No `.claude/debugging-workflow.local.md` found. Ask to "set up debugging-workflow settings" to configure custom lint paths or override commands.

## Auto-Fix

When the user explicitly asks to "fix lint errors" or "apply auto-fix":

| Language      | Auto-fix Command                               |
|---------------|------------------------------------------------|
| Dart          | `dart fix --apply && dart format .`            |
| Rust          | `cargo fix --allow-dirty && cargo fmt`         |
| TypeScript/JS | `npx eslint --fix . && npx prettier --write .` |
| Go            | `gofmt -w .`                                   |
| Python        | `ruff check --fix . && ruff format .`          |
| Ruby          | `rubocop -A`                                   |
| Swift         | `swiftlint --fix`                              |

Always show a summary of what was auto-fixed (number of files changed, types of fixes applied).

## Settings Setup

Run this only when the user explicitly asks to "set up debugging-workflow settings", "create a settings file", or similar — not automatically on first analysis.

**Confirm intent** — ask: "Would you like me to create `.claude/debugging-workflow.local.md` with custom settings?" Stop if no.

**Collect settings** — ask all three questions together:
- `lint_config_path`: Path to custom lint/analysis config file (relative to project root), or leave blank for project defaults. Examples: `config/analysis_options.yaml`, `.eslintrc.strict.json`, `config/ruff.toml`
- `skip_verification`: Skip all static analysis when active? (true/false, default: false)
- `analyze_command`: Custom analysis command (e.g. `make lint`, `./scripts/check.sh`), or leave blank to auto-detect

**Write the settings file** — run `mkdir -p .claude`, then write `.claude/debugging-workflow.local.md`:

```markdown
---
lint_config_path: "<value>"
skip_verification: <value>
analyze_command: "<value>"
---
```

Confirm: "`.claude/debugging-workflow.local.md` has been created."

## Summary

After completing analysis, display a summary block:

| Field          | Value                          |
|----------------|--------------------------------|
| **Language**   | `Dart`                         |
| **Tool**       | `flutter analyze`              |
| **Status**     | Pass / Fail / Skipped          |
| **Errors**     | `0`                            |
| **Warnings**   | `2`                            |
| **Formatting** | Pass / N files need formatting |

## Additional Resources

- **`../../references/analyze-tools.md`** — Full per-language tool options, common error patterns, and best practices
- **`references/language-detection.md`** — Canonical language detection priority table
- **`examples/debugging-workflow.local.md`** — Ready-made settings template to copy to `.claude/debugging-workflow.local.md`
