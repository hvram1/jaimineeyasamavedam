"""
Extract structural data from Samhita text file and generate a CSV table.
Format: SuperSection, Section, Samam Number, Subsection Header
"""
import re
import csv
import sys

def extract_structure(input_file, output_file):
    """Extract structural information and output as CSV."""
    
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    
    # Current state
    current_supersection = ""
    current_section = ""
    current_subsection_header = ""
    current_subsection_id = 0
    
    # Results list
    results = []
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Check for SuperSection
        if line.startswith('# Start of SuperSection Title'):
            i += 1
            if i < len(lines):
                current_supersection = lines[i].strip()
            i += 1
            continue
        
        # Check for Section
        if line.startswith('# Start of Section Title'):
            i += 1
            if i < len(lines):
                current_section = lines[i].strip()
            i += 1
            continue
        
        # Check for SubSection Title
        if line.startswith('# Start of SubSection Title'):
            match = re.search(r'subsection_(\d+)', line)
            if match:
                current_subsection_id = int(match.group(1))
            i += 1
            if i < len(lines):
                current_subsection_header = lines[i].strip()
            i += 1
            continue
        
        # Check for Mantra Sets - extract Samam numbers
        if line.startswith('#Start of Mantra Sets'):
            # Get the subsection ID from the delimiter
            match = re.search(r'subsection_(\d+)', line)
            subsection_id = match.group(1) if match else str(current_subsection_id)
            
            # Read mantra content to find Samam numbers
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('#End of Mantra Sets'):
                mantra_line = lines[i].strip()
                # Find all Samam numbers (॥ N ॥ pattern)
                samam_numbers = re.findall(r'॥\s*(\d+)\s*॥', mantra_line)
                
                for samam_num in samam_numbers:
                    results.append({
                        'supersection': current_supersection,
                        'section': current_section,
                        'samam': samam_num,
                        'subsection_id': subsection_id,
                        'subsection_header': current_subsection_header
                    })
                i += 1
            continue
        
        i += 1
    
    # Remove duplicates (same Samam may appear multiple times in content)
    seen = set()
    unique_results = []
    for r in results:
        key = (r['supersection'], r['section'], r['samam'], r['subsection_id'])
        if key not in seen:
            seen.add(key)
            unique_results.append(r)
    
    # Write to CSV
    with open(output_file, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['SuperSection', 'Section', 'Samam', 'Subsection ID', 'Subsection Header'])
        for r in unique_results:
            writer.writerow([
                r['supersection'],
                r['section'],
                r['samam'],
                r['subsection_id'],
                r['subsection_header']
            ])
    
    print(f"Extracted {len(unique_results)} entries to {output_file}")
    return unique_results

if __name__ == '__main__':
    input_file = r'data\input\Samhita_with_Rishi_Devata_Chandas.txt'
    output_file = r'data\output\JSV_Samhita_Structure_Table.csv'
    
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    
    extract_structure(input_file, output_file)
