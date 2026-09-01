import re
import argparse
import os
import sys

def remove_english_lines(input_path, output_path=None):
    """
    Removes lines containing English characters (A-Z, a-z) from the file.
    Also handles common OCR artifacts like "Page <xx>" or "No content".
    """
    if not os.path.exists(input_path):
        print(f"Error: Input file '{input_path}' not found.")
        return

    if output_path is None:
        base, ext = os.path.splitext(input_path)
        output_path = f"{base}_cleaned{ext}"

    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        cleaned_lines = []
        removed_count = 0
        
        # Regex for English characters
        english_pattern = re.compile(r'[A-Za-z]')
        
        for line in lines:
            # Check if line contains English characters
            if english_pattern.search(line):
                # print(f"Removing line: {line.strip()}")
                removed_count += 1
                continue
                
            # Check if line is empty or just whitespace
            if not line.strip():
                # We might want to keep *formatting* empty lines, or remove excessive ones?
                # The user didn't specify, but often OCR adds blank lines.
                # Let's keep blank lines if they separate paragraphs, but maybe unwanted ones are removed?
                # For now, I will KEEP blank lines unless they are part of the 'Page' block which usually has surrounding blanks.
                # But simple heuristic: keep blank lines.
                cleaned_lines.append(line)
                continue
            
            cleaned_lines.append(line)
            
        with open(output_path, 'w', encoding='utf-8') as f:
            f.writelines(cleaned_lines)
            
        print(f"Processed {len(lines)} lines.")
        print(f"Removed {removed_count} lines containing English text.")
        print(f"Output saved to: {output_path}")
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Remove lines containing English text.")
    parser.add_argument("input_file", help="Path to the input file")
    parser.add_argument("-o", "--output_file", help="Path to the output file (optional)", default=None)
    
    args = parser.parse_args()
    
    remove_english_lines(args.input_file, args.output_file)
