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

## Workflow

### Step 1: Check Settings File

Before doing anything else, check whether `.claude/changelog-manager.local.md` exists:

```bash
[ -f ".claude/changelog-manager.local.md" ] && echo "exists" || echo "missing"
```

**If the file is missing**, use the Skill tool to invoke `changelog-manager:changelog-config` now to create it. That skill will collect the user's preferred languages and platforms and write the file. Wait for it to complete before continuing.

**If the file exists**, read it to load the current `languages` and `platforms` values — these will be used as defaults in the pre-flight questions below.

After the settings file is confirmed to exist, proceed to Step 2.

### Step 2: Pre-flight Checklist

Before running any scripts or reading git history, create a todo list and ask the user these questions **all at once**:

1. **Release notes** — Do you want release notes generated after the changelog is created?
2. **Platform** *(only if answer to #1 is Yes)* — Which platform(s)? Show the current value from `.claude/changelog-manager.local.md` as the default suggestion.
   - A. App Store
   - B. Play Store
   - C. Web
   - Accept single or multiple answers (e.g., "A", "A and B", "all").
3. **Languages** *(only if answer to #1 is Yes)* — Which languages should the release notes be written in? Show the current value from `.claude/changelog-manager.local.md` as the default suggestion. (Locale codes in `language_REGION` format separated by commas, e.g. `en_US, id_ID`)
4. **Git tag** — Do you want to create a new git tag based on the computed version number?

Wait for the user's answers before continuing. After receiving them, display a summary:

> **Your selections:**
> - Release notes: Yes / No
> - Platform(s): App Store / Play Store / Web *(omit if release notes = No)*
> - Languages: `en_US, id_ID` *(omit if release notes = No)*
> - Git tag: Yes / No

Then proceed to Step 3.

### Step 3: Analyze Commits

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

### Step 4: Map Commits to CHANGELOG Sections

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

### Step 5: Build the Version Block

```markdown
## [v1.2.0] - 2025-01-15

### Breaking Changes
- Removed deprecated auth endpoint

### Added
- Dark mode support (#42)

### Fixed
- Login crash on empty password field (#38)
```

### Step 6: Write CHANGELOG.md

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

### Step 7: Report to User

Summarize what was done:
- Previous version → next version (e.g., `v1.1.0 → v1.2.0`)
- Count of entries per category
- Whether CHANGELOG.md was created or updated

### Step 8: Create Git Tag (if confirmed in Step 2)

If the user answered **Yes** to git tag in Step 2, run:

```bash
git tag <next_version>
```

Use the `next_version` value from the script output in Step 3 (e.g., `v1.2.0`). Show the command and its output. Do not push the tag — only create it locally.

### Step 9: Generate Release Notes (if confirmed in Step 2)

If the user answered **Yes** to release notes in Step 2, use the Skill tool to invoke `changelog-manager:generate-release-notes` now.

Map the platform answers collected in Step 2:
- A → `appstore`
- B → `playstore`
- C → `web`

Pass the platform(s) and language codes as conversation context. These values override whatever is in `.claude/changelog-manager.local.md` for this run. Do not ask for platform or language again — use the answers from Step 2.

If the user answered **No** to both git tag and release notes in Step 2, stop after Step 7.

## Rules

- `bump`, `test`, `ci`, `chore`, and `docs` commits are always excluded — never add them manually
- Breaking changes (commits ending with `!` or containing `BREAKING CHANGE`) override other categories and always appear in `### Breaking Changes`
- Preserve all existing CHANGELOG entries unchanged when updating

## Additional Resources

- **`references/keep-a-changelog.md`** — Full Keep a Changelog format specification, section ordering, and versioning examples
