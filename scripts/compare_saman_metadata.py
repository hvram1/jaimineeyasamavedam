import json
import re
import os

def normalize_metadata(text):
    if not text:
        return ""
    # Remove dandas and extra spaces
    text = text.replace('।।', '').replace('।', '')
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def parse_ksv_file(filepath):
    supersections = {}
    current_super = None
    current_section = None
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Match SuperSection markers: # आग्नेयपाठः or # अथ आरण्यकगानम्
        if line.startswith('#'):
            # Look for lines ending in पाठः or गानम्
            ss_match = re.search(r'#\s*(.*?)(पाठः|गानम्)', line)
            if ss_match:
                # Clean up: remove "अथ" and extra spaces
                prefix = ss_match.group(1).strip()
                suffix = ss_match.group(2).strip()
                title = f"{prefix} {suffix}".strip()
                title = title.replace('अथ', '').strip()
                
                # Normalize key names to match JSV JSON as much as possible
                current_super = title
                if current_super not in supersections:
                    supersections[current_super] = {}
                current_section = None
                continue
                
            # Match section markers: # खण्डः १ or # JSV - खण्डः १
            section_match = re.search(r'#.*खण्डः\s*(\d+)', line)
            if section_match:
                if current_super is None:
                    # Default to first supersection if missing
                    current_super = "आग्नेयपाठः"
                    if current_super not in supersections:
                        supersections[current_super] = {}
                current_section = int(section_match.group(1))
                supersections[current_super][current_section] = {}
                continue
            
        if current_super is None or current_section is None:
            continue
            
        # Match entries: 1-1. पर्कः।। गोतमो गायत्र्यग्निः।।
        entry_match = re.match(r'^(\d+)-(\d+)\.\s*([^।॥]+)[।॥]{1,2}\s*(.*)', line)
        if entry_match:
            rik_num = int(entry_match.group(1))
            samam_num = int(entry_match.group(2))
            arsheyam = entry_match.group(3).strip()
            metadata = entry_match.group(4).strip()
            # Remove trailing dandas
            metadata = re.sub(r'[।॥\s]+$', '', metadata)
            
            if rik_num not in supersections[current_super][current_section]:
                supersections[current_super][current_section][rik_num] = {}
            supersections[current_super][current_section][rik_num][samam_num] = {
                "arsheyam": arsheyam,
                "metadata": metadata
            }
            
    return supersections

def normalize_title(title):
    if not title: return ""
    # Remove all spaces, "अथ", "पर्व", "ः", "पाठ", "गान" for matching
    res = title.replace(' ', '').replace('अथ', '').replace('पर्व', '').replace('ः', '').replace('पाठ', '').replace('गान', '').strip()
    return res

def compare_samans(ksv_data, jsv_json_path):
    with open(jsv_json_path, 'r', encoding='utf-8') as f:
        jsv_data = json.load(f)
        
    results = []
    global_rik_count = 0
    
    # Normalize KSV keys for matching
    ksv_normalized = {normalize_title(k): v for k, v in ksv_data.items()}
    print(f"Normalized KSV Keys: {list(ksv_normalized.keys())}")
    
    for ss_id, ss_content in jsv_data.get("supersection", {}).items():
        ss_title = ss_content.get("supersection_title", "").strip()
        ss_title_norm = normalize_title(ss_title)
        
        # Try to find matching supersection in KSV
        ksv_ss = None
        for k_norm, k_val in ksv_normalized.items():
            if ss_title_norm == k_norm or ss_title_norm in k_norm or k_norm in ss_title_norm:
                ksv_ss = k_val
                break
        
        if not ksv_ss:
            # Fallback for Aaranam
            if "Aaranam" in jsv_json_path or "aranam" in jsv_json_path.lower():
                 ksv_ss = ksv_normalized.get("आरण्यकम्")
            
        if not ksv_ss:
            continue

        # Sort JSV sections to ensure order
        sorted_sections = sorted(
            [s for s in ss_content.get("sections", {}).items() if s[0] != "count"],
            key=lambda x: int(re.search(r'section_(\d+)', x[0]).group(1))
        )
        
        # Match by index OR global number for Aaranam
        for idx, (sec_id, sec_content) in enumerate(sorted_sections):
            sec_num_match = re.search(r'section_(\d+)', sec_id)
            if not sec_num_match: continue
            global_sec_num = int(sec_num_match.group(1))
            
            # If we're in Aaranam, use the global section number directly
            if normalize_title(ss_title) == "आरण्यकम्" or "Aaranam" in jsv_json_path:
                sec_num_ksv = global_sec_num
            else:
                ksv_sec_nums = sorted(ksv_ss.keys())
                if idx >= len(ksv_sec_nums):
                    continue
                sec_num_ksv = ksv_sec_nums[idx]
            
            ksv_section = ksv_ss.get(sec_num_ksv, {})
                
            rik_counters = {}
            seen_riks_in_section = set()
            last_ksv_arsheyam_val = ""
            last_ksv_meta_val = ""
            
            subsections = sec_content.get("subsections", {})
            sorted_subs = sorted(subsections.items(), key=lambda x: int(re.search(r'subsection_(\d+)', x[0]).group(1)))
            
            for sub_id, sub_content in sorted_subs:
                rik_id = sub_content.get("rik_id")
                if rik_id is None: continue
                
                # Count mantras in this subsection
                # We need to look at the corrected-mantra_sets
                full_text = ""
                for mset in sub_content.get("corrected-mantra_sets", []):
                    full_text += mset.get("corrected-mantra", "")
                
                # Markers: ॥१॥, ॥२॥ etc.
                mantra_markers = re.findall(r'॥\s*[०-९\d]+\s*॥', full_text)
                num_mantras = len(mantra_markers) if mantra_markers else 1
                
                # JSV metadata might contain '।।' internally
                jsv_meta_raw = sub_content.get("saman_metadata", "").strip()
                
                jsv_arsheyam = sub_content.get("header", {}).get("header", "").strip()
                
                rik_ids_array = sub_content.get("rik_ids", [])
                if not rik_ids_array and rik_id is not None:
                    rik_ids_array = [rik_id]
                
                for m_idx in range(num_mantras):
                    if len(rik_ids_array) == num_mantras:
                        current_rik_id = rik_ids_array[m_idx]
                    elif len(rik_ids_array) > 0:
                        current_rik_id = rik_ids_array[min(m_idx, len(rik_ids_array)-1)]
                    else:
                        current_rik_id = rik_id
                        
                    if current_rik_id is None: continue
                    
                    if current_rik_id not in rik_counters:
                        rik_counters[current_rik_id] = 0
                        
                    if current_rik_id not in seen_riks_in_section:
                        seen_riks_in_section.add(current_rik_id)
                        global_rik_count += 1
                        
                    rik_counters[current_rik_id] += 1
                    samam_num = rik_counters[current_rik_id]
                    
                    ksv_entry = ksv_section.get(current_rik_id, {}).get(samam_num)
                    
                    # We supply the full JSV metadata since it applies to the subsection
                    jsv_meta_part = jsv_meta_raw
                    
                    # Linear KSV Inheritance: if missing, inherit from the most recent processed samam
                    ksv_arsheyam_val = ksv_entry["arsheyam"] if ksv_entry else ""
                    ksv_meta_val = ksv_entry["metadata"] if ksv_entry else ""
                    
                    if not ksv_meta_val:
                        ksv_meta_val = last_ksv_meta_val
                        if not ksv_arsheyam_val:
                            ksv_arsheyam_val = last_ksv_arsheyam_val
                            
                    # Update carry-forward state
                    if ksv_meta_val:
                        last_ksv_meta_val = ksv_meta_val
                    if ksv_arsheyam_val:
                        last_ksv_arsheyam_val = ksv_arsheyam_val
                    
                    ksv_arsheyam_val = ksv_arsheyam_val if ksv_arsheyam_val else "N/A"
                    ksv_meta_val = ksv_meta_val if ksv_meta_val else "N/A"
                    
                    norm_jsv = normalize_metadata(jsv_meta_part)
                    norm_ksv = normalize_metadata(ksv_meta_val)
                    
                    is_different = norm_jsv != norm_ksv
                    # Resolve false positives where JSV concatenates metadata for multiple samams
                    if is_different and norm_ksv and norm_ksv != "NA":
                        if norm_ksv in norm_jsv and len(norm_ksv) > 3:
                            is_different = False
                    
                    results.append({
                        "Global Rik #": global_rik_count,
                        "SuperSection": ss_title,
                        "Section": sec_num_ksv,
                        "Rik-Sama": f"{current_rik_id}-{samam_num}",
                        "JSV Arsheya": jsv_arsheyam,
                        "JSV Saman Metadata": jsv_meta_part,
                        "KSV Arsheyam": ksv_arsheyam_val,
                        "KSV Saman Metadata": ksv_meta_val,
                        "Different": "YES" if is_different else "no"
                    })
                
    return results

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Compare Saman metadata between KSV and JSV.")
    parser.add_argument("--ksv", default=r'c:\Users\sekha\OneDrive\Documents\GitHub\jaimineeyasamavedam\data\input\sama_rishi_chandas_out.txt', help="Path to KSV text file")
    parser.add_argument("--jsv", default=r'c:\Users\sekha\OneDrive\Documents\GitHub\jaimineeyasamavedam\data\output\Samhita_corrected_out.json', help="Path to JSV JSON file")
    parser.add_argument("--output", default=r'c:\Users\sekha\OneDrive\Documents\GitHub\jaimineeyasamavedam\data\output\Saman_Metadata_Comparison.md', help="Path to output markdown report")
    args = parser.parse_args()
    
    ksv_path = args.ksv
    jsv_path = args.jsv
    output_path = args.output
    
    if not os.path.exists(ksv_path) or not os.path.exists(jsv_path):
        print(f"Error: Input files missing: {ksv_path} or {jsv_path}")
        return
        
    ksv_sections = parse_ksv_file(ksv_path)
    
    import sys
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
        
    comparison = compare_samans(ksv_sections, jsv_path)
    
    # Save to Markdown
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"# Saman Metadata Comparison (KSV vs JSV) - {os.path.basename(jsv_path)}\n\n")
        f.write("| Global Rik # | SuperSection | Section | Rik-Sama | JSV Arsheya | JSV Saman Metadata | KSV Arsheyam | KSV Saman Metadata | Diff |\n")
        f.write("|---|---|---|---|---|---|---|---|---|\n")
        for row in comparison:
            f.write(f"| {row['Global Rik #']} | {row['SuperSection']} | {row['Section']} | {row['Rik-Sama']} | {row['JSV Arsheya']} | {row['JSV Saman Metadata']} | {row['KSV Arsheyam']} | {row['KSV Saman Metadata']} | {row['Different']} |\n")
    
    print(f"Comparison report saved to: {output_path}")

    # Save to Excel
    try:
        import pandas as pd
        excel_path = output_path.replace('.md', '.xlsx')
        df = pd.DataFrame(comparison)
        # Reorder columns for Excel
        cols = ["Global Rik #", "SuperSection", "Section", "Rik-Sama", "JSV Arsheya", "JSV Saman Metadata", "KSV Arsheyam", "KSV Saman Metadata", "Different"]
        df = df[cols]
        df.to_excel(excel_path, index=False)
        print(f"Excel report saved to: {excel_path}")
    except ImportError:
        print("[WARNING] 'pandas' not found. Skipping Excel export.")
    except Exception as e:
        print(f"[ERROR] Failed to export to Excel: {e}")

if __name__ == "__main__":
    main()
