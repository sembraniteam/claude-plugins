---
name: generate-branch
description: 'This skill should be used when the user invokes /git-helper:generate-branch, or asks to "create a branch", "name my branch", "what should I name this branch", "generate a branch name for this ticket", "help me create a branch for #42", or describes work they are about to start and needs a branch name. Applies team naming conventions with prefix rules (feature/, bugfix/, hotfix/, release/, chore/, bump/) and optional ticket number support.'
argument-hint: "[#ticket]"
allowed-tools: ["Bash"]
version: 0.1.0
---

# Generate Branch Name

Generate a valid git branch name following the team's branch naming conventions. Display the result for the user to copy and run manually — never create the branch automatically.

## Step 1: Read Settings

Check if `.claude/git-helper.local.md` exists. If it does, parse the YAML frontmatter to get `default_branch_prefix`:

```bash
SETTINGS=".claude/git-helper.local.md"
if [ -f "$SETTINGS" ]; then
  FRONTMATTER=$(sed -n '/^---$/,/^---$/{ /^---$/d; p; }' "$SETTINGS")
  DEFAULT_PREFIX=$(echo "$FRONTMATTER" | grep '^default_branch_prefix:' | sed 's/default_branch_prefix: *//' | sed 's/^"\(.*\)"$/\1/')
fi
```

Use `default_branch_prefix` as the fallback prefix when the work description does not clearly indicate a type (Step 2).

## Step 2: Collect Input

Collect the following from the invocation and conversation context:

1. **Work description** — what the user says they will work on
2. **Ticket number** — from the argument, in `#123` format (optional)

If the work description is unclear, ask one brief question before proceeding.

## Step 3: Select Branch Prefix

Choose the prefix that best matches the nature of the work. If ambiguous and `default_branch_prefix` is set in settings, use it as the fallback:

| Prefix | Aliases | When to use |
|--------|---------|-------------|
| `feature/` | `feat/` | New feature development |
| `bugfix/` | `fix/` | Bug fixes (non-urgent) |
| `hotfix/` | — | Urgent production fixes |
| `release/` | — | Release preparation branches |
| `chore/` | — | Non-code tasks: dependency updates, docs, tooling |
| `bump/` | — | Version/dependency increment |

**Selection rules:**
- Use `hotfix/` only for critical, time-sensitive production fixes
- Use `release/` only when preparing a version release (e.g., `release/v1.2.0`)
- Use `bump/` specifically for dependency/version bumps, not general chores
- Default to `feature/` when the work adds new functionality
- Default to `chore/` when the work does not change production code

## Step 4: Build the Description Slug

Transform the work description into a slug:

1. Extract the core intent (2–5 words)
2. Convert to lowercase
3. Replace spaces and special characters with hyphens
4. Remove leading/trailing hyphens
5. Remove consecutive hyphens

**If a ticket number is provided** (`#123`), strip the `#` and prepend to slug: `123-<slug>`

**If a scope is implied by the description**, use `type/scope/description` format. For scope decision rules and CI/CD alias compatibility, see **`references/branch-rules.md`** — Branch Formats.

## Step 5: Apply Naming Rules

Validate the generated name against all constraints:

| Rule | Valid | Invalid |
|------|-------|---------|
| Lowercase only | `feature/add-login` | `feature/Add-Login` |
| Hyphens to separate words | `fix/header-bug` | `fix/header_bug` |
| No special characters | `feat/oauth2-login` | `feat/oauth2@login` |
| No consecutive hyphens | `feature/new-login` | `feature/new--login` |
| No leading/trailing hyphens in slug | `fix/header-bug` | `fix/-header-bug-` |
| Dots only for version numbers | `release/v1.2.0` | `feature/new.login` |
| No spaces | `feature/add-login` | `feature/add login` |

## Step 6: Display the Result

Present the branch name in a code block, then show the ready-to-run command:

```
feature/123-add-oauth2-login
```

```bash
git checkout -b feature/123-add-oauth2-login
```

If multiple interpretations are valid (e.g., both `bugfix/` and `hotfix/` could apply), present the primary recommendation and one alternative:

```
Recommended: bugfix/123-fix-login-crash
Alternative: hotfix/123-fix-login-crash  ← use this if the fix is urgent
```

## Examples

| User description | Ticket | Generated branch |
|-----------------|--------|-----------------|
| "Add dark mode toggle to settings" | `#42` | `feature/42-add-dark-mode-toggle` |
| "Fix crash when opening app offline" | `#38` | `bugfix/38-fix-offline-crash` |
| "Urgent: security patch for auth bypass" | — | `hotfix/security-patch-auth-bypass` |
| "Prepare v2.0.0 release" | — | `release/v2.0.0` |
| "Update dependencies" | — | `chore/update-dependencies` |
| "Bump lodash to 4.17.21" | `#15` | `bump/15-lodash-4.17.21` |
| "Refactor auth module" (auth scope) | — | `chore/auth/refactor-module` |

## Additional Resources

- **`references/branch-rules.md`** — Full naming rules with edge cases, regex patterns, and CI/CD compatibility notes
