# Keep a Changelog — Format Reference

Source: https://keepachangelog.com/en/1.1.0/

## Guiding Principles

- Changelogs are for humans, not machines
- There should be an entry for every single version
- The same types of changes should be grouped
- Versions and sections should be linkable
- The latest version comes first
- The release date of each version is displayed
- Mention whether the project follows Semantic Versioning

## Standard Section Order

Within each version block, use this section order (omit empty sections):

1. `### Breaking Changes` — incompatible API changes (not in official spec but widely adopted)
2. `### Added` — new features
3. `### Changed` — changes in existing functionality
4. `### Deprecated` — soon-to-be removed features
5. `### Removed` — now removed features
6. `### Fixed` — bug fixes
7. `### Reverted` — reverted changes
8. `### Security` — vulnerability fixes

## File Structure

```markdown
# Changelog

All notable changes to this project will be documented in this file.

This project adheres to [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

<!-- Next release goes here -->

## [v1.1.0] - 2023-03-05

### Added
- Danish translation (#297)
- Simplified Chinese translation (#258)

### Changed
- Enhanced readability of diff output in the CLI

### Fixed
- Fix Markdown links to tag comparison URL with footnote-style links (#186)

## [v1.0.0] - 2017-06-20

### Added
- New visual identity by @tylerfortune8
- Version navigation
```

## Semantic Versioning Rules

Given version `MAJOR.MINOR.PATCH`:

| Commit Type | Version Bump |
|-------------|-------------|
| Breaking change (`!` or `BREAKING CHANGE`) | MAJOR +1, MINOR=0, PATCH=0 |
| `feat` | MINOR +1, PATCH=0 |
| `fix`, `perf`, `refactor`, `revert` | PATCH +1 |
| `bump`, `test`, `ci`, `chore`, `docs` | No bump (excluded) |

## Conventional Commits Mapping

| Conventional Commit Prefix | CHANGELOG Category |
|---------------------------|-------------------|
| `feat:` | Added |
| `fix:` | Fixed |
| `perf:` | Changed |
| `refactor:` | Changed |
| `revert:` | Reverted |
| `feat!:` or `BREAKING CHANGE` | Breaking Changes |
| `bump:`, `test:`, `ci:`, `chore:`, `docs:` | (ignored) |

## Version Linking (Optional Enhancement)

At the bottom of the file, add comparison links:

```markdown
[Unreleased]: https://github.com/user/repo/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/user/repo/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/user/repo/releases/tag/v1.0.0
```

## Common Mistakes to Avoid

- **Committing diffs** — readers can compare versions; state what changed in plain language
- **Passive voice** — use "Add X" not "X was added"
- **Vague entries** — "Fix bug" is useless; "Fix crash when user logs in with empty password" is useful
- **Inconsistent dates** — always use ISO 8601 format: `YYYY-MM-DD`
- **Overloading entries** — one entry per logical change, not one per file changed
