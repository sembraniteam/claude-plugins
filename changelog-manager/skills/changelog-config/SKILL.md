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

**Check existing settings** — if `.claude/changelog-manager.local.md` exists, read and display current settings before making changes.

**Collect languages and platforms** — if the request already specifies them, use directly. Otherwise, ask:
- Which languages should release notes be generated in?
- Which platforms should be targeted?

**Write settings file** — write YAML frontmatter only (no Markdown body required):

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

**Validate:**
- At least one language is present
- All platform values are from the valid list
- Language codes use `language_REGION` format (e.g. `en_US`, not `en`)
- If any English locale (`en_*`) is included, list it first — this ensures the English section appears before translated sections in the output file
- File is valid YAML

## Summary

After writing, display a summary block:

| Field         | Value                                  | Reason |
|---------------|----------------------------------------|--------|
| **Languages** | `en_US, id_ID`                         | N/A    |
| **Platforms** | `playstore, appstore`                  | N/A    |
| **File**      | `.claude/changelog-manager.local.md`   | N/A    |
| **Action**    | Created / Updated                      | N/A    |

Remind the user:
- The file is **gitignored** and should not be committed
- Run `generate-changelog` before `generate-release-notes` to ensure CHANGELOG.md is current

## Common Locale Codes

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
