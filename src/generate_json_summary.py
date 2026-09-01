"""
Generate a granular table summarizing Sama counts from the JSON output.
This ensures counts match between website and PDF generation since both use the same JSON.
Uses the shared samam_utils module for consistent counting.
"""
import json
import csv
from collections import OrderedDict
from samam_utils import count_samams_with_fallback
from utils import get_generated_metadata

INPUT_FILE = r'data\output\Samhita_with_Rishi_Devata_Chandas_out.json'
OUTPUT_CSV = r'data\output\JSV_Structure_Summary.csv'
OUTPUT_TXT = r'data\output\JSV_Structure_Summary.txt'

# Get metadata
metadata = get_generated_metadata()
JSV_VERSION = metadata['version']
GENERATED_AT = metadata['generated_at']

# Load the JSON
with open(INPUT_FILE, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Structure: data['supersection']['supersection_X']['sections']['section_Y']['subsections']
structure = OrderedDict()  # {supersection_title: {section_title: count}}

# Get the supersection container
supersection_container = data.get('supersection', {})

# Sort supersection keys numerically
ss_keys = sorted(supersection_container.keys(), key=lambda x: int(x.split('_')[1]) if '_' in x else 0)

for ss_key in ss_keys:
    ss_data = supersection_container[ss_key]
    ss_title = ss_data.get('supersection_title', ss_key)
    
    if ss_title not in structure:
        structure[ss_title] = OrderedDict()
    
    # Get sections
    sections = ss_data.get('sections', {})
    sec_keys = sorted(sections.keys(), key=lambda x: int(x.split('_')[1]) if '_' in x else 0)
    
    for sec_key in sec_keys:
        sec_data = sections[sec_key]
        sec_title = sec_data.get('section_title', sec_key)
        
        # Count Samam markers from corrected-mantra text
        subsections = sec_data.get('subsections', {})
        section_sama_count = 0
        for sub_key in subsections:
            sub_data = subsections[sub_key]
            mantra_sets = sub_data.get('corrected-mantra_sets', [])
            for ms in mantra_sets:
                mantra = ms.get('corrected-mantra', '')
                section_sama_count += count_samams_with_fallback(mantra)
        
        structure[ss_title][sec_title] = section_sama_count

# Write to CSV and TXT
with open(OUTPUT_CSV, 'w', encoding='utf-8-sig', newline='') as csv_file, \
     open(OUTPUT_TXT, 'w', encoding='utf-8') as txt_file:
    
    writer = csv.writer(csv_file)
    writer.writerow(['Patha (SuperSection)', 'Khanda (Section)', 'Samas (Subsections)'])
    
    txt_file.write("=" * 80 + "\n")
    txt_file.write(f"JAIMINEEYA SAMAVEDA SAMHITA - STRUCTURE SUMMARY (v{JSV_VERSION})\n")
    txt_file.write(f"Generated: {GENERATED_AT}\n")
    txt_file.write("=" * 80 + "\n\n")
    txt_file.write("Counts from JSON output (used by both website and PDF generation)\n\n")
    
    grand_total = 0
    patha_num = 0
    total_khandas = 0
    
    for ss_title, sections in structure.items():
        patha_num += 1
        patha_total = 0
        khanda_num = 0
        
        txt_file.write("-" * 80 + "\n")
        txt_file.write(f"PATHA {patha_num}: {ss_title}\n")
        txt_file.write("-" * 80 + "\n")
        
        for sec_title, count in sections.items():
            khanda_num += 1
            total_khandas += 1
            patha_total += count
            
            writer.writerow([ss_title, sec_title, count])
            txt_file.write(f"  Khanda {khanda_num}: {sec_title:30} = {count:4} Samas\n")
        
        grand_total += patha_total
        txt_file.write(f"\n  PATHA {patha_num} TOTAL: {patha_total} Samas ({khanda_num} Khandas)\n\n")
    
    txt_file.write("=" * 80 + "\n")
    txt_file.write(f"GRAND TOTAL: {grand_total} Samas\n")
    txt_file.write(f"Total Pathas: {patha_num}\n")
    txt_file.write(f"Total Khandas: {total_khandas}\n")
    txt_file.write("=" * 80 + "\n")

print(f"CSV saved to: {OUTPUT_CSV}")
print(f"TXT saved to: {OUTPUT_TXT}")
print(f"\n=== SUMMARY ===")
print(f"Total Pathas: {patha_num}")
print(f"Total Khandas: {total_khandas}")
print(f"Total Samas: {grand_total}")

