"""
Move khanda markers in the second section of Uttararchikam_complete_new.txt.

Each marker like '॥ अथ ... खण्डः ॥ || N ||' currently appears AFTER the content
it belongs to. This script moves each marker to BEFORE its content block.

Khanda 1 marker (line 112) was already fixed manually, so we skip it.
"""

file_path = r'c:\Users\sekha\OneDrive\Documents\GitHub\jaimineeyasamavedam\data\input\Uttararchikam_complete_new.txt'

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

def is_khanda_marker(line):
    stripped = line.strip()
    return 'अथ' in stripped and 'खण्डः' in stripped and '॥' in stripped

# Collect marker indices in the second section (after Khanda 1 which is already fixed at 0-indexed 111)
marker_indices = []
for i in range(112, len(lines)):  # Start after Khanda 1 marker
    if is_khanda_marker(lines[i]):
        marker_indices.append(i)

print(f"Found {len(marker_indices)} markers to move:")
for idx in marker_indices:
    print(f"  Line {idx+1}: {lines[idx].strip()}")

# Process from bottom to top so index shifts don't affect earlier markers
for marker_idx in reversed(marker_indices):
    # Find the first non-blank line above the marker
    pos = marker_idx - 1
    while pos >= 0 and lines[pos].strip() == '':
        pos -= 1
    
    if pos < 0:
        print(f"  No content above marker at line {marker_idx+1}, skipping")
        continue
    
    # Now find the start of the contiguous content block
    block_end = pos
    while pos > 0 and lines[pos - 1].strip() != '' and not is_khanda_marker(lines[pos - 1]):
        pos -= 1
    block_start = pos
    
    if block_start >= marker_idx:
        continue  # Nothing to move
    
    print(f"  Moving marker from line {marker_idx+1} to before line {block_start+1}")
    
    # Remove marker from current position and insert before content block
    marker_line = lines.pop(marker_idx)
    lines.insert(block_start, marker_line)

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print(f"\nDone! Wrote {len(lines)} lines.")
