"""
Generate a report listing Riks and/or Samams that are missing metadata.
Reads from: data/output/JSV_Samam_Granular_Table.csv
Outputs to: data/output/JSV_Missing_Metadata_Report.md (and .csv)

Supports CLI modes:
  --mode rik       Only Rik-level missing metadata (deduplicated)
  --mode samam     Only Samam-level missing metadata
  --mode combined  Both Rik and Samam sections (default)

The n:1 Samam-to-Rik mapping means multiple Samams can share a single Rik.
In 'rik' mode, each unique Rik is reported only once, avoiding false positives.
"""
import csv
import os
import sys
import datetime
import argparse

INPUT_CSV = r'data\output\JSV_Samam_Granular_Table.csv'
OUTPUT_MD = r'data\output\JSV_Missing_Metadata_Report.md'
OUTPUT_CSV = r'data\output\JSV_Missing_Metadata.csv'


def load_granular_table():
    """Load the Samam granular table, skipping the metadata first line."""
    if not os.path.exists(INPUT_CSV):
        print(f"Error: Input file {INPUT_CSV} not found.")
        return []

    rows = []
    with open(INPUT_CSV, 'r', encoding='utf-8-sig') as f:
        f.readline()  # Skip metadata line (Filename Version Timestamp)
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def find_rik_issues(rows):
    """
    Find Rik-level metadata issues, deduplicated by (Patha, Khanda, Rik_ID).
    Since the Samam-Rik mapping is n:1, multiple Samams share the same Rik.
    We only report each unique Rik once.
    """
    seen_riks = set()
    rik_issues = []

    for row in rows:
        patha = row.get('Patha_Name', '')
        khanda = row.get('Khanda', '')
        rik_id = row.get('Rik_ID', '')
        rik_text = row.get('Rik_Text', '').strip()
        rik_meta = row.get('Rik_Metadata', '').strip()

        # Deduplicate by unique Rik identity
        rik_key = (patha, khanda, rik_id)
        if rik_key in seen_riks:
            continue
        seen_riks.add(rik_key)

        missing_fields = []

        # Check: Rik Metadata exists but Text is missing
        if rik_meta and not rik_text:
            missing_fields.append('Missing_Rik_Text')

        # Check: Rik Text exists but Metadata is missing
        if rik_text and not rik_meta:
            missing_fields.append('Missing_Rik_Metadata')

        # Check: Both Rik Text AND Metadata are missing (Rik has no data at all)
        if not rik_text and not rik_meta:
            missing_fields.append('Missing_Rik_Text')
            missing_fields.append('Missing_Rik_Metadata')

        if missing_fields:
            rik_issues.append({
                'Patha': patha,
                'Khanda': khanda,
                'Rik_ID': rik_id,
                'Missing': ', '.join(missing_fields)
            })

    return rik_issues


def find_samam_issues(rows):
    """
    Find Samam-level metadata issues.
    Each row in the granular table IS a Samam, so we check per row.
    """
    samam_issues = []

    for row in rows:
        patha = row.get('Patha_Name', '')
        khanda = row.get('Khanda', '')
        rik_id = row.get('Rik_ID', '')
        samam_num = row.get('Samam_Num', '')
        global_samam = row.get('Global_Samam_Num', '0')
        saman_meta = row.get('Saman_Metadata', '').strip()

        missing_fields = []

        # Check: Samam Metadata is missing
        if not saman_meta:
            missing_fields.append('Missing_Saman_Metadata')

        if missing_fields:
            samam_issues.append({
                'Patha': patha,
                'Khanda': khanda,
                'Rik_ID': rik_id,
                'Samam_Num': samam_num,
                'Global_Samam_Num': global_samam,
                'Missing': ', '.join(missing_fields)
            })

    return samam_issues


def write_markdown_report(rik_issues, samam_issues, mode, timestamp):
    """Write the Markdown report based on mode."""
    with open(OUTPUT_MD, 'w', encoding='utf-8') as f:
        f.write("# JSV Missing Metadata Report\n\n")
        f.write(f"**Generated:** {timestamp}\n")
        f.write(f"**Mode:** {mode}\n\n")

        # --- Summary ---
        f.write("## Summary\n\n")
        if mode in ('rik', 'combined'):
            f.write(f"- **Rik-level issues:** {len(rik_issues)}\n")
        if mode in ('samam', 'combined'):
            f.write(f"- **Samam-level issues:** {len(samam_issues)}\n")

        total = 0
        if mode == 'rik':
            total = len(rik_issues)
        elif mode == 'samam':
            total = len(samam_issues)
        else:
            total = len(rik_issues) + len(samam_issues)
        f.write(f"- **Total issues:** {total}\n\n")

        # --- Rik Section ---
        if mode in ('rik', 'combined'):
            f.write("---\n\n")
            f.write("## Rik-Level Issues\n\n")
            f.write("Each unique Rik is listed once (deduplicated across n:1 Samam mappings).\n\n")

            if rik_issues:
                f.write("| Patha | Khanda | Rik ID | Missing Fields |\n")
                f.write("|---|---|---|---|\n")
                for e in rik_issues:
                    f.write(f"| {e['Patha']} | {e['Khanda']} | {e['Rik_ID']} | {e['Missing']} |\n")
            else:
                f.write("✅ **No Rik-level metadata issues found!**\n")
            f.write("\n")

        # --- Samam Section ---
        if mode in ('samam', 'combined'):
            f.write("---\n\n")
            f.write("## Samam-Level Issues\n\n")

            if samam_issues:
                f.write("| Patha | Khanda | Rik ID | Samam Num | Missing Fields |\n")
                f.write("|---|---|---|---|---|\n")
                for e in samam_issues:
                    f.write(f"| {e['Patha']} | {e['Khanda']} | {e['Rik_ID']} | {e['Samam_Num']} | {e['Missing']} |\n")
            else:
                f.write("✅ **No Samam-level metadata issues found!**\n")
            f.write("\n")

    print(f"Markdown report saved to {OUTPUT_MD}")


def write_csv_report(rik_issues, samam_issues, mode):
    """Write the CSV report for easy filtering."""
    all_entries = []

    if mode in ('rik', 'combined'):
        for e in rik_issues:
            all_entries.append({
                'Level': 'Rik',
                'Patha': e['Patha'],
                'Khanda': e['Khanda'],
                'Rik_ID': e['Rik_ID'],
                'Samam_Num': '',
                'Global_Samam_Num': '',
                'Missing': e['Missing']
            })

    if mode in ('samam', 'combined'):
        for e in samam_issues:
            all_entries.append({
                'Level': 'Samam',
                'Patha': e['Patha'],
                'Khanda': e['Khanda'],
                'Rik_ID': e['Rik_ID'],
                'Samam_Num': e['Samam_Num'],
                'Global_Samam_Num': e.get('Global_Samam_Num', ''),
                'Missing': e['Missing']
            })

    if all_entries:
        with open(OUTPUT_CSV, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'Level', 'Patha', 'Khanda', 'Rik_ID', 'Samam_Num', 'Global_Samam_Num', 'Missing'
            ])
            writer.writeheader()
            writer.writerows(all_entries)
        print(f"CSV report saved to {OUTPUT_CSV}")


def check_missing_metadata(mode='combined'):
    """Main function to check for missing metadata."""
    print(f"Checking for missing metadata (mode: {mode}) in {INPUT_CSV}...")

    rows = load_granular_table()
    if not rows:
        return

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Compute issues based on mode
    rik_issues = []
    samam_issues = []

    if mode in ('rik', 'combined'):
        rik_issues = find_rik_issues(rows)
        print(f"  Rik-level issues (deduplicated): {len(rik_issues)}")

    if mode in ('samam', 'combined'):
        samam_issues = find_samam_issues(rows)
        print(f"  Samam-level issues: {len(samam_issues)}")

    # Generate reports
    write_markdown_report(rik_issues, samam_issues, mode, timestamp)
    write_csv_report(rik_issues, samam_issues, mode)

    total = len(rik_issues) + len(samam_issues)
    print(f"Total issues: {total}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate missing metadata report for JSV Samhita data.",
        epilog="Examples:\n"
               "  python generate_missing_metadata_report.py --mode rik\n"
               "  python generate_missing_metadata_report.py --mode samam\n"
               "  python generate_missing_metadata_report.py --mode combined\n",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        '--mode', '-m',
        choices=['rik', 'samam', 'combined'],
        default='combined',
        help="Report mode: 'rik' (Rik-level only, deduplicated), "
             "'samam' (Samam-level only), "
             "'combined' (both, default)"
    )

    args = parser.parse_args()
    check_missing_metadata(mode=args.mode)
