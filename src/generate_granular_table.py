"""
Generate a fine granular table listing every individual Samam.
Uses the shared samam_utils module for consistent counting.
Output is UTF-8 with BOM for Excel compatibility.
Updated Schema (v3.0) with Global Rik Counting.
"""
import json
import csv
import os
import re
import sys
import argparse
try:
    from samam_utils import SAMAM_PATTERN
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(__file__), 'tools'))
    from samam_utils import SAMAM_PATTERN
from utils import get_generated_metadata

# --- CLI Arguments ---
parser = argparse.ArgumentParser(description='Generate a fine granular table listing every individual Samam.')
parser.add_argument('-i', '--input', dest='input_file',
                    default=r'data\output\Samhita_with_Rishi_Devata_Chandas_out.json',
                    help='Path to the input JSON file (default: data\\output\\Samhita_with_Rishi_Devata_Chandas_out.json)')
parser.add_argument('-o', '--output', dest='output_csv',
                    default=r'data\output\JSV_Samam_Granular_Table.csv',
                    help='Path to the output CSV file (default: data\\output\\JSV_Samam_Granular_Table.csv)')
args = parser.parse_args()

INPUT_FILE = args.input_file
OUTPUT_CSV = args.output_csv

# --- Helper Functions ---

def normalize_key(text):
    """Normalize metadata keys to merge duplicates (spaces, punctuation)"""
    if not text:
        return ""
    # Aggressive normalization
    text = text.strip(' \t\n\r.|॥,:;()\'"ः')
    # Collapse multiple spaces
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def parse_compound_token(token):
    """
    Check if a token is a known compound (Samasa).
    Returns (Rishi, Devata, Chandas) tuple. None if not a known compound.
    """
    # Normalize for checking
    t = token.replace('ः', '').replace(':', '').strip()
    
    # Rule: Ends in 'अग्नि' (agni)
    if t.endswith('अग्नि') or t.endswith('ग्नि'):
        devata = 'अग्निः'
        chandas = ''
        
        # Check prefix
        if 'गायत्र्या' in t or 'गायत्र्य' in t:
             chandas = 'गायत्री'
        if 'विराड्' in t:
             chandas = 'विराड्गायत्री' # Override or append? Usually it handles 'विराड्गात्र्यग्नि'
        
        # If we found at least Chandas, return
        if chandas:
            return ('', devata, chandas)
            
    return None

def parse_metadata_str(metadata_str):
    """Parse metadata string into Rishi, Devata, Chandas (Smart Parsing)"""
    result = {'rishi': '', 'devata': '', 'chandas': ''}
    if not metadata_str:
        return result
    
    cleaned = re.sub(r'^[।॥\s]+|[।॥\s]+$', '', metadata_str)
    parts = re.split(r'\s*।।\s*|\s+', cleaned)
    parts = [p.strip() for p in parts if p.strip()]
    
    # Process parts
    # If we find a compound in parts, we assign it. 
    # Remaining parts are likely Rishi (if they appear before).
    
    compounds_found = []
    other_parts = []
    
    for p in parts:
        compound = parse_compound_token(p)
        if compound:
            compounds_found.append(compound)
        else:
            other_parts.append(p)
            
    # If we found compounds, use them to populate Devata/Chandas
    # And use the other parts for Rishi
    if compounds_found:
        # Take the last compound found if multiple (unlikely)
        _, d, c = compounds_found[-1]
        result['devata'] = d
        result['chandas'] = c
        
        # Join remaining as Rishi
        result['rishi'] = ' '.join(other_parts)
    else:
        # Fallback to positional logic
        if len(parts) >= 3:
            result['rishi'] = parts[0]
            result['devata'] = parts[1]
            result['chandas'] = parts[2]
        elif len(parts) == 2:
            result['rishi'] = parts[0]
            result['devata'] = parts[1]
        elif len(parts) == 1:
            result['rishi'] = parts[0]
            
    return result


# Get metadata
metadata = get_generated_metadata()
JSV_VERSION = metadata['version']
GENERATED_AT = metadata['generated_at']

print(f"Generating Granular Table (v{JSV_VERSION})...")

# Load the JSON
with open(INPUT_FILE, 'r', encoding='utf-8') as f:
    data = json.load(f)

# CSV rows
rows = []

# Get the supersection container
supersection_container = data.get('supersection', {})

# Sort supersection keys numerically
ss_keys = sorted(supersection_container.keys(), key=lambda x: int(x.split('_')[1]) if '_' in x else 0)

global_samam_num = 0
global_rik_counter = 0

# Track previous Rik ID to detect changes for Global Rik Num increment
prev_rik_id_global_context = None

for ss_key in ss_keys:
    ss_data = supersection_container[ss_key]
    ss_title = ss_data.get('supersection_title', ss_key)
    patha_num = int(ss_key.split('_')[1]) if '_' in ss_key else 0
    
    # Get sections
    sections = ss_data.get('sections', {})
    sec_keys = sorted(sections.keys(), key=lambda x: int(x.split('_')[1]) if '_' in x else 0)
    
    for sec_key in sec_keys:
        sec_data = sections[sec_key]
        sec_title = sec_data.get('section_title', sec_key)
        
        # Get subsections (Arsheyams)
        subsections = sec_data.get('subsections', {})
        sub_keys = sorted(subsections.keys(), key=lambda x: int(x.split('_')[1]) if '_' in x else 0)
        
        for sub_key in sub_keys:
            sub_data = subsections[sub_key]
            
            # Get Arsheyam header
            header_data = sub_data.get('header', {})
            arsheyam_name = header_data.get('header', '')
            arsheyam_num = header_data.get('header_number', 0)
            
            # Get Rik info
            try:
                rik_id = int(sub_data.get('rik_id', 0))
            except ValueError:
                rik_id = 0
                
            rik_metadata = sub_data.get('rik_metadata', '')
            
            # Get Saman metadata
            saman_metadata = sub_data.get('saman_metadata', '')


            # Parse Metadata
            rik_parts = parse_metadata_str(rik_metadata)
            saman_parts = parse_metadata_str(saman_metadata)
            
            # Normalize (SKIPPED as per user request to focus on full metadata)
            # rik_rishi = normalize_key(rik_parts['rishi'])
            # ...
            
            # Logic for Global Rik Num:
            # We assume sequential processing. 
            # If rik_id changes (or matches previous but in different section context etc), we increment.
            # But wait, within a merged set, rik_id is same (e.g. 1).
            # If we move from Rik 1 to Rik 2, it increments.
            # If we move from Rik 1 (Samam 1) to Rik 1 (Samam 2), it stays same.
            # However, rik_id resets per SECTION/FILE usually? 
            # No, 'rik_id' in JSON is simply 'subsection_id' of the parent UNLESS merged.
            # "Global_Rik_Num" implies unique count of Riks.
            # If we simply count UNIQUE (Patha + Rik_ID) combinations?
            # Or just detect edge trigger.
            
            # Edge trigger logic:
            # Note: rik_id might not be globally unique (resets per section? No, per file? Yes).
            # So "prev_rik_id" comparison needs to know if we crossed a boundary.
            # But we process strictly sequentially.
            # If rik_id != prev_rik_id, it's a new Rik.
            # Except if rik_id resets to 1 in new section.
            
            # To be safe: use (ss_key, sec_key, rik_id) as unique identifier key.
            # If this key changes, increment Global Rik Count.
            current_rik_key = (ss_key, sec_key, rik_id)
            if current_rik_key != prev_rik_id_global_context:
                global_rik_counter += 1
                prev_rik_id_global_context = current_rik_key
            
            # Get corrected mantra and extract Samam numbers
            mantra_sets = sub_data.get('corrected-mantra_sets', [])
            
            # We need to output ONE row per SAMAM.
            # If there are multiple Samams in this subsection, they share the Rik Num.
            
            samam_found = False
            for ms in mantra_sets:
                mantra = ms.get('corrected-mantra', '')
                
                # Find all Samam numbers in this mantra
                samam_matches = SAMAM_PATTERN.findall(mantra)
                
                if samam_matches:
                    samam_found = True
                    # Extract the number from each match (e.g., "॥1॥" -> "1")
                    for match in samam_matches:
                        # Extract just the number
                        num_match = re.search(r'[\d०-९]+', match)
                        if num_match:
                            samam_num_str = num_match.group()
                            # Convert Devanagari to Arabic
                            dev_map = {'०': '0', '१': '1', '२': '2', '३': '3', '४': '4',
                                      '५': '5', '६': '6', '७': '7', '८': '8', '९': '9'}
                            samam_num_arabic = ''.join(dev_map.get(c, c) for c in samam_num_str)
                            samam_num = int(samam_num_arabic)
                            
                            global_samam_num += 1
                            
                            rows.append({
                                'Global_Samam_Num': global_samam_num,
                                'Global_Rik_Num': global_rik_counter,
                                'Patha_Name': ss_title,
                                'Khanda': sec_title,
                                'Rik_ID': rik_id,
                                'Rik_Text': sub_data.get('rik_text', ''),
                                'Rik_Metadata': rik_metadata,
                                'Arsheyam_Num': arsheyam_num,
                                'Patha_Num': patha_num,
                                'Samam_Num': samam_num,
                                'Arsheyam_Name': arsheyam_name,
                                'Saman_Metadata': saman_metadata
                            })
            
            if not samam_found:
                 # Fallback for no markers
                 global_samam_num += 1
                 rows.append({

                    'Global_Samam_Num': global_samam_num,
                    'Global_Rik_Num': global_rik_counter,
                    'Patha_Name': ss_title,
                    'Khanda': sec_title,
                    'Rik_ID': rik_id,
                    'Rik_Text': sub_data.get('rik_text', ''),
                    'Rik_Metadata': rik_metadata,
                    'Arsheyam_Num': arsheyam_num,
                    'Patha_Num': patha_num,
                    'Samam_Num': arsheyam_num, # Fallback
                    'Arsheyam_Name': arsheyam_name,
                    'Saman_Metadata': saman_metadata
                })


# Write CSV with UTF-8 BOM for Excel compatibility
with open(OUTPUT_CSV, 'w', encoding='utf-8-sig', newline='') as f:
    # Line 1: <Filename> <Version> <Timestamp>
    filename = os.path.basename(OUTPUT_CSV)
    f.write(f"{filename} {JSV_VERSION} {GENERATED_AT}\n")

    fieldnames = [
        'Global_Rik_Num', 'Patha_Name', 'Khanda', 'Rik_ID', 'Rik_Text', 'Rik_Metadata',
        'Global_Samam_Num', 'Arsheyam_Num', 'Patha_Num', 'Samam_Num', 'Arsheyam_Name', 
        'Saman_Metadata'
    ]
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"CSV saved to: {OUTPUT_CSV}")

# --- Generate Excel (.xlsx) ---
OUTPUT_XLSX = OUTPUT_CSV.replace('.csv', '.xlsx')
try:
    import openpyxl
    print(f"Generating Excel file: {OUTPUT_XLSX}...")
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Samam Granular Table"
    
    # Write Metadata in first row? 
    # Usually Excel tables prefer headers in row 1.
    # Let's put metadata in a separate sheet or just above? 
    # Users often want a clean table for filtering.
    # Let's put the Table in Row 1. Metadata in the file properties or specific sheet?
    # Let's stick to just the table for usability.
    
    # Write Metadata in first row
    filename = os.path.basename(OUTPUT_XLSX)
    metadata_text = f"{filename} {JSV_VERSION} {GENERATED_AT}"
    ws.append([metadata_text])
    
    # Merge first row to look like a title
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=len(fieldnames))
    
    # Style the metadata row (optional but nice)
    from openpyxl.styles import Font, Alignment
    cell = ws.cell(row=1, column=1)
    cell.font = Font(bold=True, size=12)
    cell.alignment = Alignment(horizontal="left")

    # Write Header (Now in Row 2)
    ws.append(fieldnames)
    
    # Write Rows
    for r in rows:
        row_values = [r.get(key, '') for key in fieldnames]
        ws.append(row_values)
        
    wb.save(OUTPUT_XLSX)
    print(f"Excel file saved to: {OUTPUT_XLSX}")
    
except ImportError:
    print("Warning: 'openpyxl' library not found. Skipping Excel generation.")
except PermissionError:
    print(f"ERROR: Could not save '{OUTPUT_XLSX}'. It is likely open in Excel.")
    print("Please close the file and run the script again.")
except Exception as e:
    print(f"Error generating Excel file: {e}")

print(f"Total Samam entries: {len(rows)}")
print(f"Total Unique Riks Detected: {global_rik_counter}")

# Summary by Patha
print("\n=== Summary by Patha ===")
from collections import Counter
patha_counts = Counter(r['Patha_Name'] for r in rows)
for patha, count in patha_counts.items():
    print(f"  {patha}: {count}")

