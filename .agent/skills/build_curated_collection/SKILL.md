---
name: build_curated_collection
description: Guide on using the P.K.S (Parva.Kandah.Samam) identifiers to construct independent custom text collections (Sooktamala).
---

# Build Curated Collection Skill

This skill outlines how to build a new standalone text (Sooktamala/Ritu Shanti Japam, etc) using specific verses from the larger Samhita or Aaranam codebase.

## 1. P.K.S Identifiers
*   Every single Samam in the project is identified by a unique tuple: `P.K.S`
    *   **P** = Parva (SuperSection index, e.g., `1` for Agneyam)
    *   **K** = Kandah (**Ordinal index**). Sections are mapped by their position (1st, 2nd, etc.) within a Parva. Do NOT rely on JSON key names like `section_37`.
    *   **S** = Samam number (Numeric value extracted from Devanagari boundary `॥ N ॥`)

## 2. The Extraction Workflow
### Concept 
When tasked to create a custom selection (e.g., "Ritu Shanti Japam"):
1.  **Identify Verses**: Gather the `P.K.S` identifiers (e.g., `1.7.1`). The curation tool sorts source section keys alphabetically and assigns ordinal numbers starting at 1.
2.  **Use Tools**: Do NOT manually copy-paste JSON. Use:
    *   `src/curate_jsv.py`: High-level tool for merging multiple sources via filter files.
3.  **Command**: Provide a `--filter` text file. IDs can be simple `P.K.S` or enhanced `P.K.S(Metadata)(Title)`.
4.  **Modes**: 
    *   `rik_nometa`: Extracts Rik text only, helpful for generating cleaner 'Patha' views without Samam metadata.

## 3. Renumbering and Finalization
After curation or manual editing, use `src/tools/renumber_sooktam.py` to ensure sequential IDs and verse counts:
*   **Sequential Trackers**: The tool maintains independent counters for **Samams** (in `Mantra Sets`) and **Riks** (in `Rik Text`).
*   **Grouping Logic**: It groups `Metadata`, `Text`, and `Title` blocks for the same verse into a single `subsection_N` ID based on their proximity.
*   **Cross-File Sync**: Always run the renumbering tool on both `Sooktamala.txt` and `Collection_Devanagari_Unicode.txt` to keep them synchronized before generating the final JSON.
*   **SuperSection Preservation**: Use `--preserve-super` if the file belongs to a specific indexed collection (e.g., `supersection_20`).

### Pipeline for complex cases (Example): 
1. ``` python src\curate_jsv.py --sources data\output\Vargeekaran.json data\output\Aaranam_latest_out.json --filter data\input\Nakshatra_sooktam.txt --output data\output\Nakshatra_sooktam.json --mode rik_nometa --filter-type rik```
2. ``` python src\render_pdf.py data\output\Nakshatra_sooktam.json --type collection```
3. ``` python src\tools\renumber_sooktam.py data\output\txt\Devanagari\Collection_Devanagari_Unicode.txt```
4. ``` python src\generate_json.py data\output\txt\Devanagari\Collection_Devanagari_Unicode.txt --output data\output\Nakshatra_sooktam.json```
5. ``` python src\render_pdf.py data\output\Nakshatra_sooktam.json --type collection```