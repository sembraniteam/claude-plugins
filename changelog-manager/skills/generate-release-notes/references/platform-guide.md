# Release Notes Platform Guide

## Platform Rules Summary

| Platform   | File                      | Char Limit   | Items       | Tone              |
|------------|---------------------------|--------------|-------------|-------------------|
| Play Store | `RELEASE_NOTES_PLAYSTORE` | 500 / lang   | 3–5 (max 6) | Short, clear      |
| App Store  | `RELEASE_NOTES_APPSTORE`  | 4,000 / lang | 5–6 (max 6) | Warm, detailed    |
| Web        | `RELEASE_NOTES`           | None         | Up to 6     | Full, informative |

---

## Intro Rules (All Platforms)

The intro appears before bullet points and sets the tone for the entire release note.

**Requirements:**
- Minimum 100 characters (enforced by script)
- Maximum 2 sentences
- Friendly, conversational tone
- No technical terms (no: API, refactor, SDK, endpoint, middleware)
- Must be understandable by general users

**Structure pattern:**
> [What the team did / why this release matters] — [What's inside / what version]

---

## Play Store

**Char limit:** 500 characters per language (intro + all bullet items combined)

**Writing style:**
- Ultra-concise — every character counts
- Lead with the most exciting change
- One idea per bullet point
- Avoid filler words

**Budget breakdown (500 chars):**
- Intro: ~110–130 chars (just over minimum)
- Items: ~60–80 chars each → fits 3–5 items (script caps at 6)

**English example:**
```
We've made this update to bring you a smoother, faster, and more reliable experience across the app.

- Switch between light and dark mode from Settings
- Notifications now arrive instantly
- Fixed a crash when opening the app offline
```

**Indonesian example:**
```
Pembaruan ini hadir untuk memberikan pengalaman yang lebih lancar, cepat, dan andal di seluruh aplikasi.

- Ganti tampilan terang atau gelap dari Pengaturan
- Notifikasi kini langsung muncul
- Perbaikan crash saat membuka aplikasi tanpa internet
```

---

## App Store

**Char limit:** 4,000 characters per language (intro + all bullet items combined)

**Writing style:**
- Warm and encouraging
- Can include more context per feature
- Highlight benefits, not just the feature itself
- Use "you" language — write to the user

**English example:**
```
We've been listening to your feedback and this update brings some of the most-requested improvements yet — thank you for helping us make the app better with every version.

- Dark mode is here! Switch anytime from your profile settings for a more comfortable nighttime experience
- Push notifications have been completely rebuilt for instant, reliable delivery
- The home screen loads up to 40% faster on older devices
- Fixed a crash that some users experienced when opening the app without an internet connection
- Smoother animations throughout the app for a more polished feel
```

**Indonesian example:**
```
Kami telah mendengarkan masukan kalian dan pembaruan ini membawa peningkatan yang paling banyak diminta — terima kasih sudah membantu kami membuat aplikasi ini semakin baik di setiap versi.

- Mode gelap sudah hadir! Aktifkan kapan saja dari pengaturan profil untuk kenyamanan di malam hari
- Notifikasi push telah sepenuhnya diperbarui agar lebih cepat dan andal
- Layar beranda kini memuat hingga 40% lebih cepat di perangkat lama
- Perbaikan crash yang dialami beberapa pengguna saat membuka aplikasi tanpa koneksi internet
- Animasi lebih halus di seluruh aplikasi untuk tampilan yang lebih sempurna
```

---

## Web

**Char limit:** None

**Writing style:**
- Most detailed of all platforms
- Can include motivation behind changes
- Mention contributors or PR references if appropriate
- Use headings per category if many changes

**English example:**
```
We're excited to ship v1.2.0, a release focused on performance, accessibility, and the dark mode feature our community has been requesting for months.

**What's new:**
- Dark mode — toggle from your profile settings. Your preference is saved automatically
- Instant push notifications — rebuilt from scratch for reliable delivery even on poor connections
- 40% faster home screen load on devices older than 2019
- Fixed crash on app open when offline (reported by multiple users in #support)
- Smoother micro-animations for a more polished UI experience

Thank you to everyone who submitted feedback and bug reports. Keep them coming!
```

---

## Localization Tips

### General
- Translate meaning, not words — idioms rarely translate literally
- Match the warmth and energy of the source language
- Use the natural register of the target language (formal vs. informal varies by culture)

### Indonesian (id_ID)
- Use "Anda" for formal, "kamu" for casual — pick one and be consistent
- "Fitur baru" = new feature, "Perbaikan" = fix, "Peningkatan" = improvement
- Avoid direct translations of English tech terms — use the Indonesian equivalent where it exists

### Japanese (ja_JP)
- Use です/ます form for app store copy (polite but not overly formal)
- Keep bullet points short — Japanese characters are visually denser

### Korean (ko_KR)
- Use 합니다 form (formal polite) for store copy
- Korean store users expect clean, professional tone

### Arabic (ar_SA)
- Right-to-left — the script handles text only; ensure your publishing platform handles RTL display
- Use Modern Standard Arabic for store copy, not regional dialect

---

## Priority Order for Item Selection

When character limits require trimming, remove in this order (last removed = highest priority):

1. Reverted (remove first)
2. Changed
3. Fixed
4. Added
5. Breaking Changes (remove last — always include if present)
