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


# Load the JSON file
with open("output_text/corrected-Devanagari.json", "r", encoding="utf-8") as f:
    data_corrected = json.load(f)

with open("output_text/intermediate-final-Devanagari.json", "r", encoding="utf-8") as f:
    data_final = json.load(f)

supersections = data_final.get('supersection', {})
    
for j,data_corrected_section in enumerate(data_corrected):
    #print(f" j is {j} {data_corrected_section}")
    for i, supersection in enumerate(supersections):
        for j, data_final_section in enumerate(supersections[supersection].get('sections', [])):
            if data_final_section == data_corrected_section:
                #print(f" j is {j}, i is {i} name is {data_corrected_section}")
                data_final_subsections = supersections[supersection].get('sections', [])[data_final_section].get('subsections',[])
                data_corrected_subsections = data_corrected.get(data_corrected_section).get('subsections')
                
                for k,data_corrected_subsection in enumerate(data_corrected_subsections):
                    #print(f" k is {k} {data_corrected_subsection}")
                    data_corrected_header_number = data_corrected_subsections[data_corrected_subsection].get('corrected-header',{}).get('header_number','U2')
                    for l,data_final_subsection in enumerate(data_final_subsections):
                        data_final_header_number = data_final_subsections[data_final_subsection].get('header',{}).get('header_number', 'U1')
                        
                        if data_final_header_number == data_corrected_header_number:
                            #print(f" Matched header at {l}")
                            #print(f"data_final_header {data_final_header_number}, data_corrected_header {data_corrected_header_number}" )
                            data_final_mantra_sets = data_final_subsections[data_final_subsection].get('mantra_sets', [])
                            data_corrected_mantra_sets = data_corrected_subsections[data_corrected_subsection].get('corrected-mantra_sets',[])
                            if (len(data_corrected_mantra_sets) != len(data_final_mantra_sets)):
                                print(f" Lengths of mantra_sets is {len(data_corrected_mantra_sets)}, {len(data_final_mantra_sets)} for section {data_final_section} subsection {data_final_subsection} and header {data_corrected_header_number}")
                                print(f"{data_corrected_mantra_sets}")
                                print(f"---")
                                print(f"{data_final_mantra_sets}")
                                
                            else:
                                for m,data_final_mantra in enumerate(data_final_mantra_sets):
                                    data_final_mantra['corrected-mantra']=data_corrected_mantra_sets[m].get('corrected-mantra')
                                    data_final_mantra['corrected-swara']=data_corrected_mantra_sets[m].get('corrected-swara')
                            
                            break
            
# Save the updated data_final into another file
with open("output_text/updated-final-Devanagari.json", "w", encoding="utf-8") as f:
    json.dump(data_final, f, ensure_ascii=False, indent=4)         
sys.exit(1)

for i, supersection in enumerate(supersections):
    for j, section in enumerate(supersections[supersection].get('sections', [])):
        sections = supersections[supersection].get('sections', [])
        for k, subsection in enumerate(sections[section].get('subsections', [])):
            subsections = sections[section].get('subsections', [])
            
            header = subsections[subsection].get('header', {}).get('header', 'Untitled Header')
            header_number = subsections[subsection].get('header', {}).get('header_number', 0)
            header_image = subsections[subsection].get('header', {}).get('image-ref', '')
            mantra_sets = subsections[subsection].get('mantra_sets', [])
            for mantra in mantra_sets:
                image_ref_final = mantra.get('image-ref',"")
                
                for item in data_corrected:
                    image_ref_corrected = item.get('image-ref',"")
                    if image_ref_corrected == image_ref_final:
                        mantra["corrected-mantra"]=item.get('corrected-mantra',"")
                        mantra["corrected-swara"]=item.get('corrected-swara',"")
                        data_corrected.remove(item)
                        break
                if len(data_corrected) ==0:
                    break
            if len(data_corrected) ==0:
                break
    if len(data_corrected) == 0:
        break


