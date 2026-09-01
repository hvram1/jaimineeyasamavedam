from aksharamukha import transliterate
import json

def transliterate_text(text, src_script, target_script):
    """
    Transliterates text from the source script to the target script.
    """
    try:
        flags=[]
        if target_script == "TamilExtended" or target_script == "Tamil" or target_script == "TamilBrahmi":
            flags.append('TamilRemoveApostrophe')
            flags.append('TamilGranthaVisarga')
            flags.append('TamilSubScript')
        # Perform the transliteration
        result = transliterate.process( src_script, target_script,text,False,post_options=flags)
        if target_script == "Devanagari":
            result=result.replace("ழா","ळा")

            result=result.replace("ழ","ळ")
        if target_script == "Malayalam":
            result=result.replace("ழா","ഴാ")

            result=result.replace("ழ","ഴ")
        return result
    except Exception as e:
        print(f"Error occurred during transliteration: {e}")
        return None



def transliterate_json(obj,src_script, target_script):
    if isinstance(obj, dict):
        return {k: transliterate_json(v,src_script,target_script) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [transliterate_json(item,src_script,target_script) for item in obj]
    elif isinstance(obj, str):
        return transliterate_text(obj, src_script, target_script)
    else:
        return obj

def test_transliteration():
    input_text_list=["𑌜𑍈𑌮𑌿𑌨𑍀𑌯  𑌸𑌾𑌮  𑌪𑍍𑌰𑌕𑍃𑌤𑌿  𑌗𑌾𑌨𑌮𑍍"]
    src_script = "Grantha"
    target_scripts = ["Devanagari", "Tamil", "Malayalam"]
    
    for text in input_text_list:
        transliterated_text=transliterate_text(text,src_script,target_scripts[0])
        
        #transliterated_text=transliterated_text.replace("ழா","ळा")
        #transliterated_text=transliterated_text.replace("ழ","ळ")
        print(f" This is the source {text} and this is the result {transliterated_text}")

   

def main():
    with open('output_text/updated-final-Devanagari.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    #src_script = "Grantha"
    #target_scripts = ["Devanagari", "Tamil", "Malayalam"]
    
    src_script = "Devanagari"
    target_scripts = ["Grantha", "Tamil", "Malayalam"]

    for target_script in target_scripts:
        print(f"Transliterating to {target_script}...")
        result_data = transliterate_json(data, src_script, target_script)
        
        filename = f'output_text/updated-final-{target_script}.json'
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result_data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
    #test_transliteration()