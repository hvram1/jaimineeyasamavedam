import json
import os
import shutil

def merge_ids(structure_source_path, content_source_path, output_path):
    print(f"Loading structure source: {structure_source_path}")
    with open(structure_source_path, 'r', encoding='utf-8') as f:
        struct_data = json.load(f)
        
    print(f"Loading content source: {content_source_path}")
    with open(content_source_path, 'r', encoding='utf-8') as f:
        content_data = json.load(f)

    # Check for metadata preservation
    if "meta" in content_data:
        print(f"Preserving metadata: v{content_data['meta'].get('version', 'Unknown')} generated at {content_data['meta'].get('generated_at', 'Unknown')}")
        
    updates_count = 0
    missing_struct_count = 0
    
    if "supersection" in content_data:
        for ss_key, ss_val in content_data["supersection"].items():
            if ss_key not in struct_data.get("supersection", {}):
                continue
            struct_ss = struct_data["supersection"][ss_key]
            
            if "sections" in ss_val:
                for sec_key, sec_val in ss_val["sections"].items():
                    if sec_key not in struct_ss.get("sections", {}):
                        continue
                    struct_sec = struct_ss["sections"][sec_key]
                    
                    if "subsections" in sec_val:
                        for sub_key, sub_val in sec_val["subsections"].items():
                            if sub_key not in struct_sec.get("subsections", {}):
                                missing_struct_count += 1
                                continue
                            struct_sub = struct_sec["subsections"][sub_key]
                            
                            # PATCH THE IDs
                            if "rik_id" in struct_sub:
                                sub_val["rik_id"] = struct_sub["rik_id"]
                            
                            if "rik_ids" in struct_sub:
                                sub_val["rik_ids"] = struct_sub["rik_ids"]
                                
                            if "rik_metadata" in struct_sub:
                                sub_val["rik_metadata"] = struct_sub["rik_metadata"]
                            
                            updates_count += 1

    print(f"Merge complete. Updated {updates_count} subsections.")
    if missing_struct_count > 0:
        print(f"Warning: {missing_struct_count} subsections were missing in structure source and were not updated.")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(content_data, f, indent=4, ensure_ascii=False)
    print(f"Saved merged file to: {output_path}")

if __name__ == "__main__":
    STRUCT_FILE = r"data/output/Agneyam-Pavamanam_latest_out.json"
    CONTENT_FILE = r"data/output/Samhita_with_Rishi_Devata_Chandas_out.json"
    OUTPUT_FILE = r"data/output/Samhita_with_Rishi_Devata_Chandas_out.json"
    
    if os.path.exists(STRUCT_FILE) and os.path.exists(CONTENT_FILE):
        # Create backup
        shutil.copy(CONTENT_FILE, CONTENT_FILE + ".bak")
        print(f"Created backup at {CONTENT_FILE}.bak")
        
        merge_ids(STRUCT_FILE, CONTENT_FILE, OUTPUT_FILE)
    else:
        print(f"Error: Files not found.\nStruct: {STRUCT_FILE}\nContent: {CONTENT_FILE}")
