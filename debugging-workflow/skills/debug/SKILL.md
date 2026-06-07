---
name: debug
description: This skill should be used when the user invokes /debugging-workflow:debug, reports an error or bug, pastes a stack trace, says "I have a bug", "this is not working", "fix this error", "debug this", or shares any runtime error, crash report, or unexpected behavior. As opposed to static analysis requests, which should use analyze-code.
argument-hint: "[error message, stack trace, or bug description — leave blank to inspect current state]"
allowed-tools: ["Read", "Bash", "Grep", "Glob"]
license: MIT
---

# Debugging Workflow

A systematic debugging process that moves from symptom to root cause to verified fix.

## Pre-Flight Checklist

Upon invocation, immediately create a todo list using TaskCreate with these steps. If TaskCreate is unavailable, track steps as a numbered checklist instead.

1. **Read & parse error** — understand the error message/stack trace
2. **Gather context** — read relevant source files
3. **Check git diff** — inspect recent changes
4. **Find related tests** — locate test files for affected code
5. **Conclude root cause** — synthesize findings
6. **Fix the bug** — apply targeted, best-practice fix
7. **Verify changes** — run language-specific analysis tools
8. **Run tests** — execute related tests to confirm fix

Mark each task `in_progress` before starting it and `completed` after finishing.

## Read & Parse Error

If the user provided an error message or stack trace:
- Extract the error type, message, file path, and line number
- Note the call stack or chain of causation
- Identify which file/function/line is the direct origin

If no error was provided:
- Ask: "What error or unexpected behavior are you seeing? If you have a stack trace or error message, paste it here."
- If the response is vague (e.g., "it doesn't work"), follow up with: "Which file or feature is misbehaving?"

## Context Gathering

Read source files relevant to the error origin:

1. Open the file at the line mentioned in the stack trace
2. Read the surrounding function/class for full context
3. Follow imports/dependencies up to 2 levels if the root cause is unclear
4. Note any recent TODOs, deprecated calls, or suspicious patterns

Use `Grep` to find all usages of the failing symbol if the error is about an undefined or misused identifier.

## Git Diff Review

Run `git diff` to inspect what recently changed:

```bash
git diff HEAD          # unstaged changes
git diff --cached      # staged changes
git log --oneline -10  # recent commits
git diff HEAD~1        # changes in last commit
```

Look for:
- Changes to the file that threw the error
- New imports or removed functions that could cause the issue
- Configuration or dependency changes (pubspec.yaml, Cargo.toml, package.json, etc.)

## Test Discovery

Search for test files associated with the failing code:

```bash
# Common test file patterns (all languages)
find . -name "*_test.*" -o -name "*.test.*" -o -name "*.spec.*" | grep -v node_modules

# Test files inside test/ or tests/ directories (Dart, Python)
find . \( -path "*/test*" -o -path "*/tests*" \) \
  \( -name "*.dart" -o -name "*.py" \) | grep -v node_modules
```

- For Dart: look for `test/` directory or `*_test.dart` files
- For Rust: look for `#[cfg(test)]` blocks in the same file or `tests/` directory
- For JS/TS: look for `*.test.ts`, `*.spec.ts`, `__tests__/` directory
- For Python: look for `test_*.py` or `*_test.py` in `tests/` or `test/`
- For Go: look for `*_test.go` in the same package

Note which test functions cover the failing code.

## Root Cause Analysis

Synthesize all gathered information into a clear diagnosis:

- **Root cause**: One sentence describing the actual bug
- **Why it happened**: The underlying condition that allowed the bug
- **Affected scope**: Which files, functions, or data flows are impacted
- **Fix strategy**: What change will resolve it without introducing regressions

Do not proceed to fixing until the root cause is clearly stated.

## Fix

Apply a targeted fix following language-specific best practices:

**General principles:**
- Fix only what is broken — avoid unrelated refactors
- Preserve the existing code style and conventions
- Do not add error handling for impossible scenarios
- Trust framework guarantees; only validate at system boundaries
- Write no comments unless the fix is non-obvious (hidden constraint, workaround)

**Language-specific patterns:**
- See `../../references/analyze-tools.md` for the full table with flags and language-specific idioms
- Match the existing naming conventions, type system usage, and architecture patterns
- For async code: handle futures/promises correctly; avoid fire-and-forget
- For null safety (Dart/Kotlin/TS): use proper null checks, not `!` unless provably safe

After applying the fix, briefly summarize what changed and why.

## Verification

Check for `.claude/debugging-workflow.local.md` before running tools. If it exists, parse the YAML frontmatter:
- `lint_config_path` — pass to the tool as a config flag (see `references/analyze-tools.md` for per-language flags)
- `skip_verification: true` — skip this step entirely and note it in the summary

If no settings file exists, proceed with project defaults. To configure custom lint paths, run the `analyze-code` skill and ask to "set up debugging-workflow settings".

Detect the project language and run the appropriate tool:

| Detected file/config                            | Tool(s) to run                           |
|-------------------------------------------------|------------------------------------------|
| `pubspec.yaml` / `.dart`                        | `dart analyze` or `flutter analyze`      |
| `Cargo.toml` / `.rs`                            | `cargo check` then `cargo clippy`        |
| `package.json` / `.ts` / `.tsx`                 | `tsc --noEmit` then `npx eslint <file>`  |
| `package.json` / `.js` / `.jsx`                 | `npx eslint <file>`                      |
| `requirements.txt` / `.py`                      | `ruff check .` (or `python -m pylint .`) |
| `go.mod` / `.go`                                | `go vet ./...`                           |
| `pom.xml` / `build.gradle` / `build.gradle.kts` | `mvn compile -q` or `./gradlew check`    |
| `Package.swift` / `.xcodeproj` / `.swift`       | `swiftlint lint --path <file>`           |
| `Gemfile` / `.rb`                               | `rubocop <file>`                         |
| `CMakeLists.txt` / `Makefile`                   | `cmake --build build/` or `make`         |

Run from the project root. If the tool reports errors:
- Fix each reported error before proceeding
- Re-run the tool once more if errors persist
- If errors remain after two fix-and-rerun cycles, stop and report the remaining errors to the user

Note: this step runs only the primary analysis tool. For a full formatting check, use the `analyze-code` skill.

## Test Execution

Execute the test files found in Test Discovery:

```bash
# Dart
dart test test/my_feature_test.dart
flutter test test/my_widget_test.dart

# Rust
cargo test [test_name]

# JavaScript/TypeScript
npx jest <file>
npx vitest run <file>

# Python
python -m pytest tests/test_feature.py -v

# Go
go test ./... -run TestFunctionName
```

If all tests pass: report the fix as complete with a summary.

If any test fails:
- Re-read the failing test to understand expected behavior
- Perform one additional root cause analysis (Context Gathering → Root Cause Analysis) on the failing test
- Apply a targeted fix and re-run the failing test
- If the test still fails after this second pass, stop and report both the original fix and the newly failing test to the user, and ask for guidance

## Summary

After completing all steps, display a summary block:

| Field            | Value                      |
|------------------|----------------------------|
| **Root cause**   | Brief one-line description |
| **Fix applied**  | What was changed           |
| **Verification** | Pass / Fail / Skipped      |
| **Tests**        | Pass / Fail / Not found    |

## Additional Resources

- **`../../references/analyze-tools.md`** — Full language → tool mapping, flags, and common error patterns
- **`references/debugging-patterns.md`** — Common root cause patterns by error category (null pointer, type mismatch, async race, import cycle, etc.)

### Code Analyzer Agent

For large-scale analysis — more than 5 files affected, or when the error spans multiple packages — trigger the `code-analyzer` agent using the `Agent` tool with `subagent_type: "debugging-workflow:code-analyzer"`. It runs the full analysis pipeline autonomously and returns a structured report.
