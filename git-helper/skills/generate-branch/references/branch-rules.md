# Branch Naming Rules — Detailed Reference

## Prefix Reference

| Prefix | Alias | Use case | Example |
|--------|-------|----------|---------|
| `feature/` | `feat/` | New feature development | `feature/add-login-page` |
| `bugfix/` | `fix/` | Non-urgent bug fix | `bugfix/fix-header-bug` |
| `hotfix/` | — | Urgent production fix | `hotfix/security-patch` |
| `release/` | — | Release preparation | `release/v1.2.0` |
| `chore/` | — | Non-code tasks, docs, tooling | `chore/update-dependencies` |
| `bump/` | — | Dependency version update | `bump/lodash-4.17.21` |

### Prefix Selection Guide

**`feature/` vs `chore/`**
- Does the change add or modify user-visible functionality? → `feature/`
- Is it purely internal (tooling, config, docs)? → `chore/`

**`bugfix/` vs `hotfix/`**
- Is the fix urgent and going directly to production without a full release cycle? → `hotfix/`
- Is it a normal fix that goes through the standard PR process? → `bugfix/`

**`bump/` vs `chore/`**
- Specifically updating a package version? → `bump/`
- Other non-code maintenance? → `chore/`

---

## Naming Rules

### Allowed Characters

| Characters | Rule |
|------------|------|
| `a-z` | Always allowed |
| `0-9` | Always allowed |
| `-` | Word separator |
| `.` | Only in version numbers (`release/v1.2.0`) |

### Forbidden Characters

| Characters | Reason |
|------------|--------|
| `A-Z` | Case sensitivity issues across platforms |
| `_` | Confusing with snake_case, some CI tools treat differently |
| `@`, `#`, `!`, spaces | Git does not allow in branch names |
| `/` at start or end | Reserved as path separator |

### Structural Rules

1. **No consecutive hyphens**: `feature/new--login` ❌ → `feature/new-login` ✅
2. **No leading hyphens in slug**: `feature/-new-login` ❌ → `feature/new-login` ✅
3. **No trailing hyphens in slug**: `feature/new-login-` ❌ → `feature/new-login` ✅
4. **No consecutive dots**: `release/v1..2.0` ❌ → `release/v1.2.0` ✅
5. **No leading/trailing dots**: `release/.v1.2.0` ❌

---

## Branch Formats

### Simple: `type/description`

Use when no scope or ticket is needed:
```
feature/add-dark-mode
bugfix/fix-login-crash
hotfix/security-patch
chore/update-eslint-config
```

### With Scope: `type/scope/description`

Use when the change is scoped to a module or domain:
```
feature/auth/add-oauth2-login
bugfix/api/fix-null-response
chore/ui/update-component-library
```

### With Ticket: `type/ticket-description`

Use when a ticket number is available (`#123` → `123`):
```
feature/123-add-dark-mode
bugfix/38-fix-login-crash
feature/issue-123-add-oauth2-login
```

### With Ticket and Scope: `type/scope/ticket-description`

Use for scoped changes with a ticket:
```
feature/auth/123-add-oauth2-login
bugfix/api/38-fix-null-response
```

---

## Ticket Number Formatting

User input `#123` is transformed to:
- Strip `#` → `123`
- Prepend to slug: `123-<slug>`
- Full example: `feature/123-add-oauth2-login`

Do not use `issue-` prefix unless the team explicitly uses that convention.

---

## Slug Construction Rules

Given a work description, construct the slug:

1. Extract the 2–5 most meaningful words
2. Lowercase everything
3. Replace spaces with `-`
4. Remove all non-alphanumeric, non-hyphen characters
5. Collapse consecutive hyphens to single `-`
6. Strip leading and trailing `-`

**Examples:**

| User description | Slug |
|-----------------|------|
| "Add OAuth2 login support" | `add-oauth2-login` |
| "Fix crash when app opens offline" | `fix-offline-crash` |
| "Update lodash to 4.17.21" | `lodash-4.17.21` (for `bump/`) |
| "Prepare release 2.0.0" | `v2.0.0` (for `release/`) |
| "Refactor authentication module" | `refactor-auth-module` |

---

## Release Branch Versioning

For `release/` branches, always use the `v` prefix on the version:

```
release/v1.0.0   ✅
release/1.0.0    ❌ (missing v prefix)
release/v1.2     ❌ (incomplete semver)
```

Dots are allowed in release slugs to represent version numbers. They are not allowed in any other prefix type.

---

## CI/CD Compatibility Notes

Some CI systems use branch name patterns for pipeline triggers:

- **GitHub Actions**: branch filter patterns like `feature/**`, `release/**`
- **GitLab CI**: `only: refs:` or `rules: if: $CI_COMMIT_BRANCH`
- **Jenkins**: branch-based multibranch pipeline naming

Consistent prefix usage ensures CI rules work correctly. Always use the primary prefix (e.g., `feature/`) rather than the alias (e.g., `feat/`) for maximum CI compatibility, unless the team has standardized on the alias.

---

## Common Mistakes

| Mistake | Example | Fix |
|---------|---------|-----|
| Uppercase letters | `Feature/Add-Login` | `feature/add-login` |
| Underscore | `feature/add_login` | `feature/add-login` |
| Ticket with `#` | `feature/#123-add-login` | `feature/123-add-login` |
| Too long slug | `feature/add-a-new-login-page-with-oauth2-and-sso` | `feature/add-oauth2-login` |
| No prefix | `add-login` | `feature/add-login` |
| Double hyphens | `feature/add--login` | `feature/add-login` |
