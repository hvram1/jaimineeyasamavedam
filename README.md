# Jaimineeya Samaveda Processing & Publishing Pipeline

A production-grade Vedic text processing, transliteration, and typesetting system for the **Jaimineeya Samaveda (JSV) Samhita** in both **Devanagari** and **Malayalam (with authentic Grantha swara notations & Vedic modifiers)**.

---

## 📖 Quick Start & CLI Workflows

### 1. Malayalam Pipeline (Full Samhita, Rik + Samam + RDC)

The Malayalam workflow supports interactive editing of Unicode text files, JSON AST conversion, and rendering to PDF, HTML, and Unicode TXT.

#### Step A: Generate JSON from Text / Corrections
Whenever you edit or correct [`data/input/Malayalam/Samhita_Malayalam_corrected.txt`](data/input/Malayalam/Samhita_Malayalam_corrected.txt), convert it into the AST JSON:
```powershell
python -X utf8 src/generate_json.py data/input/Malayalam/Samhita_Malayalam_corrected.txt --output data/output/malayalam/Samhita_Malayalam.json
```

#### Step B: Render PDF, HTML, and TXT
Run `src/render_pdf.py` with `--script malayalam` in one of the three output modes:

1. **Combined Mode (Default — Rik + Samam + Rishi/Devata/Chandas):**
   ```powershell
   $env:PYTHONPATH="src"; python -X utf8 src/render_pdf.py data/output/malayalam/Samhita_Malayalam.json --script malayalam
   ```
   *Generates:*
   - `data/output/pdf/Malayalam/Samhita_Malayalam.pdf`
   - `data/output/html/Malayalam/Samhita_Malayalam.html`
   - `data/output/txt/Malayalam/Samhita_Malayalam_Unicode.txt`

2. **Separate Mode (Separate Rik and Samam files with Metadata):**
   ```powershell
   $env:PYTHONPATH="src"; python -X utf8 src/render_pdf.py data/output/malayalam/Samhita_Malayalam.json --script malayalam --output-mode separate
   ```
   *Generates:*
   - `data/output/pdf/Malayalam/Rik_Malayalam.pdf` & `Samam_Malayalam.pdf`
   - `data/output/html/Malayalam/Rik_Malayalam.html` & `Samam_Malayalam.html`
   - `data/output/txt/Malayalam/Rik_Malayalam_Unicode.txt` & `Samam_Malayalam_Unicode.txt`

3. **No-Metadata Mode (Mantra Texts Only, no RDC headers):**
   ```powershell
   $env:PYTHONPATH="src"; python -X utf8 src/render_pdf.py data/output/malayalam/Samhita_Malayalam.json --script malayalam --output-mode nometa
   ```
   *Generates:*
   - `data/output/pdf/Malayalam/Rik_NoMeta_Malayalam.pdf` & `Samam_NoMeta_Malayalam.pdf`
   - `data/output/html/Malayalam/Rik_NoMeta_Malayalam.html` & `Samam_NoMeta_Malayalam.html`
   - `data/output/txt/Malayalam/Rik_NoMeta_Malayalam_Unicode.txt` & `Samam_NoMeta_Malayalam_Unicode.txt`

#### All-in-One Malayalam Generation Command
```powershell
python -X utf8 src/generate_json.py data/input/Malayalam/Samhita_Malayalam_corrected.txt --output data/output/malayalam/Samhita_Malayalam.json; $env:PYTHONPATH="src"; python -X utf8 src/render_pdf.py data/output/malayalam/Samhita_Malayalam.json --script malayalam; python -X utf8 src/render_pdf.py data/output/malayalam/Samhita_Malayalam.json --script malayalam --output-mode separate; python -X utf8 src/render_pdf.py data/output/malayalam/Samhita_Malayalam.json --script malayalam --output-mode nometa
```

---

### 2. Devanagari Pipeline (Standard Sanskrit)

#### Step A: Generate JSON from Devanagari Source
```powershell
python -X utf8 src/generate_json.py data/input/Samhita_corrected.txt --output data/output/Samhita_corrected_out.json
```

#### Step B: Render Devanagari Outputs
1. **Combined Mode:**
   ```powershell
   $env:PYTHONPATH="src"; python -X utf8 src/render_pdf.py data/output/Samhita_corrected_out.json
   ```
2. **Separate Mode:**
   ```powershell
   $env:PYTHONPATH="src"; python -X utf8 src/render_pdf.py data/output/Samhita_corrected_out.json --output-mode separate
   ```
3. **NoMeta Mode:**
   ```powershell
   $env:PYTHONPATH="src"; python -X utf8 src/render_pdf.py data/output/Samhita_corrected_out.json --output-mode nometa
   ```
4. **Kodunthirapully Variant (`-kpully`):**
   Render Devanagari Samam with red swara markings positioned **above** the mantra text (default without `-kpully` places swaras below the mantra syllables):
   ```powershell
   $env:PYTHONPATH="src"; python -X utf8 src/render_pdf.py data/output/Samhita_corrected_out.json -kpully --output-mode nometa
   ```

---

## 🔤 Malayalam Vedic Font & Swara Modifiers

The custom OpenType font [`fonts/JaimineeyaSwara.ttf`](fonts/JaimineeyaSwara.ttf) includes:
- **74 Precomposed Virama Glyphs (ക്, ച്, etc.)** featuring authentic Malayalam Chandrakala viramas.
- **Vedic Manuscript Ligatures & Bases:** Custom glyphs for `Pla` (`pla_jsv`), `Sha` (`sha_mal`), `Kra` (`k_ra_jsv`), and `Tra` (`t_ra_gran`).
- **All 11 Canonical Vedic Swara Modifiers:**

| # | Modifier | Typing Shortcut / Input | Stacking Position | Hex / PUA |
|---|---|:---:|:---:|:---:|
| 1 | **Syllable Arc (Tie / Breve)** | `(⁀)` or `(͡)` | Stacked Above | `E004 / 2040 / 0361` |
| 2 | **Caret (^ / ˄)** | `(^)` or `(˄)` | Stacked Above | `E005 / 005E / 02C4` |
| 3 | **Roof (/\\ / Ʌ)** | `(/\)` or `(Ʌ)` | Stacked Above | `E006 / 0245 / 2227` |
| 4 | **Combining Small Ring (˚ / ͦ)** | `(˚)` or `(ͦ)` | Stacked Above | `E009 / 0366 / 02DA` |
| 5 | **High/Mid-Dot (H / ॱ)** | `(ॱ)` or `(·)` | Stacked Above | `E001 / 0971 / 00B7` |
| 6 | **Underbar (_)** | `(_)` or `_` | Stacked Below | `E007 / 005F` |
| 7 | **Phrasing Danda (L / ╷)** | `(╷)` or `(L)` or `(⃓)` | Stacked Below | `E002 / 2577 / 20D3` |
| 8 | **Descending Tone (\\ / ╲)** | `(\)` or `(╲)` | Stacked Below | `E003 / 005C / 2572` |
| 9 | **Ascending Tone (/)** | `(/)` | Stacked Below | `E008 / 002F` |
| 10 | **Low Comma / Hook (,)** | `(,)` or `(ˏ)` | Stacked Below | `E00A / 002C / 0326` |
| 11 | **Phrasing Double Danda (\|\|)** | `(\|\|)` or `(॥)` | Inline | `E00B / 0965` |

### Visual Documentation & Tables
- **Interactive Glyph Inventory:** [`data/output/malayalam/glyph_table.html`](data/output/malayalam/glyph_table.html)
- **High-Res Font Chart:** [`data/output/malayalam/glyph_grid_JaimineeyaSwara.png`](data/output/malayalam/glyph_grid_JaimineeyaSwara.png)

---

## 🛠️ Font & Table Regeneration Scripts

To rebuild the font or regenerate the glyph table after editing mappings:
```powershell
python scripts/build_swara_font.py
python scripts/generate_glyph_grid.py
```
