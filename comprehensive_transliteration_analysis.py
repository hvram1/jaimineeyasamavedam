import re
from collections import defaultdict
from aksharamukha import transliterate
import regex  # added to handle grapheme clusters
import grapheme





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
    #content = re.sub(r'\([^)]*\)', '', content)
    
    # Split by spaces and filter out empty strings and punctuation-only words
    words = [word.strip() for word in content.split() if word.strip() and not all(c in '।॥।।' for c in word.strip())]
    
    return words

def analyze_all_sections():
    """Analyze all sections for word count matching and transliteration accuracy."""
    sections = read_transliteration_file()
    
    total_sections = 0
    sections_with_all_lines = 0
    matching_word_count_sections = 0
    perfect_transliteration_sections = 0
    total_words_checked = 0
    total_correct_transliterations = 0
    
    word_count_issues = []
    transliteration_issues = []
    
    for section_name, lines in sections.items():
        total_sections += 1
        
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
            
        sections_with_all_lines += 1
            
        g_words = extract_words_from_line(g_line)
        t_words = extract_words_from_line(t_line)
        c_words = extract_words_from_line(c_line)
        
        
            
        # Combine words into single strings without spaces
        g_combined = ''.join(g_words)
        t_combined = ''.join(t_words)
        c_combined = ''.join(c_words)
        
        # Get grapheme clusters for t_combined and c_combined
        t_graphemes = parse_grapheme_units(t_combined)
        c_graphemes = parse_grapheme_units(c_combined)
        g_graphemes = parse_grapheme_units(g_combined)

        if len(c_graphemes) != len(g_graphemes):
            word_count_issues.append({
                'section': section_name,
                'g_count': len(g_graphemes),
                't_count': len(t_graphemes),
                'c_count': len(c_graphemes)
            })
            continue
        
        matching_word_count_sections += 1
        
        # Check transliteration for sections with matching word counts and grapheme lengths
        section_mismatches = []
        section_matches = 0

        for i, (g_word, t_word, c_word) in enumerate(zip(g_graphemes, t_graphemes, c_graphemes)):
            total_words_checked += 1
            try:
                # Transliterate from Grantha to Devanagari
                transliterated = transliterate.process('Grantha', 'Devanagari', g_word)
                
                if transliterated == t_word and transliterated == c_word:
                    section_matches += 1
                    total_correct_transliterations += 1
                else:
                    section_mismatches.append({
                        'position': i,
                        'grantha': g_word,
                        'transliterated': transliterated,
                        'expected_t': t_word,
                        'expected_c': c_word
                    })
                    
            except Exception as e:
                section_mismatches.append({
                    'position': i,
                    'grantha': g_word,
                    'transliterated': 'ERROR',
                    'expected_t': t_word,
                    'expected_c': c_word,
                    'error': str(e)
                })
        
        if len(section_mismatches) == 0:
            perfect_transliteration_sections += 1
        else:
            transliteration_issues.append({
                'section': section_name,
                'total_words': len(c_graphemes),
                'matches': section_matches,
                'mismatches': section_mismatches
            })
    
    return {
        'total_sections': total_sections,
        'sections_with_all_lines': sections_with_all_lines,
        'matching_word_count_sections': matching_word_count_sections,
        'perfect_transliteration_sections': perfect_transliteration_sections,
        'total_words_checked': total_words_checked,
        'total_correct_transliterations': total_correct_transliterations,
        'word_count_issues': word_count_issues,
        'transliteration_issues': transliteration_issues
    }

def parse_grapheme_units(text):
    """
    Parse the string and return a list of grapheme units.
    If a substring is enclosed in parentheses, treat it as a single unit.
    Otherwise, split into grapheme clusters.
    """
    units = []
    i = 0
    while i < len(text):
        if text[i] == '(':  # Start of parenthetical
            end = text.find(')', i)
            if end != -1:
                units.append(text[i:end+1])
                i = end + 1
            else:
                # Unmatched '(', treat as normal grapheme
                units.append(text[i])
                i += 1
        else:
            # Use grapheme library to get the next grapheme cluster
            cluster = next(grapheme.graphemes(text[i:]), None)
            if cluster:
                units.append(cluster)
                i += len(cluster)
            else:
                units.append(text[i])
                i += 1
    return units

def main():
    print("COMPREHENSIVE TRANSLITERATION ANALYSIS")
    print("="*60)
    
    results = analyze_all_sections()
    
    print(f"\nOVERALL STATISTICS:")
    print(f"Total sections found: {results['total_sections']}")
    print(f"Sections with G, T, C lines: {results['sections_with_all_lines']}")
    print(f"Sections with matching G-T-C word counts: {results['matching_word_count_sections']}")
    print(f"Sections with perfect transliteration: {results['perfect_transliteration_sections']}")
    
    if results['matching_word_count_sections'] > 0:
        perfect_rate = (results['perfect_transliteration_sections'] / results['matching_word_count_sections']) * 100
        print(f"Perfect transliteration rate: {perfect_rate:.1f}%")
    
    if results['total_words_checked'] > 0:
        word_accuracy = (results['total_correct_transliterations'] / results['total_words_checked']) * 100
        print(f"\nWORD-LEVEL ACCURACY:")
        print(f"Total words checked: {results['total_words_checked']}")
        print(f"Correct transliterations: {results['total_correct_transliterations']}")
        print(f"Word-level accuracy: {word_accuracy:.1f}%")
    
    print(f"\nWORD COUNT ISSUES:")
    print(f"Sections with mismatched word counts: {len(results['word_count_issues'])}")
    
    print(f"\nTRANSLITERATION ISSUES:")
    print(f"Sections with transliteration mismatches: {len(results['transliteration_issues'])}")
    
    # Show first few examples of each type of issue
    if results['transliteration_issues']:
        print(f"\nSample transliteration issues (first 3):")
        for issue in results['transliteration_issues']:
            accuracy = (issue['matches'] / issue['total_words']) * 100
            print(f"  {issue['section']}: {issue['matches']}/{issue['total_words']} correct ({accuracy:.1f}%)")
            for mismatch in issue['mismatches']:  # Show first 2 mismatches per section
                if 'error' in mismatch:
                    print(f"    Error: {mismatch['grantha']} -> {mismatch['error']}")
                else:
                    print(f"    {mismatch['grantha']} -> {mismatch['transliterated']} (expected: {mismatch['expected_c']})")

    for result in results['word_count_issues']:
        print(result)
if __name__ == "__main__":
    main()
