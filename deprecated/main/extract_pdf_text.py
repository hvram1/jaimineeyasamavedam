import pypdf
import re
import os
from char_map import char_map,missing_maps_list,ascii_combination_letters,equivalent_letters
import unicodedata
virama="\U0001134D"
prefix_html_head="""
    
    <!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8" />
    <title>Unique Character Mapping</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Grantha&family=Noto+Serif+Grantha&display=swap" rel="stylesheet">
</head>
<style>
.k1 {
    font-family: "Krishna Vedic", serif;
    font-size: 14pt;font-color: "blue";
}
.n1 {
    font-family: "Noto Sans Grantha", sans-serif;
    font-size: 14pt; font-color: "green";
}
.n2 {
    font-family: "Noto Serif Grantha", serif;
    font-size: 14pt; font-color: "red";
}
</style>"""

def write_html_table(outfile, uniq_chars,char_map):

    prefix_html_body="""
<body>
    <p> Some chracters are better in Noto Sans Grantha while some others are better in Noto Serif Grantha. 
    Take a look at the row where ASCII value is 297 
    </p>
    <table border="1" cellpadding="8" cellspacing="0">
        <tr>
            <th>Krishna Vedic</th>
            <th>Noto Sans Grantha</th>
            <th>Noto Serif Grantha</th>
            <th>ASCII Val   ue</th>
            <th>Unicode Value</th>
            <th>Unicode Name</th>
        </tr>
    """
    suffix_html_body="""
    </table>
</body>
</html>
"""
    content_html=""
    for key in uniq_chars.keys():
        current_ascii_index=int(hex(ord(key)),16)
        value=char_map.get(current_ascii_index)
        #print(f"key is {key} hex is {hex(ord(key))}")
        unicode_code_point = ""
        if value:
            # If value is a string, print all code points (handles multi-char values)
            unicode_code_point = " ".join([f"U+{ord(ch):04X}" for ch in str(value)])
        unicode_name = ""
        try:
            if value and len(str(value)) == 1:
                unicode_name = unicodedata.name(str(value))
            elif value:
                unicode_name = " / ".join([unicodedata.name(ch) for ch in str(value)])
        except Exception:
            unicode_name = ""
        row = f"<tr><td class=\"k1\">{key}</td><td class=\"n1\">{value}</td> <td class=\"n2\">{value}</td><td>{hex(current_ascii_index)}</td><td>{unicode_code_point}</td><td>{unicode_name}</td></tr>\n"
        content_html+=row
    
    with open(outfile,"w",encoding="utf-8") as f:
        f.write(prefix_html_head)
        f.write(prefix_html_body)
        f.write(content_html)
        f.write(suffix_html_body)
        
def extract_text_from_pdf(pdf_path, output_file):
    # Open the PDF file
    with open(pdf_path, 'rb') as pdf_file:
        reader = pypdf.PdfReader(pdf_file)
        texts=""
        # Iterate through each page
        for page_number, page in enumerate(reader.pages, start=1):
            # Extract text from the page
            text = page.extract_text(extraction_mode="layout" , layout_mode_space_vertically=False)
            fonts = set()
            if '/Resources' in page and '/Font' in page['/Resources']:
                font_dict = page['/Resources']['/Font']
                for font_key in font_dict.keys():
                    font = font_dict[font_key]
                    if '/BaseFont' in font:
                        fonts.add(font['/BaseFont'])
                        
            #print(f"Page {page_number} uses fonts: {fonts}")
            texts += f"\n\n __{page_number}__:\n\n {text} \n\n"
            #texts += text
            # Save the text in Unicode format to a file
        #output_file = f"{output_dir}/output-layout.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(texts)
        print(f"Text extracted and saved to {output_file}")
        return texts
def process_missing_maps(texts):
    newstring=texts
    
    for item in missing_maps_list:
        #print(f"Missing Maps Item to match {hex(ord(item))}")
        pattern=f"\"{item}\""
        matches = re.finditer(item,newstring)
        
        for match in matches:
            end,newstart=match.span()
            prefix_text=newstring[:end]
            list_lines=prefix_text.splitlines()

            suffix_text=newstring[end:]
            list_lines_1=suffix_text.splitlines()
            err=(f" Pattern {item} occured in {len(list_lines)}th line {list_lines[-1]}{list_lines_1[0]}")
            line=list_lines[-1]+list_lines_1[0]
            err_line_inhex=""
            for current_ascii_character in line:
                err_line_inhex+=f"{hex(ord(current_ascii_character))} "
            print(f"{err}")
            print(f"{err_line_inhex}")
            break
    
def process_mapping_table(texts):
    uniq_chars={}
    for c in texts:
        #current_ascii_index=int(hex(ord(c)),16)
        if uniq_chars.get(c) == None:
                uniq_chars[c]=1
    outfile = f"output_text/mapping.html"
    write_html_table(outfile, uniq_chars,char_map)
    
def process_text(texts):
    
       
    # list_texts=list(texts)
    # print(f" len of the string {len(texts)} Length of the list {len(list_texts)}")
    #lines = texts.splitlines()
    #print(f" len of the string {len(texts)} Number of lines {len(lines)}")
    
    #pattern1="\u00c0\u00eb"
    #pattern1_replace="\u00eb\u00c0"
    #pattern2="\u00c7\u00eb"
    #pattern2_replace="\u00eb\u00c7"
    pattern3="\u00cd\u00cd"
    pattern3_replace="\u00ce"
    #pattern4="\u00c0\u00f1"
    #pattern4_replace="\u00f1\u00c0"
    #pattern5="\u00c2\u00e8"
    #pattern5_replace="\u00e8\u00c2"
    pattern6="\u00cd\u0053\u00dc\u00c0"
    pattern6_replace="\u00cd\u0053\u00c0\u00dc"
    #pattern6_replace="\U00011337\U0001134D\U00011320\U0001134B"
    #pattern7="\u0107\u00ec"
    #pattern7_replace="\U00011326\U0001134D\U00011330\U00011340"
    pattern8="\u0024"  # To compensate for some error in extraction 
    #pattern8_replace="\013e"
    pattern8_replace = "\U00011328\U0001134D\U00011335"
    pattern9="\u006f\u00c0"
    pattern9_replace="\u006f"
    #texts=texts.replace(pattern1,pattern1_replace)
    #texts=texts.replace(pattern2,pattern2_replace)
    texts=texts.replace(pattern3,pattern3_replace)
    #texts=texts.replace(pattern4,pattern4_replace)
    #texts=texts.replace(pattern5,pattern5_replace)
    texts=texts.replace(pattern6,pattern6_replace)
    #texts=texts.replace(pattern7,pattern7_replace)
    texts=texts.replace(pattern8,pattern8_replace)
    texts=texts.replace(pattern9,pattern9_replace)
    
    # c2 = c1
    # c5 = c4
    # 0x0103 = 0x74 + c4 ( long vowel)
    # 0x0104 = 0x56 + c1 ( short vowel )
    # 0x0105 = 0x56 + c4 ( long vowel )
    # 0x0106 = 0x64 + c1 ( short vowel )
    # 0x0107 = 0x64 + c4 ( long vowel )
    # 0x0108 = 0x71 + c1 ( short vowel )
    # 0x0109 = 0x71 + c4 ( long vowel )
    # 0x010a = 0x6e + c4 ( long vowel )
    # 0x010c = 0x53 + c1 ( short vowel)
    # = texts.count(pattern1)
    #occurence2 = texts.count(pattern2)
    #occurence3 = texts.count(pattern3)
    #print(f" Length of char_map is {len(char_map)}, missing maps {len(missing_maps_list)}")
    #print(f" Occurence of {pattern1} = {occurence1} , Occurence of {pattern2}= {occurence2}, Occurence of {pattern3}={occurence3}")
    patterns_list= [
    "(\u00CD)([\u0000-\u0fff])(\u00C0)",
    "(\u00CD)([\u0000-\u0fff])(\u00CF)",
    "(\u00CD)([\u0000-\u0fff])([\u012C\u012E\u00d2\u00d8\u00dc\u00dd\u00df\u00e0\u00e1\u00e4\u00e5\u00e9\u00eb\u00ec\u00ed\u00ee\u00f1\u00f2])",
    "(\u00CE)([\u0000-\u0fff])([\u00e0\u00e1\u00e4])",
    #"(\u00CE)([\u0000-\u0fff])(\u00C0)",
    #"(\u00CE)([\u0000-\u0fff])(\u00CF)"
    ]
    newstring=texts
    
    
    for pattern in patterns_list:
        print(f"Processing patternset 1 (E,ai,jE and jai with vosubscripts): {pattern} with string of length {len(newstring)}")
        matches = re.finditer(pattern,newstring)
        my_newstring=""
        start=0
        for match in matches:
            end,newstart=match.span()

            my_newstring+=newstring[start:end]
            first_char=int(hex(ord(newstring[match.start()])),16)
            second_char=int(hex(ord(newstring[match.start()+1])),16)
            third_char=int(hex(ord(newstring[match.end()-1])),16)
            print(f"text is {hex(ord(newstring[match.start()]))} first_char {hex(first_char)} second_char {hex(second_char)} third_char {hex(third_char)}")
            first_value=char_map.get(first_char)

            second_value=char_map.get(second_char)
            if third_char == 0xc0:
                third_value="\U0001134B"
            elif third_char == 0xcf:
                third_value="\U0001134C"
            else:
                third_value=char_map.get(third_char)
                #third_value=f"{virama}{third_value}"
            if second_value == None  or third_value == None:
                print(f"Warning: No mapping found for {hex(first_char)} or {hex(second_char)} or {hex(third_char)} at {match.span()}")
            else:
                #if virama in third_value :
                #    temp_string=f"{second_value}{third_value}{first_value}"
                #else:
                    
                    #temp_string=f"{second_value}{virama}{third_value}{first_value}"
                if third_char == 0xc0 or third_char == 0xcf:
                    temp_string=f"{second_value}{third_value}"
                elif third_char == 0xec:
                    temp_string=f"{second_value}{virama}{third_value}{first_value}"
                elif third_char == 0xeb:
                    temp_string=f"{second_value}{virama}{third_value}{first_value}"
                else:
                    temp_string=f"{second_value}{third_value}{first_value}"
                print(f"replaced {newstring[end:newstart]} with {temp_string}")
                my_newstring+=temp_string
            start=newstart
        remaining_string=newstring[start:]
        newstring=my_newstring+remaining_string
    
    patterns_list= [
    "([\u0000-\u0fff])([\u00d5\u00d6\u00df\u00e0\u00ee])([\u00c0\u00c1\u00c2\u00c4\u00c5\u00c7\u00c8\u00cf])(\u00EB)",
    
    
    ]
    for pattern in patterns_list:
        print(f"Processing patternset 2 (ravattu with vowel): {pattern} with string of length {len(newstring)}")
        matches = re.finditer(pattern,newstring)
        my_newstring=""
        start=0
        for match in matches:
            end,newstart=match.span()

            my_newstring+=newstring[start:end]
            first_char=int(hex(ord(newstring[match.start()])),16)
            second_char=int(hex(ord(newstring[match.start()+1])),16)
            third_char=int(hex(ord(newstring[match.start()+2])),16)
            fourth_char=int(hex(ord(newstring[match.end()-1])),16)
            print(f"text is {hex(ord(newstring[match.start()]))} first_char {hex(first_char)} second_char {hex(second_char)} third_char {hex(third_char)} fourth_char {hex(fourth_char)}")
            first_value=char_map.get(first_char)

            second_value=char_map.get(second_char)
            
            third_value=char_map.get(third_char)

            fourth_value=char_map.get(fourth_char)
            if second_value == None  or third_value == None or fourth_value == None or first_value == None:
                print(f"Warning: No mapping found for {hex(first_char)} or {hex(second_char)} or {hex(third_char)} or {hex(fourth_char)} at {match.span()}")
            else:
                #if virama in third_value :
                #    temp_string=f"{second_value}{third_value}{first_value}"
                #else:
                    
                    #temp_string=f"{second_value}{virama}{third_value}{first_value}"
                temp_string=f"{first_value}{second_value}{fourth_value}{third_value}"
                print(f"replaced {newstring[end:newstart]} with {temp_string}")
                my_newstring+=temp_string
            start=newstart
        remaining_string=newstring[start:]
        newstring=my_newstring+remaining_string


    patterns_list= [
    "([\u0000-\u0fff])([\u00e0])(\u00EB)",
    
    
    ]
    for pattern in patterns_list:
        print(f"Processing patternset 3 (ravattu with subscript): {pattern} with string of length {len(newstring)}")
        matches = re.finditer(pattern,newstring)
        my_newstring=""
        start=0
        for match in matches:
            end,newstart=match.span()

            my_newstring+=newstring[start:end]
            first_char=int(hex(ord(newstring[match.start()])),16)
            second_char=int(hex(ord(newstring[match.start()+1])),16)
            third_char=int(hex(ord(newstring[match.end()-1])),16)
            print(f"text is {hex(ord(newstring[match.start()]))} first_char {hex(first_char)} second_char {hex(second_char)} third_char {hex(third_char)}")
            first_value=char_map.get(first_char)

            second_value=char_map.get(second_char)
            
            third_value=char_map.get(third_char)
            if second_value == None  or third_value == None:
                print(f"Warning: No mapping found for {hex(first_char)} or {hex(second_char)} or {hex(third_char)} at {match.span()}")
            else:
                #if virama in third_value :
                #    temp_string=f"{second_value}{third_value}{first_value}"
                #else:
                    
                    #temp_string=f"{second_value}{virama}{third_value}{first_value}"
                temp_string=f"{third_value}{virama}{first_value}{second_value}"
                print(f"replaced {newstring[end:newstart]} with {temp_string}")
                my_newstring+=temp_string
            start=newstart
        remaining_string=newstring[start:]
        newstring=my_newstring+remaining_string

    patterns_list= [
        "([\u00ce\u00cd])([\u0000-\u0fff])",
        
        #"(\u00cd)([\u0000-\u0fff])",
        
    ]

    for pattern in patterns_list:
        print(f"Processing patternset 4 (jE and jai ): {pattern} with string of length {len(newstring)}")
        matches = re.finditer(pattern,newstring)
        my_newstring=""
        start=0
        for match in matches:
            end,newstart=match.span()

            my_newstring+=newstring[start:end]
            first_char=int(hex(ord(newstring[match.start()])),16)
            second_char=int(hex(ord(newstring[match.end()-1])),16)

            print(f"text is {hex(ord(newstring[match.start()]))} first_char {hex(first_char)} second_char {hex(second_char)} at {match.span()}")
            first_value=char_map.get(first_char)

            second_value=char_map.get(second_char)

            if second_value == None or first_value == None:
                print(f"Warning: No mapping found for {hex(first_char)} or {hex(second_char)}  at {match.span()}")
                start,end=match.span()
                prefix_text=newstring[:end]
                list_lines=prefix_text.splitlines()

                suffix_text=newstring[end:]
                list_lines_1=suffix_text.splitlines()
                err=(f" Error occured in {len(list_lines)}th line {list_lines[-1]}{list_lines_1[0]}")
                line=list_lines[-1]+list_lines_1[0]
                err_line_inhex=""
                for current_ascii_character in line:
                    err_line_inhex+=f"{hex(ord(current_ascii_character))} "
                print(f"{err}")
                print(f"{err_line_inhex}")
            else:
                temp_string=f"{second_value}{first_value}"
                print(f"replaced {newstring[end:newstart]} with {temp_string}")
                my_newstring+=temp_string
            start=newstart
        remaining_string=newstring[start:]
        newstring=my_newstring+remaining_string
        
    patterns_list= [
        "([\u0000-\uffff])([\u00c0\u00c1\u00c2\u00c4\u00c5\u00c7\u00c8])([\u00d8\u00dc\u00e8\u00ee\u00f1\u00f2])",
 
    ]
    

    for pattern in patterns_list:
        print(f"Processing patternset 5 ( consonant vowel with subscript ): {pattern} with string of length {len(newstring)}")
        matches = re.finditer(pattern,newstring)
        my_newstring=""
        start=0
        for match in matches:
            end,newstart=match.span()

            my_newstring+=newstring[start:end]
            first_char=int(hex(ord(newstring[match.start()])),16)
            second_char=int(hex(ord(newstring[match.start()+1])),16)
            third_char=int(hex(ord(newstring[match.end()-1])),16)

            print(f"text is {hex(ord(newstring[match.start()]))} first_char {hex(first_char)} second_char {hex(second_char)} third_char {hex(third_char)} at {match.span()}")
            first_value=char_map.get(first_char)

            second_value=char_map.get(second_char)

            third_value=char_map.get(third_char)

            if second_value == None or first_value == None or third_value == None:
                print(f"Warning: No mapping found for {hex(first_char)} or {hex(second_char)} or {hex(third_char)} at {match.span()}")
                start,end=match.span()
                prefix_text=newstring[:end]
                list_lines=prefix_text.splitlines()

                suffix_text=newstring[end:]
                list_lines_1=suffix_text.splitlines()
                err=(f" Error occured in {len(list_lines)}th line {list_lines[-1]}{list_lines_1[0]}")
                line=list_lines[-1]+list_lines_1[0]
                err_line_inhex=""
                for current_ascii_character in line:
                    err_line_inhex+=f"{hex(ord(current_ascii_character))} "
                print(f"{err}")
                print(f"{err_line_inhex}")
            else:
                
                temp_string=f"{first_value}{third_value}{second_value}"
                print(f"replaced {newstring[end:newstart]} with {temp_string}")
                my_newstring+=temp_string
            start=newstart

        remaining_string=newstring[start:]
        newstring=my_newstring+remaining_string    

    patterns_list= [
        "([\u0000-\uffff])([\u00c0\u00c1\u00c2\u00c4\u00c5\u00c7\u00c8\u00c9\u00cb\u00cd\u00ce\u00cf])([\u00ea\u00eb\u00ec])",
        #"([\u0000-\uffff])(\u00e0)(\u00eb)",
        #"([\u0000-\uffff])(\u00c2)(\u00ec)",
        #"([\u0000-\uffff])(\u00c1)(\u00ec)",
        #"([\u0000-\uffff])(\u00c1)(\u00eb)",
        #"([\u0000-\uffff])(\u00c5)(\u00eb)",
        #"([\u0000-\uffff])(\u00cf)(\u00eb)",
        #"([\u0000-\uffff])(\u00c5)(\u00ec)",  # This is not correct i feel . Line 557 ,572
        #"([\u0000-\uffff])(\u00c8)(\u00eb)",
        
        #0x63 0xd5 0xc5 0xeb 
        
        
        
        
        
    ]
    

    for pattern in patterns_list:
        print(f"Processing patternset 6 (yaphala repala ravttu with vowel): {pattern} with string of length {len(newstring)}")
        matches = re.finditer(pattern,newstring)
        my_newstring=""
        start=0
        for match in matches:
            end,newstart=match.span()

            my_newstring+=newstring[start:end]
            first_char=int(hex(ord(newstring[match.start()])),16)
            second_char=int(hex(ord(newstring[match.start()+1])),16)
            third_char=int(hex(ord(newstring[match.end()-1])),16)

            print(f"text is {hex(ord(newstring[match.start()]))} first_char {hex(first_char)} second_char {hex(second_char)} third_char {hex(third_char)} at {match.span()}")
            first_value=char_map.get(first_char)

            second_value=char_map.get(second_char)

            third_value=char_map.get(third_char)

            if second_value == None or first_value == None or third_value == None:
                print(f"Warning: No mapping found for {hex(first_char)} or {hex(second_char)} or {hex(third_char)} at {match.span()}")
                start,end=match.span()
                prefix_text=newstring[:end]
                list_lines=prefix_text.splitlines()

                suffix_text=newstring[end:]
                list_lines_1=suffix_text.splitlines()
                err=(f" Error occured in {len(list_lines)}th line {list_lines[-1]}{list_lines_1[0]}")
                line=list_lines[-1]+list_lines_1[0]
                err_line_inhex=""
                for current_ascii_character in line:
                    err_line_inhex+=f"{hex(ord(current_ascii_character))} "
                print(f"{err}")
                print(f"{err_line_inhex}")
            else:
                if third_char == 0xeb:
                    temp_string=f"{third_value}{virama}{first_value}{second_value}"
                else:
                    temp_string=f"{first_value}{virama}{third_value}{second_value}"
                print(f"replaced {newstring[end:newstart]} with {temp_string}")
                my_newstring+=temp_string
            start=newstart

        remaining_string=newstring[start:]
        newstring=my_newstring+remaining_string    
       
    patterns_list= [
        "([\u0000-\u00ff])([\u00ea\u00eb\u00ec])"
    ]
    

    for pattern in patterns_list:
        #my_x=" ".join(f"{hex(ord(c))}" for c in newstring)
        print(f"Processing patternset 7 (yaphala repala ravttu without vowel): {pattern} with string of length {len(newstring)}")
        matches = re.finditer(pattern,newstring)
        my_newstring=""
        start=0
        for match in matches:
            end,newstart=match.span()

            my_newstring+=newstring[start:end]
            first_char=int(hex(ord(newstring[match.start()])),16)
            second_char=int(hex(ord(newstring[match.end()-1])),16)
            

            print(f"text is {hex(ord(newstring[match.start()]))} first_char {hex(first_char)} second_char {hex(second_char)}  at {match.span()}")
            first_value=char_map.get(first_char)

            second_value=char_map.get(second_char)

           

            if second_value == None or first_value == None  :
                print(f"Warning: No mapping found for {hex(first_char)} or {hex(second_char)}  at {match.span()}")
                start,end=match.span()
                prefix_text=newstring[:end]
                list_lines=prefix_text.splitlines()

                suffix_text=newstring[end:]
                list_lines_1=suffix_text.splitlines()
                err=(f" Error occured in {len(list_lines)}th line {list_lines[-1]}{list_lines_1[0]}")
                line=list_lines[-1]+list_lines_1[0]
                err_line_inhex=""
                for current_ascii_character in line:
                    err_line_inhex+=f"{hex(ord(current_ascii_character))} "
                print(f"{err}")
                print(f"{err_line_inhex}")
            else:
                if second_char == 0xeb:
                    temp_string=f"{second_value}{virama}{first_value}"
                else:
                    temp_string=f"{first_value}{virama}{second_value}"
                print(f"replaced {newstring[end:newstart]} with {temp_string}")
                my_newstring+=temp_string
            start=newstart

        remaining_string=newstring[start:]
        newstring=my_newstring+remaining_string    
       
    #print("Hex values:", " ".join(f"{hex(ord(c))}" for c in newstring))      
    recreated_output=""  
    recreated_hex = "" 
    x="";x1="" 
    # pattern for $
    
    
    for c in newstring:
        current_ascii_character=c
        current_ascii_index=int(hex(ord(current_ascii_character)),16)
        if char_map.get(current_ascii_index) ==None:
                    #print(f"no mapping for {current_ascii_character} for index {current_ascii_index}")
                    current_unicode_character=current_ascii_character
                    x+=f"{hex(ord(current_ascii_character))} "
                    x1+=f"{current_unicode_character}"

                    
                
        else:
            current_unicode_character=char_map.get(current_ascii_index)
            #print(f" mapping in {current_unicode_character} for {current_ascii_character} for index {current_ascii_index}")
            x1+=f"{current_unicode_character}"
            x+=f"{hex(ord(current_ascii_character))} "
    recreated_output=x1
    recreated_hex=x
    #print(f"hex={recreated_hex}")
    return recreated_output
    
            
         


def write_grantha_files(output_dir,recreated_output):
    output_file = f"{output_dir}/output_grantha.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
            f.write(recreated_output)
    print(f"Text extracted and saved to {output_file}")
    
    output_file = f"{output_dir}/output_grantha.html"
    additional_body="""
    <style>
        body,pre {
      font-family: "Noto Sans Grantha", sans-serif; /* Use the defined font name */
    }
    </style>
    <body>
    <pre>
    """
    
    additional_body_suffix="""
    </pre>
    </body>
    </html>
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(prefix_html_head)
        
        f.write(additional_body)
        f.write(recreated_output)
        f.write(additional_body_suffix)

def read_file_to_list(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        texts = file.read()
    return texts
# Example usage

def main():
    pdf_path = "S1.pdf"  # Path to your PDF file
    output_dir = "output_text"  # Directory to save the text files
    output_file = f"{output_dir}/output-layout.txt"
    nonworking_patterns=["\u0103\u00e8",
                         "\u010a",
                         "\u006d\u00cd\u006b\u00e0\u00c0\u00eb",
                         "\u00cd[\u0000-\u0fff]\u00c0",
                         "\u00cd[\u0000-\u0fff][^\u00c0]",
                         
                         ]
    os.makedirs(output_dir, exist_ok=True)

    #texts=extract_text_from_pdf(pdf_path, output_file)

    texts=read_file_to_list(output_file) 
    for nonworking_pattern in nonworking_patterns:
        #occurence2 = texts.count(nonworking_pattern)
        occurence2 = len(list(re.finditer(nonworking_pattern, texts)))
        print(f"Non-working pattern '{nonworking_pattern}' found {occurence2} times.")
    # Example: convert hex int 0xf8 to unicode string '\u00f8'
    for key in equivalent_letters:
        unicode_char = chr(key)
        unicode_value=chr(equivalent_letters[key])
        texts=texts.replace(unicode_char,unicode_value)
    for key in ascii_combination_letters.keys():
        # Convert key (int) to Unicode code point character
        unicode_char = chr(key)
        value=ascii_combination_letters[key]
        
        value_string="".join(chr(c) for c in value)
        
        occurence2=texts.count(unicode_char)
        #print(f"Key: {hex(key)},  {unicode_char} Value: {value_string}, Occurrence: {occurence2}")
        texts=texts.replace(unicode_char,value_string)
    process_mapping_table(texts)
    #process_missing_maps(texts)
    lines=texts.splitlines()
    recreated_output=""
    line_num=0
    for line in lines:
        line_num+=1
        if len(line)!=0:
            #print(f"Input: {line} length {len(line)}")
            unicode_line=process_text(line)
            print("Hex values:", " ".join(f"{hex(ord(c))}" for c in line))
            print(f" Line {line_num} Input: {line} length {len(line)} Output: {unicode_line} length {len(unicode_line)}")
        else:
            unicode_line=""
            print(f" skipped processing ")
        
        recreated_output+=unicode_line+"\n"
    write_grantha_files(output_dir,recreated_output)

if __name__ == "__main__":
    main()
