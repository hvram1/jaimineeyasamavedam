---
name: render_vedic_latex
description: Instructions for safely rendering complex Vedic accents and footnotes into LuaLaTeX.
---

# Render Vedic Text & PDF Skill

This skill dictates the logic for translating parsed JSON into production-ready LaTeX (for PDFs) and HTML via `src/render_pdf.py`.

## 1. Visarga-Accent Preprocessing (CRITICAL)
In Vedic Devanagari typesetting, when an accent (e.g., Anudatta, Swarita) follows a Visarga (`ः`), it must be visually shifted to sit atop/below the preceding vowel.
*   **Source Format**: `Wordः(1)` (Logical sequence)
*   **Rendering Need**: The script `src/utils.py` handles the `step_preprocess_visarga_accent` swap, transforming the string to `Word(1)ः` right before emitting LaTeX or HTML.
*   **Rule**: NEVER modify the logical format in the source JSON or Text file. This is purely a visual rendering transformation.

## 2. Metadata Whitespace Preservation (HTML)
Manual alignment in `rik_metadata` and `saman_metadata` must be preserved in HTML output.
*   **Logic**: Use the `preserve_spaces=True` flag in `format_dandas_html()`. This prevents the standard normalization (collapsing multi-spaces into one).
*   **CSS Requirements**: The `.rik-metadata` and `.header-meta` classes must use `white-space: pre-wrap;` to respect these preserved spaces in the browser.

## 3. Section-Level Aggregation (Counts)
In `collection` mode, section headers must display aggregate counts of all content types.
*   **Mixed Sections**: Display as `(ऋ-N, सा-M)` where N is Rik count and M is Samam count.
*   **Rik/Samam Only**: Display as regular numerals `(N)`.
*   **Implementation**: Aggregation is performed in `src/render_pdf.py` and passed to the template via `section.Count`.
*   **Styling**: Use the `.section-samam-count` class for these header numerals to ensure proper alignment and styling.

## 4. LaTeX Footnote Resolution
*   The raw text uses markers like `(s1)`.
*   These must be mapped against the `footnotes` dictionary within the JSON.
*   Convert to true LaTeX footnotes using `\footnote{...}`.
*   **Prayoga Procedures**: Dedicated procedural markdown files are supported which are dynamically built into the document structure as a compiled Appendix (`\chapter*{...}`) and footnote jumpers. Please refer to `.agent/skills/manage_prayoga_procedures/SKILL.md` for specifics on linking, parsing, and rendering.
*   **JSON Generation with Procedures**: To add procedure links:
    ```bash
    python src/generate_json.py <input.txt> --procedures data/input/prayoga/prayoga_index.yaml --output output.json
    ```

## 5. Scriptio Continua (Continuous Text)
When generating "Rik Samhita" (Continuous Text):
*   `remove_mantra_spaces()` must collapse word spaces while strictly preserving special markers such as line breaks (`\\`), structural lines (e.g., Colophons like `॥ इति ... ॥`), and footnote hooks.

## 6. Fonts & Rendering
*   **Devanagari PDF**: Uses XeLaTeX/LuaLaTeX with `fontspec` and `AdishilaVedic` font family.
*   **Malayalam PDF**: Uses XeLaTeX with `NotoSerifMalayalam-Regular.ttf` for base text, `JaimineeyaSwara.ttf` for superscript swaras and modifiers, `NotoSerifDevanagari-Regular.ttf` for Vedic accents, and `Nimbus Roman.ttf` for English numerals and footnotes.
*   **HTML**: CSS font-family stack utilizing `JaimineeyaSwara`, `Noto Serif Malayalam`, and `Adishila Vedic`.

## 7. Malayalam CLI Commands

### Step A: Generate JSON from Malayalam Text
```powershell
python -X utf8 src/generate_json.py data/input/Malayalam/Samhita_Malayalam_corrected.txt --output data/output/malayalam/Samhita_Malayalam.json
```

### Step B: Compile PDF / HTML / TXT Outputs
*   **Combined Mode (Default):**
    ```powershell
    $env:PYTHONPATH="src"; python -X utf8 src/render_pdf.py data/output/malayalam/Samhita_Malayalam.json --script malayalam
    ```
*   **Separate Mode (Rik & Samam with metadata):**
    ```powershell
    $env:PYTHONPATH="src"; python -X utf8 src/render_pdf.py data/output/malayalam/Samhita_Malayalam.json --script malayalam --output-mode separate
    ```
*   **NoMeta Mode (Mantra texts only):**
    ```powershell
    $env:PYTHONPATH="src"; python -X utf8 src/render_pdf.py data/output/malayalam/Samhita_Malayalam.json --script malayalam --output-mode nometa
    ```

