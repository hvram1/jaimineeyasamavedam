#from docx import Document
import platform
from pathlib import Path
import re

import sys
import argparse
#from doc_utils import escape_for_latex
import jinja2
import subprocess
import tempfile
import os
import json
import urllib.parse
import yaml
from requests.models import PreparedRequest
import grapheme

# --- New import for utility functions ---
from utils import (
    combine_halants, combine_ardhaksharas,
    my_encodeURL, my_format,
    replacecolon, normalize_and_trim,
    parse_mantra_for_latex, 
    sanitize_data_structure,
    load_pipeline_config,
    get_generated_metadata
)
# --- End new import ---

# ----------------------------------------------------
# DEVANAGARI NUMERAL CONVERSION
# ----------------------------------------------------
HTML_FOOTNOTE_COUNTER = 0
HTML_FOOTNOTES_ACCUMULATOR = []  # Accumulates footnotes across subsections within a section
HTML_SEEN_CONTENT_MAP = {} # Tracks seen footnote CONTENT -> (id, display_num)

def to_devanagari_numeral(num):
    """Convert Arabic numerals to Devanagari numerals."""
    if num is None:
        return ""
    mapping = {'0': '०', '1': '१', '2': '२', '3': '३', '4': '४',
               '5': '५', '6': '६', '7': '७', '8': '८', '9': '९'}
    return ''.join(mapping.get(c, c) for c in str(num))

def reset_html_footnote_counter(dummy=None):
    """Reset the HTML footnote counter AND clear the accumulator.
    Call this at section boundaries (start of each section).
    Takes a dummy argument so it can be used as a Jinja filter.
    Returns empty string so it doesn't output anything in the template.
    """
    global HTML_FOOTNOTE_COUNTER, HTML_FOOTNOTES_ACCUMULATOR, HTML_SEEN_CONTENT_MAP
    HTML_FOOTNOTES_ACCUMULATOR.clear()
    HTML_SEEN_CONTENT_MAP.clear()
    return ""

def accumulate_footnotes(footnotes_list):
    """Add footnotes to the section-level accumulator.
    Called by formatting functions instead of rendering inline.
    """
    global HTML_FOOTNOTES_ACCUMULATOR, HTML_SEEN_CONTENT_MAP
    HTML_FOOTNOTES_ACCUMULATOR.extend(footnotes_list)

def render_section_footnotes(dummy=None):
    """Render all accumulated footnotes for this section.
    Call this at section end in the template.
    Returns HTML for the footnote section, or empty string if no footnotes.
    """
    global HTML_FOOTNOTES_ACCUMULATOR
    
    if not HTML_FOOTNOTES_ACCUMULATOR:
        return ""
        
    output = ['<hr class="footnote-separator"/>']
    output.append('<div class="footnote-section">')
    for unique_id, display_num, text in HTML_FOOTNOTES_ACCUMULATOR:
        output.append(f'<div class="footnote-item" id="{unique_id}"><sup class="footnote-ref">{display_num}</sup> {text}</div>')
    output.append('</div>')
    
    return '\n'.join(output)



CURRENT_PDF_FONT = "AdishilaVedic"
CURRENT_TOC_LEVEL = "section"

# ----------------------------------------------------
# 1. NEW UTILITY: Local Visarga Accent Ordering
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
# 2. NEW UTILITY: Accent Replacements (RAISED ZERO-WIDTH)
# ----------------------------------------------------
def replace_accents(text):
    r"""
    Replaces ASCII markers (1), (2), etc., with raised accent marks.
    
    Uses \makebox[0pt] to create zero-width accent overlays that don't
    add horizontal spacing. The accents are raised using \raisebox and
    made bold/larger using \accentmark.
    
    Unicode Vedic Accent Characters:
    - U+0951 = ॑ (Swarita - vertical line above)
    - U+1CD2 = ᳒ (Anudatta - horizontal line below) 
    - U+1CF8 = ᳸ (Kampa - curved mark)
    - U+1CF9 = ᳹ (Trikampa - double curve)
    """
    if not text: return text
    
    if 'Adishila' in CURRENT_PDF_FONT:
        replacements = [
            ('(1)', r'\raisebox{0.6ex}{\accentmark{12}{\char"0951}}'),
            ('(2)', r'\raisebox{0.6ex}{\accentmark{15}{\char"1CD2}}'),
            ('(3)', r'\raisebox{0.4ex}{\accentmark{12}{\char"1CF8}}'),
            ('(4)', r'\raisebox{0.4ex}{\accentmark{12}{\char"1CF9}}'),
        ]
    else:
        # For Noto Sans and other fonts, use a Non-Breaking Space (\char"00A0) as a base
        # to suppress dotted circles. Wrap in \makebox[0pt] to hide the NBSP width.
        replacements = [
            ('(1)', r'\raisebox{0.7ex}{\makebox[0pt]{\accentmark{12}{\char"00A0\char"0951}}}'), # Swarita
            ('(2)', r'\raisebox{-0.1ex}{\makebox[0pt]{\accentmark{15}{\char"00A0\char"1CD2}}}'), # Anudatta
            ('(3)', r'\raisebox{0.5ex}{\makebox[0pt]{\accentmark{12}{\char"00A0\char"1CF8}}}'), # Kampa
            ('(4)', r'\raisebox{0.5ex}{\makebox[0pt]{\accentmark{12}{\char"00A0\char"1CF9}}}'), # Trikamba
        ]
  
    for marker, replacement in replacements:
        text = text.replace(marker, replacement)
    
    return text

def replace_accents_html(text):
    """
    Replaces ASCII markers with HTML Unicode entities wrapped in spans for positioning.
    """
    if not text:
        return text
    replacements = [
        ('(1)', '<span class="accent-swarita">&#x0951;</span>'),  # Swarita
        ('(2)', '<span class="accent-anudatta">&#x1CD2;</span>'),  # Anudatta
        ('(3)', '<span class="accent-kampa">&#x1CF8;</span>'),  # Kampa
        ('(4)', '<span class="accent-trikampa">&#x1CF9;</span>'),  # Trikampa
    ]
    for marker, replacement in replacements:
        text = text.replace(marker, replacement)
    return text

# ----------------------------------------------------
# 2. NEW UTILITY: Consecutive Accent Handler
# ----------------------------------------------------
def handle_consecutive_accents(text):
    r"""
    Previously inserted \kern to separate specific accent transitions 
    that were prone to visual overlap with AdishilaVedic font.
    
    With Noto Sans Devanagari, this kerning is not needed and causes
    unwanted spacing. Returning text unchanged.
    """
    if not text: return text
    
    # NOTE: Kerning disabled for Noto Sans Devanagari
    # The font handles accent spacing properly without manual adjustments
    # Keep the patterns commented for reference if switching fonts:
    
    # CASE A: Anudatta (2) followed by Anudatta (2)
    # pat_2_2 = r'(\(2\))(?=[^()]{1,5}\(2\))'
    # text = re.sub(pat_2_2, r'\1\\kern0.15em', text)

    # CASE B: Swarita (1) followed by Anudatta (2)
    # pat_1_2 = r'(\(1\))(?=[^()]{1,5}\(2\))'
    # text = re.sub(pat_1_2, r'\1\\kern0.15em', text)

    # CASE C: Anudatta (2) followed by Kampa (3) or Trikampa (4)
    # pat_2_3= r'(\(2\))(?=[^()]{1,5}\(3\))'
    # text = re.sub(pat_2_3, r'\1\\kern0.15em', text)

    # pat_2_4= r'(\(2\))(?=[^()]{1,5}\(4\))'
    # text = re.sub(pat_2_4, r'\1\\kern0.15em', text)
    
    return text

# ----------------------------------------------------
# 3. NEW UTILITY: Remove Mantra Spaces (Samhita Mode)
# ----------------------------------------------------
def remove_mantra_spaces(text):
    """
    Removes all spaces within the text to create continuous Samhita text.
    Handles all types of Unicode whitespace characters.
    Preserves Dandas.
    """
    if not text: return text
    
    # Remove all Unicode whitespace characters using regex
    # \s covers: space, tab, newline, carriage return, form feed, vertical tab
    # Also explicitly remove non-breaking space (U+00A0) and other invisible separators
    text = re.sub(r'\s+', '', text)
    text = text.replace('\u00A0', '')  # Non-breaking space
    text = text.replace('\u200B', '')  # Zero-width space
    text = text.replace('\u200C', '')  # Zero-width non-joiner
    text = text.replace('\u200D', '')  # Zero-width joiner
    text = text.replace('\uFEFF', '')  # Byte order mark
    
    return text

def split_rik_lines_html(text):
    """
    Splits multi-Rik text so each Rik appears on its own line.
    Splits after each verse marker (॥ N ॥) and joins with <br>.
    If only one Rik is present, returns the text unchanged.
    """
    if not text:
        return text
    # Split after each ॥ N ॥ pattern (Devanagari or ASCII digits)
    # The marker stays at the end of each segment
    parts = re.split(r'((?:॥|\|\|)\s*[०-९\d]+\s*(?:॥|\|\|))', text)
    if len(parts) <= 1:
        return text
    # Re-join: marker goes with the preceding text segment
    lines = []
    current = ''
    for part in parts:
        if re.match(r'(?:॥|\|\|)\s*[०-९\d]+\s*(?:॥|\|\|)', part):
            current += part
            lines.append(current.strip())
            current = ''
        else:
            current += part
    # If there's leftover text after the last marker, append it
    if current.strip():
        lines.append(current.strip())
    # Filter out empty lines
    lines = [l for l in lines if l]
    if len(lines) <= 1:
        return text
    return '<br>'.join(lines)

def split_rik_lines_latex(text):
    """
    Splits multi-Rik text so each Rik appears on its own line in LaTeX.
    Splits after each verse marker (॥ N ॥) and joins with \\newline.
    If only one Rik is present, returns the text unchanged.
    """
    if not text:
        return text
    parts = re.split(r'((?:॥|\|\|)\s*[०-९\d]+\s*(?:॥|\|\|))', text)
    if len(parts) <= 1:
        return text
    lines = []
    current = ''
    for part in parts:
        if re.match(r'(?:॥|\|\|)\s*[०-९\d]+\s*(?:॥|\|\|)', part):
            current += part
            lines.append(current.strip())
            current = ''
        else:
            current += part
    if current.strip():
        lines.append(current.strip())
    lines = [l for l in lines if l]
    if len(lines) <= 1:
        return text
    # Use standard LaTeX line break (\\) for multi-verse Riks
    return ' \\\\ '.join(lines)
    

# ----------------------------------------------------
# FOOTNOTE PROCESSING UTILITIES
# ----------------------------------------------------
def process_footnotes_latex(text, footnotes_dict, seen_markers=None, subsection_key=None):
    """
    Replace (s1), (s2) markers with state-aware LaTeX footnotes/references.
    
    Args:
        text: The text containing footnote markers like (s1), (s2)
        footnotes_dict: Dictionary { "s1": "text" }
        seen_markers: set of seen markers ("s1", "s2") for this subsection scope
        subsection_key: unique ID for the subsection to generate stable labels
    """
    if not footnotes_dict:
        return text
    
    # We need to find all markers matching (s\d+) in the text
    # and replace them sequentially to update the seen_markers set.
    
    def replacer(match):
        marker = match.group(1) # s1
        full_marker = match.group(0) # (s1)
        
        if marker not in footnotes_dict:
            return full_marker # Keep original if not found (or log error)
            
        footnote_text = footnotes_dict[marker]
        
        if seen_markers is not None and subsection_key is not None:
             label = f"fn:{subsection_key}:{marker}"
             if marker in seen_markers:
                 # Reference existing footnote
                 # Use rule (2.5ex) to ensure top alignment + raisebox (1.2ex) to match template
                 return f"\\rule{{0pt}}{{2.5ex}}\\textsuperscript{{\\raisebox{{1.2ex}}{{\\normalfont\\ref{{{label}}}}}}}"
             else:
                 # Create new footnote with label
                 seen_markers.add(marker)
                 return f"\\rule{{0pt}}{{2.5ex}}\\footnote{{{footnote_text}\\label{{{label}}}}}"
        else:
             # Fallback to stateless replacement (old behavior)
             return f"\\rule{{0pt}}{{2.5ex}}\\footnote{{{footnote_text}}}"

    # Sanitize invisible characters that break footnote matching
    # These are zero-width chars that can appear around (s1) markers from copy-paste
    invisible_chars_pattern = r'[\u200b\u200c\u200d\ufeff\u2060\u180e\u00ad]'
    text = re.sub(invisible_chars_pattern, '', text)
    
    pattern = r'\((s\d+)\)'
    new_text = re.sub(pattern, replacer, text)
    
    return new_text

def process_footnotes_html(text, footnotes_dict, local_counter=0, seen_markers_map=None, subsection_key=None):
    """
    Replace (s1), (s2) markers with HTML superscript links.
    Uses LOCAL counter for display numbering (resets per subsection).
    Uses subsection_key for unique IDs to prevent collisions across document.
    
    Args:
        text: Text to process
        footnotes_dict: Dict mapping markers to text
        local_counter: Current local counter for this subsection (display only)
        seen_markers_map: Map of seen markers to (unique_id, display_num) in this subsection
        subsection_key: Unique key for this subsection
        
    Returns:
        (processed_text, list_of_footnotes_data, new_local_counter)
        footnotes_data tuple: (unique_id, display_num, text)
    """
    if not footnotes_dict:
        return text, [], local_counter
    
    footnotes_list = []
    
    import os
    
    # Sanitize invisible characters that break footnote matching
    invisible_chars_pattern = r'[\u200b\u200c\u200d\ufeff\u2060\u180e\u00ad]'
    text = re.sub(invisible_chars_pattern, '', text)
    
    # regex to find (sX)
    matches = list(set(re.findall(r'\(s\d+\)', text))) # set to unique within this text block
    # Sort matches
    matches.sort(key=lambda x: int(x[2:-1]))
    
    # Sort matches
    matches.sort(key=lambda x: int(x[2:-1]))


    for marker_full in matches:
        marker = marker_full[1:-1] # strip ( ) -> s1
        if marker in footnotes_dict:
             footnote_text = footnotes_dict[marker].strip()
             
             # Check if CONTENT has been seen in the broader context
             if seen_markers_map is not None and footnote_text in seen_markers_map:
                 # Reuse existing number and ID
                 unique_id, dev_num = seen_markers_map[footnote_text]
                 # For duplicates, link to existing ID
                 replacement = f'<sup class="footnote-ref"><a href="#{unique_id}">{dev_num}</a></sup>'
                 text = text.replace(marker_full, replacement)
             else:
                 # New footnote
                 local_counter += 1
                 # footnote_text already fetched above
                 devanagari_num = to_devanagari_numeral(local_counter)
                 
                 # Generate unique ID using subsection_key
                 safe_key = subsection_key if subsection_key else "unknown"
                 unique_id = f"fn-{safe_key}-{marker}"
                 
                 # Replace this specific marker occurrence
                 replacement = f'<sup class="footnote-ref"><a href="#{unique_id}" id="ref-{unique_id}">{devanagari_num}</a></sup>'
                 text = text.replace(marker_full, replacement)
                 
                 footnotes_list.append((unique_id, devanagari_num, footnote_text))
                 
                 if seen_markers_map is not None:
                     seen_markers_map[footnote_text] = (unique_id, devanagari_num)

    return text, footnotes_list, local_counter

def process_footnotes_text(text, footnotes_dict):
    """
    Replace (s1), (s2) markers with Devanagari superscript numerals for plain text.
    Uses Unicode superscript characters where available.
    
    Args:
        text: The text containing footnote markers
        footnotes_dict: Dictionary mapping marker to footnote text
    
    Returns:
        Tuple of (processed_text, footnotes_list for display)
    """
    if not footnotes_dict:
        return text, []
    
    footnotes_list = []
    
    for marker, footnote_text in sorted(footnotes_dict.items(), key=lambda x: int(x[0].replace('s', ''))):
        num = int(marker.replace('s', ''))
        devanagari_num = to_devanagari_numeral(num)
        pattern = rf'\({re.escape(marker)}\)'
        # Use parentheses for plain text to indicate superscript reference
        replacement = f'({devanagari_num})'
        text = re.sub(pattern, replacement, text)
        footnotes_list.append((devanagari_num, footnote_text))
    
    return text, footnotes_list


def split_rik_lines_text(text):
    """Ensure each Rik verse ends with a newline for plain text output."""
    if not text:
        return ""
    # Pattern to match a verse marker (e.g., ॥ ७ ॥) optionally followed by spaces
    # and ensure there's a newline after it.
    pattern = r'(॥\s*[\d०-९]+\s*॥)\s*'
    # Replace with the marker followed by a newline, but only if not already followed by one
    # To keep it simple, we'll just replace marker+any trailing space with marker+\n
    return re.sub(pattern, r'\1\n', text).strip()


def replace_footnote_markers_filter(text, footnotes_dict={}):
    """Filter to replace footnote markers in text."""
    if not text:
        return ""
    processed_text, _ = process_footnotes_text(text, footnotes_dict)
    return processed_text


def format_dandas(text):
    """
    Adds spaces around danda symbols (| || । ॥) and cleans up extra spaces.
    Safe to use on strings that might be None.
    """
    if not text or not isinstance(text, str):
        return text

    # --- STEP 1: Normalize Double Dandas ---
    # Convert ASCII ||, spaced | |, Devanagari ।। (two singles), and OCR II to ॥
    # IMPORTANT: We must catch '।।' (two U+0964) before processing singles!
    text = re.sub(r'\|\|', '॥', text)       
    text = re.sub(r'\|\s*\|', '॥', text)    
    text = re.sub(r'।।', '॥', text)         
    text = re.sub(r'II', '॥', text)         

    # --- STEP 2: Normalize Single Danda ---
    # Convert remaining ASCII | to Devanagari ।
    text = text.replace('|', '।')

    # --- STEP 3: Apply Spacing Rules ---
    
    # Rule B: Double Danda (॥) -> Standard spaces
    text = text.replace('॥', r' ॥ ')

    # --- STEP 4: Cleanup ---
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    
    # --- STEP 5: Prevent Line Breaks in Mantra Numbers ---
    danda_pattern = r'(?:\|\||॥)'      
    digits = r'[\d०-९]+'        
    pattern = rf'({danda_pattern})\s+({digits})\s+({danda_pattern})'
    text = re.sub(pattern, r'\\mbox{\1 \2 \3}', text)

    # Rule A: Single Danda (।) -> Add \enspace BEFORE it
    # \enspace is 0.5em, roughly the width of a digit, very visible.
    # We also keep a normal space after it.
    text = text.replace('।', r'\enspace । ')

    return text
    
def clean_stack_arg(text):
    r"""
    Aggressively removes LaTeX newlines, paragraphs, comments, and line breaks.
    """
    if not text:
        return ""
    text = re.sub(r'\\+newline', '', text)
    text = re.sub(r'\\par', '', text)
    text = text.replace('%', '').replace('\n', ' ').replace('\r', '')
    return text.strip()

                        
def CreatePdf(templateFileName, name, DocfamilyName, data, prayogas=None, current_os="Windows", output_mode="combined", font_family="AdishilaVedic", doc_title_sa="जैमिनीय साम संहिता", pdf_color_mode="bw", closing_mantras=None, summary_table=None, total_riks=None, total_samams=None, summary_title="संहिता सङ्ख्या", toc_level='section', has_riks=True, has_samams=True, output_dir_override=None, name_override=None, jsv_version=None, generated_at=None, kpully=False):
    data=escape_for_latex(data)
    
    outputdir="data/output"
    logdir=f"{outputdir}/logs"
    exit_code=0
    
    # Use overrides if provided
    name = name_override or name
    outputdir = output_dir_override or f"{outputdir}/pdf/{DocfamilyName}"
    
    TexFileName=f"{name}_{DocfamilyName}.tex"
    PdfFileName=f"{name}_{DocfamilyName}.pdf"
    TocFileName=f"{name}_{DocfamilyName}.toc"
    LogFileName=f"{name}_{DocfamilyName}.log"
    template = templateFileName
    Path(outputdir).mkdir(parents=True, exist_ok=True)
    Path(logdir).mkdir(parents=True, exist_ok=True)
    
    if not jsv_version or not generated_at:
        from utils import get_generated_metadata
        meta = get_generated_metadata()
        jsv_version = jsv_version or meta['version']
        generated_at = generated_at or meta['generated_at']
    
    document = template.render(
        supersections=data, 
        os=current_os, 
        output_mode=output_mode,
        version=jsv_version,
        generated_at=generated_at,
        font_family=font_family,
        doc_title_sa=doc_title_sa,
        pdf_color_mode=pdf_color_mode,
        closing_mantras=closing_mantras or [],
        font_path=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "fonts").replace("\\", "/") + "/",
        summary_table=summary_table,
        total_riks=total_riks,
        total_samams=total_samams,
        summary_title=summary_title,
        toc_level=toc_level,
        has_riks=has_riks,
        has_samams=has_samams,
        prayogas=prayogas or [],
        kpully=kpully
    )
    

    tmpdirname="."
    with tempfile.TemporaryDirectory() as tmpdirname:
        tmpfilename=f"{tmpdirname}/{TexFileName}"

        with open(tmpfilename,"w",encoding="utf-8") as f:
            f.write(document)
        
        try:
            cmd = ["xelatex", "-interaction=nonstopmode", tmpfilename]
            proc = subprocess.run(cmd, cwd=tmpdirname, capture_output=True, text=True, encoding='utf-8', errors='ignore')
            
            # Step 2: run makeindex if .idx file exists to generate index (.ind)
            idx_file = Path(tmpdirname) / f"{Path(TexFileName).stem}.idx"
            if idx_file.exists() and idx_file.stat().st_size > 0:
                cmd_idx = ["makeindex", "-c", "-q", str(idx_file.name)]
                subprocess.run(cmd_idx, cwd=tmpdirname, capture_output=True, text=True, encoding='utf-8', errors='ignore')
                
            # Step 3: Pass 2 of xelatex to resolve TOC, index, and page cross-references
            proc = subprocess.run(cmd, cwd=tmpdirname, capture_output=True, text=True, encoding='utf-8', errors='ignore')
            if proc.returncode != 0:
                print(f"[WARNING] xelatex compilation returned non-zero code {proc.returncode}")
        except Exception as e:
            print(f"[WARNING] Failed to run xelatex: {e}")
        
        src_pdf_file=Path(f"{tmpdirname}/{PdfFileName}")
        dst_pdf_file=Path(f"{outputdir}/{PdfFileName}")
        src_log_file=Path(f"{tmpdirname}/{LogFileName}")
        dst_log_file=Path(f"{logdir}/{LogFileName}")
        src_tex_file=Path(f"{tmpdirname}/{TexFileName}")
        dst_tex_file=Path(f"{outputdir}/{TexFileName}")
        
        import shutil
        path = Path(src_tex_file)
        if path.is_file():
            try:
                shutil.copyfile(src_tex_file, dst_tex_file)
                src_tex_file.unlink(missing_ok=True)
            except Exception as e:
                print(f"[WARN] Could not move TeX file: {e}")
        path = Path(src_pdf_file)
        if path.is_file():
            try:
                shutil.copyfile(src_pdf_file, dst_pdf_file)
                src_pdf_file.unlink(missing_ok=True)
            except Exception as e:
                print(f"[WARN] Could not overwrite PDF file (may be locked in viewer): {e}")
        path = Path(src_log_file)
        if path.is_file():
            try:
                shutil.copyfile(src_log_file, dst_log_file)
                src_log_file.unlink(missing_ok=True)
            except Exception as e:
                print(f"[WARN] Could not move log file: {e}")

    return exit_code

def CreateTextFile(templateFileName, name, DocfamilyName, data, output_mode="combined", doc_title_sa="जैमिनीय साम संहिता", closing_mantras=None, toc_level='section', output_dir_override=None, name_override=None, jsv_version=None, generated_at=None):
    outputdir="data/output"
    logdir="data/output/logs"
    exit_code=0
    
    TexFileName=f"{name}_{DocfamilyName}_Unicode.tex"
    PdfFileName=f"{name}_{DocfamilyName}_Unicode.pdf"
    TextFileName=f"{name}_{DocfamilyName}_Unicode.txt"
    TocFileName=f"{name}_{DocfamilyName}_Unicode.toc"
    LogFileName=f"{name}_{DocfamilyName}_Unicode.log"
    template = templateFileName
    outputdir = f"{outputdir}/txt/{DocfamilyName}"  # Use DocfamilyName for directory
    Path(outputdir).mkdir(parents=True, exist_ok=True)
    Path(logdir).mkdir(parents=True, exist_ok=True)
    
    from utils import get_generated_metadata
    meta = get_generated_metadata()
    
    document = template.render(
        supersections=data, 
        output_mode=output_mode,
        doc_title_sa=doc_title_sa,
        version=jsv_version or meta['version'],
        generated_at=generated_at or meta['generated_at'],
        closing_mantras=closing_mantras or [],
        toc_level=toc_level
    )
    

    tmpdirname="."
    with tempfile.TemporaryDirectory() as tmpdirname:
        tmpfilename=f"{tmpdirname}/{TextFileName}"

        with open(tmpfilename,"w",encoding="utf-8") as f:
            f.write(document)
        
        src_text_file=Path(f"{tmpdirname}/{TextFileName}")
        dst_text_file=Path(f"{outputdir}/{TextFileName}")
        
        path = Path(src_text_file)
        if path.is_file():
            if dst_text_file.exists():
                dst_text_file.unlink()
            src_text_file.rename(dst_text_file)  

    return exit_code


def escape_for_latex(data):
    if isinstance(data, dict):
        new_data = {}
        for key in data.keys():
            if key in ('malayalam-mantra-sets', 'corrected-mantra_sets', 'mantra_sets'):
                new_data[key] = data[key]
            else:
                new_data[key] = escape_for_latex(data[key])
        return new_data
    elif isinstance(data, list):
        return [escape_for_latex(item) for item in data]
    elif isinstance(data, str):
        latex_special_chars = {
            "&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#", "_": r"\_",
            "{": r"\{", "}": r"\}", "~": r"\textasciitilde{}", "^": r"\^{}",
            "\\": r"\textbackslash{}", "\n": " ", "-": r"{-}",
            "\xA0": "~", "[": r"{[}", "]": r"{]}",
        }
        return "".join([latex_special_chars.get(c, c) for c in data])

def _format_deva_word_latex(word: str, with_modifiers: bool = True) -> str:
    """Format any inline swara modifiers inside Devanagari words with a small gap."""
    if not word:
        return ""
    if not with_modifiers:
        for m_ch in ('_', '·', 'ॱ', '.', ',', '\\', '┃', 'L', '╷', '^', '⁀', '∧', '✓'):
            word = word.replace(m_ch, '')
        return word.replace('&', r'\&').replace('%', r'\%').replace('$', r'\$').replace('#', r'\#')
        
    gap = r"\hspace{0.18em}"
    res = []
    i = 0
    while i < len(word):
        ch = word[i]
        if ch == '_':
            res.append(f"{{\\textcolor{{ModifierSkyBlue}}{{\\raisebox{{-0.1ex}}{{\\rule{{0.3em}}{{0.13ex}}}}}}{gap}}}")
        elif ch in ('·', 'ॱ'):
            res.append(f"{{\\swarafont \\textcolor{{ModifierSkyBlue}}{{\\raisebox{{1.15ex}}{{\\hspace{{0.04em}}\\char\"E001}}}}{gap}}}")
        elif ch == '.':
            res.append(f"{{\\textcolor{{ModifierSkyBlue}}{{\\textbf{{.}}}}{gap}}}")
        elif ch == ',':
            res.append(f"{{\\textcolor{{ModifierSkyBlue}}{{\\textbf{{,}}}}{gap}}}")
        elif ch == '\\':
            res.append(f"{{\\swarafont \\textcolor{{ModifierSkyBlue}}{{\\raisebox{{-0.50ex}}{{\\hspace{{-0.20em}}\\char\"E003}}}}{gap}}}")
        elif ch in ('┃', 'L'):
            res.append(f"{{\\swarafont \\textcolor{{ModifierSkyBlue}}{{\\raisebox{{-0.35ex}}{{\\hspace{{0.06em}}\\char\"E002}}}}\\hspace{{0.18em}}}}")
        elif ch == '╷':
            res.append(f"{{\\swarafont \\textcolor{{ModifierSkyBlue}}{{\\raisebox{{0.15ex}}{{\\hspace{{0.04em}}\\char\"E008}}}}{gap}}}")
        elif ch == '&':
            res.append(r"\&")
        elif ch == '%':
            res.append(r"\%")
        elif ch == '$':
            res.append(r"\$")
        elif ch == '#':
            res.append(r"\#")
        else:
            res.append(ch)
        i += 1
    return "".join(res)


def _apply_deva_modifier_latex(chunk: str, mod: str) -> str:
    """Apply swara modifier styling in LaTeX with zero horizontal footprint and a small following gap."""
    m = mod.strip('()')
    gap = r"\hspace{0.18em}"
    if m in ('C', 'c', '·', 'ॱ', '\uE001'):
        # Upper shoulder dot (MOD-C)
        glyph = r"\rlap{\swarafont \textcolor{ModifierSkyBlue}{\raisebox{1.15ex}{\hspace{0.04em}\char" + '"E001}}}' + gap
        return f"{chunk}{glyph}"
    elif m in ('E', 'e', '┃', '\uE002'):
        # Tone Column (MOD-E) rendered AFTER the preceding akshara without overlapping 'a' extender
        glyph = r"\rlap{\swarafont \textcolor{ModifierSkyBlue}{\raisebox{-0.35ex}{\hspace{0.06em}\char" + '"E002}}}' + r"\hspace{0.18em}"
        return f"{chunk}{glyph}"
    elif m in ('G', 'g', '\\', '\uE003'):
        # Lower Under-Slash (MOD-G)
        glyph = r"\rlap{\swarafont \textcolor{ModifierSkyBlue}{\raisebox{-0.50ex}{\hspace{-0.20em}\char" + '"E003}}}' + gap
        return f"{chunk}{glyph}"
    elif m in ('A', 'a', '⁀', '\uE004'):
        # Melodic Arc (MOD-A)
        glyph = r"\rlap{\swarafont \textcolor{ModifierSkyBlue}{\raisebox{1.18ex}{\hspace{-0.38em}\char" + '"E004}}}' + gap
        return f"{chunk}{glyph}"
    elif m in ('D', 'd', '∧', 'Ʌ', '\uE006'):
        # Chevron Roof (MOD-D)
        glyph = r"\rlap{\swarafont \textcolor{ModifierSkyBlue}{\raisebox{1.15ex}{\hspace{-0.32em}\char" + '"E006}}}' + gap
        return f"{chunk}{glyph}"
    elif m in ('A1', 'a1', 'A_1', 'a_1', '\uE00D'):
        # Arc over Danda (MOD-A1)
        glyph = r"\rlap{\swarafont \textcolor{ModifierSkyBlue}{\raisebox{1.18ex}{\hspace{-0.58em}\char" + '"E00D}}}' + gap
        return f"{chunk}{glyph}"
    elif m in ('D1', 'd1', 'D_1', 'd_1', '↗', '\uE00E'):
        # Rising Stroke (MOD-D1)
        glyph = r"\rlap{\swarafont \textcolor{ModifierSkyBlue}{\raisebox{0.15ex}{\hspace{0.04em}\char" + '"E00E}}}' + gap
        return f"{chunk}{glyph}"
    elif m in ('D2', 'd2', 'D_2', 'd_2', '✓', '\uE00F'):
        # Check Tick (MOD-D2)
        glyph = r"\rlap{\swarafont \textcolor{ModifierSkyBlue}{\raisebox{0.15ex}{\hspace{0.04em}\char" + '"E00F}}}' + gap
        return f"{chunk}{glyph}"
    elif m in ('H', 'h', '|', '\uE00C'):
        # High-Pitch Swarita (MOD-H)
        glyph = r"\rlap{\swarafont \textcolor{ModifierSkyBlue}{\raisebox{1.15ex}{\hspace{0.04em}\char" + '"E00C}}}' + gap
        return f"{chunk}{glyph}"
    elif m in ('F', 'f', '╷', '\uE008'):
        # Danda with Dot (MOD-F)
        glyph = r"\rlap{\swarafont \textcolor{ModifierSkyBlue}{\raisebox{0.15ex}{\hspace{0.04em}\char" + '"E008}}}' + gap
        return f"{chunk}{glyph}"
    elif m == '_':
        glyph = r"\rlap{\textcolor{ModifierSkyBlue}{\raisebox{-0.1ex}{\rule{0.3em}{0.13ex}}}}" + gap
        return f"{chunk}{glyph}"
    elif m == '.':
        glyph = r"{\textcolor{ModifierSkyBlue}{\textbf{.}}}" + gap
        return f"{chunk}{glyph}"
    elif m == ',':
        glyph = r"{\textcolor{ModifierSkyBlue}{\textbf{,}}}" + gap
        return f"{chunk}{glyph}"
    else:
        return f"{chunk}({mod}){gap}"


def _format_single_deva_word_latex(tok, with_modifiers=True, exclude_mods=None):
    """Format a single Devanagari word token with swara stacking and modifiers."""
    if exclude_mods is None:
        exclude_mods = set()
    word = tok.get('word', '')
    swara = tok.get('swara', '')
    visarga = tok.get('visarga', '')
    if visarga:
        word += visarga
    
    if with_modifiers:
        core_word = word.rstrip('_,.\\·ॱ┃L╷^⁀∧✓')
        trailing_punct = word[len(core_word):]
        sw_parts, mods = _parse_swara_and_modifiers(swara)
        mods = [m for m in mods if m not in exclude_mods and m.strip('()') not in exclude_mods]
    else:
        core_word = word.rstrip('_,.\\·ॱ┃L╷^⁀∧✓')
        trailing_punct = ''
        sw_parts, _ = _parse_swara_and_modifiers(swara)
        mods = []
    
    sw_str = " ".join(sw_parts) if sw_parts else ""
    
    syllables = split_deva_syllables(core_word) if core_word else []
    last_syl = syllables.pop() if syllables else ''
    
    word_chunks = []
    for syl in syllables:
        syl_formatted = _format_deva_word_latex(syl, with_modifiers=with_modifiers)
        word_chunks.append(syl_formatted)
    
    last_syl_formatted = _format_deva_word_latex(last_syl, with_modifiers=with_modifiers) if last_syl else ''
    
    if sw_str and last_syl_formatted:
        clean_sw = sw_str.replace('{', '').replace('}', '')
        sw_styled = f"{{\\smallredfont \\bfseries \\textcolor{{SwaraRed}}{{{sw_str}}}}}"
        if len(clean_sw) > 1:
            chunk = f"\\stackleft{{{last_syl_formatted}}}{{{sw_styled}}}"
        else:
            chunk = f"\\stackcenter{{{last_syl_formatted}}}{{{sw_styled}}}"
    elif sw_str and not last_syl_formatted:
        sw_styled = f"{{\\smallredfont \\bfseries \\textcolor{{SwaraRed}}{{{sw_str}}}}}"
        chunk = f"\\stackcenter{{\\phantom{{अ}}}}{{{sw_styled}}}"
    else:
        chunk = f"{{{last_syl_formatted}}}"
    
    if with_modifiers:
        if trailing_punct:
            for p in trailing_punct:
                if p not in exclude_mods:
                    chunk = _apply_deva_modifier_latex(chunk, p)
        for mod in mods:
            chunk = _apply_deva_modifier_latex(chunk, mod)
    
    word_chunks.append(chunk)
    return "".join(word_chunks)


def _render_devanagari_mantra_body(subsection, subsection_key=None, seen_markers=None, with_modifiers: bool = None):
    """Helper to render Devanagari mantra body with swaras and modifiers."""
    if seen_markers is None:
        seen_markers = set()
    if with_modifiers is None:
        global CURRENT_WITH_SWARA_MODIFIERS
        with_modifiers = CURRENT_WITH_SWARA_MODIFIERS
        
    from malayalam.ml_text import tokenize_mantra_line
    
    mantra_sets = subsection.get('corrected-mantra_sets', [])
    if not mantra_sets:
        mantra_sets = subsection.get('mantra_sets', [])
    if not mantra_sets:
        return []

    MOD_A_SET = {'A', 'a', '⁀', '\uE004', '╭╮', '͡'}
    MOD_A1_SET = {'A1', 'a1', 'A_1', 'a_1', '\uE00D'}
    MOD_D_SET = {'D', 'd', '∧', 'Ʌ', '✓', '↗', 'D1', 'd1', 'D2', 'd2', '\uE006', '\uE00E', '\uE00F'}
    DEVA_DIGITS = str.maketrans('0123456789', '०१२३४५६७८९')
    
    footnote_data = subsection.get('footnotes', {})
    formatted_paragraphs = []
    
    for mantra_set in mantra_sets:
        line = mantra_set.get('corrected-mantra') or mantra_set.get('mantra', '')
        if not line:
            continue
        tokens = tokenize_mantra_line(line)
        paragraph_buffer = []
        
        idx = 0
        while idx < len(tokens):
            v_count, v_num = _match_verse_num_marker(tokens, idx)
            if v_count > 0:
                v_num_deva = str(v_num).translate(DEVA_DIGITS)
                paragraph_buffer.append(f"\\nolinebreak\\hspace{{0.35em}}\\mbox{{॥ {v_num_deva} ॥}}")
                full_paragraph = "".join(paragraph_buffer)
                formatted_paragraphs.append(f"{{\\noindent\\centering\\sloppy {full_paragraph}}}")
                formatted_paragraphs.append(r"\par\vspace{0.8em}")
                paragraph_buffer = []
                idx += v_count
                continue
            
            tok = tokens[idx]
            t = tok['type']
            
            if t == 'space':
                prev_is_danda = (idx > 0 and tokens[idx-1]['type'] == 'danda')
                if prev_is_danda:
                    paragraph_buffer.append(r"\hspace{0.35em}")
            elif t == 'danda':
                ch = tok['char']
                if ch == '।':
                    paragraph_buffer.append(r"\nolinebreak\hspace{0.12em}।\hspace{0.35em}")
                elif ch == '॥':
                    paragraph_buffer.append(r"\nolinebreak\hspace{0.15em}॥\hspace{0.35em}")
                else:
                    paragraph_buffer.append(f"\\nolinebreak\\hspace{{0.12em}}{ch}\\hspace{{0.35em}}")
            elif t == 'marker':
                if with_modifiers:
                    m_str = tok['marker'].strip('()')
                    if m_str in MOD_A_SET:
                        next_w_idx = idx + 1
                        while next_w_idx < len(tokens) and tokens[next_w_idx]['type'] == 'space':
                            next_w_idx += 1
                        if next_w_idx < len(tokens) and tokens[next_w_idx]['type'] == 'word' and paragraph_buffer:
                            prev_chunk = paragraph_buffer.pop()
                            next_tok = tokens[next_w_idx]
                            chunk2 = _format_single_deva_word_latex(next_tok, with_modifiers=True)
                            arc_glyph = r"\rlap{\swarafont \textcolor{ModifierSkyBlue}{\raisebox{1.18ex}{\hspace{-0.38em}\char" + '"E004}}}'
                            paragraph_buffer.append(f"\\mbox{{{prev_chunk}{arc_glyph}\\hspace{{0.08em}}{chunk2}}}")
                            idx = next_w_idx + 1
                            continue
                    elif m_str in MOD_D_SET:
                        next_w_idx = idx + 1
                        while next_w_idx < len(tokens) and tokens[next_w_idx]['type'] == 'space':
                            next_w_idx += 1
                        if next_w_idx < len(tokens) and tokens[next_w_idx]['type'] == 'word' and paragraph_buffer:
                            prev_chunk = paragraph_buffer.pop()
                            next_tok = tokens[next_w_idx]
                            chunk2 = _format_single_deva_word_latex(next_tok, with_modifiers=True)
                            d_glyph = r"\rlap{\swarafont \textcolor{ModifierSkyBlue}{\raisebox{1.18ex}{\hspace{-0.32em}\char" + '"E006}}}'
                            paragraph_buffer.append(f"\\mbox{{{prev_chunk}{d_glyph}\\hspace{{0.08em}}{chunk2}}}")
                            idx = next_w_idx + 1
                            continue
                    m_esc = _apply_deva_modifier_latex("", tok['marker'])
                    paragraph_buffer.append(m_esc)
            elif t == 'footnote':
                marker = tok.get('text', '').strip('()')
                fn_text = footnote_data.get(marker, '')
                if fn_text:
                    safe_key = subsection_key if subsection_key else "unknown"
                    label = f"fn:{safe_key}:{marker}"
                    if marker in seen_markers:
                        paragraph_buffer.append(f"\\rule{{0pt}}{{2.5ex}}\\textsuperscript{{\\raisebox{{1.2ex}}{{\\normalfont\\ref{{{label}}}}}}}")
                    else:
                        paragraph_buffer.append(f"\\rule{{0pt}}{{2.5ex}}\\footnote{{{fn_text}\\label{{{label}}}}}")
                        seen_markers.add(marker)
            elif t == 'word':
                sw = tok.get('swara', '')
                _, tok_mods = _parse_swara_and_modifiers(sw)
                has_mod_a1 = any(m.strip('()') in MOD_A1_SET for m in tok_mods)
                has_mod_a = any(m.strip('()') in MOD_A_SET for m in tok_mods)
                has_mod_d = any(m.strip('()') in MOD_D_SET for m in tok_mods)
                
                if has_mod_d and with_modifiers:
                    next_w_idx = idx + 1
                    while next_w_idx < len(tokens) and tokens[next_w_idx]['type'] == 'space':
                        next_w_idx += 1
                    
                    if next_w_idx < len(tokens) and tokens[next_w_idx]['type'] == 'word':
                        next_tok = tokens[next_w_idx]
                        next_sw = next_tok.get('swara', '')
                        _, next_mods = _parse_swara_and_modifiers(next_sw)
                        next_has_a1 = any(m.strip('()') in MOD_A1_SET for m in next_mods)
                        
                        if next_has_a1:
                            # Chained MOD-D + MOD-A1 over danda: e.g. बाहू(Ʌ)तो(A1) । हाइ
                            d_idx = next_w_idx + 1
                            while d_idx < len(tokens) and tokens[d_idx]['type'] == 'space':
                                d_idx += 1
                            if d_idx < len(tokens) and tokens[d_idx]['type'] == 'danda':
                                d_char = tokens[d_idx]['char']
                                third_w_idx = d_idx + 1
                                while third_w_idx < len(tokens) and tokens[third_w_idx]['type'] == 'space':
                                    third_w_idx += 1
                                if third_w_idx < len(tokens) and tokens[third_w_idx]['type'] == 'word':
                                    third_tok = tokens[third_w_idx]
                                    chunk1 = _format_single_deva_word_latex(tok, with_modifiers=True, exclude_mods=MOD_D_SET)
                                    chunk2 = _format_single_deva_word_latex(next_tok, with_modifiers=True, exclude_mods=MOD_A1_SET | MOD_D_SET)
                                    chunk3 = _format_single_deva_word_latex(third_tok, with_modifiers=True)
                                    d_glyph = r"\rlap{\swarafont \textcolor{ModifierSkyBlue}{\raisebox{1.18ex}{\hspace{-0.32em}\char" + '"E006}}}'
                                    arc_danda_glyph = r"\rlap{\swarafont \textcolor{ModifierSkyBlue}{\raisebox{1.18ex}{\hspace{-0.58em}\char" + '"E00D}}}'
                                    combined_mbox = f"\\mbox{{{chunk1}{d_glyph}\\hspace{{0.08em}}{chunk2}\\hspace{{0.12em}}{arc_danda_glyph}{d_char}\\hspace{{0.12em}}{chunk3}}}"
                                    paragraph_buffer.append(combined_mbox)
                                    idx = third_w_idx + 1
                                    continue
                        
                        chunk1 = _format_single_deva_word_latex(tok, with_modifiers=True, exclude_mods=MOD_D_SET)
                        chunk2 = _format_single_deva_word_latex(next_tok, with_modifiers=True)
                        d_glyph = r"\rlap{\swarafont \textcolor{ModifierSkyBlue}{\raisebox{1.18ex}{\hspace{-0.32em}\char" + '"E006}}}'
                        combined_mbox = f"\\mbox{{{chunk1}{d_glyph}\\hspace{{0.08em}}{chunk2}}}"
                        paragraph_buffer.append(combined_mbox)
                        idx = next_w_idx + 1
                        continue

                if has_mod_a1 and with_modifiers:
                    d_idx = idx + 1
                    while d_idx < len(tokens) and tokens[d_idx]['type'] == 'space':
                        d_idx += 1
                    if d_idx < len(tokens) and tokens[d_idx]['type'] == 'danda':
                        d_char = tokens[d_idx]['char']
                        next_w_idx = d_idx + 1
                        while next_w_idx < len(tokens) and tokens[next_w_idx]['type'] == 'space':
                            next_w_idx += 1
                        if next_w_idx < len(tokens) and tokens[next_w_idx]['type'] == 'word':
                            next_tok = tokens[next_w_idx]
                            chunk1 = _format_single_deva_word_latex(tok, with_modifiers=True, exclude_mods=MOD_A1_SET)
                            chunk2 = _format_single_deva_word_latex(next_tok, with_modifiers=True)
                            arc_danda_glyph = r"\rlap{\swarafont \textcolor{ModifierSkyBlue}{\raisebox{1.18ex}{\hspace{-0.58em}\char" + '"E00D}}}'
                            combined_mbox = f"\\mbox{{{chunk1}\\hspace{{0.12em}}{arc_danda_glyph}{d_char}\\hspace{{0.12em}}{chunk2}}}"
                            paragraph_buffer.append(combined_mbox)
                            idx = next_w_idx + 1
                            continue
                
                if has_mod_a and with_modifiers:
                    next_w_idx = idx + 1
                    while next_w_idx < len(tokens) and tokens[next_w_idx]['type'] == 'space':
                        next_w_idx += 1
                    
                    if next_w_idx < len(tokens) and tokens[next_w_idx]['type'] == 'word':
                        next_tok = tokens[next_w_idx]
                        chunk1 = _format_single_deva_word_latex(tok, with_modifiers=True, exclude_mods=MOD_A_SET)
                        chunk2 = _format_single_deva_word_latex(next_tok, with_modifiers=True)
                        arc_glyph = r"\rlap{\swarafont \textcolor{ModifierSkyBlue}{\raisebox{1.18ex}{\hspace{-0.38em}\char" + '"E004}}}'
                        combined_mbox = f"\\mbox{{{chunk1}{arc_glyph}\\hspace{{0.08em}}{chunk2}}}"
                        paragraph_buffer.append(combined_mbox)
                        idx = next_w_idx + 1
                        continue
                
                chunk = _format_single_deva_word_latex(tok, with_modifiers=with_modifiers)
                paragraph_buffer.append(chunk)
            idx += 1
            
        if paragraph_buffer:
            full_paragraph = "".join(paragraph_buffer)
            formatted_paragraphs.append(f"{{\\noindent\\centering\\sloppy {full_paragraph}}}")
            formatted_paragraphs.append(r"\par\vspace{0.8em}")
            
    return formatted_paragraphs


def format_mantra_sets(subsection, supersection_title, section_title, subsection_title, footnote_dict={}, prev_rik_id=None, subsection_key=None, toc_level='section'):
    
    formatted_output = []
    
    # --- FOOTNOTE TRACKING ---
    seen_markers = set()
    
    # --- DATA EXTRACTION ---
    current_rik_id = subsection.get('rik_id')
    current_rik_ids = subsection.get('rik_ids', [current_rik_id] if current_rik_id else [])
    string_1 = subsection.get('rik_metadata', '')
    string_2 = subsection.get('rik_text', '')
    string_3 = subsection.get('saman_metadata', '')
    
    # Determine if we should show rik_metadata and rik_text
    # Show if: first subsection, OR if any rik_id in current rik_ids differs from prev_rik_id
    # This ensures that when a subsection spans multiple Riks (e.g., [7, 8]) and Rik 7 was already
    # shown, we still display the combined text that includes Rik 8
    show_rik_info = (prev_rik_id is None) or (current_rik_id != prev_rik_id)
    # Also show if rik_ids contains multiple Riks and the last one differs from prev
    if not show_rik_info and len(current_rik_ids) > 1:
        # If we have multiple Riks in this subsection, check if the MAX Rik ID is new
        max_rik_id = max(current_rik_ids) if current_rik_ids else None
        if max_rik_id is not None and max_rik_id != prev_rik_id:
            show_rik_info = True
    
    # Clean titles for Display
    # Clean titles for Display
    display_sub_title = re.sub(r'^([|॥]+)\s*', r'\1 ', subsection_title)
    
    # --- SPLIT HEADER FOR INDEX/TOC ---
    # The user wants TOC and Index to ONLY have the Header (excluding Metadata)
    # Since the input title string contains "|| Header || || Metadata ||", we must split it.
    
    samam_header_only = display_sub_title
    
    # Regex to capture first block: || Text ||  (Non-greedy)
    # We look for [Dandas] [Content] [Dandas]
    m_split = re.match(r'([|॥]+\s*.*?[|॥]+)', display_sub_title)
    if m_split:
        samam_header_only = m_split.group(1).strip()
    
    # Index title: Strip dandas from the Clean Header
    index_title = re.sub(r'[|॥]', '', samam_header_only).strip()

    # --- LAYOUT CONSTRUCTION ---
    
    # 1. Page Break / Indexing Logic
    formatted_output.append(r"\par\filbreak")              
    formatted_output.append(r"\phantomsection")
    if subsection_title:
        # Use Clean Header for TOC and Index
        # Ensure TOC entry has proper danda formatting
        toc_title = format_dandas(samam_header_only)
        if toc_level == 'subsection':
            formatted_output.append(f"\\addcontentsline{{toc}}{{section}}{{{toc_title}}}")
        elif toc_level == 'both':
            formatted_output.append(f"\\addcontentsline{{toc}}{{subsection}}{{{toc_title}}}")
        formatted_output.append(f"\\index{{{index_title}}}")

    # 2. String 1: Rik Metadata (Plain Centered) - Only if rik_id changed
    # COLOR: BLUE
    if string_1 and show_rik_info:
        s1 = format_dandas(string_1)
        s1 = process_footnotes_latex(s1, subsection.get('footnotes', {}), seen_markers, subsection_key)
        formatted_output.append(f"{{\\centering \\textcolor{{AccentPurple}}{{{s1}}} \\par}}")
        formatted_output.append(r"\vspace{0.6em}")

    # 3. String 2: Rik Text (With Vedic Accents, Upright) - Only if rik_id changed
    # COLOR: BLUE
    if string_2 and show_rik_info:
        # Step A: Remove Spaces (Samhita Mode)
        s2 = remove_mantra_spaces(string_2)
        # Step A.1: Fix Visarga-Accent Order
        # s2 = fix_visarga_accent_order_local(s2)
        # Step B: Handle Consecutive Accent Kerning
        s2 = handle_consecutive_accents(s2)
        # Step C: Replace Accents with LaTeX commands (with adjusted sizes)
        s2 = replace_accents(s2)
        # Process Footnotes in Rik Text
        s2 = process_footnotes_latex(s2, subsection.get('footnotes', {}), seen_markers, subsection_key)
        # Step D: Format Dandas (Spaces around dandas only)
        # s2 = format_dandas(s2) -- moved after splitting
        
        # Split multi-Rik text so each Rik is on its own line
        s2 = split_rik_lines_latex(s2)
        s2 = format_dandas(s2)
        
        # SAFETY PATCH: Remove any lingering \newline commands that might have snuck in
        s2 = s2.replace(r'\newline', ' ').replace(r'\textbackslash{}newline', ' ')
        
        # Output: Upright (not italics)
        formatted_output.append(f"{{\\centering \\textcolor{{blue}}{{{s2}}} \\par}}")
        
        # --- NEW: Layout grouping for Rik + Samam ---
        has_samam_content = bool(display_sub_title.strip() or string_3.strip() or subsection.get('mantra_sets'))
        if has_samam_content:
            formatted_output.append(r"\nopagebreak")                
            formatted_output.append(r"\vspace{0.3em}") # Reduced space to keep together
            formatted_output.append(r"\nopagebreak")
        else:
            formatted_output.append(r"\vspace{0.8em}")

    # 4. Combined Header: || Subsection header || || samam_metadata ||
    header_part = display_sub_title.strip()
    header_part = format_dandas(header_part)
    header_part = f"\\textbf{{\\textcolor{{AccentGreen}}{{{header_part}}}}}"  
    
    # COLOR: Samam Metadata -> BROWN
    meta_part = format_dandas(string_3).strip()
    meta_part = process_footnotes_latex(meta_part, subsection.get('footnotes', {}), seen_markers, subsection_key)
    if meta_part:
        meta_part = f"\\textcolor{{AccentBrown}}{{{meta_part}}}"
    
    combined_header = ""
    if header_part and meta_part:
        combined_header = f"{header_part} \\quad {meta_part}"
    elif header_part:
        combined_header = header_part
    elif meta_part:
        combined_header = meta_part
    
    if combined_header:
        formatted_output.append(f"{{\\centering {combined_header} \\par}}")
        
    # Procedure links are shown at section/supersection header level in template
    # No sama-level procedure links (subsection scope shown at header)

    # Keep header with mantra text
    formatted_output.append(r"\nopagebreak")                
    formatted_output.append(r"\vspace{0.4em}")
    formatted_output.append(r"\nopagebreak")

    # --- MANTRA CONTENT RENDERING ---
    body_paras = _render_devanagari_mantra_body(subsection, subsection_key, seen_markers)
    formatted_output.extend(body_paras)

    return "\n\n".join(formatted_output)


# ----------------------------------------------------
# RIK-ONLY FORMATTING (for separate output mode)
# ----------------------------------------------------
def format_rik_only(subsection, supersection_title, section_title, subsection_title, footnote_dict={}, prev_rik_id=None, subsection_key=None, toc_level='section'):
    """
    Format only Rik content (rik_metadata and rik_text) for separate output mode.
    Skips all Samam-related content.
    """
    formatted_output = []
    
    # --- FOOTNOTE TRACKING ---
    seen_markers = set()
    
    current_rik_id = subsection.get('rik_id')
    string_1 = subsection.get('rik_metadata', '')
    string_2 = subsection.get('rik_text', '')
    
    # Skip if no Rik content
    if not string_1 and not string_2:
        return ""
    
    # Only show if rik_id changed (avoid duplicates)
    show_rik_info = (prev_rik_id is None) or (current_rik_id != prev_rik_id)
    if not show_rik_info:
        return ""
    
    # Page Break / Indexing
    formatted_output.append(r"\par\filbreak")
    formatted_output.append(r"\phantomsection")
    
    rik_id_display = f"ऋक् {to_devanagari_numeral(current_rik_id)}" if current_rik_id else ""
    if rik_id_display:
        if toc_level == 'subsection':
            formatted_output.append(f"\\addcontentsline{{toc}}{{section}}{{{rik_id_display}}}")
        elif toc_level == 'both':
            formatted_output.append(f"\\addcontentsline{{toc}}{{subsection}}{{{rik_id_display}}}")

    # Rik Metadata
    if string_1:
        s1 = format_dandas(string_1)
        # Apply footnotes
        s1 = process_footnotes_latex(s1, subsection.get('footnotes', {}), seen_markers, subsection_key)
        formatted_output.append(f"{{\\centering \\textcolor{{AccentPurple}}{{{s1}}} \\par}}")
        formatted_output.append(r"\vspace{0.6em}")

    # Rik Text (with Vedic Accents)
    if string_2:
        s2 = remove_mantra_spaces(string_2)
        # s2 = fix_visarga_accent_order_local(s2)
        s2 = handle_consecutive_accents(s2)
        s2 = replace_accents(s2)
        # Apply footnotes
        s2 = process_footnotes_latex(s2, subsection.get('footnotes', {}), seen_markers, subsection_key)
        s2 = format_dandas(s2)
        formatted_output.append(f"{{\\centering \\textcolor{{blue}}{{{s2}}} \\par}}")
        formatted_output.append(r"\vspace{0.8em}")

    return "\n\n".join(formatted_output)


# ----------------------------------------------------
# SAMAM-ONLY FORMATTING (for separate output mode)
# ----------------------------------------------------
def format_samam_only(subsection, supersection_title, section_title, subsection_title, footnote_dict={}, prev_rik_id=None, subsection_key=None, toc_level='section'):
    """
    Format only Samam content (header, saman_metadata, mantra text) for separate output mode.
    Skips all Rik-related content.
    """
    formatted_output = []
    
    # --- FOOTNOTE TRACKING ---
    seen_markers = set()
    
    string_3 = subsection.get('saman_metadata', '')
    
    # Clean titles
    display_sub_title = re.sub(r'^([|॥]+)\s*', r'\1 ', subsection_title) if subsection_title else ""
    index_title = re.sub(r'[|॥]', '', subsection_title).strip() if subsection_title else ""

    # Page Break / Indexing
    formatted_output.append(r"\par\filbreak")
    formatted_output.append(r"\phantomsection")
    if subsection_title:
        toc_title = display_sub_title.strip()
        if toc_level == 'subsection':
            formatted_output.append(f"\\addcontentsline{{toc}}{{section}}{{{toc_title}}}")
        elif toc_level == 'both':
            formatted_output.append(f"\\addcontentsline{{toc}}{{subsection}}{{{toc_title}}}")
        formatted_output.append(f"\\index{{{index_title}}}")

    # Combined Header: Subsection header + samam_metadata
    header_part = display_sub_title.strip()
    header_part = f"\\textbf{{\\textcolor{{AccentGreen}}{{{header_part}}}}}" if header_part else ""
    
    meta_part = format_dandas(string_3).strip()
    meta_part = process_footnotes_latex(meta_part, subsection.get('footnotes', {}), seen_markers, subsection_key)
    if meta_part:
        meta_part = f"\\textcolor{{AccentBrown}}{{{meta_part}}}"
    
    combined_header = ""
    if header_part and meta_part:
        combined_header = f"{header_part} \\quad {meta_part}"
    elif header_part:
        combined_header = header_part
    elif meta_part:
        combined_header = meta_part
        
    # Procedure links are shown at section/supersection header level in template
    # No sama-level procedure links (handled at header)
    
    if combined_header:
         formatted_output.append(f"{{\\centering {combined_header} \\par}}")

    formatted_output.append(r"\nopagebreak")
    formatted_output.append(r"\vspace{0.5em}")
    formatted_output.append(r"\nopagebreak")

    # Mantra Content Rendering (Samam text only - no Rik text)
    body_paras = _render_devanagari_mantra_body(subsection, subsection_key, seen_markers)
    formatted_output.extend(body_paras)

    return "\n\n".join(formatted_output)


# ----------------------------------------------------
# RIK NO-METADATA FORMATTING (for nometa output mode)
# ----------------------------------------------------
def format_rik_nometa(subsection, supersection_title, section_title, subsection_title, footnote_dict={}, prev_rik_id=None, subsection_key=None, toc_level='section'):
    """
    Format only Rik text (without rik_metadata) for nometa output mode.
    Skips all Samam-related content and metadata.
    """
    formatted_output = []
    
    # --- FOOTNOTE TRACKING ---
    seen_markers = set()
    
    current_rik_id = subsection.get('rik_id')
    string_2 = subsection.get('rik_text', '')
    
    # Skip if no Rik content
    if not string_2:
        return ""
    
    # Only show if rik_id changed (avoid duplicates)
    show_rik_info = (prev_rik_id is None) or (current_rik_id != prev_rik_id)
    if not show_rik_info:
        return ""
    
    # Page Break / Indexing
    formatted_output.append(r"\par\filbreak")
    formatted_output.append(r"\phantomsection")
    
    rik_id_display = f"ऋक् {to_devanagari_numeral(current_rik_id)}" if current_rik_id else ""
    if rik_id_display:
        if toc_level == 'subsection':
            formatted_output.append(f"\\addcontentsline{{toc}}{{section}}{{{rik_id_display}}}")
        elif toc_level == 'both':
            formatted_output.append(f"\\addcontentsline{{toc}}{{subsection}}{{{rik_id_display}}}")

    # Rik Text (with Vedic Accents) - NO METADATA
    if string_2:
        s2 = remove_mantra_spaces(string_2)
        s2 = handle_consecutive_accents(s2)
        s2 = replace_accents(s2)
        # Apply footnotes
        s2 = process_footnotes_latex(s2, subsection.get('footnotes', {}), seen_markers, subsection_key)
        # Split multi-Rik text so each Rik is on its own line
        s2 = split_rik_lines_latex(s2)
        s2 = format_dandas(s2)
        formatted_output.append(f"{{\\centering \\textcolor{{blue}}{{{s2}}} \\par}}")
        formatted_output.append(r"\vspace{0.8em}")

    return "\n\n".join(formatted_output)


# ----------------------------------------------------
# SAMAM NO-METADATA FORMATTING (for nometa output mode)
# ----------------------------------------------------
def format_samam_nometa(subsection, supersection_title, section_title, subsection_title, footnote_dict={}, prev_rik_id=None, subsection_key=None, toc_level='section'):
    """
    Format only Samam content (header, mantra text) for nometa output mode.
    Skips all Rik-related content and saman_metadata.
    """
    formatted_output = []
    
    # --- FOOTNOTE TRACKING ---
    seen_markers = set()
    
    # Clean titles - skip saman_metadata
    display_sub_title = re.sub(r'^([|॥]+)\s*', r'\1 ', subsection_title) if subsection_title else ""
    index_title = re.sub(r'[|॥]', '', subsection_title).strip() if subsection_title else ""

    # Page Break / Indexing
    formatted_output.append(r"\par\filbreak")
    formatted_output.append(r"\phantomsection")
    if subsection_title:
        toc_title = display_sub_title.strip()
        if toc_level == 'subsection':
            formatted_output.append(f"\\addcontentsline{{toc}}{{section}}{{{toc_title}}}")
        elif toc_level == 'both':
            formatted_output.append(f"\\addcontentsline{{toc}}{{subsection}}{{{toc_title}}}")
        formatted_output.append(f"\\index{{{index_title}}}")

    # Header only (NO saman_metadata)
    header_part = display_sub_title.strip()
    if header_part:
        header_part = f"\\textcolor{{AccentGreen}}{{{header_part}}}"
        formatted_output.append(f"{{\\centering \\textbf{{{header_part}}} \\par}}")

    formatted_output.append(r"\nopagebreak")
    formatted_output.append(r"\vspace{0.5em}")
    formatted_output.append(r"\nopagebreak")

    # Mantra Content Rendering (Samam text only - no metadata)
    body_paras = _render_devanagari_mantra_body(subsection, subsection_key, seen_markers)
    formatted_output.extend(body_paras)

    return "\n\n".join(formatted_output)


def format_mantra_sets_text(subsection,section_title,subsection_title):
    
    formatted_sets = []
    
    mantra_sets = subsection.get('mantra_sets', [])
    mantra_array = []
    for mantra_set in mantra_sets:
        mantra_words = mantra_set.get('mantra-words', [])
        mantra=""
        for w,word in enumerate(mantra_words):
            actual_word = word.get('word', 'WORD')
            
            mantra+=" " +actual_word
        mantra_array.append(mantra)
    
        
    corrected_mantra_sets = subsection.get('corrected-mantra_sets', [])
    corrected_mantra_array = []
    if corrected_mantra_sets is not None:
        for corrected in corrected_mantra_sets:
            corrected_mantra = corrected.get('corrected-mantra', '')
            if corrected_mantra:
                corrected_mantra_array.append(corrected_mantra)
                
    if len(corrected_mantra_array) != 0:
        mantra_array = corrected_mantra_array
    footnotes = subsection.get('footnotes', {})
    # Note: #Start/#End of Mantra Sets markers are added by the Jinja2 template
    # Do not add them here to avoid duplication
    for mantra in mantra_array:
        # Keep mantra content together - replace \newline% with single space or nothing
        clean_mantra = mantra.replace('\\newline%', '').replace('\\newline', '')
        # Apply footnote application
        clean_mantra, _ = process_footnotes_text(clean_mantra, footnotes)
        formatted_sets.append(clean_mantra)
    return "\n".join(formatted_sets)


# ----------------------------------------------------
# MALAYALAM SAMAM-ONLY FORMATTING (Phase 1 pilot)
# ----------------------------------------------------
_ENGLISH_DIGITS = str.maketrans("०१२३४५६७८९൦൧൨൩൪൫൬൭൮൯", "01234567890123456789")

MODIFIER_DIRECT_MAP = {
    # Modifiers from updated Google Sheet (A..H)
    "A": "\uE004",  # Syllable Arc (Tie) ╭╮ / ⁀
    "B": "\uE005",  # Caret / Peak /\ / ^
    "C": "\uE001",  # High/Mid-Dot ॱ / ·
    "D": "\uE006",  # Chevron Roof Ʌ
    "E": "\uE002",  # Heavy Vertical ┃
    "F": "\uE002",  # Light Vertical ╷
    "G": "\uE003",  # Descending Tone \ / ⟍
    "H": "\uE002",  # Swarita ॑ / |

    # Lowercase variants
    "a": "\uE004", "b": "\uE005", "c": "\uE001", "d": "\uE006",
    "e": "\uE002", "f": "\uE002", "g": "\uE003", "h": "\uE002",

    # Direct Symbols matching "How to enter" column
    "^": "\uE005", "˄": "\uE005",
    "Ʌ": "\uE006", "/\\": "\uE006", "∧": "\uE006",
    "⁀": "\uE004", "͡": "\uE004", "╭╮": "\uE004",
    "ͦ": "\uE009", "˚": "\uE009",
    "ॱ": "\uE001", "·": "\uE001",
    "_": "\uE007",
    "|": "\uE002", "│": "\uE002", "।": "।",
    "┃": "\uE002", "╷": "\uE002", "⃓": "\uE002",
    "\\": "\uE003", "╲": "\uE003", "⟍": "\uE003",
    "/": "\uE008",
    ",": "\uE00A", "ˏ": "\uE00A", "̦": "\uE00A",
    "||": "\uE00B", "॥": "\uE00B",
    "॑": "\uE002", "ˈ": "\uE002",
    "L": "\uE002", "l": "\uE002",
}


MODIFIER_KEYS = {
    "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L",
    "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l",
    "A1", "a1", "A_1", "a_1",
    "B1", "b1", "D1", "d1", "D2", "d2",
    "^", "˄", "Ʌ", "/\\", "∧", "⁀", "͡", "╭╮", "ͦ", "˚", "ॱ", "·",
    "|", "│", "।", "┃", "╷", "⃓", "\\", "╲", "⟍", "॑", "ˈ",
    "\uE001", "\uE002", "\uE003", "\uE004", "\uE005", "\uE006", "\uE008", "\uE00A", "\uE00B", "\uE00C", "\uE00D",
    "\uE00E", "\uE00F", "\uE02A", "\uE02B", "\uE02C", "\uE02D"
}


def _apply_mantrakshara_modifier(syl_esc: str, mod: str) -> str:
    """Attach a swara modifier to a Mantrakshara in ModifierSkyBlue."""
    if not mod:
        return syl_esc
    m_clean = mod.strip("()")
    if m_clean in ("A", "a", "╭╮", "⁀", "\uE004"):
        return f"{syl_esc}\\rlap{{\\swarafont \\textcolor{{ModifierSkyBlue}}{{\\raisebox{{1.15ex}}{{\\hspace{{-0.40em}}\uE004}}}}}}"
    elif m_clean in ("A1", "a1", "A_1", "a_1", "\uE00D"):
        return f"{syl_esc}\\rlap{{\\swarafont \\textcolor{{ModifierSkyBlue}}{{\\raisebox{{1.15ex}}{{\\hspace{{-0.55em}}\uE00D}}}}}}"
    elif m_clean in ("B", "b", "^", "˄", "/\\", "∧", "\uE005"):
        return f"{syl_esc}\\rlap{{\\swarafont \\textcolor{{ModifierSkyBlue}}{{\\raisebox{{1.15ex}}{{\\hspace{{-0.40em}}\uE005}}}}}}"
    elif m_clean in ("B1", "b1", "\uE02C"):
        return f"{syl_esc}\\rlap{{\\swarafont \\textcolor{{ModifierSkyBlue}}{{\\raisebox{{1.15ex}}{{\\hspace{{-0.35em}}\uE02C}}}}}}"
    elif m_clean in ("C", "c", "ॱ", "·", "\uE001"):
        return f"{syl_esc}{{\\swarafont \\textcolor{{ModifierSkyBlue}}{{\\raisebox{{0.25ex}}{{\\hspace{{0.10em}}\uE001\\hspace{{0.05em}}}}}}}}"
    elif m_clean in ("D", "d", "Ʌ", "\uE006"):
        return f"{syl_esc}\\rlap{{\\swarafont \\textcolor{{ModifierSkyBlue}}{{\\raisebox{{1.15ex}}{{\\hspace{{-0.65em}}\uE006}}}}}}"
    elif m_clean in ("D1", "d1", "\uE00E"):
        return f"{syl_esc}\\rlap{{\\swarafont \\textcolor{{ModifierSkyBlue}}{{\\raisebox{{1.15ex}}{{\\hspace{{-0.40em}}\uE00E}}}}}}"
    elif m_clean in ("D2", "d2", "\uE00F"):
        return f"{syl_esc}{{\\swarafont \\textcolor{{ModifierSkyBlue}}{{\\raisebox{{0.50ex}}{{\\hspace{{0.10em}}\uE00F\\hspace{{0.05em}}}}}}}}"
    elif m_clean in ("E", "e", "┃", "\uE002"):
        return f"{syl_esc}{{\\swarafont \\textcolor{{ModifierSkyBlue}}{{\\raisebox{{0.05ex}}{{\\hspace{{0.05em}}\uE002}}}}}}"
    elif m_clean in ("F", "f", "╷", "\uE008"):
        return f"{syl_esc}{{\\swarafont \\textcolor{{ModifierSkyBlue}}{{\\raisebox{{0.05ex}}{{\\hspace{{0.05em}}\uE008}}}}}}"
    elif m_clean in ("G", "g", "\\", "╲", "⟍", "\uE003"):
        return f"{syl_esc}\\rlap{{\\swarafont \\textcolor{{ModifierSkyBlue}}{{\\raisebox{{-0.35ex}}{{\\hspace{{-0.65em}}\uE003}}}}}}"
    elif m_clean in ("H", "h", "L", "l", "|", "│", "॑", "ˈ", "\uE00C"):
        return f"{syl_esc}\\rlap{{\\swarafont \\textcolor{{ModifierSkyBlue}}{{\\raisebox{{1.10ex}}{{\\hspace{{-0.55em}}\uE00C}}}}}}"
    elif m_clean in ("I", "i", "\uE02A"):
        return f"{syl_esc}{{\\swarafont \\textcolor{{ModifierSkyBlue}}{{\\raisebox{{0.50ex}}{{\\hspace{{0.10em}}\uE02A\\hspace{{0.05em}}}}}}}}"
    elif m_clean in ("J", "j", "\uE02B"):
        return f"{syl_esc}{{\\swarafont \\textcolor{{ModifierSkyBlue}}{{\\raisebox{{0.80ex}}{{\\hspace{{0.10em}}\uE02B\\hspace{{0.05em}}}}}}}}"
    elif m_clean in ("K", "k", "\uE02D"):
        return f"{syl_esc}{{\\swarafont \\textcolor{{ModifierSkyBlue}}{{\\raisebox{{0.50ex}}{{\\hspace{{0.10em}}\uE02D\\hspace{{0.05em}}}}}}}}"
    return syl_esc


def _has_mod_a1(tok) -> bool:
    """Check if a token carries MOD-A1 (arc over danda)."""
    if not tok:
        return False
    if tok.get('type') == 'marker':
        return tok.get('marker', '').strip("()") in ("A1", "a1", "A_1", "a_1", "\uE00D")
    if tok.get('type') == 'word':
        sw = tok.get('swara', '')
        if sw:
            _, mods = _parse_swara_and_modifiers(sw)
            return any(m.strip("()") in ("A1", "a1", "A_1", "a_1", "\uE00D") for m in mods)
    return False


def _has_multiple_swaras(tok) -> bool:
    """Check if a word token has multiple or compound swara glyphs."""
    if not tok or tok.get('type') != 'word':
        return False
    sw = tok.get('swara', '')
    if not sw:
        return False
    sw_parts, _ = _parse_swara_and_modifiers(sw)
    if len(sw_parts) > 1:
        return True
    if sw_parts:
        sw_text = sw_parts[0].strip("()")
        if "\u1134D" in sw_text or "\u0D4D" in sw_text or len(sw_text) >= 3:
            return True
    return False


def _match_verse_num_marker(tokens: list, idx: int) -> tuple[int, str | None]:
    """Check if tokens starting at idx form a composite verse number marker like || N || or ॥ N ॥.
    Returns (token_count, number_string) if matched, else (0, None).
    """
    if idx >= len(tokens):
        return 0, None
    sub = tokens[idx:]
    if sub[0].get('type') != 'danda' or sub[0].get('char') not in ('॥', '||', '|', '।।'):
        return 0, None

    j = 1
    while j < len(sub) and sub[j].get('type') == 'space':
        j += 1
    
    if j < len(sub) and sub[j].get('type') in ('word', 'other'):
        val = (sub[j].get('word') or sub[j].get('text') or '').translate(_ENGLISH_DIGITS).strip()
        if re.match(r'^\d+$', val):
            num_str = val
            j += 1
            while j < len(sub) and sub[j].get('type') == 'space':
                j += 1
            if j < len(sub) and sub[j].get('type') == 'danda' and sub[j].get('char') in ('॥', '||', '|', '।।'):
                j += 1
                while j < len(sub) and sub[j].get('type') == 'space':
                    j += 1
                return j, num_str
    return 0, None


def _parse_swara_and_modifiers(swara_str: str):
    """Decompose swara string into pitch swara markers and Mantrakshara modifiers."""
    if not swara_str:
        return [], []
    if "(" in swara_str:
        parens = re.findall(r"\(([^)]+)\)", swara_str)
    else:
        parens = [swara_str]
    
    swaras = []
    mods = []
    for p in parens:
        if p in MODIFIER_KEYS:
            mods.append(p)
        else:
            # Check if p has trailing modifier char (e.g. \uE001, \uE003, \uE004, etc.)
            m = re.search(r"([\uE001-\uE00C\^\\/\|\_]+)$", p)
            if m:
                base = p[:m.start()]
                trailing_mods = p[m.start():]
                if base:
                    swaras.append(base)
                for tm in trailing_mods:
                    mods.append(tm)
            else:
                swaras.append(p)
    return swaras, mods


SWARA_CANONICAL_MAP = {
    # Sha base and combinations
    "𑌶": "\u0D36",                 # Grantha Sha -> Malayalam Sha
    "\u11336": "\u0D36",
    "𑌶𑌾": "\uE010",               # Shaa
    "\u11336\u1133E": "\uE010",
    "ശാ": "\uE010",
    "𑌶𑌿": "\uE011",               # Shi
    "\u11336\u1133F": "\uE011",
    "ശി": "\uE011",
    "𑌶𑍀": "\uE012",               # Shii
    "\u11336\u11340": "\uE012",
    "ശീ": "\uE012",
    "𑌶𑍍": "\uE013",               # Sha + Virama
    "\u11336\u1134D": "\uE013",
    "ശ്": "\uE013",
    "𑌶𑍁": "\uE015",               # Shu
    "\u11336\u11341": "\uE015",
    "ശു": "\uE015",
    "𑌶𑍂": "\uE016",               # Shuu
    "\u11336\u11342": "\uE016",
    "ശൂ": "\uE016",
    "𑌶𑍃": "\uE017",               # Shr
    "\u11336\u11343": "\uE017",
    "𑌶𑍄": "\uE018",               # Shrr
    "\u11336\u11344": "\uE018",
    "𑌶𑍇": "\uE019",               # She
    "\u11336\u11347": "\uE019",
    "𑌶𑍈": "\uE01A",               # Shai
    "\u11336\u11348": "\uE01A",
    "𑌶𑍋": "\uE01B",               # Sho
    "\u11336\u1134B": "\uE01B",
    "𑌶𑍌": "\uE01C",               # Shau
    "\u11336\u1134C": "\uE01C",

    # Tra & Kra
    "𑌤𑍍𑌰": "\uE01D",               # Tra
    "\u11324\u1134D\u11330": "\uE01D",
    "𑌤𑍍𑌰𑌾": "\uE01D",
    "ത്രാ": "\uE01D",
    "ത്ര": "\uE01D",
    "𑌕𑍍𑌰": "\uE01E",               # Kra
    "\u11315\u1134D\u11330": "\uE01E",
    "ക്രം": "\uE01E",
    "ക്ര": "\uE01E",
    "𑌕𑍍𑌰𑍍": "\uE01F",              # Kra + Virama
    "\u11315\u1134D\u11330\u1134D": "\uE01F",
    "ക്ര്": "\uE01F",

    # Pla family
    "𑌪𑍍𑌲": "\uE020",               # Pla
    "\u1132A\u1134D\u11332": "\uE020",
    "പ്ല": "\uE020",
    "𑌪𑍍𑌲𑌾": "\uE021",              # Plaa
    "\u1132A\u1134D\u11332\u1133E": "\uE021",
    "പ്ലാ": "\uE021",
    "𑌪𑍍𑌲𑌿": "\uE022",              # Pli
    "\u1132A\u1134D\u11332\u1133F": "\uE022",
    "പ്ലി": "\uE022",
    "𑌪𑍍𑌲𑍀": "\uE023",              # Plii
    "\u1132A\u1134D\u11332\u11340": "\uE023",
    "പ്ലീ": "\uE023",
    "𑌪𑍍𑌲𑍁": "\uE024",              # Plu
    "\u1132A\u1134D\u11332\u11341": "\uE024",
    "പ്ലു": "\uE024",
    "𑌪𑍍𑌲𑍂": "\uE025",              # Pluu
    "\u1132A\u1134D\u11332\u11342": "\uE025",
    "പ്ലൂ": "\uE025",
    "𑌪𑍍𑌲𑍍": "\uE026",              # Pla + Virama
    "\u1132A\u1134D\u11332\u1134D": "\uE026",
    "പ്ല്": "\uE026",

    # Clean composites
    "ശൃ": "\uE027",
    "𑌷𑍃": "\uE028",               # Shrr
    "\u11337\u11343": "\uE028",
    "ഷൃ": "\uE028",
    "𑌣𑍂": "\uE029",               # Nna + U
    "\u11323\u11342": "\uE029",
    "ണൂ": "\uE029",
}


def _swara_latex(swara: str) -> str:
    """Latex for pure swara marker pitch glyphs rendered in bold SwaraRed."""
    if not swara:
        return ""
    # Filter out modifiers which attach directly to Mantrakshara
    if swara in MODIFIER_KEYS or swara in ("A", "B", "C", "D", "E", "F", "G", "H", "L", "a", "b", "c", "d", "e", "f", "g", "h", "l"):
        return ""
    # Resolve to canonical PUA/Malayalam ligature if mapped
    clean_swara = SWARA_CANONICAL_MAP.get(swara, swara)
    return f"{{\\swarafont \\bfseries \\textcolor{{SwaraRed}}{{{clean_swara}}}}}"


def wrap_latin_for_latex(text: str) -> str:
    r"""Wrap any Latin/English character sequences with {\latinfont ...} so they render in Nimbus Roman."""
    if not text:
        return text
    if r'\latinfont' in text:
        return text
    return re.sub(r'([A-Za-z0-9][A-Za-z0-9\s,\.\-\':;/\(\)]*)', r'{\\latinfont \1}', text)


def _render_malayalam_mantra_body(subsection):
    """Helper to render Malayalam mantra body with top swara stacks and footnotes."""
    from malayalam.ml_text import tokenize_mantra_line
    from malayalam.ml_transliterate import split_malayalam_syllables, devanagari_to_malayalam
    
    mantra_sets = subsection.get('malayalam-mantra-sets', [])
    if not mantra_sets:
        mantra_sets = subsection.get('corrected-mantra_sets', [])
    if not mantra_sets:
        mantra_sets = subsection.get('mantra_sets', [])
    if not mantra_sets:
        return []

    footnote_data = subsection.get('footnotes', {})
    paragraph_buffer = []
    formatted_paragraphs = []
    
    has_mod_b_pending = False
    has_mod_a1_pending = False
    for mantra_set in mantra_sets:
        line = mantra_set.get('malayalam-mantra') or mantra_set.get('corrected-mantra') or mantra_set.get('mantra', '')
        if not line:
            continue
        line = line.replace('ർ', '൪').replace('ര്', '൪')
        tokens = tokenize_mantra_line(line)
        
        idx_t = 0
        while idx_t < len(tokens):
            v_count, v_num = _match_verse_num_marker(tokens, idx_t)
            if v_count > 0:
                paragraph_buffer.append(f"\\nolinebreak\\hspace{{0.65em plus 0.25em minus 0.1em}}\\mbox{{\\malayalamfont ॥{v_num}॥}}")
                full_paragraph = "".join(paragraph_buffer)
                formatted_paragraphs.append(f"{{\\noindent\\justifying\\sloppy {{\\malayalamfont {full_paragraph}}}}}")
                formatted_paragraphs.append(r"\par\vspace{1.1em}")
                paragraph_buffer = []
                idx_t += v_count
                continue

            tok = tokens[idx_t]
            t = tok['type']
            if t == 'space':
                prev_tok = tokens[idx_t - 1] if idx_t > 0 else None
                next_tok = tokens[idx_t + 1] if idx_t + 1 < len(tokens) else None
                
                # Space is suppressed around MOD-A1 and its bridging danda
                if has_mod_a1_pending or _has_mod_a1(prev_tok) or _has_mod_a1(next_tok):
                    idx_t += 1
                    continue
                if prev_tok and prev_tok.get('type') == 'danda' and idx_t > 1 and _has_mod_a1(tokens[idx_t - 2]):
                    idx_t += 1
                    continue
                
                # Space is preserved around normal dandas / footnotes or when adjacent to multi-swaras
                prev_is_danda = (prev_tok and prev_tok['type'] in ('danda', 'footnote'))
                next_is_danda = (next_tok and next_tok['type'] in ('danda', 'footnote'))
                
                prev_multi = (prev_tok and _has_multiple_swaras(prev_tok))
                next_multi = (next_tok and _has_multiple_swaras(next_tok))
                
                if prev_is_danda or next_is_danda or prev_multi or next_multi:
                    paragraph_buffer.append(" ")
                else:
                    paragraph_buffer.append(r"\hskip 0pt plus 1.5pt\allowbreak ")
            elif t == 'danda':
                has_mod_b_pending = False
                if has_mod_a1_pending:
                    has_mod_a1_pending = False
                    d_char = tok['char'].replace('|', '।')
                    paragraph_buffer.append(f"{{\\malayalamfont {d_char}}}")
                else:
                    paragraph_buffer.append(format_dandas(tok['char']))
            elif t == 'footnote':
                marker = tok.get('text', '').strip('()')
                fn_text = footnote_data.get(marker, '')
                if fn_text:
                    try:
                        fn_text = devanagari_to_malayalam(fn_text)
                    except Exception:
                        pass
                    fn_esc = escape_for_latex(fn_text)
                    fn_esc = wrap_latin_for_latex(fn_esc)
                    paragraph_buffer.append(f"\\footnote{{\\malayalamfont {fn_esc}}}")
            elif t == 'marker':
                m_str = tok['marker']
                if m_str.strip("()") in ("B", "b", "^", "˄", "/\\", "∧", "\uE005"):
                    has_mod_b_pending = True
                if m_str.strip("()") in ("A1", "a1", "A_1", "a_1", "\uE00D"):
                    has_mod_a1_pending = True
                m_esc = _apply_mantrakshara_modifier("", m_str)
                paragraph_buffer.append(m_esc)
            elif t == 'word':
                if _has_mod_a1(tok):
                    has_mod_a1_pending = True
                word = tok['word']
                swara = tok['swara']
                if not word:
                    idx_t += 1
                    continue

                # Strip trailing punctuation (like _, ., ,) so swara marker stays on the preceding mantrakshara
                core_word = word.rstrip("_,.")
                trailing_punct = word[len(core_word):]

                if not core_word:
                    punct_esc = escape_for_latex(word)
                    paragraph_buffer.append(f"{{\\malayalamfont \\textcolor{{ModifierSkyBlue}}{{{punct_esc}}}}}")
                    idx_t += 1
                    continue

                if swara:
                    swara_parts, mod_parts = _parse_swara_and_modifiers(swara)
                    
                    syllables = split_malayalam_syllables(core_word)
                    parts = []
                    for idx, syl in enumerate(syllables):
                        syl_esc = escape_for_latex(syl)
                        if syl in ("_", ".", ",", ";", "._", "_.", ",_"):
                            parts.append(f"{{\\malayalamfont \\textcolor{{ModifierSkyBlue}}{{{syl_esc}}}}}")
                        elif idx == len(syllables) - 1:
                            # Attach all modifiers to the final mantrakshara syllable
                            for mod in mod_parts:
                                if mod.strip("()") in ("B", "b", "^", "˄", "/\\", "∧", "\uE005"):
                                    has_mod_b_pending = True
                                syl_esc = _apply_mantrakshara_modifier(syl_esc, mod)
                            
                            swara_str = "".join(swara_parts)
                            swara_latex = _swara_latex(swara_str)
                            if swara_latex:
                                if has_mod_b_pending:
                                    swara_latex = f"\\hspace{{-0.85em}}\\raisebox{{0.40ex}}{{{swara_latex}}}"
                                    has_mod_b_pending = False
                                stack_code = f"\\stackcenter{{\\malayalamfont {syl_esc}}}{{{swara_latex}}}"
                                parts.append(stack_code)
                            else:
                                parts.append(f"{{\\malayalamfont {syl_esc}}}")
                        else:
                            parts.append(f"{{\\malayalamfont {syl_esc}}}")
                    if trailing_punct:
                        tp_esc = escape_for_latex(trailing_punct)
                        parts.append(f"{{\\malayalamfont \\textcolor{{ModifierSkyBlue}}{{{tp_esc}}}}}")
                    paragraph_buffer.append("".join(parts))
                else:
                    syl_parts = []
                    syllables = split_malayalam_syllables(core_word)
                    for syl in syllables:
                        syl_esc = escape_for_latex(syl)
                        if syl in ("_", ".", ",", ";", "._", "_.", ",_"):
                            syl_parts.append(f"{{\\malayalamfont \\textcolor{{ModifierSkyBlue}}{{{syl_esc}}}}}")
                        else:
                            syl_parts.append(f"{{\\malayalamfont {syl_esc}}}")
                    if trailing_punct:
                        tp_esc = escape_for_latex(trailing_punct)
                        syl_parts.append(f"{{\\malayalamfont \\textcolor{{ModifierSkyBlue}}{{{tp_esc}}}}}")
                    paragraph_buffer.append("".join(syl_parts))
            else:
                extra_text = tok.get("text", "")
                extra_esc = escape_for_latex(extra_text)
                if extra_text.strip() in (".", ",", "_", "._", "_.", ",_", ",.", ";"):
                    paragraph_buffer.append(f"{{\\malayalamfont \\textcolor{{ModifierSkyBlue}}{{{extra_esc}}}}}")
                else:
                    paragraph_buffer.append(f"{{\\malayalamfont {extra_esc}}}")
            idx_t += 1

        if paragraph_buffer:
            full_paragraph = "".join(paragraph_buffer)
            formatted_paragraphs.append(f"{{\\noindent\\justifying\\sloppy {{\\malayalamfont {full_paragraph}}}}}")
            formatted_paragraphs.append(r"\par\vspace{1.1em}")
            paragraph_buffer = []

    if paragraph_buffer:
        full_paragraph = "".join(paragraph_buffer)
        formatted_paragraphs.append(f"{{\\noindent\\justifying\\sloppy {{\\malayalamfont {full_paragraph}}}}}")
        formatted_paragraphs.append(r"\par\vspace{1.1em}")

    return formatted_paragraphs


def format_malayalam_rik_block(subsection, prev_rik_id=None, include_metadata=True):
    """Format Rik metadata + Rik text (with elevated Vedic accents and footnotes) for LaTeX PDF."""
    from malayalam.ml_transliterate import devanagari_to_malayalam, split_malayalam_syllables

    current_rik_id = subsection.get('rik_id')
    rik_ids = subsection.get('rik_ids', [current_rik_id] if current_rik_id else [])
    rik_metadata = subsection.get('rik_metadata', '')
    rik_text = subsection.get('rik_text', '')
    
    show_rik = (prev_rik_id is None) or (current_rik_id != prev_rik_id) or (len(rik_ids) > 1 and max(rik_ids) != prev_rik_id)
    if not show_rik or (not rik_metadata and not rik_text):
        return ""
    
    footnote_data = subsection.get('footnotes', {})
    out = []
    if include_metadata and rik_metadata:
        try:
            rm = devanagari_to_malayalam(rik_metadata)
        except Exception:
            rm = rik_metadata
        rm = format_dandas(rm)
        rm_esc = escape_for_latex(rm)
        out.append(f"{{\\centering {{\\malayalamfont \\textcolor{{AccentPurple}}{{{rm_esc}}}}} \\par}}")
        out.append(r"\nopagebreak\vspace{0.2em}\nopagebreak")
    
    if rik_text:
        try:
            rt = devanagari_to_malayalam(rik_text)
        except Exception:
            rt = rik_text
        rt = clean_stack_arg(rt)
        
        # Replace footnote markers (s1), etc. with LaTeX footnotes
        def _replace_fn(match):
            m = match.group(1)
            fn = footnote_data.get(m, '')
            if fn:
                try:
                    fn = devanagari_to_malayalam(fn)
                except Exception:
                    pass
                fn_esc = escape_for_latex(fn)
                fn_esc = wrap_latin_for_latex(fn_esc)
                return f"\\footnote{{\\malayalamfont {fn_esc}}}"
            return ""
        
        rt = re.sub(r'\(s(\d+)\)', r'(s\1)', rt)
        rt = re.sub(r'\((s\d+)\)', _replace_fn, rt)
        
        # Format Vedic accents over Malayalam syllables using stackengine
        tokens = re.findall(r'\\footnote\{[^}]*\}|॥\s*[\d०-९]+\s*॥|[।॥]|\s+|[^\s।॥()]+(?:\(\d+\))*', rt)
        tok_out = []
        for tok in tokens:
            if tok.isspace():
                continue
            elif tok in ['।', '॥']:
                tok_out.append(f'\\hspace{{0.25em}}{tok}\\hspace{{0.25em}}')
            elif re.match(r'॥\s*[\d०-९]+\s*॥', tok):
                tok_out.append(f'\\hspace{{0.35em}}\\mbox{{{tok.translate(_ENGLISH_DIGITS)}}}')
            elif tok.startswith(r'\footnote'):
                tok_out.append(tok)
            else:
                segs = re.findall(r'[^\s()]+?(?:\(\d+\)|$)', tok)
                seg_out = []
                for seg in segs:
                    m_acc = re.match(r'^(.*?)\((\d+)\)$', seg)
                    if m_acc:
                        base_word, acc_num = m_acc.group(1), m_acc.group(2)
                        sylls = split_malayalam_syllables(base_word)
                        if len(sylls) > 1:
                            prefix = escape_for_latex(''.join(sylls[:-1]))
                            last_syl = escape_for_latex(sylls[-1])
                        else:
                            prefix = ''
                            last_syl = escape_for_latex(base_word)
                        if acc_num == '1':
                            seg_out.append(f'{prefix}\\rikSwarita{{{last_syl}}}')
                        elif acc_num == '2':
                            seg_out.append(f'{prefix}\\rikAnudatta{{{last_syl}}}')
                        elif acc_num == '3':
                            seg_out.append(f'{prefix}\\rikKampa{{{last_syl}}}')
                        elif acc_num == '4':
                            seg_out.append(f'{prefix}\\rikTrikampa{{{last_syl}}}')
                        else:
                            seg_out.append(escape_for_latex(seg))
                    else:
                        seg_out.append(escape_for_latex(seg))
                tok_out.append(''.join(seg_out))
        
        rt_formatted = "".join(tok_out)
        out.append(f"{{\\noindent\\justifying\\sloppy {{\\malayalamfont \\textcolor{{AccentBlue}}{{{rt_formatted}}}}}}}")
        out.append(r"\par\vspace{0.5em}")
        
    return "\n".join(out)


def format_malayalam_samam_block(subsection, subsection_title, toc_level='section', include_metadata=True):
    """Format Samam subsection header + Saman metadata + Samam mantras in Malayalam for LaTeX PDF."""
    from malayalam.ml_transliterate import devanagari_to_malayalam

    formatted_output = []

    # Clean titles for Display
    display_sub_title = re.sub(r'^([|॥]+)\s*', r'\1 ', subsection_title) if subsection_title else ''

    # Header only (exclude metadata) for TOC/Index
    samam_header_only = display_sub_title
    m_split = re.match(r'([|॥]+\s*.*?[|॥]+)', display_sub_title)
    if m_split:
        samam_header_only = m_split.group(1).strip()
    index_title = re.sub(r'[|॥]', '', samam_header_only).strip()

    try:
        display_sub_title = devanagari_to_malayalam(display_sub_title)
        samam_header_only = devanagari_to_malayalam(samam_header_only)
        index_title = devanagari_to_malayalam(index_title)
    except Exception:
        pass

    formatted_output.append(r"\par\filbreak")
    formatted_output.append(r"\phantomsection")
    if subsection_title:
        toc_title = format_dandas(samam_header_only)
        mal_toc = "{\\malayalamfont " + toc_title + "}"
        if toc_level == 'subsection':
            formatted_output.append(f"\\addcontentsline{{toc}}{{section}}{{{mal_toc}}}")
        elif toc_level == 'both':
            formatted_output.append(f"\\addcontentsline{{toc}}{{subsection}}{{{mal_toc}}}")
        if index_title:
            formatted_output.append(f"\\index{{{index_title}}}")

    # SubSection Title + Saman Metadata
    header_parts = []
    if display_sub_title:
        header_parts.append(format_dandas(display_sub_title.strip()))
    
    if include_metadata:
        saman_metadata = subsection.get('saman_metadata', '')
        if saman_metadata:
            try:
                sm_mal = devanagari_to_malayalam(saman_metadata)
            except Exception:
                sm_mal = saman_metadata
            header_parts.append(f"\\textcolor{{AccentBrown}}{{{format_dandas(sm_mal)}}}")
    
    if header_parts:
        header_latex = "{\\malayalamfont \\textbf{\\textcolor{AccentGreen}{" + " \\quad ".join(header_parts) + "}}}"
        formatted_output.append("{\\centering " + header_latex + " \\par}")

    # Keep header with mantra text
    formatted_output.append(r"\nopagebreak")
    formatted_output.append(r"\vspace{0.4em}")
    formatted_output.append(r"\nopagebreak")

    mantra_paragraphs = _render_malayalam_mantra_body(subsection)
    formatted_output.extend(mantra_paragraphs)

    return "\n\n".join(formatted_output)


def format_malayalam_rik_only(subsection, supersection_title, section_title, subsection_title, prev_rik_id=None, toc_level='section'):
    """Rik-only mode (with metadata) for Malayalam."""
    return format_malayalam_rik_block(subsection, prev_rik_id=prev_rik_id, include_metadata=True)


def format_malayalam_rik_nometa(subsection, supersection_title, section_title, subsection_title, prev_rik_id=None, toc_level='section'):
    """Rik-only mode (without metadata) for Malayalam."""
    return format_malayalam_rik_block(subsection, prev_rik_id=prev_rik_id, include_metadata=False)


def format_malayalam_samam_only(subsection, supersection_title, section_title, subsection_title, toc_level='section'):
    """Samam-only mode (with metadata) for Malayalam."""
    return format_malayalam_samam_block(subsection, subsection_title, toc_level=toc_level, include_metadata=True)


def format_malayalam_samam_nometa(subsection, supersection_title, section_title, subsection_title, toc_level='section'):
    """Samam-only mode (without metadata) for Malayalam."""
    return format_malayalam_samam_block(subsection, subsection_title, toc_level=toc_level, include_metadata=False)


def format_malayalam_combined(subsection, supersection_title, section_title, subsection_title, prev_rik_id=None, toc_level='section'):
    """Combined mode: Rik (with metadata) followed by Samam (with metadata) for Malayalam."""
    parts = []
    rik_part = format_malayalam_rik_block(subsection, prev_rik_id=prev_rik_id, include_metadata=True)
    if rik_part:
        parts.append(rik_part)
    samam_part = format_malayalam_samam_block(subsection, subsection_title, toc_level=toc_level, include_metadata=True)
    if samam_part:
        parts.append(samam_part)
    return "\n\n".join(parts)


def format_malayalam_samam(subsection, supersection_title, section_title, subsection_title, toc_level='section'):
    """Legacy alias for format_malayalam_samam_only."""
    return format_malayalam_samam_only(subsection, supersection_title, section_title, subsection_title, toc_level=toc_level)


def _normalize_malayalam_samam_text_line(line: str) -> str:
    """Normalize Malayalam Samam line for Unicode text export:
    1. Converts Devanagari/Malayalam numerals to ASCII English numerals (e.g. ॥१॥ -> ॥ 1 ॥).
    2. Converts any internal PUA characters to standard Grantha Unicode equivalents.
    3. Converts swara modifier shorthand tags (A..H) to their authentic Unicode symbols.
    4. Converts Vedic digit 4 (൪) back to standard Malayalam chillu-r (ർ) for Unicode text.
    """
    if not line:
        return ""
    
    # 1. Convert verse numerals to ASCII English digits with clean spacing
    line = re.sub(r'॥\s*([०-९\d൦-൯]+)\s*॥', lambda m: f"॥ {m.group(1).translate(_ENGLISH_DIGITS)} ॥", line)
    
    # 2. Map PUA swara characters to authentic Grantha characters
    pua_to_grantha = {
        '\uE010': '𑌶𑌾',
        '\uE011': '𑌶𑌿',
        '\uE012': '𑌶𑍀',
        '\uE013': '𑌶𑍍',
        '\uE015': '𑌶𑍁',
        '\uE016': '𑌶𑍂',
        '\uE020': '𑌪𑍍𑌲',
        '\uE021': '𑌪𑍍𑌲𑌾',
        '\uE022': '𑌪𑍍𑌲𑌿',
        '\uE023': '𑌪𑍍𑌲𑍀',
        '\uE027': '𑌶𑍍𑌰𑍂',
        '\uE028': '𑌷𑍃',
        '\uE029': '𑌣𑍁',
    }
    for pua, gran in pua_to_grantha.items():
        line = line.replace(pua, gran)
        
    # 3. Map Swara Modifier codes to Unicode symbols (using non-combining characters for standalone text rendering)
    mod_to_unicode = {
        'A': '⁀', 'a': '⁀', '\uE004': '⁀', '╭╮': '⁀',
        'A1': '⁀', 'a1': '⁀', 'A_1': '⁀', 'a_1': '⁀', '\uE00D': '⁀',
        'B': '^', 'b': '^', '\uE005': '^',
        'C': '·', 'c': '·', '\uE001': '·', 'ॱ': '·',
        'D': '∧', 'd': '∧', '\uE006': '∧', 'Ʌ': '∧',
        'D1': '↗', 'd1': '↗', 'D_1': '↗', 'd_1': '↗', '\uE00E': '↗',
        'D2': '✓', 'd2': '✓', 'D_2': '✓', 'd_2': '✓', '\uE00F': '✓',
        'I': '⫽', 'i': '⫽', '\uE02A': '⫽',
        'J': '¯', 'j': '¯', '\uE02B': '¯',
        'B1': '/', 'b1': '/', 'B_1': '/', 'b_1': '/', '\uE02C': '/',
        'K': '⨯', 'k': '⨯', '\uE02D': '⨯',
        'E': '┃', 'e': '┃', '\uE002': '┃',
        'F': '╷', 'f': '╷', '\uE008': '╷',
        'G': '\\', 'g': '\\', '\uE003': '\\',
        'H': '|', 'h': '|', '\uE00C': '|',
        'L': '|', 'l': '|',
    }
    
    def _rep_paren(m):
        content = m.group(1)
        if content in mod_to_unicode:
            return f"({mod_to_unicode[content]})"
        return m.group(0)
    
    line = re.sub(r'\(([^)]+)\)', _rep_paren, line)
    # Convert Vedic repha ൪ back to chillu-r ർ in text export
    line = line.replace('൪', 'ർ')
    return line


def format_malayalam_samam_text(subsection, section_title, subsection_title):
    """Plain-text artifact for Malayalam Samam with Grantha swara markers and Unicode modifiers."""
    formatted_sets = []
    
    # 1. Prioritize malayalam-mantra-sets (contains native Malayalam with Grantha swaras and modifiers)
    for mantra_set in subsection.get('malayalam-mantra-sets', []):
        mantra = mantra_set.get('malayalam-mantra', '')
        if mantra:
            formatted_sets.append(_normalize_malayalam_samam_text_line(mantra))
    if formatted_sets:
        return "\n".join(formatted_sets)
        
    # 2. Check corrected-mantra_sets
    corrected_mantra_sets = subsection.get('corrected-mantra_sets', [])
    if corrected_mantra_sets:
        for corrected in corrected_mantra_sets:
            c_mantra = corrected.get('corrected-mantra', '')
            if c_mantra:
                formatted_sets.append(_normalize_malayalam_samam_text_line(c_mantra))
        if formatted_sets:
            return "\n".join(formatted_sets)

    # 3. Check mantra_sets
    for mantra_set in subsection.get('mantra_sets', []):
        words = []
        for word_dict in mantra_set.get('mantra-words', []):
            w = word_dict.get('word', '')
            sw = word_dict.get('swara', '')
            if sw:
                words.append(f"{w}({sw})")
            else:
                words.append(w)
        if words:
            formatted_sets.append(_normalize_malayalam_samam_text_line(" ".join(words)))

    return "\n".join(formatted_sets)


# ----------------------------------------------------
# RIK-ONLY TEXT FORMATTING (for separate output mode)
# ----------------------------------------------------
def format_rik_only_text(subsection, section_title, subsection_title, prev_rik_id=None):
    """Format only Rik content for plain text output."""
    formatted_output = []
    
    current_rik_id = subsection.get('rik_id')
    rik_ids = subsection.get('rik_ids', [current_rik_id] if current_rik_id else [])
    rik_metadata = subsection.get('rik_metadata', '')
    rik_text = subsection.get('rik_text', '')
    
    # Skip if no Rik content or if this Rik was already shown
    show_rik_info = (prev_rik_id is None) or (current_rik_id != prev_rik_id)
    
    # Also show if rik_ids contains multiple Riks and the max ID differs from prev
    if not show_rik_info and len(rik_ids) > 1:
        max_rik_id = max(rik_ids) if rik_ids else None
        if max_rik_id is not None and max_rik_id != prev_rik_id:
            show_rik_info = True

    if not show_rik_info or (not rik_metadata and not rik_text):
        return ""
    
    # Rik ID header
    if current_rik_id:
        formatted_output.append(f"॥ ऋक् {to_devanagari_numeral(current_rik_id)} ॥")
    
    # Rik Metadata
    if rik_metadata:
        formatted_output.append(rik_metadata)
    
    # Rik Text (keep accent markers matching vedic_text.txt encoding)
    if rik_text:
        footnotes = subsection.get('footnotes', {})
        rik_text, _ = process_footnotes_text(rik_text, footnotes)
        formatted_output.append(rik_text)
    
    return "\n".join(formatted_output)


# ----------------------------------------------------
# SAMAM-ONLY TEXT FORMATTING (for separate output mode)
# ----------------------------------------------------
def format_samam_only_text(subsection, section_title, subsection_title):
    """Format only Samam content for plain text output."""
    formatted_output = []
    
    header = subsection.get('header', {}).get('header', '')
    saman_metadata = subsection.get('saman_metadata', '')
    
    # Header with Samam metadata on same line
    if header and saman_metadata:
        formatted_output.append(f"{header}  {saman_metadata}")
    elif header:
        formatted_output.append(header)
    elif saman_metadata:
        formatted_output.append(saman_metadata)
    
    # Mantra content
    mantra_sets = subsection.get('mantra_sets', [])
    corrected_mantra_sets = subsection.get('corrected-mantra_sets', [])
    
    # Use corrected mantras if available
    mantra_array = []
    if corrected_mantra_sets:
        for corrected in corrected_mantra_sets:
            corrected_mantra = corrected.get('corrected-mantra', '')
            if corrected_mantra:
                mantra_array.append(corrected_mantra)
    else:
        for mantra_set in mantra_sets:
            mantra_words = mantra_set.get('mantra-words', [])
            mantra = ""
            for word in mantra_words:
                actual_word = word.get('word', '')
                mantra += " " + actual_word
            mantra_array.append(mantra.strip())
    
    footnotes = subsection.get('footnotes', {})
    for mantra in mantra_array:
        # Clean LaTeX formatting for plain text
        clean_mantra = mantra.replace('\\newline%', ' ')
        clean_mantra = clean_mantra.replace('\\newline', ' ')
        clean_mantra = re.sub(r'\\[a-zA-Z]+\{[^}]*\}', '', clean_mantra)  # Remove \command{...}
        clean_mantra = re.sub(r'\\[a-zA-Z]+', '', clean_mantra)  # Remove \command
        clean_mantra = re.sub(r'\s+', ' ', clean_mantra).strip()  # Clean extra spaces
        
        # Apply footnote application
        clean_mantra, _ = process_footnotes_text(clean_mantra, footnotes)
        formatted_output.append(clean_mantra)
    
    return "\n".join(formatted_output)


# ----------------------------------------------------
# RIK NO-METADATA TEXT FORMATTING (for nometa output mode)
# ----------------------------------------------------
def format_rik_nometa_text(subsection, section_title, subsection_title, prev_rik_id=None):
    """Format only Rik text (without metadata) for plain text output."""
    formatted_output = []
    
    current_rik_id = subsection.get('rik_id')
    rik_ids = subsection.get('rik_ids', [current_rik_id] if current_rik_id else [])
    rik_text = subsection.get('rik_text', '')
    
    # Skip if no Rik content or if this Rik was already shown
    show_rik_info = (prev_rik_id is None) or (current_rik_id != prev_rik_id)

    # Also show if rik_ids contains multiple Riks and the max ID differs from prev
    if not show_rik_info and len(rik_ids) > 1:
        max_rik_id = max(rik_ids) if rik_ids else None
        if max_rik_id is not None and max_rik_id != prev_rik_id:
            show_rik_info = True

    if not show_rik_info or not rik_text:
        return ""
    
    # Rik ID header
    if current_rik_id:
        formatted_output.append(f"॥ ऋक् {to_devanagari_numeral(current_rik_id)} ॥")
    
    # Rik Text only (NO metadata)
    if rik_text:
        footnotes = subsection.get('footnotes', {})
        rik_text, _ = process_footnotes_text(rik_text, footnotes)
        formatted_output.append(rik_text)
    
    return "\n".join(formatted_output)


# ----------------------------------------------------
# SAMAM NO-METADATA TEXT FORMATTING (for nometa output mode)
# ----------------------------------------------------
def format_samam_nometa_text(subsection, section_title, subsection_title):
    """Format only Samam mantra text (without header or metadata) for plain text output.
    
    Note: The header is output separately by the template's SubSection Title section,
    so we do NOT include it here to avoid duplication.
    """
    formatted_output = []
    
    # Mantra content
    mantra_sets = subsection.get('mantra_sets', [])
    corrected_mantra_sets = subsection.get('corrected-mantra_sets', [])
    
    # Use corrected mantras if available
    mantra_array = []
    if corrected_mantra_sets:
        for corrected in corrected_mantra_sets:
            corrected_mantra = corrected.get('corrected-mantra', '')
            if corrected_mantra:
                mantra_array.append(corrected_mantra)
    else:
        for mantra_set in mantra_sets:
            mantra_words = mantra_set.get('mantra-words', [])
            mantra = ""
            for word in mantra_words:
                actual_word = word.get('word', '')
                mantra += " " + actual_word
            mantra_array.append(mantra.strip())
    
    footnotes = subsection.get('footnotes', {})
    for mantra in mantra_array:
        # Clean LaTeX formatting for plain text
        clean_mantra = mantra.replace('\\newline%', ' ')
        clean_mantra = clean_mantra.replace('\\newline', ' ')
        clean_mantra = re.sub(r'\\[a-zA-Z]+\{[^}]*\}', '', clean_mantra)  # Remove \command{...}
        clean_mantra = re.sub(r'\\[a-zA-Z]+', '', clean_mantra)  # Remove \command
        clean_mantra = re.sub(r'\s+', ' ', clean_mantra).strip()  # Clean extra spaces
        
        # Apply footnote application
        clean_mantra, _ = process_footnotes_text(clean_mantra, footnotes)
        formatted_output.append(clean_mantra)
    
    return "\n".join(formatted_output)


# ----------------------------------------------------
# HTML GENERATION FUNCTIONS
# ----------------------------------------------------

def escape_for_html(text):
    """Escape special HTML characters."""
    if not text:
        return text
    html_escapes = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#39;',
    }
    return ''.join(html_escapes.get(c, c) for c in text)

def format_dandas_html(text, preserve_spaces=False):
    """
    Formats danda symbols for HTML output.
    Adds appropriate spacing and wraps mantra numbers in spans.
    """
    if not text or not isinstance(text, str):
        return text

    # Normalize dandas
    text = re.sub(r'\|\|', '॥', text)
    text = re.sub(r'\|\s*\|', '॥', text)
    text = re.sub(r'।।', '॥', text)
    text = text.replace('|', '।')

    # Wrap mantra numbers in span
    danda_pattern = r'(?:\|\||॥)'
    digits = r'[\d०-९]+'
    pattern = rf'({danda_pattern})\s*({digits})\s*({danda_pattern})'
    text = re.sub(pattern, r'<span class="mantra-number">\1 \2 \3</span>', text)

    # Add spacing around dandas
    text = text.replace('॥', ' <span class="danda">॥</span> ')
    text = text.replace('।', ' <span class="danda">।</span> ')

    # Clean up extra spaces ONLY if we don't want to preserve manual alignments
    if not preserve_spaces:
        text = re.sub(r'\s+', ' ', text)
        
    return text.strip()


def handle_consecutive_trikamba_html(text):
    """
    Inserts a thin space between consecutive trikamba accent marks (4) in HTML
    to prevent visual overlap when rendered.
    
    This is only needed for HTML rendering; PDF rendering handles spacing correctly.
    """
    if not text:
        return text
    
    # Pattern: (4) followed by 1-3 characters (a single Devanagari grapheme cluster) 
    # and then another (4)
    # We insert a thin space character after the first character following (4)
    # when another (4) follows soon after
    
# Match: (4) + short text (1-3 chars) + (4)
    # Replace with: (4) + short text + thin space + (4)
    pattern = r'\(4\)([^\(\)]{1,3})\(4\)'
    replacement = r'(4)\1 (4)'  # Insert a regular space before the second (4)
    
    text = re.sub(pattern, replacement, text)
    
    return text

HTML_MOD_MAP = {
    'C': ('mod-c', '&#xE001;', 'Upper Shoulder Dot (·)'),
    'c': ('mod-c', '&#xE001;', 'Upper Shoulder Dot (·)'),
    '·': ('mod-c', '&#xE001;', 'Upper Shoulder Dot (·)'),
    'ॱ': ('mod-c', '&#xE001;', 'Upper Shoulder Dot (·)'),
    'H': ('mod-h', '&#xE00C;', 'High Pitch Swarita (|)'),
    'h': ('mod-h', '&#xE00C;', 'High Pitch Swarita (|)'),
    '|': ('mod-h', '&#xE00C;', 'High Pitch Swarita (|)'),
    'G': ('mod-g', '&#xE003;', 'Lower Under-Slash (\\)'),
    'g': ('mod-g', '&#xE003;', 'Lower Under-Slash (\\)'),
    '\\': ('mod-g', '&#xE003;', 'Lower Under-Slash (\\)'),
    'A': ('mod-a', '&#xE004;', 'Melodic Arc (⁀)'),
    'a': ('mod-a', '&#xE004;', 'Melodic Arc (⁀)'),
    '⁀': ('mod-a', '&#xE004;', 'Melodic Arc (⁀)'),
    'A1': ('mod-a1', '&#xE00D;', 'Arc over Danda'),
    'a1': ('mod-a1', '&#xE00D;', 'Arc over Danda'),
    'A_1': ('mod-a1', '&#xE00D;', 'Arc over Danda'),
    'a_1': ('mod-a1', '&#xE00D;', 'Arc over Danda'),
    'D': ('mod-d', '&#xE006;', 'Chevron Roof (∧)'),
    'd': ('mod-d', '&#xE006;', 'Chevron Roof (∧)'),
    '∧': ('mod-d', '&#xE006;', 'Chevron Roof (∧)'),
    'Ʌ': ('mod-d', '&#xE006;', 'Chevron Roof (∧)'),
    'D1': ('mod-d1', '&#xE00E;', 'Rising Stroke (↗)'),
    'd1': ('mod-d1', '&#xE00E;', 'Rising Stroke (↗)'),
    'D_1': ('mod-d1', '&#xE00E;', 'Rising Stroke (↗)'),
    'd_1': ('mod-d1', '&#xE00E;', 'Rising Stroke (↗)'),
    '↗': ('mod-d1', '&#xE00E;', 'Rising Stroke (↗)'),
    'D2': ('mod-d2', '&#xE00F;', 'Check Tick (✓)'),
    'd2': ('mod-d2', '&#xE00F;', 'Check Tick (✓)'),
    'D_2': ('mod-d2', '&#xE00F;', 'Check Tick (✓)'),
    'd_2': ('mod-d2', '&#xE00F;', 'Check Tick (✓)'),
    '✓': ('mod-d2', '&#xE00F;', 'Check Tick (✓)'),
    'I': ('mod-i', '&#xE02A;', 'Double Shoulder Dash (⫽)'),
    'i': ('mod-i', '&#xE02A;', 'Double Shoulder Dash (⫽)'),
    'J': ('mod-j', '&#xE02B;', 'Overhead Horizontal Bar (¯)'),
    'j': ('mod-j', '&#xE02B;', 'Overhead Horizontal Bar (¯)'),
    'B1': ('mod-b1', '&#xE02C;', 'Diagonal Bridging Slash (/)'),
    'b1': ('mod-b1', '&#xE02C;', 'Diagonal Bridging Slash (/)'),
    'B_1': ('mod-b1', '&#xE02C;', 'Diagonal Bridging Slash (/)'),
    'b_1': ('mod-b1', '&#xE02C;', 'Diagonal Bridging Slash (/)'),
    'K': ('mod-k', '&#xE02D;', 'Shoulder Cross Mark (⨯)'),
    'k': ('mod-k', '&#xE02D;', 'Shoulder Cross Mark (⨯)'),
    'B': ('mod-b', '&#xE005;', 'Peak Elevation Caret (∧)'),
    'b': ('mod-b', '&#xE005;', 'Peak Elevation Caret (∧)'),
    '^': ('mod-b', '&#xE005;', 'Peak Elevation Caret (∧)'),
    'E': ('mod-e', '&#xE002;', 'Bold Tone Column (┃)'),
    'e': ('mod-e', '&#xE002;', 'Bold Tone Column (┃)'),
    '┃': ('mod-e', '&#xE002;', 'Bold Tone Column (┃)'),
    'F': ('mod-f', '&#xE008;', 'Danda with Overhead Dot (╷)'),
    'f': ('mod-f', '&#xE008;', 'Danda with Overhead Dot (╷)'),
    '╷': ('mod-f', '&#xE008;', 'Danda with Overhead Dot (╷)'),
    '_': ('mod-under', '_', 'Underbar'),
    ',': ('mod-comma', ',', 'Comma'),
    '.': ('mod-dot', '.', 'Dot')
}

def render_mod_html(mod_str: str) -> str:
    m = mod_str.strip('()')
    if m in HTML_MOD_MAP:
        cls, glyph, title = HTML_MOD_MAP[m]
        return f'<span class="swara-mod {cls}" title="{title}">{glyph}</span>'
    return f'<span class="swara-mod">{mod_str}</span>'

DEVA_SYLLABLE_RE = re.compile(
    r'(?:[\u0904-\u0914\u0960\u0961]|(?:[\u0915-\u0939\u0958-\u095F]\u094D)*[\u0915-\u0939\u0958-\u095F](?:[\u093E-\u094D\u094E\u094F\u0955-\u0957\u0962\u0963])?)(?:[\u0901-\u0903])?(?:[_,.\\·ॱ┃L╷^⁀∧✓])*'
)

def split_deva_syllables(text: str):
    res = DEVA_SYLLABLE_RE.findall(text)
    return res if res else ([text] if text else [])

def format_deva_syl_html(syl: str, with_modifiers: bool = True) -> str:
    if not with_modifiers:
        return syl.rstrip('_,.\\·ॱ┃L╷^⁀∧✓')
    m = re.match(r'^(.*?)([_,.\\·ॱ┃L╷^⁀∧✓]*)$', syl)
    base = m.group(1) if m else syl
    extras = m.group(2) if m else ''
    extras_html = ''.join([render_mod_html(e) for e in extras])
    return base + extras_html

def render_deva_html_from_line(line: str, with_modifiers: bool = True) -> str:
    """Render a Devanagari mantra line to flexbox-stacked HTML matching visual baseline."""
    from malayalam.ml_text import tokenize_mantra_line
    tokens = tokenize_mantra_line(line)
    
    # Identify spanning markers that attach to the preceding word
    SPANNING_MARKERS = {'A', 'a', '⁀', 'A1', 'a1', 'A_1', 'a_1', 'D', 'd', '∧', 'Ʌ', 'B', 'b', '^', 'B1', 'b1'}
    
    rendered_items = []
    
    idx = 0
    while idx < len(tokens):
        v_count, v_num = _match_verse_num_marker(tokens, idx)
        if v_count > 0:
            rendered_items.append({
                'type': 'verse_num',
                'html': f'<span class="mantra-word verse-num-word"><span class="mantra-text verse-num-marker"><span class="danda">॥</span><span class="verse-num">{v_num}</span><span class="danda">॥</span></span><span class="swara-text">&nbsp;</span></span>'
            })
            idx += v_count
            continue
            
        tok = tokens[idx]
        t = tok['type']
        
        if t == 'space':
            prev_is_danda = (idx > 0 and tokens[idx-1]['type'] == 'danda')
            if prev_is_danda:
                rendered_items.append({
                    'type': 'space',
                    'html': '<span class="mantra-word word-space"><span class="mantra-text">&nbsp;</span><span class="swara-text">&nbsp;</span></span>'
                })
        elif t == 'danda':
            rendered_items.append({
                'type': 'danda',
                'html': f'<span class="mantra-word"><span class="mantra-text danda">{tok["char"]}</span><span class="swara-text">&nbsp;</span></span>'
            })
        elif t == 'marker':
            m_val = tok.get('marker', '').strip('()')
            if with_modifiers and m_val in SPANNING_MARKERS:
                if m_val in ('A', 'a', '⁀', '\uE004'):
                    d_idx = idx + 1
                    while d_idx < len(tokens) and tokens[d_idx]['type'] == 'space':
                        d_idx += 1
                    if d_idx < len(tokens) and tokens[d_idx]['type'] == 'danda' and tokens[d_idx]['char'] == '।':
                        m_val = 'A1'
                mod_h = render_mod_html(m_val)
                attached = False
                for prev_item in reversed(rendered_items):
                    if prev_item['type'] == 'word':
                        prev_item['spanning_mod'] = mod_h
                        prev_item['spanning_type'] = m_val
                        attached = True
                        break
                if not attached:
                    rendered_items.append({
                        'type': 'marker',
                        'html': f'<span class="mantra-word"><span class="mantra-text">{mod_h}</span><span class="swara-text">&nbsp;</span></span>'
                    })
            elif with_modifiers:
                mod_h = render_mod_html(tok['marker'])
                rendered_items.append({
                    'type': 'marker',
                    'html': f'<span class="mantra-word"><span class="mantra-text">{mod_h}</span><span class="swara-text">&nbsp;</span></span>'
                })
        elif t == 'footnote':
            rendered_items.append({
                'type': 'footnote',
                'html': f'<sup>{tok["text"]}</sup>'
            })
        elif t == 'word':
            word = tok.get('word', '')
            swara = tok.get('swara', '')
            visarga = tok.get('visarga', '')
            if visarga:
                word += visarga
            
            span_mod_html = None
            span_mod_type = None
            if not with_modifiers:
                core_word = word.rstrip('_,.\\·ॱ┃L╷^⁀∧✓')
                punct_html = ''
                mods_html = ''
                sw_parts, _ = _parse_swara_and_modifiers(swara)
            else:
                core_word = word.rstrip('_,.\\·ॱ┃L╷^⁀∧✓')
                trailing_punct = word[len(core_word):]
                punct_html = ''.join([render_mod_html(p) for p in trailing_punct])
                sw_parts, mods = _parse_swara_and_modifiers(swara)
                
                # Look ahead to check if followed by danda
                next_is_danda = False
                n_idx = idx + 1
                while n_idx < len(tokens) and tokens[n_idx]['type'] == 'space':
                    n_idx += 1
                if n_idx < len(tokens) and tokens[n_idx]['type'] == 'danda' and tokens[n_idx]['char'] == '।':
                    next_is_danda = True
                
                reg_mods = []
                for m in mods:
                    m_clean = m.strip('()')
                    if m_clean in SPANNING_MARKERS:
                        if m_clean in ('A', 'a', '⁀', '\uE004') and next_is_danda:
                            m_clean = 'A1'
                        span_mod_html = render_mod_html(m_clean)
                        span_mod_type = m_clean
                    else:
                        reg_mods.append(m)
                mods_html = ''.join([render_mod_html(m) for m in reg_mods])
            
            sw_letter = ' '.join(sw_parts) if sw_parts else ''
            syllables = split_deva_syllables(core_word) if core_word else []
            last_syl = syllables.pop() if syllables else ''
            
            w_html_parts = []
            for syl in syllables:
                syl_formatted = format_deva_syl_html(syl, with_modifiers=with_modifiers)
                w_html_parts.append(f'<span class="mantra-word"><span class="mantra-text">{syl_formatted}</span><span class="swara-text">&nbsp;</span></span>')
            
            last_syl_formatted = format_deva_syl_html(last_syl, with_modifiers=with_modifiers) if last_syl else ''
            
            rendered_items.append({
                'type': 'word',
                'prefix_syls_html': ''.join(w_html_parts),
                'last_syl_formatted': last_syl_formatted,
                'mods_html': mods_html,
                'punct_html': punct_html,
                'bot_content': sw_letter if sw_letter else "&nbsp;",
                'spanning_mod': span_mod_html,
                'spanning_type': span_mod_type
            })
        idx += 1

    # Now assemble final HTML, wrapping connected spanning groups in <span class="mantra-connected-group">
    final_output = []
    i = 0
    while i < len(rendered_items):
        item = rendered_items[i]
        if item['type'] == 'word' and item.get('spanning_mod'):
            # This word has a spanning modifier connecting to next word (and possibly danda)
            group_items = [item]
            j = i + 1
            while j < len(rendered_items):
                next_it = rendered_items[j]
                if next_it['type'] == 'space':
                    # Remove whitespace around danda inside spanning connected groups
                    j += 1
                    continue
                group_items.append(next_it)
                j += 1
                if next_it['type'] == 'word' and not next_it.get('spanning_mod'):
                    break
            
            group_html = []
            for g_item in group_items:
                if g_item['type'] == 'word':
                    span_mod_str = g_item.get('spanning_mod') or ''
                    top_content = f"{g_item['last_syl_formatted']}{g_item['mods_html']}{g_item['punct_html']}{span_mod_str}" if (g_item['last_syl_formatted'] or g_item['mods_html'] or g_item['punct_html'] or span_mod_str) else "&nbsp;"
                    bot_content = g_item['bot_content']
                    word_html = f"{g_item['prefix_syls_html']}<span class=\"mantra-word\"><span class=\"mantra-text\">{top_content}</span><span class=\"swara-text\">{bot_content}</span></span>"
                    group_html.append(word_html)
                else:
                    group_html.append(g_item['html'])
            
            final_output.append(f'<span class="mantra-connected-group">{"".join(group_html)}</span>')
            i = j
        else:
            if item['type'] == 'word':
                top_content = f"{item['last_syl_formatted']}{item['mods_html']}{item['punct_html']}" if (item['last_syl_formatted'] or item['mods_html'] or item['punct_html']) else "&nbsp;"
                bot_content = item['bot_content']
                word_html = f"{item['prefix_syls_html']}<span class=\"mantra-word\"><span class=\"mantra-text\">{top_content}</span><span class=\"swara-text\">{bot_content}</span></span>"
                final_output.append(word_html)
            else:
                final_output.append(item['html'])
            i += 1
            
    return ''.join(final_output)


def format_mantra_sets_html(subsection, supersection_title, section_title, subsection_title, footnote_dict={}, prev_rik_id=None, subsection_key=None, 
                              footnote_counter=0, footnotes_accumulator=None, seen_content_map=None, with_modifiers=True):
    """
    Formats mantra data as HTML using ruby-based layout for word/swara stacking.
    Only renders rik_metadata and rik_text if rik_id differs from prev_rik_id.
    """
    HTML_FOOTNOTE_COUNTER = footnote_counter
    formatted_output = []
    collected_footnotes = []
    seen_markers_map = seen_content_map if seen_content_map is not None else {}

    # --- DATA EXTRACTION ---
    current_rik_id = subsection.get('rik_id')
    current_rik_ids = subsection.get('rik_ids', [current_rik_id] if current_rik_id else [])
    string_1 = subsection.get('rik_metadata', '')
    string_2 = subsection.get('rik_text', '')
    string_3 = subsection.get('saman_metadata', '')
    footnote_data = subsection.get('footnotes', {})
    
    show_rik_info = (prev_rik_id is None) or (current_rik_id != prev_rik_id)
    if not show_rik_info and len(current_rik_ids) > 1:
        max_rik_id = max(current_rik_ids) if current_rik_ids else None
        if max_rik_id is not None and max_rik_id != prev_rik_id:
            show_rik_info = True
    
    # Clean titles
    display_sub_title = re.sub(r'^([|॥]+)\s*', r'\1 ', subsection_title) if subsection_title else ''

    # 1. Rik Metadata - Only if rik_id changed
    if string_1 and show_rik_info:
        s1 = escape_for_html(string_1)
        s1 = format_dandas_html(s1, preserve_spaces=True)
        s1, fnotes, HTML_FOOTNOTE_COUNTER = process_footnotes_html(s1, footnote_data, HTML_FOOTNOTE_COUNTER, seen_markers_map, subsection_key)
        collected_footnotes.extend(fnotes)
        formatted_output.append(f'<div class="rik-metadata sanskrit-text">{s1}</div>')

    # 2. Rik Text (With accents) - Only if rik_id changed
    if string_2 and show_rik_info:
        s2 = remove_mantra_spaces(string_2)
        s2 = s2.replace('\\newline%', '').replace('\\newline', '')
        s2 = escape_for_html(s2)
        s2, fnotes, HTML_FOOTNOTE_COUNTER = process_footnotes_html(s2, footnote_data, HTML_FOOTNOTE_COUNTER, seen_markers_map, subsection_key)
        collected_footnotes.extend(fnotes)
        s2 = handle_consecutive_trikamba_html(s2)
        s2 = replace_accents_html(s2)
        s2 = split_rik_lines_html(s2)
        s2 = format_dandas_html(s2)
        formatted_output.append(f'<div class="rik-text sanskrit-text">{s2}</div>')

    # 3. Combined Header
    header_parts = []
    if display_sub_title:
        header_title = escape_for_html(display_sub_title)
        header_title = format_dandas_html(header_title)
        header_parts.append(f'<span class="header-title">{header_title}</span>')
    if string_3:
        meta = escape_for_html(string_3)
        meta = format_dandas_html(meta, preserve_spaces=True)
        meta, fnotes, HTML_FOOTNOTE_COUNTER = process_footnotes_html(meta, footnote_data, HTML_FOOTNOTE_COUNTER, seen_markers_map, subsection_key)
        collected_footnotes.extend(fnotes)
        header_parts.append(f'<span class="header-meta">{meta}</span>')
    
    if header_parts:
        formatted_output.append(f'<div class="subsection-header">{" &nbsp; ".join(header_parts)}</div>')

    # --- MANTRA CONTENT RENDERING ---
    mantra_sets = subsection.get('corrected-mantra_sets', [])
    if not mantra_sets:
        mantra_sets = subsection.get('mantra_sets', [])

    mantra_array = []
    for mset in mantra_sets:
        m = mset.get('corrected-mantra') or mset.get('mantra', '')
        if m:
            mantra_array.append(m)
        elif mset.get('mantra-words'):
            words = []
            for word_dict in mset.get('mantra-words', []):
                w = word_dict.get('word', '')
                sw = word_dict.get('swara', '')
                if sw:
                    words.append(f"{w}({sw})")
                else:
                    words.append(w)
            if words:
                mantra_array.append(" ".join(words))

    for mantra_line in mantra_array:
        clean_mantra = mantra_line.replace('\\newline%', ' ').replace('\\newline', ' ')
        clean_mantra, fnotes, HTML_FOOTNOTE_COUNTER = process_footnotes_html(clean_mantra, footnote_data, HTML_FOOTNOTE_COUNTER, seen_markers_map, subsection_key)
        collected_footnotes.extend(fnotes)
        
        verse_parts = re.split(r'(॥\s*[\d०-९]+\s*॥)', clean_mantra)
        
        for idx_v in range(0, len(verse_parts), 2):
            v_text = verse_parts[idx_v].strip()
            v_marker = verse_parts[idx_v + 1] if idx_v + 1 < len(verse_parts) else ''
            
            if not v_text and not v_marker:
                continue
                
            v_html = render_deva_html_from_line(v_text, with_modifiers=with_modifiers)
            if v_marker:
                v_num_match = re.search(r'[\d०-९]+', v_marker)
                v_num = v_num_match.group(0) if v_num_match else ''
                v_html += f' <span class="mantra-word verse-num-word"><span class="mantra-text verse-num-marker"><span class="danda">॥</span><span class="verse-num">{v_num}</span><span class="danda">॥</span></span><span class="swara-text">&nbsp;</span></span>'
                
            is_mixed = bool(string_2.strip())
            style = ' style="margin-bottom: 2.5rem;"' if is_mixed else ''
            formatted_output.append(f'<div class="mantra-verse"{style}>{v_html}</div>')

    # Accumulate footnotes for section-level rendering (don't render inline)
    if collected_footnotes and footnotes_accumulator is not None:
        footnotes_accumulator.extend(collected_footnotes)

    return '\n'.join(formatted_output), HTML_FOOTNOTE_COUNTER


def format_rik_only_html(subsection, supersection_title, section_title, subsection_title, footnote_dict={}, prev_rik_id=None, subsection_key=None,
                         footnote_counter=0, footnotes_accumulator=None, seen_content_map=None):
    """
    Format only Rik content (rik_metadata and rik_text) for HTML separate output mode.
    Skips all Samam-related content.
    """
    HTML_FOOTNOTE_COUNTER = footnote_counter
    formatted_output = []
    collected_footnotes = []
    footnote_data = subsection.get('footnotes', {})
    seen_markers_map = seen_content_map if seen_content_map is not None else {}
    
    current_rik_id = subsection.get('rik_id')
    string_1 = subsection.get('rik_metadata', '')
    string_2 = subsection.get('rik_text', '')
    
    if not string_1 and not string_2:
        return "", HTML_FOOTNOTE_COUNTER
    
    show_rik_info = (prev_rik_id is None) or (current_rik_id != prev_rik_id)
    if not show_rik_info:
        return "", HTML_FOOTNOTE_COUNTER
    
    if string_1:
        s1 = escape_for_html(string_1)
        s1 = format_dandas_html(s1, preserve_spaces=True)
        s1, fnotes, HTML_FOOTNOTE_COUNTER = process_footnotes_html(s1, footnote_data, HTML_FOOTNOTE_COUNTER, seen_markers_map, subsection_key)
        collected_footnotes.extend(fnotes)
        formatted_output.append(f'<div class="rik-metadata sanskrit-text">{s1}</div>')

    if string_2:
        s2 = remove_mantra_spaces(string_2)
        s2 = s2.replace('\\newline%', '').replace('\\newline', '')
        s2 = escape_for_html(s2)
        s2, fnotes, HTML_FOOTNOTE_COUNTER = process_footnotes_html(s2, footnote_data, HTML_FOOTNOTE_COUNTER, seen_markers_map, subsection_key)
        collected_footnotes.extend(fnotes)
        s2 = handle_consecutive_trikamba_html(s2)
        s2 = replace_accents_html(s2)
        s2 = split_rik_lines_html(s2)
        s2 = format_dandas_html(s2)
        formatted_output.append(f'<div class="rik-text sanskrit-text">{s2}</div>')

    if collected_footnotes and footnotes_accumulator is not None:
        footnotes_accumulator.extend(collected_footnotes)

    return '\n'.join(formatted_output), HTML_FOOTNOTE_COUNTER


def format_rik_nometa_html(subsection, supersection_title, section_title, subsection_title, footnote_dict={}, prev_rik_id=None, subsection_key=None,
                           footnote_counter=0, footnotes_accumulator=None, seen_content_map=None):
    """
    Format only Rik text (without rik_metadata) for HTML nometa output mode.
    Skips all Samam-related content and metadata.
    """
    HTML_FOOTNOTE_COUNTER = footnote_counter
    formatted_output = []
    collected_footnotes = []
    footnote_data = subsection.get('footnotes', {})
    seen_markers_map = seen_content_map if seen_content_map is not None else {}
    
    current_rik_id = subsection.get('rik_id')
    string_2 = subsection.get('rik_text', '')
    
    if not string_2:
        return "", HTML_FOOTNOTE_COUNTER
    
    show_rik_info = (prev_rik_id is None) or (current_rik_id != prev_rik_id)
    if not show_rik_info:
        return "", HTML_FOOTNOTE_COUNTER
    
    if string_2:
        s2 = remove_mantra_spaces(string_2)
        s2 = s2.replace('\\newline%', '').replace('\\newline', '')
        s2 = escape_for_html(s2)
        s2, fnotes, HTML_FOOTNOTE_COUNTER = process_footnotes_html(s2, footnote_data, HTML_FOOTNOTE_COUNTER, seen_markers_map, subsection_key)
        collected_footnotes.extend(fnotes)
        s2 = handle_consecutive_trikamba_html(s2)
        s2 = replace_accents_html(s2)
        s2 = split_rik_lines_html(s2)
        s2 = format_dandas_html(s2)
        formatted_output.append(f'<div class="rik-text">{s2}</div>')

    if collected_footnotes and footnotes_accumulator is not None:
        footnotes_accumulator.extend(collected_footnotes)

    return '\n'.join(formatted_output), HTML_FOOTNOTE_COUNTER


def format_samam_only_html(subsection, supersection_title, section_title, subsection_title, footnote_dict={}, prev_rik_id=None, subsection_key=None,
                           footnote_counter=0, footnotes_accumulator=None, seen_content_map=None, with_modifiers=True):
    """
    Format only Samam content (header, saman_metadata, mantra text) for HTML separate output mode.
    Skips all Rik-related content.
    """
    HTML_FOOTNOTE_COUNTER = footnote_counter
    formatted_output = []
    collected_footnotes = []
    footnote_data = subsection.get('footnotes', {})
    seen_markers_map = seen_content_map if seen_content_map is not None else {}
    
    string_3 = subsection.get('saman_metadata', '')
    
    # Clean titles
    display_sub_title = re.sub(r'^([|॥]+)\s*', r'\1 ', subsection_title) if subsection_title else ''

    # Header
    header_parts = []
    if display_sub_title:
        header_title = escape_for_html(display_sub_title)
        header_title = format_dandas_html(header_title)
        header_parts.append(f'<span class="header-title">{header_title}</span>')
    if string_3:
        meta = escape_for_html(string_3)
        meta = format_dandas_html(meta, preserve_spaces=True)
        meta, fnotes, HTML_FOOTNOTE_COUNTER = process_footnotes_html(meta, footnote_data, HTML_FOOTNOTE_COUNTER, seen_markers_map, subsection_key)
        collected_footnotes.extend(fnotes)
        header_parts.append(f'<span class="header-meta">{meta}</span>')
    
    if header_parts:
        formatted_output.append(f'<div class="subsection-header">{" &nbsp; ".join(header_parts)}</div>')

    # Mantra Content
    mantra_sets = subsection.get('corrected-mantra_sets', [])
    if not mantra_sets:
        mantra_sets = subsection.get('mantra_sets', [])

    mantra_array = []
    for mset in mantra_sets:
        m = mset.get('corrected-mantra') or mset.get('mantra', '')
        if m:
            mantra_array.append(m)
        elif mset.get('mantra-words'):
            words = []
            for word_dict in mset.get('mantra-words', []):
                w = word_dict.get('word', '')
                sw = word_dict.get('swara', '')
                if sw:
                    words.append(f"{w}({sw})")
                else:
                    words.append(w)
            if words:
                mantra_array.append(" ".join(words))

    for mantra_line in mantra_array:
        clean_mantra = mantra_line.replace('\\newline%', ' ').replace('\\newline', ' ')
        clean_mantra, fnotes, HTML_FOOTNOTE_COUNTER = process_footnotes_html(clean_mantra, footnote_data, HTML_FOOTNOTE_COUNTER, seen_markers_map, subsection_key)
        collected_footnotes.extend(fnotes)
        
        verse_parts = re.split(r'(॥\s*[\d०-९]+\s*॥)', clean_mantra)
        
        for idx_v in range(0, len(verse_parts), 2):
            v_text = verse_parts[idx_v].strip()
            v_marker = verse_parts[idx_v + 1] if idx_v + 1 < len(verse_parts) else ''
            
            if not v_text and not v_marker:
                continue
                
            v_html = render_deva_html_from_line(v_text, with_modifiers=with_modifiers)
            if v_marker:
                v_num_match = re.search(r'[\d०-९]+', v_marker)
                v_num = v_num_match.group(0) if v_num_match else ''
                v_html += f' <span class="mantra-word verse-num-word"><span class="mantra-text verse-num-marker"><span class="danda">॥</span><span class="verse-num">{v_num}</span><span class="danda">॥</span></span><span class="swara-text">&nbsp;</span></span>'
                
            formatted_output.append(f'<div class="mantra-verse">{v_html}</div>')

    if collected_footnotes and footnotes_accumulator is not None:
        footnotes_accumulator.extend(collected_footnotes)
            
    return '\n'.join(formatted_output), HTML_FOOTNOTE_COUNTER


def format_samam_nometa_html(subsection, supersection_title, section_title, subsection_title, footnote_dict={}, prev_rik_id=None, subsection_key=None,
                             footnote_counter=0, footnotes_accumulator=None, seen_content_map=None, with_modifiers=True):
    """
    Format only Samam content (header, mantra text) for HTML nometa output mode.
    Skips all Rik-related content and saman_metadata.
    """
    HTML_FOOTNOTE_COUNTER = footnote_counter
    formatted_output = []
    collected_footnotes = []
    footnote_data = subsection.get('footnotes', {})
    seen_markers_map = seen_content_map if seen_content_map is not None else {}
    
    # Clean titles
    display_sub_title = re.sub(r'^([|॥]+)\s*', r'\1 ', subsection_title) if subsection_title else ''

    # Header - ONLY subsection header, no metadata
    if display_sub_title:
        header_title = escape_for_html(display_sub_title)
        header_title = format_dandas_html(header_title)
        formatted_output.append(f'<div class="subsection-header"><span class="header-title">{header_title}</span></div>')

    # Mantra Content
    mantra_sets = subsection.get('corrected-mantra_sets', [])
    if not mantra_sets:
        mantra_sets = subsection.get('mantra_sets', [])

    mantra_array = []
    for mset in mantra_sets:
        m = mset.get('corrected-mantra') or mset.get('mantra', '')
        if m:
            mantra_array.append(m)
        elif mset.get('mantra-words'):
            words = []
            for word_dict in mset.get('mantra-words', []):
                w = word_dict.get('word', '')
                sw = word_dict.get('swara', '')
                if sw:
                    words.append(f"{w}({sw})")
                else:
                    words.append(w)
            if words:
                mantra_array.append(" ".join(words))

    for mantra_line in mantra_array:
        clean_mantra = mantra_line.replace('\\newline%', ' ').replace('\\newline', ' ')
        clean_mantra, fnotes, HTML_FOOTNOTE_COUNTER = process_footnotes_html(clean_mantra, footnote_data, HTML_FOOTNOTE_COUNTER, seen_markers_map, subsection_key)
        collected_footnotes.extend(fnotes)
        
        verse_parts = re.split(r'(॥\s*[\d०-९]+\s*॥)', clean_mantra)
        
        for idx_v in range(0, len(verse_parts), 2):
            v_text = verse_parts[idx_v].strip()
            v_marker = verse_parts[idx_v + 1] if idx_v + 1 < len(verse_parts) else ''
            
            if not v_text and not v_marker:
                continue
                
            v_html = render_deva_html_from_line(v_text, with_modifiers=with_modifiers)
            if v_marker:
                v_num_match = re.search(r'[\d०-९]+', v_marker)
                v_num = v_num_match.group(0) if v_num_match else ''
                v_html += f' <span class="mantra-word verse-num-word"><span class="mantra-text verse-num-marker"><span class="danda">॥</span><span class="verse-num">{v_num}</span><span class="danda">॥</span></span><span class="swara-text">&nbsp;</span></span>'
                
            formatted_output.append(f'<div class="mantra-verse">{v_html}</div>')

    if collected_footnotes and footnotes_accumulator is not None:
        footnotes_accumulator.extend(collected_footnotes)
            
    return '\n'.join(formatted_output), HTML_FOOTNOTE_COUNTER


def format_malayalam_samam_html(subsection, subsection_title, include_metadata=True,
                                 footnote_counter=0, footnotes_accumulator=None, seen_content_map=None, subsection_key=None):
    """
    Format Malayalam Samam content as semantic HTML with clean Grantha swara stacking.
    - Strips all parentheses from the swara marker line.
    - Aligns swara modifiers (Mod-A..Mod-H) cleanly without parentheses.
    """
    from malayalam.ml_text import tokenize_mantra_line
    from malayalam.ml_transliterate import split_malayalam_syllables
    
    formatted_output = []
    collected_footnotes = []
    seen_markers_map = seen_content_map if seen_content_map is not None else {}
    footnote_data = subsection.get('footnotes', {})
    
    # 1. Header
    display_sub_title = re.sub(r'^([|॥]+)\s*', r'\1 ', subsection_title) if subsection_title else ''
    saman_metadata = subsection.get('saman_metadata', '') if include_metadata else ''
    
    header_parts = []
    if display_sub_title:
        header_title = escape_for_html(display_sub_title)
        header_title = format_dandas_html(header_title)
        header_parts.append(f'<span class="header-title">{header_title}</span>')
    if saman_metadata:
        meta = escape_for_html(saman_metadata)
        meta = format_dandas_html(meta, preserve_spaces=True)
        meta, fnotes, footnote_counter = process_footnotes_html(meta, footnote_data, footnote_counter, seen_markers_map, subsection_key)
        collected_footnotes.extend(fnotes)
        header_parts.append(f'<span class="header-meta">{meta}</span>')
        
    if header_parts:
        formatted_output.append(f'<div class="subsection-header">{" &nbsp; ".join(header_parts)}</div>')
        
    # 2. Mantra verses
    mantra_array = []
    mantra_sets = subsection.get('malayalam-mantra-sets', [])
    if not mantra_sets:
        mantra_sets = subsection.get('corrected-mantra_sets', [])
    if not mantra_sets:
        mantra_sets = subsection.get('mantra_sets', [])

    for mset in mantra_sets:
        m = mset.get('malayalam-mantra') or mset.get('corrected-mantra') or mset.get('mantra', '')
        if m:
            mantra_array.append(m)
        elif mset.get('mantra-words'):
            words = []
            for word_dict in mset.get('mantra-words', []):
                w = word_dict.get('word', '')
                sw = word_dict.get('swara', '')
                if sw:
                    words.append(f"{w}({sw})")
                else:
                    words.append(w)
            if words:
                mantra_array.append(" ".join(words))

def render_vedic_html_from_line(text: str) -> str:
    """Exact Python equivalent of renderVedicHTML from Curation Tool app.js.
    Renders stacked red swaras with <ruby> and blue modifiers with .swara-mod.
    """
    from malayalam.ml_transliterate import split_malayalam_syllables

    tokens = re.split(r'(\s+|[।॥])', text)
    html_parts = []
    chunk_re = re.compile(r'([^\s()_.,]+)?((?:\([^()]+\)|[_,.])*)')
    paren_re = re.compile(r'\(([^()]+)\)|(_|,|\.)')
    
    for token in tokens:
        if not token:
            continue
        if token.isspace():
            html_parts.append(' ')
            continue
        if token in ('।', '॥'):
            html_parts.append(f'<span class="danda">{token}</span>')
            continue
        
        word_html = []
        for m in chunk_re.finditer(token):
            base = m.group(1) or ''
            extras = m.group(2) or ''
            if not base and not extras:
                continue
            
            swara_letter = ''
            modifiers_html = []
            has_mod_b = False
            
            for pm in paren_re.finditer(extras):
                inner = (pm.group(1) or pm.group(2) or '').strip()
                if inner in ('C', 'c', '·', '\uE001'):
                    modifiers_html.append('<span class="swara-mod mod-c" title="MOD-C: Upper Shoulder Dot">&#xE001;</span>')
                elif inner in ('H', 'h', '|', '\uE00C'):
                    modifiers_html.append('<span class="swara-mod mod-h" title="MOD-H: High Pitch Swarita">&#xE00C;</span>')
                elif inner in ('G', 'g', '\\', '\uE003'):
                    modifiers_html.append('<span class="swara-mod mod-g" title="MOD-G: Lower Under-Slash (\\)">&#xE003;</span>')
                elif inner in ('A', 'a', '⁀', '\uE004'):
                    modifiers_html.append('<span class="swara-mod mod-a" title="MOD-A: Melodic Arc (⁀)">&#xE004;</span>')
                elif inner in ('A1', 'a1', 'A_1', 'a_1', '\uE00D'):
                    modifiers_html.append('<span class="swara-mod mod-a1" title="MOD-A1: Arc over Danda">&#xE00D;</span>')
                elif inner in ('D', 'd', '∧', 'Ʌ', '\uE006'):
                    modifiers_html.append('<span class="swara-mod mod-d" title="MOD-D: Chevron Roof (∧)">&#xE006;</span>')
                elif inner in ('D1', 'd1', 'D_1', 'd_1', '↗', '\uE00E'):
                    modifiers_html.append('<span class="swara-mod mod-d1" title="MOD-D1: Rising Stroke (↗)">&#xE00E;</span>')
                elif inner in ('D2', 'd2', 'D_2', 'd_2', '✓', '\uE00F'):
                    modifiers_html.append('<span class="swara-mod mod-d2" title="MOD-D2: Check Tick (✓)">&#xE00F;</span>')
                elif inner in ('I', 'i', '⫽', '\uE02A'):
                    modifiers_html.append('<span class="swara-mod mod-i" title="MOD-I: Double Shoulder Dash (⫽)">&#xE02A;</span>')
                elif inner in ('J', 'j', '¯', '\uE02B'):
                    modifiers_html.append('<span class="swara-mod mod-j" title="MOD-J: Overhead Horizontal Bar (¯)">&#xE02B;</span>')
                elif inner in ('B1', 'b1', 'B_1', 'b_1', '\uE02C'):
                    modifiers_html.append('<span class="swara-mod mod-b1" title="MOD-B1: Diagonal Bridging Slash (/)">&#xE02C;</span>')
                elif inner in ('K', 'k', '⨯', 'x', 'X', '\uE02D'):
                    modifiers_html.append('<span class="swara-mod mod-k" title="MOD-K: Shoulder Cross Mark (⨯)">&#xE02D;</span>')
                elif inner in ('B', 'b', '^', '\uE005'):
                    has_mod_b = True
                elif inner in ('E', 'e', '┃', '\uE002'):
                    modifiers_html.append('<span class="swara-mod mod-e" title="MOD-E: Bold Tone Column (┃)">&#xE002;</span>')
                elif inner in ('F', 'f', '╷', '\uE008'):
                    modifiers_html.append('<span class="swara-mod mod-f" title="MOD-F: Danda with Overhead Dot (╷)">&#xE008;</span>')
                elif inner == '_':
                    modifiers_html.append('<span class="swara-mod mod-under" title="MOD-UNDERBAR">_</span>')
                elif inner == ',':
                    modifiers_html.append('<span class="swara-mod mod-comma" title="MOD-COMMA">,</span>')
                elif inner == '.':
                    modifiers_html.append('<span class="swara-mod mod-dot" title="MOD-DOT">.</span>')
                else:
                    swara_letter = SWARA_CANONICAL_MAP.get(inner, inner)
            
            mods_str = ''.join(modifiers_html)
            syllables = split_malayalam_syllables(base) if base else []
            last_syl = syllables.pop() if syllables else ''
            
            for syl in syllables:
                word_html.append(f'<span class="akshara-base">{syl}</span>')
            
            if has_mod_b:
                caret_group = f'<span class="swara-mod mod-b"><span class="caret-glyph">&#xE005;</span><span class="swara-on-caret">{swara_letter}</span></span>'
                word_html.append(f'<span class="akshara-base">{last_syl}{mods_str}{caret_group}</span>')
            elif swara_letter and last_syl:
                word_html.append(f'<ruby class="vedic-ruby"><rb class="akshara-base">{last_syl}{mods_str}</rb><rt class="swara-above">{swara_letter}</rt></ruby>')
            elif swara_letter and not last_syl:
                word_html.append(f'<ruby class="vedic-ruby"><rb class="akshara-base">&nbsp;{mods_str}</rb><rt class="swara-above">{swara_letter}</rt></ruby>')
            elif last_syl or mods_str:
                word_html.append(f'<span class="akshara-base">{last_syl}{mods_str}</span>')
        
        html_parts.append(f'<span class="mantra-word">{"".join(word_html) or token}</span>')
    
    return ''.join(html_parts)


def format_malayalam_samam_html(subsection, subsection_title, include_metadata=True,
                                 footnote_counter=0, footnotes_accumulator=None, seen_content_map=None, subsection_key=None):
    """
    Format Malayalam Samam content as semantic HTML with clean Grantha swara stacking,
    identically matching the visual output of the Curation Tool.
    """
    formatted_output = []
    collected_footnotes = []
    seen_markers_map = seen_content_map if seen_content_map is not None else {}
    footnote_data = subsection.get('footnotes', {})
    
    # 1. Header
    display_sub_title = re.sub(r'^([|॥]+)\s*', r'\1 ', subsection_title) if subsection_title else ''
    saman_metadata = subsection.get('saman_metadata', '') if include_metadata else ''
    
    header_parts = []
    if display_sub_title:
        header_title = escape_for_html(display_sub_title)
        header_title = format_dandas_html(header_title)
        header_parts.append(f'<span class="header-title">{header_title}</span>')
    if saman_metadata:
        meta = escape_for_html(saman_metadata)
        meta = format_dandas_html(meta, preserve_spaces=True)
        meta, fnotes, footnote_counter = process_footnotes_html(meta, footnote_data, footnote_counter, seen_markers_map, subsection_key)
        collected_footnotes.extend(fnotes)
        header_parts.append(f'<span class="header-meta">{meta}</span>')
        
    if header_parts:
        formatted_output.append(f'<div class="subsection-header">{" &nbsp; ".join(header_parts)}</div>')
        
    # 2. Mantra verses
    mantra_array = []
    mantra_sets = subsection.get('malayalam-mantra-sets', [])
    if not mantra_sets:
        mantra_sets = subsection.get('corrected-mantra_sets', [])
    if not mantra_sets:
        mantra_sets = subsection.get('mantra_sets', [])

    for mset in mantra_sets:
        m = mset.get('malayalam-mantra') or mset.get('corrected-mantra') or mset.get('mantra', '')
        if m:
            mantra_array.append(m)
        elif mset.get('mantra-words'):
            words = []
            for word_dict in mset.get('mantra-words', []):
                w = word_dict.get('word', '')
                sw = word_dict.get('swara', '')
                if sw:
                    words.append(f"{w}({sw})")
                else:
                    words.append(w)
            if words:
                mantra_array.append(" ".join(words))

    for mantra_line in mantra_array:
        clean_mantra = mantra_line.replace('\\newline%', ' ').replace('\\newline', ' ').replace('ർ', '൪').replace('ര്', '൪')
        clean_mantra, fnotes, footnote_counter = process_footnotes_html(clean_mantra, footnote_data, footnote_counter, seen_markers_map, subsection_key)
        collected_footnotes.extend(fnotes)
        
        verse_parts = re.split(r'(॥\s*[\d०-९]+\s*॥)', clean_mantra)
        
        for idx_v in range(0, len(verse_parts), 2):
            v_text = verse_parts[idx_v].strip()
            v_marker = verse_parts[idx_v + 1] if idx_v + 1 < len(verse_parts) else ''
            
            if not v_text and not v_marker:
                continue
                
            v_html = render_vedic_html_from_line(v_text)
            if v_marker:
                num_m = re.search(r'[\d०-९]+', v_marker)
                v_num = num_m.group(0).translate(_ENGLISH_DIGITS) if num_m else ''
                v_marker_html = f'<span class="mantra-word verse-num-word"><span class="mantra-text verse-num-marker"><span class="danda">॥</span><span class="verse-num">{v_num}</span><span class="danda">॥</span></span><span class="swara-text">&nbsp;</span></span>'
                formatted_output.append(f'<div class="mantra-verse">{v_html} {v_marker_html}</div>')
            elif v_html:
                formatted_output.append(f'<div class="mantra-verse">{v_html}</div>')

    if collected_footnotes and footnotes_accumulator is not None:
        footnotes_accumulator.extend(collected_footnotes)

    return '\n'.join(formatted_output), footnote_counter


def preprocess_html_data(supersections, output_mode='combined', script='devanagari', with_modifiers=True):
    """
    Pre-processes all subsection content for HTML template rendering.
    """
    index_entries = []
    
    for super_key, supersection in supersections.items():
        for section_key, section in supersection.get('sections', {}).items():
            if section_key == 'count': continue
            
            # --- SECTION STATE ---
            footnote_counter = 0
            footnotes_accumulator = []
            seen_content_map = {}
            
            section['html_subsections'] = [] # List of HTML strings
            
            prev_rik_id = None
            
            for subsection_key, subsection in section.get('subsections', {}).items():
                unique_key = f"{super_key}_{section_key}_{subsection_key}"
                is_malayalam = (script == 'malayalam')
                
                # Dispatch based on mode
                html_content = ""
                if output_mode == 'rik':
                    html_content, footnote_counter = format_rik_only_html(
                        subsection, None, None, subsection.get('header', {}).get('header'), {}, 
                        prev_rik_id, unique_key, 
                        footnote_counter, footnotes_accumulator, seen_content_map
                    )
                elif output_mode == 'rik_nometa':
                    html_content, footnote_counter = format_rik_nometa_html(
                        subsection, None, None, subsection.get('header', {}).get('header'), {}, 
                        prev_rik_id, unique_key, 
                        footnote_counter, footnotes_accumulator, seen_content_map
                    )
                elif output_mode == 'samam':
                    if is_malayalam:
                        html_content, footnote_counter = format_malayalam_samam_html(
                            subsection, subsection.get('header', {}).get('header', ''), include_metadata=True,
                            footnote_counter=footnote_counter, footnotes_accumulator=footnotes_accumulator,
                            seen_content_map=seen_content_map, subsection_key=unique_key
                        )
                    else:
                        html_content, footnote_counter = format_samam_only_html(
                            subsection, None, None, subsection.get('header', {}).get('header'), {}, 
                            prev_rik_id, unique_key, 
                            footnote_counter, footnotes_accumulator, seen_content_map,
                            with_modifiers=with_modifiers
                        )
                elif output_mode == 'samam_nometa':
                    if is_malayalam:
                        html_content, footnote_counter = format_malayalam_samam_html(
                            subsection, subsection.get('header', {}).get('header', ''), include_metadata=False,
                            footnote_counter=footnote_counter, footnotes_accumulator=footnotes_accumulator,
                            seen_content_map=seen_content_map, subsection_key=unique_key
                        )
                    else:
                        html_content, footnote_counter = format_samam_nometa_html(
                            subsection, None, None, subsection.get('header', {}).get('header'), {}, 
                            prev_rik_id, unique_key, 
                            footnote_counter, footnotes_accumulator, seen_content_map,
                            with_modifiers=with_modifiers
                        )
                else:
                    if is_malayalam:
                        r_html = ""
                        if subsection.get('rik_text') or subsection.get('rik_metadata'):
                            r_html, footnote_counter = format_rik_only_html(
                                subsection, None, None, subsection.get('header', {}).get('header'), {}, 
                                prev_rik_id, unique_key, 
                                footnote_counter, footnotes_accumulator, seen_content_map
                            )
                        s_html, footnote_counter = format_malayalam_samam_html(
                            subsection, subsection.get('header', {}).get('header', ''), include_metadata=True,
                            footnote_counter=footnote_counter, footnotes_accumulator=footnotes_accumulator,
                            seen_content_map=seen_content_map, subsection_key=unique_key
                        )
                        html_content = f"{r_html}\n{s_html}" if r_html else s_html
                    else:
                        html_content, footnote_counter = format_mantra_sets_html(
                            subsection, None, None, subsection.get('header', {}).get('header'), {}, 
                            prev_rik_id, unique_key, 
                            footnote_counter, footnotes_accumulator, seen_content_map,
                            with_modifiers=with_modifiers
                        )
                
                # INDEX COLLECT
                header = subsection.get('header', {}).get('header', '')
                if header:
                    # Consistent logic with PDF: strip dandas and spaces
                    index_title = re.sub(r'[|॥]', '', header).strip()
                    if index_title:
                        # Append to list; we'll deduplicate by adding disambiguation if needed
                        index_entries.append({
                            'title': index_title,
                            'anchor': f"{super_key}-{section_key}-{subsection_key}"
                        })

                section['html_subsections'].append({
                    'id': f"{super_key}-{section_key}-{subsection_key}",
                    'content': html_content
                })
                
                prev_rik_id = subsection.get('rik_id')
                
            # --- GENERATE FOOTNOTE HTML ---
            # Using the logic from render_section_footnotes but locally
            if footnotes_accumulator:
                 output = ['<hr class="footnote-separator"/>']
                 output.append('<div class="footnote-section">')
                 for unique_id, display_num, text in footnotes_accumulator:
                     output.append(f'<div class="footnote-item" id="{unique_id}"><sup class="footnote-ref">{display_num}</sup> {text}</div>')
                 output.append('</div>')
                 section['html_footer'] = '\n'.join(output)
            else:
                 section['html_footer'] = ""

    # Deduplicate and sort index alphabetically
    # To properly sort devanagari we can just use python sorted, it works decently.
    # Group by title to remove duplicates pointing to different anchors (or keep them?)
    # Usually index groups by title and lists pages. For HTML we'll just link to the first occurrence
    unique_index = {}
    title_counts = {}
    
    # Sort by anchor to maintain document order before deduplication/suffixing
    index_entries.sort(key=lambda x: x['anchor'])
    
    for entry in index_entries:
        title = entry['title']
        if title in unique_index:
            # Duplicate title found! Add a numeric suffix to make it unique in the index
            title_counts[title] = title_counts.get(title, 1) + 1
            unique_title = f"{title} ({title_counts[title]})"
            unique_index[unique_title] = entry['anchor']
        else:
            unique_index[title] = entry['anchor']
            title_counts[title] = 1
            
    # Sorted list for template
    sorted_index = []
    for title in sorted(unique_index.keys()):
        sorted_index.append({
            'title': title,
            'anchor': unique_index[title]
        })
    
    return sorted_index


def clean_toc_title(raw_title):
    """
    Cleans the raw subsection title to extract just the first block of text 
    wrapped in dandas (e.g., extracting just the Samam header and removing metadata).
    """
    if not raw_title: return ""
    display_sub_title = re.sub(r'^([|॥]+)\s*', r'\1 ', raw_title)
    m_split = re.match(r'([|॥]+\s*.*?[|॥]+)', display_sub_title)
    if m_split:
        return m_split.group(1).strip()
    return display_sub_title.strip()



def CreateHtmlFile(templateFileName, name, DocfamilyName, data, html_font="'AdishilaVedic', 'AdishilaSanVedic'", output_mode="combined", doc_title_sa="जैमिनीय साम संहिता", closing_mantras=None, summary_table=None, total_riks=None, total_samams=None, summary_title="संहिता सङ्ख्या", toc_level='section', has_riks=True, has_samams=True, output_dir_override=None, name_override=None, jsv_version=None, generated_at=None, script='devanagari', with_modifiers=True, kpully=False):
    """
    Creates an HTML file from the template and data.
    Similar to CreatePdf but outputs HTML instead.
    
    Args:
        html_font: Font family string for HTML output (e.g., "'AdishilaVedic', 'AdishilaSanVedic'")
        output_mode: 'combined', 'rik', or 'samam' for filtering content
        doc_title_sa: Sanskrit title for the document
        closing_mantras: List of closing mantra lines to render at the end
    """
    outputdir = "data/output"
    exit_code = 0
    
    # Malayalam script mode has no HTML template yet; skip gracefully
    if templateFileName is None:
        return
    
    # Use overrides if provided
    name = name_override or name
    outputdir = output_dir_override or f"{outputdir}/html/{DocfamilyName}"
    
    HtmlFileName = f"{name}_{DocfamilyName}.html"
    template = templateFileName
    Path(outputdir).mkdir(parents=True, exist_ok=True)
    
    global HTML_FOOTNOTE_COUNTER
    HTML_FOOTNOTE_COUNTER = 0 # Not used in pre-process mode but kept for safety
    
    # PRE-PROCESS DATA
    html_index = preprocess_html_data(data, output_mode, script=script, with_modifiers=with_modifiers)
    
    if not jsv_version or not generated_at:
        from utils import get_generated_metadata
        meta = get_generated_metadata()
        jsv_version = jsv_version or meta['version']
        generated_at = generated_at or meta['generated_at']
    
    import base64
    jaimineeya_swara_b64 = ""
    font_file = Path("fonts/JaimineeyaSwara.ttf")
    if font_file.exists():
        with open(font_file, "rb") as f_font:
            jaimineeya_swara_b64 = base64.b64encode(f_font.read()).decode("ascii")
    
    document = template.render(
        supersections=data, 
        html_font=html_font, 
        output_mode=output_mode,
        doc_title_sa=doc_title_sa,
        version=jsv_version,
        generated_at=generated_at,
        html_index=html_index,
        closing_mantras=closing_mantras or [],
        summary_table=summary_table,
        total_riks=total_riks,
        total_samams=total_samams,
        summary_title=summary_title,
        toc_level=toc_level,
        has_riks=has_riks,
        has_samams=has_samams,
        jaimineeya_swara_b64=jaimineeya_swara_b64,
        kpully=kpully
    )
    
    output_path = Path(f"{outputdir}/{HtmlFileName}")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(document)
    
    print(f"HTML file created: {output_path}")
    
    # Auto-sync to data/output/html/<script>/
    try:
        script_dir = "Malayalam" if script == 'malayalam' else "Devanagari"
        sync_dir = Path("data/output/html") / script_dir
        sync_dir.mkdir(parents=True, exist_ok=True)
        import shutil
        shutil.copy2(output_path, sync_dir / HtmlFileName)
        # Also sync base name without redundant script suffix if present
        clean_name = HtmlFileName.replace('_Devanagari.html', '.html').replace('_Malayalam.html', '.html')
        if clean_name != HtmlFileName:
            shutil.copy2(output_path, sync_dir / clean_name)
    except Exception:
        pass

    return exit_code


def main():
    # Force UTF-8 encoding for console output
    if sys.stdout.encoding.lower() != 'utf-8':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    
    # 0. Load Configuration from centralized pipeline_config.yaml
    pipeline_cfg = load_pipeline_config()
    config = pipeline_cfg.get('render', {})
    
    cfg_defaults = config.get('defaults', {})
    cfg_types = config.get('types', {})
    cfg_paths = config.get('paths', {})

    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Generate PDF, HTML, and Text from Vedic text JSON',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Output Modes:
  combined  - Single output with both Rik and Samam content (default)
  separate  - Two separate outputs: Rik-only and Samam-only (with metadata)
  nometa    - Two separate outputs: Rik-only and Samam-only (without metadata)

Examples:
  python renderPDF.py input.json
  python renderPDF.py input.json --output-mode separate
  python renderPDF.py input.json --output-mode nometa
        """
    )
    parser.add_argument('input_file', nargs='?', default=None,
                        help='Input JSON file (auto-selected based on --type if not specified)')
    parser.add_argument('--output-mode', dest='output_mode',
                        choices=['combined', 'separate', 'nometa'], default=None,
                        help='Output mode: combined (default), separate, or nometa')
    parser.add_argument('--pdf-font', dest='pdf_font', default=None,
                        help='Font for PDF output')
    parser.add_argument('--html-font', dest='html_font', default=None,
                        help="Font for HTML output")
    parser.add_argument('--type', choices=['samhita', 'aaranam', 'collection'], default='samhita',
                        help='Type of Samaveda text: samhita, aaranam, or collection')
    
    parser.add_argument('--script', dest='script',
                        choices=['devanagari', 'malayalam'], default='devanagari',
                        help='Rendering script: devanagari (default) or malayalam (Phase 1 Samam-only pilot)')
    
    # CLI OPTION for Swara Modifiers in Devanagari
    parser.add_argument('--swara-modifiers', dest='swara_modifiers', action='store_true', default=True,
                        help='Include swara modifiers in Devanagari (default: True)')
    parser.add_argument('--no-swara-modifiers', dest='swara_modifiers', action='store_false',
                        help='Exclude swara modifiers in Devanagari')
    
    # CLI OPTION for Kodunthirapully variant (swaras below mantra text)
    parser.add_argument('-kpully', '--kpully', dest='kpully', action='store_true', default=False,
                        help='Render Devanagari with swara markings stacked below the mantra text (Kodunthirapully paddhati)')
    
    # Color Mode Option (Defaults to color for rich Vedic rendering)
    parser.add_argument('--pdf-color-mode', dest='pdf_color_mode',
                        choices=['bw', 'color'], default='color',
                        help='Color mode for PDF output: color (default) or bw')
                        
    parser.add_argument('--toc-level', dest='toc_level',
                        choices=['section', 'subsection', 'both'], default=None,
                        help='Determines which headers appear in the TOC.')
    
    parser.add_argument('--title', dest='title', default=None,
                        help='Custom Sanskrit title for the document.')
    
    parser.add_argument('--output', '-o', dest='output', default=None,
                        help='Override the default output basename or specify a full output path.')
    
    # Target format filters
    parser.add_argument('--html-only', dest='html_only', action='store_true', default=False,
                        help='Generate only HTML output (skips PDF and text generation)')
    parser.add_argument('--pdf-only', dest='pdf_only', action='store_true', default=False,
                        help='Generate only PDF output (skips HTML and text generation)')
    parser.add_argument('--txt-only', dest='txt_only', action='store_true', default=False,
                        help='Generate only Text output (skips PDF and HTML generation)')
    parser.add_argument('--samam-only', dest='samam_only', action='store_true', default=False,
                        help='Generate only Samam output (skips Rik output in separate/nometa modes)')
    parser.add_argument('--rik-only', dest='rik_only', action='store_true', default=False,
                        help='Generate only Rik output (skips Samam output in separate/nometa modes)')
    
    args = parser.parse_args()
    mode_type = args.type
    type_settings = cfg_types.get(mode_type, {})

    # Priority Merging: CLI > Config Type > Config Default > Hardcoded fallback
    output_mode = args.output_mode or type_settings.get('output_mode') or cfg_defaults.get('output_mode', 'combined')
    pdf_font = args.pdf_font or type_settings.get('pdf_font') or cfg_defaults.get('pdf_font', 'AdishilaVedic')
    html_font = args.html_font or type_settings.get('html_font') or cfg_defaults.get('html_font', "'AdishilaVedic', 'AdishilaSanVedic'")
    pdf_color_mode = args.pdf_color_mode or type_settings.get('pdf_color_mode') or 'color'
    toc_level = args.toc_level or type_settings.get('toc_level') or cfg_defaults.get('toc_level', 'section')
    
    kpully_mode = args.kpully or type_settings.get('kpully') or cfg_defaults.get('kpully', False)
    
    global CURRENT_PDF_FONT
    CURRENT_PDF_FONT = pdf_font
    global CURRENT_TOC_LEVEL
    CURRENT_TOC_LEVEL = toc_level
    global CURRENT_WITH_SWARA_MODIFIERS
    CURRENT_WITH_SWARA_MODIFIERS = args.swara_modifiers
    global CURRENT_KPULLY_MODE
    CURRENT_KPULLY_MODE = kpully_mode
    
    # Target format dispatch flags
    gen_pdf = not (args.html_only or args.txt_only)
    gen_txt = not (args.html_only or args.pdf_only)
    gen_html = not (args.pdf_only or args.txt_only)
    gen_rik = not args.samam_only
    gen_samam = not args.rik_only
    
    # Handle output path overrides
    out_dir = None
    out_name = None
    if args.output:
        out_path = Path(args.output)
        if args.output.endswith('/') or args.output.endswith('\\') or out_path.is_dir():
            out_dir = str(out_path)
            out_name = None
        else:
            out_dir = str(out_path.parent) if str(out_path.parent) != '.' else None
            out_name = out_path.name
    
    # Auto-select default input file
    input_file = args.input_file or type_settings.get('input_file')
    if not input_file:
         # Fallback to historical hardcoded defaults
         if mode_type == 'aaranam':
             input_file = 'data/output/Aaranam_latest_out.json'
         elif mode_type == 'collection':
             input_file = 'data/output/Collection_latest_out.json'
         else:
             input_file = 'data/output/Agneyam-Pavamanam_latest_out.json'
    
    file_prefix = type_settings.get('file_prefix') or (
        "Aaranam" if mode_type == 'aaranam' else 
        "Collection" if mode_type == 'collection' else "Samhita"
    )

    # Path configuration
    tpl_paths = cfg_paths.get('templates', {})
    template_dir = tpl_paths.get('pdf', "templates/pdf")
    text_template_dir = tpl_paths.get('text', "templates/text")
    html_template_dir = tpl_paths.get('html', "templates/html")
    
    templateFile_Grantha = f"{template_dir}/Grantha_main.template"
    templateFile_Devanagari = f"{template_dir}/Devanagari_main.template"
    templateFile_Tamil = f"{template_dir}/Tamil_main.template"
    templateFile_Malayalam = f"{template_dir}/Malayalam_main.template"
    
    text_templateFile_Devanagari = f"{text_template_dir}/Devanagari_main.template"
    html_templateFile_Devanagari = f"{html_template_dir}/Devanagari_main_html.template"

    outputdir = cfg_paths.get('output_root', "data/output")
    logdir = cfg_paths.get('logs', "data/output/logs")
    
    # LaTeX/Text Jinja environment (uses LaTeX-style delimiters)
    latex_jinja_env = jinja2.Environment(
    block_start_string = r'\BLOCK{',
    block_end_string = '}',
    variable_start_string = r'\VAR{',
    variable_end_string = '}',
    comment_start_string = r'\#{',
    comment_end_string = '}',
    line_statement_prefix = '%-',
    line_comment_prefix = '%#',
    trim_blocks = True,
    lstrip_blocks=True,
    autoescape = False,
    loader = jinja2.FileSystemLoader(os.path.abspath('.')),
    extensions=['jinja2.ext.loopcontrols']
    )
    latex_jinja_env.filters["my_encodeURL"] = my_encodeURL
    latex_jinja_env.filters["escape_for_latex"] = escape_for_latex
    latex_jinja_env.filters["replace_footnotes"] = replace_footnote_markers_filter
    latex_jinja_env.filters["format_mantra_sets_text"] = format_mantra_sets_text
    latex_jinja_env.filters["format_mantra_sets"] = format_mantra_sets
    latex_jinja_env.filters["format_rik_only"] = format_rik_only
    latex_jinja_env.filters["format_samam_only"] = format_samam_only
    latex_jinja_env.filters["format_rik_only_text"] = format_rik_only_text
    latex_jinja_env.filters["format_samam_only_text"] = format_samam_only_text
    latex_jinja_env.filters["format_rik_nometa"] = format_rik_nometa
    latex_jinja_env.filters["format_samam_nometa"] = format_samam_nometa
    latex_jinja_env.filters["format_rik_nometa_text"] = format_rik_nometa_text
    latex_jinja_env.filters["format_malayalam_rik_only"] = format_malayalam_rik_only
    latex_jinja_env.filters["format_malayalam_rik_nometa"] = format_malayalam_rik_nometa
    latex_jinja_env.filters["format_malayalam_samam_only"] = format_malayalam_samam_only
    latex_jinja_env.filters["format_malayalam_samam_nometa"] = format_malayalam_samam_nometa
    latex_jinja_env.filters["format_malayalam_combined"] = format_malayalam_combined
    latex_jinja_env.filters["format_malayalam_samam"] = format_malayalam_samam
    latex_jinja_env.filters["format_malayalam_samam_text"] = format_malayalam_samam_text
    latex_jinja_env.filters["format_samam_nometa_text"] = format_samam_nometa_text
    latex_jinja_env.filters["split_rik_lines"] = split_rik_lines_text
    latex_jinja_env.filters["replacecolon"] = replacecolon
    latex_jinja_env.filters["clean_toc_title"] = clean_toc_title
    
    # HTML Jinja environment (uses same LaTeX-style delimiters for consistency)
    html_jinja_env = jinja2.Environment(
    block_start_string = r'\BLOCK{',
    block_end_string = '}',
    variable_start_string = r'\VAR{',
    variable_end_string = '}',
    comment_start_string = r'\#{',
    comment_end_string = '}',
    line_statement_prefix = '%-',
    line_comment_prefix = '%#',
    trim_blocks = True,
    lstrip_blocks=True,
    autoescape = False,
    loader = jinja2.FileSystemLoader(os.path.abspath('.')),
    extensions=['jinja2.ext.loopcontrols']
    )
    html_jinja_env.filters["format_mantra_sets_html"] = format_mantra_sets_html
    html_jinja_env.filters["format_rik_only_html"] = format_rik_only_html
    html_jinja_env.filters["format_samam_only_html"] = format_samam_only_html
    html_jinja_env.filters["format_rik_nometa_html"] = format_rik_nometa_html
    html_jinja_env.filters["format_samam_nometa_html"] = format_samam_nometa_html
    html_jinja_env.filters["escape_for_html"] = escape_for_html
    html_jinja_env.filters["replacecolon"] = replacecolon
    html_jinja_env.filters["reset_html_footnote_counter"] = reset_html_footnote_counter
    html_jinja_env.filters["render_section_footnotes"] = render_section_footnotes
    html_jinja_env.filters["clean_toc_title"] = clean_toc_title

    # Load input JSON data
    ts_string_Devanagari = Path(input_file).read_text(encoding="utf-8")
    data_Devanagari = json.loads(ts_string_Devanagari)
    
    # Extract metadata for cascading versioning
    meta = data_Devanagari.get('meta', {})
    jsv_version = meta.get('version')
    # Use actual generation time instead of cascading from JSON
    generated_at = get_generated_metadata()['generated_at']
    if jsv_version:
        print(f"[INFO] Using cascading Version {jsv_version} (Final Generation: {generated_at})")
    
    # --- MALAYALAM SCRIPT MODE (Phase 1 Samam-only pilot) ---
    script = args.script
    if script == 'malayalam':
        from malayalam.ml_text import transform_ast
        from malayalam.ml_transliterate import devanagari_to_malayalam
        data_Devanagari, ml_warnings, ml_stats = transform_ast(data_Devanagari)
        print(f"[INFO] Malayalam script mode: Full Samhita "
              f"({ml_stats['marked_words']} marked words, {len(ml_warnings)} warnings)")
        # Transliterate supersection and section titles to Malayalam
        for ss_key, ss_data in data_Devanagari.get('supersection', {}).items():
            if ss_data.get('supersection_title'):
                try:
                    ss_data['supersection_title'] = devanagari_to_malayalam(ss_data['supersection_title'])
                except Exception:
                    pass
            for sec_key, sec_data in ss_data.get('sections', {}).items():
                if sec_key != 'count' and sec_data.get('section_title'):
                    try:
                        sec_data['section_title'] = devanagari_to_malayalam(sec_data['section_title'])
                    except Exception:
                        pass

    supersections = data_Devanagari.get('supersections', data_Devanagari.get('supersection', {}))
    supersections = sanitize_data_structure(supersections)
    closing_mantras = data_Devanagari.get('closing-mantras', data_Devanagari.get('closing_mantras', []))
    
    # Generate Summary Table
    summary_table = []
    total_riks = 0
    total_samams = 0
    
    for ss_key, ss_data in supersections.items():
        if ss_key == 'count': continue
        patha_name = ss_data.get('supersection_title', ss_key).replace('॥', '').strip()
        patha_riks = 0
        patha_samams = 0
        khanda_rows = []
        for sec_key, sec_data in ss_data.get('sections', {}).items():
            if sec_key == 'count': continue
            khanda_name = sec_data.get('section_title', sec_key).replace('॥', '').replace(':', 'ः').strip()
            
            seen_riks = set()
            samam_count = 0
            
            # Smart count: only count if displayable text exists
            for sub_key, sub_data in sec_data.get('subsections', {}).items():
                rik_text = sub_data.get('rik_text', '').strip()
                rik_ids = sub_data.get('rik_ids', [])
                
                # Only count Rik if there is Rik text to display
                if rik_text:
                    if rik_ids:
                        seen_riks.update(rik_ids)
                    else:
                        r_id = sub_data.get('rik_id')
                        if r_id is not None:
                            seen_riks.add(r_id)
                
                # Samam count logic
                sub_samam_count = 0
                has_samam_text = False
                for ms in sub_data.get('corrected-mantra_sets', []):
                    mantra = ms.get('corrected-mantra', '')
                    if mantra.strip():
                        has_samam_text = True
                    # Count all ॥ N ॥ markers
                    m_markers = re.findall(r'॥\s*[०-९\d]+\s*॥', mantra)
                    if m_markers:
                        sub_samam_count += len(m_markers)
                
                # If no markers found but mantra sets exist, count as 1 if there's text
                if sub_samam_count == 0 and has_samam_text:
                    sub_samam_count = 1
                
                samam_count += sub_samam_count
                    
            # Total aggregation format for section headers
            sec_riks = len(seen_riks)
            
            # Summary table row generation
            if sec_riks > 0 or samam_count > 0:
                if khanda_name:
                    khanda_rows.append({
                        'khanda': khanda_name,
                        'riks': to_devanagari_numeral(sec_riks),
                        'samams': to_devanagari_numeral(samam_count)
                    })
                patha_riks += sec_riks
                patha_samams += samam_count
                total_riks += sec_riks
                total_samams += samam_count

            count_parts = []
            if script == 'malayalam':
                if sec_riks > 0 and samam_count > 0:
                    count_parts.append(f"ऋ-{sec_riks}")
                    count_parts.append(f"സാ-{samam_count}")
                elif sec_riks > 0:
                    count_parts.append(str(sec_riks))
                elif samam_count > 0:
                    count_parts.append(str(samam_count))
                else:
                    count_parts.append("0")
            else:
                if sec_riks > 0 and samam_count > 0:
                    count_parts.append(f"ऋ-{to_devanagari_numeral(sec_riks)}")
                    count_parts.append(f"सा-{to_devanagari_numeral(samam_count)}")
                elif sec_riks > 0:
                    count_parts.append(to_devanagari_numeral(sec_riks))
                elif samam_count > 0:
                    count_parts.append(to_devanagari_numeral(samam_count))
                else:
                    count_parts.append("०")
            
            sec_data['Count'] = ", ".join(count_parts) if khanda_name else ""
        
        # Add total count for the supersection using similar combined logic
        ss_count_parts = []
        if script == 'malayalam':
            if patha_riks > 0 and patha_samams > 0:
                ss_count_parts.append(f"ऋ-{patha_riks}")
                ss_count_parts.append(f"സാ-{patha_samams}")
            elif patha_riks > 0:
                ss_count_parts.append(str(patha_riks))
            else:
                ss_count_parts.append(str(patha_samams))
        else:
            if patha_riks > 0 and patha_samams > 0:
                ss_count_parts.append(f"ऋ-{to_devanagari_numeral(patha_riks)}")
                ss_count_parts.append(f"सा-{to_devanagari_numeral(patha_samams)}")
            elif patha_riks > 0:
                ss_count_parts.append(to_devanagari_numeral(patha_riks))
            else:
                ss_count_parts.append(to_devanagari_numeral(patha_samams))
            
        ss_data['Count'] = ", ".join(ss_count_parts)
        
        if khanda_rows:
            summary_table.append({
                'patha': patha_name,
                'patha_riks': to_devanagari_numeral(patha_riks),
                'patha_samams': to_devanagari_numeral(patha_samams),
                'khandas': khanda_rows
            })
                
    total_riks_dev = to_devanagari_numeral(total_riks)
    total_samams_dev = to_devanagari_numeral(total_samams)
    
    # Define Sanskrit title based on type (for PDF/html generation)
    # Priority: CLI > Config Type > JSON Meta > Default
    doc_title_sa = args.title or type_settings.get('doc_title')
    
    if not doc_title_sa:
        doc_title_sa = data_Devanagari.get('meta', {}).get('title')
        
    summary_title_sa = type_settings.get('summary_title')
    
    if not doc_title_sa:
        if mode_type == 'aaranam':
            doc_title_sa = "जैमिनीय साम आरण्य गानम्"
            summary_title_sa = "आरण्यम् सङ्ख्या"
        elif mode_type == 'collection':
            doc_title_sa = "जैमिनीय साम सूक्त माला"
            summary_title_sa = "सूक्तम् सङ्ख्या"
        else:
            doc_title_sa = "जैमिनीय साम संहिता"
            summary_title_sa = "संहिता सङ्ख्या"
    
    current_os = platform.system()

    deva_doc_title_sa = doc_title_sa

    # Malayalam script: transliterate the title on the title page
    if script == 'malayalam' and doc_title_sa:
        from malayalam.ml_transliterate import devanagari_to_malayalam
        try:
            doc_title_sa = devanagari_to_malayalam(doc_title_sa)
        except Exception:
            pass
    
    print(f"Processing {input_file} in '{output_mode}' mode...")
    print(f"Document Title: {doc_title_sa}")
    
    # Procedures are loaded from JSON's procedure_ref field (injected by generate_json.py --procedures)
    # No backward compatibility with prayoga_index.yaml
    prayoga_dir = Path("data/input/prayoga")
    procedures = {}
    
    for super_key, supersection in supersections.items():
        for section_key, section in supersection.get('sections', {}).items():
            if section_key == 'count': continue
            for subsection_key, subsection in section.get('subsections', {}).items():
                # Only include procedures that are explicitly referenced in the JSON
                if subsection.get('procedure_ref'):
                    procedure_ref = subsection['procedure_ref']
                    file_path = procedure_ref.get('file', '')
                    if file_path and file_path not in procedures:
                        full_md_path = prayoga_dir / file_path
                        if full_md_path.exists():
                            with open(full_md_path, 'r', encoding='utf-8') as f:
                                md_content = f.read()
                            if md_content.startswith('---'):
                                parts = md_content.split('---', 2)
                                if len(parts) >= 3:
                                    md_content = parts[2].strip()
                            latex_content = md_content.replace('_', '\\_').replace('&', '\\&').replace('%', '\\%').replace('$', '\\$')
                            latex_content = re.sub(r'(?m)^### (.*?)$', r'\\subsubsection*{\1}', latex_content)
                            latex_content = re.sub(r'(?m)^## (.*?)$', r'\\subsection*{\1}', latex_content)
                            latex_content = re.sub(r'(?m)^# (.*?)$', r'\\section*{\1}', latex_content)
                            latex_content = re.sub(r'\*\*(.*?)\*\*', r'\\textbf{\1}', latex_content)
                            latex_content = re.sub(r'\*(.*?)\*', r'\\textit{\1}', latex_content)
                            latex_content = re.sub(r'(?m)^- (.*?)$', r'$\\bullet$ \1\n\n', latex_content)
                            
                            procedures[file_path] = {
                                'slug': Path(file_path).stem,
                                'title': procedure_ref.get('title', 'विधिः'),
                                'latex_content': latex_content
                            }
    
    prayogas_list = list(procedures.values())

    doc_family = 'Malayalam' if script == 'malayalam' else 'Devanagari'

    # Template selection (Malayalam script uses its own Samam-only templates)
    if script == 'malayalam':
        template_file_src = templateFile_Malayalam
        text_template_file_src = f"{text_template_dir}/Malayalam_main.template"
        html_template_file_src = f"{html_template_dir}/Malayalam_main_html.template"
        pdf_font = "NotoSerifMalayalam"
        html_font = "Noto Serif Malayalam"
    else:
        template_file_src = templateFile_Devanagari
        text_template_file_src = text_templateFile_Devanagari
        html_template_file_src = html_templateFile_Devanagari

    # Dual text generation helper for Malayalam script mode
    deva_text_template_file = latex_jinja_env.get_template(text_templateFile_Devanagari) if script == 'malayalam' else None
    from malayalam.ml_transliterate import convert_malayalam_data_to_devanagari

    if output_mode == 'combined':
        # Default: Combined output (Rik + Samam together)
        template_file = latex_jinja_env.get_template(template_file_src)
        text_template_file = latex_jinja_env.get_template(text_template_file_src)
        html_template_file = html_jinja_env.get_template(html_template_file_src) if html_template_file_src else None
        
        if gen_pdf:
            CreatePdf(template_file, f"{file_prefix}", doc_family, supersections, prayogas=prayogas_list, current_os=current_os, output_mode='combined', font_family=pdf_font, doc_title_sa=doc_title_sa, pdf_color_mode=pdf_color_mode, closing_mantras=closing_mantras, summary_table=summary_table, total_riks=total_riks_dev, total_samams=total_samams_dev, summary_title=summary_title_sa, toc_level=toc_level, has_riks=total_riks > 0, has_samams=total_samams > 0, output_dir_override=out_dir, name_override=out_name, jsv_version=jsv_version, generated_at=generated_at, kpully=kpully_mode)
        if gen_txt:
            CreateTextFile(text_template_file, f"{file_prefix}", doc_family, supersections, output_mode='combined', doc_title_sa=doc_title_sa, closing_mantras=closing_mantras, toc_level=toc_level, output_dir_override=out_dir, name_override=out_name, jsv_version=jsv_version, generated_at=generated_at)
            if script == 'malayalam':
                deva_supersections = convert_malayalam_data_to_devanagari(supersections)
                CreateTextFile(deva_text_template_file, f"{file_prefix}", 'Devanagari', deva_supersections, output_mode='combined', doc_title_sa=deva_doc_title_sa, closing_mantras=closing_mantras, toc_level=toc_level, output_dir_override=out_dir, name_override=out_name, jsv_version=jsv_version, generated_at=generated_at)
        if gen_html:
            CreateHtmlFile(html_template_file, f"{file_prefix}", doc_family, supersections, html_font=html_font, output_mode='combined', doc_title_sa=doc_title_sa, closing_mantras=closing_mantras, summary_table=summary_table, total_riks=total_riks_dev, total_samams=total_samams_dev, summary_title=summary_title_sa, toc_level=toc_level, has_riks=total_riks > 0, has_samams=total_samams > 0, output_dir_override=out_dir, name_override=out_name, jsv_version=jsv_version, generated_at=generated_at, script=script, with_modifiers=args.swara_modifiers, kpully=kpully_mode)
        print("Success! Generated combined output files.")
        
    elif output_mode == 'separate':
        # Separate mode: Generate Rik-only and Samam-only files (with metadata, jsv_version=jsv_version, generated_at=generated_at)
        template_file = latex_jinja_env.get_template(template_file_src)
        text_template_file = latex_jinja_env.get_template(text_template_file_src)
        html_template_file = html_jinja_env.get_template(html_template_file_src) if html_template_file_src else None
        
        # Rik-only output: Pass output_mode='rik' to template
        if gen_rik:
            print("Generating Rik-only output (with metadata)...")
            final_out_name = f"{out_name}_Rik" if out_name else "Rik"
            if gen_pdf:
                CreatePdf(template_file, f"Rik", doc_family, supersections, prayogas=prayogas_list, current_os=current_os, output_mode='rik', font_family=pdf_font, doc_title_sa=doc_title_sa, pdf_color_mode=pdf_color_mode, closing_mantras=closing_mantras, summary_table=summary_table, total_riks=total_riks_dev, total_samams=total_samams_dev, summary_title=summary_title_sa, toc_level=toc_level, has_riks=total_riks > 0, has_samams=total_samams > 0, output_dir_override=out_dir, name_override=final_out_name, jsv_version=jsv_version, generated_at=generated_at, kpully=kpully_mode)
            if gen_txt:
                CreateTextFile(text_template_file, f"Rik", doc_family, supersections, output_mode='rik', doc_title_sa=doc_title_sa, closing_mantras=closing_mantras, toc_level=toc_level, output_dir_override=out_dir, name_override=final_out_name, jsv_version=jsv_version, generated_at=generated_at)
                if script == 'malayalam':
                    deva_supersections = convert_malayalam_data_to_devanagari(supersections)
                    CreateTextFile(deva_text_template_file, f"Rik", 'Devanagari', deva_supersections, output_mode='rik', doc_title_sa=deva_doc_title_sa, closing_mantras=closing_mantras, toc_level=toc_level, output_dir_override=out_dir, name_override=final_out_name, jsv_version=jsv_version, generated_at=generated_at)
            if gen_html:
                CreateHtmlFile(html_template_file, f"Rik", doc_family, supersections, html_font=html_font, output_mode='rik', doc_title_sa=doc_title_sa, closing_mantras=closing_mantras, summary_table=summary_table, total_riks=total_riks_dev, total_samams=total_samams_dev, summary_title=summary_title_sa, toc_level=toc_level, has_riks=total_riks > 0, has_samams=total_samams > 0, output_dir_override=out_dir, name_override=final_out_name, jsv_version=jsv_version, generated_at=generated_at, script=script, with_modifiers=args.swara_modifiers, kpully=kpully_mode)
        
        # Samam-only output: Pass output_mode='samam' to template
        if gen_samam:
            print("Generating Samam-only output (with metadata)...")
            final_out_name = f"{out_name}_Samam" if out_name else "Samam"
            if gen_pdf:
                CreatePdf(template_file, f"Samam", doc_family, supersections, prayogas=prayogas_list, current_os=current_os, output_mode='samam', font_family=pdf_font, doc_title_sa=doc_title_sa, pdf_color_mode=pdf_color_mode, closing_mantras=closing_mantras, summary_table=summary_table, total_riks=total_riks_dev, total_samams=total_samams_dev, summary_title=summary_title_sa, toc_level=toc_level, has_riks=total_riks > 0, has_samams=total_samams > 0, output_dir_override=out_dir, name_override=final_out_name, jsv_version=jsv_version, generated_at=generated_at, kpully=kpully_mode)
            if gen_txt:
                CreateTextFile(text_template_file, f"Samam", doc_family, supersections, output_mode='samam', doc_title_sa=doc_title_sa, closing_mantras=closing_mantras, toc_level=toc_level, output_dir_override=out_dir, name_override=final_out_name, jsv_version=jsv_version, generated_at=generated_at)
                if script == 'malayalam':
                    deva_supersections = convert_malayalam_data_to_devanagari(supersections)
                    CreateTextFile(deva_text_template_file, f"Samam", 'Devanagari', deva_supersections, output_mode='samam', doc_title_sa=deva_doc_title_sa, closing_mantras=closing_mantras, toc_level=toc_level, output_dir_override=out_dir, name_override=final_out_name, jsv_version=jsv_version, generated_at=generated_at)
            if gen_html:
                CreateHtmlFile(html_template_file, f"Samam", doc_family, supersections, html_font=html_font, output_mode='samam', doc_title_sa=doc_title_sa, closing_mantras=closing_mantras, summary_table=summary_table, total_riks=total_riks_dev, total_samams=total_samams_dev, summary_title=summary_title_sa, toc_level=toc_level, has_riks=total_riks > 0, has_samams=total_samams > 0, output_dir_override=out_dir, name_override=final_out_name, jsv_version=jsv_version, generated_at=generated_at, script=script, with_modifiers=args.swara_modifiers, kpully=kpully_mode)
        
        print("Success! Generated separate Rik and Samam output files.")
        
    else:
        # Nometa mode: Generate Rik-only and Samam-only files (without metadata, jsv_version=jsv_version, generated_at=generated_at)
        template_file = latex_jinja_env.get_template(template_file_src)
        text_template_file = latex_jinja_env.get_template(text_template_file_src)
        html_template_file = html_jinja_env.get_template(html_template_file_src) if html_template_file_src else None
        
        # Rik-only output (no metadata, jsv_version=jsv_version, generated_at=generated_at): Pass output_mode='rik_nometa' to template
        if gen_rik:
            print("Generating Rik-only output (without metadata)...")
            final_out_name = f"{out_name}_Rik_NoMeta" if out_name else "Rik_NoMeta"
            if gen_pdf:
                CreatePdf(template_file, f"Rik_NoMeta", doc_family, supersections, current_os=current_os, output_mode='rik_nometa', font_family=pdf_font, doc_title_sa=doc_title_sa, pdf_color_mode=pdf_color_mode, closing_mantras=closing_mantras, summary_table=summary_table, total_riks=total_riks_dev, total_samams=total_samams_dev, summary_title=summary_title_sa, toc_level=toc_level, has_riks=total_riks > 0, has_samams=total_samams > 0, output_dir_override=out_dir, name_override=final_out_name, jsv_version=jsv_version, generated_at=generated_at, kpully=kpully_mode)
            if gen_txt:
                CreateTextFile(text_template_file, f"Rik_NoMeta", doc_family, supersections, output_mode='rik_nometa', doc_title_sa=doc_title_sa, closing_mantras=closing_mantras, toc_level=toc_level, output_dir_override=out_dir, name_override=final_out_name, jsv_version=jsv_version, generated_at=generated_at)
                if script == 'malayalam':
                    deva_supersections = convert_malayalam_data_to_devanagari(supersections)
                    CreateTextFile(deva_text_template_file, f"Rik_NoMeta", 'Devanagari', deva_supersections, output_mode='rik_nometa', doc_title_sa=deva_doc_title_sa, closing_mantras=closing_mantras, toc_level=toc_level, output_dir_override=out_dir, name_override=final_out_name, jsv_version=jsv_version, generated_at=generated_at)
            if gen_html:
                CreateHtmlFile(html_template_file, f"Rik_NoMeta", doc_family, supersections, html_font=html_font, output_mode='rik_nometa', doc_title_sa=doc_title_sa, closing_mantras=closing_mantras, summary_table=summary_table, total_riks=total_riks_dev, total_samams=total_samams_dev, summary_title=summary_title_sa, toc_level=toc_level, has_riks=total_riks > 0, has_samams=total_samams > 0, output_dir_override=out_dir, name_override=final_out_name, jsv_version=jsv_version, generated_at=generated_at, script=script, with_modifiers=args.swara_modifiers, kpully=kpully_mode)
        
        # Samam-only output (no metadata, jsv_version=jsv_version, generated_at=generated_at): Pass output_mode='samam_nometa' to template
        if gen_samam:
            print("Generating Samam-only output (without metadata)...")
            final_out_name = f"{out_name}_Samam_NoMeta" if out_name else "Samam_NoMeta"
            if gen_pdf:
                CreatePdf(template_file, f"Samam_NoMeta", doc_family, supersections, current_os=current_os, output_mode='samam_nometa', font_family=pdf_font, doc_title_sa=doc_title_sa, pdf_color_mode=pdf_color_mode, closing_mantras=closing_mantras, summary_table=summary_table, total_riks=total_riks_dev, total_samams=total_samams_dev, summary_title=summary_title_sa, toc_level=toc_level, has_riks=total_riks > 0, has_samams=total_samams > 0, output_dir_override=out_dir, name_override=final_out_name, jsv_version=jsv_version, generated_at=generated_at, kpully=kpully_mode)
            if gen_txt:
                CreateTextFile(text_template_file, f"Samam_NoMeta", doc_family, supersections, output_mode='samam_nometa', doc_title_sa=doc_title_sa, closing_mantras=closing_mantras, toc_level=toc_level, output_dir_override=out_dir, name_override=final_out_name, jsv_version=jsv_version, generated_at=generated_at)
                if script == 'malayalam':
                    deva_supersections = convert_malayalam_data_to_devanagari(supersections)
                    CreateTextFile(deva_text_template_file, f"Samam_NoMeta", 'Devanagari', deva_supersections, output_mode='samam_nometa', doc_title_sa=deva_doc_title_sa, closing_mantras=closing_mantras, toc_level=toc_level, output_dir_override=out_dir, name_override=final_out_name, jsv_version=jsv_version, generated_at=generated_at)
            if gen_html:
                CreateHtmlFile(html_template_file, f"Samam_NoMeta", doc_family, supersections, html_font=html_font, output_mode='samam_nometa', doc_title_sa=doc_title_sa, closing_mantras=closing_mantras, summary_table=summary_table, total_riks=total_riks_dev, total_samams=total_samams_dev, summary_title=summary_title_sa, toc_level=toc_level, has_riks=total_riks > 0, has_samams=total_samams > 0, output_dir_override=out_dir, name_override=final_out_name, jsv_version=jsv_version, generated_at=generated_at, script=script, with_modifiers=args.swara_modifiers, kpully=kpully_mode)
        
        print("Success! Generated separate Rik and Samam output files without metadata.")

if __name__ == "__main__":
    main()