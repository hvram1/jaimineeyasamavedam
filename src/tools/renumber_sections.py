import re
import argparse
from pathlib import Path
import sys

def main():
    parser = argparse.ArgumentParser(description="Renumber supersections, sections, and subsections in a Jaimineeya text file.")
    parser.add_argument('input_file', help="Path to the input text file")
    parser.add_argument('--start-super', type=int, default=1, help="Starting number for supersections")
    parser.add_argument('--start-sec', type=int, default=1, help="Starting number for sections")
    parser.add_argument('--start-sub', type=int, default=1, help="Starting number for subsections")
    parser.add_argument('--dry-run', action='store_true', help="Print changes without writing to file")
    
    args = parser.parse_args()
    input_path = Path(args.input_file)
    
    if not input_path.exists():
        print(f"Error: {input_path} not found")
        sys.exit(1)

    print(f"Processing: {input_path}")
    print(f"Starting at: SuperSection {args.start_super}, Section {args.start_sec}, SubSection {args.start_sub}")

    with open(input_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    current_sup_val = args.start_super - 1
    current_sec_val = args.start_sec - 1
    current_sub_val = args.start_sub # Initial subsection number
    
    new_lines = []
    
    # Trackers for stats
    sup_ids = set()
    sec_ids = set()
    sub_ids = set()

    for i, line in enumerate(lines):
        modified = False
        original_line = line
        
        # Check for start markers to increment counters
        if '# Start of SuperSection Title' in line:
            current_sup_val += 1
        if '# Start of Section Title' in line:
            current_sec_val += 1
            
        # Replace markers in the line
        # Use lambda for counting if needed, but here we use simple sequential increments
        
        # Subsection replace
        if 'subsection_' in line:
            line = re.sub(r'subsection_\d+', f'subsection_{current_sub_val}', line)
            sub_ids.add(current_sub_val)
            modified = True
            
        # Section replace (matches 'section_N' but not 'supersection_N' or 'subsection_N')
        # Negative lookbehind ensures we don't accidentally match 'super' or 'sub' prefixes
        if 'section_' in line and 'supersection_' not in line and 'subsection_' not in line:
            line = re.sub(r'(?<!super)(?<!sub)section_\d+', f'section_{current_sec_val}', line)
            sec_ids.add(current_sec_val)
            modified = True
            
        # Supersection replace
        if 'supersection_' in line:
            line = re.sub(r'supersection_\d+', f'supersection_{current_sup_val}', line)
            sup_ids.add(current_sup_val)
            modified = True
        
        new_lines.append(line)
        
        # Increment subsection count AFTER the end of the mantra sets block
        # This ensures all markers for the SAME subsection (Title Start/End, Mantra Start/End) have the same number
        if '#End of Mantra Sets' in line or '# End of Mantra Sets' in line:
            current_sub_val += 1

    if args.dry_run:
        print("Dry run complete. No changes written.")
    else:
        with open(input_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        print(f"Successfully updated {input_path}")

    print(f"Final Counts:")
    print(f"  SuperSections: {len(sup_ids)} ({min(sup_ids) if sup_ids else 'N/A'} - {max(sup_ids) if sup_ids else 'N/A'})")
    print(f"  Sections: {len(sec_ids)} ({min(sec_ids) if sec_ids else 'N/A'} - {max(sec_ids) if sec_ids else 'N/A'})")
    print(f"  SubSections: {len(sub_ids)} ({min(sub_ids) if sub_ids else 'N/A'} - {max(sub_ids) if sub_ids else 'N/A'})")

if __name__ == "__main__":
    main()
