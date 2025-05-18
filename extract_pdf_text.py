import PyPDF2
import re
virama="\U0001134D"

def write_html_table(outfile, uniq_chars,char_map):
    prefix_html="""
    <!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8" />
    <title>Unique Character Mapping</title>
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
</style>
<body>
    <p> Some chracters are better in Noto Sans Grantha while some others are better in Noto Serif Grantha. 
    Take a look at the row where ASCII value is 297 
    </p>
    <table border="1" cellpadding="8" cellspacing="0">
        <tr>
            <th>Krishna Vedic</th>
            <th>Noto Sans Grantha</th>
            <th>Noto Serif Grantha</th>
            <th>ASCII Value</th>
            <th>Unicode Value</th>
            <th>Unicode Name</th>
        </tr>
    """
    suffix_html="""
    </table>
</body>
</html>
"""
    content_html=""
    for key in uniq_chars.keys():
        current_ascii_index=int(hex(ord(key)),16)
        value=char_map.get(current_ascii_index)
        print(f"key is {key} hex is {hex(ord(key))}")
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
        row = f"<tr><td class=\"k1\">{key}</td><td class=\"n1\">{value}</td> <td class=\"n2\">{value}</td><td>{current_ascii_index}</td><td>{unicode_code_point}</td><td>{unicode_name}</td></tr>\n"
        content_html+=row
    
    with open(outfile,"w",encoding="utf-8") as f:
        f.write(prefix_html)
        f.write(content_html)
        f.write(suffix_html)
        
def extract_text_from_pdf(pdf_path, output_dir):
    # Open the PDF file
    with open(pdf_path, 'rb') as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        texts=""
        # Iterate through each page
        for page_number, page in enumerate(reader.pages, start=1):
            # Extract text from the page
            text = page.extract_text()
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
        output_file = f"{output_dir}/output.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(texts)
        print(f"Text extracted and saved to {output_file}")
        return texts

def process_text(texts):
    uniq_chars={}
    for c in texts:
        #current_ascii_index=int(hex(ord(c)),16)
        if uniq_chars.get(c) == None:
                uniq_chars[c]=1
    outfile = f"{output_dir}/mapping.html"
    write_html_table(outfile, uniq_chars,char_map)
       
    # list_texts=list(texts)
    # print(f" len of the string {len(texts)} Length of the list {len(list_texts)}")
    pattern1="\u00c0\u00eb"
    pattern1_replace="\u00eb\u00c0"
    pattern2="\u00c7\u00eb"
    pattern2_replace="\u00eb\u00c7"
    occurence1 = texts.count(pattern1)
    occurence2 = texts.count(pattern2)
    print(f" Length of char_map is {len(char_map)}, missing maps {len(missing_maps_list)}")
    print(f" Occurence of {pattern1} = {occurence1} , Occurence of {pattern2}= {occurence2}")
    texts=texts.replace(pattern1,pattern1_replace)
    texts=texts.replace(pattern2,pattern2_replace)
    
    newstring=texts
    missing_regular_exp=[
        "\(", #0x28
        "\)", #0x29
        "\+", #0x2b
        "\[", #0x5b,
        "\|", #0x7c
    ]
    for item in missing_maps_list:
        print(f"Item to match {hex(ord(item))}")
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
    
    patterns_list= [
        "(\u00ce)([\u0000-\u0fff])(\u00ea)",
        
        "(\u00cd)([\u0000-\u0fff])(\u00ea)",
        
    ]
    
    for pattern in patterns_list:
        print(f"Processing patternset 1: {pattern} with string of length {len(newstring)}")
        matches = re.finditer(pattern,newstring)
        my_newstring=""
        start=0
        for match in matches:
            end,newstart=match.span()

            my_newstring+=newstring[start:end]
            first_char=int(hex(ord(newstring[match.start()])),16)
            second_char=int(hex(ord(newstring[match.start()+1])),16)
            third_char=int(hex(ord(newstring[match.end()-1])),16)
            # print(f"text is {hex(ord(newstring[match.start()]))} first_char {first_char} second_char {second_char} third_char {third_char}")
            first_value=char_map.get(first_char)

            second_value=char_map.get(second_char)

            third_value=char_map.get(third_char)
            if second_value == None or first_value == None or third_value == None:
                print(f"Warning: No mapping found for {hex(first_char)} or {hex(second_char)} or {hex(third_char)} at {match.span()}")
            else:
                temp_string=f"{second_value}{virama}{third_value}{first_value}"
                my_newstring+=temp_string
            start=newstart

        newstring=my_newstring

    patterns_list= [
        "(\u00ce)([\u0000-\u0fff])",
        
        "(\u00cd)([\u0000-\u0fff])",
        
    ]

    for pattern in patterns_list:
        print(f"Processing patternset 2: {pattern} with string of length {len(newstring)}")
        matches = re.finditer(pattern,newstring)
        my_newstring=""
        start=0
        for match in matches:
            end,newstart=match.span()

            my_newstring+=newstring[start:end]
            first_char=int(hex(ord(newstring[match.start()])),16)
            second_char=int(hex(ord(newstring[match.end()-1])),16)

            # print(f"text is {hex(ord(newstring[match.start()]))} first_char {first_char} second_char {second_char} ")
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
                my_newstring+=temp_string
            start=newstart

        newstring=my_newstring    

    patterns_list= [
        "([\u0000-\u0fff])(\u00ec)",
        
        "([\u0000-\u0fff])(\u00ea)",
        
    ]

    for pattern in patterns_list:
        print(f"Processing patternset 3: {pattern} with string of length {len(newstring)}")
        matches = re.finditer(pattern,newstring)
        my_newstring=""
        start=0
        for match in matches:
            end,newstart=match.span()

            my_newstring+=newstring[start:end]
            first_char=int(hex(ord(newstring[match.start()])),16)
            second_char=int(hex(ord(newstring[match.end()-1])),16)

            # print(f"text is {hex(ord(newstring[match.start()]))} first_char {first_char} second_char {second_char} ")
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
                temp_string=f"{first_value}{virama}{second_value}"
                my_newstring+=temp_string
            start=newstart

        newstring=my_newstring    

    patterns_list= [
        "([\u0000-\u0fff])(\u00eb)",
        
        
        
    ]

    for pattern in patterns_list:
        print(f"Processing patternset 4: {pattern} with string of length {len(newstring)}")
        matches = re.finditer(pattern,newstring)
        my_newstring=""
        start=0
        for match in matches:
            end,newstart=match.span()

            my_newstring+=newstring[start:end]
            first_char=int(hex(ord(newstring[match.start()])),16)
            second_char=int(hex(ord(newstring[match.end()-1])),16)

            # print(f"text is {hex(ord(newstring[match.start()]))} first_char {first_char} second_char {second_char} ")
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
                temp_string=f"{second_value}{virama}{first_value}"
                my_newstring+=temp_string
            start=newstart

        newstring=my_newstring    

    lines = newstring.splitlines()
    print(f" len of the string {len(newstring)} Number of lines {len(lines)}")
    line_num=1
    recreated_output=""
    for line in lines:
        recreated_line=[]
        recreated_hex=[]
        words = line.split()
        for word in words:
            # print(f"WORD={word}")
            # word=word.replace("Àë","ëÀ")

            x=""
            x1=""
            i=0
            while i<len(word):

                current_ascii_character=word[i]
                current_ascii_index=int(hex(ord(current_ascii_character)),16)

                if char_map.get(current_ascii_index) ==None:
                    # print(f"no mapping for {l}")
                    current_unicode_character=current_ascii_character
                    x+=f"{hex(ord(current_ascii_character))} "
                    x1+=f"{current_unicode_character}"

                    pass
                else:
                    current_unicode_character=char_map.get(current_ascii_index)
                    if i+1 < len(word):
                        next_ascii_character=word[i+1]
                        next_ascii_index=int(hex(ord(next_ascii_character)),16)
                        next_unicode_character=char_map.get(next_ascii_index)
                        # print(f"current index {i} {hex(current_ascii_index)} l1 is {current_unicode_character} next ascii index {i+1} is {hex(next_ascii_index)} l1_next is {next_unicode_character}")
                    else:
                        next_ascii_character=next_unicode_character=""
                        next_ascii_index=-1
                    '''
                    if current_ascii_index == 0xce or current_ascii_index == 0xcd:
                        
                        #print(f"flipping chars for {current_ascii_index}")
                        x+=f"{hex(ord(current_ascii_character))} {hex(ord(next_ascii_character))} "
                        x1+=f"{next_unicode_character}{current_unicode_character}"
                        i+=1
                    elif next_ascii_index == 0xec or next_ascii_index== 0xea :  
                        x+=f"{hex(ord(current_ascii_character))} {hex(ord(next_ascii_character))} "
                        x1+=f"{current_unicode_character}{virama}{next_unicode_character}"
                        i+=1
                    elif next_ascii_index == 0xeb:
                        x+=f"{hex(ord(current_ascii_character))} {hex(ord(next_ascii_character))} "
                        x1+=f"{next_unicode_character}{virama}{current_unicode_character}"
                        i+=1
                    
                    else:'''
                    x1+=f"{current_unicode_character}"
                    x+=f"{hex(ord(current_ascii_character))} "
                i+=1

                #if uniq_chars.get(current_ascii_character) == None:
                #    uniq_chars[current_ascii_character]=1
            # print(f"hex {x}")
            recreated_hex.append(x)
            # x2=flip_chars(x1)
            # print(f"recreated {x1}")
            recreated_line.append(x1)
        print(f"-------")
        new_line=" ".join(recreated_line)
        new_hex=",".join(recreated_hex)
        print(f"recreated_line{line_num}={new_line}")
        recreated_output+=new_line+"\n"
        print(f"hex={new_hex}")
        line_num+=1

    output_file = f"{output_dir}/output_grantha.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
            f.write(recreated_output)
    print(f"Text extracted and saved to {output_file}")
    


def read_file_to_list(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        texts = file.read()
    return texts
# Example usage
pdf_path = "S1.pdf"  # Path to your PDF file
output_dir = "output_text"  # Directory to save the text files
output_file = f"{output_dir}/output.txt"
import os
from char_map import char_map,missing_maps_list
import unicodedata
os.makedirs(output_dir, exist_ok=True)

# texts=extract_text_from_pdf(pdf_path, output_dir)

texts=read_file_to_list(output_file) 
process_text(texts)
