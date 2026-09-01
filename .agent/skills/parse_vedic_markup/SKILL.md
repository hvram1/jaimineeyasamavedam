---
name: parse_vedic_markup
description: Guidelines for converting Jaimineeya Samavedam structured text into hierarchical JSON.
---

# Parse Vedic Markup Skill

This skill provides the standard rules for taking raw Vedic text markup and properly parsing/modifying the Python parsing scripts (e.g., `src/generate_json.py`).

## 1. Hierarchy Rules
The JSON structure must rigidly follow this path:
`Parva (SuperSection) -> Kandah (Section) -> Arsheyam (Subsection/Header) -> Samam (Mantra Sets) -> Rik (Individual verse)`

## 2. Text Markup Conventions
*   **SuperSection**: Starts with `# Start of SuperSection Title -- ID ## DO NOT EDIT` and ends with `# End of SuperSection Title -- ID`
*   **Section**: Starts with `# Start of Section Title -- ID ## DO NOT EDIT` and ends with `# End of Section Title -- ID`
*   **Subsection**: Starts with `# Start of SubSection Title -- ID ## DO NOT EDIT` and ends with `# End of SubSection Title -- ID`
*   **Mantras**: Block starts with `# Start of Mantra Sets -- ID ## DO NOT EDIT` and ends with `# End of Mantra Sets -- ID`.
*   **Marker Stability**: The parser is robust to whitespace before `##`. For example, both `subsection_22##` and `subsection_22  ##` are valid.
*   **Samam boundaries**: Marked by double dandas with Devanagari numerals, e.g., `॥ २ ॥`. All pipeline components must convert Arabic numerals to Devanagari numerals when modifying text files.
*   **Dandas**: Always output `॥` instead of `||` or `| |`.

## 3. Safe Parsing Rules
*   **Invisible Characters**: Always use UTF-8 stripping for invisible Unicode characters like Zero-Width Joiners (ZWJ) that may break regex matching.
*   **Metadata Embedding**: Footnotes must appear immediately after the swara (no space). Format: `Word(Swara)(sN)`.

## 4. Vedic Transliteration Rules (Devanagari $\rightarrow$ Malayalam)
*   **Vocalic $r$ / Pre-consonantal Repha**: Transliterate `र्` before consonants (e.g. `र्हा`, `र्त्य`, `र्द्ध`, `र्ध्न`) as `൪` (`U+0D6A`, circular repha), e.g. `बर्हा` $\rightarrow$ `ബ൪ഹാ`, `बर्ही` $\rightarrow$ `ബ൪ഹീ`, `मर्त्या` $\rightarrow$ `മ൪ത്യാ`, `मूर्ध्नो` $\rightarrow$ `മൂ൪ധ്നോ`. Note: `൪` is excluded from ASCII digit normalization so it is preserved as an authentic Vedic repha.
*   **Intervocalic ळ (LLDA)**: Transliterate Devanagari `ळ` (`U+0933`) to Malayalam `ഴ` (`U+0D34`), e.g. `अग्निमीळे` $\rightarrow$ `അഗ്നിമീഴേ`.
*   **Word-Final "आ" Shortening**: Transliterate word-final "आ" / "ा" in titles and nouns as short "അ" (removing terminal `ാ` matra), e.g. `जैमिनीय साम संहिता` $\rightarrow$ `ജൈമിനീയ സാമ സംഹിത`, `जैमिनीय साम सूक्त माला` $\rightarrow$ `ജൈമിനീയ സാമ സൂക്തമാല`.
*   **Word-Final Halant Ma**: Transliterate word-final `മ്` to Malayalam Anusvara `ം` (e.g. `सूक्तम्` $\rightarrow$ `സൂക്തം`).
*   **Vocalic R Repair**: `്ൃ` $\rightarrow$ `ൃ`, `്ൄ` $\rightarrow$ `ൄ` (prevents double virama).
*   **End-of-Samam Line Breaking**: Line/paragraph breaks after each Samam verse marker `॥N॥` / `||N||`.

