"""Generate Malayalam_JSV/swara_mapping.json from the Google Sheet CSV export.

Source sheet: https://docs.google.com/spreadsheets/d/1S0xu2DdhuhbZLVrSjJrKp-iH152Ys_QB0fWNLK6MSYI/
This is a frozen-data generator: run once per sheet revision, review the diff,
commit the JSON. The CSV is read from a local export path (not fetched live).

Simplified mapping (2026-08-14 revision): ONLY the Ayugma table is used
(Yugma swaras are not used by the Samhita). The "Grantha Glyph" column is
authoritative: grantha_text is taken verbatim from it and grantha_codepoints
are derived from the actual glyph characters, so they can never drift from
the curated glyphs. The "Grantha Hex" column is kept as sheet_hex_reference
for audit only (it is stale in places, e.g. A04/A13/A17).

Manuscript truth: A13 (Saa) has the MALAYALAM character (ശ, U+0D36) in the
Grantha Glyph column, matching the reference manuscript; the hex column
still shows the Grantha U+11336 for reference.

Usage:
    .venv\\Scripts\\python.exe -X utf8 Malayalam_JSV\\generate_swara_mapping.py <sheet.csv> [--out swara_mapping.json]
"""

import argparse
import csv
import json
from datetime import date
from pathlib import Path

SHEET_URL = (
    "https://docs.google.com/spreadsheets/d/"
    "1S0xu2DdhuhbZLVrSjJrKp-iH152Ys_QB0fWNLK6MSYI/"
    "export?format=csv&gid=0"
)

# Devanagari swara letter per Ayugma entry id. The sheet has no Devanagari
# column; this map associates each entry with the marker character(s) it
# represents. Multi-character entries (A15/A17/A19) are combined clusters.
AYUGMA_DEVANAGARI = {
    "A01": "\u0915",  # क Ka
    "A02": "\u0916",  # ख Kha
    "A03": "\u091A",  # च Ca
    "A04": "\u091F",  # ट Ta (sheet glyph now canonical U+1131F)
    "A05": "\u0923",  # ण Na
    "A06": "\u0924",  # त Ta
    "A07": "\u0925",  # थ Tha
    "A08": "\u092A",  # प Pa
    "A09": "\u092B",  # फ Pha
    "A10": "\u092D",  # भ Bha
    "A11": "\u092F",  # य Ya
    "A12": "\u0938",  # स Sa
    "A13": "\u0936",  # श Saa (Malayalam ശ per manuscript)
    "A14": "\u0937",  # ष Ssa
    "A15": "\u092A\u094D\u0932",  # प्ल Pla
    "A16": "\u0919",  # ङ Nga
    "A17": "\u0924\u094D\u0930",  # त्र Tra
    "A18": "\u0930",  # र Ra
    "A19": "\u0915\u094D\u0930",  # क्र Kra
}

# Fixed matra table: Devanagari dependent vowel sign -> Grantha dependent sign.
# Grantha has no dependent vocalic signs; those two rows are deliberately empty
# (U+11343/U+11344 exist only as independent vowels in the block).
MATRA_TABLE = {
    "\u093E": "\U0001133E",  # AA
    "\u093F": "\U0001133F",  # I
    "\u0940": "\U00011340",  # II
    "\u0941": "\U00011341",  # U
    "\u0942": "\U00011342",  # UU
    "\u0943": "\U00011343",  # VOCALIC R
    "\u0944": "\U00011344",  # VOCALIC RR
    "\u0947": "\U00011347",  # E
    "\u0948": "\U00011348",  # AI
    "\u094B": "\U0001134B",  # O
    "\u094C": "\U0001134C",  # AU
    "\u0902": "\U00011302",  # ANUSVARA
    "\u0903": "\U00011303",  # VISARGA
    "\u094D": "\U0001134D",  # VIRAMA
}


def parse_row(row: list[str], category: str) -> dict:
    raw_id = row[0].strip()
    glyph = row[2].strip() if len(row) > 2 else ""
    grantha_hex = row[3].strip() if len(row) > 3 else ""
    mal_char = row[7].strip() if len(row) > 7 else ""
    mal_name = row[8].strip() if len(row) > 8 else ""
    meaning = row[9].strip() if len(row) > 9 else ""
    notes = row[10].strip() if len(row) > 10 else ""
    text = glyph.strip()
    return {
        "id": raw_id,
        "category": category,
        "devanagari_char": AYUGMA_DEVANAGARI.get(raw_id, ""),
        "grantha_text": text,
        "grantha_codepoints": [f"{ord(ch):04X}" for ch in text],
        "sheet_hex_reference": grantha_hex,
        "malayalam_char": mal_char,
        "malayalam_name": mal_name,
        "meaning": meaning,
        "notes": notes,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_path", type=Path)
    parser.add_argument("--out", type=Path, default=Path(__file__).parent / "swara_mapping.json")
    args = parser.parse_args()

    with open(args.csv_path, encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.reader(fh))

    ayugma: list[dict] = []
    modifiers: list[dict] = []

    mode = "swara"
    for row in rows:
        cells = [c.strip() for c in row]
        if not any(cells):
            continue
        if cells[0].startswith("Sl No"):
            mode = "modifier"
            continue
        if mode == "swara":
            raw_id = cells[0]
            if raw_id.startswith("A"):
                ayugma.append(parse_row(cells, "ayugma"))
        else:
            if not cells[0] or cells[0].startswith("Sl No"):
                continue
            sl_no = cells[0]
            glyph = cells[1] if len(cells) > 1 else ""
            how_to_enter = cells[2] if len(cells) > 2 else ""
            example = cells[3] if len(cells) > 3 else ""
            direct_input = cells[4] if len(cells) > 4 else ""
            stack_pos = cells[5] if len(cells) > 5 else ""
            color = cells[6] if len(cells) > 6 else "green"
            modifier_sym = cells[7] if len(cells) > 7 else ""

            modifiers.append(
                {
                    "sl_no": sl_no,
                    "glyph": glyph,
                    "how_to_enter": how_to_enter,
                    "example": example,
                    "direct_input": direct_input,
                    "stack_pos": stack_pos or ("Above" if modifier_sym in ("(A)", "(F)", "(G)", "(I)", "(L)") else "Below" if modifier_sym in ("(B)", "(H)", "(J)", "(J_1)", "(K)") else "Inline"),
                    "color": color,
                    "modifier_symbol": modifier_sym,
                }
            )

    missing_dev = [e["id"] for e in ayugma if not e["devanagari_char"]]
    if missing_dev:
        raise ValueError(f"Ayugma entries without Devanagari letter: {missing_dev}")

    result = {
        "_meta": {
            "source": SHEET_URL,
            "export_date": date.today().isoformat(),
            "description": (
                "Authoritative swara and modifier mapping for the Jaimineeya Samaveda "
                "Malayalam transliteration and rendering pipeline. Contains Ayugma swara "
                "bases (A01-A19), fixed matra table, and 12 Canonical Vedic Modifiers (A-L)."
            ),
            "manuscript_truth_notes": (
                "A13 (Saa): the Grantha Glyph column holds the MALAYALAM "
                "character ശ (U+0D36), as in the reference manuscript; the "
                "hex column shows the Grantha U+11336 for reference."
            ),
            "modifier_status": "active_phase_1",
            "matra_table_notes": (
                "Devanagari dependent vowel sign -> Grantha dependent sign. "
                "The marker text is decomposed per syllable, then a Consonant "
                "or Modifier glyph from the Ayugma table is combined with the "
                "fixed matra from this table."
            ),
        },
        "matra_table": {f"U+{ord(d):04X}": f"U+{ord(g):04X}" for d, g in MATRA_TABLE.items()},
        "ayugma": ayugma,
        "modifiers": modifiers,
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(result, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    a_entries = {e["id"]: e["grantha_text"] for e in ayugma}
    print(f"Wrote {args.out}")
    print(f"  Ayugma  entries: {len(ayugma)}")
    print(f"  Modifier entries: {len(modifiers)} (deferred)")
    print(f"  Matra table rows: {len(MATRA_TABLE)}")
    for k in ["A01", "A04", "A13", "A15", "A17", "A19"]:
        entry = a_entries.get(k)
        if entry is None:
            continue
        name = next(e["malayalam_name"] for e in ayugma if e["id"] == k)
        print(f"    {k}: {entry!r}  ({name})")


if __name__ == "__main__":
    main()