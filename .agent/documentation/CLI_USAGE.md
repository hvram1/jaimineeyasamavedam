# CLI Usage Documentation

This document describes how to use the primary scripts `generate_json.py` and `render_pdf.py` for processing Jaimineeya Sama Veda text.

## 1. `generate_json.py`

This script converts raw text input into a structured JSON file used for rendering.

**Location:** `src/generate_json.py`

### Usage

```bash
python src/generate_json.py <input_file> [OPTIONS]
```

### Arguments

| Argument | Description | Default |
| :--- | :--- | :--- |
| `input_file` | Input text file to process (positional, required). | - |
| `--input-mode` | Processing mode: `initial` or `correction`. | `correction` |
| `--output` | Path for the generated JSON output file. | Auto-generated: `data/output/<input_basename>_out.json` |
| `--metadata-csv` | CSV file to enrich metadata (correction mode only). | None |
| `--initial-json` | Trusted Initial JSON output to map Rik IDs correctly (correction mode only). | None |
| `--procedures` | Path to procedure index YAML file (e.g., `data/input/prayoga/prayoga_index.yaml`). If omitted, no procedure links are added. | None |

### Modes

*   **Initial Mode (`--input-mode initial`)**:
    *   Reads from the input file (expects text with structural markers).
    *   Also reads auxiliary metadata files:
        *   `data/input/rishi_devata_chandas_for_rik.txt` - Rik metadata (Rishi, Devata, Chandas)
        *   `data/input/sama_rishi_chandas_out.txt` - Samam metadata
        *   `data/input/vedic_text.txt` - Rik text content
    *   Used for the first pass of processing from raw input.
    *   Input file must contain structural markers (SuperSection, Section, SubSection, Mantra Sets).

*   **Correction Mode (`--input-mode correction`)** *(default)*:
    *   Reads from the input file (expects processed Unicode text with embedded metadata).
    *   **Does NOT** read auxiliary files. It expects all metadata to be present in the input file itself.
    *   Used for subsequent passes after manual edits.
    *   Optionally enriches with metadata from CSV file using `--metadata-csv`.

### Examples

**Run in Correction Mode (default):**
```bash
python src/generate_json.py data\input\Samhita_with_Rishi_Devata_Chandas.txt
```

**Run in Initial Mode:**
```bash
python src/generate_json.py data/input/Agneyam-Pavamanam_corrected.txt --input-mode initial
```

**Run in Correction Mode with CSV Metadata Enrichment:**
```bash
python src/generate_json.py data/input/Agneyam-Pavamanam_corrected.txt --metadata-csv data/output/JSV_Samam_Granular_Table.csv
```

---

## 2. `render_pdf.py`

This script takes the JSON output from the previous step and generates PDF, HTML, and Text files.

**Location:** `src/render_pdf.py`

### Usage

```bash
python src/render_pdf.py [INPUT_FILE] [OPTIONS]
```

### Arguments

| Argument | Description | Default |
| :--- | :--- | :--- |
| `input_file` | The input JSON file path (Positional). | `data/output/Agneyam-Pavamanam_corrected_out.json` |
| `--output`, `-o` | Override the default output basename or specify a full output path. | Auto-generated based on input |
| `--output-mode` | Output style: `combined`, `separate`, or `nometa`. | `combined` |
| `--pdf-font` | Font name to use for PDF generation. | `AdiShila Vedic` |
| `--html-font` | Font family string for HTML output. | `'AdiShila Vedic', 'Adishila SanVedic'` |
| `--pdf-color-mode` | Color mode for PDF: `bw` or `color`. | `bw` |
| `--toc-level` | TOC headers: `section`, `subsection`, or `both`. | `section` |
| `--title` | Custom Sanskrit title for the document. | From `pipeline_config.yaml` or input JSON metadata. |

### Output Modes

| Mode | Description |
| :--- | :--- |
| `combined` | Single output with both Rik and Samam content, including all metadata. |
| `separate` | Two separate outputs: Rik-only and Samam-only, **with** metadata. |
| `nometa` | Two separate outputs: Rik-only and Samam-only, **without** metadata (plain text suitable for re-processing). |

### Examples

**Generate Combined Output (Standard):**
```bash
python src/render_pdf.py
```

**Custom Document Title:**
```bash
python src/render_pdf.py data/output/Prayogamala-pb.json --type collection --title "प्रयोगमाला पूर्वभागम्"
```

**Generate Separate Rik and Samam Files (with metadata):**
```bash
python src/render_pdf.py data/output/Agneyam-Pavamanam_corrected_out.json --output-mode separate
```

**Generate No-Metadata Output (for re-processing):**
```bash
python src/render_pdf.py data/output/Agneyam-Pavamanam_corrected_out.json --output-mode nometa
```

**Custom Output Path and Filename:**
```bash
python src/render_pdf.py data/output/Sooktamala.json -o data/exports/my_sooktam
```

### Notes and Best Practices
*   **Metadata Whitespace Preservation**: In HTML output, manual alignment of Rishi/Devata metadata is preserved. Ensure the source TXT file matches the desired visual layout.
*   **Aggregate Counting**: In `collection` mode, section headers automatically display aggregate counts. For mixed content, the format is **(ऋ-N, सा-M)**. If the section contains only one type, it shows only the numeral **(N)**.
*   **Navigation IDs**: Every section and subsection is assigned a unique ID (e.g., `#supersection_1-section_1-subsection_1`) for robust linking and table of contents navigation.

---

## 3. `generate_website.py`

This script generates the static HTML website from JSON data.

**Location:** `src/generate_website.py`

### Usage

```bash
python src/generate_website.py [OPTIONS]
```

### Arguments

| Argument | Description | Default |
| :--- | :--- | :--- |
| `--source-file`, `-s` | Path to the input JSON file. | Required |
| `--output-dir`, `-o` | Output directory (default: `docs`). | `docs` |
| `--audio-dir`, `-d` | Directory for audio placeholder folders. | `data/input/Audio_Placeholders` |
| `--samhita`, `-m` | Generate for Samhita mode. | Default |
| `--aranam`, `-a` | Generate for Aaranam mode. | - |
| `--collection`, `-c` | Generate for Collection mode. | - |
| `--title` | Custom title for the collection (used with `--collection`). | From JSON metadata |

### Examples

**Generate Samhita website:**
```bash
python src/generate_website.py -s data/output/Vargeekaran.json -o docs/samhita
```

**Generate Collection with custom title:**
```bash
python src/generate_website.py -s data/output/Sooktamala.json -o docs/collection/sooktamala -c --title "साम सूक्तमाला"
```

---

## 4. `generate_Rik_for_samhita.py`

This script generates a PDF containing primarily Rik text, intended for Samhita verification or specific output formats.

**Location:** `src/generate_Rik_for_samhita.py`

### Usage

```bash
python generate_Rik_for_samhita.py [OPTIONS]
```

### Arguments

| Argument | Description | Default |
| :--- | :--- | :--- |
| `-i`, `--input` | Path to input text file. | `data/input/vedic_text.txt` |
| `-o`, `--output` | Base name for output files (PDF/Tex/HTML). | `vedic_output` |
| `-f`, `--format` | Output format: `pdf`, `html`, or `all`. | `all` |

### Features

*   **PDF Generation**: Creates a high-quality PDF using LuaLaTeX.
*   **HTML Generation**: Creates an HTML file for quick verification and web display.

### Examples

**Default Usage:**
```bash
python src/generate_Rik_for_samhita.py
```

**Custom Input and Output:**
```bash
python src/generate_Rik_for_samhita.py -i data/input/Uttararchikam.txt -o uttararchikam_rik
```

**Generate HTML Only:**
```bash
python src/generate_Rik_for_samhita.py -f html
```

---

## 4. `generate_granular_table.py`

This script generates a detailed Excel/CSV table listing every individual Samam with its metadata.

**Location:** `src/generate_granular_table.py`

### Usage

```bash
python src/generate_granular_table.py
```

### Output Files

| File | Description |
| :--- | :--- |
| `data/output/JSV_Samam_Granular_Table.csv` | CSV file (UTF-8 with BOM for Excel) |
| `data/output/JSV_Samam_Granular_Table.xlsx` | Excel file (requires `openpyxl`) |

### Output Columns

| Column | Description |
| :--- | :--- |
| `Global_Samam_Num` | Sequential Samam number (1-1226) |
| `Global_Rik_Num` | Sequential unique Rik number (1-530) |
| `Patha_Name` | Name of the Patha (आग्नेयपाठः, etc.) |
| `Khanda` | Section/Khanda name |
| `Rik_ID` | Rik ID within the section |
| `Arsheyam_Name` | Name of the Arsheyam |
| `Rik_Rishi`, `Rik_Devata`, `Rik_Chandas` | Rik metadata (parsed) |
| `Samam_Rishi`, `Samam_Devata`, `Samam_Chandas` | Samam metadata (parsed) |

---

## 5. `apply_excel_corrections.py`

This script reads corrections from the Excel file and applies them back to the JSON data. This enables an **Excel-based metadata correction workflow**.

**Location:** `src/apply_excel_corrections.py`

### Usage

```bash
# Preview changes (dry run - no modifications)
python src/apply_excel_corrections.py --dry-run

# Apply corrections (creates backup first)
python src/apply_excel_corrections.py
```

### Arguments

| Argument | Description | Default |
| :--- | :--- | :--- |
| `--dry-run` | Preview changes without modifying JSON | False |
| `--excel` | Path to the Excel file | `data/output/JSV_Samam_Granular_Table.xlsx` |
| `--json` | Path to the JSON file to update | `data/output/Samhita_with_Rishi_Devata_Chandas_out.json` |

### Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│  1. Generate Excel from JSON                                    │
│     python src/generate_granular_table.py                       │
│     → Creates JSV_Samam_Granular_Table.xlsx                     │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  2. Edit Metadata in Excel                                      │
│     - Open data/output/JSV_Samam_Granular_Table.xlsx            │
│     - Edit individual fields: Rik_Rishi, Rik_Devata,            │
│       Rik_Chandas, Samam_Rishi, Samam_Devata, Samam_Chandas     │
│     - Edit full strings: Rik_Metadata, Saman_Metadata           │
│     - Save and close the file                                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  3. Apply Corrections to JSON                                   │
│     python src/apply_excel_corrections.py --dry-run  (preview)  │
│     python src/apply_excel_corrections.py            (apply)    │
│     → Updates JSON, creates backup automatically                │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  4. Regenerate Outputs                                          │
│     python src/render_pdf.py                                    │
│     python src/generate_website.py                              │
│     → Creates updated HTML, PDF, TXT, Website                   │
└─────────────────────────────────────────────────────────────────┘
```

### Features

- **Dry Run Mode**: Preview all changes before applying
- **Automatic Backup**: Creates timestamped backup before modifying JSON
- **Change Report**: Shows detailed list of what was modified
- **Error Handling**: Reports rows that couldn't be matched

---

## 6. `curate_jsv.py`

This script curates a subset of JSON files based on a list of P.K.S (Parva, Kandah, Samam) identifiers. It supports merging from multiple sources (Samhita, Aaranam, etc.) into a standalone curated JSON (Sooktamala).

**Location:** `src/curate_jsv.py`

### Usage

```bash
python src/curate_jsv.py --sources <src1> [src2...] --filter <filter_file> --output <output_file> [OPTIONS]
```

### Arguments

| Argument | Description | Default |
| :--- | :--- | :--- |
| `--sources` | List of source JSON files (Samhita, Aaranam, etc.). | From `pipeline_config.yaml` |
| `--filter` | Text file containing P.K.S identifiers (one per line, e.g., `1.1.1`). | From `pipeline_config.yaml` |
| `--output` | Path to the output curated JSON file. | From `pipeline_config.yaml` |
| `--title` | Custom title for the curated collection. | "जैमिनीय साम सूक्तमाला" |
| `--mode` | Selection mode: `samam` (default), `rik`, `both`, or `rik_nometa`. | `samam` |

### Features

*   **Merging**: Automatically merges supersections and closing mantras from multiple JSON sources.
*   **P.K.S Filtering**: Precisely extracts specific Samams based on the global section **ordinal** index. 
    *   **Note**: The tool sorts source section keys (Kandahs) and assigns them numbers 1, 2, 3... based on their position. This ensures robust mapping regardless of naming conventions in the source JSON.
*   **Text Modes**:
    *   `samam`: Only includes Samam music text (musical notations), drops Rik meta.
    *   `rik`: Only includes the original Rik verse text, includes all Rik metadata.
    *   `both`: Includes both Samam and Rik text for comparison.
    *   `rik_nometa`: Includes ONLY the original Rik verse text, stripping all metadata fields.

### Examples

**Standard Samam Curation:**
```bash
python src/curate_jsv.py --sources data/output/Vargeekaran.json --filter data/input/Nakshatra_sooktam.txt --output data/output/nakshatra_sooktam.json
```

**Curate Rik Text instead of Samam (with metadata):**
```bash
python src/curate_jsv.py --sources data/output/Vargeekaran.json --filter my_filter.txt --output my_rik_collection.json --mode rik
```

**Curate Rik Text ONLY (no metadata):**
```bash
python src/curate_jsv.py --sources data/output/Vargeekaran.json --filter my_filter.txt --output my_rik_only.json --mode rik_nometa
```

---

## 7. `renumber_sooktam.py`

This script renumbers IDs (`supersection_N`, `section_N`, `subsection_N`) and mantra markers (`॥ N ॥`) in both `.txt` and `.json` files.

**Location:** `src/tools/renumber_sooktam.py`

### Features

*   **Component Grouping**: The tool uses a set-based tracking logic. If a verse is composed of separate blocks (e.g., `# Start of Rik Metadata` followed by `# Start of Rik Text`), they are all grouped under the same `subsection_N` ID even if separated by blank lines. Only repeated components (e.g., a second Metadata block) trigger a counter increment.
*   **Sequential Sync**: Ensures perfectly sequential IDs across curated collections.

### Usage

```bash
python src/tools/renumber_sooktam.py <input_file> [OPTIONS]
```

### Arguments

| Argument | Description | Default |
| :--- | :--- | :--- |
| `input_file` | Path to the `.txt` or `.json` file to renumber. | - |
| `--jsv-version` | Manual version override (e.g. 5.0). Updates src/VERSION. | None |
| `--no-increment` | Use current version from src/VERSION without bumping. | False |
| `--no-renumber` | Inject-Only mode: update metadata header but skip renumbering content. | False |
| `--preserve-super` | Preserve existing SuperSection IDs (only renumbers sections/subsections). | False |
| `--preserve-all` | Preserve ALL structure IDs (only renumbers Samams). | False |
| `--start-super` | Starting number for SuperSections. | 1 |
| `--start-section` | Starting number for Sections. | 1 |
| `--start-subsection` | Starting number for SubSections. | 1 |
| `--reset-per-super` | Reset Section/SubSection counters at every SuperSection boundary. | False |
| `--contiguous-samams` | Do NOT reset Samam numbering at SuperSection boundaries (global contiguous). | False |

### Examples

**Renumber TXT file resetting Samams per SuperSection (Default):**
```bash
python src/tools/renumber_sooktam.py data/output/txt/Devanagari/Samhita_Unicode.txt
```

**Renumber while keeping existing structure IDs (Samam-only renumbering):**
```bash
python src/tools/renumber_sooktam.py data/input/Aaranam_latest.txt --preserve-all
```

**Custom starting offsets:**
```bash
python src/tools/renumber_sooktam.py MyText.txt --start-super 5 --start-section 10
```

---

## 7. Footnote Formatting Guide

This section describes how to correctly format footnotes in the source text file.

### Footnote Syntax

Footnotes use the format `(sN)` where N is a number (e.g., `(s1)`, `(s2)`, `(s3)`).

### Placement Rules

> [!IMPORTANT]
> **Footnote markers must be placed immediately after the swara** with NO space.

**Correct:**
```
इ(श)(s1)     ← footnote attaches to इ (correct)
वा(चा)(s2)   ← footnote attaches to वा (correct)
```

**Incorrect:**
```
इ(श) (s1)    ← space before footnote - may attach to wrong character
इ (s1)(श)    ← footnote before swara - incorrect placement
```

### Pattern

The general pattern for a mantra character with swara and footnote is:
```
Word(Swara)(sN)
```

Where:
- `Word` = The Devanagari character/syllable
- `(Swara)` = The swara marking in parentheses
- `(sN)` = The footnote marker (no space before it)

### Footnote Definitions

Footnotes are defined in a separate block in the source file:
```
# Start of Footnote -- subsection_1 ## DO NOT EDIT
s1: Kerala Padhati explanation here
s2: Thogur Padhati explanation here
# End of Footnote -- subsection_1 ## DO NOT EDIT
```

### Invisible Characters Warning

> [!CAUTION]
> Avoid copying text from PDFs or web pages directly, as invisible Unicode characters (zero-width joiners, etc.) may be introduced. These can break footnote detection. If footnotes aren't rendering correctly, try deleting and retyping the `(sN)` marker.

---

## 8. Malayalam Script Pipeline (CLI Guide)

The Malayalam workflow converts, transliterates, and renders the Jaimineeya Samaveda into Malayalam base text with Grantha superscript swara notations and Vedic modifiers.

### Step 1: Generate JSON AST from Malayalam Text
```powershell
python -X utf8 src/generate_json.py data/input/Malayalam/Samhita_Malayalam_corrected.txt --output data/output/malayalam/Samhita_Malayalam.json
```

### Step 2: Render PDF, HTML, and Unicode TXT
Run `src/render_pdf.py` with `--script malayalam` in one of the 3 available output modes:

1. **Combined Mode (Default — Rik + Samam + Rishi/Devata/Chandas):**
   ```powershell
   $env:PYTHONPATH="src"; python -X utf8 src/render_pdf.py data/output/malayalam/Samhita_Malayalam.json --script malayalam
   ```
   *Generated Outputs:*
   - `data/output/pdf/Malayalam/Samhita_Malayalam.pdf`
   - `data/output/html/Malayalam/Samhita_Malayalam.html`
   - `data/output/txt/Malayalam/Samhita_Malayalam_Unicode.txt`

2. **Separate Mode (Separate Rik and Samam files with Metadata):**
   ```powershell
   $env:PYTHONPATH="src"; python -X utf8 src/render_pdf.py data/output/malayalam/Samhita_Malayalam.json --script malayalam --output-mode separate
   ```
   *Generated Outputs:*
   - `data/output/pdf/Malayalam/Rik_Malayalam.pdf` & `Samam_Malayalam.pdf`
   - `data/output/html/Malayalam/Rik_Malayalam.html` & `Samam_Malayalam.html`
   - `data/output/txt/Malayalam/Rik_Malayalam_Unicode.txt` & `Samam_Malayalam_Unicode.txt`

3. **No-Metadata Mode (Mantra Texts Only, no RDC headers):**
   ```powershell
   $env:PYTHONPATH="src"; python -X utf8 src/render_pdf.py data/output/malayalam/Samhita_Malayalam.json --script malayalam --output-mode nometa
   ```
   *Generated Outputs:*
   - `data/output/pdf/Malayalam/Rik_NoMeta_Malayalam.pdf` & `Samam_NoMeta_Malayalam.pdf`
   - `data/output/html/Malayalam/Rik_NoMeta_Malayalam.html` & `Samam_NoMeta_Malayalam.html`
   - `data/output/txt/Malayalam/Rik_NoMeta_Malayalam_Unicode.txt` & `Samam_NoMeta_Malayalam_Unicode.txt`

### All-in-One Command
```powershell
python -X utf8 src/generate_json.py data/input/Malayalam/Samhita_Malayalam_corrected.txt --output data/output/malayalam/Samhita_Malayalam.json; $env:PYTHONPATH="src"; python -X utf8 src/render_pdf.py data/output/malayalam/Samhita_Malayalam.json --script malayalam; python -X utf8 src/render_pdf.py data/output/malayalam/Samhita_Malayalam.json --script malayalam --output-mode separate; python -X utf8 src/render_pdf.py data/output/malayalam/Samhita_Malayalam.json --script malayalam --output-mode nometa
```

### Font Building & Glyph Table Generation
To re-build the custom font or regenerate the interactive HTML glyph table:
```powershell
python scripts/build_swara_font.py
python scripts/generate_glyph_grid.py
```


