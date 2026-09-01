import re
from docx import Document

def extract_rishi_chandas_docx(docx_path, output_path):
    print(f"Reading {docx_path}...")
    
    try:
        # Load the Word document
        doc = Document(docx_path)
        
        # 1. Extract all text from paragraphs and join them
        # We use a newline separator to preserve structure
        full_text = []
        for para in doc.paragraphs:
            full_text.append(para.text)
        
        # Join into one massive string for regex processing
        content = "\n".join(full_text)

        # 2. Define the Regex Pattern
        # (\d+-\d+\.)  -> Starts with Number-Number. (e.g., 2-1.)
        # .*?          -> Lazy match of everything in between
        # (?=卐)       -> Lookahead: Stops right before the Swastika
        pattern = r"(\d+-\d+\..*?)\s*(?=[卐ॐ])"

        # 3. Find all matches (DOTALL allows matching across newlines)
        matches = re.findall(pattern, content, re.DOTALL)

        if not matches:
            print("No matches found. Check if the pattern (Number-Number.) or symbol (卐) is correct.")
            return

        # 4. Write to output file
        with open(output_path, 'w', encoding='utf-8') as f:
            for match in matches:
                # Clean up newlines/spaces inside the extracted string
                clean_match = match.replace('\n', ' ').strip()
                f.write(clean_match + "\n")
        
        print(f"Success! Extracted {len(matches)} entries to '{output_path}'")

    except Exception as e:
        print(f"Error processing file: {e}")

# --- Configuration ---
input_docx = "sama-rishi.docx"  # Rename this to your file
output_txt = "sama_rishi_chandas_out.txt"

if __name__ == "__main__":
    extract_rishi_chandas_docx(input_docx, output_txt)