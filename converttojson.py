import json
import sys
import re
import os
import cv2
import numpy as np 
import grapheme

def combine_images(images_to_combine):
    i=0
    if len(images_to_combine)<2:
        return
    if len(images_to_combine)%2 !=0: # If there are odd images skip the first one . 
        images_to_combine=images_to_combine[1:]
    while (i< len(images_to_combine)):
        first_image=images_to_combine[i]
        second_image=images_to_combine[i+1]
        img1 = cv2.imread(first_image)
        img2 = cv2.imread(second_image)
        # Resize to same width if needed
        if img1.shape[1] != img2.shape[1]:
            width = min(img1.shape[1], img2.shape[1])
            img1 = cv2.resize(img1, (width, img1.shape[0]))
            img2 = cv2.resize(img2, (width, img2.shape[0]))
        combined = np.vstack((img1, img2))
        out_name = f"combined_{os.path.basename(first_image).split('_')[1].split('.')[0]}_{os.path.basename(second_image).split('_')[1].split('.')[0]}.png"
        #print(f" Creating {out_name}")
        output_dir=os.path.dirname(first_image)
        out_path = os.path.join(output_dir, out_name)
        print(f" Creating {out_path} with {first_image} and {second_image}")
        cv2.imwrite(out_path, combined)
        i+=2
    return

def read_text_file_to_dict(file_path):
    """
    Reads a text file and returns a dictionary where the key is the page number (as string)
    and the value is a set of lines for that page.
    The text file contains lines of the pattern "XXX" where XXX is the page number.
    """
    page_dict = {}
    current_page = None
    pattern = r'__(\d+)__'
    with open(file_path, 'r', encoding='utf-8') as file:
        texts = file.read()
    for line in texts.splitlines():
        match = re.search(pattern, line)
        if match:
            current_page = match.group(1)
            if current_page not in page_dict:
                page_dict[current_page] = []
            continue
        elif current_page is not None and line.strip() :
            # If the line is not a page number, add it to the current page's set
            page_dict[current_page].append(line.strip())
        
        elif line.strip() == '':
            # Ignore empty lines
            continue
        
    return page_dict

header_pattern_1=r'^(\d+)[^=]+$' # A section header begins with this
section_end_pattern_1=r'[^=]+(=)[^=]+$'
section_end_pattern_2="19 𑌸𑌾𑌮𑌮𑍍।"  # All sections have an ending of x+y=z . But the first section just has x

header_pattern_3='……'

page_number_pattern=r'^\d+$'
# Removed a character 1 from line 10671 10620 10653 in output_grantha.txt
# Joined the separate 4(145) into previous line
# Joined (179) into previous line 
# Joined 17 ।।  (1043)
# Joined 8 (1090)
pattern_to_ignore=[ # These lines need not be merged 
        "𑌜𑍈𑌮𑌿𑌨𑍀𑌯  𑌸𑌾𑌮  𑌪𑍍𑌰𑌕𑍃𑌤𑌿  𑌗𑌾𑌨𑌮𑍍",
        "।।𑌆𑌗𑍍𑌨𑍇𑌯 𑌪𑌾𑌂:।।",
        "𑌹𑌰𑌿: ஓ𑌮𑍍",
]
pattern_to_retrofit=[
        "𑌮𑍁𑌦𑍍𑌗𑌸𑍍𑌯𑌵𑌾𑌂 𑌗𑍀𑌰𑌸𑌸𑍍𑌯 𑌦𑍇𑌵𑌾𑌨𑌾𑌂𑌵𑌾 ।।",
        #"𑌅𑌗𑍍𑌨𑍇𑌜𑌰𑌿𑌤𑌰𑍍𑌵𑌿𑌸𑍍𑌖𑌤𑌿𑌰𑍗𑌹𑍋𑌵𑌾𑌏𑌹𑌿 𑌯𑌾",
        "𑌪𑍍𑌰𑌜𑌾𑌪𑌤𑍇𑌰𑍍𑌵𑌾𑌵𑌰𑍁𑌣𑌸𑍍𑌯𑌚𑍇",
        "𑌵𑌿𑌰𑍍𑌧𑌾𑌨𑍇 𑌉𑌤𑍍𑌤𑌰𑍇।।",
        "𑌬𑍈𑌲𑍍𑌵𑌸𑍍𑌯।।",
        "𑌪𑍍𑌰𑌸𑌮𑍍𑌮𑌰𑌾𑌜𑌞𑍍𑌚𑍍𑌜𑌰𑍍𑌷𑌣𑍀𑌨𑌾𑌮𑌿𑌨𑍍𑌦𑌰𑌂𑌸𑍍𑌤𑍋𑌤𑌾𑌨𑌵𑍍𑌯𑌂",
        "𑌕𑌕𑍍𑌷𑌾𑌣𑌿𑌵𑌾 ।",
        "𑌔𑌡𑍍𑌵𑌸𑌦𑍍𑌮𑌨𑌾𑌨𑌿𑌵𑌾 ।।",
        "𑌔𑌦𑌲𑍇 𑌇𑌤𑌿𑌵𑌾 ।",
        "𑌆𑌙𑍍𑌗𑌿𑌰𑌸𑌾𑌨𑌿𑌵𑌾 ।",
        "𑌵𑌾𑌤𑍃𑌤𑍀𑌯𑌂 ।",
        "𑌇𑌨𑍍𑌦𑍇𑌰𑌾𑌦𑌧𑍀𑌚𑍋𑌅𑌸𑍍𑌥𑌭𑌿𑌰𑍀 𑌯𑌾 𑌈 𑌯𑌾 । 𑌵𑍃𑌤𑍍𑌰𑌾𑌣𑍍𑌯",
        "𑌮𑌨𑌾𑌯𑍇𑌰 ।",
        "𑌇𑌤𑌿 𑌵𑌾𑌰𑍍𑌯𑌾𑌨𑌾𑌂 𑌸𑌾𑌮𑌾𑌨𑌿 𑌚𑌤𑍍𑌵𑌾𑌰𑌿 𑌸𑌾𑌂𑌶𑌾𑌨𑌾𑌨𑌿𑌵𑌾।।",
        "𑌵𑌜𑍍𑌰𑌸𑍍𑌯𑌵𑌾𑌂𑌗𑍀𑌰𑌸𑌸𑍍𑌯।",
        "𑌕𑌶𑍍𑌯𑌪𑌸𑍍𑌯𑌵𑌾𑌨𑍀𑌤𑍗𑌚𑍗 ।",
        "𑌪𑍍𑌰𑌿𑌯𑌾𑌣𑌿।",
        "𑌆𑌕𑍂𑌪𑌾𑌰𑌾𑌣𑌿𑌵𑌾।",
        "𑌦𑍇𑌵𑌪𑍁𑌰𑍇।",
        "𑌸𑌾𑌮𑌮𑍈𑌧𑌾𑌤𑌿𑌥𑌂𑌵𑌾 ।",
        "𑌸𑌾𑌮𑌵𑌾",
        "𑌮𑌹𑍋𑌵𑌿𑌶𑍀𑌯𑍇 ।",
        "𑌗𑍗𑌤𑌮𑌸𑍍𑌯𑌵𑌾𑌪𑍍𑌰𑌤𑍋𑌦𑍗 ।",
        "𑌵𑌾𑌰𑌾𑌹𑌾𑌣𑌿𑌵𑌾…",
        "𑌸𑍁𑌰𑌸𑍇𑌚𑍇।।",
        "𑌸𑌂𑌪𑌚𑌾  𑌤𑍃𑌤𑍀𑌯𑌂 ।",
        "𑌸𑌾𑌮𑌾𑌨𑌿 𑌤𑍍𑌰𑍀𑌣𑌿  𑌶𑌾𑌰𑍍𑌙𑍍𑌗𑌾𑌣𑌿𑌵𑌾 ।",
        "𑌨𑌿𑌧 𑌨𑌾𑌨𑌿𑌵𑌾 𑌤𑍍𑌵𑌾𑌷𑍍𑌟𑍍𑌰𑍀𑌸𑌾𑌮𑌾𑌨𑍀 ।",
        "𑌤𑍃𑌤𑍀𑌯𑍇𑌤𑌰𑌾𑌣𑌿𑌪 𑌤𑍍𑌯𑌰𑍍𑌥𑌃 ।",
        "𑌹𑌾𑌬𑍁𑌜𑌨  𑌡𑌾𑌬𑍁𑌜𑌨  𑌡𑌾𑌬𑍁𑌜𑌨 𑌜𑍍𑌜𑌨  𑌡𑌾𑌬𑍁𑌜𑌨",
       
        
]

super_section_titles_start=[
"_𑌆𑌗𑍍𑌨𑍇𑌯𑌃 𑌪𑌾𑌂𑌃",
"।। 𑌤𑌚𑌪𑌾𑌂𑌃 ।।",
"।। 𑌬𑍃𑌹𑌤𑌿 𑌪𑌾𑌂𑌃 ।।",
"।।𑌅𑌸𑌾𑌵𑌿 𑌪𑌾𑌂𑌃।।",
"।। 𑌐𑌨𑍍𑌦𑌰 𑌪𑌾𑌂𑌃 ।।",
]
super_section_titles_end=[
"।।𑌆𑌗𑍍𑌨𑍇𑌯𑌃 𑌪𑌾𑌂𑌃 𑌸𑌮𑌾𑌪𑍍𑌤𑌃 ।।"  ,
"।। 𑌇𑌤𑌿 𑌤𑌚𑌪𑌾𑌂𑌃 𑌸𑌮𑌾𑌪𑍍𑌤𑌃 ।।" ,
"।। 𑌇𑌤𑌿 𑌬𑍍𑌰𑌹𑌤𑍀 𑌪𑌾𑌂𑌃 𑌸𑌮𑌾𑌪𑍍𑌤𑌃 ।।" ,
"।।𑌅𑌸𑌾𑌵𑌿 𑌪𑌾𑌂𑌃 𑌸𑌮𑌾𑌪𑍍𑌤𑌃 ।।" ,
"𑌐𑌨𑍍𑌦𑌰 𑌪𑌾𑌂 𑌸𑌮𑌾𑌪𑍍𑌤𑌃"
]
textfile = sys.argv[1]
text_dict= read_text_file_to_dict(textfile)

my_json_header={}
supersections={}
sections={}
supersection_number=1
section_number=1
subsections={}
subsection_markers={}
current_subsection_text=[]
subsection_lineslist=[]
current_header=None
out_json={}
page_json={}
subsection_number=1
#page_json["page"]=1
line_number=1
line_json={}
myLine_list=[]
line_category="mantra"
supersection_title=super_section_titles_start[0]
in_section=False
for page in text_dict.keys():
    lines = text_dict[page]
    #print(f"Processing page {page} with {len(lines)} lines")
    line_number_in_page=1
    for line in lines:
        #print(f"Processing line {line_number} on page {page} {line}")
        line = line.strip()
        line_json={}
        line_json["line_number"]=line_number
        line_json["page"]=page
        line_json["text"]=line
        line_json["line_number_in_page"]=line_number_in_page
        if re.match(page_number_pattern, line):
            #print(f" Page number Appending {line} to myLine_list of length {len(myLine_list)}")
            
            line_json["category"]="page_number"
            myLine_list.append(line_json)
            #continue
        elif line in pattern_to_ignore :
            #print(f"Generic  Appending {line} to myLine_list of length {len(myLine_list)}")
            
            line_json["category"]="generic"
            myLine_list.append(line_json)
            #continue
        #elif line in pattern_to_retrofit :
        #    line_json["category"]="toBeAddedLater"
        #    myLine_list.append(line_json)

        elif re.match(section_end_pattern_1, line) or (line==section_end_pattern_2):
            #print(f"Count  Appending {line} to myLine_list of length {len(myLine_list)}")
            #print(f" Matched a new ending ${line}")
            line_json["category"]="count"
            if line == section_end_pattern_2:
                print(f" Matched an end of section without '+' {line}")
                line_json['text']="0+19=19"
            myLine_list.append(line_json)
            if in_section == True:
                    my_json=subsection_markers["subsection_"+str(subsection_number)]
                    my_json["page_end"]=page
                    my_json["line_end"]=line_number-1
                    subsection_markers["subsection_"+str(subsection_number)]=my_json
                    subsections["subsection_"+str(subsection_number)] = {"header":my_json_header, "lines":subsection_lineslist}
                    page_json["subsection_"+str(subsection_number)] = myLine_list
                    #print(f" Creating page_json of {section_number} with myLine_list of length {len(myLine_list)}")
                    current_subsection_text = []
                    myLine_list = []
                    subsection_lineslist=[]
                    sections["section_"+str(section_number)] = {"subsections": subsections, "count": line_json}
                    #page_json[section_number] = sections
                    section_number+=1
                    subsection_number+=1
                    subsections={}
                    
            
            in_section=False
        
        elif header_pattern_3 in line:
        #elif re.match(header_pattern_3,line):
            #print(f"Section end  Appending {line} to myLine_list of length {len(myLine_list)}")
            line_json["category"]="section-end"
            myLine_list.append(line_json)
            in_section=False
            
        elif re.match(header_pattern_1, line) :
            #print(f" Matched header at {line}")
            if current_header is not None:
                if in_section == True:
                    try:
                        my_json = subsection_markers["subsection_"+str(subsection_number)]
                    except KeyError:
                        print(f" Key error for subsection {subsection_number} in page {page} encountered {line}")
                        my_json = {}
                    my_json["page_end"]=page
                    my_json["line_end"]=line_number-1
                    subsection_markers["subsection_"+str(subsection_number)]=my_json
                    #subsections[subsection_number] = subsection_lineslist
                    subsections["subsection_"+str(subsection_number)] = {"header":my_json_header, "lines":subsection_lineslist}
                    page_json["subsection_"+str(subsection_number)] = myLine_list
                    #print(f" Creating page_json of {section_number} with myLine_list of length {len(myLine_list)}")
                    current_subsection_text = []
                    myLine_list = []
                    subsection_lineslist=[]
                    subsection_number+=1
                in_section = True
            else:
                print(f" current header is None for {page} encountering {line}")
                current_subsection_text = []
                myLine_list = []
                subsection_lineslist=[]
                in_section = True

            # Replace the "||" and the "|" for header    
            head_text=line_json['text']
            head_text=head_text.replace("।।"," ") 
            head_text=head_text.replace("।"," ")
            line_json['text']=head_text 

            line_category="mantra" # This is for the next line
            current_header = line
            
            line_json["category"]="header"
        
            myLine_list.append(line_json)
            my_json_header=line_json
            #subsection_lineslist.append(line_json)
            #print(f"header  Appending {line} to myLine_list of length {len(myLine_list)}")
            #continue
        
        else:
            #print(f"{line_category}  Appending {line} to myLine_list of length {len(myLine_list)}")
            in_section=True
            current_subsection_text.append(line)
            found_super_section_end=False
            found_super_section_start=False
            for sub_string in super_section_titles_start:
                if  sub_string in line:
                        line_json["category"]="super-section-start"
                        supersection_title = line
                        #print(f" Start of super section {line_json}")
                        found_super_section_start=True
                        supersection_number += 1
                        break
            if found_super_section_start !=True:
                for sub_string in super_section_titles_end:
                    if  sub_string in line:
                        line_json["category"]="super-section-end"
                        current_header = None
                        #print(f" End of super section {line_json} with supersection_title {supersection_title}")
                        #sections[section_number] = {"subsections": subsections, "count": line_json}
                        # Because we found a supersection it means the previous subsection should be completed
                        #my_json["page_end"]=page
                        #my_json["line_end"]=line_number-1
                        #subsection_markers["subsection_"+str(subsection_number)]=my_json
                        #subsections[subsection_number] = subsection_lineslist
                        #subsections["subsection_"+str(subsection_number)] = {"header":my_json_header, "lines":subsection_lineslist}
                        #page_json["subsection_"+str(subsection_number)] = myLine_list
                        #print(f" Creating page_json of {section_number} with myLine_list of length {len(myLine_list)}")
                        
                        #sections["section_"+str(section_number)] = {"subsections": subsections, "count": line_json}
                    #page_json[section_number] = sections
                        current_subsection_text = []
                        myLine_list = []
                        subsection_lineslist=[]
                        subsection_number+=1
                        section_number+=1
                        
                        
                        subsections={}
                        supersections["supersection_"+str(supersection_number)] = {"supersection_title":supersection_title, "sections":sections}
                        sections={}
                        
                        found_super_section_end=True
                        break
            if found_super_section_end == False and found_super_section_start == False:   
                line_json["category"]=line_category
            if line_category == "mantra" and current_header !=None:
                if line in pattern_to_retrofit:
                    print(f" Matching {line} in pattern_to_retrofit")
                    line_category = "mantra"  # Making the next line also as mantra
                else:
                    line_category = "swara"
            elif line_category == "swara":
                line_category = "mantra"
            myLine_list.append(line_json)
            subsection_lineslist.append(line_json)
            
        if len(current_subsection_text)==0 and in_section == True:
                subsection_markers["subsection_"+str(subsection_number)]={"page_start":page,"line_start":line_number}
                line_start=f"section_start=Page-{page} Line--{line_number}"
                current_subsection_text.append(line_start)
        line_number+=1
        line_number_in_page+=1
        
supersections["supersection_"+str(supersection_number)] = {"supersection_title":supersection_title, "sections":sections}        
output_dir = "output_text"        
print(f" Number of sections: {len(subsections)} {len(subsection_markers)}")
final_json={"supersection":{}}
for key in supersections.keys():
    temp_x=supersections[key]['supersection_title']
    temp_x=temp_x.replace("_","")
    supersections[key]['supersection_title']=temp_x
    # The above hack has to be done since the super section and start were the same
    # and hence introduced a _ to differentiate. Removing it here to make sure the final copy is fine
    print(f" Supersection: {supersections[key]['supersection_title']} contains {len(supersections[key]['sections'])} sections")
    final_json["supersection"][key]={}
    final_json["supersection"][key]['supersection_title']=supersections[key]['supersection_title']
    final_json["supersection"][key]['sections']={}
    for key1 in supersections[key]['sections'].keys():
        print(f"  Section: {supersections[key]['sections'][key1]['count']['text']} contains {len(supersections[key]['sections'][key1]['subsections'])} subsections")
        final_json["supersection"][key]['sections'][key1]={}
        # Extract all numbers using re pattern match from count text
        #pattern= r'(\d+)\+(\d+)=(\d+)'
        # Matches patterns like (247+15=262) with any characters before/after, but captures the numbers and operators
        pattern = r'.*?(\d+)\s*\+\s*(\d+)\s*=\s*(\d+).*'
        
        match = re.search(pattern, supersections[key]['sections'][key1]['count']['text'])
        if match:
            #print(f"Matched pattern: {match.groups()}")
            #count_json
            final_json["supersection"][key]['sections'][key1]['count']={}
            final_json["supersection"][key]['sections'][key1]['count']['prev_count']=match.group(1).strip()
            final_json["supersection"][key]['sections'][key1]['count']['current_count']=match.group(2).strip()
            final_json["supersection"][key]['sections'][key1]['count']['total_count']=match.group(3).strip()

        #final_json[key]['sections'][key1]['count']=supersections[key]['sections'][key1]['count']['text']
        final_json["supersection"][key]['sections'][key1]['subsections']={}
        
        for key2 in supersections[key]['sections'][key1]['subsections'].keys():
            print(f"    Subsection: {supersections[key]['sections'][key1]['subsections'][key2]['header']['text']}")
            final_json["supersection"][key]['sections'][key1]['subsections'][key2]={}
            lines= supersections[key]['sections'][key1]['subsections'][key2]['lines']
            category=""
            i=0
            #if len(lines) %2 !=0:
            #    print(f" Skipping this subsection since odd number of lines and swaras \n {lines} ")
            #    continue
            mantra_sets=[]
            print(f" length of lines {len(lines)}")
            while (i < len(lines)):
                mantra_line = lines[i]
                try:
                    swara_line = lines[i+1]
                    print(f" line {i} {mantra_line['category']} line {i+1} {swara_line['category']}")
                except IndexError:
                    print(f"line {i} {mantra_line['category']}")
                    swara_line=None
                
                if swara_line==None or mantra_line["category"] == swara_line["category"]:
                    print(f" This is NOT an error. Accomodating mantras without swaras ")
                    mantra=mantra_line["text"]
                    mantra_words=mantra.split()
                    mantra_set={}
                    instance=0
                    mantra_set["mantra-words"]=[]
                    for word in mantra_words:
                        word_grapheme_length=grapheme.length(word)
                        mantra_word={}
                        pattern=r'\((\d+)\)'
                        pattern1=r'।।(\d+)।।'  #।।2।।
                        match=re.search(pattern,word)
                        if match:
                            instance=match.group(1)
                            word=re.sub(pattern,"",word)
                        
                        match1=re.search(pattern1,word)
                        if match1:
                            #instance=match.group(1)
                            word=re.sub(pattern1,"",word)
                        mantra_word["word"]=word
                        mantra_word["swara_positions"]=[{"position":1}]
                        mantra_set["mantra-words"].append(mantra_word)
                    path=f"lines/page_{mantra_line['page']}/line_{mantra_line['line_number_in_page']:02d}.png"
                    mantra_set["image-ref"]=path
                    if instance!=0:
                        mantra_set["instance"]=instance
                    mantra_sets.append(mantra_set)
                    i=i+1
                else:
                    
                    if mantra_line["page"] != swara_line["page"]:
                        print(f" Mantra and Swara are in 2 different pages {mantra_line['page']} line {mantra_line['line_number_in_page']:02d} and {swara_line['page']} line {swara_line['line_number_in_page']:02d}")
                        #combine_images([f"lines/page_{mantra['page']}/line_{mantra['line_number_in_page']:02d}.png", f"lines/page_{swara['page']}/line_{swara['line_number_in_page']:02d}.png"])
                    mantra=mantra_line["text"]
                    swara=swara_line["text"]
                    swara_grapheme_length=grapheme.length(swara)
                    mantra_words=mantra.split()
                    # need to divide swara_grapheme_length swaras equally among mantra_words
                    mantra_set={}
                    instance=0
                    mantra_set["mantra-words"]=[]
                    for word in mantra_words:
                        word_grapheme_length=grapheme.length(word)
                        mantra_word={}
                        pattern=r'\((\d+)\)'
                        pattern1=r'।।(\d+)।।'  #।।2।।
                        match=re.search(pattern,word)
                        if match:
                            instance=match.group(1)
                            word=re.sub(pattern,"",word)
                        
                        match1=re.search(pattern1,word)
                        if match1:
                            #instance=match.group(1)
                            word=re.sub(pattern1,"",word)
                        mantra_word["word"]=word
                        mantra_word["swara_positions"]=[{"position":1}]
                        mantra_set["mantra-words"].append(mantra_word)
                    match=re.search(pattern,swara)
                    if match:
                        instance=match.group(1)
                        swara=re.sub(pattern,"",swara)
                    match1=re.search(pattern1,swara)
                    if match1:
                        #instance=match.group(1)
                        swara=re.sub(pattern1,"",swara)
                    swara_graphemes=swara.split()
                    mantra_set["swara"] = " ".join(c for c in swara_graphemes)
                    #mantra_sets.append(mantra_set)

                    mantra_grapheme_length=grapheme.length(mantra)
                    path=f"lines/page_{mantra_line['page']}/combined_{mantra_line['line_number_in_page']:02d}_{swara_line['line_number_in_page']:02d}.png"
                    mantra_set["image-ref"]=path
                    if instance!=0:
                        mantra_set["instance"]=instance
                    mantra_sets.append(mantra_set)
                    if os.path.exists(os.path.join("output_text", path)):
                        #print(f"File exists: {path}")
                        pass
                    else:
                        #print(f"File does not exist: {path}")
                        if os.path.exists(f"output_text/lines/page_{mantra_line['page']}/line_{mantra_line['line_number_in_page']:02d}.png") and os.path.exists(f"output_text/lines/page_{swara_line['page']}/line_{swara_line['line_number_in_page']:02d}.png"):
                            combine_images([f"output_text/lines/page_{mantra_line['page']}/line_{mantra_line['line_number_in_page']:02d}.png", f"output_text/lines/page_{swara_line['page']}/line_{swara_line['line_number_in_page']:02d}.png"])
                        else:
                            if os.path.exists(f"output_text/lines/page_{mantra_line['page']}/line_{mantra_line['line_number_in_page']:02d}.png"):
                                #print(f"File exists: lines/page_{mantra['page']}/line_{mantra['line_number_in_page']:02d}.png")
                                pass
                            else:
                                print(f"1 File of line does not exist: output_text/lines/page_{mantra_line['page']}/line_{mantra_line['line_number_in_page']:02d}.png")
                            if os.path.exists(f"output_text/lines/page_{swara_line['page']}/line_{swara_line['line_number_in_page']:02d}.png"):
                                #print(f"File exists: lines/page_{swara['page']}/line_{swara['line_number_in_page']:02d}.png")
                                pass
                            else:
                                print(f"2 File of line does not exist: output_text/lines/page_{swara_line['page']}/line_{swara_line['line_number_in_page']:02d}.png")
                                pass
                        pass
                    i += 2
            header_json=supersections[key]['sections'][key1]['subsections'][key2]['header']
            new_header_json={}
            final_json["supersection"][key]['sections'][key1]['subsections'][key2]['mantra_sets']=mantra_sets
            final_json["supersection"][key]['sections'][key1]['subsections'][key2]['header']={}
            pattern_header=r'(\d+)(.*)'
            match_header=re.search(pattern_header,header_json['text'])
            if match_header:
                new_header_json["header_number"]=match_header.group(1).strip()
                new_header_json["header"]=match_header.group(2).strip()
            else:
                new_header_json["header"]=header_json['text']
            new_header_json["image-ref"]=f"lines/page_{header_json['page']}/line_{header_json['line_number_in_page']:02d}.png"
            final_json["supersection"][key]['sections'][key1]['subsections'][key2]['header']=new_header_json
        
output_file = f"{output_dir}/line-category.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(page_json, f, ensure_ascii=False, indent=2)

output_file = f"{output_dir}/section_markers.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(subsection_markers, f, ensure_ascii=False, indent=2)
    
output_file = f"{output_dir}/sections.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(supersections, f, ensure_ascii=False, indent=2)
    
output_file = f"{output_dir}/final-Grantha.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(final_json, f, ensure_ascii=False, indent=2)
    


