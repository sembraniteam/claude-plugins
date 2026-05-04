---
name: changelog-config
description: This skill should be used when the user asks to "configure changelog", "set changelog languages", "changelog settings", "setup changelog manager", "add a language to release notes", "change release notes language", "update changelog config", or "set platforms for release notes".
version: 0.1.0
---

# Changelog Config

Create or update the changelog manager settings file at `.claude/changelog-manager.local.md`. This file controls which languages are used for release notes and which platforms are targeted.

## Settings File Location

```
<project-root>/.claude/changelog-manager.local.md
```

This file is gitignored by the plugin's `.gitignore` (`.claude/*.local.md` pattern). Do not commit it.

## Settings Format

```yaml
---
languages:
  - code: en
    name: English
  - code: id
    name: Indonesian
platforms:
  - playstore
  - appstore
  - web
---
```

### Field Reference

| Field | Required | Description |
|-------|----------|-------------|
| `languages` | Yes | Ordered list of language blocks |
| `languages[].code` | Yes | ISO 639-1 code (e.g. `en`, `id`, `fr`, `ja`, `ko`) |
| `languages[].name` | Yes | Human-readable name shown in output headings |
| `platforms` | Yes | List of target platforms |

### Valid Platform Values

| Value | Output File | Char Limit |
|-------|------------|------------|
| `playstore` | `RELEASE_NOTES_PLAYSTORE` | 500 / lang |
| `appstore` | `RELEASE_NOTES_APPSTORE` | 4,000 / lang |
| `web` | `RELEASE_NOTES` | No limit |

## Workflow

### Step 1: Check Existing Settings

Check if `.claude/changelog-manager.local.md` exists. If it does, read and display current settings to the user before making changes.

### Step 2: Collect Languages and Platforms

If the user's request already specifies languages and platforms, use them directly. Otherwise ask:
- Which languages should release notes be generated in?
- Which platforms should be targeted?

### Step 3: Write Settings File

Write the file with YAML frontmatter only (no markdown body required):

```yaml
---
languages:
  - code: en
    name: English
  - code: id
    name: Indonesian
platforms:
  - playstore
  - appstore
---
```

### Step 4: Validate

Confirm:
- At least one language is present
- All platform values are from the valid list
- Language codes are valid ISO 639-1 codes
- If English (`en`) is included, it is listed first — the script validates English items against CHANGELOG.md and skips validation for all other languages
- File is valid YAML

### Step 5: Report to User

Show the final settings and remind the user:
- The file is gitignored and should not be committed
- Run `generate-changelog` before `generate-release-notes` to ensure CHANGELOG.md is current

## Common Language Codes

Use the following as a reference when the user specifies a language by name rather than code:

| Code | Language |
|------|----------|
| `en` | English |
| `id` | Indonesian |
| `fr` | French |
| `de` | German |
| `ja` | Japanese |
| `ko` | Korean |
| `zh` | Chinese (Simplified) |
| `es` | Spanish |
| `pt` | Portuguese |
| `ar` | Arabic |
| `hi` | Hindi |
| `tr` | Turkish |
