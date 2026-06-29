# git-helper

A Claude Code plugin that generates conventional commit messages and branch names following your team's naming conventions.

## Features

- Analyzes staged/unstaged git changes to generate conventional commit messages
- Detects breaking changes and formats `BREAKING CHANGE` footers automatically
- Generates branch names following team prefix and naming rules
- Supports optional scope and ticket number (`#123`) arguments
- Displays ready-to-run git commands with optional auto-execution after pre-flight confirmation

## Prerequisites

- Git repository

## Skills

### `/git-helper:generate-commit [file1 file2 ...]`

Generates a conventional commit message from the current git context.

**What it does:**
1. Reads optional settings from `.claude/git-helper.local.md`
2. Runs `git log`, `git status`, `git diff`, and `git diff --cached` to collect context
3. Selects the correct commit type based on the changes
4. Detects breaking changes
5. Formats the subject line, optional body, and `BREAKING CHANGE` footer
6. Displays the message and the ready-to-run `git commit` command

**Arguments:**
- `[file1 file2 ...]` — optional file paths to focus the diff on specific files

**Examples:**
```bash
# Analyze all staged/unstaged changes
/git-helper:generate-commit

# Focus on one file
/git-helper:generate-commit src/auth/login.ts

# Focus on multiple files
/git-helper:generate-commit src/auth/login.ts src/auth/logout.ts
```

---

### `/git-helper:generate-branch [#ticket]`

Generates a branch name following the team's branch naming conventions.

**What it does:**
1. Reads the user's description of the planned work
2. Selects the appropriate prefix
3. Formats the slug (lowercase, hyphens, no special chars)
4. Incorporates the ticket number if provided
5. Displays the branch name and the ready-to-run `git checkout -b` command

**Arguments:**
- `[work description]` — optional description of the planned work

**Example:**
```bash
/git-helper:generate-branch "Add dark mode toggle to settings"
# Output: feature/add-dark-mode-toggle
```

---

## Commit Types

| Type       | When to use                                      |
|------------|--------------------------------------------------|
| `feat`     | New feature for the user                         |
| `fix`      | Bug fix for the user                             |
| `docs`     | Documentation changes                            |
| `refactor` | Production code restructured, no behavior change |
| `test`     | Tests added or refactored                        |
| `chore`    | Non-production maintenance                       |
| `ci`       | CI configuration changes                         |
| `perf`     | Performance improvement                          |
| `revert`   | Reverting a previous commit                      |
| `bump`     | Dependency version update                        |

## Branch Prefixes

| Prefix     | Alias   | Use case              |
|------------|---------|-----------------------|
| `feature/` | `feat/` | New feature           |
| `bugfix/`  | `fix/`  | Non-urgent bug fix    |
| `hotfix/`  | —       | Urgent production fix |
| `release/` | —       | Release preparation   |
| `chore/`   | —       | Non-code tasks        |
| `bump/`    | —       | Dependency update     |

**Format:** `type/description` or `type/scope/description`

## Installation

```bash
cc --plugin-dir /path/to/git-helper
```

## License

MIT
