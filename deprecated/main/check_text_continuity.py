import re
from collections import defaultdict

filename = r'data\input\Samhita_with_Rishi_Devata_Chandas.txt'
SAMAM_PATTERN = re.compile(r'(?:॥|\|\|)\s*([\d०-९]+)\s*(?:॥|\|\|)')

def get_arabic(num_str):
    dev_map = {'०': '0', '१': '1', '२': '2', '३': '3', '४': '4',
               '५': '5', '६': '6', '७': '7', '८': '8', '९': '9'}
    arabic = ''.join(dev_map.get(c, c) for c in num_str)
    return int(arabic)

def check_text_file():
    print(f"Reading {filename}...")
    
    current_patha = "Unknown Patha"
    current_khanda = "Unknown Khanda"
    
    # Store data: data[patha][khanda] = [list of numbers]
    data = defaultdict(lambda: defaultdict(list))
    
    in_mantra_block = False
    
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    for i, line in enumerate(lines):
        line = line.strip()
        
        # SuperSection Detection
        if line.startswith("# Start of SuperSection Title"):
            # Next line usually has the title
            if i + 1 < len(lines):
                current_patha = lines[i+1].strip()
                continue
                
        # Section Detection
        if line.startswith("# Start of Section Title"):
            if i + 1 < len(lines):
                current_khanda = lines[i+1].strip()
                continue
        
        # Mantra Block Detection
        if line.startswith("#Start of Mantra Sets"):
            in_mantra_block = True
            continue
        if line.startswith("#End of Mantra Sets"):
            in_mantra_block = False
            continue
            
        if in_mantra_block:
            matches = SAMAM_PATTERN.findall(line)
            for m in matches:
                try:
                    num = get_arabic(m)
                    data[current_patha][current_khanda].append(num)
                except ValueError:
                    pass

    # Analyze
    # Get Metadata
    from utils import get_generated_metadata
    meta = get_generated_metadata()
    
    report_lines = [f"JAIMINEEYA SAMAVEDA SAMHITA - TEXT INPUT CONTINUITY CHECK (v{meta['version']})"]
    report_lines.append(f"Generated: {meta['generated_at']}")
    report_lines.append("=======================================================")
    
    issues_found = False
    
    # Sort Pathas vaguely if possible (manual list or sorted keys)
    patha_order = ['आग्नेयपाठः', 'तद्वपाठः', 'बृहतिपाठः', 'असाविपाठः', 'ऐन्द्रपाठः', 'पवमानपाठः']
    # Add any others found
    for p in data.keys():
        if p not in patha_order:
            patha_order.append(p)
            
    for patha in patha_order:
        if patha not in data: continue
        
        report_lines.append(f"\nPatha: {patha}")
        report_lines.append("-" * 40)
        
        khandas = data[patha]
        # Sort Khandas vaguely (Assuming numeric names like 'प्रथम खण्डः', etc is hard to sort without map, but keys are insertion ordered usually)
        # Let's just use regular sort
        
        khanda_names = sorted(khandas.keys())
        
        for khanda in khanda_names:
            nums = khandas[khanda]
            
            if not nums:
                report_lines.append(f"  {khanda}: No Samam numbers found")
                issues_found = True
                continue
                
            nums.sort()
            
            # Checks
            msgs = []
            
            # 1. Start check
            if nums[0] != 1:
                msgs.append(f"Starts at {nums[0]} (Expected 1)")
            
            # 2. Duplicate check
            duplicates = sorted(list(set([x for x in nums if nums.count(x) > 1])))
            if duplicates:
                msgs.append(f"Duplicates: {duplicates}")
                
            # 3. Gap check
            expected = set(range(1, nums[-1] + 1))
            actual = set(nums)
            missing = sorted(list(expected - actual))
            if missing:
                msgs.append(f"Missing: {missing}")
                
            if msgs:
                issues_found = True
                report_lines.append(f"  {khanda}: " + "; ".join(msgs))
            else:
                # report_lines.append(f"  {khanda}: OK (1-{nums[-1]})")
                pass

    if not issues_found:
        report_lines.append("\nSUCCESS: No numbering issues found in text input.")
    else:
        report_lines.append("\nISSUES FOUND: Please review the list above.")
        
    output_file = r'data\output\Text_Samam_Continuity_Report.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))
    print(f"Report written to {output_file}")

if __name__ == "__main__":
    check_text_file()
