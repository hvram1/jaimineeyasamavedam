# -*- coding: utf-8 -*-
import grapheme
import sys
import re

unexpected_grapheme_clusters=[
    "(\U00000020)(\U0001133F)",
    
    "(\U00000020)(\U00011302)",
    "(\U00000020)(\U00011303)",
    "(\U00000020)(\U0001133B)",
    "(\U00000020)(\U0001133E)",
    "(\U00000020)(\U00011340)",
    "(\U00000020)(\U0001134D)",
    
    ]

explore_unexpected_grapheme_clusters=[
    "\U00000020\U00011347\U00011347",
    "\U00000024",
    "\U00000033\U00011302",
    "\U00000034\U0001133E",
    "\U00000B99\U00011302",
    "\U00000B99\U00011302",
    "\U00000B99\U0001133E",
    "\U00000B99\U0001133F",
    "\U00000B99\U00011343",
    "\U00000B99\U00011347",
    "\U00000B99\U00011347\U0001133E",
    "\U00000B99\U0001134D",
    "\U00000B99\U00011357",
    "\U00000BB4\U00000BBE\U0001133E",
    "\U00000BB4\U0001133E",
    "\U00011315\U0001133F\U0001134D",
    "\U00011315\U00011340\U0001134D",
    "\U00011315\U00011347\U0001134D",
    "\U00011315\U00011348\U0001134D",
    "\U00011315\U0001134D\U00011342",
    "\U00011315\U0001134D\U00011342\U0001133E",
    "\U00011318\U00011347\U0001134D",
    "\U00011319\U0001133F\U0001134D",
    "\U0001131C\U0001133F\U0001134D",
    "\U0001131C\U00011340\U0001134D",
    "\U0001131C\U00011348\U0001134D",
    "\U0001131F\U00011340\U0001134D",
    "\U00011321\U0001133F\U0001134D",
    "\U00011321\U00011340\U0001134D",
    "\U00011323\U00011347\U0001134D",
    "\U00011324\U0001133E\U0001134D",
    "\U00011324\U0001133F\U0001134D",
    "\U00011324\U00011347\U0001134D",
    "\U00011325\U00011340\U0001134D",
    "\U00011326\U00011340\U0001134D",
    "\U00011326\U00011347\U0001134D",
    "\U00011328\U00011340\U0001134D",
    "\U00011328\U00011347\U0001134D",
    "\U00011328\U00011348\U0001134D",
    "\U0001132A\U0001133F\U0001134D",
    "\U0001132A\U00011340\U0001134D",
    "\U0001132A\U00011347\U0001134D",
    "\U0001132A\U0001134D\U00011342",
    "\U0001132A\U0001134D\U00011342\U0001134D",
    "\U00011347\U00011347",
    "\U00011338\U00011347\U0001134D",
    "\U00011337\U00011347\U0001134D",
     "\U00011337\U00011347\U0001133B",
"\U00011337\U00011347\U0001133B\U0001133E",
"\U00011337\U0001133E\U0001133B\U00011302",
 "\U00011337\U0001133E\U0001134D",
  "\U00011336\U00011347\U0001134D",
"\U00011336\U00011347\U0001134D\U00011342\U0001133E",
 "\U00011336\U00011347\U0001134D\U00011342\U0001134D",
 "\U00011335\U00011347\U0001134D",
   "\U00011332\U00011347\U0001134D",
   "\U00011330\U0001134D\U0001133F",
  "\U00011330\U0001134D\U0001133F\U00011303",
   "\U00011330\U0001134D\U00011340",
   "\U00011330\U0001134D\U00011340\U00011302",
   "\U00011330\U0001134D\U00011340\U00011303",
   "\U00011330\U0001134D\U00011342",
   "\U00011330\U0001134D\U00011343",
  "\U00011330\U0001134D\U0001134D",
   "\U00011330\U0001134D\U00011357",
  "\U0001132E\U00011348\U0001134D",
   "\U0001132E\U00011347\U0001134D",
  "\U0001132C\U00011340\U0001134D",
  "\U0001132B\U0001134D\U00011342",
  "\U00000065\U0001133F",
]

def extract_graphemes(text):
    unique_graphemes={}
    
    line_number=1
    lines=text.splitlines()
    for line in lines:
        g1  = grapheme.graphemes(line)
        for g in g1:
            if g in explore_unexpected_grapheme_clusters:
                print(f"{g} occurred in line {line_number}")
            unique_graphemes[g]=1

        line_number += 1
    return unique_graphemes

def replace_unexpected_graphemes(text):
    newstring=text
    for pattern in unexpected_grapheme_clusters:
        print(f"Processing patternset 1: {pattern} with string of length {len(newstring)}")
        matches = re.finditer(pattern,newstring)
        my_newstring=""
        start=0
        for match in matches:
            end,newstart=match.span()

            my_newstring+=newstring[start:end]
            
            temp_string=f"{match.group(2)}"
            #print(f"temp_string is {temp_string}")
            my_newstring+=temp_string
            start=newstart

        remaining_string=newstring[start:]
        newstring=my_newstring+remaining_string 
    
    '''for pattern in explore_unexpected_grapheme_clusters:
        print(f"Processing patternset 2: {pattern} with string of length {len(newstring)}")
        matches = re.finditer(pattern,newstring)
        my_newstring=""
        start=0
        for match in matches:
            end,newstart=match.span()

            #my_newstring+=newstring[start:end]
            
            temp_string=f"{match.group(1)}"
            print(f"temp_string is {temp_string}")
            my_newstring+=temp_string
            start=newstart

        #remaining_string=newstring[start:]
        #newstring=my_newstring+remaining_string
        '''
    return newstring

def main():
    if len(sys.argv) < 2:
        print("Usage: python extract_uniquegrapheme.py <input_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    unique_graphemes = extract_graphemes(content)
    
    unique_graphemes = sorted(set(unique_graphemes))
    '''content=replace_unexpected_graphemes(content)
    
    with open(input_file, 'w', encoding='utf-8') as f:
        f.write(content)'''

    for g in unique_graphemes:
        print(f"{g}  \"(\\U{'\\U'.join(f'{ord(c):08X}' for c in g)})\"")
    
if __name__ == "__main__":
    main()