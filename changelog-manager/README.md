# changelog-manager

A Claude Code plugin that automatically generates and updates `CHANGELOG.md` and release notes from git commit history, with bilingual and platform-specific support for App Store, Play Store, and web.

## Features

- Analyzes git commits following [Conventional Commits](https://www.conventionalcommits.org/) format
- Auto-computes next semantic version (MAJOR / MINOR / PATCH)
- Generates or updates `CHANGELOG.md` following [Keep a Changelog](https://keepachangelog.com) standard
- Creates platform-specific release notes with enforced character limits
- Bilingual output — configurable languages per project
- Friendly, non-technical language for general users
- Validates changelog quality: semver accuracy, entry clarity, character limits

## Prerequisites

- Git repository with conventional commits
- `jq` — [install](https://jqlang.github.io/jq/download/) (`brew install jq` or `apt install jq`)
- Python 3 (standard library only, no pip install needed)

## Skills

### `/changelog-manager:generate-changelog`

Generates or updates `CHANGELOG.md` from git history.

**Triggers:** "generate changelog", "update changelog", "add changelog entry", "prepare new version", "bump version"

**Workflow:**
1. Runs `analyze-commits.sh` to get structured commit JSON
2. Maps commits to Keep a Changelog sections
3. Computes next semantic version
4. Creates or prepends to `CHANGELOG.md`

---

### `/changelog-manager:generate-release-notes`

Creates bilingual, platform-specific release notes from the latest `CHANGELOG.md` entry.

**Triggers:** "generate release notes", "App Store release", "Play Store release", "web announcement", "bilingual release notes"

**Output files:**

| Platform   | File                      | Char Limit       |
|------------|---------------------------|------------------|
| Play Store | `RELEASE_NOTES_PLAYSTORE` | 500 / language   |
| App Store  | `RELEASE_NOTES_APPSTORE`  | 4,000 / language |
| Web        | `RELEASE_NOTES`           | No limit         |

**Requires:** `CHANGELOG.md` to exist. Run `generate-changelog` first.

Claude reads `CHANGELOG.md` itself and decides how to present each entry — as `--item` bullets, or, for a single small change or a handful of closely-themed changes, folded into a friendly one- or two-sentence summary with no bullet list at all.

---

### `/changelog-manager:changelog-config`

Configures languages and platforms for your project.

**Triggers:** "configure changelog", "set changelog languages", "add language to release notes", "changelog settings"

**Creates:** `.claude/changelog-manager.local.md`

## Configuration

Create `.claude/changelog-manager.local.md` in your project (or run `/changelog-manager:changelog-config`):

```yaml
---
languages:
  - code: en_US
    name: English
  - code: id_ID
    name: Indonesian
platforms:
  - playstore
  - appstore
  - web
---
```

This file is gitignored automatically.

## Agents

### `changelog-reviewer`

Reviews changelog and release notes quality on request.

**Triggers:** "review changelog", "check changelog quality", "validate release notes", "is my semver correct"

**Checks:**
- Semver bump correctness
- Keep a Changelog format compliance
- Entry clarity (flags vague messages like "Fix bug")
- Missing entries from git history
- Release notes character limits per platform
- Summary length (minimum 100 characters)

---

### `release-notes-validator`

Auto-trims release notes to fit platform character limits. Invoked automatically by `generate-release-notes` on character limit errors, or on demand.

**Triggers:** character limit error from the script, "trim release notes to fit", "validate release note lengths", "fix character count", "auto-trim items"

**What it does:**
1. Parses the planned `generate-release-notes.py` command from context
2. Calculates per-language character counts
3. Removes lowest-priority items from the end until the section fits
4. Appends a translated closing phrase ("And many more improvements inside!") when items are dropped
5. Re-runs the adjusted command and reports what changed

**Supported platforms:** Play Store (500 chars/lang), App Store (4,000 chars/lang)

## Commit Type Mapping

| Conventional Commit                        | CHANGELOG Section | Version Bump |
|--------------------------------------------|-------------------|--------------|
| `feat:`                                    | Added             | MINOR        |
| `fix:`                                     | Fixed             | PATCH        |
| `perf:`                                    | Changed           | PATCH        |
| `refactor:`                                | Changed           | PATCH        |
| `revert:`                                  | Reverted          | PATCH        |
| `<any type>!:` / `BREAKING CHANGE:` footer | Breaking Changes  | MAJOR        |
| `bump:`, `test:`, `ci:`, `chore:`, `docs:` | *(ignored)*       | —            |

Native `git revert` commits (`Revert "..."`, no conventional prefix) are also detected and mapped to Reverted / PATCH. Any type marked with `!` is treated as breaking (MAJOR) even if its own type would otherwise be ignored (e.g. `chore!:`).

## Installation

### Option 1: Install from this repo (marketplace)

```bash
# Add this repo as a marketplace source
/plugin marketplace add sembraniteam/claude-plugins

# Install the plugin
/plugin install changelog-manager@sembraniteam-claude-plugins
```

### Option 2: Local install (development)

```bash
# Clone the repo
git clone https://github.com/sembraniteam/claude-plugins.git

# Add the local repo as a marketplace
/plugin marketplace add /path/to/claude-plugins

# Install
/plugin install changelog-manager@sembraniteam-claude-plugins
```

## License

MIT
