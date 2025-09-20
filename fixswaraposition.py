import sys
import json
import os
import grapheme
from extract_textFromImage import extract_words_from_image
if len(sys.argv) < 2:
    print("Usage: python swaraposition.py <input_json_file>")
    sys.exit(1)

input_json_file = sys.argv[1]
with open(input_json_file, 'r', encoding='utf-8') as f:
    data = json.load(f)
output_base_dir = "output_text"    
supersections = data.get('supersection', {})
for i, supersection in enumerate(supersections):
    for j, section in enumerate(supersections[supersection].get('sections', [])):
        sections = supersections[supersection].get('sections', [])
        for k, subsection in enumerate(sections[section].get('subsections', [])):
            subsections = sections[section].get('subsections', [])
            
            mantra_sets = subsections[subsection].get('mantra_sets', [])
            
            for l, mantra_set in enumerate(mantra_sets):
                img_src=mantra_set.get('image-ref', '')
                img_path = os.path.join(output_base_dir, img_src)
                mantra_words=mantra_set.get("mantra-words", "")
                swara_list = mantra_set.get("swara", "").split()
                number_of_columns = len(mantra_words)
                number_of_swaras = len(swara_list)
                mantra_word_length=[]
                swara_word_length=[]
                for i, mantra_word in enumerate(mantra_words):
                    tup_le=(i,mantra_word.get("word"),grapheme.length(mantra_word.get("word")))
                    mantra_word_length.append(tup_le)
                
                for j, swara in enumerate(swara_list):
                    tup_le = (j, swara, grapheme.length(swara))
                    swara_word_length.append(tup_le)
                positions = extract_words_from_image(img_path, output_base_dir, mantra_word_lengths=mantra_word_length, swara_word_lengths=swara_word_length)
                #print(f"Extracted positions for {img_src}: {positions} number of mantra words {number_of_columns} number of swaras {number_of_swaras}")
                print(f"Extracted positions for {img_src}: {positions} number of mantra words {number_of_columns} of lengths {mantra_word_length} number of swaras {number_of_swaras} of lengths {swara_word_length}")
                
                for i,mantra_word in enumerate(mantra_words):
                    mantra_word.pop("swara_positions")
                if positions== None:
                    continue
                for j,position in enumerate(positions):
                    if j<len(mantra_words):
                        mantra_word=mantra_words[j].get("word", "")
                        if mantra_word=="":
                            print(f"Mantra word is empty for position {j}")
                            continue
                        if position is None:
                            print(f"Position is None for mantra word {mantra_word} at position {j}")
                            continue
                        if j >= len(swara_list):
                            print(f"Swara word is empty for position {j}")
                            continue
                        swara_word=swara_list[j]
                        mantra_word_prefix=grapheme.slice(mantra_word, 0, position[1])
                        mantra_word_suffix=grapheme.slice(mantra_word, position[1])
                        mantra_word=f"{mantra_word_prefix}({swara_word}){mantra_word_suffix}"
                        word_position,character_position=position[0],position[1]
                        swara_positions={"word_position":word_position,"character_position":character_position}
                        mantra_words[j]["word"]=mantra_word 
'''
            if (k>1):
                break
        if (j>1):
            break
    if (j>1):
        break
'''

output_json_filedir=os.path.dirname(input_json_file)
#output_json_filename=os.path.basename(input_jsonfile)
output_json_filename = f"rewritten_{os.path.basename(input_json_file)}"
out_path = os.path.join(output_json_filedir, output_json_filename)
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
