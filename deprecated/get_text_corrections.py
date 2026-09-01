
import re
import json
import glob
import os

def parse_corrections_txt(input_txt):
    with open(input_txt, "r", encoding="utf-8") as f:
        lines = f.readlines()

    data = {}
    current_section = None
    current_subsection = None
    mantra_sets = []
    in_mantra = False
    section_re = re.compile(r'# Start of Section Title -- (section_\d+)')
    subsection_re = re.compile(r'# Start of SubSection Title -- (subsection_\d+)')
    subsection_end_re = re.compile(r'# End of SubSection Title -- (subsection_\d+)')
    mantra_start_re = re.compile(r'#Start of Mantra Sets -- (subsection_\d+)')
    mantra_end_re = re.compile(r'#End of Mantra Sets -- (subsection_\d+)')
    header_buffer = None
    in_header = False

    for idx, line in enumerate(lines):
        line = line.rstrip('\n')
        section_match = section_re.match(line)
        subsection_match = subsection_re.match(line)
        subsection_end_match = subsection_end_re.match(line)
        mantra_start_match = mantra_start_re.match(line)
        mantra_end_match = mantra_end_re.match(line)

        if section_match:
            current_section = section_match.group(1)
            if current_section not in data:
                data[current_section] = {"subsections": {}}
        elif subsection_match:
            current_subsection = subsection_match.group(1)
            data[current_section]["subsections"][current_subsection] = {"corrected-mantra_sets": []}
            header_buffer = []
            in_header = True
        elif subsection_end_match and in_header:
            header_text = " ".join([l.strip() for l in header_buffer if l.strip()])
            data[current_section]["subsections"][current_subsection]["header"] = {"header": header_text}
            in_header = False
            header_buffer = None
        elif in_header:
            header_buffer.append(line)
        elif mantra_start_match:
            in_mantra = True
            mantra_sets = []
        elif mantra_end_match:
            in_mantra = False
            for mantra in mantra_sets:
                mantra=mantra.replace(')', ') ')
                data[current_section]["subsections"][current_subsection]["corrected-mantra_sets"].append({
                    "corrected-mantra": mantra,
                    "corrected-swara": ""
                })
        elif in_mantra:
            if line.strip():
                mantra_sets.append(line.strip())
    return data

def main():
    input_dir = "output_text/txt/corrections/"
    output_json = "output_text/corrected-Devanagari-from-txt.json"
    all_data = {}
    for txt_file in sorted(glob.glob(os.path.join(input_dir, "corrections_*.txt"))):
        file_data = parse_corrections_txt(txt_file)
        # Merge file_data into all_data
        for section, section_val in file_data.items():
            if section not in all_data:
                all_data[section] = section_val
            else:
                # Merge subsections
                for subsec, subsec_val in section_val["subsections"].items():
                    all_data[section]["subsections"][subsec] = subsec_val
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    print(f"Wrote: {output_json}")

if __name__ == "__main__":
    main()
