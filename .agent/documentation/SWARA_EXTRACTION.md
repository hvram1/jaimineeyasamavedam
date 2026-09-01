# Jaimineeya Samavedam: Devanagari Samhita Swara Extraction & Analysis

## 1. Overview

The `scripts/extract_devanagari_samhita_swaras.py` tool extracts the full sequential succession of Devanagari swara symbols from the Jaimineeya Samavedam Samhita text, embedding explicit sentence/verse **danda separators (`|`)** and assigning sequential serial numbers (`Sl No`).

### Key Statistics
- **Parvas**: 6 Supersections
- **Kandahs**: 59 Sections (Khandas)
- **Samas**: 722
- **Total Swara Symbol Occurrences**: 25,606
- **Sentence Danda Separators (`|`)**: 6,950
- **Total Granular Succession Rows**: 32,556

---

## 2. Command Usage

To regenerate all CSV tables, Markdown docs, HTML viewer, and print PDF:
```bash
python scripts/extract_devanagari_samhita_swaras.py
```

---

## 3. Generated Files & Schemas

### 1. Per-Sama CSV (`data/output/Samhita_Devanagari_Swara_By_Sama.csv`)
722 rows covering each Sama with continuous sequential `Sl No` (1 to 722) and swaras grouped per sentence delimited by ` | `.
- **Schema**: `Sl No,Parva,Kandah <M>,Kandah Name,Sama Name,Swara Symbols`
- **Example**:
  ```csv
  1,आग्नेयपाठः,Kandah 1,प्रथम खण्डः,गौतमस्यपर्कः,त त श | थाच् चा श | टा श टि श | चा श चि | टा श टि श | कि च | ट ट खा शि | ख श |
  ```

### 2. Granular CSV (`data/output/Samhita_Devanagari_Swara_Table.csv`)
32,556 rows tracking exact token succession with `|` rows acting as sentence boundary indicators.
- **Schema**: `Sl No,Parva,Kandah <M>,Sama Name,Swara symbol`
- **Example**:
  ```csv
  1,आग्नेयपाठः,Kandah 1,गौतमस्यपर्कः,त
  2,आग्नेयपाठः,Kandah 1,गौतमस्यपर्कः,त
  3,आग्नेयपाठः,Kandah 1,गौतमस्यपर्कः,श
  4,आग्नेयपाठः,Kandah 1,गौतमस्यपर्कः,|
  5,आग्नेयपाठः,Kandah 1,गौतमस्यपर्कः,थाच्
  ```

### 3. Markdown Document (`data/output/swara_devanagari/samhita_devanagari_swara_table.md`)
Organized hierarchically into 59 smaller sub-tables (one per Kandah under each Parva) for clarity and readability.

### 4. Interactive HTML Viewer (`data/output/swara_devanagari/samhita_devanagari_swara_table.html`)
- **Search**: Live filtering by Sama Name, Sama Number, or swara characters.
- **Navigation**: Sticky top navigation bar and TOC chips to jump to any Parva or Kandah.
- **Print**: Embedded `🖨️ Print / Save PDF` button triggering print styles.

### 5. Print-Ready PDF (`data/output/swara_devanagari/samhita_devanagari_swara_table.pdf`)
Compiled automatically via headless Microsoft Edge/Chrome:
- Page margins: `14mm 10mm` (A4 Portrait)
- Parva header preserved together with its first subsequent Kandah on the same page.
- Subsequent Kandahs break onto new pages.
- Table headers (`<thead>`) repeat across page breaks.
- Full color preservation for swara tags and danda badges.
