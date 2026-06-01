---
name: generate-changelog
description: This skill should be used when the user asks to "generate changelog", "update changelog", "create changelog", "add changelog entry", "summarize commits for changelog", "prepare a new version", or "bump version". Also trigger when the user mentions updating CHANGELOG.md or documenting recent commits.
version: 0.2.0
license: MIT
---

# Generate Changelog

Generate or update `CHANGELOG.md` by analyzing git commit history and formatting entries following the [Keep a Changelog](https://keepachangelog.com) standard with automatic semantic version bumping.

## Prerequisites

- Git repository with conventional commits
- `jq` installed (`brew install jq` or `apt install jq`)

## Workflow

### Step 1: Analyze Commits

Always run the commit analysis script first — it outputs structured JSON:

```bash
bash $CLAUDE_PLUGIN_ROOT/scripts/analyze-commits.sh
```

If the script prints `No changes since last release.` (plain text, not JSON), inform the user and stop.

The JSON output contains:

| Field          | Description                                            |
|----------------|--------------------------------------------------------|
| `last_tag`     | Last git tag, or `v0.0.0` if none                      |
| `next_version` | Computed next semver tag                               |
| `date`         | Today's date (YYYY-MM-DD)                              |
| `commits`      | Array of `{ category, message, pr, breaking }` objects |

### Step 2: Map Commits to CHANGELOG Sections

| Commit Category | CHANGELOG Section      |
|-----------------|------------------------|
| `breaking`      | `### Breaking Changes` |
| `added`         | `### Added`            |
| `changed`       | `### Changed`          |
| `fixed`         | `### Fixed`            |
| `reverted`      | `### Reverted`         |

Omit empty sections entirely. The script does not currently produce `Deprecated`, `Removed`, or `Security` categories — if those appear in a future script version, map them to `### Deprecated`, `### Removed`, and `### Security` respectively.

Format each entry as:
- `- <message> (#<pr>)` — when PR number is present
- `- <message>` — when PR number is absent

Omit empty sections entirely.

### Step 3: Build the Version Block

```markdown
## [v1.2.0] - 2025-01-15

### Breaking Changes
- Removed deprecated auth endpoint

### Added
- Dark mode support (#42)

### Fixed
- Login crash on empty password field (#38)
```

### Step 4: Write CHANGELOG.md

**If CHANGELOG.md does not exist**, create it from scratch:

```markdown
# Changelog

All notable changes to this project will be documented in this file.

This project adheres to [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

<!-- Next release goes here -->

## [v1.2.0] - 2025-01-15

### Added
- Dark mode support (#42)
```

**If CHANGELOG.md already exists**, prepend the new version block after the `## [Unreleased]` section (or immediately after the header if no Unreleased section exists). Never overwrite or remove existing entries.

### Step 5: Report to User

Summarize what was done:
- Previous version → next version (e.g., `v1.1.0 → v1.2.0`)
- Count of entries per category
- Whether CHANGELOG.md was created or updated

### Step 6: Offer to Generate Release Notes

After reporting, ask:

> Would you like to generate release notes for this version?
> - **Yes** — continue to generate release notes
> - **No** — done

If the user says **Yes**, ask two follow-up questions **in order**:

**Question 1 — Platform:**

> Which platform(s) do you want to generate release notes for?
> A. App Store
> B. Play Store
> C. Web

Accept single or multiple answers (e.g., "A", "A and B", "all"). Map answers to platform identifiers:
- A → `appstore`
- B → `playstore`
- C → `web`

**Question 2 — Languages:**

> Which languages should the release notes be written in? (Type ISO 639-1 codes separated by commas. Example: `en, id`)

Wait for the user's free-text answer. Accept a comma-separated list of ISO 639-1 language codes (e.g., `en`, `id`, `en, id, ja`). Do not suggest or assume a default — the user must type this explicitly.

**Then invoke `changelog-manager:generate-release-notes`**, passing the platform(s) and language codes from the user's answers as conversation context. These values override whatever is in `.claude/changelog-manager.local.md` for this run.

## Rules

- `bump`, `test`, `ci`, `chore`, and `docs` commits are always excluded — never add them manually
- Breaking changes (commits ending with `!` or containing `BREAKING CHANGE`) override other categories and always appear in `### Breaking Changes`
- Preserve all existing CHANGELOG entries unchanged when updating

## Additional Resources

- **`references/keep-a-changelog.md`** — Full Keep a Changelog format specification, section ordering, and versioning examples
