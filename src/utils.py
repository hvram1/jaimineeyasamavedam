import sys
from pathlib import Path
import json
import re
import os

# --- New Imports for Moved Functions ---
import grapheme
import urllib.parse
from requests.models import PreparedRequest
# --- End New Imports ---


import datetime

# --- Version and Metadata Utilities ---
VERSION_FILE = Path(__file__).parent / "VERSION"

def get_project_version():
    """Reads the current version from src/VERSION."""
    if VERSION_FILE.exists():
        try:
            return VERSION_FILE.read_text(encoding='utf-8').strip()
        except:
            pass
    return "3.0"

def increment_project_version():
    """Increments the minor version (y in x.y) in src/VERSION."""
    current_version = get_project_version()
    try:
        parts = current_version.split('.')
        if len(parts) >= 2:
            # Increment the last numerical part
            parts[-1] = str(int(parts[-1]) + 1)
            new_version = ".".join(parts)
        else:
            new_version = current_version + ".1"
            
        VERSION_FILE.write_text(new_version, encoding='utf-8')
        return new_version
    except Exception as e:
        print(f"[WARNING] Failed to increment version: {e}")
        return current_version

def set_project_version(version):
    """Manually sets the version in src/VERSION."""
    try:
        VERSION_FILE.write_text(version, encoding='utf-8')
        return True
    except Exception as e:
        print(f"[WARNING] Failed to set version: {e}")
        return False

def get_generated_metadata(increment=False):
    """Returns a dictionary with version and generation timestamp.
    If increment=True, rolls over the version number in src/VERSION.
    """
    version = increment_project_version() if increment else get_project_version()
    return {
        "version": version,
        "generated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

def inject_metadata_to_text(content, version, timestamp=None):
    """Prepends a standardized metadata block to the text content."""
    if not timestamp:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    metadata_block = [
        "# [JSV METADATA]",
        f"# Version: {version}",
        f"# Generated At: {timestamp}",
        "# [END METADATA]",
        ""
    ]
    
    # Remove any existing metadata block if present (at the start of file)
    clean_content = re.sub(r'^# \[JSV METADATA\].*?# \[END METADATA\]\s*', '', content, flags=re.DOTALL)
    
    return "\n".join(metadata_block) + clean_content

def extract_metadata_from_text(content):
    """Parses the metadata block from a text string."""
    # Default metadata
    meta = {
        "version": "3.0",
        "generated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    match = re.search(r'# \[JSV METADATA\].*?# Version:\s*(?P<version>.*?)\n.*?# Generated At:\s*(?P<at>.*?)\n.*?# \[END METADATA\]', content, re.DOTALL)
    if match:
        meta["version"] = match.group("version").strip()
        meta["generated_at"] = match.group("at").strip()
    
    return meta

def extract_closing_mantras(content):
    """
    Extracts closing mantra lines between # Closing Mantras and # End of Closing Mantras tags.
    Returns a list of cleaned lines.
    """
    if not content:
        return []
    
    closing_pattern = re.compile(r'# Closing Mantras\s*\n(.*?)\s*# End of Closing Mantras', re.DOTALL)
    closing_match = closing_pattern.search(content)
    if closing_match:
        return [line.strip() for line in closing_match.group(1).strip().split('\n') if line.strip()]
    return []

def devanagari_to_int(text):
    """Converts Devanagari numerals in a string to an integer."""
    if not text: return 0
    # Map Devanagari numerals to Western ones
    d_to_w = str.maketrans('०१२३४५६७८९', '0123456789')
    # Use only digits
    digits = re.sub(r'[^\d०-९]', '', text)
    if not digits: return 0
    return int(digits.translate(d_to_w))

def load_pipeline_config(config_path="src/pipeline_config.yaml"):
    """Loads the centralized YAML configuration file."""
    import yaml
    from pathlib import Path
    
    # Try to find config file relative to project root or current dir
    potential_paths = [
        Path(config_path),
        Path("src/pipeline_config.yaml"),
        Path(__file__).parent / "pipeline_config.yaml"
    ]
    
    for p in potential_paths:
        if p.exists():
            try:
                with open(p, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f)
            except Exception as e:
                print(f"[ERROR] Found config at {p} but failed to load: {e}")
    
    print(f"[WARNING] Centralized config file '{config_path}' not found. Using defaults.")
    return {}

# --- Functions Moved from renderPDF.py ---

# --- Original code from convert_txt_to_json_1.py starts here ---

def combine_halants(graphemes):
    """
    Combines sequences of halanted consonants with the following grapheme.
    e.g., ['पा', 'र्', 'त्', 'थी'] -> ['पा', 'र्त्थी']
    """
    # The Devanagari Halant/Virama character
    HALANT = '\u094D'
    
    result = []
    cluster_buffer = []

    for g in graphemes:
        # Check if the grapheme ends with a halant
        if g.endswith(HALANT):
            # If it is, add it to the buffer to build a cluster
            cluster_buffer.append(g)
        else:
            # This is a non-halanted grapheme (like 'पा' or 'थी')
            if cluster_buffer:
                # If we have a pending cluster, join it with this grapheme
                combined = "".join(cluster_buffer) + g
                result.append(combined)
                # Clear the buffer
                cluster_buffer = []
            else:
                # No pending cluster, just add the grapheme
                result.append(g)
    
    # If the string ended with a halant, add any remaining items
    if cluster_buffer:
        result.extend(cluster_buffer)
        
    return result


def combine_ardhaksharas(text):
    """
    Combine ardhaksharas (half consonants) with following characters to form complete units.
    For example: ग् + ना -> ग्ना as a single unit
    """
    grapheme_list = list(grapheme.graphemes(text))
    final_list = combine_halants(grapheme_list)        
    return final_list

def my_encodeURL(url,param1,value1,param2,value2):
    #x=urllib.parse.quote(URL)
    #print("URL is ",url, "param1 is ",param1,"value1 is ",value1,"param2 is ",param2,"value2 is ",value2)
    #x=urllib.parse.quote(url+"?"+param1+"="+value1+"&"+param2+"="+value2)
    req = PreparedRequest()
    params = {param1:value1,param2:value2}
    req.prepare_url(url, params)
    #print(req.url)
    return req.url

def my_format(my_number):
    my_int=int(my_number)
    my_string=f"{my_int:3d}"
    return my_string

def replacecolon(data):
    if isinstance(data,str):
        data=data.replace(":", "ः")
    return data

def normalize_and_trim(text):
    # 1. Normalize ASCII pipes to Devanagari single/double danda forms (optional)
    text = text.replace("||", "॥").replace("|", "।")
    # 2. Remove a sequence of danda/space that appears right after a sentence separator (like a dot or danda)
    #    e.g. ".... .॥ गौतम..."  ->  ".... .गौतम..."
    #    Pattern: (sep char) + optional spaces + 1+ danda-like chars + optional spaces  -> keep sep char only
    text = re.sub(r'([.\u0964\u0965])\s*[\u0964\u0965\|]+\s*', r'\1', text)
    # 3. Trim any remaining leading/trailing whitespace or danda-like characters
    text = re.sub(r'^[\s\|\u0964\u0965]+|[\s\|\u0964\u0965]+$', '', text)
    return text

def step_preprocess_visarga_accent(text):
    """
    Swaps Visarga (ः) with immediately following accent marker (1)/(2)/(3) etc.
    so the accent is applied to the preceding character (vowel) instead of the Visarga.
    Also ensures Visarga is attached to the preceding character.
    
    Input: "Word : (1)" -> "Word(1)ः"
    Input: "Word: (1)" -> "Word(1)ः" 
    Input: "Word ः (1)" -> "Word(1)ः"
    Input: "Wordः(1)" -> "Word(1)ः"
    Output: Rendered accent will now appear on 'd' (or implicit vowel), followed by Visarga.
    """
    if not text:
        return text
    
    # 1. Normalize colon to Visarga
    text = text.replace(':', 'ः')
    
    # 2. Remove space before Visarga (attach to preceding char)
    text = re.sub(r'\s+ः', 'ः', text)
    
    # 3. Swap Visarga and Accent (handling potential space between them)
    # Pattern: Visarga + optional space + (Accent)
    # accents are like (1), (2), (3), (4) or (cha), (ki) etc in Samam
    pattern = r'([ः])\s*(\([^)]+\))'
    # Replace with: Accent Marker first, then Visarga
    return re.sub(pattern, r'\2\1', text)

# --- End of Moved Functions ---

# --- NEW FUNCTION (Moved Logic from Step 2) ---

def parse_mantra_for_latex(subsection, supersection_title, section_title, subsection_title):
    # UPDATED: Removed pada_config from arguments
    
    # --- SAFETY FIX: Convert Undefined/None to empty strings ---
    def safe_str(s): return str(s) if s and 'Undefined' not in str(type(s)) else ''
    supersection_title = safe_str(supersection_title)
    section_title = safe_str(section_title)
    subsection_title = safe_str(subsection_title)
    # -------------------------------------------------------
    """
    Parses mantra text into rows of graphemes and swaras for LaTeX table rendering.
    This contains all the parsing logic, moved from renderPDF.format_mantra_sets.
    """
    mantra_number = "" # Will be captured by the loop

    mantra_sets = subsection.get('corrected-mantra_sets', [])
    
    # UPDATED: Removed logic for line_break_limit and config lookups
        
    # --- Combine all mantra lines into one single string ---
    full_mantra_string = ""
    for mantra_set in mantra_sets:
        full_mantra_string += mantra_set.get('corrected-mantra', "") + " "
    
    # --- Normalize Dandas for Parsing ---
    # Convert various forms (ASCII pipes, spaced pipes, double singles) to Standard Devanagari
    full_mantra_string = re.sub(r'\|\|', '॥', full_mantra_string)
    full_mantra_string = re.sub(r'\|\s*\|', '॥', full_mantra_string)
    full_mantra_string = re.sub(r'।।', '॥', full_mantra_string)
    full_mantra_string = full_mantra_string.replace('|', '।')
    
    # --- Main Parsing Logic ---
    all_mantra_rows = []
    all_swara_rows = []
    current_mantra_row = []
    current_swara_row = []
    # UPDATED: Removed pada_count
    i = 0
    
    while i < len(full_mantra_string):
        
        # 1. Handle whitespace (Capture it for Justification)
        if full_mantra_string[i].isspace():
            # We insert a specific marker to tell the renderer "This is a word break"
            current_mantra_row.append("SPACE_TOKEN")
            current_swara_row.append("{}") 
            i += 1
            continue
        
        # Handle visarga replacement           
        full_mantra_string = full_mantra_string.replace(":", "ः")    

        # 2. Check for danda
        if full_mantra_string[i] in '।॥|':
            number_match = re.match(r'॥\s*(\d+)\s*॥', full_mantra_string[i:])
            if number_match:
                mantra_number = f"॥ {number_match.group(1).strip()} ॥"            
                current_mantra_row.append(mantra_number)
                current_swara_row.append('{}')
                i += len(number_match.group(0))
                
                # Force line break on mantra number match
                all_mantra_rows.append(current_mantra_row)
                all_swara_rows.append(current_swara_row)
                current_mantra_row = []
                current_swara_row = []
            else:
                danda_token =  full_mantra_string[i] 
                current_mantra_row.append(danda_token)
                current_swara_row.append('{}')
                i += 1
            
            continue

        # 2.5 Explicitly Check for Footnote Token (sN) at start
        # e.g. (s2)Word... or Word(Swara)(s3) -> (s3)
        fn_match = re.match(r'\s*(\(s\d+\))', full_mantra_string[i:])
        if fn_match:
            # Found standalone footnote token
            fn_token = fn_match.group(1)
            current_mantra_row.append(f'{{{fn_token}}}')
            current_swara_row.append('{}')
            i += len(fn_match.group(0))
            continue
            
        # 3. Check for pattern: [Word] + (Swara) + Optional [Visarga/Colon]
        string_chk = full_mantra_string[i:]
        # Strict Regex: NO Parens in Word part
        # Updated to capture optional trailing Visarga/Colon (Group 3)
        match = re.match(r'\s*([^\s()।॥]+)\s*\(([^)]+)\)\s*([:ः]?)', string_chk)

        if match:
            mantra_word = match.group(1)
            swara_word = match.group(2)
            trailing_visarga = match.group(3)
            
            # Attach trailing visarga to the word if present
            if trailing_visarga:
                # Normalize just in case, though preprocessing should have done it
                trailing_visarga = trailing_visarga.replace(':', 'ः')
                mantra_word += trailing_visarga
            
            # (Removed the "Is logic Footnote" block since we handle (sN) separately now)
            
            mylist = combine_ardhaksharas(mantra_word) # Using local function
            
            if len(mylist) > 0:
                target_grapheme = mylist[-1]
                preceding_graphemes = ''.join(mylist[0:-1])

                if preceding_graphemes:
                    current_mantra_row.append(f'{{{preceding_graphemes}}}')
                    current_swara_row.append('{}') 

                current_mantra_row.append(f'{{{target_grapheme}}}')
                if swara_word:
                    current_swara_row.append(f'{{\\smallredfont {swara_word}}}')
                else:
                    current_swara_row.append('{}')
            else:
                current_mantra_row.append('{}')
                if swara_word:
                    current_swara_row.append(f'{{\\smallredfont {swara_word}}}')
                else:
                    current_swara_row.append('{}')

            match_start_index = full_mantra_string[i:].find(match.group(0))
            if match_start_index != -1:
                i += match_start_index + len(match.group(0))
            else:
                i += 1
        
        # 4. Continuous text block (no swara)
        else:
            token_start = i
            while i < len(full_mantra_string):
                # Break on space, danda, OR Start of Parentheses (potential swara/footnote)
                if full_mantra_string[i] in '।॥|' or full_mantra_string[i].isspace() or full_mantra_string[i] == '(':
                    break
                i += 1
            
            continuous_text = full_mantra_string[token_start:i].strip()
            
            if continuous_text:
                # Check if there is a previous item and it is NOT a Danda              
                if current_mantra_row and '।' not in current_mantra_row[-1] and '॥' not in current_mantra_row[-1] and "SPACE_TOKEN" not in current_mantra_row[-1]:
                    
                    # 1. Get the last entry from current_mantra_row     
                    existing_string = current_mantra_row[-1]
                    
                    # CHECK: Don't merge if the previous entry has a Swara!
                    # If it has a swara, we want the new text to be a separate token
                    # so the swara stays aligned only with its specific syllable.
                    prev_swara = current_swara_row[-1]
                    has_swara = prev_swara and prev_swara != '{}' and prev_swara != ''
                    
                    if has_swara:
                         # Append as a NEW separate token
                         current_mantra_row.append(f'{{{continuous_text}}}')
                         current_swara_row.append('{}')
                    else:
                        # 2. Clean it: Remove { and } to get raw text
                        raw_text = existing_string.replace('{', '').replace('}', '')
                        
                        # 3. Combine raw text with new tail
                        new_combined_string = raw_text + continuous_text
                        
                        # 4. Overwrite the last element
                        current_mantra_row[-1] = f'{{{new_combined_string}}}'
                    
                else:
                    # Fallback: Start of line OR previous item was a Danda 
                    # Append as a NEW separate token
                    current_mantra_row.append(f'{{{continuous_text}}}')
                    current_swara_row.append('{}')         
            if i == token_start:
                # We are stuck! (e.g. found '(' but it didn't match strict Word+Swara or Fn pattern)
                # It means we have an orphaned '(' or weird syntax.
                # Just consume one char to proceed
                current_mantra_row.append(f'{{{full_mantra_string[i]}}}')
                current_swara_row.append('{}')
                i += 1
        
    
    # Add any remaining items
    if current_mantra_row:
        all_mantra_rows.append(current_mantra_row)
        all_swara_rows.append(current_swara_row)

    # Return the raw row data for the formatter
    return all_mantra_rows, all_swara_rows

# --- End of NEW FUNCTION ---

def sanitize_data_structure(supersections):
    """
    Recursively cleans titles in the dictionary structure.
    - Replaces ':' with 'ः' in all titles.
    - Unifies various danda forms (||, ।।) to standard '॥'.
    """
    def normalize_header(text):
        if not text: return text
        # Normalize Visarga
        text = text.replace(':', 'ः')
        # Normalize Double Dandas
        text = re.sub(r'\|\|', '॥', text)       
        text = re.sub(r'\|\s*\|', '॥', text)    
        text = re.sub(r'।।', '॥', text)
        # Normalize Single Danda
        text = text.replace('|', '।')
        return text

    for ss_key, ss_val in supersections.items():
        # Clean Supersection Title
        if 'supersection_title' in ss_val:
            ss_val['supersection_title'] = normalize_header(ss_val['supersection_title'])

        # Clean Section Titles
        if 'sections' in ss_val:
            for s_key, s_data in ss_val['sections'].items():
                if s_key == 'count': continue
                if 'section_title' in s_data:
                    s_data['section_title'] = normalize_header(s_data['section_title'])
                    
                # Clean Subsection headers
                if 'subsections' in s_data:
                    for sub_key, sub_val in s_data['subsections'].items():
                        if 'header' in sub_val and 'header' in sub_val['header']:
                             sub_val['header']['header'] = normalize_header(sub_val['header']['header'])

    return supersections


def parse_mantra_set(mantra_set_text):
    """
    Parses a block of mantra set text into a list of mantra/swara dictionaries.
    Filters out tags.
    """
    mantra_sets = []
    
    # Split the text by newlines, filtering out empty lines and tag lines.
    mantras = [
        m.strip() 
        for m in mantra_set_text.split('\n') 
        if m.strip() and not m.strip().startswith('<') and not m.strip().startswith('#')
    ]
    
    for mantra in mantras:
        if mantra:
            # The entire line is placed in 'corrected-mantra', including inline swara markings.
            # Replacing danda characters with spaced versions for consistency
            mantra = mantra.replace('।', r' । ')
            
            # Apply Visarga/Accent corrections
            mantra = step_preprocess_visarga_accent(mantra)
            
            mantra_sets.append({
                "corrected-mantra": mantra,
                "corrected-swara": ""   
            })
            
    return mantra_sets

def convert_corrections_to_json(file_path="corrections_003.txt"):
    """
    Reads the text file, extracts hierarchical data using regex, and constructs 
    the final JSON object.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            file_content = f.read()
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found. Please ensure it is in the same directory.")
        return None

    meta = get_generated_metadata()
    json_output = {
        "meta": {
            "version": meta["version"],
            "generated_at": meta["generated_at"]
        },
        "supersection": {}
    }
    
    # --- 0. Helper to Extract Subsection-level Aux Data ---
    aux_data = {} # subsection_id -> {Key: Value}
    
    def extract_aux(pattern_str, key_name):
        pat = re.compile(pattern_str, re.DOTALL)
        for sub_id, content in pat.findall(file_content):
            sub_id = sub_id.strip()
            if sub_id not in aux_data: aux_data[sub_id] = {}
            aux_data[sub_id][key_name] = content.strip()

    # Regex patterns for Rik Metadata, Rik Text, and Footnotes
    extract_aux(r'# Start of Rik Metadata -- (subsection_\d+) ## DO NOT EDIT\s*(.*?)\s*# End of Rik Metadata -- \1 ## DO NOT EDIT', 'rik_metadata')
    extract_aux(r'# Start of Rik Text -- (subsection_\d+) ## DO NOT EDIT\s*(.*?)\s*# End of Rik Text -- \1 ## DO NOT EDIT', 'rik_text')
    extract_aux(r'# Start of Footnote -- (subsection_\d+) ## DO NOT EDIT\s*(.*?)\s*# End of Footnote -- \1 ## DO NOT EDIT', 'footnotes_raw')

    # --- 1. Extract ALL Supersections ---
    supersection_pattern = re.compile(
        r'# Start of SuperSection Title -- (supersection_\d+) ## DO NOT EDIT\s*'
        r'(.*?)'
        r'\s*# End of SuperSection Title -- \1 ## DO NOT EDIT\s*'
        r'(.*?)'
        r'(?=# Start of SuperSection Title -- supersection_\d+ ## DO NOT EDIT|$)',
        re.DOTALL
    )
    supersections_data = supersection_pattern.findall(file_content)
    
    if not supersections_data:
        print("Error: No supersection markers were found. Check file structure.")
        return None

    # Process each supersection
    for supersection_id, title_content, supersection_content in supersections_data:
        supersection_id = supersection_id.strip()
        
        # Extract and clean the title
        # Remove XML/HTML-style tags
        title_content = re.sub(r'<[^>]+>', '', title_content, flags=re.DOTALL)
        # Remove pipes (|| or ॥) and trim whitespace for the final title
        supersection_title = re.sub(r'[|॥\s]', '', title_content).strip()
        
        # Initialize the supersection object
        json_output["supersection"][supersection_id] = {
            "supersection_title": supersection_title,
            "sections": {}
        }
        current_supersection_sections = json_output["supersection"][supersection_id]["sections"]

        # --- 2. Extract Sections within this supersection ---
        section_pattern = re.compile(
            r'# Start of Section Title -- (section_\d+) ## DO NOT EDIT\s*'
            r'(.*?)'
            r'\s*# End of Section Title -- \1 ## DO NOT EDIT\s*'
            r'(.*?)'
            r'(?=# Start of Section Title -- section_\d+ ## DO NOT EDIT|# Start of SuperSection Title -- supersection_\d+ ## DO NOT EDIT|$)',
            re.DOTALL
        )
        sections_data = section_pattern.findall(supersection_content)
        
        # Calculate section count
        section_count_total = len(sections_data)
        current_supersection_sections["count"] = {
            "prev_count": 0,
            "current_count": section_count_total,
            "total_count": section_count_total
        }
        
        # --- 3. Extract Subsections and Mantra Sets within each section ---
        subsection_pattern = re.compile(
            r'# Start of SubSection Title -- (subsection_\d+) ## DO NOT EDIT\s*'
            r'(.*?)'
            r'\s*# End of SubSection Title -- \1 ## DO NOT EDIT'
            r'.*?'
            r'#Start of Mantra Sets -- \1 ## DO NOT EDIT\s*'
            r'(.*?)'
            r'\s*#End of Mantra Sets -- \1 ## DO NOT EDIT',
            re.DOTALL
        )

        for section_id, section_title_raw, section_content in sections_data:
            # Parse title and count from raw string if present
            # e.g. "Title (123)"
            m_count = re.match(r'(.*?)\s*\((.*?)\)$', section_title_raw.strip())
            if m_count:
                clean_section_title = m_count.group(1).strip()
                s_count = m_count.group(2).strip()
            else:
                clean_section_title = section_title_raw.strip()
                s_count = ""

            current_supersection_sections[section_id] = {
                "section_title": clean_section_title,
                "section_count": s_count,
                "subsections": {}
            }
            
            subsections_data = subsection_pattern.findall(section_content)
            
            for subsection_id, raw_header_text, mantra_set_content in subsections_data:
                # Clean up header text: remove tags, extra whitespace, and trailing markers
                clean_header_text = re.sub(r'<[^>]+>', '', raw_header_text.strip()).strip().rstrip('…|')
                
                # Retrieve Aux Data
                s_aux = aux_data.get(subsection_id, {})
                
                # Parse Footnotes
                footnotes = {}
                if 'footnotes_raw' in s_aux:
                    for line in s_aux['footnotes_raw'].split('\n'):
                        line = line.strip()
                        if not line: continue
                        m = re.match(r'(s\d+)\s*[-:]\s*(.*)', line)
                        if m:
                            footnotes[m.group(1)] = m.group(2)

                current_supersection_sections[section_id]["subsections"][subsection_id] = {
                    "corrected-mantra_sets": parse_mantra_set(mantra_set_content),
                    "header": {
                        "header": clean_header_text
                    },
                    "mantra_sets": [],
                    "rik_metadata": s_aux.get('rik_metadata', ''),
                    "rik_text": s_aux.get('rik_text', ''),
                    "saman_metadata": "",
                    "footnotes": footnotes
                }

    return json_output

if __name__ == "__main__":
    # Get the filename from command line argument
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        # Default fallback if no argument provided
        input_file = "corrections_003.txt"
    
    # These lines should be OUTSIDE the if/else block
    input_path = Path(input_file)
    output_file_path = input_path.stem + "_out.json"
    
    output_data = convert_corrections_to_json(input_file)
    
    if output_data:
        try:
            with open(output_file_path, 'w', encoding='utf-8') as outfile:
                json.dump(output_data, outfile, indent=4, ensure_ascii=False)
            print(f"Conversion complete! The structured data is saved to '{output_file_path}'")
        except IOError as e:
            print(f"Error writing to file: {e}")