---
name: generate-changelog
description: This skill should be used when the user asks to "generate changelog", "update changelog", "create changelog", "add changelog entry", "summarize commits for changelog", "prepare a new version", or "bump version". Also trigger when the user mentions updating CHANGELOG.md or documenting recent commits.
license: MIT
---

# Generate Changelog

Generate or update `CHANGELOG.md` by analyzing git commit history and formatting entries following the [Keep a Changelog](https://keepachangelog.com) standard with automatic semantic version bumping.

## Prerequisites

- Git repository with conventional commits
- `jq` installed (`brew install jq` or `apt install jq`)

## Settings Check

Check whether `.claude/changelog-manager.local.md` exists:

```bash
[ -f ".claude/changelog-manager.local.md" ] && echo "exists" || echo "missing"
```

**If missing** — invoke `changelog-manager:changelog-config` via Skill tool to create it. Wait for it to complete before continuing.

**If exists** — read the current `languages` and `platforms` values; use them as defaults in the pre-flight questions below.

## Pre-flight Questions

Ask all questions at once:

1. **Release notes** — Do you want release notes generated after the changelog is created?
2. **Platform(s)** *(only if #1 = Yes)* — Which platform(s)? Show current value from settings as default.
   - A. App Store
   - B. Play Store
   - C. Web
   - Accept single or multiple answers (e.g., "A", "A and B", "all").
3. **Languages** *(only if #1 = Yes)* — Which languages? Show current value from settings as default. (Locale codes in `language_REGION` format, e.g. `en_US, id_ID`)
4. **Git tag** — Do you want to create a new git tag based on the computed version?

After answers, confirm selections:

> **Your selections:**
> - Release notes: Yes / No
> - Platform(s): App Store / Play Store / Web *(omit if release notes = No)*
> - Languages: `en_US, id_ID` *(omit if release notes = No)*
> - Git tag: Yes / No

## Commit Analysis

Run the commit analysis script:

```bash
bash $CLAUDE_PLUGIN_ROOT/scripts/analyze-commits.sh
```

If the script prints `No changes since last release.`, inform the user and stop.

The JSON output contains:

| Field          | Description                                            |
|----------------|--------------------------------------------------------|
| `last_tag`     | Last git tag, or `v0.0.0` if none                      |
| `next_version` | Computed next semver tag                               |
| `date`         | Today's date (YYYY-MM-DD)                              |
| `commits`      | Array of `{ category, message, pr, breaking }` objects |

## Write CHANGELOG.md

**Map commits to sections:**

| Commit Category | CHANGELOG Section                          |
|-----------------|--------------------------------------------|
| `breaking`      | `### Breaking Changes`                     |
| `added`         | `### Added`                                |
| `changed`       | `### Changed`                              |
| `fixed`         | `### Fixed`                                |
| `reverted`      | `### Reverted`                             |
| `deprecated`    | `### Deprecated` *(future script version)* |
| `removed`       | `### Removed` *(future script version)*    |
| `security`      | `### Security` *(future script version)*   |

Omit empty sections. Format entries as:
- `- <message> (#<pr>)` when PR number is present
- `- <message>` when absent

**Build the version block:**

```markdown
## [v1.2.0] - 2025-01-15

### Breaking Changes
- Removed deprecated auth endpoint

### Added
- Dark mode support (#42)

### Fixed
- Login crash on empty password field (#38)
```

**If CHANGELOG.md does not exist** — create from scratch with header + `## [Unreleased]` section + new version block.

**If CHANGELOG.md exists** — prepend the new version block after `## [Unreleased]` (or after the header if no Unreleased section). Never overwrite or remove existing entries.

## Confirmed Actions

Execute in order, showing output for each:

1. **Create git tag** (if confirmed) — run `git tag <next_version>`. Show command and output. Do not push.
2. **Generate release notes** (if confirmed) — invoke `changelog-manager:generate-release-notes` via Skill tool. Map platform answers: A → `appstore`, B → `playstore`, C → `web`. Pass platform(s) and language codes as context — do not ask again.

If both git tag and release notes were No, stop after writing CHANGELOG.md.

## Summary

After completing all actions, display a summary block:

| Field                | Value                         | Reason                                   |
|----------------------|-------------------------------|------------------------------------------|
| **Previous version** | `v1.1.0`                      | N/A                                      |
| **Next version**     | `v1.2.0`                      | Semver bump based on commit types        |
| **Entries added**    | `3`                           | N/A                                      |
| **CHANGELOG.md**     | Created / Updated             | N/A                                      |
| **Git tag**          | `v1.2.0` / Not created        | N/A                                      |
| **Release notes**    | Generated / Not generated     | N/A                                      |

## Rules

- `bump`, `test`, `ci`, `chore`, and `docs` commits are always excluded — never add them manually
- Breaking changes (commits ending with `!` or containing `BREAKING CHANGE`) override other categories and always appear in `### Breaking Changes`
- Preserve all existing CHANGELOG entries unchanged when updating

## Additional Resources

- **`references/keep-a-changelog.md`** — Full Keep a Changelog format specification, section ordering, and versioning examples
