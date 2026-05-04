# Example: Play Store — English + Indonesian

## Input: CHANGELOG.md latest block

```markdown
## [v1.3.0] - 2026-05-04

### Added
- Dark mode support (#42)
- Push notification improvements (#45)

### Fixed
- Crash when opening app offline (#38)
```

## Command

```bash
python3 $CLAUDE_PLUGIN_ROOT/scripts/generate-release-notes.py \
  --platform playstore \
  --lang en \
    --intro "We've packed this update with features you've been asking for, plus important fixes to make your experience smoother and more reliable every day." \
    --items "- You can now switch to dark mode from Settings
- Notifications arrive faster and more reliably
- Fixed a crash when opening the app without internet" \
  --lang id \
    --intro "Pembaruan ini hadir dengan fitur-fitur yang kalian minta dan perbaikan penting untuk pengalaman yang lebih lancar setiap harinya." \
    --items "- Kini bisa beralih ke mode gelap dari Pengaturan
- Notifikasi datang lebih cepat dan andal
- Perbaikan crash saat membuka aplikasi tanpa internet"
```

## Output: RELEASE_NOTES_PLAYSTORE

```
# Release Notes — Play Store

## EN
We've packed this update with features you've been asking for, plus important fixes to make your experience smoother and more reliable every day.

- You can now switch to dark mode from Settings
- Notifications arrive faster and more reliably
- Fixed a crash when opening the app without internet

## ID
Pembaruan ini hadir dengan fitur-fitur yang kalian minta dan perbaikan penting untuk pengalaman yang lebih lancar setiap harinya.

- Kini bisa beralih ke mode gelap dari Pengaturan
- Notifikasi datang lebih cepat dan andal
- Perbaikan crash saat membuka aplikasi tanpa internet
```

## Notes

- EN section: ~340 chars (well within 500 limit)
- ID section: ~298 chars (well within 500 limit)
- Intro EN: 163 chars (above 100-char minimum)
- Intro ID: 131 chars (above 100-char minimum)
- Items prioritized: Added first, then Fixed (no Breaking Changes or Reverted in this release)
