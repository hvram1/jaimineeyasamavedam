---
name: sync_csv_metadata
description: Protocol for syncing Rik and Samam metadata between generated JSON and CSV correction tables.
---

# Sync CSV Metadata Skill

This skill documents the round-trip lifecycle of modifying Vedic metadata (Rishi, Devata, Chandas).

## The Round-Trip Architecture
1. **Extraction**: `generate_granular_table.py` / `generate_rik_table.py` flatten the deeply nested JSON into tabular CSV/Excel formats. 
2. **Key Concept**: The system uses `Global_Rik_Num` as the stable primary key to map metadata back to verses.
3. **Correction Workflow**: Scholars edit the CSV/Excel files (not the JSON or Python scripts!).
4. **Re-injection**: Scripts (e.g., `apply_excel_corrections.py` or `generate_json.py --metadata-file`) read the CSV, locate the `Global_Rik_Num`, and inject the updated `Rik_Rishi`, `Rik_Devata`, or `Rik_Chandas` into the JSON structure.

## Rules for Agents
*   **Do not hardcode metadata fixes in Python**. 
*   **Fallback Resolution**: If metadata parsing (e.g., splitting a raw string "Rishi: X, Devata: Y, Chandas: Z") fails during extraction, utilize the smart string parser (`parse_metadata_str`) and normalize keys `normalize_key()`.
