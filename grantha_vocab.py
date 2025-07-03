from char_map import char_map,ascii_combination_letters
grantha_vowels=[
    "\U00011305", #A
    "\U00011306", #AA
    "\U00011307", #I
    "\U00011308", #II
    "\U00011309", #U
    "\U0001130A", #UU
    "\U0001130F", #EE
    "\U00011310", #AI
    "\U00011313", #O
    "\U00011314", #AU
    "\U00011362", #L
    "\U00011363", #LL
    "\U0001130C",
    "\U00011361",
    "\U0001130B",
    "\U00011360"
]

grantha_consonants=[
    "\U00011315",
    "\U00011316",
    "\U00011317",
    "\U00011318",
    "\U00011319",
    "\U0001131A",
    "\U0001131B",
    "\U0001131C",
    "\U0001131D",
    "\U0001131E",
    "\U0001131F",
    "\U00011320",
    "\U00011321",
    "\U00011322",
    "\U00011323",
    "\U00011324",
    "\U00011325",
    "\U00011326",
    "\U00011327",
    "\U00011328",
    "\U0001132A",
    "\U0001132B",
    "\U0001132C",
    "\U0001132D",
    "\U0001132E",
    "\U0001132F",
    "\U00011330",
    "\U00011332",
    "\U00011333",
    "\U00011335",
    "\U00011336",
    "\U00011337",
    "\U00011338",
    "\U00011339",
]

grantha_vowel_extender=[
    "\U0001133E",  #AA
    "\U0001133F",  #I
    "\U00011340",  #II
    "\U00011341",  #U
    "\U00011342",  #UU
    "\U00011357",  #R
    "\U00011343",  #R
    "\U00011344",  #R

    "\U00011347", #EE
    "\U00011348", #AI
    "\U0001134B", #O
    "\U0001134C", #AU

]

'''grantha_extra =[  # possibly vowels
    "\U0001130C",
    "\U00011361",
    "\U0001130B",
    "\U00011360"
    
]'''

grantha_punctuation =[
    "\U00011302",
]

grantha_ra="\U00011330"
grantha_ya="\U0001132F"
grantha_virama="\U0001134D"
# 𑌰𑍍𑌦𑍀. (ra+virama+da+deergha)
# 𑌦𑍍𑌰𑍀  (da + virama + ra + deergha )


ascii_numbers=[0x30,0x31,0x32,0x33,0x34,0x35,0x36,0x37,0x38,0x39,0x1c4,0x1c5,0x1c6,0x1c7,0x1c8,0x1c9,0x1ca,0x1cb,0x1cc,0x1cd]
ascii_tamil_letters=[0xbbe,0xbb4,0x6f]
ascii_punctuation=[0x2e,0x3d,0x51,0x4d,0x46,0x2c,0x48]

for consonant in grantha_consonants:
    for vowel in grantha_vowel_extender:
        print(f"1. {consonant}{vowel}")
        print(f"2. {grantha_ra}{grantha_virama}{consonant}{vowel}")
        print(f"3. {consonant}{grantha_virama}{grantha_ra}{vowel}")
        print(f"4. {consonant}{grantha_virama}{grantha_ya}{vowel}")
        print(f"5. {grantha_ra}{grantha_virama}{consonant}{grantha_virama}{consonant}{vowel}")

    

    print(f"11. {grantha_ra}{grantha_virama}{consonant}")
    print(f"12. {grantha_ra}{grantha_virama}{consonant}{grantha_virama}{consonant}")
    print(f"13. {consonant}{grantha_virama}{grantha_ra}")
    print(f"14. {consonant}{grantha_virama}{grantha_ya}")

ascii_others=[]
ascii_subscripts=[]
ascii_consonants=[]
ascii_vowels=[]
ascii_extenders_follow=[]
ascii_extenders_preceding=[]

for ascii_key in char_map.keys():
    value_grantha=char_map[ascii_key]
    
    if (grantha_virama in value_grantha):
        #print(f" {hex(ascii_key)} {value_grantha}  subscript ")
        if len(value_grantha) > 2:
            #print(f" {hex(ascii_key)} {value_grantha}  -- virama >2 combination")
            ascii_others.append(ascii_key)
        elif len(value_grantha) == 2:
            value_grantha = value_grantha.replace(grantha_virama, "")
            ascii_subscripts.append(ascii_key)
            #print(f" {hex(ascii_key)} {value_grantha}  -- subscript ==2 combination")

    elif len(value_grantha) ==2:
        if value_grantha[1] in grantha_vowel_extender :
            #ascii_vowels.append(ascii_key)
            #print(f" {hex(ascii_key)} {value_grantha}   -- vowel combination")
        
            #ascii_consonants.append(ascii_key)
            if ascii_key not in ascii_combination_letters.keys():
                print(f" Unexpected Error for {hex(ascii_key)}")
            else:
                #print(f" {hex(ascii_key)} {value_grantha[1]}   -- ascii character combination ")
                pass
        elif value_grantha[0] in grantha_vowel_extender :
            print(f" Unexpected")
    elif len(value_grantha) > 2:
        #print(f" {hex(ascii_key)} {value_grantha}   -- other combination")
        ascii_others.append(ascii_key)
    else:
        
        if value_grantha in grantha_vowels:
            ascii_vowels.append(ascii_key)
            #print(f" {hex(ascii_key)} {value_grantha}   -- single character vowel")
        elif value_grantha in grantha_consonants:
            ascii_consonants.append(ascii_key)
            #print(f" {hex(ascii_key)} {value_grantha}   -- single character consonant")
        elif value_grantha in grantha_vowel_extender:
            ascii_extenders_follow.append(ascii_key)
            #print(f" {hex(ascii_key)} {value_grantha}   -- single character extender follow")
        
        elif ascii_key in ascii_numbers:
            #ascii_numbers.append(ascii_key)
            #print(f" {hex(ascii_key)} {value_grantha}   -- single character number")
            pass
        elif ascii_key in ascii_tamil_letters:
            #ascii_tamil_letters.append(ascii_key)
            #print(f" {hex(ascii_key)} {value_grantha}   -- single character tamil letter")
            pass
        elif ascii_key in ascii_punctuation:
            #ascii_punctuation.append(ascii_key)
            #print(f" {hex(ascii_key)} {value_grantha}   -- single character punctuation")
            pass
        else:
            print(f" {hex(ascii_key)} {value_grantha}   -- missing category 1")

print(f" char_map {len(char_map)} ascii_vowels {len(ascii_vowels)} ascii_consonants {len(ascii_consonants)} ascii_extenders_follow {len(ascii_extenders_follow)} ascii_extenders_preceding {len(ascii_extenders_preceding)} ascii_others {len(ascii_others)} ascii_subscripts {len(ascii_subscripts)}")

for key in char_map.keys():
    if (
        key not in ascii_others
        and key not in ascii_vowels
        and key not in ascii_consonants
        and key not in ascii_extenders_follow
        and key not in ascii_extenders_preceding
        and key not in ascii_subscripts
        and key not in ascii_combination_letters.keys()
        and key not in ascii_numbers
        and key not in ascii_tamil_letters
        and key not in ascii_punctuation
    ):
        print(f" {hex(key)} {char_map[key]}   -- missing category ")
print(f" These are the ascii vowel extenders")
for key in ascii_extenders_follow:
    print(f"Key {hex(key)} Value {char_map[key]}" )
