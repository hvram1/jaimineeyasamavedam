# Technical Specification (SPEC.md)
## Jaimineeya Samaveda (JSV) Devanagari-to-Malayalam Transliteration & Stacking Pipeline

---

## 1. Executive Summary & Objective

This project automates the conversion, transliteration, and typesetting of the **Jaimineeya Samaveda (JSV) Samhita** from digital Devanagari sources into publication-ready **Malayalam script with stacked Grantha swara notations**.

By parsing the existing digital Devanagari text directly from `C:\Users\sekha\OneDrive\Documents\GitHub\jaimineeyasamavedam`, this solution bypasses manual re-typing and error-prone manuscript OCR while preserving 100% base-text accuracy.

### Primary Goals:
1. **Automated Base Transliteration:** Convert Sanskrit Devanagari base text into standard Malayalam script with 100% phonetic accuracy.
2. **Swara Notation Mapping:** Map subscript Devanagari swara letters to authentic **Grantha Unicode glyphs** (`U+11300`–`U+1137F`). The relevant Grantha characters are available in the `https://docs.google.com/spreadsheets/d/1S0xu2DdhuhbZLVrSjJrKp-iH152Ys_QB0fWNLK6MSYI/edit?gid=0#gid=0` Google Sheet.  There has to be the logic to override Grantha rules for "Pla" and "Sha" and associated ligatures. Rest of the swaras are classical Grantha and so Grantha ligatures are applicable.  
3. **Layout Stack Inversion:** Invert vertical positioning—transforming Devanagari *subscript* swaras (below base text) into Malayalam *superscript* swaras (stacked directly above base text).
4. **Editable Intermediate Formats:** Export intermediate representations as structured JSON and lightweight plain-text compact markup for quick proofreading and git diffing. We have a Unicode export for Devanagari already. 
5. **Typesetting Output:** Compile publication-grade PDFs using XeLaTeX/LuaLaTeX and micro-positioning macros. An extensive JSON --> TEX mapper is already available and could possibly be extended (render_pdf.py) to handle the Malayalam text. 
6. **Modifier table:** This is a new artifact in Malayalam that is not present in Devangari. We need to define a scheme to introduce swara modifiers. The Unicode encoding for this could be derived from the "Modified Set" table in https://docs.google.com/spreadsheets/d/1S0xu2DdhuhbZLVrSjJrKp-iH152Ys_QB0fWNLK6MSYI/edit?gid=0#gid=0` Google Sheet. Suggestion is also given for the modifier encoding. 
7. **Correction workflow:** The correction workflow for Devanagari is already available and we should reuse that for Malayalam as well. Manual corrections done in Unicode text file and then converted to json file with generate_json.py and then subsequently converted to html, tex/pdf and Unicode text. 
7. **Reuse existing assets:** Use the assets available in the jaimineeyasamavedam project. The key .py files are generate_json.py, render_pdf.py, generate_website.py. Also, read the skills and documentation available in the project folder. 
8. Process till Page 307 (Malayalam_JSV\scans\page_0307.png). The rest are repeated from different sections. 
---

## 2. Technical Architecture & Data Flow

```
+---------------------------+
| Devanagari Source Text    |
| (Vedic JSV Samhita Markup)|
+-------------+-------------+
              |
              v
+-------------+-------------+
| 1. Vedic Parser           |
| (parse_vedic_markup)      |
+-------------+-------------+
              |
              v
+-------------+-------------+
| 2. Aksharamukha & Grantha |
| Transliteration Engine    |
+-------------+-------------+
              |
              v
+-------------+-------------+
| 3. Swara Inverter         |
| (Subscript -> Superscript)|
+-------------+-------------+
              |
              v
+-------------+-------------+
| 4. JSON / Compact Markup  |
| Intermediate Storage      |
+-------------+-------------+
              |
              +-----------------------+
              |                       |
              v                       v
+-------------+-------------+ +-------+-------------------+
| 5a. XeLaTeX PDF Renderer  | | 5b. HTML / Web Generator  |
| (render_vedic_latex)      | | (generate_vedic_website)|
+---------------------------+ +---------------------------+
```

---

## 3. Key Pipeline Modules

### 3.1 Parser & Structural Normalization
- Extracts structural elements: `Parva` (SuperSection), `Kandah` (Section), `Arsheyam` (SubSection), `Samam` (Mantra Sets), and `Rik` (Individual verse).
- Normalizes dandas (`॥`), Devanagari numerals (`०-९`), visargas, and footnoting hooks (`(s1)`).
- Preserves ZWJ/ZWNJ placement and strips extraneous invisible control codes.

### 3.2 Transliteration Engine
- Uses `aksharamukha` library for Sanskrit Devanagari to Malayalam transliteration.
- Maps custom Vedic swara markers to Grantha Unicode characters (`U+11300`–`U+1137F`).
- Implements Visarga-Accent Preprocessing (relocating accent positioning visually relative to preceding vowels and Visarga `ः`).

### 3.3 Swara Stacking & Layout Inversion
- Inverts vertical swara positioning: Devanagari subscript swara marks are mapped to Malayalam superscript swara stackings above base aksharas.
- Micro-positioning macros in TeX handle exact glyph heights and horizontal alignments.

### 3.4 Data Models & Intermediate Formats
- **JSON Format:** Hierarchical structure (`Parva` -> `Kandah` -> `Arsheyam` -> `Samam` -> `Rik`).
- **Compact Markup:** Text representation suitable for diffing and manuscript proofreading.

---

## 4. Verification & Validation Plan

1. **Automated Syntax Check:** Run script execution tests and syntax verification.
2. **Akshara Integrity Verification:** Round-trip and phonetic verification across transliterated strings.
3. **Typesetting & Visual QA:** XeLaTeX compilation testing and visual stack alignment inspection.

---


## 5. Roadmap & Implementation Status

1. **Rik-to-Samam Cross-Linking:** Add numbering scheme linking Rik number to the respective Samam numbers (valid for both Devanagari and Malayalam).
2. **Export to Unicode Numerals:** In the "Export to Unicode" option, convert Devanagari numerals to English numerals.
3. **[COMPLETED] Line Spacing & Clearance:** Line spacing increased to 2.15 (LaTeX XeLaTeX) and 2.2 with 18px row-gap (HTML) to provide generous clearance for descending tone markers (`\`) and top swara stacks.
4. **[COMPLETED] Sama Numeral Marker Formatting:** Isolated with `0.65em` horizontal spacing, enclosed in unbreakable containers (`\mbox` / `inline-flex`), with automatic line breaks initiating each new Sama on a fresh line.
5. **[COMPLETED] Unified Repha Standard:** Unified all pre-consonantal R occurrences (`ർ` / `ര്`) to traditional Repha **`൪`** (`U+0D6A`) across all rendering layers and source data.
6. **Space Modifier:** Introduce a fine-adjustment space modifier for advanced publisher typesetting.

---

## 6. Authoritative Ayugma Swara Concordance

The 19 Ayugma (odd/subscript) pitch bases follow the traditional Kerala Jaiminiya Lakshana order from the [Google Sheets Reference Concordance](https://docs.google.com/spreadsheets/d/1S0xu2DdhuhbZLVrSjJrKp-iH152Ys_QB0fWNLK6MSYI/edit?gid=0#gid=0):

| ID | Devanagari | Malayalam | Grantha Glyph | Grantha Hex | Traditional Technical Name | Classification |
| :--- | :---: | :---: | :---: | :---: | :--- | :--- |
| **A01** | क | **ക** | 𑌕 | `U+11315` | **Avaroham (അവരോഹം)** | Odd Swara Base |
| **A02** | ख | **ഖ** | 𑌖 | `U+11316` | **Anvangulyam (അന്വംഗുല്യം)** | Odd Swara Base |
| **A03** | च | **ച** | 𑌚 | `U+1131A` | **Udgamam (ഉദ്ഗമം)** | Odd Swara Base |
| **A04** | ट | **ട** | 𑌟 | `U+1131F` | **Yanam (യാനം)** | Odd Swara Base |
| **A05** | ण | **ണ** | 𑌣 | `U+11323` | **"Na" Swaram ("ണ" സ്വരം)** | Odd Swara Base |
| **A06** | त | **ത** | 𑌤 | `U+11324` | **Aavarttam (ആവർത്തം)** | Odd Swara Base |
| **A07** | थ | **ഥ** | 𑌥 | `U+11325` | **Utthanam (ഉത്ഥാനം)** | Odd Swara Base |
| **A08** | प | **പ** | 𑌪 | `U+1132A` | **Kshepanam (ക്ഷേപണം)** | Odd Swara Base |
| **A09** | फ | **ഫ** | 𑌫 | `U+1132B` | **"Pha" Swaram (ഫ-സ്വരം)** | Odd Swara Base |
| **A10** | भ | **ഭ** | 𑌭 | `U+1132D` | **Mardanam (മർദ്ദനം)** | Odd Swara Base |
| **A11** | य | **യ** | 𑌯 | `U+1132F` | **Marsanam (മർശനം)** | Odd Swara Base |
| **A12** | स | **സ** | 𑌸 | `U+11338` | **Anamika Marsanam (അനാമികാമർശനം)** | Odd Swara Base |
| **A13** | श | **ശ** | **ശ** | `U+0D36` | **Anuvarnna Swara Rahitya Suchakah** | Manuscript Malayalam Base |
| **A14** | ष | **ഷ** | 𑌷 | `U+11337` | **Aadyavarnna Swaraa Bhava Dyotakah** | Odd Swara Base |
| **A15** | प्ल | **പ്ല** | **\uE020** | `U+E020` | **"Pla" Swara Ityucyamanaha ("പ്ല" സ്വര ഇത്യുച്യമാനഃ)** | Authentic Vedic Pla Base |
| **A16** | ङ | **ങ** | 𑌙 | `U+11319` | **Ng-Swaram ("ങ" സ്വര ഇത്യുച്യമാനഃ)** | Odd Swara Base |
| **A17** | त्र | **ത്ര** | **\uE01D** | `U+E01D` | **Tra Swarakhyaha (ത്രസ്വരാഖ്യഃ)** | Conjunct Base |
| **A18** | र | **ര** | 𑌰 | `U+11330` | **Druta Swara Position Indicator** | Odd Swara Base |
| **A19** | क्र | **ക്ര / കൃ** | **\uE01E** | `U+E01E` | **Krishtakhya Swara Bhedah (കൃഷ്ടാഖ്യ സ്വര ഭേദഃ)** | Conjunct Base |

---

## 7. Canonical 8 Vedic Swara Modifiers & Inline Marks

| ID / Mark | Shortcut | Modifier Name | Glyph Codepoint | Visual Position | Lakshana Role |
| :--- | :---: | :--- | :---: | :---: | :--- |
| **MOD-A** | `(A)` / `(⁀)` | **Syllable Spanning Arc (Tie)** | `\uE004` / `U+2040` | Stacked Above (2 Syllables) | Overhead curved arch spanning across two words for connected tone transition. |
| **MOD-A1** | `(A1)` / `(A_1)` | **Bridging Arc over Danda** | `\uE00D` | Centered over Danda `।` | Syllable-spanning arch precisely centered over the bridging danda between phrases. |
| **MOD-B** | `(B)` / `(∧)` | **Peak Elevation Caret** | `\uE005` / `U+2227` | Stacked Above (2 Syllables) | Elevated melodic peak over syllable transition, with swara marker sitting above apex. |
| **MOD-C** | `(C)` / `(·)` | **Shoulder Pause Dot** | `\uE001` / `U+00B7` | Upper-Right Shoulder | High pause dot with natural advance width to prevent syllable collision. |
| **MOD-D** | `(D)` / `(Ʌ)` | **Chevron Roof** | `\uE006` / `U+0245` | Stacked Above (2 Syllables) | Roof-tone modulation spanning across words. |
| **MOD-E** | `(E)` / `(┃)` | **Phrasing Heavy Danda** | `\uE002` / `U+2503` | Inline | Structural major cadence division. |
| **MOD-F** | `(F)` / `(╷)` | **Light Vertical Line** | `\uE002` / `U+2577` | Inline | Minor phrasing tone separator. |
| **MOD-G** | `(G)` / `(\)` | **Descending Tone Slash** | `\uE003` / `U+005C` | Stacked Below | Downward falling pitch attached to the bottom-center of the preceding consonant. |
| **MOD-H** | `(H)` / `(|)` | **Overhead Swarita** | `\uE00C` / `U+007C` | Stacked Above | Vertical upper tone stroke situated directly on top of the base syllable. |
| **Dot (`.`)** | `.` / `(.)` | **Pause Dot** | `\uE001` / `.` | **Inline** | Stobha and breath pause indicator. |
| **Underbar (`_`)** | `_` / `(_)` | **Elongation / Low Line** | `\uE007` / `_` | **Inline** | Tone elongation or rhythmic phrasing gap. |
| **Comma (`,`)** | `,` / `(,)` | **Low Comma** | `\uE00A` / `,` | **Inline** | Minor cadence pause / breath comma. |

---

## 8. Project Links & Open Source Assets

- 🔤 **Custom Font:** [`fonts/JaimineeyaSwara.ttf`](file:///c:/Users/sekha/OneDrive/Documents/GitHub/jaimineeyasamavedam/fonts/JaimineeyaSwara.ttf) ([GitHub Link](https://github.com/sekharnarayanaswamy-del/jaimineeyasamavedam/blob/format-mantras/fonts/JaimineeyaSwara.ttf))
- 📖 **Specification & Developer Guide:** [`Malayalam_JSV/spec.md`](file:///c:/Users/sekha/OneDrive/Documents/GitHub/jaimineeyasamavedam/Malayalam_JSV/spec.md) ([GitHub Link](https://github.com/sekharnarayanaswamy-del/jaimineeyasamavedam/blob/format-mantras/Malayalam_JSV/spec.md))
- 🎨 **Interactive Glyph Table:** [`data/output/malayalam/glyph_table.html`](file:///c:/Users/sekha/OneDrive/Documents/GitHub/jaimineeyasamavedam/data/output/malayalam/glyph_table.html) ([GitHub Link](https://github.com/sekharnarayanaswamy-del/jaimineeyasamavedam/blob/format-mantras/data/output/malayalam/glyph_table.html))
- 🌐 **Interactive Publication Blog:** [`docs/blog/Malayalam_JSV_Publication_Blog.html`](file:///c:/Users/sekha/OneDrive/Documents/GitHub/jaimineeyasamavedam/docs/blog/Malayalam_JSV_Publication_Blog.html) ([GitHub Link](https://github.com/sekharnarayanaswamy-del/jaimineeyasamavedam/blob/format-mantras/docs/blog/Malayalam_JSV_Publication_Blog.html))
python Malayalam_JSV/generate_spec.py
```

---

## 6. Frozen Swara Lookup (reviewed 2026-08-14)

The 229 distinct swara markers (25,606 total occurrences) extracted from
`data/input/Samhita_corrected.txt` are resolved through the frozen table
`Malayalam_JSV/swara_lookup_frozen.json`, generated by
`Malayalam_JSV/generate_marker_review.py`. The pipeline reads the frozen
JSON; it never reads the live Google Sheet.

### 6.1 Approved decisions (revised 2026-08-14: Ayugma-only mapping)

- **Only the Ayugma table is used.** Yugma swaras (even swaras) are not used
  by the Samhita and are omitted from `swara_mapping.json`. The corpus
  markers use exactly the Ayugma letter set (क ख च ट ण त थ प फ भ य स श ष
  प्ल त्र र क्र ङ); letters outside it do not occur as markers.
- **The 'Grantha Glyph' column is authoritative.** `grantha_text` is taken
  verbatim from the glyph column and `grantha_codepoints` are derived from
  the actual glyph characters, so they cannot drift from the curated glyphs.
  The 'Grantha Hex' column is kept as `sheet_hex_reference` for audit only
  (it is stale in places: A04, A13, A17).
- **A13 (Saa) -> Malayalam ശ (U+0D36)** per the reference manuscript: the
  sheet's Grantha Glyph column holds the Malayalam character for this swara.
  All `श`-family markers (श, शा, शि, शु, शी, …) now stack ശ + MALAYALAM
  matras (U+0D3E…U+0D4D): Grantha matras cannot shape onto the Malayalam
  base and produced dotted circles; `generate_marker_review.py` rewrites the
  matra codepoints (093E→0D3E etc.) whenever the last emitted base letter is
  A13.
- **Sheet anomalies FIXED in the sheet (2026-08-14), no overrides needed:**
  A04 glyph is now canonical ट = U+1131F (hex column still says U+1133D
  UPADHMANIYA — stale); A15/A17/A19 now carry the virama
  (𑌪𑍍𑌲 / 𑌤𑍍𑌰 / 𑌕𑍍𑌰) and resolve as sheet entries. No marker is
  `source=decided` anymore.
- **Corrupted markers** (9 occurrences, `source=corrupt` in the frozen
  table) are resolved best-effort and flagged in QA; no source data edits:
  `चा। द्ध्रिषाऔ(टि`, `शि। उपई(कि`, `Sटा`, `टि `, `खि `, `टा `, `षै `
  plus two source-annotation errors (input file to be corrected; the
  overrides become inert once the markers are removed):
  - `मा` — `नार्क्ता(मा)`: the marker does not match its word (नार्क्ता ends
    in -क्ता); the same mantra later renders the word मा with marker (कि).
  - `वृ` — `वृ(वृ)`: flagged corrupt per review.
  (No markers remain `source=fallback`.)

### 6.2 Generated artifacts
- `Malayalam_JSV/swara_mapping.json` — Ayugma-only swara table (19 entries,
  glyph-derived text + codepoints, `sheet_hex_reference` audit column) +
  modifiers deferred + fixed matra table; regenerable from
  `Malayalam_JSV/generate_swara_mapping.py <sheet.csv>`.
- `Malayalam_JSV/samhita_marker_review.csv` — human review table (all 229
  markers with per-character resolution, sheet-entry matches, flags).
- `Malayalam_JSV/swara_lookup_frozen.json` — machine-readable frozen lookup
  consumed by `src/malayalam/`; each entry carries BOTH `grantha_text`
  (actual Unicode glyph characters) and `grantha_codepoints`.

### 6.3 Fonts
Bundled in `fonts/` (static hinted TTFs from notofonts.github.io):
`NotoSerifMalayalam-Regular.ttf`, `NotoSansMalayalam-Regular.ttf`,
`NotoSansGrantha-Regular.ttf`, `NotoSerifGrantha-Regular.ttf`. Validated
with fontTools: Grantha faces contain U+11317/U+1134D/U+1133E; Malayalam
faces contain U+0D15.

### 6.4 Pilot implementation (supersection_1 / section_1, Samam only)

**Transliteration module** (`src/malayalam/`):
- `ml_map.py` — loads `swara_lookup_frozen.json` (lru_cache); exposes
  `marker_to_grantha` (prefers the frozen `grantha_text` characters, so the
  manuscript-truth Malayalam ശ flows through), `marker_source`,
  `is_footnote_marker`, `coverage_report`.
- `ml_transliterate.py` — Aksharamukha wrapper (danda placeholders,
  `devanagari_to_malayalam`, `devanagari_to_grantha` fallback for unknown
  markers), combining-mark normalization (virama-before-matra removal,
  space-detach fix, ാ+െ/േ collapse), post-processing (word-final മ്→ം,
  ാ-collapse, ്ൃ→ൃ), and syllable/grapheme splitting. `split_malayalam_syllables`
  merges C+virama+C conjuncts and chillu+consonant into one syllable — this
  mirrors `utils.combine_halants` and is the unit a swara stacks above.
  `devanagari_syllable_count` does NOT count a trailing `म्` (anusvara, not
  a syllable: `ता(त) म्` → Malayalam `താം` = 1 syllable).
- `ml_text.py` — `tokenize_mantra_line` (Word(Swara) pairs, dandas,
  footnotes, Devanagari-numeral runs kept verbatim), `transform_subsection`
  adds `malayalam-mantra-sets` = [{malayalam-mantra, devanagari-mantra}],
  `transform_ast`, `render_intermediate_text`, and a CLI:
  `python -m malayalam.ml_text --input data/output/Vargeekaran.json --output <json> --text-out <txt> --qa-out <qa> --supersection supersection_1 --section section_1`
  (run from repo root with `$env:PYTHONPATH="src"`).
  `transform_line` merges a STANDALONE anusvara word (`म्`, `ं`, `म्ः`;
  609 occurrences corpus-wide) into the preceding word token: as a separate
  word it would render as a bare Malayalam combining mark U+0D02 with no
  base (visible dotted circle).
- Syllable-count QA: asserts Devanagari syllable count == Malayalam syllable
  count per marked word; any mismatch is a warning. Pilot: 317 marked words,
  0 warnings, 0 unknown markers (60 distinct markers; every marked word
  resolves from the sheet — sources: sheet 317 / decided 0 / fallback 0
  occurrences in the pilot).

**Rendering** (`src/render_pdf.py --script malayalam`, Samam-only & Combined modes):
- Transforms the AST in `main()` via `ml_text.transform_ast`, supports `output_mode='combined'`, `'separate'`, and `'nometa'`.
- **PDF Stacking (LaTeX):** `format_malayalam_samam` re-tokenizes each `malayalam-mantra` line and stacks the Grantha swara ABOVE the final syllable of the word with `\stackon` (via `\stackcenter` / `\stackleft`). Swara glyphs use `\swarafont` (`JaimineeyaSwara.ttf`) for Grantha bases, manuscript ligatures (Pla/Sha), and Vedic Modifiers (Mod-A..Mod-H in `ModifierDarkBlue`).
- **HTML Output:** Standalone, self-contained HTML generated via `templates/html/Malayalam_main_html.template` with embedded base64 `JaimineeyaSwara.ttf` for full offline & mobile rendering. Uses flexbox column layout with raised, compact swaras (`0.90rem`), dynamic right-edge anchoring for inter-syllable modifiers (Mod-A arc, Mod-B caret, Mod-D chevron), and bottom-right anchoring for Mod-G.
- **Unicode Plaintext Export:** Plaintext `.txt` files use standard Unicode Grantha characters (`𑌶𑌿`, `𑌪𑍍𑌲`, `𑌤𑍂`, `𑌟𑌾`, etc.) without Private Use Area (PUA) codepoints, non-combining standard Unicode symbols for swara modifiers (`(⁀)`, `(∧)`, `(·)`, `(Ʌ)`, `(\)`, `(|)`), and English ASCII digits for verse numbers (`॥ 1 ॥`).

**Font & Typography Setup**:
- `\setmainfont` & `\malayalamfont`: `NotoSerifMalayalam-Regular.ttf` for base Malayalam text.
- `\swarafont`: `JaimineeyaSwara.ttf` for superscript swaras, precomposed viramas, manuscript ligatures (Pla/Sha), and all 11 Vedic modifiers.
- `\devafont`: `NotoSerifDevanagari-Regular.ttf` for Vedic accents (Swarita, Anudatta, Kampa).
- `\latinfont`: `Nimbus Roman.ttf` for English numerals, page numbers, title metadata, and English text in footnotes.

---

## 5. Execution CLI Commands

### Step A: Generate AST JSON from Corrections
```powershell
python -X utf8 src/generate_json.py data/input/Malayalam/Agneyam_K1_extract.txt --output data/output/malayalam/Agneyam_K1_extract.json
```

### Step B: Compile PDF, HTML, and Unicode TXT
*   **Combined Mode (Full Samhita: Rik + Samam + RDC + Footnotes + Index):**
    ```powershell
    $env:PYTHONPATH="src"; python -X utf8 src/render_pdf.py data/output/malayalam/Agneyam_K1_extract.json --script malayalam
    ```
*   **Separate Mode (Rik & Samam with metadata):**
    ```powershell
    $env:PYTHONPATH="src"; python -X utf8 src/render_pdf.py data/output/malayalam/Agneyam_K1_extract.json --script malayalam --output-mode separate
    ```
*   **No-Metadata Mode (Mantra text only):**
    ```powershell
    $env:PYTHONPATH="src"; python -X utf8 src/render_pdf.py data/output/malayalam/Agneyam_K1_extract.json --script malayalam --output-mode nometa
    ```

---

## 6. Output Artifacts (`data/output/`)
- **PDFs:** `data/output/pdf/Malayalam/` (`Samhita_Malayalam.pdf`, `Rik_Malayalam.pdf`, `Samam_Malayalam.pdf`, `Rik_NoMeta_Malayalam.pdf`, `Samam_NoMeta_Malayalam.pdf`)
- **HTMLs:** `data/output/html/Malayalam/` (`Samhita_Malayalam.html`, `Rik_Malayalam.html`, `Samam_Malayalam.html`, `Rik_NoMeta_Malayalam.html`, `Samam_NoMeta_Malayalam.html`)
- **Unicode TXTs:** `data/output/txt/Malayalam/` (`Samhita_Malayalam_Unicode.txt`, `Rik_Malayalam_Unicode.txt`, `Samam_Malayalam_Unicode.txt`, `Rik_NoMeta_Malayalam_Unicode.txt`, `Samam_NoMeta_Malayalam_Unicode.txt`)
- **Glyph Inventory:** `data/output/malayalam/glyph_table.html` & `data/output/malayalam/glyph_grid_JaimineeyaSwara.png`

---

## 7. Malayalam Transliteration & Correction Workflow Recipe

The Malayalam edition involves a two-stage data lifecycle: **Automated Transliteration** from the digital Devanagari baseline, followed by **Manual Swara Modifier Enrichment** and **Multi-Format Export**.

```
+----------------------------------------------------------------------------------+
| Phase 1: Automated Devanagari-to-Malayalam Transliteration Pipeline              |
| 1. Base Text Transliteration (src/malayalam/ml_transliterate.py):                |
|    - Phonetically transliterates Sanskrit Devanagari -> Malayalam.              |
|    - Normalizes orthography: word-final മ് -> ം, ്ൃ -> ൃ, combines conjuncts.    |
| 2. Swara Mapping (src/malayalam/ml_map.py & swara_lookup_frozen.json):           |
|    - Inverts Devanagari subscript swaras to Grantha Unicode characters.         |
|    - Preserves authentic manuscript ligatures (Pla 𑌪𑍍𑌲, Sha 𑌶𑌿, Tra 𑌤𑍍𑌰, Kra 𑌕𑍍𑌰).|
| 3. Baseline Text Export (src/malayalam/ml_text.py):                              |
|    - Emits baseline editable Unicode text file: data/input/Malayalam/*.txt       |
+----------------------------------------+-----------------------------------------+
                                         |
                                         v
+----------------------------------------------------------------------------------+
| Phase 2: Manual Swara Modifier Enrichment                                        |
| - Vedic scholar opens data/input/Malayalam/*.txt in VS Code or any text editor.  |
| - Inserts Swara Modifiers by hand using keyboard shorthand tags:                 |
|   (e.g., (A) for Arc, (C) for Dot, (G) for Slash, (H) for Swarita, (D) for Roof) |
|   Example: ഹോ(𑌖)(A) ബാ(𑌪𑍍𑌲)(G)                                                      |
+----------------------------------------+-----------------------------------------+
                                         |
                                         v
+----------------------------------------------------------------------------------+
| Phase 3: Automated Multi-Format Typesetting & Export                             |
| 1. AST Parsing:                                                                  |
|    python -X utf8 src/generate_json.py data/input/Malayalam/<extract>.txt        |
|      --output data/output/malayalam/<extract>.json                               |
| 2. Multi-Format Rendering:                                                       |
|    python -X utf8 src/render_pdf.py data/output/malayalam/<extract>.json         |
|      --script malayalam                                                          |
|    -> Publication PDF: LaTeX XeLaTeX with JaimineeyaSwara.ttf micro-stacking.    |
|    -> Responsive HTML: Standalone HTML with base64 font & dynamic modifier arcs. |
|    -> Plaintext (.txt): Standard Unicode text with Grantha & English digits.    |
| 3. Static Website Generation:                                                    |
|    python src/generate_website.py --malayalam                                    |
|    -> Full interactive digital archive generated at docs/malayalam/              |
+----------------------------------------------------------------------------------+
```

---

## 8. Swara Modifier Notation & Input Reference Table

Below is the authoritative reference for entering Swara Modifiers by hand into the Malayalam Unicode text files:

| Modifier ID | Name | Keyboard / Text Input Tags | Plaintext Export Symbol | Visual Glyph | Visual Position | Chanting / Musical Function | Input Example |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- |
| **Mod-A** | Syllable Arc (Tie) | `(A)`, `(a)`, `(⁀)`, `(╭╮)` | `(⁀)` (`U+2040`) |  / ◠ | **Above** (Inter-syllable bridge) | Connects two syllables in a smooth continuous breath | `ഹോ(𑌖)(A) ബാ(𑌪𑍍𑌲)` |
| **Mod-B** | Peak Elevation Caret | `(B)`, `(b)`, `(∧)`, `(^)` | `(∧)` (`U+2227`) |  / ∧ | **Above** (Inter-syllable peak) | Upward pitch bend / peak emphasis between syllables | `ഹോ(B) ബാ` |
| **Mod-C** | Shoulder Pause Dot | `(C)`, `(c)`, `(·)`, `(ॱ)` | `(·)` (`U+00B7`) | ॱ / · | **Shoulder** (Upper right of syllable) | Stobha separator / rhythmic micro-pause | `ഓ(𑌤)(C) ഗ്നാ(𑌤)` |
| **Mod-D** | Chevron Roof | `(D)`, `(d)`, `(Ʌ)` | `(Ʌ)` (`U+0245`) |  / Ʌ | **Above** (Inter-syllable chevron) | Stepped descent inflection between syllables | `ഹോ(𑌪𑍍𑌲)(D) ഇഴാ` |
| **Mod-E** | Heavy Phrasing Danda | `(E)`, `(e)`, `(┃)` | `(┃)` (`U+2503`) | ┃ | **Inline** (Heavy vertical) | Major structural chanting division | `വാ(E)` |
| **Mod-F** | Light Vertical Mark | `(F)`, `(f)`, `(╷)` | `(╷)` (`U+2577`) | ╷ | **Inline** (Light vertical) | Minor breath pause / sub-cadence | `ഇ(F)` |
| **Mod-G** | Descending Tone Slash | `(G)`, `(g)`, `(\)`, `(╲)` | `(\)` (`U+005C`) | \ | **Below** (Bottom-right of syllable) | Falling pitch cadence drop | `ബാ(𑌪𑍍𑌲)(G)` |
| **Mod-H** | Overhead Swarita | `(H)`, `(h)`, `(|)`, `(॑)` | `(|)` (`U+007C`) | \| / ॑ | **Above** (Centered over syllable) | Classical Vedic Swarita accent | `ദാ(𑌚𑌿)(H)` |
| **Mod-L** | Lower Danda | `(L)`, `(l)`, `(|)` | `(|)` (`U+007C`) | \| | **Inline** (Downward stem) | Deep cadence marker | `താ(L)` |
| **Underbar** | Syllable Linker | `(_)`, `_` | `_` (`U+005F`) | _ | **Below** (Baseline connector) | Sustains multi-syllable phrase continuation | `താ_യാ_ഇ` |

