
import sys
import re

def contains_devanagari(text):
    # Devanagari Unicode block is U+0900 to U+097F
    return bool(re.search(r'[\u0900-\u097F]', text))

def clean_file(input_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Filter lines: Keep only if it contains Devanagari or is effectively empty (newlines)
    # Actually, the user wants to clean English text. Empty lines might be useful to preserve paragraph structure?
    # But looking at the file, the empty lines often sandwich the noise.
    # Let's keep a line if it has Devanagari. What about blank lines?
    # Ideally we preserve structure. 
    # But if an English block was "Page 92", removing it leaves a blank line or merges things?
    # Use simple logic: If line has alphabetic English characters [a-zA-Z], treat it as suspect.
    # But earlier I thought "Keep if Devanagari".
    # Let's stick to "Keep if Devanagari OR if it is whitespace only".
    # But "Page 92" has whitespace. 
    # Let's try: If line contains Devanagari, keep it. 
    # If line is empty/whitespace, keep it (maybe? or maybe clean it up).
    # The user said "Clean all the English text out".
    
    cleaned_lines = []
    for line in lines:
        if contains_devanagari(line):
            cleaned_lines.append(line)
        elif not line.strip():
            # Preserve blank lines for now, we can always tighten later if needed, 
            # but usually stripping English leaves gaps we might want to close or keep depending on structure.
            # Looking at the input, "Page 92" is surrounded by blank lines.
            # If we remove "Page 92", we get 3 blank lines.
            # Maybe we should just only keep lines with Devanagari?
            # Let's look at the file content again.
            # Line 18: Page 92. Line 19: Text.
            # If I remove 18, I have 17 (blank) and 19 (text).
            # The structure seems to be blocks of text.
            # Let's just keep lines with Devanagari.
            # Wait, if I drop ALL blank lines, the text might become a solid wall.
            # Let's check the Devanagari lines.
            # Line 19, 20 are paragraphs.
            # If I drop blank lines, 19 and 20 will be adjacent. That seems fine.
            # BUT, look at Line 22 and 24 (Page 93) and 25.
            # Line 22 ends ...
            # Line 25 starts ...
            # They are likely continuous text split by pagination.
            # So removing blank lines constitutes a "merge" which might be good.
            # However, looking at Line 19 and 20, they end with || 13 || and || 14 ||. They are distinct verses.
            # Merging them onto one line is bad? No, f.readlines() keeps the \n.
            # So they will be on separate lines.
            pass
    
    # Revised logic:
    # 1. Iterate through lines.
    # 2. If line has Devanagari -> Keep.
    # 3. If line has NO Devanagari -> Discard (it's English noise or empty).
    # 4. Result: A list of Devanagari lines.
    
    cleaned_lines = [line for line in lines if contains_devanagari(line)]
    
    with open(input_path, 'w', encoding='utf-8') as f:
        f.writelines(cleaned_lines)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python clean_english.py <input_file>")
        sys.exit(1)
    
    clean_file(sys.argv[1])
