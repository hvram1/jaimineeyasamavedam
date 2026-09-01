import json

# Input and output file paths
input_path = "output_text/intermediate-final-Devanagari.json"
output_path = "output_text/intermediate-final-Devanagari-with-corrected-mantra_sets.json"


def extract_corrected_mantra_sets(mantra_sets):
    corrected = []
    for mantra_set in mantra_sets:
        cm = mantra_set.get('corrected-mantra', None)
        cs = mantra_set.get('corrected-swara', None)
        corrected.append({
            'corrected-mantra': cm,
            'corrected-swara': cs
        })
        if cm and cs:
            del mantra_set['corrected-mantra']
            del mantra_set['corrected-swara']
    # Only return if at least one is not both None
    if any((x['corrected-mantra'] is not None or x['corrected-swara'] is not None) for x in corrected):
        
        return corrected
    else:
        return None

with open(input_path, "r", encoding="utf-8") as f:
    data = json.load(f)

supersections = data.get('supersection', {})

for supersection_key, supersection in supersections.items():
    sections = supersection.get('sections', {})
    for section_key, section in sections.items():
        subsections = section.get('subsections', {})
        for subsection_key, subsection in subsections.items():
            mantra_sets = subsection.get('mantra_sets', [])
            corrected_mantra_sets = extract_corrected_mantra_sets(mantra_sets)
            if corrected_mantra_sets is not None:
                subsection['corrected-mantra_sets'] = corrected_mantra_sets
            elif 'corrected-mantra_sets' in subsection:
                del subsection['corrected-mantra_sets']


with open(output_path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

print(f"Written: {output_path}")
