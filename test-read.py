import grapheme
import char_map
import json
import os
import cv2
import numpy as np

def get_character_count(sentence,printDebug=False):
    grapheme_length=0
    unicode_length=0
    aaMatra_count=0
    aiMatra_count=0
    eeMatra_count=0
    ooMatra_count=0
    auMatra_count=0
    uuMatra_count=0
    tamil_aa_count=0
    au_count=0
    rVocallicMatra_count=0
    ii_count=0
    anusvara_count=0
    uMatra_count=0
    tamil_aa = '\u0bbe'
    # subtract
    n_na_gran=f"{char_map.na_gran}{char_map.virama}{char_map.na_gran}"
    t_va_gran=f"{char_map.ta_gran}{char_map.virama}{char_map.va_gran}"
    sh_ra_gran=f"{char_map.sha_gran}{char_map.virama}{char_map.ra_gran}{char_map.uMatra_gran}"
    k_ssa_gran=f"{char_map.ka_gran}{char_map.virama}{char_map.ssa_gran}"
    na_h_gran=f"{char_map.na_gran}{char_map.aaMatra_gran}{char_map.visarga_gran}"
    ta_h_gran=f"{char_map.ta_gran}{char_map.aaMatra_gran}{char_map.visarga_gran}"
    na_i_h_gran=f"{char_map.na_gran}{char_map.iMatra_gran}{char_map.visarga_gran}"
    va_h_gran=f"{char_map.va_gran}{char_map.aaMatra_gran}{char_map.visarga_gran}"
    n_na_gran_count=0
    t_va_gran_count=0
    sh_ra_gran_count=0
    k_ssa_gran_count=0
    misc_count=0
    
    for word in sentence.split():
        if printDebug==True:
            print(" ".join(f"{ord(c):04x}" for c in word))
        grapheme_list=list(grapheme.graphemes(word))
        aaMatra_count += word.count(char_map.aaMatra_gran)
        aiMatra_count+=word.count(char_map.aiMatra_gran)
        eeMatra_count+=word.count(char_map.eeMatra_gran)
        ooMatra_count+=word.count(char_map.ooMatra_gran)
        auMatra_count+=word.count(char_map.auMatra_gran)
        uuMatra_count+=word.count(char_map.uuMatra_gran)
        anusvara_count+=word.count(char_map.anusvara_gran)
        au_count+=word.count(char_map.au_gran)
        au_count+=word.count(char_map.auLengthMark_gran)
        n_na_gran_count+=word.count(n_na_gran)
        t_va_gran_count+=word.count(t_va_gran)
        rVocallicMatra_count+=word.count(char_map.rVocallicMatra_gran)
        ii_count+=word.count(char_map.ii_gran)
        uMatra_count+=word.count(char_map.uMatra_gran)
        tamil_aa_count+=word.count(tamil_aa)
        sh_ra_gran_count+=word.count(sh_ra_gran)
        k_ssa_gran_count+=word.count(k_ssa_gran)
        grapheme_length+=len(grapheme_list)
        unicode_length+=len(word)
        if (
            na_h_gran in grapheme_list
            or na_i_h_gran in grapheme_list
            or ta_h_gran in grapheme_list
            or va_h_gran in grapheme_list
        ):
            misc_count+=1
    char_count = (
        aiMatra_count * 2
        + aaMatra_count
        + eeMatra_count
        + ooMatra_count * 2
        + auMatra_count * 2
        + uuMatra_count
        + au_count
        + rVocallicMatra_count
        + ii_count * 2
        + anusvara_count
        + uMatra_count
        + tamil_aa_count
        + misc_count
        + grapheme_length
        - n_na_gran_count
        - t_va_gran_count
        - (sh_ra_gran_count * 3)
        - k_ssa_gran_count
    )
    if printDebug == True:
        print(f" length of graphemes {grapheme_length} length in unicode {unicode_length} character length {char_count} aaMatra {aaMatra_count} aiMatra {aiMatra_count} eeMatra {eeMatra_count} ooMatra {ooMatra_count} auMatra {auMatra_count} uuMatra {uuMatra_count} uMatra {uMatra_count} auCount {au_count} rVocallic {rVocallicMatra_count} iicount {ii_count} anusvaracount {anusvara_count} {list(grapheme.graphemes(sentence))}")
    return char_count

def find_matching_hashmap(hashmaps, **params):
        
        for hashmap in hashmaps:
            if all(hashmap.get(k) == v for k, v in params.items()):
                return hashmap
        return None
    
def get_char_position(word_img):
    #cx, cy, cw, ch = box
    
    
    gray_line = cv2.cvtColor(word_img, cv2.COLOR_BGR2GRAY)
    _, thresh_line = cv2.threshold(gray_line, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    # Dilate to connect character components
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    dilated_line = cv2.dilate(thresh_line, kernel, iterations=1)
    # Find contours (characters)
    contours, _ = cv2.findContours(dilated_line, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    char_boxes = [cv2.boundingRect(c) for c in contours]
    sorted_chars = sorted(char_boxes, key=lambda b: b[0])  # left-to-right
      
    for (x, y, w, h) in sorted_chars:
        cv2.rectangle(word_img, (x, y), (x + w, y + h), (255, 0, 0), 5)
        pass
    #print(f" Image has {len(sorted_chars)} characters Text has {num_chars} for {image_path}")
    #cv2.imshow("Characters", word_img)
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()
    
    
    return (word_img,sorted_chars)

def extract_words_from_image(image_path, output_dir, mantra_word, swara_word):
    positions=[]
    base_name = os.path.basename(image_path)
    directory_name = os.path.dirname(image_path)
    img_names=base_name.split('_')
    if len(img_names) <3:
        print(f" This is a mantra only line and no positions")
        return False,positions
    first_image=os.path.join(directory_name, "line_" + img_names[1].split('.')[0]+ ".png")
    second_image=os.path.join(directory_name, "line_" + img_names[2].split('.')[0]+ ".png")
    if not os.path.exists(first_image) or not os.path.exists(second_image) or not os.path.exists(image_path):
        print(f"Skipping {image_path} as one of the line images {first_image} or {second_image} does not exist or the {image_path} does not exist")
        return True,positions
    swaraFlag_differ=False
    mantraFlag_differ=False
    charCountFlag_differ=False
    swaraPositionMismatch=False
    swara_list=swara_word.split()
    
    img1 = cv2.imread(first_image)
    img2 = cv2.imread(second_image)
    # Resize to same width if needed
    if img1.shape[1] != img2.shape[1]:
        width = min(img1.shape[1], img2.shape[1])
        img1 = cv2.resize(img1, (width, img1.shape[0]))
        img2 = cv2.resize(img2, (width, img2.shape[0]))
        
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5,5))
    dilated = cv2.dilate(thresh, kernel, iterations=10)
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    boxes = [cv2.boundingRect(c) for c in contours]
    # Sort by y (top to bottom), then x (left to right)
    boxes = sorted(boxes, key=lambda b: (b[0], b[1]))
    #print(f"Found {len(boxes)} words in the image.{image_path}")

    # Find contours for words (external contours)
    gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    _, thresh1 = cv2.threshold(gray1, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    kernel1 = cv2.getStructuringElement(cv2.MORPH_RECT, (5,5))
    dilated1 = cv2.dilate(thresh1, kernel1, iterations=20)
    contours, _ = cv2.findContours(dilated1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    boxes1 = [cv2.boundingRect(c) for c in contours]
    # Sort by y (top to bottom), then x (left to right)
    boxes1 = sorted(boxes1, key=lambda b: (b[0]))
    #print(f"Found {len(boxes1)} mantra words in the image.{first_image}")
    mantra_word_lengths=mantra_word.split()
    mantra_char_count=get_character_count(mantra_word)
    if (len(mantra_word_lengths) !=0 ):
        if len(boxes1) == len(mantra_word_lengths):
            pass
        else:
            
            print(f"Mantra word lengths differ: Text {len(mantra_word_lengths)} Image {len(boxes1)} for {image_path}")
            mantraFlag_differ=True

    gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
    _, thresh2 = cv2.threshold(gray2, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    kernel2 = cv2.getStructuringElement(cv2.MORPH_RECT, (5,5))
    dilated2 = cv2.dilate(thresh2, kernel2, iterations=15)
    contours2, _ = cv2.findContours(dilated2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    boxes2 = [cv2.boundingRect(c) for c in contours2]
    # Sort by y (top to bottom), then x (left to right)
    boxes2 = sorted(boxes2, key=lambda b: (b[0]))
    swara_word_lengths=swara_word.split()
    if (len(swara_word_lengths) !=0 ):
        if len(boxes2) == len(swara_word_lengths):
            pass
        else:
            print(f"Swara word lengths differ: Text {len(swara_word_lengths)} Image {len(boxes2)} for {image_path}")
            swaraFlag_differ=True

    newboxes = []
    for (x1,y1,w1,h1) in boxes2:
        newbox=[x1,y1,x1+w1,img.shape[0]]
        newboxes.append(newbox)
   
    boxed_image,char_boxes = get_char_position(img1)
    abs_diff_value=3
    abs_diff = abs(len(char_boxes) - mantra_char_count)
    if abs_diff > abs_diff_value:
        charCountFlag_differ=True
        print(f" Image has {len(char_boxes)} characters Text {mantra_word} has {mantra_char_count} for {image_path}")
        get_character_count(mantra_word,True)
    
        
        
    if charCountFlag_differ != True:
        
        positions=[]
            
        for i, (x1, y1, x2, y2) in enumerate(newboxes):
            
            for j, (bx, by, bw, bh) in enumerate(char_boxes):
                foundMatch=False
                # Check if boxes overlap horizontally
                # Calculate horizontal overlap between newbox (x1, y1, x2, y2) and boxes1 (bx, by, bx+bw, by+bh)
                overlap_start = max(x1, bx)
                overlap_end = min(x2, bx + bw)
                overlap_width = max(0, overlap_end - overlap_start)
                newbox_width = x2 - x1
                if newbox_width > 0 and (overlap_width / newbox_width) >= 0.3:
                    new_tuple=(i,j) # i is the swara and j is the mantra
                    positions.append(new_tuple)
                    foundMatch=True
                    break
            if foundMatch==False:
                if i< len(swara_list):
                    print(f"No match for swara {i} {swara_list[i]} for {image_path}")
                    swaraPositionMismatch = True
                else:
                    print(f"Swara position at {i}  is greater than known swaras {len(swara_list)} . Ignoring this swara position ")
                    

    errorFlag=False
    if charCountFlag_differ == True or mantraFlag_differ == True or swaraFlag_differ == True or swaraPositionMismatch == True : #len(char_boxes) !=mantra_char_count:
        
        boxedFileName=f"boxed_{base_name}"
        bimg_path=os.path.join(directory_name,boxedFileName)
        for (x,y,w,h) in char_boxes:
            cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),5)
        cv2.imwrite(bimg_path, img)
        for (x1, y1, x2, y2) in newboxes:
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 5)
        boxedswaraFileName=f"boxed_swara_{base_name}"
        bimg_path=os.path.join(directory_name,boxedswaraFileName)
        cv2.imwrite(bimg_path,img)
        if swaraFlag_differ == True:
            errorFlag=False
        if charCountFlag_differ == True or mantraFlag_differ == True or swaraPositionMismatch == True:
            errorFlag=True
           
    
    return errorFlag,positions

list_of_sentences=[
    #"𑌅𑌗𑍍𑌨𑌆𑌯𑌾𑌹𑍀 𑌵𑍀।𑌤𑌾𑌯𑌾𑌇𑌗𑍃𑌣𑌾𑌨𑍋𑌹𑌵𑍍𑌯𑌦𑌾 𑌤𑌾",    #27 character boxes (19,31)
    #"𑌯𑌾 𑌇। 𑌨𑍀𑌹𑍋𑌤𑌾 𑌸𑌤𑍍𑌸𑍀𑌬 𑌰𑍍𑌹𑌾 𑌇 𑌷𑍀। 𑌬 𑌰𑍍𑌹𑌾 𑌇", # 25 character boxes (19,30)
    #"𑌦𑌾 𑌤𑌾 𑌯𑍇। 𑌨𑍀𑌹𑍋𑌤𑌾 𑌸𑌾𑌤𑍍 । 𑌸𑌾 𑌇 𑌬𑌾। 𑍠 𑌹𑌾",#26 character boxes (16,27)
    #"𑌤𑍍𑌵𑌮𑌗𑍍𑌨𑍇 𑌯𑌜𑍍𑌞𑌾𑌨𑌾𑌂𑌤𑍍𑌵𑌮 𑌗𑍍𑌨𑌾 𑌇। 𑌯𑌜𑍍𑌞𑌾𑌨𑌾𑌂𑌹𑍋𑌤𑌾", #29 character boxes (22,38)
    #"𑌵𑌿 𑌶𑍍𑌪𑍇 𑌷𑌾𑌂 𑌹𑌾 𑌇 𑌤𑌾: । 𑌦𑍇 𑌵𑌾𑌇 𑌭𑌾 𑌇 𑌰𑍍𑌮𑌾 ।", #27 character boxes (17,29)
    #"𑌪𑍇𑌰𑌷𑍍𑌠𑌂 𑌵𑌾: । 𑌅 𑌤𑌾 𑌇 𑌥𑍀𑌂 । 𑌸𑍍𑌤𑍁 𑌷𑍇 𑌮𑌿𑌤𑍍𑌰𑌮𑌿𑌵",
    #"𑌅𑌶𑍍𑌪𑌨𑍍𑌨𑌤𑍍𑌵𑌾𑌵𑌾𑌰𑌵 𑌭𑌾𑌂 । 𑌵𑌨𑍍𑌦𑌧𑍍𑌯𑌾𑌅𑌗𑍍𑌨𑌿𑌨𑍍𑌨𑌮𑍋 𑌭𑌾",
    #"𑌨𑍁 𑌷𑍇। 𑌜 𑌨𑌾 𑌔 𑌹𑍋 𑌬𑌾  𑌹𑍋 𑌇 ழா।।4।।",
    #"𑌤𑍇 𑌨𑌾 𑌕𑌾 𑌮𑌾 𑌚𑍍𑌛𑌾𑌇                  𑌭𑌾। 𑌓           𑌇 ।। 1।।                (120)", #To be debugged 
    #"𑌯𑌾 𑌸𑍍𑌮𑌾 𑌹𑍋 𑌇 𑌶𑍍𑌰𑍁 𑌤𑌰𑍍𑌵𑌨𑍍𑌨𑌾𑌕𑍍𑌷𑌾𑌇𑌬𑍃",
    "𑌮𑌾𑌨𑌾𑌃 । 𑌹𑍃𑌣𑍀 𑌥𑌾 𑌆𑌤𑌿𑌥𑌿𑌂 𑌵𑌾𑌸𑍁 𑌰𑌾𑌗𑍍𑌨𑌿𑌃 ।",
    
    
    
]

 
def process_grantha_data():
    with open("output_text/line-category.json", "r", encoding="utf-8") as f:
        line_json = json.load(f)
    all_hashmaps = []
    for key, hashmap_list in line_json.items():
        if isinstance(hashmap_list, list):
            all_hashmaps.extend(hashmap_list)
    count_mantra=0
    error_count=0
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
                    count_mantra+=1
                    img_src=mantra_set.get('image-ref', '')
                    img_path = os.path.join(output_base_dir, img_src)
                    base_name = os.path.basename(img_path)
                    directory_name = os.path.dirname(img_path)
                    img_names=base_name.split('_')
                    if base_name.startswith("combined"):
                        
                        mantra_line=int(img_names[1])
                    else:
                        mantra_line=int(img_names[1].split('.')[0])
                    page_names=directory_name.split('_')
                    page_number=int(page_names[2])
                    
                    hashmap = find_matching_hashmap(all_hashmaps, page=str(page_number), line_number_in_page=mantra_line)
                    mantra_text=""        
                    if hashmap !=None:
                        mantra_text=hashmap.get('text')
                    mantra_char_count=get_character_count(mantra_text)
                    swara_list = mantra_set.get("swara", "").split()
                    error_status,positions=extract_words_from_image(img_path,output_base_dir,mantra_text,mantra_set.get("swara", ""))
                    #if len(positions) >0:
                    #    print(f"{swara_list}")
                    #    print(f"Positions {positions} {img_path}")
                    #else:
                    #    print(f"No positions for {img_path}")
                    mantra_words=mantra_set.get("mantra-words", "")
                    if error_status == True:
                        print(f" Error in swara position calculation for {i}-{j}-{k}-{l}")
                        error_count+=1
                    
                    swara_list = mantra_set.get("swara", "").split()
                    number_of_columns = len(mantra_words)
                    number_of_swaras = len(swara_list)
                    mantra_word_length=[]
                    swara_word_length=[]
    print(f" Total count {count_mantra} Error {error_count}")

if __name__ == "__main__":
    process_grantha_data()
    #for sentence in list_of_sentences:
    #    get_character_count(sentence,True)



    


    # Example usage:
    # hashmaps = [
    #     {"a": 1, "b": 2},
    #     {"a": 2, "b": 3},
    #     {"a": 1, "b": 3}
    # ]
    # result = find_matching_hashmap(hashmaps, a=1, b=3)
    # print(result)  # Output: {'a': 1, 'b': 3}
        
