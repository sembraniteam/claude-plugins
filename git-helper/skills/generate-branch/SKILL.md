---
name: generate-branch
description: This skill should be used when the user invokes /git-helper:generate-branch, asks to "create a branch name", "name my branch", "what should I name this branch", "suggest a branch name", "what prefix should I use", "what branch should I create for this", or describes work they are about to start and needs a branch name for it. Applies team naming conventions with prefix rules (feature/, bugfix/, hotfix/, release/, chore/, bump/).
argument-hint: "[#ticket] [work description]"
allowed-tools: ["Bash"]
---

# Generate Branch Name

Generate a valid git branch name following team naming conventions. This skill generates and displays the branch name only — running `git checkout -b` is always the caller's responsibility (either the user directly, or the `generate-commit` skill when invoking this skill via the Skill tool).

## Input Collection

Collect from the invocation and conversation context:
- **Work description** — what the user will work on (optional)
- **File paths** — from the argument, limits the diff to specific files (optional)

If no work description is provided, run the context script and infer a 2–5 word description from the staged diff (primary) or unstaged diff (secondary). Pass any file paths as arguments to scope the diff. Do not ask — infer from diff:

```bash
# All changes
bash "$CLAUDE_PLUGIN_ROOT/scripts/collect-context.sh"

# Scoped to specific files
bash "$CLAUDE_PLUGIN_ROOT/scripts/collect-context.sh" "src/auth/login.ts" "src/auth/logout.ts"
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

Present the branch name in a code block with the ready-to-run command:

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

## Summary

After generating the branch name, display a summary block:

| Field      | Value                      | Reason                        |
|------------|----------------------------|-------------------------------|
| **Branch** | `feature/add-oauth2-login` | N/A                           |
| **Prefix** | `feature/`                 | Why this prefix was selected  |

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
