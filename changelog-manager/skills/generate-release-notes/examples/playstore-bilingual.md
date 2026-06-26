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
  --lang en_US \
    --intro "We've packed this update with features you've been asking for, plus important fixes to make your experience smoother and more reliable every day." \
    --item "You can now switch to dark mode from Settings" \
    --item "Notifications arrive faster and more reliably" \
    --item "Fixed a crash when opening the app without internet" \
    --outro "Update now and let us know what you think!" \
  --lang id_ID \
    --intro "Pembaruan ini hadir dengan fitur-fitur yang kalian minta dan perbaikan penting untuk pengalaman yang lebih lancar setiap harinya." \
    --item "Kini bisa beralih ke mode gelap dari Pengaturan" \
    --item "Notifikasi datang lebih cepat dan andal" \
    --item "Perbaikan crash saat membuka aplikasi tanpa internet" \
    --outro "Perbarui sekarang dan beri tahu kami pendapat Anda!"
```

## Output: RELEASE_NOTES_PLAYSTORE

```
# Release Notes — Play Store

## EN_US
We've packed this update with features you've been asking for, plus important fixes to make your experience smoother and more reliable every day.

- You can now switch to dark mode from Settings
- Notifications arrive faster and more reliably
- Fixed a crash when opening the app without internet

Update now and let us know what you think!

## ID_ID
Pembaruan ini hadir dengan fitur-fitur yang kalian minta dan perbaikan penting untuk pengalaman yang lebih lancar setiap harinya.

- Kini bisa beralih ke mode gelap dari Pengaturan
- Notifikasi datang lebih cepat dan andal
- Perbaikan crash saat membuka aplikasi tanpa internet

Perbarui sekarang dan beri tahu kami pendapat Anda!
```

## Notes

- EN_US section: ~384 chars (well within 500 limit)
- ID_ID section: ~332 chars (well within 500 limit)
- Intro EN_US: 144 chars (above 100-char minimum)
- Intro ID_ID: 131 chars (above 100-char minimum)
- Outro is optional but strongly recommended — remove it first if the section approaches the 500-char limit
- Items prioritized: Added first, then Fixed (no Breaking Changes or Reverted in this release)
