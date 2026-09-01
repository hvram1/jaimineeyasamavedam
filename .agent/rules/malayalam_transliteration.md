---
description: Malayalam Vedic transliteration and orthography rules for Jaimineeya Samavedam
always_apply: true
---

# Malayalam Vedic Transliteration & Orthography Rules

When transliterating or curating Jaimineeya Samavedam texts in Malayalam script:

## 1. Short (ह्रस्व) vs Long (दीर्घ) E & O Swaras
- In Devanagari Sanskrit, "ए" and "ओ" are inherently diphthongs/long.
- In Malayalam Vedic manuscripts (Namboothiri Grantha-Malayalam tradition), **short vowels (ह्रस्व)** are systematically used in place of long vowels in conjuncts, vocatives, stobha particles, and specific sandhi positions:
  - **E Swara**: Use short `െ` (`U+0D46`) / `എ` (`U+0D0E`) instead of long `േ` (`U+0D47`) / `ഏ` (`U+0D0F`) where appropriate:
    - Conjuncts & clusters: `അഗ്നേ` $\rightarrow$ `അഗ്നെ`, `ത്വമഗ്നേ` $\rightarrow$ `ത്വമഗ്നെ`, `വിശ്വേ` $\rightarrow$ `വിശ്വെ`, `ദ്വേ` $\rightarrow$ `ദ്വെ`, `ക്ഷേ` $\rightarrow$ `ക്ഷെ`.
    - Sibilants & verb endings: `ഷേ` $\rightarrow$ `ഷെ` (e.g., `നുഷേ` $\rightarrow$ `നുഷെ`, `സ്തുഷേ` $\rightarrow$ `സ്തുഷെ`, `ജനുഷേ` $\rightarrow$ `ജനുഷെ`, `ശൈരീഷേ` $\rightarrow$ `ശൈരീഷെ`).
    - Particles / Vocatives: `യേ` $\rightarrow$ `യെ`, `ദേ` $\rightarrow$ `ദെ`.
  - **O Swara**: Use short `ൊ` (`U+0D4A`) / `ഒ` (`U+0D12`) instead of long `ോ` (`U+0D4B`) / `ഓ` (`U+0D13`):
    - Sibilants & endings: `ഷോ` $\rightarrow$ `ഷൊ` (e.g., `ആഇഷോ` $\rightarrow$ `ആഇഷൊ`, `സാഇഷോ` $\rightarrow$ `സാഇഷൊ`, `ഹാഇഷോ` $\rightarrow$ `ഹാഇഷൊ`, `ഇഷോ` $\rightarrow$ `ഇഷൊ`, `ദക്ഷോ` $\rightarrow$ `ദക്ഷൊ`, `മാനുഷോ` $\rightarrow$ `മാനുഷൊ`).
    - Conjuncts: `രാക്ഷാണോ` $\rightarrow$ `രാക്ഷാണൊ`, `സ്തോ` $\rightarrow$ `സ്തൊ`, `ദ്രോ` $\rightarrow$ `ദ്രൊ`, `ക്ഷോ` $\rightarrow$ `ക്ഷൊ`.
    - Stobhas & vocatives: `ഹോ` $\rightarrow$ `ഹൊ` (e.g., `ഹോവാ` $\rightarrow$ `ഹൊവാ`, `ഹോഇ` $\rightarrow$ `ഹൊഇ`), `നോ` $\rightarrow$ `നൊ`, `ദോ` $\rightarrow$ `ദൊ`, `ഭോ` $\rightarrow$ `ഭൊ`.

## 2. Repha (Vocalic R)
- Consonant-preceding Repha (`ർ` / `ര\u0D4D`) is rendered with the traditional Vedic Repha symbol `൪` (e.g., `ർഹാ` $\rightarrow$ `൪ഹാ`, `ർവാ` $\rightarrow$ `൪വാ`).

## 3. Vedic LLA / ZHA
- Devanagari Vedic `ळ` (`U+0933`) and `ळ्ह` (`U+0934`) are rendered as Malayalam `ഴ` (`U+0D34`) / `ഴ്` (e.g., `ഇഴാ` for `इळा` / `ഇള`).

## 4. Word-Final Vowels & Anusvara
- Word-final long AA matra is shortened in titles (e.g., `സംഹിതാ` $\rightarrow$ `സംഹിത`, `മാലാ` $\rightarrow$ `മാല`).
- Word-final halant `മ്` is normalized to anusvara `ം` (e.g., `സൂക്തമ്` $\rightarrow$ `സൂക്തം`).
