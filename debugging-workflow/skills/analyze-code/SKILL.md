---
name: analyze-code
description: This skill should be used when verifying code changes after a bug fix, running static analysis, checking code quality before committing, or when the user asks to "analyze code", "check for errors", "run lint", "verify my changes", "run dart analyze", "run cargo check", "run eslint", "check types", or mentions any language-specific analysis tool. Detects the project's primary language automatically and runs the appropriate set of analysis tools.
version: 0.1.0
license: MIT
allowed-tools: ["Read", "Bash", "Grep", "Glob"]
---

# Analyze Code

Automatically detect the project language and run the appropriate static analysis, type checking, and formatting tools.

## Settings

Before running any analysis, check for a project-local settings file at `.claude/debugging-workflow.local.md`.

If found, read it with the Read tool and parse the YAML frontmatter:

```
---
lint_config_path: "path/to/custom-config"   # optional
skip_verification: false                    # set to true to skip all analysis
analyze_command: ""                         # optional custom command, e.g. "make lint"
---
```

- **`lint_config_path`**: Path to a custom lint/analysis config file. When set, pass it to the tool as a flag (see language-specific flag table below). Leave empty or omit to use the project default.
- **`skip_verification`**: If `true`, skip analysis entirely and report "Verification skipped (skip_verification: true in settings)".
- **`analyze_command`**: If set and non-empty, run this command instead of the auto-detected tool for the primary analysis step (e.g. `make lint`, `pnpm run lint`, `./scripts/check.sh`).

If the file does not exist, run the following setup checklist before proceeding:

### Settings Setup Checklist

Create a todo list using TaskCreate with these steps:
1. Ask user whether to create a settings file
2. Collect `lint_config_path` from user
3. Collect `skip_verification` from user
4. Ask for optional custom analyze command
5. Write `.claude/debugging-workflow.local.md`

Mark each item `in_progress` before starting and `completed` after finishing.

---

**Step 1 — Ask whether to create a settings file**

Ask: "No settings file found at `.claude/debugging-workflow.local.md`. Would you like me to create one?"

- If **no**: skip remaining steps, proceed with analysis using project defaults.
- If **yes**: continue to Step 2.

**Step 2 — Collect `lint_config_path`**

Ask: "Enter the path to your custom lint/analysis config file, relative to the project root. Leave blank to use the project default.

Examples:
- Dart:        `config/analysis_options.yaml`
- ESLint:      `.eslintrc.strict.json`
- Ruff:        `config/ruff.toml`
- RuboCop:     `.rubocop.ci.yml`
- SwiftLint:   `.swiftlint.strict.yml`

`lint_config_path`:"

Wait for the user's response. Store the value (empty string if blank).

**Step 3 — Collect `skip_verification`**

Ask: "Skip static analysis entirely when this setting is active? (true/false, default: false)

`skip_verification`:"

Wait for the user's response. Default to `false` if blank or invalid.

**Step 4 — Optional: custom analyze command (skip if not needed)**

Ask: "If you use a custom command to run analysis (e.g. `make lint`, `./scripts/check.sh`), enter it here. Leave blank to use the auto-detected tool.

`analyze_command` (optional):"

Wait for the user's response. Store the value (empty string if blank).

**Step 5 — Write `.claude/debugging-workflow.local.md`**

Create `.claude/` directory if it does not exist (`mkdir -p .claude`), then write the file using the Write tool:

```markdown
---
lint_config_path: "<value from Step 2>"
skip_verification: <value from Step 3>
analyze_command: "<value from Step 4>"
---
```

Omit `analyze_command` line entirely if the user left it blank.

Confirm to the user: "`.claude/debugging-workflow.local.md` has been created."

---

After the checklist completes, proceed with analysis using the newly created settings.

### Lint config path flags by language

| Language               | Flag to use                                                                              |
|------------------------|------------------------------------------------------------------------------------------|
| Dart                   | `dart analyze --options <lint_config_path>`                                              |
| Rust                   | `RUSTFMT_TOML=<lint_config_path> cargo fmt` / `rustfmt --config-path <lint_config_path>` |
| TypeScript/JS (ESLint) | `npx eslint --config <lint_config_path>`                                                 |
| Python (Ruff)          | `ruff check --config <lint_config_path>`                                                 |
| Python (Pylint)        | `pylint --rcfile <lint_config_path>`                                                     |
| Ruby                   | `rubocop --config <lint_config_path>`                                                    |
| Go                     | (no flag — `go vet` uses standard toolchain config)                                      |
| Swift                  | `swiftlint lint --config <lint_config_path>`                                             |

---

### `analyze_command` override

If `analyze_command` is set and non-empty in the settings file, **run that command instead of the auto-detected tool** for the primary analysis step. Still run the formatting check using the standard tool unless `skip_verification` is `true`.

Example: if `analyze_command: "make lint"`, run `make lint` and report its output directly.

---

## Language Detection

Detect the primary language by checking for these files (in priority order):

1. `pubspec.yaml` → **Dart/Flutter**
2. `Cargo.toml` → **Rust**
3. `tsconfig.json` or `.ts`/`.tsx` files → **TypeScript**
4. `package.json` (without tsconfig) → **JavaScript**
5. `go.mod` → **Go**
6. `requirements.txt`, `pyproject.toml`, or `setup.py` → **Python**
7. `pom.xml` → **Java/Maven**
8. `build.gradle` or `build.gradle.kts` → **Kotlin/Java/Gradle**
9. `Package.swift` or `.xcodeproj` → **Swift**
10. `Gemfile` → **Ruby**
11. `CMakeLists.txt` or `Makefile` → **C/C++**

If multiple are present, prefer the language of the file most recently edited.

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

### 2. Check Formatting

Run a formatting check (non-destructive) if a formatter is available:

| Language      | Format Check Command                                |
|---------------|-----------------------------------------------------|
| Dart          | `dart format --output=none --set-exit-if-changed .` |
| Rust          | `rustfmt --check src/**/*.rs`                       |
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

## Additional Resources

- **`../debug/references/analyze-tools.md`** — Full per-language tool options, common error patterns, and best practices
