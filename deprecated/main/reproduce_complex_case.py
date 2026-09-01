
import re

class MockParser:
    def __init__(self):
        pass

    def parse_range_string(self, range_str):
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

    def _split_ignoring_parens(self, text, pattern):
        # (Same as implemented)
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
        
        matches = list(pattern.finditer(text))
        valid_matches = []
        for m in matches:
            m_start, m_end = m.span()
            is_forbidden = False
            for f_start, f_end in forbidden_ranges:
                if f_start < m_start < f_end:
                    is_forbidden = True
                    break
            if not is_forbidden:
                valid_matches.append(m)
        
        tokens = []
        last_end = 0
        for m in valid_matches:
            tokens.append(text[last_end:m.start()])
            val = m.group(1) if m.re.groups > 0 else m.group(0)
            tokens.append(val)
            last_end = m.end()
        tokens.append(text[last_end:])
        return tokens

    def process_text_for_rik(self, text, rik_id):
        """
        Resolves conditional content inside parentheses for a specific Rik ID.
        Example: "Name (Default, 5 Override)"
        For Rik 4 -> "Name (Default)"
        For Rik 5 -> "Name (Default Override)" (or whatever logic applies)
        """
        if '(' not in text:
            return text
            
        def replace_parens(match):
            content = match.group(1)
            # Check if content has numbers
            if not any(char.isdigit() for char in content):
                return f"({content})" # No numbers, keep as is
            
            # Parse content: separation by comma or just spaces?
            # User example: "ऋषिः सुकक्षो वा, 5 सुकक्षः" (Comma separated)
            # Devata example: "ऋषिः 3 अग्निहवषि वा " (Space separated)
            
            # Strategy: Split by comma first if present? 
            # Or use a general "Tokenize by number" approach similar to parse_devata_section
            
            # Simple approach: Split by commas, then check start of each segment
            parts = [p.strip() for p in content.split(',')]
            resolved_parts = []
            
            for part in parts:
                # Check for "Number Text" pattern
                # Or "Text Number Text" (mixed)? Assumed "Number Text" for overrides
                
                # Regex to find leading number range
                m_num = re.match(r'^([\d\s–-]+)\s+(.*)', part)
                if m_num:
                    range_str = m_num.group(1)
                    val_str = m_num.group(2)
                    
                    # Check if rik_id is in range
                    ids = self.parse_range_string(range_str)
                    if rik_id in ids:
                        resolved_parts.append(val_str)
                else:
                    # No leading number -> Default text for this bracket
                    # Check if embedded number exists like "Text 5 Text"? 
                    # For now assume text part is applicable to all unless it's an override block
                    # But wait, "ऋषिः 3 अग्नि..." - "ऋषिः" is text, "3 ..." is override
                    
                    # Should we use the logic of "parse_devata_chandas_section" here?
                    # That logic extracts (Default, OverridesMap).
                    # Yes!
                    pass 
            
            # IF split by comma fails to handle "Text Number Val", we need the smarter parser
            # Let's try reusing the logic of `parse_devata_chandas_section` conceptually
            
            p_default, p_map = self.parse_inner_content(content)
            
            final_subparts = []
            if p_default: final_subparts.append(p_default)
            if rik_id in p_map:
                final_subparts.append(p_map[rik_id])
                
            if not final_subparts:
                return "" # Parenthesis becomes empty? e.g. (5 OnlyFor5) -> empty for 4
            
            return f"({' '.join(final_subparts)})"

        return re.sub(r'\(([^)]+)\)', replace_parens, text)

    def parse_inner_content(self, text):
        # Similar to parse_devata_chandas_section but returns map
        rik_specific_map = {}
        default_value = ""
        
        # 1. Check for leading text (Default)
        leading_match = re.match(r'^([^\d]+?)(?=\d|$)', text)
        if leading_match:
            default_value = leading_match.group(1).strip().rstrip(',').strip()
        
        # 2. Find overrides: "N Value"
        pattern = re.compile(
            r'(\d+(?:\s*[,–-]\s*\d+)*)\s+([^\d,]+?)(?=\s*\d+(?:\s*[,–-]\s*\d+)*\s+[^\d]|$)'
        )
        for match in pattern.finditer(text):
            num_str = match.group(1).strip()
            value = match.group(2).strip().rstrip(',').strip()
            if value:
                for rid in self.parse_range_string(num_str):
                    rik_specific_map[rid] = value
                    
        return default_value, rik_specific_map

parser = MockParser()


# Test Case 1: Rishi
# "4, 5 श्रुतकक्षः (ऋषिः सुकक्षो वा, 5 सुकक्षः) आंगिरसः"
base_text = "श्रुतकक्षः (ऋषिः सुकक्षो वा, 5 सुकक्षः) आंगिरसः"
print("-" * 20)
print(f"INPUT: {base_text}")
print(f"Rik 4 (Expected: (Default)): {parser.process_text_for_rik(base_text, 4)}")
print(f"Rik 5 (Expected: (Default Specific)): {parser.process_text_for_rik(base_text, 5)}")

# Test Case 2: Devata
# "इन्द्रः (ऋषिः 3 अग्निहवषि वा )"
devata_text = "इन्द्रः (ऋषिः 3 अग्निहवषि वा )"
print("-" * 20)
print(f"INPUT: {devata_text}")
print(f"Rik 3 (Expected: (Specific)): {parser.process_text_for_rik(devata_text, 3)}")
print(f"Rik 4 (Expected: (Empty?)): {parser.process_text_for_rik(devata_text, 4)}")
