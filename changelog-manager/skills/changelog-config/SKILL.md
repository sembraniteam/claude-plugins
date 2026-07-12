---
name: changelog-config
description: This skill should be used when the user asks to "configure changelog", "set changelog languages", "changelog settings", "setup changelog manager", "add a language to release notes", "change release notes language", "update changelog config", "set platforms for release notes", "show me my changelog settings", "what platforms are configured", or "view my changelog config".
argument-hint: "[language code] [platform]  e.g. en_US playstore"
allowed-tools: ["Read", "Write", "Bash"]
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

`playstore`, `appstore`, `web` — for output files and char limits per platform, see the Platform Reference table in `changelog-manager:generate-release-notes`'s `SKILL.md`.

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

Remind the user:
- The file is **gitignored** and should not be committed
- Run `generate-changelog` before `generate-release-notes` to ensure CHANGELOG.md is current

## Additional Resources

- **`references/locale-codes.md`** — Common locale codes and language names to suggest when asking about languages
