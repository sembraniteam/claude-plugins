# debugging-workflow

Systematic debugging plugin for Claude Code. Guides Claude through a structured debugging process: pre-flight checklist → context gathering → git diff analysis → test discovery → root cause analysis → targeted fix → multi-language verification.

## Features

- **`/debugging-workflow:debug`** — Full debugging workflow triggered as a slash command
- **`analyze-code` skill** — Auto-activating code analysis with language detection
- **`code-analyzer` agent** — Autonomous multi-language static analysis reporter

## Supported Languages

Auto-detects and runs analysis for:

| Language       | Tools                                            |
|----------------|--------------------------------------------------|
| Dart / Flutter | `dart analyze`, `flutter analyze`, `dart format` |
| Rust           | `cargo check`, `cargo clippy`, `rustfmt`         |
| TypeScript     | `tsc --noEmit`, `eslint`, `prettier`             |
| JavaScript     | `eslint`, `prettier`                             |
| Go             | `go vet`, `gofmt`                                |
| Python         | `ruff`, `pylint`, `mypy`                         |
| Java           | `mvn compile`                                    |
| Kotlin         | `ktlint`, `./gradlew check`                      |
| Swift          | `swiftlint`                                      |
| Ruby           | `rubocop`                                        |
| C/C++          | `clang-tidy`, `cppcheck`                         |

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

### Debug a specific error

```
/debugging-workflow:debug Null pointer exception at UserRepository.dart:42:
E/flutter (1234): #0      UserRepository.getUser (package:myapp/data/user_repository.dart:42:15)
```

### Debug without an error message

```
/debugging-workflow:debug
```
Claude will ask what's misbehaving and investigate from there.

### Standalone code analysis

```
Analyze my code before I commit.
Run dart analyze on this project.
Check for TypeScript errors.
```

### Full project audit via agent

```
Run a full code analysis on this project.
Check everything before I open a PR.
```

## Configuration (optional)

Create `.claude/debugging-workflow.local.md` in your project root to customize behavior:

```markdown
---
lint_config_path: "config/analysis_options.yaml"
skip_verification: false
---
```

| Field               | Type    | Default | Description                                                                                                    |
|---------------------|---------|---------|----------------------------------------------------------------------------------------------------------------|
| `lint_config_path`  | string  | `""`    | Path to a custom lint/analysis config, relative to project root. Passed to the language tool as a config flag. |
| `skip_verification` | boolean | `false` | Set `true` to skip the static analysis step (Step 7) entirely.                                                 |

A template is at `skills/analyze-code/examples/debugging-workflow.local.md`.

> This file should not be committed — it's already in `.gitignore` via `.claude/*.local.md`.

---

## Debugging Workflow Steps

1. **Pre-flight checklist** — Creates a visible todo list for the full session
2. **Parse error** — Extracts file, line, error type from stack trace
3. **Gather context** — Reads source files at error origin and upstream dependencies
4. **Git diff** — Inspects recent changes that may have introduced the bug
5. **Find tests** — Locates related test files for the affected code
6. **Root cause** — States the exact cause before touching any code
7. **Fix** — Applies a targeted fix following language best practices
8. **Verify** — Runs language-appropriate analyze/lint tools until clean
9. **Run tests** — Executes related tests to confirm the fix holds

## Plugin Structure

```
debugging-workflow/
├── .claude-plugin/
│   └── plugin.json
├── skills/
│   ├── debug/
│   │   ├── SKILL.md                          # Main slash command
│   │   └── references/
│   │       ├── analyze-tools.md              # Language → tool mapping
│   │       └── debugging-patterns.md         # Root cause pattern library
│   └── analyze-code/
│       ├── SKILL.md                          # Auto-activating analysis skill
│       └── examples/
│           └── debugging-workflow.local.md   # Settings template (copy to .claude/)
├── agents/
│   └── code-analyzer.md                      # Autonomous analysis agent
└── README.md
```
