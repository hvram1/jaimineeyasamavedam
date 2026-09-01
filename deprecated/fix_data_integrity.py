import csv
import re
import shutil

TEXT_FILE = r'data\input\Samhita_with_Rishi_Devata_Chandas.txt'
CSV_FILE = r'data\output\JSV_Samam_Granular_Table.csv'

def fix_data():
    print("Starting Data Integrity Fix...")
    
    # 1. FIX TEXT
    print("Fixing Text File...")
    with open(TEXT_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    new_lines = []
    fixed_text_count = 0
    
    # Pattern for duplicate 17 in Agneya
    # Location: Line ~493. Content: "शन्नोदेवी:(ती) ।आभीष्टा(टि) या(ख) इशन्नोभुवा(शु) म..."
    # It contains 17 (duplicate) and 18.
    
    for line in lines:
        # Check for the specific problematic line in Agneya Patha
        if "शन्नोदेवी" in line and "॥१७॥" in line and "॥१८॥" in line:
            print(f"  Found problematic line: {line.strip()[:50]}...")
            # Remove the first marker (17)
            # Regex to remove "॥१७॥" and optional whitespace
            fixed_line = re.sub(r'॥\s*१७\s*॥\s*', '', line, count=1)
            new_lines.append(fixed_line)
            print(f"  Fixed to: {fixed_line.strip()[:50]}...")
            fixed_text_count += 1
        else:
            new_lines.append(line)
            
    if fixed_text_count == 0:
        print("wWARNING: Could not find Text issue (duplicate 17). Check if already fixed.")
    else:
        # Backup and Save
        shutil.copy(TEXT_FILE, TEXT_FILE + ".bak_fix")
        with open(TEXT_FILE, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        print("  Text file saved.")

    # 2. FIX CSV
    print("Fixing CSV File...")
    rows = []
    with open(CSV_FILE, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for row in reader:
            rows.append(row)
            
    new_rows = []
    global_counter = 0
    
    # Targets:
    # Agneya 3, Samam 18 (Duplicate) -> Row ~54.
    # Brihati 4, Samam 6 (Duplicate) -> Row ~471.
    
    deleted_count = 0
    fixed_brihati_count = 0
    
    seen_agneya_18 = 0
    
    for row in rows:
        # Agneya Fix
        if row['Patha_Num'] == '1' and 'तृतीय' in row['Khanda'] and row['Samam_Num'] == '18':
            seen_agneya_18 += 1
            if seen_agneya_18 == 2:
                print(f"  Deleting Duplicate CSV Row: {row['Global_Samam_Num']} (Agneya 18)")
                deleted_count += 1
                continue # SKIP THIS ROW
        
        # Brihati Fix
        if row['Patha_Num'] == '3' and 'चतुर्थ' in row['Khanda'] and row['Samam_Num'] == '6':
            # Check if this is the SECOND 6 (which is actually 7)
            # How to distinguish? Global IDs are sequential.
            # Row 470 is 6. Row 471 is 6.
            # We want to change the second one to 7.
            # Or reliance on order.
            pass 
            # I will handle this logic inside the append loop
            
        # Add to new list (with modifications)
        
        # Special handling for Brihati 6 -> 7
        # We need to detect which one it is.
        # Logic: If we see a 6, check if next one is 6? No, streaming.
        # We can use the original Global ID to capture the specific row.
        # Row 471 (Global 470) was the one to change.
        
        if row['Global_Samam_Num'] == '470': # Based on inspection
             print(f"  Fixing Brihati Row {row['Global_Samam_Num']}: Samam 6 -> 7")
             row['Samam_Num'] = '7'
             fixed_brihati_count += 1
             
        # Add row
        new_rows.append(row)

    # Re-index Global IDs
    print("  Re-indexing Global IDs...")
    final_rows = []
    for i, row in enumerate(new_rows):
        row['Global_Samam_Num'] = str(i + 1)
        final_rows.append(row)
        
    # Validation
    if deleted_count != 1:
        print(f"WARNING: Deleted {deleted_count} rows. Expected 1.")
    if fixed_brihati_count != 1:
        print(f"WARNING: Fixed {fixed_brihati_count} Brihati rows. Expected 1.")
        
    # Save CSV
    shutil.copy(CSV_FILE, CSV_FILE + ".bak_fix")
    with open(CSV_FILE, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(final_rows)
    print("  CSV file saved.")
    print("Done.")

if __name__ == "__main__":
    fix_data()
