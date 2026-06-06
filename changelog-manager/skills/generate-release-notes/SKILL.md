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

## Workflow

### Step 1: Read Settings

Read `.claude/changelog-manager.local.md`. If it does not exist, use defaults and notify the user:

```yaml
languages:
  - code: en_US
    name: English
platforms:
  - web
```

### Step 2: Read CHANGELOG.md

Read the latest version block (the first `## [vX.Y.Z]` section). Extract:
- Version number and release date
- All categorized entries by section (Breaking Changes, Added, Changed, Fixed, Reverted)

### Step 3: Generate Per-Platform Notes

For each platform in settings, build and run one command with all language blocks:

```bash
python3 $CLAUDE_PLUGIN_ROOT/scripts/generate-release-notes.py \
  --platform <platform> \
  --lang <code1> --intro "<intro1>" [--items "<items1>"] [--outro "<outro1>"] \
  --lang <code2> --intro "<intro2>" [--items "<items2>"] [--outro "<outro2>"]
```

#### Writing the `--intro`

Write the intro with **at least 100 characters** (enforced by the script), capped at 2 sentences, in friendly non-technical language. Include the version number or release context. Translate faithfully per language.

#### Writing the `--items`

Optional — if omitted, the script auto-extracts items from CHANGELOG.md in priority order (Breaking Changes → Added → Changed → Fixed → Reverted), capped at 6.

When provided, convert CHANGELOG entries to user-friendly, non-technical language. Format as `"- First change\n- Second change"`. Translate each item per language — non-English items are not validated against CHANGELOG.

For non-English languages, always provide `--items` with translated content — omitting it falls back to English CHANGELOG text.

**Maximum 6 items** — the script drops extras automatically.

**Platform-specific item count:**

| Platform    | Recommended Items                                |
|-------------|--------------------------------------------------|
| `playstore` | 3–5 (max 6, must fit 500 chars including intro)  |
| `appstore`  | 5–6 (max 6, can expand on key features)          |
| `web`       | Up to 6 significant changes, in full detail      |

For Play Store, prioritize: Breaking Changes > Added > Fixed > Changed > Reverted.

#### Writing the `--outro` (optional, strongly recommended)

A closing line appended after the items, separated by a blank line. Use it for calls to action, thank-you notes, or support links. Include it unless character limits force an omission.

- Keep it to 1 sentence
- Translate per language
- Counts toward the platform character limit — omit for Play Store only if the section is near 500 chars

Example: `"Thank you for updating — we hope you enjoy the new features!"`

For tone guidelines, language examples, and localization tips per language, see **`references/platform-guide.md`**.

### Step 4: Handle Errors

**Character limit exceeded** (Play Store / App Store):
1. Remove the outro if present
2. Shorten the intro (reduce to 1 sentence, aim for ~110–120 chars)
3. Remove lowest-priority items (Reverted → Changed → Fixed)
4. Shorten remaining item text
5. Re-run the script

**Intro too short** (under 100 chars):
- Expand the intro to be more descriptive and welcoming
- Add context about what the release focuses on

### Step 5: Report to User

Summarize:
- Platform(s) and output file(s) written
- Languages generated
- Character count per language (critical for Play Store)
- Any items omitted due to character limits

## Additional Resources

- **`references/platform-guide.md`** — Tone guidelines, writing examples per platform, and localization tips
- **`examples/playstore-bilingual.md`** — Complete worked example: Play Store with English + Indonesian output
