# Vedic Devanagari to Malayalam PDF/HTML Conversion Pipeline

A high-fidelity Vedic text decoding, transliteration, and document generation pipeline for **Jaimineeya Samavedam & Mahanyasam** texts. 

The pipeline decodes legacy font-encoded PDF streams (e.g. `Sanskrit98`), produces clean Unicode Devanagari text, transliterates to Malayalam while preserving all authentic Vedic swaras/accents, and generates interactive HTML viewers and print-ready A4 PDFs.

---

## Table of Contents
- [Architecture & Components](#architecture--components)
- [Workflow & Pipeline](#workflow--pipeline)
- [CLI Usage & Command Examples](#cli-usage--command-examples)
- [Input / Output Specification](#input--output-specification)
- [Key Technical Features & Resolved Edge Cases](#key-technical-features--resolved-edge-cases)

---

## Architecture & Components

```
pdfconverter/
├── src/
│   ├── sanskrit98_decoder_v5.py         # Lossless Sanskrit98 font byte decoder & deduplicator
│   └── convert_devanagari_to_malayalam.py # End-to-end transliterator, HTML viewer & PDF engine
├── decode_full.py                        # Batch script to decode raw PDF byte streams to text
├── mahanyasam_devanagari.txt             # Primary edited Unicode Devanagari text file
├── mahanyasam_malayalam.txt              # Output Malayalam text
├── mahanyasam_malayalam.html             # Output interactive HTML viewer
└── mahanyasam_malayalam.pdf              # Output A4 print-ready PDF
```

### Component Breakdown

1. **`sanskrit98_decoder_v5.py` (Font Byte Decoder & Deduplicator)**
   - Maps raw single/multi-byte font stream codes from legacy `Sanskrit98` PDFs to standard Unicode Devanagari characters.
   - Implements Vedic accent assembly (Udātta `॑`, Anudātta `॒`, Dīrgha Svarita `᳚`, Gomukha/Anusvāra `ꣳ`).
   - Handles font conjunct ordering (deferred `i-matra` `0x1a`, Repha `0x15` `र्`, Subscript *ra-phala* `0x55` `्र`, Gomukha `0x38` `ꣳ`).
   - Includes `clean_repetitions()` to automatically strip font duplication artifacts (phrase duplicates, section label repetitions, trailing label tags after `॥`).

2. **`decode_full.py` (Devanagari Batch Generator)**
   - Reads extracted PDF byte lines (`_raw_lines.json`), decodes each line using `sanskrit98_decoder_v5`, and writes `mahanyasam_devanagari.txt`.

3. **`convert_devanagari_to_malayalam.py` (Transliteration & Document Engine)**
   - **Transliteration Module:** Uses `Aksharamukha` to convert Devanagari to Malayalam script while strictly preserving Vedic accent marks, avagraha (`ऽ`), and gomukha/anunasika (`ꣳ`, `ँ`).
   - **Accent Styling:** Wraps Malayalam Anudatta bars in `<span class="anudatta-bar">॒</span>` with CSS `vertical-align: -0.52em` to prevent clearance collisions under descenders.
   - **Smart Layout Engine:** Automatically detects document hierarchy:
     - Main Titles (`॥ महान्यासः॥`) $\rightarrow$ Large (24pt/1.5rem), Bold, Centered
     - Section Subtitles (`अथ पंचागं...`) $\rightarrow$ Subtitle size (19pt/1.2rem), Bold, Centered
     - Direction Markers (`(EAST)`, `(SOUTH)`) $\rightarrow$ Italic, Bold, Centered
     - Section Headers (`...पूर्वांग रुद्राय नमः॥`, `ध्यानम्।`) $\rightarrow$ Bold, Left-aligned
     - Mantras $\rightarrow$ Standard Body text (16pt/1.0rem)
   - **PDF Generator:** Invokes headless Microsoft Edge / Google Chrome to render the HTML layout cleanly into an A4 PDF document without browser margin artifacts.

---

## Workflow & Pipeline

```mermaid
flowchart TD
    subgraph Step 1: Font Stream Decoding
        A["maha_s.pdf / _raw_lines.json"] -->|PyPDF2 & sanskrit98_decoder_v5| B["mahanyasam_devanagari.txt"]
    end

    subgraph Step 2: Manual Edit / Review
        B -->|User Corrections / Line Formatting| C["mahanyasam_devanagari.txt (Updated)"]
    end

    subgraph Step 3: Malayalam Transliteration & Document Generation
        C -->|convert_devanagari_to_malayalam.py (Read-Only)| D["mahanyasam_malayalam.txt"]
        C -->|HTML Layout & Accent Lowering| E["mahanyasam_malayalam.html"]
        E -->|Headless Edge/Chrome Printing| F["mahanyasam_malayalam.pdf"]
    end
```

---

## CLI Usage & Command Examples

> [!IMPORTANT]
> Always execute python commands from the **`pdfconverter`** project directory (or adjust the path to `src/convert_devanagari_to_malayalam.py`).

### 1. Generate Malayalam Files from Updated Devanagari Text (`.txt`)
To generate `.txt`, `.html`, and `.pdf` outputs from your edited Devanagari text file without modifying the source `.txt` file:

```bash
python src/convert_devanagari_to_malayalam.py \
  --input mahanyasam_devanagari.txt \
  --output mahanyasam_malayalam.txt \
  --html mahanyasam_malayalam.html \
  --pdf mahanyasam_malayalam.pdf
```

### 2. Generate Directly from Raw PDF File (`.pdf`)
To extract lines directly from the PDF file while preserving exact PDF page numbers, font sizes, bold weights, and page margins:

```bash
python src/convert_devanagari_to_malayalam.py \
  --input maha_s.pdf \
  --output mahanyasam_malayalam_pdfin.txt \
  --html mahanyasam_malayalam_pdfin.html \
  --pdf mahanyasam_malayalam_pdfin.pdf
```

---

## Input / Output Specification

| Flag | Argument | Input / Output | Description |
| :--- | :--- | :--- | :--- |
| `--input`, `-i` | File Path | **Input (Read-Only)** | Path to source `.txt` or `.pdf` file. The script **never** overwrites this file. |
| `--output`, `-o` | File Path | **Output** | Destination path for plain text Malayalam transliteration (`.txt`). |
| `--html` | File Path | **Output** | Destination path for interactive HTML viewer (`.html`). |
| `--pdf`, `-p` | File Path | **Output** | Destination path for A4 PDF document (`.pdf`). |
| `--nasal` | Mode Name | Option | Vedic Anunasika/Gomukha mode: `symbol` (default, keeps `ꣳ`), `gg` (`ग्ग्`), `gm` (`ग्म्`), `latin_gm` (`gm`). |
| `--pages` | Page Filter | Option | Page range for PDFs (e.g. `1-5`, `10,12`, or `all`). |

---

## Key Technical Features & Resolved Edge Cases

### 1. Sanskrit98 Byte Mechanics
- **`0x15` (Repha `र्`):** Positioned AFTER consonant in Sanskrit98 font stream; prepended before syllable onset consonant in Devanagari Unicode.
- **`0x1A` (`ि` Short i-matra):** Typed BEFORE consonant in font stream; prevented from attaching to half-consonants (`Hc`) so it correctly completes conjuncts (e.g. `निध॑नपतान्तिकाय॒`, `ग्रन्थिरसि`).
- **`0x38` (Gomukha `ꣳ`):** Mapped to `U+A8F3` (DEVANAGARI SIGN CANDRABINDU VIRAMA).
- **`0x55` (Subscript *ra-phala* `्र`):** Mapped to `('्र', 'm')` (fixing `दंष्ट्रांकुरं`, `ताम्राधरं`, `कालाभ्र`, `वज्रहस्ताय`).
- **`0x37` (Long ee-matra `ी`):** Mapped to standard matra `'m'` (fixing `ओष॑धीषु॒`).
- **Independent Vowels:** Handled ASCII `अ` + matra combinations ($\text{अ} + \text{ा} \rightarrow \text{आ}$, $\text{आ} + \text{े} \rightarrow \text{ओ}$, $\text{आ} + \text{ै} \rightarrow \text{औ}$).

### 2. Anudatta Accent Clearance in Malayalam
Malayalam characters have deep bottom descenders (e.g. `കു`, `തു`, `്ര`). Standard combining Anudatta (`॒`) collides visually with these descenders. 
The HTML renderer wraps Anudatta marks in `<span class="anudatta-bar">॒</span>` with CSS:

```css
.anudatta-bar {
    display: inline-block;
    width: 0;
    overflow: visible;
    position: relative;
    left: -0.35em;
    vertical-align: -0.52em;
    font-weight: 700;
}
```
This lowers the Anudatta bar smoothly below all Malayalam glyph descenders without drifting across words.
