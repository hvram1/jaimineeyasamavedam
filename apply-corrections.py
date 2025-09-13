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
with open("output_text/intermediate-final-Devanagari-with-corrected-mantra_sets.json", "r", encoding="utf-8") as f:
    data_corrected_Devanagari = json.load(f)

with open("output_text/intermediate-final-Devanagari.json", "r", encoding="utf-8") as f:
    data_final_Devanagari = json.load(f)

supersections_Devanagari = data_final_Devanagari.get('supersection', {})
    
for supersection_key, corrected_supersection in data_corrected_Devanagari.get('supersection', {}).items():
    if supersection_key not in supersections_Devanagari:
        continue
    final_supersection = supersections_Devanagari[supersection_key]
    for section_key, corrected_section in corrected_supersection.get('sections', {}).items():
        if section_key not in final_supersection.get('sections', {}):
            continue
        final_section = final_supersection['sections'][section_key]
        for subsection_key, corrected_subsection in corrected_section.get('subsections', {}).items():
            if subsection_key not in final_section.get('subsections', {}):
                continue
            final_subsection = final_section['subsections'][subsection_key]
            corrected_mantra_sets = corrected_subsection.get('corrected-mantra_sets', [])
            final_subsection['corrected-mantra_sets'] = corrected_mantra_sets
            
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


