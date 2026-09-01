import sys
from pathlib import Path
import json
import re
import os
import yaml
from utils import get_generated_metadata, step_preprocess_visarga_accent, load_pipeline_config, extract_metadata_from_text, extract_closing_mantras

def load_procedure_index(path="data/input/prayoga/prayoga_index.yaml"):
    """Load the procedure linking index from YAML file."""
    # Build lookup maps by scope
    index = {'supersection': {}, 'section': {}, 'subsection': {}}
    
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        for entry in data.get('procedures', []):
            scope = entry.get('scope', 'section')
            scope_id = entry.get('id', '')
            if scope_id:
                index[scope][scope_id] = {
                    'file': entry.get('file', ''),
                    'title': entry.get('title', ''),
                    'scope': scope,
                    'scope_id': scope_id
                }
    return index

def resolve_procedure(proc_index, supersection_id, section_id, subsection_id):
    """Resolve procedure ref: subsection > section > supersection."""
    if subsection_id in proc_index.get('subsection', {}):
        return proc_index['subsection'][subsection_id]
    if section_id in proc_index.get('section', {}):
        return proc_index['section'][section_id]
    if supersection_id in proc_index.get('supersection', {}):
        return proc_index['supersection'][supersection_id]
    return None


# --- Version and Metadata ---
metadata = get_generated_metadata()
JSV_VERSION = metadata['version']
GENERATED_AT = metadata['generated_at']

# --- 1. HELPER: Devanagari Digit Converter ---
def devanagari_to_int(text):
    """Converts Devanagari digits string to integer."""
    if not text: return None
    mapping = {'०':'0', '१':'1', '२':'2', '३':'3', '४':'4', 
               '५':'5', '६':'6', '७':'7', '८':'8', '९':'9'}
    converted = "".join([mapping.get(char, char) for char in text])
    try:
        return int(converted)
    except ValueError:
        return None

# --- 2. HELPER: Safe File Reader ---
def safe_read_file(file_path):
    if not os.path.exists(file_path):
        print(f"[WARNING] File '{file_path}' not found. Returning empty list.")
        return []
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        if "\n\n" in content:
             lines = [line.strip() for line in content.split('\n\n') if line.strip()]
        else:
             lines = [line.strip() for line in content.split('\n') if line.strip()]
    return lines

# --- 2.5. HELPER: Sanitize Invisible Characters ---
def sanitize_invisible_chars(text):
    """
    Remove invisible Unicode characters that can break pattern matching.
    These often get introduced when copy-pasting from web pages or PDFs.
    """
    if not text:
        return text
    # Characters to remove around footnote markers
    invisible_chars = [
        '\u200b',  # Zero-width space
        '\u200c',  # Zero-width non-joiner
        '\u200d',  # Zero-width joiner
        '\ufeff',  # BOM / Zero-width no-break space
        '\u2060',  # Word joiner
        '\u180e',  # Mongolian vowel separator
        '\u00ad',  # Soft hyphen
        '\u00a0',  # No-Break Space (NBSP)
    ]
    for char in invisible_chars:
        text = text.replace(char, '')
    
    return text


def parse_mantra_set(mantra_set_text):
    mantra_sets = []
    mantras = [
        m.strip() 
        for m in mantra_set_text.split('\n') 
        if m.strip() and not m.strip().startswith('<') and not m.strip().startswith('#')
    ]
    full_text = "\n".join(mantras)
    return mantras, full_text

# --- 3. CLASS: Rik Metadata Parser (ENHANCED) ---
class RikMetadataParser:
    """
    Parses rishi_devata_chandas_for_rik.txt with support for Rik-specific 
    Devata and Chandas overrides.
    
    Format: (1-10) 1 Rishi1 2 Rishi2...।। Devata।। 8 SpecialDevata।। Chandas।।
    
    Numbers before a name indicate Rik-specific assignment.
    Names without numbers are defaults for all Riks in that section.
    """
    
    def __init__(self, filepath):
        self.section_lines = []
        self.load_data(filepath)
        self.current_section_idx = -1
        self.current_section_idx = -1
        self.current_map = {} 

    def _split_ignoring_parens(self, text, pattern):
        """
        Splits text by regex pattern, but ignores matches inside parentheses.
        Returns a list of tokens similar to re.split, including valid delimiters.
        """
        # 1. Identify forbidden regions (inside parentheses)
        forbidden_ranges = []
        depth = 0
        start_idx = -1
        for i, char in enumerate(text):
            if char == '(':
                if depth == 0: start_idx = i
                depth += 1
            elif char == ')':
                depth -= 1
                if depth == 0 and start_idx != -1:
                    forbidden_ranges.append((start_idx, i))
                    start_idx = -1
        
        # 2. Find all matches of the pattern
        matches = list(pattern.finditer(text))
        
        # 3. Filter matches that overlap with forbidden regions
        valid_matches = []
        for m in matches:
            m_start, m_end = m.span()
            is_forbidden = False
            for f_start, f_end in forbidden_ranges:
                # If match starts inside a forbidden range
                if f_start < m_start < f_end:
                    is_forbidden = True
                    break
            if not is_forbidden:
                valid_matches.append(m)
        
        # 4. Construct tokens list
        tokens = []
        last_end = 0
        for m in valid_matches:
            # Text before the match
            tokens.append(text[last_end:m.start()])
            # The delimiter (capturing group 1 if present, else group 0)
            # The pattern is expected to be wrapped in a capturing group like (pattern)
            val = m.group(1) if m.re.groups > 0 else m.group(0)
            tokens.append(val)
            last_end = m.end()
        # Remaining text
        tokens.append(text[last_end:])
        
        return tokens

    def process_value_for_rik(self, text, rik_id):
        """
        Resolves conditional content inside parentheses for a specific Rik ID.
        Also cleans formatting labels like 'ऋषिः'.
        """
        if not text or '(' not in text:
            return text
            
        def replace_match(match):
            content = match.group(1)
            
            # Simple check: if no numbers, it's just text (applies to all)
            if not any(char.isdigit() for char in content):
                # Clean labels
                cleaned = re.sub(r'(?:ऋषिः|देवता|छन्दः)\s*', '', content).strip()
                return f"({cleaned})" if cleaned else ""
                
            # Parse inner content for overrides
            # 1. Default (text before first number)
            default_val = ""
            leading_match = re.match(r'^([^\d]+?)(?=\d|$)', content)
            if leading_match:
                default_val = leading_match.group(1).strip().rstrip(',').strip()
            
            # 2. Overrides (Number Val)
            overrides = {}
            pattern = re.compile(
                r'((?:\d+(?:\s*[,–-]\s*\d+)*(?:,\s*)?)+)\s+([^\d]+?)(?=\s*\d+(?:\s*[,–-]\s*\d+)*\s+[^\d]|$)'
            )
            # Use strict finditer on the inner content
            for m in pattern.finditer(content):
                num_str = m.group(1).strip()
                val = m.group(2).strip().rstrip(',').strip()
                if val:
                    for rid in self.parse_range_string(num_str):
                        overrides[rid] = val
                        
            # 3. Determine final value for this Rik ID
            parts = []
            
            # Add default value if present (cleaned)
            clean_default = re.sub(r'(?:ऋषिः|देवता|छन्दः)\s*', '', default_val).strip()
            if clean_default:
                parts.append(clean_default)
                
            # Add specific override if present (cleaned)
            if rik_id in overrides:
                clean_override = re.sub(r'(?:ऋषिः|देवता|छन्दः)\s*', '', overrides[rik_id]).strip()
                if clean_override:
                    parts.append(clean_override)
            
            if not parts:
                return ""
                
            return f"({' '.join(parts)})"

        # Apply replacement to all parenthesized blocks
        return re.sub(r'\(([^)]+)\)', replace_match, text)

    def load_data(self, filepath):
        if not os.path.exists(filepath):
            print(f"[WARNING] Rik Metadata file '{filepath}' not found.")
            return
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            # Also globally replace colons with Devanagari visargas during load
            self.section_lines = [line.strip().replace(':', 'ः') for line in f if line.strip() and not line.strip().startswith('#')]

    def parse_range_string(self, range_str):
        """Parse a range string like '1, 3, 5-8' into list of integers."""
        indices = []
        range_str = range_str.replace('–', '-').replace(' ', '')
        parts = range_str.split(',')
        for part in parts:
            if '-' in part:
                try:
                    subparts = part.split('-')
                    if len(subparts) == 2 and subparts[0] and subparts[1]:
                        start, end = int(subparts[0]), int(subparts[1])
                        indices.extend(range(start, end + 1))
                except ValueError: continue
            else:
                try:
                    if part: indices.append(int(part))
                except ValueError: continue
        return indices

    def parse_devata_chandas_section(self, section_text):
        """
        Parse a Devata or Chandas section for Rik-specific entries.
        Uses _split_ignoring_parens to robustly handle values that may contain numbers in parens.
        """
        if not section_text:
            return "", {}
        
        section_text = section_text.strip().strip('।|॥,').strip()
        if not section_text:
            return "", {}
        
        rik_specific_map = {}
        default_value = ""
        
        # Pattern for number groups: "1" or "1, 2" or "1-3, 5"
        # Must be wrapped in capturing group for split to return it
        num_pattern = re.compile(r'((?:\d+(?:\s*[,–-]\s*\d+)*(?:,\s*)?)+)')
        
        # Tokenize: [Text, NumGroup, Text, NumGroup, Text...]
        tokens = self._split_ignoring_parens(section_text, num_pattern)
        
        # The first token is the default value (if any)
        # However, due to regex, if it starts with number, first token is empty string
        # tokens[0] = Text before first number (Default)
        # tokens[1] = First Number Group
        # tokens[2] = Value for First Number Group
        # ...
        
        if tokens:
            # Clean up default value
            val = tokens[0].strip().rstrip(',').strip()
            if val:
                default_value = val
                
            # Iterate over pairs (Number, Value)
            for i in range(1, len(tokens) - 1, 2):
                num_str = tokens[i].strip()
                val_text = tokens[i+1].strip().rstrip(',').strip()
                
                # If val_text is empty, it might mean the number group continues or is malformed, 
                # but typically it means the value is empty.
                if val_text:
                    for rik_id in self.parse_range_string(num_str):
                        rik_specific_map[rik_id] = val_text
                        
        return default_value, rik_specific_map

    def parse_section_line(self, line):
        """
        Parse a full metadata line for a section (Kandah).
        
        Format examples:
        1) (1-10) 1 Rishi1 2 Rishi2...।। Devata।। Chandas।।
        2) (1-10) 1 Rishi1...।। Devata।। 8 OverrideDevata।। Chandas।।
        3) (1-10) 1 Rishi1...।। Default, 2 Override1 3 Override2।। Chandas।।
        
        Returns: {rik_id: "।। Rishi Devata Chandas ।।"} 
        """
        # 1. Extract Rik range from (1-10) prefix
        range_match = re.match(r'^\s*\(([\d\s–-]+)\)', line)
        rik_range = []
        if range_match:
            rik_range = self.parse_range_string(range_match.group(1))
            line = re.sub(r'^\s*\([\d\s–-]+\)', '', line).strip()
        
        # 2. Split by any multiple danda or pipe variant to separate Rishi, Devata, Chandas sections
        parts = re.split(r'\s*(?:[|॥।]\s*)+', line)
        
        # First part is Rishi section (before first danda group)
        rishi_section = parts[0] if parts else ""
        
        # Remaining parts are Devata and Chandas (after first danda group)
        suffix_parts = parts[1:] if len(parts) > 1 else []
        
        # 3. Parse Rishi section (numbers before names)
        # 3. Parse Rishi section (numbers before names)
        rishi_map = {}
        # Pattern matching number groups, ensuring they are separated
        num_group_pattern = re.compile(r'((?:\d+(?:\s*[–-]\s*\d+)*(?:,\s*)?)+)')
        
        # Use new split method to avoid splitting numbers inside parens
        tokens = self._split_ignoring_parens(rishi_section, num_group_pattern)
        
        # Handle implicit first rishi or normal structure
        default_rishi = ""
        if len(tokens) > 0 and tokens[0].strip():
             default_rishi = tokens[0].strip().rstrip(',').strip()
        
        for i in range(1, len(tokens), 2):
            num_str = tokens[i]
            name_text = tokens[i+1] if (i+1) < len(tokens) else ""
            name_text = name_text.strip().rstrip(',').strip()
            
            if name_text:
                for rik_id in self.parse_range_string(num_str):
                    rishi_map[rik_id] = name_text
        
        # If there's a default rishi found at start, fill in missing IDs
        if default_rishi:
            for rik_id in rik_range:
                if rik_id not in rishi_map:
                    rishi_map[rik_id] = default_rishi
        
        # 4. Parse Devata and Chandas sections
        # Key insight: The LAST non-empty part is Chandas, everything else is Devata
        devata_default, devata_specific = "", {}
        chandas_default, chandas_specific = "", {}
        
        # Clean and filter non-empty parts
        clean_suffix_parts = [p.strip().strip('।|॥') for p in suffix_parts if p.strip().strip('।|॥')]
        
        if len(clean_suffix_parts) == 0:
            # No Devata or Chandas
            pass
        elif len(clean_suffix_parts) == 1:
            # Single part - could be Devata only or Chandas only
            # Treat as Chandas (since that's typically the last field)
            chandas_default, chandas_specific = self.parse_devata_chandas_section(clean_suffix_parts[0])
        else:
            # Multiple parts: LAST is Chandas, rest are Devata
            # Combine all Devata parts (they might be split by ।।, e.g., "अग्निः ।। 8 इन्द्रः")
            devata_parts = clean_suffix_parts[:-1]
            chandas_part = clean_suffix_parts[-1]
            
            # Parse Chandas (last part)
            chandas_default, chandas_specific = self.parse_devata_chandas_section(chandas_part)
            
            # Parse Devata (all middle parts combined)
            # Each part may have default + overrides
            for part in devata_parts:
                part_default, part_specific = self.parse_devata_chandas_section(part)
                
                # First non-empty default becomes the Devata default
                if part_default and not devata_default:
                    devata_default = part_default
                
                # Merge all Rik-specific overrides
                devata_specific.update(part_specific)
        
        # 5. Build combined metadata map for each Rik
        meta_map = {}
        for rik_id in rik_range:
            # Get Rishi for this Rik (processed)
            rishi = self.process_value_for_rik(rishi_map.get(rik_id, ""), rik_id)
            
            # Get Devata for this Rik (specific or default, processed)
            devata = self.process_value_for_rik(devata_specific.get(rik_id, devata_default), rik_id)
            
            # Get Chandas for this Rik (specific or default, processed)
            chandas = self.process_value_for_rik(chandas_specific.get(rik_id, chandas_default), rik_id)
            
            # Build combined metadata string - only include non-empty parts
            parts_list = []
            if rishi:
                parts_list.append(rishi)
            if devata:
                parts_list.append(devata)
            if chandas:
                parts_list.append(chandas)
            
            if parts_list:
                meta_map[rik_id] = "।। " + " ".join(parts_list) + " ।।"
        
        return meta_map

    def advance_section(self):
        self.current_section_idx += 1
        if self.current_section_idx < len(self.section_lines):
            self.current_map = self.parse_section_line(self.section_lines[self.current_section_idx])
        else:
            self.current_map = {}

    def get_metadata_by_rik_id(self, rik_id):
        return self.current_map.get(rik_id, "")

# --- 4. CLASS: Rik Text Parser (ORIGINAL) ---
class RikTextParser:
    def __init__(self, filepath):
        self.sections = [] 
        self.current_section_idx = -1
        self.current_map = {}
        self.load_data(filepath)

    def load_data(self, filepath):
        if not os.path.exists(filepath):
            print(f"[WARNING] Rik Text file '{filepath}' not found.")
            return
        
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            content = f.read()

        # Strip Title and Supersection title markup blocks
        content = re.sub(r'#\s*Title\s*#.*?#\s*End of Title\s*#', '', content, flags=re.DOTALL)
        content = re.sub(r'#\s*Supersection title\s*#.*?#\s*End of Supersection title\s*#?', '', content, flags=re.DOTALL)
        # Also strip Iti (patha-end) markers so they don't produce false Rik matches
        content = re.sub(r'॥\s*इति[^॥]*॥', '', content)

        # Split by khanda/parva start markers (e.g. "॥ अथ प्रथमः खण्डः ॥" or "॥ अथ शाक्वर पर्वा ॥")
        # Handles single/double pipe variations used in Uttararchikam
        raw_sections = re.split(r'(?:॥|\|\|)?\s*अथ\s+[^॥|]+(?:खण्डः|पर्वा)\s*(?:\|\||॥)', content)
        # Pattern to match Rik text ending with ॥ num ॥
        # Captures text before the number and the Devanagari/Arabic numeral
        rik_pattern = re.compile(r'([^॥]+?)॥\s*([०-९\d]+)\s*॥')
        
        for block in raw_sections:
            if not block.strip(): 
                continue
            section_map = {}  # {rik_id: text}
            
            # Find all Rik entries in this section block
            for match in rik_pattern.finditer(block):
                raw_text = match.group(1).strip()
                rik_num_str = match.group(2)
                rik_id_int = devanagari_to_int(rik_num_str)
                
                # Skip header lines (e.g. patha/section titles).
                # Valid Riks usually have '।' (danda) as pada separators OR 
                # '(' swara markers. Headers have neither.
                # using OR ensures we catch:
                # 1. Unaccented Riks (have dandas)
                # 2. Short single-pada Riks (no internal dandas, but have accents)
                if '।' not in raw_text and '(' not in raw_text:
                    continue
                
                # Use raw_text as-is - no truncation needed
                # (Previously had logic to find first swara marker, but it was cutting off valid text)
                
                # Strip line number prefix (e.g., "12: ") if present at the start
                # The input file has format: "N: text ॥ num ॥"
                raw_text = re.sub(r'^\s*\d+:\s*', '', raw_text)
                
                clean_text = f"{raw_text} ॥ {rik_num_str} ॥"
                
                # Apply Visarga/Accent corrections
                # clean_text = step_preprocess_visarga_accent(clean_text)
                
                # Store by rik_id (overwrite if duplicate - take last occurrence)
                section_map[rik_id_int] = clean_text
            
            if section_map:
                self.sections.append(section_map)
                print(f"[INFO] RikTextParser Section {len(self.sections)}: Loaded {len(section_map)} unique Riks")

    def advance_section(self):
        self.current_section_idx += 1
        if self.current_section_idx < len(self.sections):
            self.current_map = self.sections[self.current_section_idx]
        else:
            self.current_map = {}

    def get_text_by_rik_id(self, rik_id):
        """Get rik text by rik_id. Returns None if not found."""
        if rik_id is None:
            return None
        return self.current_map.get(rik_id, None)

    def get_current_section_max_id(self):
        """Returns the maximum Rik ID in the current section, or 0 if empty/no section."""
        if not self.current_map:
            return 0
        return max(self.current_map.keys())

    
    def get_data_by_samam_id(self, samam_id_str):
        """Legacy method - kept for compatibility."""
        return None


# --- 4b. CLASS: Saman Metadata Parser (NEW) ---
class SamanMetadataParser:
    """Parses sama_rishi_chandas_out.txt and provides sequential samam access."""
    
    def __init__(self, filepath):
        self.sections = []  # List of lists: [(rik_id, title, metadata), ...]
        self.current_section_idx = -1
        self.current_samams = []  # Current section's samams in order
        self.samam_counter = 0    # Index into current_samams
        self.load_data(filepath)
    
    def load_data(self, filepath):
        if not os.path.exists(filepath):
            print(f"[WARNING] Saman Metadata file '{filepath}' not found.")
            return
        
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = [line.strip().replace(':', 'ः') for line in f if line.strip()]
        
        current_section = []  # List of (rik_id, title, metadata) tuples in order
        prev_rik_id = 0
        
        for line in lines:
            # Skip comment lines starting with #
            if line.startswith('#'):
                continue
            
            # Parse format: "RikId-SamamCount. [Title] ।। [Metadata] ।।"
            match = re.match(r'^(\d+)-(\d+)\.(.*)$', line)
            if not match:
                continue
            
            rik_id = int(match.group(1))
            samam_idx = int(match.group(2))
            rest = match.group(3).strip()
            
            # Detect section break: Rik ID resets to 1 after being higher
            if rik_id == 1 and prev_rik_id > 1 and current_section:
                self.sections.append(current_section)
                current_section = []
            
            prev_rik_id = rik_id
            
            # Extract title (part before ।।) and metadata (part after first ।।)
            title = ""
            metadata = ""
            if rest:
                # Split at first danda or pipe sequence (single or multiple, ASCII or Devanagari)
                split_pattern = r'\s*(?:[|॥।]\s*)+'
                parts = re.split(split_pattern, rest, maxsplit=1)
                # Title is the part before the delimiter
                title = parts[0].strip() if parts else ""
                if len(parts) > 1:
                    meta_part = parts[1].strip()
                    if meta_part:
                        # Clean and standardize danda wrapping
                        meta_part = re.sub(r'^[।|॥\s]+', '', meta_part)
                        meta_part = re.sub(r'[।|॥\s]+$', '', meta_part)
                            # Normalize internal pipes to Devanagari dandas
                        meta_part = meta_part.replace('||', '॥').replace('|', '।')
                        
                        if meta_part:
                            metadata = '।। ' + meta_part + ' ।।'

            # Store as (rik_id, title, metadata) tuple in order
            current_section.append((rik_id, title, metadata))
        
        # Don't forget the last section
        if current_section:
            self.sections.append(current_section)
        
        print(f"[INFO] Loaded {len(self.sections)} sections from Samam metadata file.")
        for i, sec in enumerate(self.sections):
            print(f"  Section {i+1}: {len(sec)} samams")
    
    def advance_section(self):
        """Move to next section, reset counter."""
        self.current_section_idx += 1
        if self.current_section_idx < len(self.sections):
            self.current_samams = self.sections[self.current_section_idx]
        else:
            self.current_samams = []
        self.samam_counter = 0
    
    def get_next_samam(self):
        """Get next samam's (rik_id, title, metadata). Returns (None, '', '') if exhausted."""
        if self.samam_counter >= len(self.current_samams):
            return (None, "", "")
        
        rik_id, title, metadata = self.current_samams[self.samam_counter]
        self.samam_counter += 1
        return (rik_id, title, metadata)
    
    def peek_next_samam(self):
        """Peek at next samam without advancing counter. Returns (rik_id, title, metadata) or (None, '', '')."""
        if self.samam_counter >= len(self.current_samams):
            return (None, "", "")
        return self.current_samams[self.samam_counter]
    
    def peek_rik_id(self):
        """Peek at current samam's rik_id without advancing counter."""
        if self.samam_counter >= len(self.current_samams):
            return None
        return self.current_samams[self.samam_counter][0]
    
    def get_metadata_for_rik(self, rik_id):
        """Get next available metadata for given Rik ID. Returns empty string if exhausted."""
        # Legacy method - kept for compatibility but not used in new flow
        return ""
    
    def get_remaining_for_rik(self, rik_id):
        """Get all remaining metadata for this Rik (for concatenation case)."""
        # Legacy method - kept for compatibility
        return []
    
    def count_remaining_for_rik(self, rik_id):
        """Count how many remaining samams (from current position) have the specified Rik ID."""
        count = 0
        for i in range(self.samam_counter, len(self.current_samams)):
            if self.current_samams[i][0] == rik_id:
                count += 1
            else:
                # Stop counting once we hit a different Rik ID
                break
        return count


# --- 5. MAIN CONVERSION LOGIC ---

def clean_rik_metadata_format(text):
    if not text: return ""
    text = " ".join(text.split())
    text = re.sub(r'[।|]+\s*$', '', text).strip()
    
    # Normalize pipes -> dandas
    text = text.replace('||', '॥').replace('|', '।')
    
    if not text: return ""
    return text + "।।"

def convert_corrections_to_json(
    file_path="data/input/Agneyam-Pavamanam_latest.txt",
    rik_meta_file="data/input/rishi_devata_chandas_for_rik.txt",
    saman_meta_file="data/input/sama_rishi_chandas_out.txt",
    rik_text_file="data/input/vedic_text.txt",
    title="Jaimineeya Samaveda Samhita Data"
):
    print(f"--- Step 1: Loading External Datasets ---")
    
    # Load pipeline config to find procedure index
    pipeline_cfg = load_pipeline_config()
    
    # CLI arg --procedures takes priority; if not specified, no procedures (default: no procedure)
    proc_index_file = args.procedures if args.procedures else None
    proc_index = {}
    if proc_index_file and os.path.exists(proc_index_file):
        proc_index = load_procedure_index(proc_index_file)
        print(f"[INFO] Loaded procedure index from {proc_index_file} with {sum(len(v) for v in proc_index.values())} entries.")
    else:
        print(f"[INFO] No procedure index specified (use --procedures to add).")
    
    rik_meta_parser = RikMetadataParser(rik_meta_file)
    rik_text_parser = RikTextParser(rik_text_file)
    saman_meta_parser = SamanMetadataParser(saman_meta_file)
    
    # NOTE: saman_meta_parser advances per section along with other parsers
    # since sama_rishi_chandas_out.txt now uses local Rik IDs per section

    print(f"--- Step 2: Parsing Structure from {file_path} ---")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            file_content = f.read()
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return None

    json_output = {
        "meta": {
            "version": JSV_VERSION,
            "generated_at": GENERATED_AT,
            "title": title
        },
        "supersection": {}
    }
    
    supersection_pattern = re.compile(r'# Start of SuperSection Title -- (supersection_\d+)\s*## DO NOT EDIT\s*(.*?)\s*# End of SuperSection Title -- \1\s*## DO NOT EDIT\s*(.*?)(?=# Start of SuperSection Title -- supersection_\d+|$)', re.DOTALL)
    section_pattern = re.compile(r'# Start of Section Title -- (section_\d+)\s*## DO NOT EDIT\s*(.*?)\s*# End of Section Title -- \1\s*## DO NOT EDIT\s*(.*?)(?=# Start of Section Title -- section_\d+|# Start of SuperSection Title -- supersection_\d+|$)', re.DOTALL)
    subsection_pattern = re.compile(r'# Start of SubSection Title -- (subsection_\d+)\s*## DO NOT EDIT\s*(.*?)\s*# End of SubSection Title -- \1\s*## DO NOT EDIT\s*#\s*Start of Mantra Sets -- \1\s*## DO NOT EDIT\s*(.*?)\s*#\s*End of Mantra Sets -- \1\s*## DO NOT EDIT', re.DOTALL)

    print(f"--- Step 2a: Extracting SuperSections ---")
    supersections_data = supersection_pattern.findall(file_content)
    
    if not supersections_data:
        print("[ERROR] No SuperSections found.")
        return None
    
    print(f"[INFO] Found {len(supersections_data)} SuperSection(s)")

    global_rik_offset = 0
    global_subsection_offset = 0

    for ss_idx, (supersection_id, title_content, supersection_content) in enumerate(supersections_data, 1):
        supersection_id = supersection_id.strip()
        title_content = re.sub(r'<[^>]+>', '', title_content, flags=re.DOTALL)
        supersection_title = re.sub(r'[|॥\s]', '', title_content).strip()
        
        print(f"\n--- Processing SuperSection {ss_idx}/{len(supersections_data)}: {supersection_title[:30]}... ---")
        
        json_output["supersection"][supersection_id] = {
            "supersection_title": supersection_title,
            "sections": {}
        }
        current_supersection_sections = json_output["supersection"][supersection_id]["sections"]
        
        print(f"  Extracting sections...")
        sections_data = section_pattern.findall(supersection_content)
        print(f"  Found {len(sections_data)} section(s)")
        
        section_count = len(sections_data)
        current_supersection_sections["count"] = { "prev_count": 0, "current_count": section_count, "total_count": section_count }
        
        for sec_idx, (section_id, section_title, section_content) in enumerate(sections_data, 1):
            # Update offset based on the section we are about to leave (if any)
            if rik_text_parser.current_section_idx >= 0:
                 section_max = rik_text_parser.get_current_section_max_id()
                 global_rik_offset += section_max

            # Advance ALL external parsers - they all use local Rik IDs per section now
            rik_meta_parser.advance_section()
            rik_text_parser.advance_section()
            saman_meta_parser.advance_section()  # Now advances per section (local Rik IDs)
            
            print(f"    Section {sec_idx}/{len(sections_data)}: {section_title.strip()[:40]}...", end=" ")

            
            clean_section_title = section_title.strip()
            
            subsections_data = subsection_pattern.findall(section_content)
            print(f"({len(subsections_data)} subsections)")
            
            # Count the total number of samams (mantras) in this section
            section_mantra_count = 0
            for _, _, mantra_set_content in subsections_data:
                # Need to use the same logic as the inner loop but just for counting
                m_list, full_text = parse_mantra_set(mantra_set_content)
                m_markers = re.findall(r'॥\s*[०-९\d]+\s*॥', full_text)
                section_mantra_count += len(m_markers) if m_markers else 1
                
            def int_to_devanagari_local(n):
                mapping = {'0':'०', '1':'१', '2':'२', '3':'३', '4':'४', '5':'५', '6':'६', '7':'७', '8':'८', '9':'९'}
                return "".join(mapping[c] for c in str(n))
                
            # Remove any manually appended count like "(२)" from title string if present
            clean_section_title = re.sub(r'\s*\([०-९\d]+\)$', '', clean_section_title).strip()
            
            current_supersection_sections[section_id] = {
                "section_title": clean_section_title,
                "Count": int_to_devanagari_local(section_mantra_count) if clean_section_title else "",
                "subsections": {}
            }
            
            current_section_subsection_count = 0
            
            # Track last known Rik values for carry-forward
            last_rik_id = None
            last_rik_text = None
            last_rik_meta = ""
            
            # Track titles used in this section to detect duplicate/continuation samams
            used_titles_in_section = set()
            
            for subsection_id, raw_header_text, mantra_set_content in subsections_data:
                current_section_subsection_count += 1
                
                clean_header_text = re.sub(r'<[^>]+>', '', raw_header_text.strip()).strip().rstrip('…|').replace(':', 'ः')
                
                # Apply Visarga/Accent corrections BEFORE parsing
                mantra_set_content = step_preprocess_visarga_accent(mantra_set_content)
                
                mantra_list, full_saman_text = parse_mantra_set(mantra_set_content)
                
                # Count how many mantras (samams) are in this subsection by finding mantra number markers (॥N॥)
                # Pattern matches Devanagari numerals enclosed in dandas: ॥१॥, ॥२॥, ॥१०॥, etc.
                mantra_markers = re.findall(r'॥\s*[०-९\d]+\s*॥', full_saman_text)
                num_mantras = len(mantra_markers) if mantra_markers else 1
                
                # --- 1. GET SAMAM METADATA FOR ALL MANTRAS IN THIS SUBSECTION ---
                # Consume 'num_mantras' entries from sama_rishi_chandas_out.txt
                # Also collect ALL unique Rik IDs and their text/metadata
                saman_meta_val = ""
                rik_id_from_saman = None
                
                # Track all unique Riks in this subsection for multi-Rik display
                rik_ids_in_subsection = []  # Ordered list of unique rik_ids
                
                for mantra_idx in range(num_mantras):
                    rik_id, saman_title, saman_meta = saman_meta_parser.get_next_samam()
                    
                    # Use the first valid rik_id as primary
                    if rik_id is not None and rik_id_from_saman is None:
                        rik_id_from_saman = rik_id
                    
                    # Track all unique rik_ids in order of appearance
                    if rik_id is not None and rik_id not in rik_ids_in_subsection:
                        rik_ids_in_subsection.append(rik_id)
                    
                    # Concatenate metadata from all samams
                    if saman_meta:
                        saman_meta_val = (saman_meta_val + " " + saman_meta).strip() if saman_meta_val else saman_meta

                
                # --- 3. DETERMINE RIK_TEXT AND RIK_METADATA ---
                # Build combined rik_text and rik_metadata for ALL Riks in this subsection
                all_rik_texts = []
                all_rik_metas = []
                
                if rik_ids_in_subsection:
                    for rid in rik_ids_in_subsection:
                        # Get Rik text
                        rik_txt = rik_text_parser.get_text_by_rik_id(rid)
                        # Get Rik metadata
                        raw_meta = rik_meta_parser.get_metadata_by_rik_id(rid)
                        cleaned_meta = clean_rik_metadata_format(raw_meta) if rik_txt else ""
                        
                        if rik_txt:
                            all_rik_texts.append(rik_txt)
                        if cleaned_meta:
                            all_rik_metas.append(cleaned_meta)
                        
                        # Update carry-forward tracking
                        if rid != last_rik_id:
                            last_rik_id = rid
                            last_rik_text = rik_txt
                            last_rik_meta = raw_meta
                    
                    # Join all Rik texts with separator for display
                    display_rik_text = "\n".join(all_rik_texts) if all_rik_texts else None
                    rik_meta_val = " ".join(all_rik_metas) if all_rik_metas else ""
                    
                elif rik_id_from_saman is not None:
                    # Single Rik case (backward compatibility)
                    local_rik_id = rik_id_from_saman
                    display_rik_text = rik_text_parser.get_text_by_rik_id(local_rik_id)
                    raw_rik_meta = rik_meta_parser.get_metadata_by_rik_id(rik_id_from_saman)
                    
                    if rik_id_from_saman != last_rik_id:
                        last_rik_id = rik_id_from_saman
                        last_rik_text = display_rik_text
                        last_rik_meta = raw_rik_meta
                    
                    rik_meta_val = clean_rik_metadata_format(raw_rik_meta)
                    if not display_rik_text:
                        rik_meta_val = ""
                else:
                    # No saman metadata - use carry-forward
                    rik_id_from_saman = last_rik_id
                    display_rik_text = last_rik_text
                    raw_rik_meta = last_rik_meta
                    saman_meta_val = ""
                    rik_meta_val = clean_rik_metadata_format(raw_rik_meta) if display_rik_text else ""

                # --- NEW: Apply Visarga Preprocessing globally ---
                # Only process text fields, skip metadata fields to preserve parens as requested
                # display_rik_text = step_preprocess_visarga_accent(display_rik_text)
                full_saman_text = step_preprocess_visarga_accent(full_saman_text)
                # -----------------------------------------------

                # --- CHECK FOR EXISTING SUBSECTION (MERGE MODE) ---
                if subsection_id in current_supersection_sections[section_id]["subsections"]:
                    existing_entry = current_supersection_sections[section_id]["subsections"][subsection_id]
                    
                    # 1. Append mantra set
                    existing_entry["corrected-mantra_sets"].append({
                        "corrected-mantra": full_saman_text, 
                        "corrected-swara": ""
                    })
                    
                    # 2. Merge Rik IDs (preserve order, unique)
                    for rid in rik_ids_in_subsection:
                        if rid not in existing_entry["rik_ids"]:
                            existing_entry["rik_ids"].append(rid)
                            
                    # 3. Update Rik Metadata and Text (Re-generate based on merged IDs)
                    # Note: This is slightly expensive but safe. Or we can just append if we trust the order.
                    # Let's just append the new text/metadata if it's new.
                    
                    # Simple Append Strategy for Metadata strings
                    if rik_meta_val and rik_meta_val not in existing_entry["rik_metadata"]:
                         existing_entry["rik_metadata"] = (existing_entry["rik_metadata"] + " " + rik_meta_val).strip()
                         
                    if display_rik_text:
                        # For text, we might want to be careful not to duplicate if it's the exact same Rik
                        # But if it's a new Rik, we append.
                        # Since we re-generated display_rik_text for the current block, we can append it.
                        if existing_entry["rik_text"]:
                            existing_entry["rik_text"] += "\n" + display_rik_text
                        else:
                            existing_entry["rik_text"] = display_rik_text

                    # 4. Merge Saman Metadata
                    if saman_meta_val:
                        if existing_entry["saman_metadata"]:
                            existing_entry["saman_metadata"] += " " + saman_meta_val
                        else:
                            existing_entry["saman_metadata"] = saman_meta_val
                            
                else:
                    # --- NEW ENTRY ---
                    current_supersection_sections[section_id]["subsections"][subsection_id] = {
                        "header": { "header": clean_header_text },
                        "rik_id": rik_id_from_saman,
                        "rik_ids": rik_ids_in_subsection,  
                        "rik_metadata": rik_meta_val,     
                        "rik_text": display_rik_text,     
                        "saman_metadata": saman_meta_val, 
                        "corrected-mantra_sets": [{
                            "corrected-mantra": full_saman_text, 
                            "corrected-swara": ""
                        }],
                        "mantra_sets": [],
                        "procedure_ref": resolve_procedure(proc_index, supersection_id, section_id, subsection_id)
                    }
            

            global_subsection_offset += current_section_subsection_count

    # --- Extract Closing Mantras ---
    json_output["closing_mantras"] = extract_closing_mantras(file_content)
    if json_output["closing_mantras"]:
        print(f"[INFO] Extracted {len(json_output['closing_mantras'])} closing mantra lines.")

    print(f"\n--- Step 3: Processing Complete ---")
    print(f"[INFO] Total subsections processed: {global_subsection_offset}")
    return json_output

def extract_rik_only_data(combined_data):
    """Extract only Rik-related content from combined data."""
    rik_data = {"supersection": {}}
    
    for ss_id, ss_content in combined_data.get("supersection", {}).items():
        rik_data["supersection"][ss_id] = {
            "supersection_title": ss_content.get("supersection_title", ""),
            "sections": {}
        }
        
        for sec_id, sec_content in ss_content.get("sections", {}).items():
            if sec_id == "count":
                rik_data["supersection"][ss_id]["sections"]["count"] = sec_content
                continue
                
            rik_data["supersection"][ss_id]["sections"][sec_id] = {
                "section_title": sec_content.get("section_title", ""),
                "section_count": sec_content.get("section_count", ""),
                "subsections": {}
            }
            
            # Track unique Rik IDs to avoid duplicates
            seen_rik_ids = set()
            
            for sub_id, sub_content in sec_content.get("subsections", {}).items():
                rik_id = sub_content.get("rik_id")
                
                # Skip if we've already seen this Rik ID
                if rik_id in seen_rik_ids:
                    continue
                seen_rik_ids.add(rik_id)
                
                rik_data["supersection"][ss_id]["sections"][sec_id]["subsections"][sub_id] = {
                    "header": sub_content.get("header", {"header": f"Rik {rik_id}"}),
                    "rik_id": rik_id,
                    "rik_metadata": s_aux.get('rik_metadata', None),
                    "rik_text": s_aux.get('rik_text', None),
                    "saman_metadata": "",  # Empty for Rik-only
                    "corrected-mantra_sets": [],  # Empty for Rik-only
                    "mantra_sets": [],  # Empty for Rik-only
                }
    
    return rik_data


def extract_samam_only_data(combined_data):
    """Extract only Samam-related content from combined data."""
    samam_data = {"supersection": {}}
    
    for ss_id, ss_content in combined_data.get("supersection", {}).items():
        samam_data["supersection"][ss_id] = {
            "supersection_title": ss_content.get("supersection_title", ""),
            "sections": {}
        }
        
        for sec_id, sec_content in ss_content.get("sections", {}).items():
            if sec_id == "count":
                samam_data["supersection"][ss_id]["sections"]["count"] = sec_content
                continue
                
            samam_data["supersection"][ss_id]["sections"][sec_id] = {
                "section_title": sec_content.get("section_title", ""),
                "section_count": sec_content.get("section_count", ""),
                "subsections": {}
            }
            
            for sub_id, sub_content in sec_content.get("subsections", {}).items():
                samam_data["supersection"][ss_id]["sections"][sec_id]["subsections"][sub_id] = {
                    "header": sub_content.get("header", {}),
                    "saman_metadata": sub_content.get("saman_metadata", ""),
                    "corrected-mantra_sets": sub_content.get("corrected-mantra_sets", []),
                    "mantra_sets": sub_content.get("mantra_sets", []),
                }
    
    return samam_data


# --- UNICODE TEXT FILE PARSER (for correction cycle) ---
def parse_unicode_text_file(filepath, metadata_file_path=None, title="Jaimineeya Samaveda Samhita Data"):
    """
    Parses the unicode text file produced by convert_corrections_to_json.
    Reconstructs the JSON structure.
    Uses # Start/End markers to identify sections.
    Optionally enriches with metadata from CSV.
    """
    
    if not os.path.exists(filepath):
        print(f"[ERROR] Unicode file '{filepath}' not found.")
        return None
    
    # Load procedure index - CLI arg takes priority; if not specified, no procedures
    pipeline_cfg = load_pipeline_config()
    proc_index_file = args.procedures if args.procedures else None
    proc_index = {}
    if proc_index_file and os.path.exists(proc_index_file):
        proc_index = load_procedure_index(proc_index_file)
        print(f"[INFO] Loaded procedure index from {proc_index_file} with {sum(len(v) for v in proc_index.values())} entries.")
    else:
        print(f"[INFO] No procedure index specified (use --procedures to add).")

    
    import csv 
    import re
    
    # --- Load Metadata (XLSX, TXT, or CSV) ---
    metadata_data = {}
    if metadata_file_path:
        if os.path.exists(metadata_file_path):
            try:
                # 1. Excel (.xlsx) - Recommended for editing
                if metadata_file_path.lower().endswith('.xlsx'):
                    try:
                        import openpyxl
                        wb = openpyxl.load_workbook(metadata_file_path, data_only=True)
                        ws = wb.active
                        
                        # Find Header Row (Scan first 5 rows)
                        header_row_idx = 1
                        headers = {}
                        found_header = False
                        
                        for r_idx, row in enumerate(ws.iter_rows(max_row=5, values_only=True), 1):
                            if row and 'Global_Samam_Num' in row:
                                header_row_idx = r_idx
                                for c_idx, val in enumerate(row):
                                    if val: headers[val] = c_idx
                                found_header = True
                                break
                        
                        if found_header:
                            for row in ws.iter_rows(min_row=header_row_idx+1, values_only=True):
                                if not row: continue
                                try:
                                    gsn_idx = headers.get('Global_Samam_Num')
                                    if gsn_idx is not None and row[gsn_idx] is not None:
                                        key = int(row[gsn_idx])
                                        row_data = {}
                                        for h_name, h_idx in headers.items():
                                            val = row[h_idx]
                                            row_data[h_name] = str(val) if val is not None else ''
                                        metadata_data[key] = row_data
                                except (ValueError, IndexError):
                                    continue
                            print(f"[INFO] Loaded metadata for {len(metadata_data)} samams from Excel (.xlsx).")
                        else:
                            print("[ERROR] Could not find header 'Global_Samam_Num' in first 5 rows of Excel file.")
                    except ImportError:
                        print("[ERROR] 'openpyxl' library missing. Install it to read .xlsx files, or save as .txt.")

                # 2. Text (.txt) - Excel "Unicode Text" (Tab-delimited, likely UTF-16)
                elif metadata_file_path.lower().endswith('.txt'):
                    encoding = 'utf-16'
                    delimiter = '\t'
                    # Try UTF-16 first (standard for Excel Unicode Text)
                    try:
                        with open(metadata_file_path, 'r', encoding=encoding) as f:
                            # Verify if readable
                            f.readline()
                            f.seek(0)
                            reader = csv.DictReader(f, delimiter=delimiter)
                            for row in reader:
                                try:
                                    k_str = row.get('Global_Samam_Num', '').strip()
                                    if k_str:
                                        metadata_data[int(k_str)] = row
                                except ValueError: continue
                    except UnicodeError:
                         # Fallback to UTF-8
                         print("[INFO] UTF-16 read failed for .txt, trying UTF-8...")
                         with open(metadata_file_path, 'r', encoding='utf-8') as f:
                            reader = csv.DictReader(f, delimiter=delimiter)
                            for row in reader:
                                try:
                                    k_str = row.get('Global_Samam_Num', '').strip()
                                    if k_str:
                                        metadata_data[int(k_str)] = row
                                except ValueError: continue
                    print(f"[INFO] Loaded metadata for {len(metadata_data)} samams from Text file (.txt).")

                # 3. CSV (.csv) - Legacy/Programmatic
                else:
                    with open(metadata_file_path, 'r', encoding='utf-8-sig') as f:
                        first_line = f.readline()
                        if not first_line.startswith('Global_Samam_Num'):
                             pass # Skip non-header first line if present
                        else:
                             f.seek(0)
                        
                        reader = csv.DictReader(f)
                        for row in reader:
                            try:
                                key = int(row['Global_Samam_Num'])
                                metadata_data[key] = row
                            except (ValueError, KeyError):
                                continue
                    print(f"[INFO] Loaded metadata for {len(metadata_data)} samams from CSV.")

            except Exception as e:
                print(f"[ERROR] Failed to load Metadata file: {e}")
        else:
             print(f"[ERROR] Metadata file not found: {metadata_file_path}")
    # -------------------------------------

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # GLOBAL SANITIZATION: Remove invisible characters from the entire file content
    content = sanitize_invisible_chars(content)
    
    # Initialize data structure from file metadata if present
    file_meta = extract_metadata_from_text(content)
    data = {
        "meta": {
            "version": file_meta.get("version", JSV_VERSION),
            "generated_at": GENERATED_AT,
            "title": title
        },
        "supersection": {}
    }
    
    # Patterns for matching markers (use \s* to handle hand-edited markers like 'supersection_22##')
    ss_regex = r'#\s*Start\s+of\s+SuperSection\s+Title\s+--\s+(?P<ss_id>.*?)\s*##\s*DO\s+NOT\s+EDIT'
    sec_regex = r'#\s*Start\s+of\s+Section\s+Title\s+--\s+(?P<sec_id>.*?)\s*##\s*DO\s+NOT\s+EDIT'
    sub_regex = r'#\s*Start\s+of\s+SubSection\s+Title\s+--\s+(?P<sub_id>.*?)\s*##\s*DO\s+NOT\s+EDIT'
    mantra_regex = r'#\s*Start\s+of\s+Mantra\s+Sets\s+--\s+(?P<mantra_id>.*?)\s*##\s*DO\s+NOT\s+EDIT'
    
    supersection_pattern = re.compile(
        ss_regex + r'\s*\n(?P<ss_title>.*?)\s*#\s*End\s+of\s+SuperSection\s+Title\s+--\s+(?P=ss_id)', 
        re.MULTILINE | re.DOTALL
    )
    section_pattern = re.compile(
        sec_regex + r'\s*\n(?P<sec_title>.*?)\s*#\s*End\s+of\s+Section\s+Title\s+--\s+(?P=sec_id)', 
        re.MULTILINE | re.DOTALL
    )
    rik_metadata_pattern = re.compile(
        r'#\s*Start\s+of\s+Rik\s+Metadata\s+--\s+(?P<rik_meta_id>.*?)\s*##\s*DO\s+NOT\s+EDIT\s*\n(?P<rik_meta_text>.*?)\s*#\s*End\s+of\s+Rik\s+Metadata', 
        re.MULTILINE | re.DOTALL
    )
    rik_text_pattern = re.compile(
        r'#\s*Start\s+of\s+Rik\s+Text\s+--\s+(?P<rik_text_id>.*?)\s*##\s+DO\s+NOT\s+EDIT\s*\n(?P<rik_text>.*?)\s*#\s*End\s+of\s+Rik\s+Text', 
        re.MULTILINE | re.DOTALL
    )
    subsection_pattern = re.compile(
        sub_regex + r'\s*\n(?P<sub_title>.*?)\s*#\s*End\s+of\s+SubSection\s+Title\s+--\s+(?P=sub_id)', 
        re.MULTILINE | re.DOTALL
    )
    mantra_pattern = re.compile(
        mantra_regex + r'\s*\n(?P<mantra_text>.*?)\s*#\s*End\s+of\s+Mantra\s+Sets\s+--\s+(?P=mantra_id)', 
        re.MULTILINE | re.DOTALL
    )
    saman_metadata_pattern = re.compile(
        r'#\s*Start\s+of\s+(?:Samam|Saman)\s+Metadata\s+--\s+(?P<saman_meta_id>.*?)\s*##\s*DO\s+NOT\s+EDIT\s*\n(?P<saman_meta_text>.*?)\s*#\s*End\s+of\s+(?:Samam|Saman)\s+Metadata', 
        re.MULTILINE | re.DOTALL
    )
    
    # Extract supersections
    for ss_match in supersection_pattern.finditer(content):
        ss_id = ss_match.group("ss_id")
        ss_title = ss_match.group("ss_title").strip()
        # Normalize titles (visargas and pipes) since we removed global colon replacement
        ss_title = ss_title.replace(':', 'ः').replace('||', '॥').replace('|', '।')
        data["supersection"][ss_id] = {
            "supersection_title": ss_title,
            "sections": {}
        }

    
    # Build section-to-supersection mapping by scanning file order
    section_to_supersection = {}
    # Build section-to-supersection mapping by scanning file order sequentially
    for line in content.split('\n'):
        line = line.strip()
        ss_match = re.search(r'#\s*Start\s+of\s+SuperSection\s+Title\s+--\s+(.*?)\s*##\s*DO\s+NOT\s+EDIT', line)
        if ss_match:
            current_supersection = ss_match.group(1).strip()
        sec_match = re.search(r'#\s*Start\s+of\s+Section\s+Title\s+--\s+(.*?)\s*##\s*DO\s+NOT\s+EDIT', line)
        if sec_match and current_supersection:
            section_to_supersection[sec_match.group(1).strip()] = current_supersection
    
    # Extract sections and assign to correct supersection
    for sec_match in section_pattern.finditer(content):
        sec_id = sec_match.group("sec_id")
        sec_title = sec_match.group("sec_title").strip()
        # Normalize titles
        sec_title = sec_title.replace(':', 'ः').replace('||', '॥').replace('|', '।')
        # Use the mapping to find the correct supersection
        ss_id = section_to_supersection.get(sec_id, 'supersection_1')
        if ss_id in data["supersection"]:
            data["supersection"][ss_id]["sections"][sec_id] = {
                "section_title": sec_title,
                "subsections": {}
            }

    
    # Extract Rik metadata for each subsection
    rik_metadata_map = {}
    for rm_match in rik_metadata_pattern.finditer(content):
        sub_id = rm_match.group("rik_meta_id")
        raw_meta = rm_match.group("rik_meta_text").strip()
        
        # FEATURE: Handle quoted literals for "exactly as given" metadata
        if raw_meta.startswith('"') and raw_meta.endswith('"'):
            # Extract content between quotes, preserve everything else (no normalization)
            meta_text = raw_meta[1:-1]
            # Replace inner newlines with space to maintain JSON structure, but keep everything else
            meta_text = meta_text.replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ')
        else:
            # Normal processing for unquoted metadata - preserve newlines for multi-verse Arsheyams
            meta_text = raw_meta.strip()
            # Strip any literal \newline commands that may have crept in
            meta_text = meta_text.replace('\\newline%', ' ').replace('\\newline', ' ')
            # Normalize pipes
            meta_text = meta_text.replace('||', '॥').replace('|', '।')
            # Normalize colon to visarga for unquoted metadata
            meta_text = meta_text.replace(':', 'ः')
            
        rik_metadata_map[sub_id] = meta_text

    
    # Extract Rik text for each subsection
    rik_text_map = {}
    for rt_match in rik_text_pattern.finditer(content):
        # ... existing extraction ...
        sub_id = rt_match.group("rik_text_id")
        # Sanitize Rik text: preserve newlines (required for multi-verse identification), 
        # but remove backslashes and literal \newline commands
        rik_text = rt_match.group("rik_text").strip().replace('\r\n', '\n').replace('\r', '\n')
        rik_text = rik_text.replace('\\newline%', ' ').replace('\\newline', ' ').replace('\\', '')
        # Normalize pipes for Rik text as well (as per "visarga handling" pattern)
        rik_text = rik_text.replace('||', '॥').replace('|', '।')
        # Apply Visarga Accent Preprocessing
        # rik_text = step_preprocess_visarga_accent(rik_text)
        rik_text_map[sub_id] = rik_text
    
    # Extract subsection headers (Samam header + metadata)
    subsection_headers = {}
    for sub_match in subsection_pattern.finditer(content):
        sub_id = sub_match.group("sub_id")
        header_line = sub_match.group("sub_title").strip()
        # Sanitize header line to remove NBSP
        header_line = sanitize_invisible_chars(header_line)
        # Split header and saman_metadata (they're separated by double space)
        parts = header_line.split('  ', 1)
        header = parts[0].strip()
        saman_metadata = parts[1].strip() if len(parts) > 1 else ""
        # Normalize headers and saman_metadata (visargas and pipes)
        header = header.replace(':', 'ः').replace('||', '॥').replace('|', '।')
        saman_metadata = saman_metadata.replace(':', 'ः').replace('||', '॥').replace('|', '।')
        subsection_headers[sub_id] = {"header": header, "saman_metadata": saman_metadata}

    
    # Extract Saman / Samam metadata for each subsection
    saman_metadata_map = {}
    for sm_match in saman_metadata_pattern.finditer(content):
        sub_id = sm_match.group("saman_meta_id").strip()
        raw_meta = sm_match.group("saman_meta_text").strip()
        raw_meta = raw_meta.replace(':', 'ः').replace('||', '॥').replace('|', '।')
        saman_metadata_map[sub_id] = raw_meta

    # Extract mantra sets
    mantra_sets_map = {}
    for m_match in mantra_pattern.finditer(content):
        sub_id = m_match.group("mantra_id")
        # Capture raw mantra text first
        mantra_text_raw = m_match.group("mantra_text")
        
        # Sanitize invisible characters (Redundant if global is done, but keeps logic localized/independent)
        # Also normalize pipes/dandas as requested ("visarga handling" interpreted as punctuation normalization)
        mantra_text = sanitize_invisible_chars(mantra_text_raw.strip())
        mantra_text = re.sub(r'\(\|\|?\)', lambda m: '(__PIPE__)' if len(m.group(0)) == 3 else '(__DBLPIPE__)', mantra_text)
        mantra_text = mantra_text.replace('||', '॥').replace('|', '।')
        mantra_text = mantra_text.replace('(__PIPE__)', '(|)').replace('(__DBLPIPE__)', '(||)')
        # Apply Visarga Accent Preprocessing
        mantra_text = step_preprocess_visarga_accent(mantra_text)
        
        # Parse mantras - each line is part of the mantra content
        mantras = [line.strip() for line in mantra_text.split('\n') if line.strip()]
        
        # Append to existing mantras if subsection already encountered (handle split blocks)
        if sub_id in mantra_sets_map:
            mantra_sets_map[sub_id].extend(mantras)
        else:
            mantra_sets_map[sub_id] = mantras
    
    # Extract footnotes
    footnote_pattern = re.compile(
        r'#\s*Start of Footnote -- (\S+)\s+## DO NOT EDIT\s*\n(.*?)\s*\n#\s*End of Footnote',
        re.MULTILINE | re.DOTALL
    )
    footnotes_map = {}
    for fn_match in footnote_pattern.finditer(content):
        sub_id = fn_match.group(1)
        footnote_text = fn_match.group(2).strip()
        # Parse footnotes: "s1 - footnote text" or "s1: footnote text" or "s1 : footnote text"
        footnotes = {}
        for line in footnote_text.split('\n'):
            line = line.strip()
            if not line: continue
            
            # Try to match sN separator text
            # Separator can be - or :
            m_fn = re.match(r'^(s\d+)\s*[-:]\s*(.*)$', line)
            if m_fn:
                key = m_fn.group(1).strip()
                text = m_fn.group(2).strip()
                footnotes[key] = text
        if footnotes:
            footnotes_map[sub_id] = footnotes
    
    # Build subsection-to-section mapping
    subsection_to_section = {}
    current_section = None
    for line in content.split('\n'):
        line = line.strip()
        sec_match = re.search(r'#\s*Start\s+of\s+Section\s+Title\s+--\s+(.*?)\s*##\s*DO\s+NOT\s+EDIT', line)
        if sec_match:
            current_section = sec_match.group(1).strip()
        sub_match = re.search(r'#\s*Start\s+of\s+SubSection\s+Title\s+--\s+(.*?)\s*##\s*DO\s+NOT\s+EDIT', line)
        if sub_match and current_section:
            subsection_to_section[sub_match.group(1).strip()] = current_section
    
    # Build complete subsections
    all_subsection_ids = set(subsection_headers.keys()) | set(mantra_sets_map.keys())
    
    # Trackers for Inheritance (Rule 1 & 2)
    last_rik_text = ""
    last_rik_metadata = ""

    # Add subsections to their sections
    global_samam_count = 0
    sorted_sub_ids = sorted(all_subsection_ids, key=lambda x: int(x.replace('subsection_', '')) if x.startswith('subsection_') else 0)
    
    for sub_id in sorted_sub_ids:
        sec_id = subsection_to_section.get(sub_id, 'section_1')
        
        # Find the supersection containing this section
        for ss_id in data["supersection"]:
            if sec_id in data["supersection"][ss_id]["sections"]:
                header_info = subsection_headers.get(sub_id, {"header": "", "saman_metadata": ""})
                
                # Extract rik_id from subsection number (DEFAULT)
                sub_num = int(sub_id.replace('subsection_', '')) if sub_id.startswith('subsection_') else 0
                rik_id_to_use = sub_num
                rik_ids_to_use = None
                
                rik_meta_to_use = rik_metadata_map.get(sub_id, "")
                saman_meta_to_use = saman_metadata_map.get(sub_id) or header_info["saman_metadata"]
                
                # New Metadata Fields
                rik_rishi_val = ""
                rik_devata_val = ""
                rik_chandas_val = ""
                saman_rishi_val = ""
                saman_devata_val = ""
                saman_chandas_val = ""
                
                # Calculate how many samams are in this subsection
                mantra_lines = mantra_sets_map.get(sub_id, [])
                full_mantra_text = "\n".join(mantra_lines)
                # Count Devanagari numeral markers inside double dandas
                mantra_markers = re.findall(r'॥\s*[०-९\d]+\s*॥', full_mantra_text)
                num_mantras = len(mantra_markers) if mantra_markers else 1
                
                # Use current global counter for CSV lookup
                current_lookup_index = global_samam_count + 1
                
                # Update Global Counter for next iteration (add actual number of mantras)
                global_samam_count += num_mantras
                
                if metadata_data and current_lookup_index in metadata_data:
                    meta_row = metadata_data[current_lookup_index]
                    
                    if meta_row.get('Rik_ID'):
                         try:
                             rik_id_to_use = int(meta_row['Rik_ID'])
                         except ValueError:
                             pass
                             
                    if meta_row.get('Rik_Metadata'):
                        rik_meta_to_use = meta_row['Rik_Metadata']
                        
                    if meta_row.get('Saman_Metadata'):
                        saman_meta_to_use = meta_row['Saman_Metadata']
                    
                    # Map new specific fields
                    rik_rishi_val = meta_row.get('Rik_Rishi', '')
                    rik_devata_val = meta_row.get('Rik_Devata', '')
                    rik_chandas_val = meta_row.get('Rik_Chandas', '')
                    saman_rishi_val = meta_row.get('Samam_Rishi', '')
                    saman_devata_val = meta_row.get('Samam_Devata', '')
                    saman_chandas_val = meta_row.get('Samam_Chandas', '')
                    

                
                # Build subsection entry
                subsection_entry = {
                    "header": {"header": header_info["header"], "header_number": sub_num},
                    "rik_id": rik_id_to_use, 
                    "saman_metadata": saman_meta_to_use,
                    "mantra_sets": [],
                    "corrected-mantra_sets": [{"corrected-mantra": '\n'.join(mantra_sets_map.get(sub_id, []))}],
                    "footnotes": footnotes_map.get(sub_id, {}),
                    
                    # New Fields
                    "rik_rishi": rik_rishi_val,
                    "rik_devata": rik_devata_val,
                    "rik_chandas": rik_chandas_val,
                    "saman_rishi": saman_rishi_val,
                    "saman_devata": saman_devata_val,
                    "saman_chandas": saman_chandas_val,
                    "procedure_ref": resolve_procedure(proc_index, ss_id, sec_id, sub_id),
                }

                # --- Rik Inheritance Logic (Rule 1, 2 & 3) ---
                has_new_metadata = sub_id in rik_metadata_map
                has_new_text = sub_id in rik_text_map
                
                # Handle Rik Metadata
                if has_new_metadata:
                    # Tag present: update tracker (could be new content or explicit null)
                    last_rik_metadata = rik_metadata_map[sub_id]
                    if last_rik_metadata.strip() == "":
                         last_rik_metadata = "" # Explicit Reset
                elif has_new_text:
                    # New text appears but NO metadata tag -> Break inheritance (Rule 3)
                    last_rik_metadata = ""

                # Handle Rik Text
                if has_new_text:
                    # Tag present: update tracker (could be new content or explicit null)
                    last_rik_text = rik_text_map[sub_id]
                # else: Tag missing -> inherit from last_rik_text

                # Populate the entry from the trackers
                subsection_entry["rik_metadata"] = last_rik_metadata
                subsection_entry["rik_text"] = last_rik_text
                
                data["supersection"][ss_id]["sections"][sec_id]["subsections"][sub_id] = subsection_entry
                break
    
    # Calculate Samam counts per section
    def int_to_devanagari_local(n):
        mapping = {'0':'०', '1':'१', '2':'२', '3':'३', '4':'४', '5':'५', '6':'६', '7':'७', '8':'८', '9':'९'}
        return "".join(mapping[c] for c in str(n))

    for ss_id, ss_data in data["supersection"].items():
        for sec_id, sec_data in ss_data["sections"].items():
            mantra_count = 0
            for sub_id, sub_data in sec_data["subsections"].items():
                for mantra_set in sub_data.get("corrected-mantra_sets", []):
                    text = mantra_set.get("corrected-mantra", "")
                    m_markers = re.findall(r'॥\s*[०-९\d]+\s*॥', text)
                    mantra_count += len(m_markers) if m_markers else 1
            sec_data["Count"] = int_to_devanagari_local(mantra_count) if sec_data.get("section_title") else ""
    
    # --- Extract Closing Mantras ---
    data["closing_mantras"] = extract_closing_mantras(content)
    if data["closing_mantras"]:
        print(f"[INFO] Extracted {len(data['closing_mantras'])} closing mantra lines.")

    return data


if __name__ == "__main__":
    import argparse
    import sys
    from pathlib import Path
    
    # 0. Load Configuration
    pipeline_cfg = load_pipeline_config()
    config = pipeline_cfg.get('generate_json', {})
    sources_cfg = config.get('sources', {})

    parser = argparse.ArgumentParser(
        description='Generate JSON for Samhita rendering',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Input Modes:
  initial     - Reads raw text files and combines with external metadata files
                (rishi_devata_chandas_for_rik.txt, sama_rishi_chandas_out.txt, vedic_text.txt)
  correction  - Reads processed Unicode text file with embedded metadata

Examples:
  python generate_json.py --type samhita --input-mode initial
  python generate_json.py input.txt --input-mode correction
        """
    )
    parser.add_argument('input_file', type=str, nargs='?', default=None,
                        help='Input text file to process')
    parser.add_argument('--input-mode', choices=['initial', 'correction'], default=None,
                        help='Input mode: initial or correction (priority: CLI > Config > default: correction)')
    parser.add_argument('--output', type=str, default=None,
                        help='Output JSON file path')
    parser.add_argument('--metadata-file', type=str, default=None,
                        help='Optional .xlsx, .txt, or .csv file to enrich metadata (correction mode only)')
    parser.add_argument('--initial-json', type=str, default=None,
                        help='Trusted Initial JSON output to map Rik IDs correctly (correction mode only)')
    
    parser.add_argument('--type', choices=['samhita', 'aaranam'], default='samhita',
                        help='Type of Samaveda text: samhita or aaranam')
    parser.add_argument('--procedures', type=str, default=None,
                        help='Path to procedure index YAML file (e.g., data/input/prayoga/prayoga_index.yaml). If not specified, no procedures will be linked.')
    
    args = parser.parse_args()
    
    mode_type = args.type
    type_cfg = config.get(mode_type, {})

    # Priority: CLI > Config > Default
    input_file = args.input_file or type_cfg.get('input')
    if not input_file:
        print(f"Error: No input file provided for type '{mode_type}'. Please specify via CLI or config.")
        parser.print_help()
        sys.exit(1)

    input_mode = args.input_mode or type_cfg.get('mode') or 'correction'
    
    if mode_type == 'aaranam':
        title = "Jaimineeya Samam Aaranam"
    else:
        title = "Jaimineeya Sama Samhita Patha"

    if input_mode == 'initial':
        # Initial mode: use multiple source files
        rik_meta = sources_cfg.get('rik_meta', "data/input/rishi_devata_chandas_for_rik.txt")
        saman_meta = sources_cfg.get('saman_meta', "data/input/sama_rishi_chandas_out.txt")
        rik_text = sources_cfg.get('rik_text', "data/input/vedic_text.txt")
        
        output_file_path = args.output or type_cfg.get('output')
        if not output_file_path:
             output_dir = "data/output"
             Path(output_dir).mkdir(parents=True, exist_ok=True)
             output_file_path = str(Path(output_dir) / (Path(input_file).stem + "_out.json"))
             
        print(f"Processing {input_file} in INITIAL mode ({mode_type})...")
        output_data = convert_corrections_to_json(input_file, rik_meta, saman_meta, rik_text, title=title)
        
    else:
        # Correction mode: parse Unicode text file
        output_file_path = args.output or type_cfg.get('output')
        if not output_file_path:
             output_dir = "data/output"
             Path(output_dir).mkdir(parents=True, exist_ok=True)
             output_file_path = str(Path(output_dir) / (Path(input_file).stem + "_out.json"))
             
        print(f"Processing {input_file} in CORRECTION mode ({mode_type})...")
        if args.metadata_file:
            print(f"Enriching with metadata from: {args.metadata_file}")
        output_data = parse_unicode_text_file(input_file, metadata_file_path=args.metadata_file, title=title)
    
    if output_data:
        try:
            with open(output_file_path, 'w', encoding='utf-8') as outfile:
                json.dump(output_data, outfile, indent=4, ensure_ascii=False)
            print(f"Success! Saved to '{output_file_path}'")
        except IOError as e:
            print(f"Error writing to file: {e}")