import json

input_path = "output_text/final-Grantha.json"
output_path = "x1.json"

with open(input_path, "r", encoding="utf-8") as f:
    data = json.load(f)



# Retain the key 'supersection' in the output, containing only 'supersection_5'
output_data = {"supersection": {"supersection_5": data["supersection"]["supersection_5"]}}

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(output_data, f, ensure_ascii=False, indent=2)

print(f"Written supersection_5 to {output_path}")

'''
[(1, 1), (2, 1), (3, 1), (6, 1), (8, 1), (11, 1), (12, 1)] 
number of mantra words 14 of lengths 
[(0, '𑌵𑌿', 1), (1, '𑌶𑍍𑌪𑍋', 2), (2, '𑌹𑌾', 1), (3, '𑌇', 1), (4, '।', 1), (5, '𑌪𑌾𑌰𑍍𑌕𑍍𑌤', 4), (6, '𑌨𑌾', 1), (7, '𑌆𑌭𑌿', 2), (8, '𑌭𑍂', 1), (9, '𑌤', 1), (10, '𑌰', 1), (11, '𑌨𑍍𑌨𑌾', 2), (12, '𑌰𑌾𑌃', 1), (13, '।', 1)] 
number of swaras 8 of lengths 
[(0, '𑌤𑍍𑌯', 2), (1, '𑌤', 1), (2, '𑌶', 1), (3, '𑌟𑌿', 1), (4, '𑌕𑌿', 1), (5, '𑌕𑍍𑌯𑌚', 3), (6, '𑌕', 1), (7, '𑌚', 1)]

'''

'''
 {'swara_mantra_intersections': 
 {'swara-0': [(1, {'intersecting_characters': [1, 2, 3]})], 'swara-1': [2], 'swara-2': [3], 'swara-3': [6], 'swara-4': [8], 'swara-5': [10], 'swara-6': [11], 'swara-7': [(12, {'intersecting_characters': [0, 1]})]},
 'swara_word_char_mapping': 
 {'swara-0': (1298, 79, 284, 197), 'swara-1': (1879, 79, 177, 126), 'swara-2': (2355, 79, 195, 103), 'swara-3': (3824, 23, 195, 196), 'swara-4': (5012, 20, 158, 162), 'swara-5': (5833, 78, 462, 198), 'swara-6': (6589, 79, 145, 103), 'swara-7': (7024, 78, 192, 104)}, 
 'mantra_word_char_mapping': 
 {'mantra-0': (606, 20, 279, 210), 'mantra-1': (1005, 28, 618, 331), 'mantra-2': (1722, 96, 422, 173), 'mantra-3': (2253, 95, 221, 141), 'mantra-4': (2620, 56, 31, 194), 'mantra-5': (2754, 89, 804, 289), 'mantra-6': (3657, 97, 365, 165), 'mantra-7': (4129, 20, 625, 278), 'mantra-8': (4868, 57, 465, 201), 'mantra-9': (5428, 98, 229, 161), 'mantra-10': (5771, 98, 194, 133), 'mantra-11': (6422, 97, 380, 162), 'mantra-12': (6916, 95, 426, 139), 'mantra-13': (7478, 56, 31, 194)},
 'image_name': 'output_text/lines/page_241/combined_04_05.png'} 
 number of mantra words 14 of lengths 
 [(0, '𑌵𑌿', 1), (1, '𑌶𑍍𑌪𑍋', 2), (2, '𑌹𑌾', 1), (3, '𑌇', 1), (4, '।', 1), (5, '𑌪𑌾𑌰𑍍𑌕𑍍𑌤', 4), (6, '𑌨𑌾', 1), (7, '𑌆𑌭𑌿', 2), (8, '𑌭𑍂', 1), (9, '𑌤', 1), (10, '𑌰', 1), (11, '𑌨𑍍𑌨𑌾', 2), (12, '𑌰𑌾𑌃', 1), (13, '।', 1)]
 number of swaras 8 of lengths 
 [(0, '𑌤𑍍𑌯', 2), (1, '𑌤', 1), (2, '𑌶', 1), (3, '𑌟𑌿', 1), (4, '𑌕𑌿', 1), (5, '𑌕𑍍𑌯𑌚', 3), (6, '𑌕', 1), (7, '𑌚', 1)]
'''
