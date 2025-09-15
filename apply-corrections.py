import json
import sys

def find_matching_set(data, image_ref):
    if isinstance(data, dict):
        for key, value in data.items():
            if key == "mantra_sets":
                for mantra_set in value:
                    for mantra in mantra_set.get("mantras", []):
                        if mantra.get("image-ref") == image_ref:
                            return mantra_set
            result = find_matching_set(value, image_ref)
            if result:
                return result
    elif isinstance(data, list):
        for item in data:
            result = find_matching_set(item, image_ref)
            if result:
                return result
    return None



# Load the JSON file (now using the generated file with corrected-mantra_sets)
with open("output_text/corrected-Devanagari.json", "r", encoding="utf-8") as f:
    data_corrected_Devanagari = json.load(f)

with open("output_text/intermediate-final-Devanagari-with-corrected-mantra_sets.json", "r", encoding="utf-8") as f:
    data_final_Devanagari = json.load(f)

supersections_Devanagari = data_final_Devanagari.get('supersection', {})

for j,data_corrected_section_Devanagari in enumerate(data_corrected_Devanagari):
    #print(f" j is {j} {data_corrected_section}")
    for i, supersection_Devanagari in enumerate(supersections_Devanagari):
        for j, data_final_section_Devanagari in enumerate(supersections_Devanagari[supersection_Devanagari].get('sections', [])):
            if data_final_section_Devanagari == data_corrected_section_Devanagari:
                #print(f" j is {j}, i is {i} name is {data_corrected_section}")
                data_final_subsections_Devanagari = supersections_Devanagari[supersection_Devanagari].get('sections', [])[data_final_section_Devanagari].get('subsections',[])
                data_corrected_subsections_Devanagari = data_corrected_Devanagari.get(data_corrected_section_Devanagari).get('subsections')
                
                for k,data_corrected_subsection_Devanagari in enumerate(data_corrected_subsections_Devanagari):
                    #print(f" k is {k} {data_corrected_subsection}")
                    
                    data_final_mantra_sets_Devanagari = data_final_subsections_Devanagari[data_corrected_subsection_Devanagari].get('mantra_sets', [])
                    data_corrected_mantra_sets_Devanagari = data_corrected_subsections_Devanagari[data_corrected_subsection_Devanagari].get('corrected-mantra_sets',[])
                    data_final_subsections_Devanagari[data_corrected_subsection_Devanagari]['corrected-mantra_sets'] = data_corrected_mantra_sets_Devanagari
                    '''
                    if (len(data_corrected_mantra_sets_Devanagari) != len(data_final_mantra_sets_Devanagari)):
                        print(f" Lengths of corrected_mantra_sets is {len(data_corrected_mantra_sets_Devanagari)}, original_mantra_sets is {len(data_final_mantra_sets_Devanagari)} for section {data_final_section_Devanagari} subsection {data_corrected_subsection_Devanagari} ")
                        for m,data_corrected_mantra_set in enumerate(data_corrected_mantra_sets_Devanagari):
                            print(f"Corrected Mantra Set {m}: {data_corrected_mantra_set.get('corrected-mantra')}")
                        #(f"{data_corrected_mantra_sets}")
                        print(f"---")
                        #print(f"{data_final_mantra_sets}")
                        for m,data_final_mantra_Devanagari in enumerate(data_final_mantra_sets_Devanagari):
                            mantra=""
                            mantra_words = data_final_mantra_Devanagari.get('mantra-words', [])
                            for w,word in enumerate(mantra_words):
                                actual_word = word.get('word', 'WORD')
                                mantra+=" " +actual_word
                            print(f"Mantra for final set {m}: {mantra}")
                    else:
                        for m,data_final_mantra_Devanagari in enumerate(data_final_mantra_sets_Devanagari):
                            data_final_mantra_Devanagari['corrected-mantra']=data_corrected_mantra_sets_Devanagari[m].get('corrected-mantra')
                            data_final_mantra_Devanagari['corrected-swara']=data_corrected_mantra_sets_Devanagari[m].get('corrected-swara')
                    '''
     
'''
for section_key, corrected_section in corrected_supersection.get('sections', {}).items():
    if section_key not in final_supersection.get('sections', {}):
        print(f"Section {section_key} not found in final supersection {supersection_key}, skipping.")
        continue
    final_section = final_supersection['sections'][section_key]
    for subsection_key, corrected_subsection in corrected_section.get('subsections', {}).items():
        if subsection_key not in final_section.get('subsections', {}):
            print(f"Subsection {subsection_key} not found in final section {section_key}, skipping.")
            continue
        final_subsection = final_section['subsections'][subsection_key]
        corrected_mantra_sets = corrected_subsection.get('corrected-mantra_sets', [])
        print(f"Processing subsection: {subsection_key} ")
        final_subsection['corrected-mantra_sets'] = corrected_mantra_sets
'''         
# Save the updated data_final into another file
with open("output_text/updated-final-Devanagari.json", "w", encoding="utf-8") as f:
    json.dump(data_final_Devanagari, f, ensure_ascii=False, indent=4)         
sys.exit(1)

for i, supersection_Devanagari in enumerate(supersections_Devanagari):
    for j, section in enumerate(supersections_Devanagari[supersection_Devanagari].get('sections', [])):
        sections = supersections_Devanagari[supersection_Devanagari].get('sections', [])
        for k, subsection in enumerate(sections[section].get('subsections', [])):
            subsections = sections[section].get('subsections', [])
            
            header = subsections[subsection].get('header', {}).get('header', 'Untitled Header')
            header_number = subsections[subsection].get('header', {}).get('header_number', 0)
            header_image = subsections[subsection].get('header', {}).get('image-ref', '')
            mantra_sets = subsections[subsection].get('mantra_sets', [])
            for mantra in mantra_sets:
                image_ref_final = mantra.get('image-ref',"")
                
                for item in data_corrected_Devanagari:
                    image_ref_corrected = item.get('image-ref',"")
                    if image_ref_corrected == image_ref_final:
                        mantra["corrected-mantra"]=item.get('corrected-mantra',"")
                        mantra["corrected-swara"]=item.get('corrected-swara',"")
                        data_corrected_Devanagari.remove(item)
                        break
                if len(data_corrected_Devanagari) ==0:
                    break
            if len(data_corrected_Devanagari) ==0:
                break
    if len(data_corrected_Devanagari) == 0:
        break


