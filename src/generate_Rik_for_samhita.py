import subprocess
import os
import re
# ----------------------------------------------------
# Globals for Configuration
# ----------------------------------------------------
CURRENT_PDF_FONT = "NotoSansDevanagari"
CURRENT_PDF_COLOR_MODE = "color"
CURRENT_PDF_DRAFT_MODE = False

# ----------------------------------------------------
# 0. NEW UTILITY: Local Visarga Accent Ordering
# ----------------------------------------------------
def fix_visarga_accent_order_local(text):
    """
    Always swap so accent appears on character BEFORE visarga.
    Input: Word:(1) -> Word(1):  (accent now on preceding character)
    """
    if not text: return text
    
    # Normalize colons
    text = text.replace(':', 'ः')
    text = re.sub(r'\s+ः', 'ः', text)
    
    # Always swap Visarga + Accent to Accent + Visarga
    pattern = r'([ः])\s*(\([^)]+\))'
    text = re.sub(pattern, r'\2\1', text)
    
    return text

# ----------------------------------------------------
# 1. Utility function: Accent Replacements
# ----------------------------------------------------
def replace_accents(text):
    """
    Replaces ASCII markers (1), (2), etc., with LaTeX commands.
    We do NOT add any extra spacing or breaks here.
    """
    if 'Adishila' in CURRENT_PDF_FONT:
        replacements = [
            ('(1)', r'\makebox[0pt][l]{\raisebox{0.2ex}{\accentmark{22}{\char"0951}}}'),  # Swarita
            ('(2)', r'\makebox[0pt][l]{\raisebox{0.2ex}{\accentmark{27}{\char"1CD2}}}'),  # Anudatta
            ('(3)', r'\makebox[0pt][l]{\raisebox{0.2ex}{\accentmark{20}{\char"1CF8}}}'),  # Kampa
            ('(4)', r'\makebox[0pt][l]{\raisebox{0.2ex}{\accentmark{20}{\char"1CF9}}}'),  # Trikampa
        ]
    else:
        replacements = [
            ('(1)', '\u0951'),  
            ('(2)', '\u1CD2'),  
            ('(3)', '\u1CF8'),  
            ('(4)', '\u1CF9'),  
        ]
  
    for marker, replacement in replacements:
        text = text.replace(marker, replacement)
    
    return text

# ----------------------------------------------------
# 2. NEW: Consecutive Accent Handler (Updated)
# ----------------------------------------------------
def handle_consecutive_accents(text):
    r"""
    Inserts a small \kern to separate specific accent transitions 
    that are prone to visual overlap.
    
    Handled Transitions:
    1. Anudatta (2) -> Anudatta (2)
    2. Swarita (1)  -> Anudatta (2) [NEW]
    """
    
    # CASE A: Anudatta (2) followed by Anudatta (2)
    # ---------------------------------------------
    # Pattern: Match (2) ONLY if followed by 1-5 chars and then another (2)
    pat_2_2 = r'(\(2\))(?=[^()]{1,5}\(2\))'
    text = re.sub(pat_2_2, r'\1\\kern0.15em', text)

    # CASE B: Swarita (1) followed by Anudatta (2)
    # ---------------------------------------------
    # Pattern: Match (1) ONLY if followed by 1-5 chars and then (2)
    # This prevents the vertical line of Swarita from hitting the line of Anudatta
    pat_1_2 = r'(\(1\))(?=[^()]{1,5}\(2\))'
    text = re.sub(pat_1_2, r'\1\\kern0.15em', text)

    # CASE C:  Anudatta (2) followed by Kamba (3) or Trikamba (4)
    # ---------------------------------------------
    # Pattern: Match (1) ONLY if followed by 1-5 chars and then (2)
    # This prevents the vertical line of Swarita from hitting the line of Anudatta
    pat_2_3= r'(\(2\))(?=[^()]{1,5}\(3\))'
    text = re.sub(pat_2_3, r'\1\\kern0.15em', text)

    pat_2_4= r'(\(2\))(?=[^()]{1,5}\(4\))'
    text = re.sub(pat_2_4, r'\1\\kern0.15em', text)
    
    return text

# ----------------------------------------------------
# 3. Utility function: Line Breaks (With Clearpage for Atha)
# ----------------------------------------------------
def add_enhanced_linebreaks(text):
    # --- STEP 0: NORMALIZE ---
    text = text.replace('\ufeff', '') # Remove BOM if present
    text = text.replace('II.', '॥').replace('II', '॥').replace('||', '॥')
    text = text.replace('|', r'।\ ').replace('।', r'।\ ')
    text = text.strip()
    danda = r'॥'

    # --- STEP 1: DE-FRAGMENTATION (Fix Broken Headers) ---
    # Merge "||" + "Atha/Iti" if split across lines
    # FIX: Only merge if "||" is at the start of the line (isolated),
    # to avoid merging the previous line's closing danda with the next line's start.
    text = re.sub(r'(?m)^\s*॥\s+((?:अथ|इति|समाप्तः))', r'॥ \1', text)
    # Merge "Text..." + "||" (Orphan closing danda)
    text = re.sub(r'(समाप्तः|खण्डः|प्रारम्भः)\s*\n\s*॥', r'\1 ॥', text)

    # --- STEP 2: GLUE MANTRA NUMBERS TO PRECEDING TEXT ---
    # Finds: (Any Space/Newline) + (|| Digits ||)
    # Replaces with: (Tilde/NBSP) + (|| Digits ||)
    mantra_block_pattern = r'॥\s*[\d\u0966-\u096F]+\s*॥'
    text = re.sub(r'\s+(' + mantra_block_pattern + ')', r'~\1', text)

    # --- STEP 3: WRAP SPECIAL BLOCKS IN \mbox{} ---
    
    # 3a. HEADERS FIRST: Protect & Add Clearpage for Atha
    # We match headers first to consume any trailing numerals (e.g. अथ ... खण्डः ॥ २ ॥)
    # into the same \mbox so they stay on the same line.
    def mbox_wrapper_headers(match):
        content = match.group(1).strip()
        # Normalize internal spaces to single space
        content = re.sub(r'\s+', ' ', content)
        
        # 1. Main Title: || Atha Uttararchikam ||
        if 'उत्तरार्चिकम्' in content:
             # Main Title Style: Centered, Large, Green, Own Page
             return r'\clearpage\thispagestyle{empty}\vspace*{2in}{\centering\Huge\bfseries\textcolor{AccentGreen}{' + content + r'}\par}\vfill\clearpage'
        
        # 2. Khandah/Kandah (Section): || Atha ... Khandah ||
        if 'खण्डः' in content:
            if 'अथ' in content and not CURRENT_PDF_DRAFT_MODE:
                prefix = r'\clearpage\phantomsection'
            else:
                prefix = r'\vspace*{1em}\phantomsection'
            return prefix + r'\addcontentsline{toc}{section}{' + content + r'}\vspace*{1em}{\centering\Large\bfseries\textcolor{AccentGreen}{' + content + r'}\par}\vspace*{1em}'

        # Create the wrapped block for standard headers
        wrapped_block = r'\mbox{' + content + r'}'
        
        # CHECK: If this block contains "Atha", prepend \clearpage, else just vspace
        if 'अथ' in content:
            if not CURRENT_PDF_DRAFT_MODE:
                return r'\clearpage\vspace*{1em}{\centering\Large\bfseries\textcolor{AccentGreen}{' + content + r'}\par}\vspace*{1em}'
            else:
                return r'\vspace*{2em}{\centering\Large\bfseries\textcolor{AccentGreen}{' + content + r'}\par}\vspace*{1em}'
        elif 'इति' in content or 'समाप्तः' in content:
            if 'संहिता' in content:
                # Make the Samhita title Huge!
                return r'\vspace*{2em}{\centering\Huge\bfseries\textcolor{AccentGreen}{' + content + r'}\par}\vspace*{1em}'
            return r'\vspace*{1em}{\centering\Large\bfseries\textcolor{AccentGreen}{' + content + r'}\par}\vspace*{1em}'
            
        return wrapped_block

    # Regex matches: 
    # 1. Optional leading danda
    # 2. Atha/Iti/Samaptah
    # 3. Content until...
    # 4. Closing danda OR "Khanda" OR "Kandah" OR "Uttararchikam"
    # 5. Optional suffix: EITHER a full numeral block (|| N ||) OR just a closing danda (||)
    # (Removed single danda option to force capture of numbers if present)
    # UPDATED: Accept [~\s]* before suffix to handle the glue tilde added in Step 2.
    # FIX: Added |[~\s]*॥ to capture trailing danda for main titles without numbers.
    pat_headers = r'^\s*((?:॥\s*)?(?:अथ|इति|समाप्तः).*?(?:॥|खण्डः|काण्डः|उत्तरार्चिकम्)(?:[~\s]*॥\s*[\d\u0966-\u096F]+\s*॥|[~\s]*॥)?)'
    text = re.sub(pat_headers, mbox_wrapper_headers, text, flags=re.DOTALL | re.MULTILINE)

    # 3b. MANTRA NUMBERS: Force Spaces & Protect (standalone)
    # || 10 ||  ->  \mbox{॥ 10 ॥}
    text = re.sub(r'॥\s*([\d\u0966-\u096F]+)\s*॥', r'\\mbox{॥ \1 ॥}', text)

    # --- STEP 4: ADD LINE BREAKS (\\) ---
    # Add a LaTeX break ` \\` after every protected block (\mbox)
    # This ensures headers and mantra numbers end their lines immediately.
    text = re.sub(r'(\\mbox\{.*?\})', r'\1 \\\\', text)

    # --- STEP 5: CLEANUP ---
    # Fix double breaks
    text = re.sub(r'\\\\\s*\\\\', r'\\\\', text)
    # Remove orphan dandas on empty lines
    text = re.sub(r'(?m)^\s*॥\s*$', '', text)
    # Clean paragraph spacing
    text = re.sub(r'\n\s*\n\s*\n', r'\n\n', text)
    
    return text.lstrip()

# ----------------------------------------------------
# 4. Utility function: Reduce Trailing Whitespace (UPDATED)
# ----------------------------------------------------
def eliminate_trailing_whitespace(text):
    zero_space = r'\\hspace{0pt}' 
    
    # 1. Handle standalone Dandas
    text = re.sub(r'\s(॥)', zero_space + r'\1', text)
    
    # 2. Handle Mantra Numbers (Adjusted for the new spacing)
    # Matches: (Space) (|| Space Digits Space ||)
    # We apply the zero_space buffer before the leading Danda
    mantra_number_pattern = r'(\s)(॥\s*[\u0966-\u096F]+\s*॥)'
    text = re.sub(mantra_number_pattern, zero_space + r'\2', text)
    
    return text
  
# ----------------------------------------------------
# 4. Utility function: Reduce Trailing Whitespace
# ----------------------------------------------------

def reduce_trailing_whitespace(text):
    #"""
    #Inserts LaTeX \allowbreak and negative space (\!) before Danda (॥) 
    #or mantra numbers to force a line break opportunity.
    #"""
    
    # LaTeX command to allow a break and slightly pull back space
    break_command = r'\\allowbreak\\!'
    
    # 1. Targets the space before a standalone Danda: " ॥" -> "\allowbreak\!॥"
    # We replace the leading space and insert the break command.
    text = re.sub(r'\s(॥)', break_command + r'\1', text)

    # 2. Targets the space before the mantra number block: " ॥ १ ॥" -> "\allowbreak\!॥ १ ॥"
    mantra_number_pattern = r'(\s)(॥\s*[\u0966-\u096F][\u0966-\u096F\s]*॥)'
    
    # We replace the leading space and insert the break command.
    text = re.sub(mantra_number_pattern, break_command + r'\2', text)
    
    return text

    # ----------------------------------------------------
    # NEW UTILITY: Remove Internal Spaces (Continuous Script - Samhita aka Scriptio continua)
    # ----------------------------------------------------
def remove_mantra_spaces(text):
    """
    Removes all spaces within mantra lines to create continuous text.
    Preserves spaces in Colophons (lines containing 'इति', 'अथ', 'समाप्तः')
    and preserves blanks in Title blocks completely.
    """
    text = text.replace('\ufeff', '') # Remove BOM if present
    lines = text.split('\n')
    processed_lines = []
    
    preserve_keywords = ['इति', 'अथ', 'समाप्तः', 'संहिता', 'पर्वः', 'पर्वा', 'प्रारम्भः']
    
    in_preserve_block = False
    
    for line in lines:
        if '# Title #' in line or '# Supersection' in line:
            in_preserve_block = True
            
        if in_preserve_block or any(keyword in line for keyword in preserve_keywords):
            processed_lines.append(line)
        else:
            # It is a Mantra line: Remove all spaces and tabs
            clean_line = line.replace(' ', '').replace('\t', '')
            processed_lines.append(clean_line)
            
        if '# End of Title' in line or '# End of Supersection' in line:
            in_preserve_block = False
            
    return '\n'.join(processed_lines)


#----------------------------------------------------
# 7. CHECK OUTPUT PERMISSION (NEW FUNCTION)
# ----------------------------------------------------
def get_writable_filename(base_filename):
    """
    Checks if the PDF file is open/locked. If so, asks the user for a new name.
    """
    while True:
        pdf_filename = f"{base_filename}.pdf"
        
        # If the file doesn't exist, we are good to go.
        if not os.path.exists(pdf_filename):
            return base_filename

        # If it exists, try to open it in append mode to check for lock.
        try:
            with open(pdf_filename, 'a'):
                pass # Success, file is writable
            return base_filename
        except PermissionError:
            print(f"\nERROR: The file '{pdf_filename}' is open in another program.")
            print("Please close the PDF or provide a new filename.")
            new_name = input("Enter new base filename (or press Enter to retry): ").strip()
            
            if new_name:
                base_filename = new_name
            # If they just press Enter, we loop back and try the same name again (hoping they closed it)

# ----------------------------------------------------
# 5. Main processing function
# ----------------------------------------------------
def generate_and_compile_latex(input_text, base_filename='vedic_output'):
    """
    Generate LaTeX file with processed text and compile it using LuaLaTeX.
    """
    
    # Ensure output directory exists
    output_dir = "data/output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    # Prepend output directory to base_filename if not already present
    if not base_filename.startswith(output_dir):
        base_filename = os.path.join(output_dir, os.path.basename(base_filename))

    base_filename = get_writable_filename(base_filename)
    tex_filename = f'{base_filename}.tex'

    # 1. NEW: Remove spaces (Create Continuous Script)
    # We do this BEFORE regex conversions so it can see `# Title #` tags!
    processed_text = remove_mantra_spaces(input_text)

    #-- FIX: Corrected processing pipeline ---
    # NEW: Handle Markdown-style Title and Supersection markers BEFORE latex linebreaking mechanics
    def replace_main_title_latex(match):
        content = match.group(1).strip()
        return r'\clearpage\thispagestyle{empty}\vspace*{2in}{\centering\Huge\bfseries\textcolor{AccentGreen}{' + content + r'}\par}\vfill\clearpage'
    processed_text = re.sub(r'#\s*Title\s*#(.*?)#\s*End of Title\s*#', replace_main_title_latex, processed_text, flags=re.DOTALL | re.IGNORECASE)

    def replace_supersection_latex(match):
        content = match.group(1).strip()
        return r'\clearpage\phantomsection\addcontentsline{toc}{part}{' + content + r'}\vspace*{1em}{\centering\huge\bfseries\textcolor{AccentGreen}{' + content + r'}\par}\vspace*{1em}'
    processed_text = re.sub(r'#\s*Supersection title\s*#(.*?)#\s*End of Supersection title.*?#', replace_supersection_latex, processed_text, flags=re.DOTALL | re.IGNORECASE)
    
    # 1. First, fix visarga ordering
    processed_text = fix_visarga_accent_order_local(processed_text)
    processed_text = handle_consecutive_accents(processed_text)
    
    # 2. Then replace all accents with LaTeX commands
    # (The \kerns we added above are preserved)
    processed_text = replace_accents(processed_text)
   
    processed_text = add_enhanced_linebreaks(processed_text)

    # 6. Handle trailing whitespace LAST
    processed_text = eliminate_trailing_whitespace(processed_text)
    
    # 7. Add Summary Table
    summary_table = r'''
\clearpage
\begin{center}
\renewcommand{\arraystretch}{1.2}
\begin{tabular}{|l|c|c|}
\hline
\textbf{काण्डं} & \textbf{खण्डं} & \textbf{ऋक्} \\
\hline
आग्नेयम् & १२ & ११६ \\
तद्वम् & १२ & ११८ \\
बृहति & ८ & ८० \\
असावि & ६ & ५७ \\
ऐन्द्रम् & १० & ९७ \\
पवमानम् & ११ & ११९ \\
आरणम् & ६ & ५४ \\
शाक्वरम् & १ & ४ \\
\hline
 & \textbf{६६} & \textbf{६४५} \\
\hline
\end{tabular}
\end{center}
'''
    processed_text += summary_table
    # --- End of pipeline fix ---


    # Get the absolute path to the font directory
    # base_dir is defined in main, but we are in a function. 
    # Let's derive it relative to this script file location (src/)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Pointing to the root fonts directory as requested
    # Note: AdishilaVedic font files were not found in the repository. 
    # Please ensure they are located in the 'fonts' directory.
    font_path = os.path.join(base_dir, "fonts").replace("\\", "/") + "/"
    
    # Create LaTeX document
    latex_content = r'''\documentclass[12pt,a4paper]{article}
\usepackage{fontspec}
\usepackage[margin=1in]{geometry}
\usepackage{setspace}
\usepackage[dvipsnames]{xcolor} % Added for colors
\usepackage[hidelinks]{hyperref} % Added for phantomsection/toc support
\onehalfspacing

% Set the main font
\setmainfont[
    Path = ''' + font_path + r''',
    Extension = .ttf,
    UprightFont = *,
    AutoFakeBold=1.5,
    Script=Devanagari,
    Renderer=HarfBuzz,
]{''' + CURRENT_PDF_FONT + r'''}

% Command to format accent marks with larger size and bold
\newcommand{\accentmark}[2]{%
    {\fontsize{#1pt}{#1pt}\selectfont\bfseries\addfontfeature{FakeBold=3}#2}%
}

% --- CUSTOM COLORS (Matching HTML color scheme) ---
''' + (r'''
\definecolor{AccentBlue}{HTML}{062b66}
\definecolor{AccentPurple}{HTML}{7b1fa2}
\definecolor{AccentGreen}{HTML}{0a3b11}
\definecolor{SwaraRed}{HTML}{c62828}
''' if CURRENT_PDF_COLOR_MODE == 'color' else r'''
\definecolor{AccentBlue}{HTML}{000000}
\definecolor{AccentPurple}{HTML}{000000}
\definecolor{AccentGreen}{HTML}{000000}
\definecolor{SwaraRed}{HTML}{000000}
''') + r'''

% --- ACCENT OVERLAP ADJUSTMENT ---
% Defines a small negative space (kerning) to pull the next character closer
% Used when two "danger" accents (Anudatta/Kampa) appear consecutively.
\newcommand{\accentadj}{\kern0.15ex}



% --- ADD THESE LINES FOR AGGRESSIVE LINE BREAKING ---
\setlength{\emergencystretch}{1em}
\tolerance=10000 % Allow high tolerance for stretching/shrinking lines
\pretolerance=10000 % Allow high pretolerance
\emergencystretch=1in % Allow emergency stretching to fit text
\setlength{\parindent}{0pt} % Removes the indentation at start of paragraphs
\centering                % Forces text to be CENTERED (as requested)

\begin{document}
\fontsize{18pt}{27pt}\selectfont
\color{''' + ('AccentBlue' if CURRENT_PDF_COLOR_MODE == 'color' else 'black') + r'''}

''' + processed_text + r'''

\end{document}
'''
    
    # Write LaTeX file
    try:
        with open(tex_filename, 'w', encoding='utf-8') as f:
            f.write(latex_content)
        
        print(f"LaTeX file created: {tex_filename}")
        
        # Compile with LuaLaTeX
        print("Compiling with LuaLaTeX...")
        latex_dir = os.path.dirname(os.path.abspath(tex_filename))
        for i in range(2): # 2 passes for TOC if ever needed, though Rik table doesn't have TOC
            result = subprocess.run(['lualatex', '-interaction=nonstopmode', f'-output-directory={latex_dir}', tex_filename], 
                                  capture_output=True, text=True, check=True, encoding='utf-8')
        
        print(f"✓ PDF created successfully: {base_filename}.pdf")
        
    except FileNotFoundError:
        print("Error: LuaLaTeX not found.")
    except subprocess.CalledProcessError as e:
        print("Error during compilation:")
        if e.stdout: print('\n'.join(e.stdout.splitlines()[-10:]))
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# ----------------------------------------------------
# 8. HTML GENERATION (NEW)
# ----------------------------------------------------
def replace_accents_html(text):
    """
    Replaces ASCII markers with HTML Unicode entities wrapped in spans for positioning.
    Matches the style of Rik_Devanagari_Unicode.html
    """
    replacements = [
        ('(1)', '<span class="accent-swarita">&#x0951;</span>'),  # Swarita
        ('(2)', '<span class="accent-anudatta">&#x1CD2;</span>'),  # Anudatta
        ('(3)', '<span class="accent-kampa">&#x1CF8;</span>'),  # Kampa
        ('(4)', '<span class="accent-trikampa">&#x1CF9;</span>'),  # Trikampa
    ]
    for marker, replacement in replacements:
        text = text.replace(marker, replacement)
    return text

def format_text_html(text):
    toc_entries = []

    # Normalize dandas
    text = text.replace('II.', '॥').replace('II', '॥').replace('||', '॥')
    text = text.replace('|', '।').replace('।', '। ') # Add space after single danda
    
    # Handle Supersections
    def supersection_replacer(match):
        content = match.group(1).strip()
        header_id = f"supersection-{len(toc_entries)}"
        toc_entries.append({
            'title': content,
            'id': header_id,
            'is_chapter': True
        })
        return f'</div></div><div class="section"><h1 id="{header_id}" class="chapter-title" style="color: var(--accent-green)">{content}</h1></div><div class="subsection"><div class="rik-text">'
    text = re.sub(r'<SUPERSECTION>(.*?)</SUPERSECTION>', supersection_replacer, text, flags=re.DOTALL)
    
    # Handle Headers (Pattern: || ... Atha/Iti ... ||)
    # We strip the dandas for the title output and wrap in section-title
    # Regex finds: || [Content] ||
    def header_replacer(match):
        content = match.group(1).strip()
        # Remove leading dandas
        content = re.sub(r'^[॥\s]+', '', content)
        # Remove trailing dandas ONLY if NOT part of a numeral block (text ending in digits + close danda)
        # Check if content ends with something like "॥ १ ॥" or "|| 1 ||" (normalized to ॥)
        # Regex: Ends with ॥ then space then digits then space then ॥
        if not re.search(r'॥\s*[\d\u0966-\u096F]+\s*॥$', content):
             content = re.sub(r'[॥\s]+$', '', content)
             
        # Normalize internal spaces
        content = re.sub(r'\s+', ' ', content).strip()
        
        # ID creation for TOC
        header_id = f"header-{len(toc_entries)}"
        is_chapter = 'उत्तरार्चिकम्' in content or 'संहिता' in content
        
        toc_entries.append({
            'title': content,
            'id': header_id,
            'is_chapter': is_chapter
        })
             
        # Close previous subsection and rik-text divs (</div></div>)
        # Insert independent Section Header block
        # Open new subsection and rik-text divs
        if is_chapter:
             return f'</div></div><div class="section"><h1 id="{header_id}" class="chapter-title">{content}</h1></div><div class="subsection"><div class="rik-text">'
        return f'</div></div><div class="section"><h2 id="{header_id}" class="section-title">{content}</h2></div><div class="subsection"><div class="rik-text">'

    # Regex matches: 
    # 1. Optional leading danda
    # 2. Atha/Iti/Samaptah
    # 3. Content until...
    # 4. Closing danda OR "Khanda" OR "Kandah" OR "Uttararchikam"
    # 5. Optional suffix: EITHER a full numeral block (|| N ||) OR just a danda (||)
    # UPDATED: Added |काण्डः|उत्तरार्चिकम् to match LaTeX logic.
    # UPDATED: Accept [~\s]* before suffix to be robust.
    pat_headers = r'^\s*((?:॥\s*)?(?:अथ|इति|समाप्तः).*?(?:॥|खण्डः|काण्डः|उत्तरार्चिकम्)(?:[~\s]*॥\s*[\d\u0966-\u096F]+\s*॥|[~\s]*॥)?)'
    text = re.sub(pat_headers, header_replacer, text, flags=re.DOTALL | re.MULTILINE)
    
    # Handle Mantra numbers (|| 1 ||)
    # Wrap in span to prevent breaking and style, then add <br> for new line after each Rik
    # Enforce spaces around the number: ॥ N ॥
    text = re.sub(r'॥\s*([\d\u0966-\u096F]+)\s*॥', r'<span class="mantra-number">॥ \1 ॥</span><br>', text)
    
    # Replace newlines with <br> for text content
    text = text.replace('\n', '<br>\n')
    
    # Wrap initial content.
    # We assume the text starts with mantra content. 
    # If the text immediately starts with a header, the regex replacement above will have put 
    # two closing divs at the very start (</div></div><div class="section"...).
    # To handle this cleanly, we simply prepend the opening tags. 
    # Modern parsers will ignore the initial orphan closing tags if they occur.
    text = '<div class="subsection"><div class="rik-text">' + text
        
    text += '</div></div>' # Close last tags
    
    return text, toc_entries

def generate_html(input_text, base_filename):
    """
    Generates an HTML version of the Vedic text.
    """
    # Ensure output directory exists (replicate logic from latex function)
    # We assume run from root
    output_dir = os.path.join("data", "output")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Prepend output directory to base_filename if not already present
    # Check if it looks like a path
    if os.sep not in base_filename and '/' not in base_filename:
         base_filename = os.path.join(output_dir, base_filename)
    
    # Pipeline
    
    # 1. Remove spaces (Continuous Script) BEFORE parsing markdown titles
    processed_text = remove_mantra_spaces(input_text)
    
    # NEW: Handle Markdown-style Title and Supersection markers BEFORE html linebreaking mechanics
    def replace_main_title_html(match):
        content = match.group(1).strip()
        return f'<div class="title-page"><h1 class="chapter-title">{content}</h1></div>'
    processed_text = re.sub(r'#\s*Title\s*#(.*?)#\s*End of Title\s*#', replace_main_title_html, processed_text, flags=re.DOTALL | re.IGNORECASE)

    # Tag supersections to parse in format_html
    def replace_supersection_html(match):
        content = match.group(1).strip()
        return f'<SUPERSECTION>{content}</SUPERSECTION>'
    processed_text = re.sub(r'#\s*Supersection title\s*#(.*?)#\s*End of Supersection title.*?#', replace_supersection_html, processed_text, flags=re.DOTALL | re.IGNORECASE)
    
    subtitle_html = ""
    
    # 2. Replace Accents
    processed_text = fix_visarga_accent_order_local(processed_text)
    processed_text = replace_accents_html(processed_text)
    
    # 3. Formatting
    processed_text, toc_entries = format_text_html(processed_text)
    
    # Build TOC HTML
    toc_html = '<div class="toc"><h2>अनुक्रमणिका</h2><ul>'
    for entry in toc_entries:
        cls = "toc-chapter" if entry['is_chapter'] else "toc-section"
        toc_html += f'<li class="{cls}"><a href="#{entry["id"]}">{entry["title"]}</a></li>'
    toc_html += '</ul></div>'
    
    # Choose color CSS based on flag
    html_colors = f'''
        :root {{
            --primary-color: #2d3a4a;
            --accent-blue: #1565c0;
            --accent-green: #2e7d32;
            --accent-skyblue: #039BE5;
            --accent-purple: #7b1fa2;
            --swara-red: #c62828;
            --bg-light: #f8f9fa;
            --border-color: #dee2e6;
        }}''' if CURRENT_PDF_COLOR_MODE == 'color' else f'''
        :root {{
            --primary-color: #000000;
            --accent-blue: #000000;
            --accent-green: #000000;
            --accent-skyblue: #000000;
            --accent-purple: #000000;
            --swara-red: #000000;
            --bg-light: #ffffff;
            --border-color: #dddddd;
        }}'''
        
    # HTML Template
    html_content = f'''<!DOCTYPE html>
<html lang="sa">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>॥ सामसंहिता ॥</title>
    <style>
        {html_colors}
        
        * {{
            box-sizing: border-box;
        }}

        body {{
            font-family: 'AdishilaVedic', 'AdishilaSanVedic', 'Noto Sans Devanagari', 'Siddhanta', 'Arial Unicode MS', sans-serif;
            font-size: 1.3rem;
            line-height: 1.8;
            color: var(--primary-color);
            background: var(--bg-light);
            margin: 0;
            padding: 0;
        }}
        
        .container {{
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            background: white;
            min-height: 100vh;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }}
        
        /* Header Styles */
        .title-page {{
            text-align: center;
            padding: 60px 20px;
            border-bottom: 2px solid var(--border-color);
            margin-bottom: 40px;
        }}
        
        .title-page h1 {{
            font-size: 2.5rem;
            color: var(--primary-color);
            margin: 0;
        }}
        
        /* Chapter/Section Styles */
        .section {{
            margin-top: 30px;
            padding-top: 15px;
            border-top: 1px solid var(--border-color);
        }}
        
        .section-title {{
            text-align: center;
            font-size: 2.0rem;
            color: var(--accent-green);
            margin-bottom: 8px;
        }}

        .chapter-title {{
            text-align: center;
            font-size: 2.25rem;
            color: var(--accent-skyblue);
            margin-bottom: 20px;
        }}
        
        /* Mantra Styles */
        .subsection {{
            margin: 0;
            padding: 3px 10px;
            background: white;
            border-left: 4px solid var(--accent-blue);
            text-align: center;
            margin-bottom: 15px;
        }}
        
        .rik-text {{
            text-align: center;
            color: var(--accent-blue);
            font-size: 1.5rem;
            margin-bottom: 0;
        }}
        
        .mantra-number {{
            display: inline-block;
            white-space: nowrap;
            color: var(--primary-color);
            font-weight: bold;
        }}
        
        /* Accent marks - zero-width positioning for fonts without native Vedic support */
        .accent-swarita {{
            display: inline-block;
            width: 0;
            overflow: visible;
            color: var(--accent-blue);
            font-weight: bold;
            font-size: 1.2em;
            position: relative;
            left: -0.1em;
            top: -0.15em;
        }}
        
        .accent-anudatta {{
            display: inline-block;
            width: 0;
            overflow: visible;
            color: var(--accent-blue);
            font-weight: bold;
            font-size: 1.2em;
            position: relative;
            left: -0.1em;
            top: -0.15em;
        }}
        
        .accent-kampa {{
            display: inline-block;
            width: 0;
            overflow: visible;
            color: var(--accent-blue);
            font-weight: bold;
            font-size: 1.2em;
            position: relative;
            left: -0.1em;
            top: -0.15em;
        }}
        
        .accent-trikampa {{
            display: inline-block;
            width: 0;
            overflow: visible;
            color: var(--accent-blue);
            font-weight: bold;
            font-size: 1.2em;
            position: relative;
            left: -0.1em;
            top: -0.15em;
        }}
        
        /* TOC Styles */
        .toc {{
            background: #f1f3f5;
            padding: 20px;
            margin: 20px auto;
            border-radius: 8px;
            border: 1px solid var(--border-color);
        }}
        .toc h2 {{
            text-align: center;
            color: var(--primary-color);
            margin-top: 0;
            font-size: 1.8rem;
        }}
        .toc ul {{
            list-style: none;
            padding: 0;
        }}
        .toc li {{
            margin-bottom: 8px;
        }}
        .toc a {{
            text-decoration: none;
            color: var(--accent-blue);
            font-size: 1.2rem;
            transition: color 0.2s;
        }}
        .toc a:hover {{
            color: var(--accent-green);
            text-decoration: underline;
        }}
        .toc-chapter {{
            font-weight: bold;
            font-size: 1.4rem;
            margin-top: 15px;
            text-align: center;
        }}
        .toc-section {{
            padding-left: 20px;
        }}
        
        /* TOC Styles */
        .toc {{
            background: #f1f3f5;
            padding: 20px;
            margin: 20px auto;
            border-radius: 8px;
            border: 1px solid var(--border-color);
        }}
        .toc h2 {{
            text-align: center;
            color: var(--primary-color);
            margin-top: 0;
            font-size: 1.8rem;
        }}
        .toc ul {{
            list-style: none;
            padding: 0;
            columns: 2;
            column-gap: 40px;
        }}
        @media (max-width: 600px) {{
            .toc ul {{
                columns: 1;
            }}
        }}
        .toc li {{
            margin-bottom: 8px;
            break-inside: avoid;
        }}
        .toc a {{
            text-decoration: none;
            color: var(--accent-blue);
            font-size: 1.2rem;
            transition: color 0.2s;
        }}
        .toc a:hover {{
            color: var(--accent-green);
            text-decoration: underline;
        }}
        .toc-chapter {{
            font-weight: bold;
            font-size: 1.4rem;
            margin-top: 15px;
            text-align: center;
        }}
        .toc-section {{
            padding-left: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="title-page">
            <h1>॥ सामसंहिता ॥</h1>
            {subtitle_html}
        </div>
        {toc_html}
        {processed_text}
    </div>
</body>
</html>'''

    html_filename = f"{base_filename}.html"
    try:
        with open(html_filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"✓ HTML created successfully: {html_filename}")
    except Exception as e:
        print(f"Error creating HTML: {e}")


if __name__ == "__main__":
    import argparse
    
    # Use relative path for portability
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    default_input = os.path.join(base_dir, "data", "input", "vedic_text.txt")
    
    parser = argparse.ArgumentParser(description='Generate Rik for Samhita with PDF output.')
    parser.add_argument('-i', '--input', default=default_input,
                        help=f'Path to input text file (default: {default_input})')
    parser.add_argument('-o', '--output', default='vedic_output',
                        help='Base name for output files (default: vedic_output)')
    parser.add_argument('-f', '--format', choices=['pdf', 'html', 'all'], default='all',
                        help='Output format: pdf, html, or all (default: all)')
    parser.add_argument('--pdf-font', dest='pdf_font', default='NotoSansDevanagari',
                        help='Font for PDF output (default: NotoSansDevanagari)')
    parser.add_argument('--pdf-color-mode', dest='pdf_color_mode',
                        choices=['bw', 'color'], default='color',
                        help='Color mode for PDF output: bw or color (default: color)')
    parser.add_argument('--draft', action='store_true',
                        help='Enable draft mode (no new pages for each Khandah and Atha)')
    
    args = parser.parse_args()
    
    input_file = args.input
    output_base = args.output
    output_format = args.format
    
    CURRENT_PDF_FONT = args.pdf_font
    CURRENT_PDF_COLOR_MODE = args.pdf_color_mode
    CURRENT_PDF_DRAFT_MODE = args.draft
    
    if os.path.exists(input_file):
        try:
            print(f"Reading input from: {input_file}")
            with open(input_file, 'r', encoding='UTF-8') as f:
                text = f.read()                      
            
            # Generate LaTeX/PDF if requested
            if output_format in ['pdf', 'all']:
                generate_and_compile_latex(text, output_base)
            
            # Generate HTML if requested
            if output_format in ['html', 'all']:
                generate_html(text, output_base)
            
        except Exception as e:
            print(f"Error: {e}")
    else:
        print(f"Error: Input file not found: {input_file}")

#
