# Example: Feature Release Changelog Entry

A complete example showing commit input → `analyze-commits.sh` JSON output → CHANGELOG.md entry.

## Input: Commits Since Last Tag

Last tag: `v1.1.0`

```
b3f92a1 feat(auth): add OAuth2 login support (#47)
c4d81b2 feat(profile): add avatar upload with crop (#44)
a7e63c9 fix(login): prevent crash on empty password field (#45)
e2f14d8 fix(api): retry on 503 with exponential backoff (#46)
9b2c57a chore: update dependencies
d1a83f0 ci: add Android build to CI matrix
```

## Script Output

```bash
bash $CLAUDE_PLUGIN_ROOT/scripts/analyze-commits.sh
```

```json
{
  "last_tag": "v1.1.0",
  "next_version": "v1.2.0",
  "date": "2025-06-15",
  "commits": [
    { "category": "added", "message": "add OAuth2 login support", "pr": "47", "breaking": false },
    { "category": "added", "message": "add avatar upload with crop", "pr": "44", "breaking": false },
    { "category": "fixed", "message": "prevent crash on empty password field", "pr": "45", "breaking": false },
    { "category": "fixed", "message": "retry on 503 with exponential backoff", "pr": "46", "breaking": false }
  ]
}
```

`chore` and `ci` commits are excluded automatically.

## Output: CHANGELOG.md Entry

```markdown
## [v1.2.0] - 2025-06-15

### Added
- add OAuth2 login support (#47)
- add avatar upload with crop (#44)

### Fixed
- prevent crash on empty password field (#45)
- retry on 503 with exponential backoff (#46)
```

## CHANGELOG.md After Update

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [v1.2.0] - 2025-06-15

### Added
- add OAuth2 login support (#47)
- add avatar upload with crop (#44)

### Fixed
- prevent crash on empty password field (#45)
- retry on 503 with exponential backoff (#46)

## [v1.1.0] - 2025-05-01

### Added
- dark mode support (#40)
```

The new version block is prepended after `## [Unreleased]`. Existing entries are unchanged.

## Summary Output

| Field                | Value              | Reason                                    |
|----------------------|--------------------|-------------------------------------------|
| **Previous version** | `v1.1.0`           | N/A                                       |
| **Next version**     | `v1.2.0`           | MINOR bump — new `feat` commits, no break |
| **Entries added**    | `4`                | N/A                                       |
| **CHANGELOG.md**     | Updated            | N/A                                       |
| **Git tag**          | Not created        | N/A                                       |
| **Release notes**    | Not generated      | N/A                                       |
