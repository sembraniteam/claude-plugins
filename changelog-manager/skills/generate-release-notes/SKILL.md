---
name: generate-release-notes
description: This skill should be used when the user asks to generate release notes, create release notes, prepare an App Store or Play Store release, write a web announcement, produce bilingual release notes, or update store listing copy. Relevant phrases include "generate release notes", "create release notes", "prepare App Store release", "prepare Play Store release", "bilingual release notes", "translate release notes", or references to RELEASE_NOTES, RELEASE_NOTES_APPSTORE, or RELEASE_NOTES_PLAYSTORE files.
license: MIT
---

# Generate Release Notes

Generate platform-specific, bilingual release notes from the latest entry in `CHANGELOG.md` using `generate-release-notes.py`. Produces separate output files per platform with enforced character limits and user-friendly language.

## Prerequisites

- `CHANGELOG.md` must exist with at least one version entry — invoke `generate-changelog` first if needed
- Python 3 (standard library only, no pip install)
- Settings at `.claude/changelog-manager.local.md` — invoke `changelog-config` if missing

## Platform Reference

| Platform    | Output File               | Char Limit         | Tone                   |
|-------------|---------------------------|--------------------|------------------------|
| `playstore` | `RELEASE_NOTES_PLAYSTORE` | 500 per language   | Concise, bullet-first  |
| `appstore`  | `RELEASE_NOTES_APPSTORE`  | 4,000 per language | Friendly, feature-rich |
| `web`       | `RELEASE_NOTES`           | No limit           | Detailed, full context |

## Context & Inputs

**Read settings** — read `.claude/changelog-manager.local.md`. If it does not exist, use defaults and notify the user:

```yaml
languages:
  - code: en_US
    name: English
platforms:
  - web
```

**Read CHANGELOG.md** — extract the latest version block (first `## [vX.Y.Z]` section):
- Version number and release date
- All categorized entries by section (Breaking Changes, Added, Changed, Fixed, Reverted)

## Generate Notes

For each platform, build and run one command with all language blocks:

```bash
python3 $CLAUDE_PLUGIN_ROOT/scripts/generate-release-notes.py \
  --platform <platform> \
  --lang <code1> --intro "<intro1>" [--items "<items1>"] [--outro "<outro1>"] \
  --lang <code2> --intro "<intro2>" [--items "<items2>"] [--outro "<outro2>"]
```

**`--intro`** — at least 100 characters, capped at 2 sentences, friendly non-technical language. Include the version number or release context. Translate faithfully per language.

**`--items`** (optional) — if omitted, the script auto-extracts from CHANGELOG.md in priority order (Breaking Changes → Added → Changed → Fixed → Reverted), capped at 6. When provided, convert CHANGELOG entries to user-friendly language as `"- First change\n- Second change"`. Max 6 items.

> **Non-English languages:** Always provide `--items` with translated content. Omitting `--items` for a non-English language causes the section to display raw English CHANGELOG text.

| Platform    | Recommended Items                                |
|-------------|--------------------------------------------------|
| `playstore` | 3–5 (max 6, must fit 500 chars including intro)  |
| `appstore`  | 5–6 (can expand on key features)                 |
| `web`       | Up to 6 significant changes, in full detail      |

For Play Store, prioritize: Breaking Changes > Added > Fixed > Changed > Reverted.

**`--outro`** (optional, strongly recommended) — 1-sentence closing appended after items with a blank line. Use for calls to action, thank-you notes, or support links. Translate per language. Omit for Play Store only if near 500 chars.

Example: `"Thank you for updating — we hope you enjoy the new features!"`

For tone guidelines, language examples, and localization tips, see **`references/platform-guide.md`**.

## Error Handling

**Character limit exceeded** (Play Store / App Store):
1. Remove the outro if present
2. Shorten intro to 1 sentence (~110–120 chars)
3. Remove lowest-priority items (Reverted → Changed → Fixed)
4. Shorten remaining item text
5. Re-run the script

**Intro too short** (under 100 chars) — expand to be more descriptive; add release context.

## Summary

After generating, display a summary block:

| Field             | Value                                               | Reason          |
|-------------------|-----------------------------------------------------|-----------------|
| **Version**       | `v1.2.0`                                            | N/A             |
| **Platform(s)**   | `appstore, playstore`                               | N/A             |
| **Languages**     | `en_US, id_ID`                                      | N/A             |
| **Files written** | `RELEASE_NOTES_APPSTORE`, `RELEASE_NOTES_PLAYSTORE` | N/A             |
| **Char count**    | `en_US: 1,234 / id_ID: 1,102`                       | N/A             |
| **Items omitted** | None / `Changed, Reverted` *(if truncated)*         | Character limit |

## Additional Resources

- **`references/platform-guide.md`** — Tone guidelines, writing examples per platform, and localization tips
- **`examples/playstore-bilingual.md`** — Complete worked example: Play Store with English + Indonesian output
