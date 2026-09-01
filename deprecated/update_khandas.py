#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script to update Khanda markers in Uttararchikam_complete_new.txt:
1. Change "इति" to "अथ"
2. Increment the numeral (both word and digit) by one for each Khanda marker
"""

import re
import os

# Devanagari digit mapping
dev_to_int = {'०': '0', '१': '1', '२': '2', '३': '3', '४': '4',
              '५': '5', '६': '6', '७': '7', '८': '8', '९': '9'}
int_to_dev = {v: k for k, v in dev_to_int.items()}

def devanagari_to_int(s):
    result = ''
    for ch in s:
        if ch in dev_to_int:
            result += dev_to_int[ch]
    return int(result) if result else None

def int_to_devanagari(n):
    return ''.join(int_to_dev[d] for d in str(n))

# Sanskrit ordinal names for Khanda numbers
# Mapping from number N to the Sanskrit word for Khanda N
khanda_words = {
    1: 'प्रथमः',
    2: 'द्वितीयः',
    3: 'तृतीयः',
    4: 'चतुर्थः',
    5: 'पञ्चमः',
    6: 'षष्ठः',
    7: 'सप्तमः',
    8: 'अष्ठमः',  # using the form found in the file
    9: 'नवमः',
    10: 'दशमः',
    11: 'एकादशः',
    12: 'द्वादशः',
    13: 'त्रयोदशः',
    14: 'चतुर्दशः',
    15: 'पञ्चदशः',
    16: 'षोढशः',  # using the form found in file (line 24)
    17: 'सप्तदशः',
    18: 'अष्टादशः',
    19: 'एकोनविंशः',
    20: 'विंशः',
    21: 'एकविंशः',
    22: 'द्वाविंशः',
    23: 'त्रयोविंशः',
    24: 'चतुर्वविंशः',  # using form from file (typo in original? line 33)
    25: 'पच्ञविंशः',  # using form from file (line 34)
    26: 'षढ्विंशः',
    27: 'सप्तविंशः',
    28: 'अष्टविंशः',
    29: 'नवविंशः',
    30: 'त्रिंशतः',
    31: 'एकत्रिंशतः',
    32: 'द्वात्रिंशतः',
    33: 'त्रयःस्त्रिंशतः',
    34: 'त्चतुस्त्रिंशतः',
    35: 'पञ्चस्त्रिंशतः',
    36: 'षढ्त्रिंशतः',
    37: 'सप्तत्रिंशतः',
    38: 'अष्टत्रिंशतः',
    39: 'एकोनचत्वारिंशत',  # using form from file (line 58) - no visarga
    40: 'चत्वारिंशत',
    41: 'एकचत्वारिंशत्',
    42: 'द्विचत्वारिंशत्',
    43: 'त्रिचत्वारिंशतः',
    44: 'चतुश्चत्वारिंशतः',
    45: 'पञ्चचत्वारिंशतः',
    46: 'षट्चत्वारिंशतः',
    47: 'सप्तचत्वारिंशतः',
    48: 'अष्टचत्वारिंशतः',
    49: 'एकोनपञ्चाशतः',
    50: 'पञ्चाशतः',
    51: 'एकपञ्चाशतः',
    52: 'द्विपञ्चाशतः',
    53: 'त्रिपञ्चाशतः',
    54: 'चतुःपञ्चाशतः',
    55: 'पञ्चपञ्चाशतः',
    56: 'षट्पञ्चाशतः',
    57: 'सप्तपञ्चाशतः',
    58: 'अष्टपञ्चाशतः',
    59: 'एकोनषष्टितमः',
    60: 'षष्टितमः',
}

def main():
    filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                           'data', 'input', 'Uttararchikam_complete_new.txt')
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    
    changes = []
    
    for i, line in enumerate(lines):
        # Pattern to match Khanda markers
        # Various formats found in the file:
        # ॥ इति प्रथमः खण्डः ॥ || १ ||
        # ॥एकोनचत्वारिंशत खण्डः॥ || ३९ ||
        # ॥ द्विचत्वारिंशत् खण्डः ॥ || ४२ ||
        # || ४८ || (standalone)
        # etc.
        
        # Look for lines containing khanda markers with ॥ ... खण्डः ॥
        # Match pattern: ॥ [optional इति] [word] खण्डः ॥ || [number] ||
        m = re.search(r'(॥\s*(?:इति\s+)?)([\u0900-\u097F\s]+?)\s*(खण्डः)\s*(॥\s*\|{1,2}\s*)([०-९]+)(\s*\|{1,2})', line)
        if m:
            prefix = m.group(1)     # ॥ इति  or ॥ 
            word = m.group(2).strip()  # Sanskrit word
            khandah = m.group(3)    # खण्डः
            mid = m.group(4)        # ॥ || 
            num_str = m.group(5)    # Devanagari numeral
            suffix = m.group(6)     # ||
            
            current_num = devanagari_to_int(num_str)
            if current_num is not None:
                new_num = current_num + 1
                new_dev = int_to_devanagari(new_num)
                
                # Get the new word for (current_num + 1)
                if new_num in khanda_words:
                    new_word = khanda_words[new_num]
                else:
                    print(f"WARNING: No word mapping for Khanda {new_num} (line {i+1})")
                    new_word = word  # keep old word if no mapping
                
                # Build new marker with "अथ" instead of "इति"
                old_marker = m.group(0)
                new_prefix = '॥ अथ '
                new_marker = f'{new_prefix}{new_word} {khandah} ॥ || {new_dev} ||'
                
                new_line = line[:m.start()] + new_marker + line[m.end():]
                
                changes.append({
                    'line_num': i + 1,
                    'old_num': current_num,
                    'new_num': new_num,
                    'old_marker': old_marker.strip(),
                    'new_marker': new_marker.strip(),
                })
                
                lines[i] = new_line
    
    # Handle standalone numeral markers: || N || (without ॥ ... खण्डः ॥)
    # Line 81: || ४८ ||
    # Line 97: || ५४ ||  (at beginning of content line)
    # Line 108: || ५८ || (at end of content line)
    # These need special handling - searching for standalone ॥-less markers
    for i, line in enumerate(lines):
        stripped = line.strip()
        # Check for standalone marker: just || N || on its own line
        standalone_match = re.match(r'^(\s*\|{1,2}\s*)([०-९]+)(\s*\|{1,2}\s*)$', stripped)
        if standalone_match:
            num_str = standalone_match.group(2)
            current_num = devanagari_to_int(num_str)
            if current_num is not None:
                new_num = current_num + 1
                new_dev = int_to_devanagari(new_num)
                if new_num in khanda_words:
                    new_word = khanda_words[new_num]
                    new_marker = f' ॥ अथ {new_word} खण्डः ॥ || {new_dev} ||'
                    changes.append({
                        'line_num': i + 1,
                        'old_num': current_num,
                        'new_num': new_num,
                        'old_marker': stripped,
                        'new_marker': new_marker.strip(),
                    })
                    lines[i] = new_marker + '\r'
                else:
                    print(f"WARNING: No word mapping for standalone Khanda {new_num} (line {i+1})")
    
    # Sort changes by line number for reporting
    changes.sort(key=lambda x: x['line_num'])
    
    print(f"\nTotal changes: {len(changes)}\n")
    print(f"{'Line':>5} | {'Old#':>4} -> {'New#':>4} | Old Marker -> New Marker")
    print("-" * 120)
    for c in changes:
        print(f"{c['line_num']:>5} | {c['old_num']:>4} -> {c['new_num']:>4} | {c['old_marker'][:50]:50} -> {c['new_marker'][:50]}")
    
    # Write the changes
    new_content = '\n'.join(lines)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"\nFile updated successfully: {filepath}")

if __name__ == '__main__':
    main()
