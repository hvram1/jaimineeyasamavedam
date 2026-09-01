import grapheme
import char_map
import json
import os
import cv2
import numpy as np


def find_matching_hashmap(hashmaps, **params):
        
        for hashmap in hashmaps:
            if all(hashmap.get(k) == v for k, v in params.items()):
                return hashmap
        return None
    



list_of_sentences=[
    #"𑌅𑌗𑍍𑌨𑌆𑌯𑌾𑌹𑍀 𑌵𑍀।𑌤𑌾𑌯𑌾𑌇𑌗𑍃𑌣𑌾𑌨𑍋𑌹𑌵𑍍𑌯𑌦𑌾 𑌤𑌾",    #27 character boxes (19,31)
    #"𑌯𑌾 𑌇। 𑌨𑍀𑌹𑍋𑌤𑌾 𑌸𑌤𑍍𑌸𑍀𑌬 𑌰𑍍𑌹𑌾 𑌇 𑌷𑍀। 𑌬 𑌰𑍍𑌹𑌾 𑌇", # 25 character boxes (19,30)
    #"𑌦𑌾 𑌤𑌾 𑌯𑍇। 𑌨𑍀𑌹𑍋𑌤𑌾 𑌸𑌾𑌤𑍍 । 𑌸𑌾 𑌇 𑌬𑌾। 𑍠 𑌹𑌾",#26 character boxes (16,27)
    #"𑌤𑍍𑌵𑌮𑌗𑍍𑌨𑍇 𑌯𑌜𑍍𑌞𑌾𑌨𑌾𑌂𑌤𑍍𑌵𑌮 𑌗𑍍𑌨𑌾 𑌇। 𑌯𑌜𑍍𑌞𑌾𑌨𑌾𑌂𑌹𑍋𑌤𑌾", #29 character boxes (22,38)
    #"𑌵𑌿 𑌶𑍍𑌪𑍇 𑌷𑌾𑌂 𑌹𑌾 𑌇 𑌤𑌾: । 𑌦𑍇 𑌵𑌾𑌇 𑌭𑌾 𑌇 𑌰𑍍𑌮𑌾 ।", #27 character boxes (17,29)
    #"𑌪𑍇𑌰𑌷𑍍𑌠𑌂 𑌵𑌾: । 𑌅 𑌤𑌾 𑌇 𑌥𑍀𑌂 । 𑌸𑍍𑌤𑍁 𑌷𑍇 𑌮𑌿𑌤𑍍𑌰𑌮𑌿𑌵",
    #"𑌅𑌶𑍍𑌪𑌨𑍍𑌨𑌤𑍍𑌵𑌾𑌵𑌾𑌰𑌵 𑌭𑌾𑌂 । 𑌵𑌨𑍍𑌦𑌧𑍍𑌯𑌾𑌅𑌗𑍍𑌨𑌿𑌨𑍍𑌨𑌮𑍋 𑌭𑌾",
    "𑌨𑍁 𑌷𑍇। 𑌜 𑌨𑌾 𑌔 𑌹𑍋 𑌬𑌾  𑌹𑍋 𑌇 ழா।।4।।",
    #"𑌤𑍇 𑌨𑌾 𑌕𑌾 𑌮𑌾 𑌚𑍍𑌛𑌾𑌇                  𑌭𑌾। 𑌓           𑌇 ।। 1।।                (120)", #To be debugged 
    "𑌯𑌾 𑌸𑍍𑌮𑌾 𑌹𑍋 𑌇 𑌶𑍍𑌰𑍁 𑌤𑌰𑍍𑌵𑌨𑍍𑌨𑌾𑌕𑍍𑌷𑌾𑌇𑌬𑍃",
    "𑌮𑌾𑌨𑌾𑌃 । 𑌹𑍃𑌣𑍀 𑌥𑌾 𑌆𑌤𑌿𑌥𑌿𑌂 𑌵𑌾𑌸𑍁 𑌰𑌾𑌗𑍍𑌨𑌿𑌃 ।",
    
    
    
]

 
def process_grantha_data():
    
    with open("output_text/line-category.json", "r", encoding="utf-8") as f:
        line_json = json.load(f)
    all_hashmaps = []
    for key, hashmap_list in line_json.items():
        if isinstance(hashmap_list, list):
            all_hashmaps.extend(hashmap_list)

    with open("output_text/image-properties.json", "r", encoding="utf-8") as f:
        image_json = json.load(f)
    
    
    
    with open("output_text/final-Grantha.json", 'r', encoding='utf-8') as f:
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
                    mantra_sub_position_hash={}
                    OneWord_MantraFlag=False
                    error_Flag=False
                    swara_differ_Flag=False
                    mantra_differ_Flag=False
                    mantra_words=mantra_set.get("mantra-words", "")
                    for i,mantra_word in enumerate(mantra_words):
                        mantra_word.pop("swara_positions")
                    
                    img_src=mantra_set.get('image-ref', '')
                    img_path = os.path.join(output_base_dir, img_src)
                    base_name = os.path.basename(img_path)
                    directory_name = os.path.dirname(img_path)
                    img_names=base_name.split('_')
                    page_names=directory_name.split('_')
                    page_number=int(page_names[2])
                    if base_name.startswith("combined"):
                        
                        mantra_line=int(img_names[1])
                        swara_line=int(img_names[2].replace(".png",""))
                        hashmap = image_json.get(img_path)
                        if hashmap is None:
                            print(f" WARNING {img_path} not found in image_json")
                            continue
                        image_mantra_words=hashmap.get("mantra_word_char_mapping",{})
                        image_swara_words=hashmap.get("swara_word_char_mapping",{})
                        intersection_words=hashmap.get("swara_mantra_intersections",{})
                        
                        text_swara_list = mantra_set.get("swara", "").split()
                        text_mantra_words=mantra_set.get("mantra-words", "")
                        if len(image_mantra_words) ==1:
                            print(f" {img_path} Entire mantra  mapped as 1 word ")
                            OneWord_MantraFlag=True
                        if len(text_mantra_words) != len(image_mantra_words) and len(image_mantra_words) < len(text_mantra_words):
                            
                            hashmap_og_text = find_matching_hashmap(all_hashmaps, page=str(page_number), line_number_in_page=mantra_line)
                            if hashmap_og_text !=None:
                                og_mantra_text=hashmap_og_text.get('text').split()
                            mantra_differ_Flag = True
                            #print(f" {img_path} mantra text {len(text_mantra_words)} , image {len(image_mantra_words)}, og_mantra_text {len(og_mantra_text)}")
                        
                        if len(image_swara_words) != len(text_swara_list):
                            
                            hashmap_og_text = find_matching_hashmap(all_hashmaps, page=str(page_number), line_number_in_page=swara_line)
                            if hashmap_og_text !=None:
                                og_swara_text=hashmap_og_text.get('text').split()
                            if len(og_swara_text) != len(image_swara_words):
                                #print(f" {img_path} swara text {len(text_swara_list)} , image {len(image_swara_words)} og_swara_text {len(og_swara_text)}")
                                swara_differ_Flag=True
                                # Check for empty swara word mapping and if this is not the last
                        for s,swara_key in enumerate(intersection_words.keys()):
                            swara_mapping=intersection_words.get(swara_key)
                            #print(f" {img_path} swara_key {swara_key} has mapping {swara_mapping}")
                            if len(swara_mapping) ==0 and s != len(intersection_words)-1:
                                print(f" ERROR {img_path} swara_key {swara_key} has a empty mapping in image_swara_words")
                                
                                error_Flag=True
                        last_mantra_position=-1
                        full_sentence=""    
                        for item in intersection_words.keys():
                            mantra_item = intersection_words.get(item)
                            if len(mantra_item) ==0:
                                #print(f" {img_path} Case of missing swara mantra intesction for {item}")
                                continue
                            swara_position = int(item.replace("swara-", ""))
                            mantra_sub_position=-1
                            if swara_position < len(text_swara_list):
                                swara=text_swara_list[swara_position]
                            if len(mantra_item) >1 :
                                #print(f" Picking only the first item for {img_path} ({swara}) matching more than one {mantra_item} -  ")
                                pass
                            if isinstance(mantra_item, list):
                                
                                try:
                                    
                                    mantra_position=int(mantra_item[0])
                                    
                                        
                                except Exception as e:
                                    #print(f"Error processing mantra_item: {mantra_item[0]}, Exception: {e}")
                                    if len(mantra_item) >=1:
                                        for sub_item in mantra_item[0]:
                                            if isinstance(sub_item, int):
                                                mantra_position = sub_item
                                            if isinstance(sub_item, dict):
                                                char_map=sub_item.get('intersecting_characters',{})
                                                if len(char_map) >1:
                                                    for ch, char in enumerate(char_map):
                                                    #print(f" WARNING {img_path} matching multiple charaters . picking the first one {char_map} .  ")
                                                    # check if the sub char position and word is already mapped ( in case of 1 word images)
                                                        if mantra_sub_position_hash.get(ch,-1) ==mantra_position:
                                                            pass
                                                        else:
                                                            mantra_sub_position=char_map[ch]
                                                            mantra_sub_position_hash[ch] = mantra_position
                                                            print(f" WARNING {img_path} matching multiple charaters . picking {ch} at {mantra_position} for swara {item}.  ")

                                                            break
                                    else:
                                        #print(f" WARNING {img_path} mantra_item is not a list or empty {mantra_item}. Possibly not an error . Ignoring ")
                                        continue

                                    #
                                if mantra_position < len(text_mantra_words):
                                    
                                    mantra=text_mantra_words[mantra_position]
                                    #print(f" 1. MANTRA {img_path} {mantra.get('word','')}({swara}) ")
                                    while (last_mantra_position < mantra_position-1):
                                        
                                        last_mantra_position += 1
                                        prev_mantra=text_mantra_words[last_mantra_position].get('word','')
                                        full_sentence+=f' {prev_mantra}'
                                    if mantra_sub_position == -1:
                                        full_sentence+=f" {mantra.get('word','')}({swara})"
                                    else:
                                        mantra_to_be_split=mantra.get('word','')
                                        #print(f" 1. position is {mantra_sub_position} for {mantra_to_be_split}")
                                        g1_x_1 = grapheme.slice(mantra_to_be_split,end=mantra_sub_position+1)
                                        g1_x_2 = grapheme.slice(mantra_to_be_split,start=mantra_sub_position+1)
                                        full_sentence+=f' {g1_x_1}({swara}){g1_x_2}'
                                    last_mantra_position=mantra_position
                                    
                                elif mantra_position == len(text_mantra_words):
                                    mantra=text_mantra_words[mantra_position-1]
                                    #print(f" 2. Adjusting the last position MANTRA {img_path} {mantra.get('word','')}({swara}) ")
                                    while (last_mantra_position < mantra_position-2):
                                        
                                        last_mantra_position += 1
                                        prev_mantra=text_mantra_words[last_mantra_position].get('word','')
                                        full_sentence+=" "+prev_mantra
                                    if mantra_sub_position == -1:
                                        full_sentence+=f" {mantra.get('word','')}({swara})"
                                    else:
                                        mantra_to_be_split=mantra.get('word','')
                                        #print(f" 2. position is {mantra_sub_position} for {mantra_to_be_split}")
                                        g1_x_1 = grapheme.slice(mantra_to_be_split,end=mantra_sub_position+1)
                                        g1_x_2 = grapheme.slice(mantra_to_be_split,start=mantra_sub_position+1)
                                        full_sentence+=f' {g1_x_1}({swara}){g1_x_2}'
                                        #pass
                                    last_mantra_position=mantra_position
                                else:
                                    mantra_sentence=""
                                    
                                    for mantra in text_mantra_words:
                                        mantra_sentence+=f'{mantra.get("word","")} '
                                    error_Flag=True
                                    print(f" ERROR {img_path} mantra_position {mantra_position} is more than text -  {len(text_mantra_words)} {mantra_sentence} {mantra_set.get('swara', '')}")
                                        
                                
                            else:
                                print(f" {img_path} mantra_item is of type {type(mantra_item)} and its value is {mantra_item}")
                        while (last_mantra_position < len(text_mantra_words)-1 ):
                            last_mantra_position+=1
                            prev_mantra=text_mantra_words[last_mantra_position].get('word','')
                            full_sentence+=" "+prev_mantra
                        print(f"{img_path} {full_sentence}")
                        mantra_words=mantra_set.get("mantra-words", "")
                        full_sentence_array=full_sentence.split()
                        diff_len=abs(len(mantra_words) - len(full_sentence_array))
                        if diff_len >2 :
                            print(f"ERROR {img_path} Length not the same {len(mantra_words)} {len(full_sentence_array)}")
                            print(f" {mantra_words}")
                            error_Flag=True
                        mantra_set.pop("mantra-words")
                        mantra_words=[]
                        for i, mantra_word in enumerate(full_sentence_array):
                            my_hash={}
                            my_hash["word"]=mantra_word
                            mantra_words.append(my_hash)
                        mantra_set["mantra-words"]=mantra_words
                        mantra_set["probableError"]=error_Flag
                        
                            
                    else:
                        mantra_line=int(img_names[1].split('.')[0])
                    page_names=directory_name.split('_')
                    page_number=int(page_names[2])
    output_json_filename = f"rewritten_final-Grantha.json"
    out_path = os.path.join("output_text", output_json_filename)
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
                    
                    
                    
                    
    

if __name__ == "__main__":
    process_grantha_data()
   
        
