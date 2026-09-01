"""
Apply corrections from Excel file to the JSON data.

This script reads the JSV_Samam_Granular_Table.xlsx file and applies 
metadata corrections (Rik_Rishi, Rik_Devata, Rik_Chandas, Samam_Rishi, 
Samam_Devata, Samam_Chandas) back to the source JSON file.

Workflow:
1. Run generate_granular_table.py to create Excel file
2. User edits metadata columns in Excel
3. Run this script to apply corrections to JSON
4. Run render_pdf.py to regenerate outputs

Usage:
    python src/apply_excel_corrections.py [--dry-run]

Options:
    --dry-run    Show what would be changed without modifying the JSON
"""

import json
import os
import sys
import argparse
from datetime import datetime

# Configure stdout for UTF-8 to handle Sanskrit characters on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

try:
    import openpyxl
except ImportError:
    print("ERROR: 'openpyxl' library is required.")
    print("Install it with: pip install openpyxl")
    sys.exit(1)

# File paths
EXCEL_FILE = r'data\output\JSV_Samam_Granular_Table.xlsx'
JSON_FILE = r'data\output\Samhita_with_Rishi_Devata_Chandas_out.json'
BACKUP_SUFFIX = '_backup'

# Column mappings: Excel column name -> JSON field name
# These are the fields that can be edited in Excel and applied to JSON
CORRECTION_COLUMNS = {
    # Individual parsed fields
    'Rik_Rishi': 'rik_rishi',
    'Rik_Devata': 'rik_devata', 
    'Rik_Chandas': 'rik_chandas',
    'Samam_Rishi': 'samam_rishi',
    'Samam_Devata': 'samam_devata',
    'Samam_Chandas': 'samam_chandas',
    # Full metadata strings
    'Rik_Metadata': 'rik_metadata',
    'Saman_Metadata': 'saman_metadata',
}

# Columns used to identify the subsection
KEY_COLUMNS = ['Patha_Num', 'Rik_ID', 'Arsheyam_Num', 'Global_Samam_Num']


def load_excel_data(excel_path):
    """Load data from Excel file, skipping the metadata row."""
    print(f"Loading Excel file: {excel_path}")
    
    wb = openpyxl.load_workbook(excel_path, read_only=True)
    ws = wb.active
    
    rows = list(ws.iter_rows(values_only=True))
    
    # Row 1 is metadata, Row 2 is headers, Row 3+ is data
    if len(rows) < 3:
        print("ERROR: Excel file has no data rows")
        return None, None
    
    headers = list(rows[1])  # Row 2 (0-indexed: 1)
    data_rows = rows[2:]     # Row 3 onwards
    
    print(f"Found {len(data_rows)} data rows")
    print(f"Headers: {headers}")
    
    wb.close()
    return headers, data_rows


def load_json_data(json_path):
    """Load the JSON data."""
    print(f"Loading JSON file: {json_path}")
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def find_subsection(data, patha_num, rik_id, arsheyam_num):
    """
    Find a subsection in the JSON data by its identifiers.
    Returns (supersection_key, section_key, subsection_key, subsection_data) or None
    """
    supersection_container = data.get('supersection', {})
    
    for ss_key, ss_data in supersection_container.items():
        # Check patha number
        ss_num = int(ss_key.split('_')[1]) if '_' in ss_key else 0
        if ss_num != patha_num:
            continue
            
        sections = ss_data.get('sections', {})
        for sec_key, sec_data in sections.items():
            subsections = sec_data.get('subsections', {})
            for sub_key, sub_data in subsections.items():
                sub_rik_id = sub_data.get('rik_id', 0)
                header_data = sub_data.get('header', {})
                sub_arsheyam_num = header_data.get('header_number', 0)
                
                # Match by rik_id and arsheyam_num
                try:
                    if int(sub_rik_id) == int(rik_id) and int(sub_arsheyam_num) == int(arsheyam_num):
                        return (ss_key, sec_key, sub_key, sub_data)
                except (ValueError, TypeError):
                    continue
    
    return None


def normalize_value(value):
    """Normalize a value for comparison - strip whitespace, handle None."""
    if value is None:
        return ''
    return str(value).strip()


def apply_corrections(data, headers, excel_rows, dry_run=False):
    """
    Apply corrections from Excel to JSON data.
    Returns (modified_data, change_count, error_count, changes, errors)
    """
    # Build column index map
    col_idx = {h: i for i, h in enumerate(headers) if h}
    
    # Verify required columns exist
    missing_keys = [k for k in KEY_COLUMNS if k not in col_idx]
    if missing_keys:
        print(f"ERROR: Required columns not found in Excel: {missing_keys}")
        return data, 0, 1, [], [f"Missing key columns: {missing_keys}"]
    
    # Check which correction columns are available
    available_corrections = {k: v for k, v in CORRECTION_COLUMNS.items() if k in col_idx}
    print(f"Correction columns found: {list(available_corrections.keys())}")
    
    if not available_corrections:
        print("ERROR: No correction columns found in Excel")
        return data, 0, 1, [], ["No correction columns found"]
    
    changes = []
    errors = []
    
    # Track unique subsections we've already updated (to avoid duplicate updates)
    updated_subsections = set()
    
    for row_num, row in enumerate(excel_rows, start=3):  # Excel row 3 onwards
        try:
            patha_num = int(row[col_idx['Patha_Num']] or 0)
            rik_id = int(row[col_idx['Rik_ID']] or 0)
            arsheyam_num = int(row[col_idx['Arsheyam_Num']] or 0)
            global_samam = int(row[col_idx['Global_Samam_Num']] or 0)
        except (ValueError, TypeError) as e:
            errors.append(f"Row {row_num}: Could not parse key columns - {e}")
            continue
        
        # Find the subsection
        result = find_subsection(data, patha_num, rik_id, arsheyam_num)
        if not result:
            errors.append(f"Row {row_num}: Could not find subsection (Patha={patha_num}, Rik={rik_id}, Arsheyam={arsheyam_num})")
            continue
        
        ss_key, sec_key, sub_key, sub_data = result
        subsection_id = (ss_key, sec_key, sub_key)
        
        # Skip if we've already updated this subsection (multiple Samams share same Rik)
        if subsection_id in updated_subsections:
            continue
        
        updated_subsections.add(subsection_id)
        
        # Check each correction column
        for excel_col, json_field in available_corrections.items():
            excel_value = normalize_value(row[col_idx[excel_col]])
            current_value = normalize_value(sub_data.get(json_field, ''))
            
            # Only record a change if the Excel value is different AND non-empty
            # (empty Excel values don't overwrite existing data)
            if excel_value and excel_value != current_value:
                changes.append({
                    'row': row_num,
                    'subsection': sub_key,
                    'field': json_field,
                    'excel_col': excel_col,
                    'old': current_value,
                    'new': excel_value,
                    'path': f"{ss_key}/{sec_key}/{sub_key}"
                })
                
                if not dry_run:
                    # Apply the change directly to the subsection data
                    sub_data[json_field] = excel_value
    
    return data, len(changes), len(errors), changes, errors


def backup_json(json_path):
    """Create a backup of the JSON file."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = json_path.replace('.json', f'{BACKUP_SUFFIX}_{timestamp}.json')
    
    with open(json_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Backup created: {backup_path}")
    return backup_path


def save_json(data, json_path):
    """Save the modified JSON data."""
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"JSON saved: {json_path}")


def main():
    parser = argparse.ArgumentParser(description='Apply Excel corrections to JSON')
    parser.add_argument('--dry-run', action='store_true', 
                        help='Show changes without modifying JSON')
    parser.add_argument('--excel', default=EXCEL_FILE,
                        help=f'Path to Excel file (default: {EXCEL_FILE})')
    parser.add_argument('--json', default=JSON_FILE,
                        help=f'Path to JSON file (default: {JSON_FILE})')
    args = parser.parse_args()
    
    print("=" * 60)
    print("Excel to JSON Metadata Correction Tool")
    print("=" * 60)
    print(f"\nFields that can be corrected:")
    for excel_col, json_field in CORRECTION_COLUMNS.items():
        print(f"  {excel_col} -> {json_field}")
    print()
    
    # Check files exist
    if not os.path.exists(args.excel):
        print(f"ERROR: Excel file not found: {args.excel}")
        sys.exit(1)
    
    if not os.path.exists(args.json):
        print(f"ERROR: JSON file not found: {args.json}")
        sys.exit(1)
    
    # Load data
    headers, excel_rows = load_excel_data(args.excel)
    if headers is None:
        sys.exit(1)
    
    json_data = load_json_data(args.json)
    
    # Apply corrections
    print(f"\n{'DRY RUN - ' if args.dry_run else ''}Scanning for changes...")
    
    modified_data, change_count, error_count, changes, errors = apply_corrections(
        json_data, headers, excel_rows, dry_run=args.dry_run
    )
    
    # Report errors
    if errors:
        print(f"\n=== Errors ({len(errors)}) ===")
        for err in errors[:10]:  # Show first 10
            print(f"  [!] {err}")
        if len(errors) > 10:
            print(f"  ... and {len(errors) - 10} more errors")
    
    # Report changes
    if changes:
        print(f"\n=== Changes ({'Would be made' if args.dry_run else 'Applied'}: {change_count}) ===")
        
        # Group changes by field for summary
        from collections import Counter
        field_counts = Counter(c['excel_col'] for c in changes)
        print("\nSummary by field:")
        for field, count in sorted(field_counts.items()):
            print(f"  {field}: {count} changes")
        
        print("\nDetails (first 20):")
        for change in changes[:20]:
            print(f"  [{change['subsection']}] {change['excel_col']}:")
            old_display = change['old'][:40] + '...' if len(change['old']) > 40 else change['old']
            new_display = change['new'][:40] + '...' if len(change['new']) > 40 else change['new']
            print(f"    '{old_display}' -> '{new_display}'")
        if change_count > 20:
            print(f"  ... and {change_count - 20} more changes")
    else:
        print("\n[OK] No changes detected. Excel values match JSON.")
    
    # Save if not dry run and there are changes
    if not args.dry_run and change_count > 0:
        backup_json(args.json)
        save_json(modified_data, args.json)
        print(f"\n[OK] Applied {change_count} corrections to JSON")
        print("\nNext steps:")
        print("  1. Run: python src/render_pdf.py")
        print("  2. Run: python src/generate_website.py")
    elif args.dry_run and change_count > 0:
        print(f"\n[>>] Would apply {change_count} corrections")
        print("  Run without --dry-run to apply changes")
    
    print("\n" + "=" * 60)


if __name__ == '__main__':
    main()
