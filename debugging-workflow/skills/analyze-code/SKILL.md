---
name: analyze-code
description: This skill should be used when verifying code changes after a bug fix, running static analysis, checking code quality before committing, or when the user asks to "analyze code", "check for errors", "run lint", "verify my changes", "run dart analyze", "run cargo check", "run eslint", "check types", or mentions any language-specific analysis tool. Detects the project's primary language automatically and runs the appropriate set of analysis tools.
license: MIT
allowed-tools: ["Read", "Bash", "Grep", "Glob"]
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
- **`analyze_command`**: When set, run this instead of the auto-detected tool for the primary analysis step. The formatting check (Step 2) still runs unless `skip_verification` is `true`.

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

---

### `analyze_command` override

If `analyze_command` is set and non-empty, **run that command instead of the auto-detected tool** for the primary analysis step. The formatting check (Step 2) still runs using the standard tool unless `skip_verification` is `true`.

Example: if `analyze_command: "make lint"`, run `make lint` and report its output directly.

---

## Language Detection

Detect the primary language by checking for marker files in priority order (first match wins):

| Priority | Marker file(s)                                       | Language        |
|----------|------------------------------------------------------|-----------------|
| 1        | `pubspec.yaml`                                       | Dart / Flutter  |
| 2        | `Cargo.toml`                                         | Rust            |
| 3        | `tsconfig.json` or any `.ts` / `.tsx` file           | TypeScript      |
| 4        | `package.json` (no tsconfig present)                 | JavaScript      |
| 5        | `go.mod`                                             | Go              |
| 6        | `requirements.txt`, `pyproject.toml`, or `setup.py`  | Python          |
| 7        | `pom.xml`                                            | Java / Maven    |
| 8        | `build.gradle` or `build.gradle.kts`                 | Kotlin / Gradle |
| 9        | `Package.swift` or `.xcodeproj`                      | Swift           |
| 10       | `Gemfile`                                            | Ruby            |
| 11       | `CMakeLists.txt` or `Makefile`                       | C / C++         |

For Dart: if `pubspec.yaml` contains `flutter:` as a top-level key, treat as Flutter; otherwise pure Dart. If no marker file is found, ask the user which language the project uses.

## Analysis Steps

### 1. Run Primary Analyze Tool

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

### 2. Check Formatting

Run a formatting check (non-destructive) if a formatter is available:

| Language      | Format Check Command                                |
|---------------|-----------------------------------------------------|
| Dart          | `dart format --output=none --set-exit-if-changed .` |
| Rust          | `cargo fmt -- --check`                              |
| TypeScript/JS | `npx prettier --check .`                            |
| Go            | `gofmt -l .`                                        |
| Python        | `ruff format --check .`                             |
| Ruby          | `rubocop --only Layout`                             |

### 3. Interpret Results

After running tools:
- **Zero errors**: Report "Analysis passed — no issues found"
- **Warnings only**: List each warning with file:line and a brief fix suggestion
- **Errors**: List each error with file:line, explain the cause, and propose a fix
- **Tool not found**: Report which tool is missing and suggest how to install it

### 4. Auto-Fix (if requested)

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

## Reporting Format

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

> **Tip:** No `.claude/debugging-workflow.local.md` found. Ask me to "set up debugging-workflow settings" to configure custom lint paths or override commands.

---

## Settings Setup

Run this only when the user explicitly asks to "set up debugging-workflow settings", "create a settings file", or similar — not automatically on first analysis.

Create a todo list with these steps. If TaskCreate is unavailable, track steps as a numbered checklist instead. Mark each task `in_progress` before starting and `completed` after finishing.

**Step 1 — Confirm intent**

Ask: "Would you like me to create `.claude/debugging-workflow.local.md` with custom settings?"

- If **no**: stop.
- If **yes**: continue.

**Step 2 — Collect `lint_config_path`**

Ask: "Enter the path to your custom lint/analysis config file (relative to project root), or leave blank to use project defaults.

Examples: `config/analysis_options.yaml`, `.eslintrc.strict.json`, `config/ruff.toml`

`lint_config_path`:"

**Step 3 — Collect `skip_verification`**

Ask: "Skip all static analysis when this setting is active? (true/false, default: false)

`skip_verification`:"

Default to `false` if blank or invalid.

**Step 4 — Optional custom analyze command**

Ask: "Custom analysis command (e.g. `make lint`, `./scripts/check.sh`), or leave blank to auto-detect.

`analyze_command`:"

**Step 5 — Write the settings file**

Run `mkdir -p .claude`, then write `.claude/debugging-workflow.local.md`:

```markdown
---
lint_config_path: "<value from Step 2>"
skip_verification: <value from Step 3>
analyze_command: "<value from Step 4>"
---
```

Confirm: "`.claude/debugging-workflow.local.md` has been created."

---

## Additional Resources

- **`../../references/analyze-tools.md`** — Full per-language tool options, common error patterns, and best practices
- **`../../references/language-detection.md`** — Canonical language detection priority table
