import json
import sys





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
                    
     
  
# Save the updated data_final into another file
with open("output_text/updated-final-Devanagari.json", "w", encoding="utf-8") as f:
    json.dump(data_final_Devanagari, f, ensure_ascii=False, indent=4)         
sys.exit(1)


