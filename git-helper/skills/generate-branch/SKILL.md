---
name: generate-branch
description: This skill should be used when the user invokes /git-helper:generate-branch, asks to "create a branch name", "name my branch", "what should I name this branch", "suggest a branch name", "what prefix should I use", "what branch should I create for this", "branch for ticket #123", "I'm working on #456, what branch name?", or describes work they are about to start and needs a branch name for it. Applies team naming conventions with prefix rules (feature/, bugfix/, hotfix/, release/, chore/, bump/).
argument-hint: "[work description]"
allowed-tools: ["Bash", "AskUserQuestion"]
---

# Generate Branch Name

Generate a valid git branch name following team naming conventions. When invoked directly by the user, this skill will ask to create and switch to the branch after generating the name. When invoked via the Skill tool by `generate-commit`, it outputs the branch name only — the calling skill owns the checkout step.

## Input Collection

Collect from the invocation and conversation context:
- **Work description** — what the user will work on (optional)
- **File paths** — from the argument, limits the diff to specific files (optional)

If no work description is provided, run these commands and infer a 2–5 word description from the staged diff (primary) or unstaged diff (secondary). Append `-- <files>` to scope diffs to specific paths. Do not ask — infer from diff:

```bash
git --no-pager log --oneline -10
git --no-pager status --short
git --no-pager diff [-- <files>]
git --no-pager diff --cached [-- <files>]
```

If the diff is empty and no description was provided, ask the user for a one-sentence description of the work.

If the description is provided but unclear (e.g., a single ambiguous word like "fix" with no additional context), ask one brief clarifying question before proceeding.

## Branch Construction

**Select prefix** — choose the best match; default to `feature/` when ambiguous:

| Prefix     | When to use                                  |
|------------|----------------------------------------------|
| `feature/` | New feature development                      |
| `bugfix/`  | Non-urgent bug fix                           |
| `hotfix/`  | Urgent production fix                        |
| `release/` | Release preparation (e.g., `release/v1.2.0`) |
| `chore/`   | Non-code tasks: docs, tooling, config        |
| `bump/`    | Dependency/version update                    |

**Build the slug** from the work description:
1. Extract 2–5 core words, lowercase, replace spaces and special chars with hyphens
2. Remove leading/trailing and consecutive hyphens
3. If scope implied by description: use `type/scope/slug` format

For the `type/scope/slug` three-part format and full naming rules, see **`references/branch-rules.md`**.

**Naming constraints:**

| Rule                          | Valid               | Invalid              |
|-------------------------------|---------------------|----------------------|
| Lowercase only                | `feature/add-login` | `feature/Add-Login`  |
| Hyphens as word separator     | `fix/header-bug`    | `fix/header_bug`     |
| No special characters         | `feat/oauth2-login` | `feat/oauth2@login`  |
| No consecutive hyphens        | `feature/new-login` | `feature/new--login` |
| Dots only for version numbers | `release/v1.2.0`    | `feature/new.login`  |

## Output

Present the branch name in a fenced code block, then the ready-to-run command on its own line:

```
feature/add-oauth2-login
```

```bash
git checkout -b feature/add-oauth2-login
```

If multiple prefixes are valid, show a primary recommendation and one alternative:

```
Recommended: bugfix/fix-login-crash
Alternative: hotfix/fix-login-crash  ← use this if the fix is urgent
```

**When invoked via the Skill tool by another skill** (e.g., `generate-commit`): always output the branch name in the fenced code block so the calling skill can extract it. Do not ask the user to confirm checkout — the calling skill owns that step.

## Execution

**When invoked directly by the user** (not via the Skill tool): after displaying the branch name, use `AskUserQuestion` to ask:

> "Do you want me to create and switch to this branch now?"
> Options: Yes / No

If the user answers **Yes**, run `git checkout -b <branch-name>` immediately and display its output. Do not re-display the command for the user to run — just run it.

If the user answers **No**, leave the command displayed for the user to run manually.

## Examples

| User description                         | Generated branch                    |
|------------------------------------------|-------------------------------------|
| "Add dark mode toggle to settings"       | `feature/add-dark-mode-toggle`      |
| "Fix crash when opening app offline"     | `bugfix/fix-offline-crash`          |
| "Urgent: security patch for auth bypass" | `hotfix/security-patch-auth-bypass` |
| "Prepare v2.0.0 release"                 | `release/v2.0.0`                    |
| "Update dependencies"                    | `chore/update-dependencies`         |
| "Bump lodash to 4.17.21"                 | `bump/lodash-4.17.21`               |
| "Refactor auth module" (auth scope)      | `chore/auth/refactor-module`        |

## Additional Resources

- **`references/branch-rules.md`** — Full naming rules with edge cases, regex patterns, and CI/CD compatibility notes

### Scripts

- **`scripts/validate-branch.sh`** — Standalone utility for external/CI use, not invoked as part of this skill's workflow. Validates a branch name against team naming rules. Exit 0 = valid, exit 1 = invalid with reasons listed. Run as: `./scripts/validate-branch.sh <branch-name>`
