import re
import sys
from pathlib import Path

try:
    from docx import Document
except ImportError:
    print("Error: 'python-docx' library missing. Run: pip install python-docx")
    sys.exit(1)

def extract_metadata_hard_clean(docx_path, output_path):
    if not docx_path.exists():
        print(f"File not found: {docx_path}")
        return

    print(f"Processing: {docx_path.name}")
    try:
        doc = Document(docx_path)
    except Exception as e:
        print(f"Error reading DOCX: {e}")
        return

    # Combine text
    full_text = "\n".join([p.text.strip() for p in doc.paragraphs if p.text.strip()])

    found_entries = []

    # --- 1. FIND BLOCKS ---
    # Start: Range Pattern e.g. "(1-10)" or "(1 – 8)"
    start_pattern = re.compile(r'(\(\s*[\d०-९]+\s*[-–—]\s*[\d०-९]+\s*\))')

    # Stop: Mantra Numbering (e.g. 1.1.1)
    # We look for this to define the "End of search area"
    stop_pattern = re.compile(r'(\s+[\d०-९]+\.[\d०-९]+\.[\d०-९]+)')

    # Danda Pattern for final trim
    danda_regex = re.compile(r'(॥|।।|\|\|)')

    search_pos = 0
    
    while search_pos < len(full_text):
        # A. Find Start
        match = start_pattern.search(full_text, search_pos)
        if not match:
            break 

        start_index = match.start()
        
        # B. Find Stop (Mantra Number)
        stop_match = stop_pattern.search(full_text, start_index)
        
        if stop_match:
            end_index = stop_match.start()
            raw_chunk = full_text[start_index:end_index]
            search_pos = stop_match.end()
        else:
            raw_chunk = full_text[start_index:]
            search_pos = len(full_text)

        # --- 2. HARD CLEANUP (The Fix) ---
        
        # A. Force split at Swastika
        # We check for both common Unicode variations just in case
        if '卐' in raw_chunk:
            raw_chunk = raw_chunk.split('卐')[0]
        if '卍' in raw_chunk:
            raw_chunk = raw_chunk.split('卍')[0]

        # B. Flatten newlines
        clean_chunk = re.sub(r'\s+', ' ', raw_chunk).strip()

        # C. Trim to Last Danda (Preserve the Danda)
        # This removes any trailing garbage spaces or letters left after the split
        danda_matches = list(danda_regex.finditer(clean_chunk))
        if danda_matches:
            last_danda = danda_matches[-1]
            cut_point = last_danda.end()
            clean_chunk = clean_chunk[:cut_point]

        if clean_chunk:
            found_entries.append(clean_chunk)

    # Save Results
    if found_entries:
        with open(output_path, "w", encoding="utf-8") as f:
            for entry in found_entries:
                f.write(entry + "\n")
        print(f"\nSUCCESS! Extracted {len(found_entries)} clean metadata blocks.")
        print(f"Saved to: {output_path}")
        
        # Debug preview
        if len(found_entries) > 0:
            print(f"\n--- Entry 1 Preview (Length: {len(found_entries[0])}) ---")
            print(found_entries[0][:100] + "...")
            print("--- End of Entry 1 ---")
    else:
        print("\nNo metadata found.")

if __name__ == "__main__":
    script_dir = Path(__file__).parent
    
    # Update filename
    input_file = script_dir / "rik-rishi.docx" 
    output_file = script_dir / "Extracted-metadata.txt"
    
    extract_metadata_hard_clean(input_file, output_file)   
   
    
    