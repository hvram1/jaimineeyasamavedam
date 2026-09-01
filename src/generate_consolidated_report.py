import os
import re

# File paths
STRUCTURE_SUMMARY_FILE = r'data\output\JSV_Structure_Summary.txt'
RECONCILIATION_REPORT_FILE = r'data\output\JSV_Samhita_Reconciliation_Report.md'
OUTPUT_FILE = r'data\output\JSV_Consolidated_Report.md'

def parse_structure_summary(file_path):
    """Parses the structure summary text file to extract detailed counts."""
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return []

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    patha_sections = []
    current_patha = None
    current_khandas = []
    
    for line in lines:
        line = line.strip()
        
        # Identify Patha Start: "PATHA 1: आग्नेयपाठः"
        patha_match = re.match(r'^PATHA \d+: (.*)', line)
        if patha_match:
            # If we were already processing a patha, save it (though usually followed by TOTAL line logic)
            # But the structure is Patha Header -> Khandas -> Patha Total. 
            # We'll save when we hit a new "PATHA" or EOF, but "TOTAL" line is better trigger to close.
            if current_patha:
                # This case shouldn't generally happen if TOTAL line logic works, but for safety
                pass 
            
            fullname = line # "PATHA 1: आग्नेयपाठः"
            current_patha = {
                'name': fullname,
                'khandas': [],
                'total_sc': 0
            }
            continue

        # Identify Khanda: "Khanda 1: प्रथम खण्डः                    =   19 Samas"
        if "Khanda" in line and "=" in line and "Samas" in line:
            # Flexible regex for spaces
            k_match = re.search(r'Khanda \d+:\s+(.*?)\s+=\s+(\d+)\s+Samas', line)
            if k_match and current_patha:
                k_name = k_match.group(1).strip()
                k_count = k_match.group(2).strip()
                current_patha['khandas'].append((k_name, k_count))
                continue

        # Identify Total: "PATHA 1 TOTAL: 182 Samas (12 Khandas)"
        if "TOTAL:" in line and "Samas" in line:
            if current_patha:
                total_match = re.search(r'TOTAL:\s+(\d+)\s+Samas', line)
                if total_match:
                    current_patha['total_sc'] = total_match.group(1)
                
                patha_sections.append(current_patha)
                current_patha = None
                
    return patha_sections

def read_reconciliation_report(file_path):
    """Reads the reconciliation report."""
    if not os.path.exists(file_path):
         return None
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def generate_consolidated_report():
    print(f"Generating consolidated report...")
    
    # 1. Read Reconciliation Report
    recon_content = read_reconciliation_report(RECONCILIATION_REPORT_FILE)
    if not recon_content:
        print("Reconciliation report missing.")
        return

    # 2. Parse Detailed Structure
    structure_data = parse_structure_summary(STRUCTURE_SUMMARY_FILE)
    
    # 3. Build Report
    output_lines = []
    
    # Split Recon Report at "## Section 2" to insert details
    if "## Section 2" in recon_content:
        parts = recon_content.split("## Section 2")
        intro_part = parts[0]
        # Reinject the header "## Section 2" for the second part
        rest_part = "## Section 2" + parts[1]
    else:
        # Fallback if structure changed
        intro_part = recon_content
        rest_part = ""

    # Add Intro
    output_lines.append(intro_part.rstrip())
    output_lines.append("\n\n")
    
    # Add Detailed Structure Section
    output_lines.append("## Detailed Structure Breakdown\n")
    output_lines.append(f"Derived from `{os.path.basename(STRUCTURE_SUMMARY_FILE)}`.\n")
    
    for patha_info in structure_data:
        # Header: formatted clearly
        p_name = patha_info['name'] 
        output_lines.append(f"\n### {p_name}\n\n")
        
        # Table
        output_lines.append("| Khanda | Samas |\n")
        output_lines.append("| :--- | :--- |\n")
        
        for k_name, k_count in patha_info['khandas']:
            output_lines.append(f"| {k_name} | {k_count} |\n")
            
        # Total Row
        output_lines.append(f"| **TOTAL** | **{patha_info['total_sc']}** |\n")
        output_lines.append("\n")
        
    output_lines.append("---\n\n")
    
    # Add Rest of Report
    output_lines.append(rest_part.lstrip())
    
    # Write File
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("".join(output_lines))
        
    print(f"Successfully generated: {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_consolidated_report()
