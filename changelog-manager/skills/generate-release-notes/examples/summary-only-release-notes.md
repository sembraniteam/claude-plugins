# Example: summary-only release notes (no `--item` flags) — Play Store

Two scenarios where a friendly sentence reads better than a bullet list: a single small fix, and a handful of closely related changes woven into one sentence. In both, `--item` is simply omitted — there's no separate flag for this.

## Scenario 1: a single small fix

### Input: CHANGELOG.md latest block

```markdown
## [v1.3.1] - 2026-07-15

### Fixed
- Typo in the account settings label (#51)
```

A single, minor fix like this reads better as one friendly sentence than as a summary followed by a list with just one dash in it — leave `--item` out entirely rather than passing a single one.

## Command

```bash
python3 $CLAUDE_PLUGIN_ROOT/scripts/generate-release-notes.py \
  --platform playstore \
  --lang en_US \
    --summary "This small update polishes up the account settings screen with a quick wording fix for a clearer experience." \
  --lang id_ID \
    --summary "Pembaruan kecil ini merapikan layar pengaturan akun dengan perbaikan teks agar lebih mudah dipahami."
```

## Output: RELEASE_NOTES_PLAYSTORE

```
# Release Notes — Play Store

## EN_US
This small update polishes up the account settings screen with a quick wording fix for a clearer experience.

## ID_ID
Pembaruan kecil ini merapikan layar pengaturan akun dengan perbaikan teks agar lebih mudah dipahami.
```

## Notes

- No bullet list, no blank-line-separated items block — just the summary (and an optional `--outro`, omitted here since the section is already tiny).
- The script never reads `CHANGELOG.md` itself — Claude read it in the skill's Context & Inputs step and decided here that "Typo in the account settings label" doesn't deserve its own bullet for a one-line fix, so no `--item` flag was passed at all.
- EN_US section: 108 chars; ID_ID section: 100 chars — both comfortably within the 500-char Play Store limit, so `release-notes-validator` never needs to trim them (there's nothing to trim — see its Step 3b).

## Scenario 2: several small related changes, folded into one sentence

Omitting `--item` isn't only for a single change — a set of small, closely-themed fixes can also read better as one sentence than as three near-identical bullets.

### Input: CHANGELOG.md latest block

```markdown
## [v1.4.0] - 2026-07-20

### Fixed
- Misaligned button on the settings screen (#60)
- Incorrect date format in the activity log (#61)
- Minor spacing issue on the profile card (#62)
```

### Command

```bash
python3 $CLAUDE_PLUGIN_ROOT/scripts/generate-release-notes.py \
  --platform playstore \
  --lang en_US \
    --summary "This release brings a handful of small polish fixes to the settings, activity log, and profile screens for a cleaner overall look."
```

### Output: RELEASE_NOTES_PLAYSTORE

```
# Release Notes — Play Store

## EN_US
This release brings a handful of small polish fixes to the settings, activity log, and profile screens for a cleaner overall look.
```

### Notes

- Three separate `Fixed` entries exist in CHANGELOG.md, but they're all minor polish on the UI, not distinct user-facing features — three bullets like "Fixed misaligned button", "Fixed date format", "Fixed spacing issue" would read as noise, not news. One sentence naming the affected areas communicates the same thing more cleanly.
- EN_US section: 130 chars — well within the 500-char Play Store limit.
- If the individual fixes were more distinct or higher-impact (e.g. a crash fix plus a new feature), passing them as `--item` bullets would be the better choice — summary-only fits a *tightly-themed* set of small changes, not any multi-item release.
