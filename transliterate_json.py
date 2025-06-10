from aksharamukha import transliterate
import json

def transliterate_text(text, src_script, target_script):
    """
    Transliterates text from the source script to the target script.
    """
    try:
        # Perform the transliteration
        result = transliterate.process( src_script, target_script,text)
        return result
    except Exception as e:
        print(f"Error occurred during transliteration: {e}")
        return None

with open('output_text/final-Grantha.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
        
src_script="Grantha"
target_scripts=["Devanagari","Tamil","Malayalam"]

def transliterate_json(obj,src_script, target_script):
    if isinstance(obj, dict):
        return {k: transliterate_json(v,src_script,target_script) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [transliterate_json(item,src_script,target_script) for item in obj]
    elif isinstance(obj, str):
        return transliterate_text(obj, src_script, target_script)
    else:
        return obj
for target_script in target_scripts:
    print(f"Transliterating to {target_script}...")
    result_data = transliterate_json(data, src_script, target_script)
    
    
    filename = f'output_text/final-{target_script}.json'

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(result_data, f, ensure_ascii=False, indent=2)