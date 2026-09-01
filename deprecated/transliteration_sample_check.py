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

def check_transliteration_sample():
    """Check transliteration of G words against T words for first 10 sections with matching word counts."""
    sections = read_transliteration_file()
    
    matching_sections = []
    transliteration_results = []
    processed_count = 0
    
    for section_name, lines in sections.items():
        if processed_count >= 10:  # Only process first 10 matching sections
            break
            
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
            processed_count += 1
            
            print(f"\n{section_name}:")
            print(f"G words ({len(g_words)}): {g_words}")
            print(f"T words ({len(t_words)}): {t_words}")
            print(f"C words ({len(c_words)}): {c_words}")
            
            # Perform transliteration comparison for each word pair
            mismatches = []
            matches = 0
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
                        matches += 1
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
            
            print(f"  Summary: {matches} matches, {len(mismatches)} mismatches")
            
            if mismatches:
                transliteration_results.append({
                    'section': section_name,
                    'mismatches': mismatches,
                    'total_words': len(g_words),
                    'matches': matches
                })
    
    return matching_sections, transliteration_results

def main():
    print("TRANSLITERATION CHECK FOR SAMPLE SECTIONS")
    print("="*60)
    
    matching_sections, transliteration_results = check_transliteration_sample()
    
    print(f"\n\nSUMMARY:")
    print(f"Total sections processed: {len(matching_sections)}")
    print(f"Sections with transliteration mismatches: {len(transliteration_results)}")
    
    if transliteration_results:
        print(f"\nDetailed mismatch summary:")
        for result in transliteration_results:
            accuracy = (result['matches'] / result['total_words']) * 100
            print(f"  {result['section']}: {result['matches']}/{result['total_words']} correct ({accuracy:.1f}%)")

if __name__ == "__main__":
    main()
