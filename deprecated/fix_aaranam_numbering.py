
import re

def renumber_subsections(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # The point where confusion starts is the duplicate subsection_85.
    # We should have converted the second one to 85_1 in the previous step,
    # but looking at the file view, it seems I might have only done it partially or my regex was slightly off in previous turns?
    # No, wait, in Step 1231 view:
    # Line 660: # Start of SubSection Title -- subsection_85
    # ...
    # Line 679: #End of Mantra Sets -- subsection_85
    #
    # Line 680 starts subsection_86
    # But wait, where is the duplicate?
    # Ah, in step 1191 view, there was a duplicate.
    # In step 1198 (multi_replace), I renamed the second one to 85_1.
    # In step 1204 (replace), I inserted a title for 85_1.
    # Let's check step 1231 again carefully.
    
    # Line 660: subsection_85 (Agastya's Arka)
    # Line 665: End of Mantra Sets -- subsection_85
    # Line 666: Section 14
    # Line 670: Start os Mantra Sets -- subsection_85 (THIS IS THE DUPLICATE, but wait...)
    # In Step 1231 output, line 670 shows: "#Start of Mantra Sets -- subsection_85 ## DO NOT EDIT"
    # Wait, did my previous edits fail or get reverted?
    # Step 1198 said "The following changes were made...".
    # Step 1204 said "The following changes were made...".
    # But looking at Step 1231 view, line 670 says "subsection_85".
    # Wait, Step 1198 had regex mismatch for chunks?
    # "chunk 2: target content not found...".
    # "chunk 1" was the Start of Mantra Sets change. It says [diff_block_start] ... -#Start of Mantra Sets -- subsection_85 ... +#Start of Mantra Sets -- subsection_85_1
    # So line 670 SHOULD start with 85_1 if it worked.
    # However, Step 1231 shows line 670 as "#Start of Mantra Sets -- subsection_85".
    # This implies the edit MIGHT NOT have persisted or I am misreading the file content.
    # Ah, I see line 670 in Step 1231 view is: "#Start of Mantra Sets -- subsection_85 ## DO NOT EDIT".
    # This is weird. Let me check if I am looking at the same file.
    # Yes, Aaranam_latest.txt.
    
    # Let's assume the state is problematic and re-do the fix properly with a script.
    # We want to find the SECOND occurrence of subsection_85 and rename it to 86, and then increment everything else.
    # BUT, we also have to be careful about what "everything else" means.
    # Currently, do we have 86, 87, 88...?
    # Yes, line 680 is subsection_86.
    
    # Algorithm:
    # 1. Regex find all "subsection_(\d+)" occurrences.
    # 2. Iterate through them.
    # 3. If we see 85, then another 85, we trigger the shift.
    # 4. The first 85 stays 85.
    # 5. The second 85 becomes 86.
    # 6. The original 86 becomes 87, etc.
    
    # We need to replace strings like:
    # "subsection_85" -> "subsection_85" (first time)
    # "subsection_85" -> "subsection_86" (second time)
    # "subsection_86" -> "subsection_87"
    # ...
    
    # Since we are shifting up, we should probably do this carefully to avoid replacing 86 match with 87 and then finding 87 and replacing it with 88 in the same pass if we are not careful.
    # The safest way is to tokenize or build a list of replacements and apply them map-style or rebuild the string.
    
    parts = re.split(r'(subsection_\d+)', content)
    new_content = []
    
    seen_85_count = 0
    mapping_offset = 0
    
    # To keep track of what numbers we have seen to know when to start shifting.
    # The duplicate 85 is the trigger.
    
    for part in parts:
        if part.startswith('subsection_'):
            num_str = part.split('_')[1]
            if num_str.isdigit():
                num = int(num_str)
                
                if num == 85:
                    seen_85_count += 1
                    if seen_85_count == 1:
                        # First 85, keep as is
                        new_num = 85
                    else:
                        # Second 85 (or more), this is the duplicate!
                        # This becomes 86.
                        new_num = 86
                        # And subsequent numbers need to be shifted by +1 compared to what they were.
                        # Wait, original 86 should become 87.
                        # So if we are in "shift mode", we add 1 to the number?
                        # No, if we have [..., 85, 85, 86, 87, ...]
                        # We want [..., 85, 86, 87, 88, ...]
                        # So for the second 85, we want 86. (85+1)
                        # For the existing 86, we want 87. (86+1)
                        # So yes, logic is: if we have passed the specific point (start of second 85), we increment the number.
                        pass
                
                # Check global state
                if seen_85_count >= 2:
                    # We are at or past the second 85.
                    if num == 85 and seen_85_count > 1:
                         # This is one of the duplicate 85 tokens.
                         # Note: A single "subsection_85" block has multiple mentions of "subsection_85" (start title, end title, start mantra, end mantra).
                         # We need to treat the whole BLOCK as the one to renumber.
                         # But simplistic token replacement is risky if we increment "subsection_85" to 86 multiple times for the same block.
                         # Actually, the file structure uses subsection_X markers consistently within a block.
                         # So if we are in the "second 85 block", all text markers "subsection_85" should be "subsection_86".
                         # If we are in "subsection_86 block", markers should be "subsection_87".
                         
                         # The issue is "seen_85_count" increments for each token.
                         # We have Start Title, End Title, Start Mantra, End Mantra. That's 4 tokens per subsection usually.
                         # Original 85 has 4 tokens.
                         # Duplicate 85 has 4 tokens.
                         # We want tokens 1-4 to be 85.
                         # Tokens 5-8 (duplicate 85) to be 86.
                         # Tokens 9... (original 86) to be 87.
                         
                         # Let's count how many times 85 appears.
                         # Ideally, we should track "current subsection ID context".
                         pass

    # New approach:
    # Identfy the byte offset of the boundaries.
    # The problem is that the "Start of Section 14" is between the two 85s.
    # First 85 is Agastya. Second 85 is Raudrani.
    # Section 14 starts before the second 85.
    
    # Let's rebuild the content by iterating matches and replacing strictly based on count.
    
    replacements = []
    
    # Find all iterators
    matches = list(re.finditer(r'subsection_(\d+)', content))
    
    # Filter for interest
    # We assume the file is sorted mostly.
    
    # We need to identify which matches correspond to the *second* block of 85.
    # The first block of 85 ends around line 665.
    # The second block starts around line 670.
    # We can use the fact that Section 14 is the divider.
    
    section_14_idx = content.find('section_14')
    if section_14_idx == -1:
        print("Could not find section_14 marker, aborting safestrategy.")
        return

    offset = 0
    result = ""
    
    last_pos = 0
    
    for m in matches:
        start, end = m.span()
        num = int(m.group(1))
        
        # Append text before this match
        result += content[last_pos:start]
        
        if start > section_14_idx:
            # We are after Section 14 start.
            # This covers the duplicate 85 (which is inside section 14 or right after start of section 14 header)
            # and all subsequent sections (86, 87...)
            
            # If it is 85, it becomes 86.
            # If it is >= 86, it becomes N+1.
            # If it is < 85 (unlikely here but possible if out of order), leave it? No, assume order.
            
            if num == 85:
                # This is the duplicate!
                new_num = 86
            elif num >= 86:
                new_num = num + 1
            else:
                new_num = num # Should not happen based on file flow
                
            result += f"subsection_{new_num}"
        else:
            # Before Section 14. Keep as is.
            # This includes original 85.
            result += f"subsection_{num}"
            
        last_pos = end
        
    result += content[last_pos:]
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(result)
    print("Renumbering complete.")

if __name__ == "__main__":
    renumber_subsections("data/input/Aaranam_latest.txt")
