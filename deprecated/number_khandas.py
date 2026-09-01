"""
Script to add Sanskrit word names for standalone Khanda markers AFTER Khanda 59
(where numbering resets to 1).

These standalone markers like || १ ||, || २ ||, etc. should become:
 ॥ इति प्रथमः खण्डः ॥ || १ ||
"""

import re

file_path = r'c:\Users\sekha\OneDrive\Documents\GitHub\jaimineeyasamavedam\data\input\Uttararchikam_complete_new.txt'

# Sanskrit ordinal words matching the existing pattern in the file (Khandas 1-30)
khanda_words = {
    1: 'प्रथमः',
    2: 'द्वितीयः',
    3: 'तृतीयः',
    4: 'चतुर्थः',
    5: 'पञ्चमः',
    6: 'षष्ठः',
    7: 'सप्तमः',
    8: 'अष्टमः',
    9: 'नवमः',
    10: 'दशमः',
    11: 'एकादशः',
    12: 'द्वादशः',
    13: 'त्रयोदशः',
    14: 'चतुर्दशः',
    15: 'पञ्चदशः',
    16: 'षोडशः',
    17: 'सप्तदशः',
    18: 'अष्टादशः',
    19: 'एकोनविंशः',
    20: 'विंशः',
    21: 'एकविंशः',
    22: 'द्वाविंशः',
    23: 'त्रयोविंशः',
    24: 'चतुर्विंशः',
    25: 'पञ्चविंशः',
    26: 'षड्विंशः',
    27: 'सप्तविंशः',
    28: 'अष्टाविंशः',
    29: 'एकोनत्रिंशः',
    30: 'त्रिंशः',
}

# Devanagari digit mapping
dev_digits = {'०':'0', '१':'1', '२':'2', '३':'3', '४':'4', '५':'5', '६':'6', '७':'7', '८':'8', '९':'9'}

def devanagari_to_int(s):
    result = ''
    for ch in s:
        if ch in dev_digits:
            result += dev_digits[ch]
    return int(result) if result else None

def int_to_devanagari(n):
    rev_map = {v: k for k, v in dev_digits.items()}
    return ''.join(rev_map[d] for d in str(n))

# Read the file
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Total lines: {len(lines)}")

# First find the line containing Khanda 59 marker to know where the reset starts
khanda59_line = None
for i, line in enumerate(lines):
    if '५९' in line and 'खण्ड' in line:
        khanda59_line = i
        print(f"Found Khanda 59 at line {i+1}: {line.strip()[:80]}")
        break

if khanda59_line is None:
    # Try finding || ५९ ||
    for i, line in enumerate(lines):
        if re.search(r'\|\|\s*५९\s*\|\|', line.strip()):
            khanda59_line = i
            print(f"Found Khanda 59 marker at line {i+1}: {line.strip()[:80]}")
            break

if khanda59_line is None:
    print("ERROR: Could not find Khanda 59 marker!")
    exit(1)

print(f"\nLooking for standalone markers after line {khanda59_line + 1}...")
print()

# Now process lines AFTER Khanda 59
new_lines = []
changes_made = 0

for i, line in enumerate(lines):
    stripped = line.strip()
    
    # Only modify standalone markers AFTER Khanda 59
    if i > khanda59_line:
        # Check for standalone numeral marker: || N ||
        if re.match(r'^\s*\|\|\s*[०-९]+\s*\|\|\s*$', stripped):
            num_match = re.search(r'[०-९]+', stripped)
            if num_match:
                num = devanagari_to_int(num_match.group())
                if num in khanda_words:
                    word = khanda_words[num]
                    dev_num = int_to_devanagari(num)
                    new_marker = f" ॥ इति {word} खण्डः ॥ || {dev_num} ||\r\n"
                    print(f"  Line {i+1}: || {num} || -> {new_marker.strip()}")
                    new_lines.append(new_marker)
                    changes_made += 1
                    continue
                else:
                    print(f"  Line {i+1}: || {num} || -> NO WORD DEFINED (skipping)")
        
        # Also handle line 161 pattern: || १६ || ॥ इति षोढषः खण्डः ॥
        # This already has a name but in wrong order; reformat it
        if re.match(r'^\s*\|\|\s*[०-९]+\s*\|\|\s*॥.*खण्डः\s*॥', stripped):
            num_match = re.search(r'[०-९]+', stripped)
            if num_match:
                num = devanagari_to_int(num_match.group())
                if num in khanda_words:
                    word = khanda_words[num]
                    dev_num = int_to_devanagari(num)
                    new_marker = f" ॥ इति {word} खण्डः ॥ || {dev_num} ||\r\n"
                    print(f"  Line {i+1}: '{stripped[:60]}' -> {new_marker.strip()}")
                    new_lines.append(new_marker)
                    changes_made += 1
                    continue
    
    new_lines.append(line)

print()
print(f"Total changes: {changes_made}")

if changes_made > 0:
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    print(f"\nFile updated: {file_path}")
else:
    print("\nNo changes needed.")
