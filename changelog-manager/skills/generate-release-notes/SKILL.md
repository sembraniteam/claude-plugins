---
name: generate-release-notes
description: This skill should be used when the user asks to "generate release notes", "create release notes", "prepare App Store release", "prepare Play Store release", "bilingual release notes", "translate release notes", "write what's new section", "update store listing", "draft app update description", or references RELEASE_NOTES, RELEASE_NOTES_APPSTORE, or RELEASE_NOTES_PLAYSTORE files.
argument-hint: "[platform]  e.g. playstore | appstore | web"
allowed-tools: ["Read", "Bash", "Agent"]
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

This is the only place items come from — the script itself does not read `CHANGELOG.md` or extract anything from it. Deciding which entries become `--item` flags (if any) is entirely up to Claude, done here.

## Generate Notes

For each platform, build and run one command with all language blocks:

```bash
python3 $CLAUDE_PLUGIN_ROOT/scripts/generate-release-notes.py \
  --platform <platform> \
  --lang <code1> --summary "<summary1>" [--item "<item1>" --item "<item2>"] [--outro "<outro1>"] \
  --lang <code2> --summary "<summary2>" [--item "<item1>" --item "<item2>"] [--outro "<outro2>"]
```

**`--summary`** — at least 100 characters, capped at 2 sentences, friendly non-technical language. Include the version number or release context. Translate faithfully per language. Stands alone as the entire note when no `--item` flags are passed.

**`--item`** (optional, repeatable) — pass one `--item` flag per entry, in user-friendly language, ordered by priority (Breaking Changes → Added → Changed → Fixed → Reverted — this ordering matters: `release-notes-validator` trims from the end of the list first, so put the lowest-priority entries last). Max 6 items; omitting `--item` entirely produces a summary-only section with no bullet list — no separate flag is needed for that.

> **Non-English languages:** Always translate `--item` values (or the `--summary` text, if going summary-only) — never pass the English CHANGELOG.md wording directly.

Not every release reads well as a bullet list. A single small fix is the obvious case, but a handful of closely related changes can also read better woven into one or two friendly sentences than forced into separate bullets — bullets suit distinct, independent changes; prose suits a tightly-themed set of tweaks (e.g. "several small polish fixes to the settings screen"). In either case, just omit `--item` — the section is built from `--summary` (and optional `--outro`) alone.

| Platform    | Recommended Items                                |
|-------------|--------------------------------------------------|
| `playstore` | 3–5 (max 6, must fit 500 chars including summary) |
| `appstore`  | 5–6 (can expand on key features)                 |
| `web`       | Up to 6 significant changes, in full detail      |

**`--outro`** (optional, strongly recommended) — 1-sentence closing appended after items with a blank line. Use for calls to action, thank-you notes, or support links. Translate per language. Omit for Play Store only if near 500 chars.

For tone guidelines, language examples, localization tips, and a worked outro example, see **`references/platform-guide.md`** and **`examples/playstore-bilingual.md`**. For worked summary-only examples (a single small change, and a set of closely-themed changes folded into one sentence), see **`examples/summary-only-release-notes.md`**.

## Error Handling

**Character limit exceeded** (Play Store / App Store):

Delegate to the **`release-notes-validator`** agent via the Agent tool (`subagent_type: "changelog-manager:release-notes-validator"`) — pass it the full command you attempted. It will:
1. Calculate per-language character counts
2. Remove lowest-priority items from the end (items are ordered by priority, so the last ones are lowest)
3. Append a closing phrase ("and many more improvements") if items were removed
4. Re-run the adjusted command and report what changed

Only handle manually if the agent is unavailable, mirroring the agent's own order:
1. Remove the outro if present
2. Remove lowest-priority items (Reverted → Fixed → Changed) — no-op if no `--item` flags were passed (summary-only section), skip straight to step 3
3. Shorten the summary to 1 sentence (~110–120 chars) — last resort
4. Shorten remaining item text
5. Re-run the script

**Summary too short** (under 100 chars) — expand to be more descriptive; add release context.

After generating, report the version, platforms, languages, files written, and any items omitted due to character limits.

## Additional Resources

- **`references/platform-guide.md`** — Tone guidelines, writing examples per platform, and localization tips
- **`examples/playstore-bilingual.md`** — Complete worked example: Play Store with English + Indonesian output
- **`examples/summary-only-release-notes.md`** — Worked summary-only examples (no `--item` flags): a single small fix, and a set of closely-themed fixes, each rendered as a friendly sentence instead of bullets

The **`release-notes-validator`** agent (invoked automatically — see Error Handling) auto-trims items and appends closing phrases when char limits are exceeded.
