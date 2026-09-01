
import re

file_path = r'c:\Users\sekha\OneDrive\Documents\GitHub\jaimineeyasamavedam\data\input\Uttararchikam_complete_new.txt'

def devanagari_to_int(s):
    mapping = {'०':'0', '१':'1', '२':'2', '३':'3', '४':'4', '५':'5', '६':'6', '७':'7', '८':'8', '९':'9'}
    return int(''.join(mapping.get(c, c) for c in s))

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    
    # 1. Fix typo || ध८ || -> || २८ || if present
    if "|| ध८ ||" in line:
        line = line.replace("|| ध८ ||", "|| २८ ||")
    if "|| ध८||" in line:
         line = line.replace("|| ध८||", "|| २८ ||")

    stripped = line.strip()
    
    # 2. Check for Khanda Name line that might be split from its Number
    # Pattern: contains "खण्ड" and ends with "॥" or "||"
    if ("खण्डः" in line or "खण्ड" in line) and (stripped.endswith("॥") or stripped.endswith("||")):
        # Look ahead
        found_continuation = False
        if i + 1 < len(lines):
            next_line = lines[i+1]
            next_stripped = next_line.strip()
            
            # Check for immediate || Number ||
            if re.match(r'^\|\|\s*[0-9०-९]+\s*\|\|$', next_stripped):
                combined = line.rstrip() + " " + next_stripped + "\n"
                new_lines.append(combined)
                i += 2
                continue
            
            # Check for empty line then || Number ||
            elif not next_stripped and i + 2 < len(lines):
                next_next_line = lines[i+2]
                next_next_stripped = next_next_line.strip()
                if re.match(r'^\|\|\s*[0-9०-९]+\s*\|\|$', next_next_stripped):
                    combined = line.rstrip() + " " + next_next_stripped + "\n"
                    new_lines.append(combined)
                    i += 3
                    continue
    
    new_lines.append(line)
    i += 1

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Finished formatting Khanda names and numbers to single lines.")
