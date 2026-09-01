#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Fix the reset section Khanda markers (from line 112 onwards).
These were incorrectly incremented by 1 and need to be decremented back.
Some were already fixed by the first round of multi_replace, but others
need to be fixed by targeting specific line numbers.
"""

import os

# Correct mappings: line_number -> correct marker text
# These are the ones that still need fixing based on current state
fixes = {
    124: ' \u0965 \u0905\u0925 \u091a\u0924\u0941\u0930\u094d\u0925\u0903 \u0916\u0923\u094d\u0921\u0903 \u0965 || \u096a ||\r\n',   # Khanda 4
    128: ' \u0965 \u0905\u0925 \u092a\u091e\u094d\u091a\u092e\u0903 \u0916\u0923\u094d\u0921\u0903 \u0965 || \u096b ||\r\n',   # Khanda 5
    131: ' \u0965 \u0905\u0925 \u0937\u0937\u094d\u0920\u0903 \u0916\u0923\u094d\u0921\u0903 \u0965 || \u096c ||\r\n',        # Khanda 6
    136: ' \u0965 \u0905\u0925 \u0938\u092a\u094d\u0924\u092e\u0903 \u0916\u0923\u094d\u0921\u0903 \u0965 || \u096d ||\r\n',  # Khanda 7
    141: ' \u0965 \u0905\u0925 \u0905\u0937\u094d\u0920\u092e\u0903 \u0916\u0923\u094d\u0921\u0903 \u0965 || \u096e ||\r\n',  # Khanda 8 (was duplicate)
    145: ' \u0965 \u0905\u0925 \u0928\u0935\u092e\u0903 \u0916\u0923\u094d\u0921\u0903 \u0965 || \u096f ||\r\n',              # Khanda 9
    149: ' \u0965 \u0905\u0925 \u0926\u0936\u092e\u0903 \u0916\u0923\u094d\u0921\u0903 \u0965 || \u0967\u0966 ||\r\n',        # Khanda 10
    155: ' \u0965 \u0905\u0925 \u090f\u0915\u093e\u0926\u0936\u0903 \u0916\u0923\u094d\u0921\u0903 \u0965 || \u0967\u0967 ||\r\n',  # Khanda 11
    159: ' \u0965 \u0905\u0925 \u0926\u094d\u0935\u093e\u0926\u0936\u0903 \u0916\u0923\u094d\u0921\u0903 \u0965 || \u0967\u0968 ||\r\n',  # Khanda 12 (was duplicate)
    167: ' \u0965 \u0905\u0925 \u091a\u0924\u0941\u0930\u094d\u0926\u0936\u0903 \u0916\u0923\u094d\u0921\u0903 \u0965 || \u0967\u096a ||\r\n',  # Khanda 14
    171: ' \u0965 \u0905\u0925 \u092a\u091e\u094d\u091a\u0926\u0936\u0903 \u0916\u0923\u094d\u0921\u0903 \u0965 || \u0967\u096b ||\r\n',  # Khanda 15
    174: ' \u0965 \u0905\u0925 \u0937\u094b\u0922\u0936\u0903 \u0916\u0923\u094d\u0921\u0903 \u0965 || \u0967\u096c ||\r\n',  # Khanda 16
    181: ' \u0965 \u0905\u0925 \u0938\u092a\u094d\u0924\u0926\u0936\u0903 \u0916\u0923\u094d\u0921\u0903 \u0965 || \u0967\u096d ||\r\n',  # Khanda 17 (was duplicate)
    184: ' \u0965 \u0905\u0925 \u0905\u0937\u094d\u091f\u093e\u0926\u0936\u0903 \u0916\u0923\u094d\u0921\u0903 \u0965 || \u0967\u096e ||\r\n',  # Khanda 18
    187: ' \u0965 \u0905\u0925 \u090f\u0915\u094b\u0928\u0935\u093f\u0902\u0936\u0903 \u0916\u0923\u094d\u0921\u0903 \u0965 || \u0967\u096f ||\r\n',  # Khanda 19
    190: ' \u0965 \u0905\u0925 \u0935\u093f\u0902\u0936\u0903 \u0916\u0923\u094d\u0921\u0903 \u0965 || \u0968\u0966 ||\r\n',  # Khanda 20
    193: ' \u0965 \u0905\u0925 \u090f\u0915\u0935\u093f\u0902\u0936\u0903 \u0916\u0923\u094d\u0921\u0903 \u0965 || \u0968\u0967 ||\r\n',  # Khanda 21
    196: ' \u0965 \u0905\u0925 \u0926\u094d\u0935\u093e\u0935\u093f\u0902\u0936\u0903 \u0916\u0923\u094d\u0921\u0903 \u0965 || \u0968\u0968 ||\r\n',  # Khanda 22 (was duplicate)   
    201: ' \u0965 \u0905\u0925 \u0924\u094d\u0930\u092f\u094b\u0935\u093f\u0902\u0936\u0903 \u0916\u0923\u094d\u0921\u0903 \u0965 || \u0968\u0969 ||\r\n',  # Khanda 23
    206: ' \u0965 \u0905\u0925 \u091a\u0924\u0941\u0930\u094d\u0935\u0935\u093f\u0902\u0936\u0903 \u0916\u0923\u094d\u0921\u0903 \u0965 || \u0968\u096a ||\r\n',  # Khanda 24
    211: ' \u0965 \u0905\u0925 \u092a\u091a\u094d\u091e\u0935\u093f\u0902\u0936\u0903 \u0916\u0923\u094d\u0921\u0903 \u0965 || \u0968\u096b ||\r\n',  # Khanda 25
    216: ' \u0965 \u0905\u0925 \u0937\u0922\u094d\u0935\u093f\u0902\u0936\u0903 \u0916\u0923\u094d\u0921\u0903 \u0965 || \u0968\u096c ||\r\n',  # Khanda 26 (was duplicate)
    221: ' \u0965 \u0905\u0925 \u0938\u092a\u094d\u0924\u0935\u093f\u0902\u0936\u0903 \u0916\u0923\u094d\u0921\u0903 \u0965 || \u0968\u096d ||\r\n',  # Khanda 27 (was duplicate)
    229: ' \u0965 \u0905\u0925 \u0928\u0935\u0935\u093f\u0902\u0936\u0903 \u0916\u0923\u094d\u0921\u0903 \u0965 || \u0968\u096f ||\r\n',  # Khanda 29
    233: ' \u0965 \u0905\u0925 \u0924\u094d\u0930\u093f\u0902\u0936\u0924\u0903 \u0916\u0923\u094d\u0921\u0903 \u0965 || \u0969\u0966 ||\r\n',  # Khanda 30 (was duplicate)
}

filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                       'data', 'input', 'Uttararchikam_complete_new.txt')

with open(filepath, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Total lines: {len(lines)}")
print()

for line_num, new_content in sorted(fixes.items()):
    idx = line_num - 1  # 0-based index
    old = lines[idx].strip()
    new = new_content.strip()
    print(f"Line {line_num}: '{old}' -> '{new}'")
    lines[idx] = new_content

with open(filepath, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print(f"\nDone! Fixed {len(fixes)} markers.")
