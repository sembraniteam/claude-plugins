---
name: changelog-config
description: This skill should be used when the user asks to "configure changelog", "set changelog languages", "changelog settings", "setup changelog manager", "add a language to release notes", "change release notes language", "update changelog config", or "set platforms for release notes".
license: MIT
---

# Changelog Config

Create or update the changelog manager settings file at `.claude/changelog-manager.local.md`. This file controls which languages are used for release notes and which platforms are targeted.

## Settings File Location

```
<project-root>/.claude/changelog-manager.local.md
```

This file is **gitignored** by the plugin's `.gitignore` (`.claude/*.local.md` pattern). Do not commit it.

## Settings Format

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

### Field Reference

| Field              | Required | Description                                                              |
|--------------------|----------|--------------------------------------------------------------------------|
| `languages`        | Yes      | Ordered list of language blocks                                          |
| `languages[].code` | Yes      | Locale code in `language_REGION` format (e.g. `en_US`, `id_ID`, `ja_JP`) |
| `languages[].name` | Yes      | Human-readable name shown in output headings                             |
| `platforms`        | Yes      | List of target platforms                                                 |

### Valid Platform Values

| Value       | Output File               | Char Limit   |
|-------------|---------------------------|--------------|
| `playstore` | `RELEASE_NOTES_PLAYSTORE` | 500 / lang   |
| `appstore`  | `RELEASE_NOTES_APPSTORE`  | 4,000 / lang |
| `web`       | `RELEASE_NOTES`           | No limit     |

## Workflow

### Step 1: Check Existing Settings

Check if `.claude/changelog-manager.local.md` exists. If it does, read and display current settings to the user before making changes.

### Step 2: Collect Languages and Platforms

If the user's request already specifies languages and platforms, use them directly. Otherwise, ask:
- Which languages should release notes be generated in?
- Which platforms should be targeted?

### Step 3: Write Settings File

Write the file with YAML frontmatter only (no Markdown body required):

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
---
```

### Step 4: Validate

Confirm:
- At least one language is present
- All platform values are from the valid list
- Language codes use the `language_REGION` locale format (e.g. `en_US`, not `en`)
- If any English locale (`en_*`) is included, it is listed first — the script validates English items against CHANGELOG.md and skips validation for all other languages
- File is valid YAML

### Step 5: Report to User

Show the final settings and remind the user:
- The file is **gitignored** and should not be committed
- Run `generate-changelog` before `generate-release-notes` to ensure CHANGELOG.md is current

## Common Locale Codes

Use the following as a reference when the user specifies a language by name rather than code:

| Locale    | Language                     |
|-----------|------------------------------|
| `en_US`   | English (United States)      |
| `en_GB`   | English (United Kingdom)     |
| `id_ID`   | Indonesian (Indonesia)       |
| `fr_FR`   | French (France)              |
| `de_DE`   | German (Germany)             |
| `ja_JP`   | Japanese (Japan)             |
| `ko_KR`   | Korean (South Korea)         |
| `zh_CN`   | Chinese Simplified (China)   |
| `zh_TW`   | Chinese Traditional (Taiwan) |
| `es_ES`   | Spanish (Spain)              |
| `es_MX`   | Spanish (Mexico)             |
| `pt_BR`   | Portuguese (Brazil)          |
| `pt_PT`   | Portuguese (Portugal)        |
| `ar_SA`   | Arabic (Saudi Arabia)        |
| `hi_IN`   | Hindi (India)                |
| `tr_TR`   | Turkish (Turkey)             |
