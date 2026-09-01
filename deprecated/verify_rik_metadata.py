import re
import os
import sys

# --- Copied RikMetadataParser Class ---
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
            # checking patterns used: r'((?:\d+...)+)' -> group 1 is the whole match
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
                r'((?:\d+(?:\s*[,–-]\s*\d+)*(?:,\s*)?)+)\s+([^\d,]+?)(?=\s*\d+(?:\s*[,–-]\s*\d+)*\s+[^\d]|$)'
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
            self.section_lines = [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]

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
        
        section_text = section_text.strip().strip('।|,').strip()
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
        
        # 2. Split by ।। to separate Rishi, Devata, Chandas sections
        parts = line.split('।।')
        
        # First part is Rishi section (before first ।।)
        rishi_section = parts[0] if parts else ""
        
        # Remaining parts are Devata and Chandas (after first ।।)
        suffix_parts = parts[1:] if len(parts) > 1 else []
        
        # 3. Parse Rishi section (numbers before names)
        rishi_map = {}
        # Pattern matching number groups, ensuring they are separated
        num_group_pattern = re.compile(r'((?:\d+(?:\s*[–-]\s*\d+)*(?:,\s*)?)+)')
        
        # Use new split method to avoid splitting numbers inside parens
        tokens = self._split_ignoring_parens(rishi_section, num_group_pattern)
        
        # tokens[0] should be empty if the line starts with numbers (which Rishi section usually does)
        # Structure: [PreText, Num1, Name1, Num2, Name2...]
        
        # Handle implicit first rishi if no number prefix (rare in this format but possible)
        # Actually in the file, Rishi section seems to always start with numbers or implicit default?
        # Based on file 4: "1, 3, 7 Sharyu...". tokens[0] will be empty.
        
        start_idx = 1
        default_rishi = ""
        
        if len(tokens) > 0 and tokens[0].strip():
             # If there's text before first number, it's a default rishi? 
             # Or maybe the first item has no number.
             # In the format provided: "(1-10) 1 Rishi..." -> starts with number.
             # But line 7: "(1-10) Shyavashva..." -> starts with text.
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
        clean_suffix_parts = [p.strip().strip('।|') for p in suffix_parts if p.strip().strip('।|')]
        
        if len(clean_suffix_parts) == 0:
            pass
        elif len(clean_suffix_parts) == 1:
            # Single part - could be Devata only or Chandas only
            # Treat as Chandas (since that's typically the last field)
            chandas_default, chandas_specific = self.parse_devata_chandas_section(clean_suffix_parts[0])
        else:
            # Multiple parts: LAST is Chandas, rest are Devata
            devata_parts = clean_suffix_parts[:-1]
            chandas_part = clean_suffix_parts[-1]
            
            # Parse Chandas (last part)
            chandas_default, chandas_specific = self.parse_devata_chandas_section(chandas_part)
            
            # Parse Devata (all middle parts combined)
            for part in devata_parts:
                part_default, part_specific = self.parse_devata_chandas_section(part)
                
                if part_default and not devata_default:
                    devata_default = part_default
                
                devata_specific.update(part_specific)
        
        # 5. Build combined metadata map for each Rik
        meta_map = {}
        for rik_id in rik_range:
            rishi = self.process_value_for_rik(rishi_map.get(rik_id, ""), rik_id)
            devata = self.process_value_for_rik(devata_specific.get(rik_id, devata_default), rik_id)
            chandas = self.process_value_for_rik(chandas_specific.get(rik_id, chandas_default), rik_id)
            
            parts_list = []
            if rishi: parts_list.append(rishi)
            if devata: parts_list.append(devata)
            if chandas: parts_list.append(chandas)
            
            if parts_list:
                meta_map[rik_id] = "।। " + " ".join(parts_list) + " ।।"
        
        return meta_map

# --- Main Verification Logic ---
def verify_metadata_file(input_file, output_file):
    print(f"Reading from: {input_file}")
    print(f"Writing to:   {output_file}")
    
    parser = RikMetadataParser(input_file)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"{'Section Line':<12} | {'Rik ID':<6} | {'Metadata'}\n")
        f.write("-" * 80 + "\n")
        
        for idx, line in enumerate(parser.section_lines):
            section_idx = idx + 1
            meta_map = parser.parse_section_line(line)
            
            # Sort Rik IDs numerically
            sorted_riks = sorted(meta_map.keys())
            
            for rik_id in sorted_riks:
                metadata = meta_map[rik_id]
                f.write(f"{section_idx:<12} | {rik_id:<6} | {metadata}\n")
    
    print("Verification complete.")

if __name__ == "__main__":
    input_path = "rishi_devata_chandas_for_rik.txt"
    output_path = "rik_metadata_verification.txt"
    verify_metadata_file(input_path, output_path)
