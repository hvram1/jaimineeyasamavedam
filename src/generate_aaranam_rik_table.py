"""
Generate a Rik-level table for Aaranam from the plain text input file.

This script parses data/input/Aaranam_rik.txt and produces a CSV table with:
Global_Rik_Num, Patha_Name, Khanda, Rik_ID, Rik_Text

Unlike the Samhita Rik table (which reads from a pre-parsed JSON), this script
works directly from the Aaranam Rik text input, parsing the Supersection/Khanda
hierarchy and verse delimiters (॥ N ॥) from raw Unicode text.

Usage:
    python src/generate_aaranam_rik_table.py [input_file] [-o output_csv]

Examples:
    # Use defaults:
    python src/generate_aaranam_rik_table.py

    # Specify input file:
    python src/generate_aaranam_rik_table.py data/input/Aaranam_rik.txt

    # Specify both input and output:
    python src/generate_aaranam_rik_table.py data/input/Aaranam_rik.txt -o data/output/Aaranam_Rik_Table.csv
"""
import argparse
import csv
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
from utils import get_generated_metadata, load_pipeline_config

DEFAULT_INPUT = r'data\input\Aaranam_rik.txt'
DEFAULT_OUTPUT_CSV = r'data\output\Aaranam_Rik_Table.csv'

# Devanagari digits
DEVANAGARI_DIGITS = '०१२३४५६७८९'


def devanagari_to_int(text):
    """Convert a Devanagari numeral string to an integer."""
    result = text
    for i, char in enumerate(DEVANAGARI_DIGITS):
        result = result.replace(char, str(i))
    try:
        return int(result)
    except ValueError:
        return 0


def replace_accents_unicode(text):
    """
    Replaces ASCII parenthesis accent markers with actual Unicode accents.
    (1): Swarita (U+0951)
    (2): Anudatta (U+1CD2)
    (3): Kampa (U+1CF8)
    (4): Trikampa (U+1CF9)
    """
    if not text:
        return text
    replacements = [
        ('(1)', '\u0951'),
        ('(2)', '\u1CD2'),
        ('(3)', '\u1CF8'),
        ('(4)', '\u1CF9'),
    ]
    for marker, unicode_val in replacements:
        text = text.replace(marker, unicode_val)
    return text


def parse_aaranam_rik_text(input_file):
    """
    Parse the Aaranam Rik text file and extract structured Rik data.

    The file uses the following conventions:
      - ``# Supersection title #`` / ``# End of Supersection title#``
        enclose the Patha name (e.g., ``॥ अथ आरण पाठः ॥``).
      - ``॥ अथ ... खण्डः ॥`` marks Khanda boundaries.
      - ``॥ N ॥``  (Devanagari numeral) terminates each Rik.
      - ``॥ इत्य.../इति ... समाप्तः/पर्वः ॥`` are colophon lines.

    Returns a list of dicts:
        [{ Global_Rik_Num, Patha_Name, Khanda, Rik_ID, Rik_Text }, ...]
    """
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # ── Regex patterns ──────────────────────────────────────────────
    # Verse number (Rik delimiter): ॥ N ॥
    verse_re = re.compile(r'॥\s*([०-९\d]+)\s*॥')
    # Khanda header: ॥ अथ <ordinal> खण्डः ॥
    khanda_re = re.compile(r'॥\s*अथ\s+(.*?खण्डः)\s*॥')
    # Colophon / end markers (handles sandhi forms like इत्यारण = इति+आरण)
    end_re = re.compile(r'॥\s*(इत्य|इति)')

    # ── State ────────────────────────────────────────────────────────
    rows = []
    global_rik_counter = 0
    current_patha = ""
    current_khanda = ""
    rik_buffer = []          # accumulated text fragments for the current Rik
    in_ss_title = False      # inside a supersection title block

    for line in lines:
        line = line.rstrip('\r\n')
        stripped = line.strip()

        # Skip blank lines
        if not stripped:
            continue

        # ── Supersection title block ────────────────────────────────
        if stripped.startswith('# Supersection title #') or stripped.startswith('# Title #'):
            in_ss_title = True
            rik_buffer = []  # clear buffer at supersection boundary
            continue

        if stripped.startswith('# End of Supersection title') or stripped.startswith('# End of Title'):
            in_ss_title = False
            continue

        if in_ss_title:
            # Extract Patha name: strip ॥ delimiters and "अथ " prefix
            patha = stripped.strip('॥').strip()
            if patha.startswith('अथ'):
                patha = patha[len('अथ'):].strip()
            current_patha = patha
            current_khanda = ""   # reset khanda for new supersection
            continue

        # ── Khanda header ───────────────────────────────────────────
        khanda_match = khanda_re.search(stripped)
        if khanda_match and not verse_re.search(stripped):
            # Pure khanda header line (no verse number on the same line)
            current_khanda = khanda_match.group(1).strip()
            continue

        # ── Colophon / end marker ───────────────────────────────────
        if end_re.search(stripped) and not verse_re.search(stripped):
            continue

        # ── Content line: scan for ॥ N ॥ verse delimiters ──────────
        remaining = stripped
        while remaining:
            match = verse_re.search(remaining)
            if match:
                # Text before the delimiter belongs to the current Rik
                before_text = remaining[:match.start()].strip()
                if before_text:
                    rik_buffer.append(before_text)

                # Extract the Rik ID from the Devanagari numeral
                rik_id = devanagari_to_int(match.group(1))

                # Finalize the current Rik
                if rik_buffer:
                    global_rik_counter += 1
                    combined_text = ' '.join(rik_buffer)
                    clean_text = replace_accents_unicode(combined_text)

                    rows.append({
                        'Global_Rik_Num': global_rik_counter,
                        'Patha_Name': current_patha,
                        'Khanda': current_khanda,
                        'Rik_ID': rik_id,
                        'Rik_Text': clean_text,
                    })
                    rik_buffer = []

                # Continue scanning text after the delimiter
                remaining = remaining[match.end():].strip()
            else:
                # No more verse delimiters – buffer the remaining text
                if remaining.strip():
                    rik_buffer.append(remaining.strip())
                break

    return rows


def main(input_file=None, output_csv=None):
    """Entry point: load config, parse text, write CSV."""
    # 0. Load Configuration
    pipeline_cfg = load_pipeline_config()
    aaranam_table_cfg = pipeline_cfg.get('generate_aaranam_rik_table', {})

    input_file = input_file or aaranam_table_cfg.get('input') or DEFAULT_INPUT
    output_csv = output_csv or aaranam_table_cfg.get('output_csv') or DEFAULT_OUTPUT_CSV

    # Get metadata
    metadata = get_generated_metadata()
    JSV_VERSION = metadata['version']
    GENERATED_AT = metadata['generated_at']

    print(f"Generating Aaranam Rik Table (v{JSV_VERSION})...")
    print(f"Input File : {input_file}")
    print(f"Output CSV : {output_csv}")

    # Validate input
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found.")
        return

    # Parse the text file
    rows = parse_aaranam_rik_text(input_file)

    # Write CSV with UTF-8 BOM for Excel compatibility
    with open(output_csv, 'w', encoding='utf-8-sig', newline='') as f:
        # Line 1: <Filename> <Version> <Timestamp>
        filename = os.path.basename(output_csv)
        f.write(f"{filename} {JSV_VERSION} {GENERATED_AT}\n")

        fieldnames = [
            'Global_Rik_Num', 'Patha_Name', 'Khanda', 'Rik_ID', 'Rik_Text'
        ]

        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nCSV saved to: {output_csv}")
    print(f"Total Aaranam Riks: {len(rows)}")

    # Summary by Patha and Khanda (encoding-safe for Windows console)
    def safe_print(msg):
        try:
            print(msg)
        except UnicodeEncodeError:
            print(msg.encode('ascii', 'replace').decode('ascii'))

    safe_print("\n--- Summary ---")
    current_p = None
    for r in rows:
        if r['Patha_Name'] != current_p:
            current_p = r['Patha_Name']
            patha_rows = [x for x in rows if x['Patha_Name'] == current_p]
            safe_print(f"\n  {current_p}  ({len(patha_rows)} Riks)")
            # Khandas within this Patha
            seen_khandas = []
            for pr in patha_rows:
                k = pr['Khanda'] or "(no khanda)"
                if k not in seen_khandas:
                    seen_khandas.append(k)
            for k in seen_khandas:
                k_count = sum(1 for x in patha_rows if (x['Khanda'] or "(no khanda)") == k)
                safe_print(f"    {k}: {k_count} Riks")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate a Rik-level table for Aaranam from plain text input."
    )
    parser.add_argument("input", nargs="?", default=DEFAULT_INPUT,
                        help=f"Input text file (default: {DEFAULT_INPUT})")
    parser.add_argument("-o", "--output", default=DEFAULT_OUTPUT_CSV,
                        help=f"Output CSV file (default: {DEFAULT_OUTPUT_CSV})")

    args = parser.parse_args()
    main(input_file=args.input, output_csv=args.output)
