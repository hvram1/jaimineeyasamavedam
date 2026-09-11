# Vedic HTML Reader Generator from Baraha Sources

This guide documents the tools and workflow for converting Baraha ASCII `.docx` files into standalone, responsive, interactive Vedic HTML readers with authentic Devanagari typography and chant svara notation.

---

## 🏛️ System Architecture

The generator lives in the [`src/`](file:///c:/Users/sekha/OneDrive/Documents/GitHub/vedavms/src) package:

```
src/
├── __init__.py          # Package exports
├── transliterate.py     # Standalone Baraha -> Devanagari Unicode transliteration engine
├── build_reader.py      # DOCX OpenXML parser, section extractor & HTML generator
└── config.json          # Multi-book definitions, regex rules, and font options
```

### Key Modules:

1. **[`src/transliterate.py`](file:///c:/Users/sekha/OneDrive/Documents/GitHub/vedavms/src/transliterate.py)**:
   * Pure Python transliterator converting Baraha ASCII phonetic scheme to Devanagari Unicode.
   * Parses Vedic swaras, nasals, punctuation, and applies canonical Unicode normalizations.
   * Guarantees **zero dotted circles** by ordering combining accents after base consonants, Visarga, or Anusvara.

2. **[`src/build_reader.py`](file:///c:/Users/sekha/OneDrive/Documents/GitHub/vedavms/src/build_reader.py)**:
   * Extracts raw paragraphs from Word `.docx` documents using Python standard library (`zipfile` + `xml.etree.ElementTree`).
   * No third-party dependencies required (no `python-docx` needed).
   * Segments paragraphs into structured chapters, anuvakas, and verses.
   * Generates the standalone HTML reader page with responsive navigation and typography controls.

3. **[`src/config.json`](file:///c:/Users/sekha/OneDrive/Documents/GitHub/vedavms/src/config.json)**:
   * Declarative JSON configuration decoupling book metadata and chapter regexes from generator code.

---

## 🔡 Transliteration & Svara Encoding Reference

| Baraha Token | Unicode Character | Name / Function | Devanagari Example |
| :--- | :--- | :--- | :--- |
| `q` | `॒` (U+0952) | Anudatta (bottom horizontal line) | `miqtraH` $\rightarrow$ `मि॒त्रः` |
| `#` | `॑` (U+0951) | Svarita / Udatta (top vertical stroke) | `SannO#` $\rightarrow$ `शन्नो॑` |
| `$` | `᳚` (U+1CDA) | Deergha Svarita (double vertical stroke) | `vyA$KyA` $\rightarrow$ `व्या᳚ख्या` |
| `~M` | `\u00A0ँ` (U+0901) | Candrabindu (with non-breaking space) | `SaM ~Mvaru#NaH` $\rightarrow$ `शं ँवरु॑णः` |
| `(gm)`, `(gm~)` | `ꣳ` (U+A8F3) | Candrabindu Virama (Vedic Gum) | `(gm)` $\rightarrow$ `ꣳ` |
| `(gg)` | `ᳺ` (U+1CFA) | Double Anusvara Antargomukha | `pA~NktA(gg)#` $\rightarrow$ `पा~ण्क्ताᳺ॑` |
| `&` | `ऽ` (U+093D) | Avagraha | `tE &gnE` $\rightarrow$ `ते ऽग्ने` |
| `\|` / `\|\|` | `।` / `॥` | Danda / Double Danda | `\|` $\rightarrow$ `।`, `\|\|` $\rightarrow$ `॥` |
| `^` | `\u200C` | Zero-Width Non-Joiner (ZWNJ) | Prevents ligature forming |

### Canonical Normalization Rules:
* **Accent & Visarga Ordering**: In Baraha, `#H` or `qH` is reordered to `H#` / `Hq` (`ः॑` / `ः॒`) so the accent attaches properly to the Visarga without rendering a dotted circle.
* **Accent & Anusvara Ordering**: Accents immediately following `M` attach to the Anusvara (`ं॑` / `ं॒`).
* **Consecutive Virama Cleanup**: Duplicate viramas (`््`) are collapsed.
* **Whitespace & Accent Detachment**: Accents separated by whitespace or punctuation are stripped to prevent orphaned accent glyphs.

---

## 🚀 CLI Usage & Commands

All scripts run with pure Python 3 (standard library only):

### 1. Build Readers from Config
```bash
# Build the default configured book (Taittiriya Upanishad)
python src/build_reader.py

# Build all books configured in src/config.json
python src/build_reader.py --all

# Build a specific book by ID defined in src/config.json
python src/build_reader.py --book taittiriya_upanishad
```

### 2. Override Paths on the Fly
```bash
python src/build_reader.py --input tu_baraha.docx --output taittiriya_upanishad_sanskrit.html
```

### 3. Test Transliteration Standalone
```bash
python src/transliterate.py
```

---

## 📖 How to Add a New Vedic Book

To configure a new book (e.g., *Taittiriya Brahmana*):

1. Place your Baraha `.docx` source file in the repository (e.g. `tb_baraha.docx`).
2. Add a new book entry in [`src/config.json`](file:///c:/Users/sekha/OneDrive/Documents/GitHub/vedavms/src/config.json):

```json
{
  "books": {
    "taittiriya_brahmanam": {
      "title": "तैत्तिरीय ब्राह्मणम्",
      "subtitle": "कृष्ण यजुर्वेदीय तैत्तिरीय ब्राह्मणम् (सस्वरम्)",
      "input_docx": "tb_baraha.docx",
      "output_html": "taittiriya_brahmanam_sanskrit.html",
      "back_link": "documents.html",
      "back_label": "← Documents Index",
      "chapter_regex": "^([1-3])(?!\\.)\\s*(.*(?:kANDa|ashtaka).*)$"
    }
  }
}
```

3. Run the generator:
```bash
python src/build_reader.py --book taittiriya_brahmanam
```

---

## 🎨 Interactive Reader Features

The generated HTML reader provides:
* **Sticky Navigation Header**: Branding, back navigation to the main documents catalog, font switcher, font resizing controls (`A+` / `A-`), and 1-click print.
* **Sidebar Table of Contents (TOC)**: Hierarchical Chapter and Anuvaka navigation jumping directly to specific verses.
* **Dynamic Font Switcher**: Toggles between curated Vedic fonts loaded from Google Fonts:
  * *Noto Serif Devanagari* (Default)
  * *Tiro Devanagari Sanskrit*
  * *Noto Sans Devanagari*
* **Mobile-Responsive Grid**: Collapses sidebar into a streamlined single-column layout on smaller screens.
* **Print Stylesheet**: Hides navigation headers and controls when printing or saving as PDF (`Ctrl+P` / `Cmd+P`).
