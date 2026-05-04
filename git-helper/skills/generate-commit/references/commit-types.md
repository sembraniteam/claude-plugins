# Conventional Commit Types — Detailed Reference

## Type Definitions

### feat
**New feature for the user** — not a new feature for a build script or internal tool.

✅ Use for:
- Adding a new API endpoint
- Adding a new UI component or screen
- Implementing a new user-facing capability

❌ Do not use for:
- Adding a new Makefile target
- Adding a CI step
- Adding a new test helper

---

### fix
**Bug fix for the user** — not a fix to a build script or internal tooling.

✅ Use for:
- Fixing a crash reported by users
- Correcting wrong output in a user-facing feature
- Fixing a data-processing bug that affects results

❌ Do not use for:
- Fixing a broken test (use `test`)
- Fixing a CI pipeline step (use `ci`)
- Fixing a typo in a comment (use `refactor` or `docs`)

---

### docs
**Documentation changes only.**

✅ Use for:
- Updating README.md
- Adding or editing code comments (JSDoc, docstrings)
- Updating API documentation
- Editing CONTRIBUTING.md or CHANGELOG.md manually

❌ Do not use for:
- Changing production code alongside docs (split into two commits)

---

### refactor
**Production code restructured without behavior change.**

✅ Use for:
- Renaming variables, functions, or files
- Extracting a method into a utility
- Reorganizing module structure
- Improving readability without changing output

❌ Do not use for:
- Changes that fix a bug (use `fix`)
- Changes that add functionality (use `feat`)

---

### test
**Tests added or refactored; no production code changed.**

✅ Use for:
- Adding unit tests for existing functionality
- Refactoring a test suite for clarity
- Adding integration or e2e test coverage

❌ Do not use for:
- Fixing production code to make tests pass (use `fix`)

---

### chore
**Non-production maintenance tasks.**

✅ Use for:
- Updating grunt/gulp/make tasks
- Updating `.gitignore` or `.editorconfig`
- Updating tooling configuration (ESLint, Prettier, tsconfig)
- Non-dependency-bump package.json changes

❌ Do not use for:
- Dependency version bumps (use `bump`)
- CI config changes (use `ci`)

---

### ci
**CI/CD configuration changes.**

✅ Use for:
- Modifying `.github/workflows/*.yml`
- Updating `.gitlab-ci.yml`, `Jenkinsfile`, `Dockerfile`
- Adding or removing CI steps
- Updating deployment scripts

---

### perf
**Performance improvement.**

✅ Use for:
- Reducing query execution time
- Caching expensive computations
- Reducing bundle size
- Memory usage optimization

---

### revert
**Reverting a previous commit.**

Format: `revert: revert "<original subject>"`

Include in body:
```
This reverts commit <hash>.
Reason: <why this commit is being reverted>
```

---

### bump
**Dependency version update/increment.**

✅ Use for:
- `npm update`, `pip install --upgrade`, `go get -u`
- Updating lock files (`package-lock.json`, `yarn.lock`, `go.sum`)
- Bumping project version in `package.json` or `pyproject.toml`

---

## Breaking Change Rules

Mark as breaking (`type!:` + `BREAKING CHANGE` footer) when:

1. **API removal or incompatible change**: endpoint removed, function signature changed in a non-backward-compatible way
2. **Config key renamed or removed**: environment variables, config file keys
3. **Database schema change**: requires migration, breaks existing data access
4. **Output format change**: JSON response shape changed, CSV columns renamed
5. **Explicit `BREAKING CHANGE` in diff**: a comment or commit message body

### Format

```
feat!: redesign authentication API

BREAKING CHANGE: /api/v1/auth/login has been removed.
Migrate to /api/v2/auth/login which returns a JWT instead of a session cookie.
```

---

## Ambiguous Cases

| Situation | Recommended type | Rationale |
|-----------|-----------------|-----------|
| Fix a bug AND improve performance | `fix` | Bug fix is higher user impact |
| Add a test AND fix the bug it covers | Split into two commits | Keeps history clean |
| Update README and fix a typo in code | Split into two commits | `docs` + `fix` |
| Add logging to debug a production issue | `chore` | Not user-visible feature |
| Add logging as a user-visible audit trail | `feat` | User-facing capability |
| Move files to a new directory | `refactor` | No behavior change |
| Remove dead code | `refactor` | No behavior change |
| Update a dependency to fix a security vuln | `fix` or `bump` | `fix` if it's a security patch, `bump` otherwise |

---

## Subject Line Rules

- Max 72 characters total (type + scope + colon + space + description)
- Imperative mood: "add", "fix", "remove" — not "adds", "fixed", "removing"
- No capital first letter in description
- No period at the end
- Reference ticket numbers in the footer, not the subject: `Refs: #123`

## Scope Rules

- Lowercase only
- No spaces: use hyphens (`user-auth` not `user auth`)
- Should match a module, layer, or domain: `auth`, `api`, `ui`, `db`, `cli`
- Omit scope if the change is cross-cutting or repo-wide
