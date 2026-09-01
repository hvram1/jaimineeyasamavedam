import json
import re
import argparse
import sys
from collections import defaultdict
from pathlib import Path

# Regex to match Samam numbers like ॥ 1 ॥ or || 1 || or ||1||
# We capture the number part.
SAMAM_PATTERN = re.compile(r'(?:॥|\|\|)\s*([\d०-९]+)\s*(?:॥|\|\|)')

def extract_samam_numbers(text):
    """Parses Samam numbers from mantra text."""
    if not text:
        return []
    
    # Use findall to get all matches. The regex captures the number group.
    # checking for both whole matches or just capturing group might be needed 
    # depending on how re.findall works with groups. 
    # If regex has capturing groups, findall returns list of groups.
    matches = SAMAM_PATTERN.findall(text)
    numbers = []
    
    dev_map = {'०': '0', '१': '1', '२': '2', '३': '3', '४': '4',
               '५': '5', '६': '6', '७': '7', '८': '8', '९': '9'}
               
    for m in matches:
        # m is the captured number string because of the capturing group in regex
        # Convert to Arabic
        arabic_num = ''.join(dev_map.get(c, c) for c in m)
        try:
            numbers.append(int(arabic_num))
        except ValueError:
            pass
            
    return numbers

def check_continuity(json_file, output_report=None):
    json_path = Path(json_file)
    if not json_path.exists():
        print(f"Error: File not found: {json_path}")
        return

    if output_report is None:
        output_report = json_path.parent / f"{json_path.stem}_continuity_report.txt"
    
    print(f"Reading JSON: {json_path}...")
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return

    report_lines = []
    report_lines.append(f"CONTINUITY CHECK REPORT")
    report_lines.append(f"File: {json_path.name}")
    report_lines.append("=" * 60)
    
    issues_found = False
    
    # Track statistics
    total_parvas = 0
    total_khandas = 0
    total_samas = 0

    # Traverse structure
    # Detect root container
    if 'supersection' in data:
        supersection_container = data['supersection']
    elif 'parvas' in data:
         supersection_container = data['parvas']
    else:
        # Assume the dict itself is the container if it has keys looking like supersection_X
        # OR if it just has explicit supersection keys regardless of root wrapper
        supersection_container = data

    # Helper to sort keys that might be "supersection_1", "supersection_2" etc
    def sort_key(k):
        parts = k.split('_')
        if len(parts) > 1 and parts[-1].isdigit():
            return int(parts[-1])
        # If not formatted like invalid_1, maybe just return 0 or hash 
        # But we want to iterate in meaningful order if possible.
        return 0

    ss_keys = sorted(supersection_container.keys(), key=sort_key)

    for ss_key in ss_keys:
        ss_data = supersection_container[ss_key]
        if not isinstance(ss_data, dict): continue

        ss_title = ss_data.get('supersection_title', ss_key)
        
        report_lines.append(f"\nPatha/Parva: {ss_title} ({ss_key})")
        report_lines.append("-" * 50)
        total_parvas += 1
        
        sections = ss_data.get('sections', {})
        sec_keys = sorted(sections.keys(), key=sort_key)
        
        for sec_key in sec_keys:
            sec_data = sections[sec_key]
            sec_title = sec_data.get('section_title', sec_key)
            total_khandas += 1
            
            # Collect all numbers for this section (Khanda)
            khanda_numbers = []
            
            subsections = sec_data.get('subsections', {})
            sub_keys = sorted(subsections.keys(), key=sort_key)
            
            for sub_key in sub_keys:
                sub_data = subsections[sub_key]
                
                # Check for mantra content in likely fields
                mantra_sets = sub_data.get('corrected-mantra_sets', [])
                if not mantra_sets:
                     mantra_sets = sub_data.get('mantra_sets', [])
                
                # If still empty, check if sub_data itself is the mantra string (unlikely but robust)
                
                for ms in mantra_sets:
                    mantra = ""
                    if isinstance(ms, dict):
                        mantra = ms.get('corrected-mantra', ms.get('mantra_text', ''))
                    elif isinstance(ms, str):
                        mantra = ms
                    
                    if mantra:
                        nums = extract_samam_numbers(mantra)
                        if nums:
                            khanda_numbers.extend(nums)
            
            # Now validate the sequence for this Khanda
            if not khanda_numbers:
                report_lines.append(f"  {sec_title}: NO SAMAM NUMBERS FOUND")
                issues_found = True
                continue
            
            # Sort detected numbers
            khanda_numbers.sort()
            total_samas += len(khanda_numbers)
            
            # 1. Check start
            start_val = khanda_numbers[0]
            if start_val != 1:
                report_lines.append(f"  {sec_title}: Starts at {start_val} (Expected 1)")
                issues_found = True
            
            # 2. Check duplicates
            duplicates = sorted(list(set([x for x in khanda_numbers if khanda_numbers.count(x) > 1])))
            if duplicates:
                report_lines.append(f"  {sec_title}: Duplicates found: {duplicates}")
                issues_found = True
                
            # 3. Check gaps
            expected_set = set(range(1, khanda_numbers[-1] + 1))
            actual_set = set(khanda_numbers)
            missing = sorted(list(expected_set - actual_set))
            
            if missing:
                report_lines.append(f"  {sec_title}: Gaps found! Missing: {missing}")
                issues_found = True
            
            # Optional: Log Success for verbose mode?
            # if not missing and not duplicates and start_val == 1:
            #     report_lines.append(f"  {sec_title}: OK")

    if not issues_found:
        report_lines.append("\nSUCCESS: All Khandas have contiguous Samam numbering starting from 1.")
    else:
        report_lines.append("\nISSUES FOUND: Please review the list above.")

    report_lines.append("\nSUMMARY STATISTICS")
    report_lines.append("==================")
    report_lines.append(f"Total Parvas/Pathas: {total_parvas}")
    report_lines.append(f"Total Khandas: {total_khandas}")
    report_lines.append(f"Total Samams Detected: {total_samas}")

    with open(output_report, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))
        
    print(f"\nReport generated: {output_report}")
    print(f"Status: {'ISSUES FOUND' if issues_found else 'SUCCESS'}")
    print(f"Total Samams: {total_samas}")

def main():
    parser = argparse.ArgumentParser(description="Check continuity of Samam numbers in JSON file.")
    parser.add_argument("json_file", help="Path to the JSON file to check")
    parser.add_argument("--output", "-o", help="Path to the output report file", default=None)
    
    args = parser.parse_args()
    check_continuity(args.json_file, args.output)

if __name__ == "__main__":
    main()
