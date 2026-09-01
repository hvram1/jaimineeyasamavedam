import os

spec_content = """# Technical Specification (SPEC.md)
## Jaimineeya Samaveda (JSV) Devanagari-to-Malayalam Transliteration & Stacking Pipeline

---

## 1. Executive Summary & Objective

This project automates the conversion, transliteration, and typesetting of the **Jaimineeya Samaveda (JSV) Samhita** from digital Devanagari sources into publication-ready **Malayalam script with stacked Grantha swara notations**.

By parsing the existing digital Devanagari text directly from `C:\\Users\\sekha\\OneDrive\\Documents\\GitHub\\jaimineeyasamavedam`, this solution bypasses manual re-typing and error-prone manuscript OCR while preserving 100% base-text accuracy.

### Primary Goals:
1. **Automated Base Transliteration:** Convert Sanskrit Devanagari base text into standard Malayalam script with 100% phonetic accuracy.
2. **Swara Notation Mapping:** Map subscript red Devanagari swara letters to authentic **Grantha Unicode glyphs** (`U+11300`–`U+1137F`).
3. **Layout Stack Inversion:** Invert vertical positioning—transforming Devanagari *subscript* swaras (below base text) into Malayalam *superscript* swaras (stacked directly above base text).
4. **Editable Intermediate Formats:** Export intermediate representations as structured JSON and lightweight plain-text compact markup for quick proofreading and git diffing.
5. **Typesetting Output:** Compile publication-grade PDFs using XeLaTeX/LuaLaTeX and micro-positioning macros.

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

## 5. Execution Instructions

```bash
# Run spec generator
python Malayalam_JSV/generate_spec.py
```
"""

if __name__ == "__main__":
    output_dir = os.path.dirname(os.path.abspath(__file__))
    spec_path = os.path.join(output_dir, "spec.md")
    with open(spec_path, "w", encoding="utf-8") as f:
        f.write(spec_content)
    print(f"Successfully generated spec at {spec_path}")