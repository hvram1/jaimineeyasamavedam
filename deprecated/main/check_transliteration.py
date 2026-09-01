import re
from collections import defaultdict
from aksharamukha import transliterate

def read_transliteration_file():
    """Read the transliteration-differences.txt file and extract g, t, c lines."""
    
    with open('transliteration-differences.txt', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    sections = defaultdict(list)
    current_section = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check if it's a section header
        if line.startswith('subsection_'):
            current_section = line
            continue
            
        # Check if it's a g, t, or c line
        if line.startswith('g') or line.startswith('t') or line.startswith('c'):
            if current_section:
                sections[current_section].append(line)
    
    return sections

def extract_words_from_line(line):
    """Extract words from a line, removing the prefix and parenthetical content."""
    # Remove the prefix (e.g., "g1-14", "t2-14", "c3-14")
    content = re.sub(r'^[gtc]\d+-\d+\s+', '', line)
    
    # Remove parenthetical content like (त), (श) etc.
    content = re.sub(r'\([^)]*\)', '', content)
    
    # Split by spaces and filter out empty strings and punctuation-only words
    words = [word.strip() for word in content.split() if word.strip() and not all(c in '।॥।।' for c in word.strip())]
    
    return words

def check_word_counts():
    """Check if g, t, c lines have the same number of words in each section."""
    sections = read_transliteration_file()
    
    issues = []
    
    for section_name, lines in sections.items():
        if len(lines) < 3:
            continue
            
        g_line = None
        t_line = None  
        c_line = None
        
        for line in lines:
            if line.startswith('g'):
                g_line = line
            elif line.startswith('t'):
                t_line = line
            elif line.startswith('c'):
                c_line = line
        
        if not all([g_line, t_line, c_line]):
            continue
            
        g_words = extract_words_from_line(g_line)
        t_words = extract_words_from_line(t_line)
        c_words = extract_words_from_line(c_line)
        
        print(f"\n{section_name}:")
        print(f"G words ({len(g_words)}): {g_words}")
        print(f"T words ({len(t_words)}): {t_words}")
        print(f"C words ({len(c_words)}): {c_words}")
        
        if not (len(g_words) == len(t_words) == len(c_words)):
            issues.append({
                'section': section_name,
                'g_count': len(g_words),
                't_count': len(t_words),
                'c_count': len(c_words),
                'g_words': g_words,
                't_words': t_words,
                'c_words': c_words
            })
    
    return issues

def check_transliteration():
    """Check transliteration of G words against T and C words for sections with matching word counts."""
    sections = read_transliteration_file()
    
    matching_sections = []
    transliteration_results = []
    
    for section_name, lines in sections.items():
        if len(lines) < 3:
            continue
            
        g_line = None
        t_line = None  
        c_line = None
        
        for line in lines:
            if line.startswith('g'):
                g_line = line
            elif line.startswith('t'):
                t_line = line
            elif line.startswith('c'):
                c_line = line
        
        if not all([g_line, t_line, c_line]):
            continue
            
        g_words = extract_words_from_line(g_line)
        t_words = extract_words_from_line(t_line)
        c_words = extract_words_from_line(c_line)
        
        # Only process sections where G and T have the same number of words
        if len(g_words) == len(t_words):
            matching_sections.append(section_name)
            
            print(f"\n{section_name}:")
            print(f"G words: {g_words}")
            print(f"T words: {t_words}")
            print(f"C words: {c_words}")
            
            # Perform transliteration comparison for each word pair
            mismatches = []
            for i, (g_word, t_word) in enumerate(zip(g_words, t_words)):
                try:
                    # Transliterate from Grantha to Devanagari
                    transliterated = transliterate.process('Grantha', 'Devanagari', g_word)
                    
                    if transliterated != t_word:
                        mismatches.append({
                            'position': i,
                            'grantha': g_word,
                            'transliterated': transliterated,
                            'expected_t': t_word
                        })
                        print(f"  Word {i+1}: G='{g_word}' -> '{transliterated}' != T='{t_word}' ❌")
                    else:
                        print(f"  Word {i+1}: G='{g_word}' -> '{transliterated}' == T='{t_word}' ✓")
                        
                except Exception as e:
                    print(f"  Word {i+1}: Error transliterating '{g_word}': {e}")
                    mismatches.append({
                        'position': i,
                        'grantha': g_word,
                        'transliterated': 'ERROR',
                        'expected_t': t_word,
                        'error': str(e)
                    })
            
            if mismatches:
                transliteration_results.append({
                    'section': section_name,
                    'mismatches': mismatches
                })
    
    return matching_sections, transliteration_results

def main():
    print("Checking word counts in transliteration-differences.txt...")
    issues = check_word_counts()
    
    if issues:
        print(f"\n\nFound {len(issues)} sections with mismatched word counts:")
        for issue in issues[:10]:  # Show only first 10 to avoid too much output
            print(f"\n{issue['section']}:")
            print(f"  G: {issue['g_count']} words")
            print(f"  T: {issue['t_count']} words") 
            print(f"  C: {issue['c_count']} words")
        
        if len(issues) > 10:
            print(f"\n... and {len(issues) - 10} more sections with mismatched counts.")
    else:
        print("\nAll sections have matching word counts!")
    
    print("\n" + "="*80)
    print("TRANSLITERATION CHECK FOR MATCHING SECTIONS")
    print("="*80)
    
    matching_sections, transliteration_results = check_transliteration()
    
    print(f"\n\nSUMMARY:")
    print(f"Total sections with matching G-T word counts: {len(matching_sections)}")
    print(f"Sections with transliteration mismatches: {len(transliteration_results)}")
    
    if transliteration_results:
        print(f"\nSections with mismatches:")
        for result in transliteration_results[:5]:  # Show first 5 mismatch sections
            print(f"  {result['section']}: {len(result['mismatches'])} mismatches")
        
        if len(transliteration_results) > 5:
            print(f"  ... and {len(transliteration_results) - 5} more sections with mismatches.")

if __name__ == "__main__":
    main()
