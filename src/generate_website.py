#!/usr/bin/env python3
"""
Jaimineeya Samavedam Static Website Generator

This script generates a beautiful, modern static website for the Jaimineeya Samavedam
following the Parva → Kandah → Sama hierarchy.

Design Reference: Based on https://hvram1.github.io/rigveda.sanatana.in/sukta/1/1/
Structural Change: Uses JSV hierarchy (NOT Mandala/Sukta):
    - Parva (Top level) - SuperSection in source file (like Mandala)
    - Kandah (Sub-level) - Section in source file (like Sukta)
    - Sama (Verse unit) - SubSection in source file (like Rik/Mantra)

Author: JSV Project
Version: 2.0.0
"""

# --- Path Setup and Imports ---
import os
import re
import json
import sys
import argparse
import markdown
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from collections import defaultdict
from datetime import datetime

# Add current and tools directory to path
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.append(str(current_dir))
tools_dir = current_dir / 'tools'
if tools_dir.exists() and str(tools_dir) not in sys.path:
    sys.path.append(str(tools_dir))

# --- Local Imports ---
try:
    from utils import (
        combine_ardhaksharas,
        get_generated_metadata,
        step_preprocess_visarga_accent,
        parse_mantra_for_latex,
        load_pipeline_config,
        extract_closing_mantras
    )
except ImportError:
    # Fallback/Dummy versions for linting/missing files
    def combine_ardhaksharas(s): return list(s)
    def get_generated_metadata(f): return {}
    def step_preprocess_visarga_accent(s): return s
    def parse_mantra_for_latex(s): return s
    def load_pipeline_config(): return {}

try:
    from render_pdf import (
        replace_accents_html,
        format_dandas_html,
        escape_for_html,
        remove_mantra_spaces,
        handle_consecutive_trikamba_html,
        process_footnotes_html
    )
    HAS_RENDER_IMPORTS = True
except ImportError:
    HAS_RENDER_IMPORTS = False

# Import samam_utils for counting
try:
    from samam_utils import count_samams_with_fallback
except ImportError:
    def count_samams_with_fallback(text): 
        # Very simple fallback: count (1), (2) etc.
        return len(re.findall(r'\(\d+\)', text))

# --- Configuration ---
AUDIO_FILENAME_FORMAT = "JSV_{parva}_{kandah}_{sama}.mp3"

SITE_CONFIG = {
    'samhita': {
        'title_sa': 'जैमिनीय साम संहिता',
        'title_en': 'Jaimineeya Sama Samhita',
        'footer_sa': 'जैमिनीय सामवेद संहिता',
        'meta_desc': 'Jaimineeya Sama Samhita digital archive',
        'keywords': 'Samaveda, Jaimineeya, Samhita, Ganam, Vedas, Sanskrit'
    },
    'aaranam': {
        'title_sa': 'जैमिनीय साम आरण्य गानम्',
        'title_en': 'Jaimineeya Sama Aaranya Ganam', 
        'footer_sa': 'जैमिनीय सामवेद आरण्य गानम्',
        'meta_desc': 'Jaimineeya Sama Aaranam digital archive',
        'keywords': 'Samaveda, Jaimineeya, Aaranam, Aranya, Ganam, Vedas, Sanskrit'
    },
    'collection': {
        'title_sa': 'जैमिनीय साम सङ्ग्रहः',
        'title_en': 'Jaimineeya Sama Sangraha',
        'footer_sa': 'जैमिनीय सामवेद सङ्ग्रहः',
        'meta_desc': 'Jaimineeya Sama Sangraha collection',
        'keywords': 'Samaveda, Jaimineeya, Sangraha, Collection, Vedas, Sanskrit'
    },
    'malayalam': {
        'title_sa': 'ജൈമിനീയ സാമ സംഹിതാ',
        'title_en': 'Jaimineeya Sama Samhita (Malayalam)',
        'footer_sa': 'ജൈമിനീയ സാമവേദ സംഹിതാ',
        'meta_desc': 'Jaimineeya Sama Samhita digital archive in Malayalam script with Grantha swara notations',
        'keywords': 'Samaveda, Jaimineeya, Samhita, Malayalam, Grantha, Swara, Vedas, Sanskrit'
    }
}


# --- Local fallback functions if imports fail ---
def local_escape_for_html(text):
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

def local_replace_accents_html(text):
    """
    Replaces ASCII accent markers with Unicode Vedic accent characters for HTML.
    Uses spans with zero-width positioning for correct display (matching renderPDF.py).
    """
    if not text:
        return text
    
    # Use spans with zero-width CSS positioning (matching the working renderPDF.py output)
    replacements = [
        # Swarita (Vertical line above) - U+0951
        ('(1)', '<span class="accent-swarita">\u0951</span>'),
        # Anudatta (Horizontal line below) - U+1CD2
        ('(2)', '<span class="accent-anudatta">\u1CD2</span>'),
        # Kampa (Curve) - U+1CF8
        ('(3)', '<span class="accent-kampa">\u1CF8</span>'),
        # Trikampa - U+1CF9
        ('(4)', '<span class="accent-trikampa">\u1CF9</span>'),
    ]
    
    for marker, replacement in replacements:
        text = text.replace(marker, replacement)
    
    return text


def local_process_footnotes_html(text, footnotes_dict=None, counter_obj=None, seen_map=None, accumulator=None):
    """
    Process footnotes with global accumulation support.
    """
    if not text:
        return text, []
    
    if footnotes_dict is None:
        footnotes_dict = {}
        
    # Default state if not provided (fallback)
    if counter_obj is None: counter_obj = {'val': 0}
    if seen_map is None: seen_map = {}
    if accumulator is None: accumulator = []
    
    collected_footnotes = [] # Local collection for return (legacy)
    
    # Devanagari digits for footnote references
    devanagari_digits = '०१२३४५६७८९'
    
    def replacer(match):
        marker_num = match.group(1) # '1' from 's1'
        marker_key = f's{marker_num}'
        footnote_text = footnotes_dict.get(marker_key, '').strip()
        
        unique_id = ""
        display_num = ""
        
        if footnote_text and footnote_text in seen_map:
            # Reuse existing footnote
            unique_id, display_num = seen_map[footnote_text]
        else:
            # New footnote
            counter_obj['val'] += 1
            val = counter_obj['val']
            unique_id = f'fn-kandah-{val}'
            display_num = ''.join(devanagari_digits[int(d)] for d in str(val))
            
            if footnote_text:
                seen_map[footnote_text] = (unique_id, display_num)
                accumulator.append((unique_id, display_num, footnote_text))
                collected_footnotes.append((unique_id, val, footnote_text))
        
        # Return superscript link with Devanagari number - NO WHITESPACE before/after
        return f'<sup class="footnote-ref"><a href="#{unique_id}">{display_num}</a></sup>'
    
    # Find all (sN) patterns
    pattern = r'\(s(\d+)\)'
    processed_text = re.sub(pattern, replacer, text)
    
    return processed_text, collected_footnotes

def local_format_dandas_html(text):
    """
    Formats danda symbols for HTML output.
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

    # Clean up extra spaces
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def local_remove_mantra_spaces(text):
    """
    Removes all spaces within the text to create continuous Samhita text.
    """
    if not text:
        return text
    
    # Remove all Unicode whitespace characters
    text = re.sub(r'\s+', '', text)
    text = text.replace('\u00A0', '')  # Non-breaking space
    text = text.replace('\u200B', '')  # Zero-width space
    text = text.replace('\u200C', '')  # Zero-width non-joiner
    text = text.replace('\u200D', '')  # Zero-width joiner
    
    return text

def local_handle_consecutive_trikamba(text):
    """Insert thin space between consecutive trikamba accent marks."""
    if not text:
        return text
    pattern = r'\(4\)([^\(\)]{1,3})\(4\)'
    replacement = r'(4)\1 (4)'
    pattern = r'\(4\)([^\(\)]{1,3})\(4\)'
    replacement = r'(4)\1 (4)'
    return re.sub(pattern, replacement, text)

# Choose functions based on import success
if HAS_RENDER_IMPORTS:
    _escape_html = escape_for_html
    _replace_accents = replace_accents_html
    _format_dandas = format_dandas_html
    _remove_spaces = remove_mantra_spaces
    _handle_trikamba = handle_consecutive_trikamba_html
else:
    _escape_html = local_escape_for_html
    _replace_accents = local_replace_accents_html
    _format_dandas = local_format_dandas_html
    _remove_spaces = local_remove_mantra_spaces
    _handle_trikamba = local_handle_consecutive_trikamba


def split_rik_lines_html(text):
    """
    Splits multi-Rik text so each Rik appears on its own line in HTML.
    Splits after each verse marker (॥ N ॥) and joins with <br>.
    If only one Rik is present, returns the text unchanged.
    """
    if not text:
        return text
    # Split after each ॥ N ॥ pattern (Devanagari or ASCII digits)
    # The marker stays at the end of each segment
    import re
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


def _fix_visarga_accent_with_zwj(text):
    """Swaps Visarga and accent marker so accent applies to preceding vowel."""
    if not text:
        return text
    
    # Normalize colons
    text = text.replace(':', 'ः')
    text = re.sub(r'\s+ः', 'ः', text)
    
    # Always swap Visarga + Accent to Accent + Visarga
    pattern = r'([ः])\s*(\([^)]+\))'
    text = re.sub(pattern, r'\2\1', text)
    
    return text


def format_rik_text_html(rik_text, footnotes_dict=None, counter_obj=None, seen_map=None, accumulator=None):
    """
    Format Rik text for HTML display with proper accent marks.
    Removes spaces (Samhita mode) and converts accent markers to Unicode.
    Also processes footnote markers via accumulator logic.
    Returns: (formatted_text, collected_footnotes)
    """
    if not rik_text:
        return "", []
    
    # Step 1: Remove spaces (Samhita mode)
    text = _remove_spaces(rik_text)
    
    # Step 2: Handle consecutive trikamba
    text = _handle_trikamba(text)
    
    # Step 2a: Fix Visarga-Accent Order with ZWJ for Noto font compatibility
    # text = step_preprocess_visarga_accent(text)
    
    # Step 3: Escape HTML special characters (before adding our HTML)
    text = _escape_html(text)
    
    # Step 4: Process footnotes - convert (s1) to superscript references
    text, collected_footnotes = local_process_footnotes_html(text, footnotes_dict, counter_obj, seen_map, accumulator)
    
    # Step 5: Replace accent markers with Unicode combining characters
    text = _replace_accents(text)
    
    # Step 6: Split multi-Rik text so each Rik is on its own line
    text = split_rik_lines_html(text)
    
    # Step 7: Format dandas
    text = _format_dandas(text)
    
    return text, collected_footnotes


MALAYALAM_MODIFIER_MAP = {
    'A': ('mod-a', '&#xE004;'),
    'a': ('mod-a', '&#xE004;'),
    '⁀': ('mod-a', '&#xE004;'),
    'A1': ('mod-a1', '&#xE00D;'),
    'a1': ('mod-a1', '&#xE00D;'),
    'A_1': ('mod-a1', '&#xE00D;'),
    'a_1': ('mod-a1', '&#xE00D;'),
    'B': ('mod-b', '&#xE005;'),
    'b': ('mod-b', '&#xE005;'),
    '^': ('mod-b', '&#xE005;'),
    '∧': ('mod-b', '&#xE005;'),
    'C': ('mod-c', '&#xE001;'),
    'c': ('mod-c', '&#xE001;'),
    '·': ('mod-c', '&#xE001;'),
    'D': ('mod-d', '&#xE006;'),
    'd': ('mod-d', '&#xE006;'),
    'Ʌ': ('mod-d', '&#xE006;'),
    'E': ('mod-e', '&#xE002;'),
    'e': ('mod-e', '&#xE002;'),
    '┃': ('mod-e', '&#xE002;'),
    'L': ('mod-e', '&#xE002;'),
    'F': ('mod-f', '&#x2577;'),
    'f': ('mod-f', '&#x2577;'),
    '╷': ('mod-f', '&#x2577;'),
    'G': ('mod-g', '&#xE003;'),
    'g': ('mod-g', '&#xE003;'),
    '\\': ('mod-g', '&#xE003;'),
    'H': ('mod-h', '&#xE00C;'),
    'h': ('mod-h', '&#xE00C;'),
    '|': ('mod-h', '&#xE00C;'),
    '.': ('mod-dot', '&#xE001;'),
    '_': ('mod-underbar', '&#xE007;'),
    ',': ('mod-comma', '&#xE00A;'),
}

MALAYALAM_SWARA_SUBS = {
    '𑌪𑍍𑌲': '&#xE020;',
    '𑌪𑍍𑌲𑌾': '&#xE021;',
    '𑌪𑍍𑌲𑌿': '&#xE022;',
    '𑌪𑍍𑌲𑍀': '&#xE023;',
    'ശ𑌾': '&#xE010;',
    'ശ𑌿': '&#xE011;',
    'ശ𑍀': '&#xE012;',
    'ശ്': '&#xE013;',
    'ത്ര': '&#xE01D;',
    'ക്ര': '&#xE01E;',
}

def split_malayalam_clusters(word):
    """Split Malayalam word into syllable clusters (handling conjuncts and chillus)."""
    try:
        from malayalam.ml_transliterate import split_malayalam_syllables
        return split_malayalam_syllables(word)
    except Exception:
        pattern = r'(?:[\u0D05-\u0D14]|(?:[\u0D15-\u0D3A\u0D7A-\u0D7F](?:\u0D4D[\u0D15-\u0D3A])*[\u0D3E-\u0D4D\u0D57\u0D62\u0D63]?[\u0D02\u0D03]?))'
        clusters = re.findall(pattern, word)
        if not clusters or ''.join(clusters) != word:
            return [word]
        return clusters

def format_malayalam_mantra_html(mantra_text, footnotes_dict=None, counter_obj=None, seen_map=None, accumulator=None):
    if not mantra_text:
        return "", []
    if footnotes_dict is None: footnotes_dict = {}
    if counter_obj is None: counter_obj = {'val': 0}
    if seen_map is None: seen_map = {}
    if accumulator is None: accumulator = []

    devanagari_digits = '०१२३४५६७८९'
    html_parts = []
    collected_footnotes = []

    text = mantra_text.replace('\n', ' ').strip()
    text = re.sub(r'\|\|', '॥', text)
    text = re.sub(r'\|\s*\|', '॥', text)
    text = re.sub(r'।।', '॥', text)
    text = text.replace('|', '।')

    token_re = re.compile(
        r'(\s+)|'
        r'(\|\||॥|\||।)|'
        r'(\(s\d+\))|'
        r'([^\s\|।॥()]+(?:\([^)]+\))*|\([^)]+\))'
    )

    for m in token_re.finditer(text):
        space, danda, fn, word_match = m.groups()
        if space:
            html_parts.append('<span class="word-space">&nbsp;</span>')
            continue
        elif danda:
            m_num = re.match(r'॥\s*([\d०-९]+)\s*॥', danda)
            if m_num:
                html_parts.append(f'<span class="danda">॥</span><span class="mantra-word"><span class="swara-text">&nbsp;</span><span class="mantra-text"><span class="mantra-number">{m_num.group(1)}</span></span></span><span class="danda">॥</span><div class="mantra-break"></div>')
            else:
                html_parts.append(f'<span class="danda">{danda}</span>')
            continue
        elif fn:
            marker_key = fn.strip('()')
            footnote_text = footnotes_dict.get(marker_key, '').strip()
            if footnote_text and footnote_text in seen_map:
                unique_id, display_num = seen_map[footnote_text]
            else:
                counter_obj['val'] += 1
                val = counter_obj['val']
                unique_id = f'fn-kandah-{val}'
                display_num = ''.join(devanagari_digits[int(d)] for d in str(val))
                if footnote_text:
                    seen_map[footnote_text] = (unique_id, display_num)
                    accumulator.append((unique_id, display_num, footnote_text))
                    collected_footnotes.append((unique_id, val, footnote_text))
            html_parts.append(f'<sup class="footnote-ref"><a href="#{unique_id}">{display_num}</a></sup>')
            continue
        elif word_match:
            tok = word_match.strip()
            if not tok:
                continue

            # Verse number token
            m_num = re.match(r'॥\s*([\d०-९]+)\s*॥', tok)
            if m_num:
                html_parts.append(f'<span class="danda">॥</span><span class="mantra-word"><span class="swara-text">&nbsp;</span><span class="mantra-text"><span class="mantra-number">{m_num.group(1)}</span></span></span><span class="danda">॥</span><div class="mantra-break"></div>')
                continue

            # Standalone punctuation
            if tok in ('_', '._', '_.'):
                html_parts.append(f'<span class="mantra-punct">{tok}</span>')
                continue
            elif tok == '.':
                html_parts.append('<span class="mantra-punct">.</span>')
                continue
            elif tok == ',':
                html_parts.append('<span class="mantra-punct">,</span>')
                continue

            # Word with swara / modifier parens
            base = re.sub(r'\([^)]+\)', '', tok).strip()
            parens = re.findall(r'\(([^)]+)\)', tok)

            swara_val = ''
            mods = []
            fn_marker = None
            for p in parens:
                if p in MALAYALAM_MODIFIER_MAP:
                    mods.append(MALAYALAM_MODIFIER_MAP[p])
                elif re.match(r's\d+', p):
                    fn_marker = p
                else:
                    swara_val = MALAYALAM_SWARA_SUBS.get(p, p)

            core_word = base.rstrip("_,.")
            trailing_punct = base[len(core_word):]
            if not core_word:
                core_word = base if base else '&nbsp;'

            # Split into syllables
            syllables = split_malayalam_clusters(core_word) if core_word != '&nbsp;' else ['&nbsp;']

            mod_html = ''
            for m_cls, m_glyph in mods:
                if m_cls == 'mod-b':
                    mod_html += f'<span class="swara-mod mod-b"><span class="caret-glyph">&#xE005;</span><span class="swara-on-caret">{swara_val or "&nbsp;"}</span></span>'
                    swara_val = ''
                elif m_cls == 'mod-c':
                    mod_html += '<span class="swara-mod mod-c">&#xE001;</span>'
                elif m_cls == 'mod-h':
                    mod_html += '<span class="swara-mod mod-h">&#xE00C;</span>'
                elif m_cls == 'mod-g':
                    mod_html += '<span class="swara-mod mod-g">&#xE003;</span>'
                elif m_cls == 'mod-e':
                    mod_html += '<span class="swara-mod mod-e">&#xE002;</span>'
                elif m_cls == 'mod-f':
                    mod_html += '<span class="swara-mod mod-f">&#x2577;</span>'
                else:
                    mod_html += f'<span class="swara-mod {m_cls}">{m_glyph}</span>'

            fn_html = ''
            if fn_marker:
                footnote_text = footnotes_dict.get(fn_marker, '').strip()
                if footnote_text and footnote_text in seen_map:
                    unique_id, display_num = seen_map[footnote_text]
                else:
                    counter_obj['val'] += 1
                    val = counter_obj['val']
                    unique_id = f'fn-kandah-{val}'
                    display_num = ''.join(devanagari_digits[int(d)] for d in str(val))
                    if footnote_text:
                        seen_map[footnote_text] = (unique_id, display_num)
                        accumulator.append((unique_id, display_num, footnote_text))
                        collected_footnotes.append((unique_id, val, footnote_text))
                fn_html = f'<sup class="footnote-ref"><a href="#{unique_id}">{display_num}</a></sup>'

            for idx, syl in enumerate(syllables):
                if idx == len(syllables) - 1:
                    sw_disp = swara_val if swara_val else '&nbsp;'
                    html_parts.append(f'<span class="mantra-word"><span class="swara-text">{sw_disp}</span><span class="mantra-text">{syl}{mod_html}</span></span>{fn_html}')
                else:
                    html_parts.append(f'<span class="mantra-word"><span class="swara-text">&nbsp;</span><span class="mantra-text">{syl}</span></span>')

            if trailing_punct:
                html_parts.append(f'<span class="mantra-punct">{trailing_punct}</span>')

    return ''.join(html_parts), collected_footnotes


def format_mantra_text_html(mantra_text, footnotes_dict=None, counter_obj=None, seen_map=None, accumulator=None):
    """
    Format Sama mantra text for HTML display with stacked word/swara layout.
    Parses the mantra text and creates HTML with mantra words and their associated swaras.
    Also processes footnote markers.
    Returns: (formatted_text, collected_footnotes)
    """
    if not mantra_text:
        return "", []

    # Detect Malayalam / Grantha content
    if re.search(r'[\u0D00-\u0D7F\u11300-\u1137F\uE000-\uE02F]', mantra_text):
        return format_malayalam_mantra_html(mantra_text, footnotes_dict, counter_obj, seen_map, accumulator)

    # --- Preprocess Visarga/Accents with ZWJ ---
    mantra_text = step_preprocess_visarga_accent(mantra_text)

    if footnotes_dict is None:
        footnotes_dict = {}
    
    
    # Default state if not provided
    if counter_obj is None: counter_obj = {'val': 0}
    if seen_map is None: seen_map = {}
    if accumulator is None: accumulator = []
    if footnotes_dict is None: footnotes_dict = {}

    html_parts = []
    collected_footnotes = []

    # Devanagari digits for footnote references
    devanagari_digits = '०१२३४५६७८९'
    
    # Parse the mantra text for word/swara pairs
    # Pattern: Word + (Swara) where Swara is in parentheses
    i = 0
    text = mantra_text.replace('\n', ' ').replace('\r', '').strip()
    
    # --- Normalize Dandas for Parsing ---
    # Convert various forms (ASCII pipes, spaced pipes, double singles) to Standard Devanagari
    text = re.sub(r'\|\|', '॥', text)
    text = re.sub(r'\|\s*\|', '॥', text)
    text = re.sub(r'।।', '॥', text)
    text = text.replace('|', '।')
    
    while i < len(text):
        # Skip whitespace - don't add spaces between mantra words (matching renderPDF.py)
        if text[i].isspace() or text[i] in '\u200c\u200d\ufeff':
            i += 1
            continue
        
        # Check for dandas - wrap in mantra-word for vertical alignment
        if text[i] in '।॥|':
            # Check for verse number: ॥N॥
            number_match = re.match(r'॥\s*(\d+)\s*॥', text[i:])
            if number_match:
                num = number_match.group(1)
                # Wrap verse number in mantra-word structure for alignment
                html_parts.append(
                    f'<span class="mantra-word">'
                    f'<span class="mantra-text"><span class="mantra-number">॥ {num} ॥</span></span>'
                    f'<span class="swara-text">&nbsp;</span>'
                    f'</span>'
                    f'<div class="mantra-break"></div>'
                )
                i += len(number_match.group(0))
            else:
                danda = text[i]
                # Wrap danda in mantra-word structure for vertical alignment
                html_parts.append(
                    f'<span class="mantra-word">'
                    f'<span class="mantra-text"><span class="danda">{danda}</span></span>'
                    f'<span class="swara-text">&nbsp;</span>'
                    f'</span>'
                )
                i += 1
            continue
        
        # Check for footnote marker: (sN)
        footnote_match = re.match(r'\(s(\d+)\)', text[i:])
        if footnote_match:
            marker_num = footnote_match.group(1)
            marker_key = f's{marker_num}'
            footnote_text = footnotes_dict.get(marker_key, '').strip()

            unique_id = ""
            display_num = ""
            if footnote_text and footnote_text in seen_map:
                unique_id, display_num = seen_map[footnote_text]
            else:
                counter_obj['val'] += 1
                val = counter_obj['val']
                unique_id = f'fn-kandah-{val}'
                display_num = ''.join(devanagari_digits[int(d)] for d in str(val))
                if footnote_text:
                    seen_map[footnote_text] = (unique_id, display_num)
                    accumulator.append((unique_id, display_num, footnote_text))
                    collected_footnotes.append((unique_id, val, footnote_text))

            # Add superscript reference with Devanagari number - No whitespace
            html_parts.append(f'<sup class="footnote-ref"><a href="#{unique_id}">{display_num}</a></sup>')
            i += len(footnote_match.group(0))
            continue
        
        # Match pattern: [Word](Swara) - but NOT (sN) which is a footnote
        match = re.match(r'([^\s()।॥]+)\s*\(([^)]+)\)\s*([:ः]?)', text[i:])
        if match:
            word = match.group(1)
            swara = match.group(2)
            trailing_visarga = match.group(3)
            
            # Attach trailing visarga to word if present
            if trailing_visarga:
                word += trailing_visarga
            
        # Check if swara is actually a footnote marker like 's1'
            if re.match(r's\d+$', swara):
                # This is a footnote attached to a word, not a swara
                marker_num = swara[1:] # extract number from sN
                marker_key = swara
                footnote_text = footnotes_dict.get(marker_key, '').strip()

                unique_id = ""
                display_num = ""
                if footnote_text and footnote_text in seen_map:
                    unique_id, display_num = seen_map[footnote_text]
                else:
                    counter_obj['val'] += 1
                    val = counter_obj['val']
                    unique_id = f'fn-kandah-{val}'
                    display_num = ''.join(devanagari_digits[int(d)] for d in str(val))
                    if footnote_text:
                        seen_map[footnote_text] = (unique_id, display_num)
                        accumulator.append((unique_id, display_num, footnote_text))
                        collected_footnotes.append((unique_id, val, footnote_text))
                
                # Render word + footnote superscript - No whitespace
                word = _escape_html(word)
                html_parts.append(
                    f'<span class="mantra-word"><span class="mantra-text">{word}</span><span class="swara-text">&nbsp;</span></span>'
                    f'<sup class="footnote-ref"><a href="#{unique_id}">{display_num}</a></sup>'
                )
            else:
                # Normal word + swara - Split using combine_ardhaksharas logic (matching renderPDF.py)
                clusters = combine_ardhaksharas(word)
                if len(clusters) > 0:
                    last_cluster = clusters[-1]
                    preceding = "".join(clusters[:-1])
                    
                    if preceding:
                        html_parts.append(f'<span class="mantra-word"><span class="mantra-text">{_escape_html(preceding)}</span><span class="swara-text">&nbsp;</span></span>')
                    
                    # Logic from renderPDF.py: \stackleft if len > 1, else \stackcenter
                    align_cls = " swara-left" if len(swara.strip()) > 1 else ""
                    html_parts.append(
                        f'<span class="mantra-word">'
                        f'<span class="mantra-text">{_escape_html(last_cluster)}</span>'
                        f'<span class="swara-text{align_cls}">{_escape_html(swara)}</span>'
                        f'</span>'
                    )
                else:
                    # Fallback for empty/invalid
                    align_cls = " swara-left" if len(swara.strip()) > 1 else ""
                    html_parts.append(
                        f'<span class="mantra-word">'
                        f'<span class="mantra-text">{_escape_html(word)}</span>'
                        f'<span class="swara-text{align_cls}">{_escape_html(swara)}</span>'
                        f'</span>'
                    )
            i += len(match.group(0))
            continue
        
        # Otherwise, collect text until next special character
        j = i
        while j < len(text) and text[j] not in '()।॥|' and not text[j].isspace():
            j += 1
        
        if j > i:
            word = _escape_html(text[i:j])
            # Word without swara - use &nbsp; for empty swara slot (matching renderPDF.py)
            html_parts.append(f'<span class="mantra-word"><span class="mantra-text">{word}</span><span class="swara-text">&nbsp;</span></span>')
            i = j
        else:
            # Skip unhandled character
            i += 1
    
    return ''.join(html_parts), collected_footnotes


# --- Data Classes ---
@dataclass
class Sama:
    """Represents a single Sama (verse/song)"""
    id: str
    title: str = ""
    rik_metadata: str = ""
    saman_metadata: str = ""
    rik_text: str = ""
    mantra_text: str = ""
    procedure_ref: Dict = field(default_factory=dict)
    footnotes: List[str] = field(default_factory=list)
    audio_filename: str = ""
    sama_number: int = 0
    global_number: int = 0  # Global sama number across all kandahs
    
    # Classification Fields
    saman_rishi: str = ""
    saman_devata: str = ""
    saman_chandas: str = ""
    rik_rishi: str = ""
    rik_devata: str = ""
    rik_chandas: str = ""
    rik_classifications: List[Dict] = field(default_factory=list)
    rik_ids: List[int] = field(default_factory=list) # Relative Rik IDs in Kandah

@dataclass
class Kandah:
    """Represents a Kandah (chapter/section)"""
    id: str
    title: str
    samas: List[Sama] = field(default_factory=list)
    kandah_number: int = 0

@dataclass
class Parva:
    """Represents a Parva (top-level section)"""
    id: str
    title: str
    kandahs: List[Kandah] = field(default_factory=list)
    parva_number: int = 0


# --- Parser Class ---
class JSVParser:
    """Parses the Samhita source file into Parva → Kandah → Sama structure"""
    
    def __init__(self, source_file: str, procedure_index: dict = None):
        self.source_file = source_file
        self.procedure_index = procedure_index or {}
        self.metadata = {}
        self.parvas: List[Parva] = []
        self.current_sama: Optional[Sama] = None
        self.closing_mantras: List[str] = []
    def parse(self) -> List[Parva]:
        """Main parsing method - delegates based on file type"""
        if self.source_file.lower().endswith('.json'):
            parvas = self._parse_json()
        else:
            parvas = self._parse_text_file()
            
        # Post-process to ensure sama_number matches natural sequence IDs
        self._post_process_numbering()
        return parvas

    def _post_process_numbering(self):
        """
        Recalculate all sama_number properties to match the natural mantra sequence.
        This ensures that Search hits and Jump-to targets correctly align with anchors.
        """
        for parva in self.parvas:
            for kandah in parva.kandahs:
                running_mantra_count = 0
                for sama in kandah.samas:
                    # The block's anchor ID will be based on this sama_number
                    sama.sama_number = running_mantra_count + 1
                    
                    # Update count based on actual mantras in this block
                    cnt = count_samams_with_fallback(sama.mantra_text)
                    if cnt == 0: cnt = 1
                    running_mantra_count += cnt

    def _parse_json(self) -> List[Parva]:
        """Parse JSON source file"""
        with open(self.source_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        self.metadata = data.get('meta', {})
        self.closing_mantras = data.get('closing_mantras', [])
            
        super_keys = sorted(data.get('supersection', {}).keys(), 
                          key=lambda x: int(x.split('_')[1]) if '_' in x else 0)
                          
        for ss_key in super_keys:
            ss_data = data['supersection'][ss_key]
            title = ss_data.get('supersection_title', ss_key)
            self._start_new_parva(ss_key, title)
            
            sec_keys = sorted([k for k in ss_data.get('sections', {}).keys() if k != 'count'],
                            key=lambda x: int(x.split('_')[1]) if '_' in x else 0)
                            
            for sec_key in sec_keys:
                sec_data = ss_data['sections'][sec_key]
                sec_title = sec_data.get('section_title', sec_key)
                self._start_new_kandah(sec_key, sec_title)
                
                sub_keys = sorted(sec_data.get('subsections', {}).keys(),
                                key=lambda x: int(x.split('_')[1]) if '_' in x else 0)
                                
                for sub_key in sub_keys:
                    sub_data = sec_data['subsections'][sub_key]
                    header_info = sub_data.get('header', {})
                    sama_title = header_info.get('header', '')
                    
                    self._start_new_sama(sub_key, sama_title)
                    
                    s: Optional[Sama] = self.current_sama
                    if s is not None:
                        s.rik_metadata = sub_data.get('rik_metadata', '')
                        s.saman_metadata = sub_data.get('saman_metadata', '')
                        s.rik_text = sub_data.get('rik_text', '')
                        
                        ms = sub_data.get('corrected-mantra_sets', [])
                        mantra_list = []
                        for m in ms:
                             if isinstance(m, dict):
                                 mantra_list.append(m.get('corrected-mantra', ''))
                        s.mantra_text = '\n'.join(mantra_list)
                        s.procedure_ref = sub_data.get('procedure_ref', {})
                        
                        fns = sub_data.get('footnotes', {})
                        fn_list = []
                        if isinstance(fns, dict):
                            for k, v in fns.items():
                                 fn_list.append(f"{k}: {v}")
                        s.footnotes = fn_list
                        
                        # Classification fields
                        s.saman_rishi = sub_data.get('saman_rishi', '')
                        s.saman_devata = sub_data.get('saman_devata', '')
                        s.saman_chandas = sub_data.get('saman_chandas', '')
                        s.rik_rishi = sub_data.get('rik_rishi', '')
                        s.rik_devata = sub_data.get('rik_devata', '')
                        s.rik_chandas = sub_data.get('rik_chandas', '')
                        s.rik_classifications = sub_data.get('rik_classifications', [])
                        s.rik_ids = sub_data.get('rik_ids', [])
                        if not s.rik_ids and sub_data.get('rik_id'):
                            s.rik_ids = [sub_data.get('rik_id')]
        
        self._finalize_current_sama()
        return self.parvas

    def _parse_text_file(self) -> List[Parva]:
        """Legacy Parsing method (Text File)"""
        content = self._read_file()
        
        # Extract metadata from text headers if present
        from utils import extract_metadata_from_text
        self.metadata = extract_metadata_from_text(content)
        self.closing_mantras = extract_closing_mantras(content)
        
        lines = content.split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Check for SuperSection (Parva)
            if '# Start of SuperSection Title --' in line:
                parva_id = self._extract_id(line, 'supersection_')
                i += 1
                title = lines[i].strip() if i < len(lines) else ""
                self._start_new_parva(parva_id, title)
                
            # Check for Section (Kandah)
            elif '# Start of Section Title --' in line:
                section_id = self._extract_id(line, 'section_')
                i += 1
                title = lines[i].strip() if i < len(lines) else ""
                self._start_new_kandah(section_id, title)
                
            # Check for SubSection Title (Sama title)
            elif '# Start of SubSection Title --' in line:
                subsection_id = self._extract_id(line, 'subsection_')
                i += 1
                title = lines[i].strip() if i < len(lines) else ""
                if self.current_sama and self.current_sama.id == subsection_id:
                    self.current_sama.title = title
                else:
                    self._start_new_sama(subsection_id, title)
                    
            # Check for Rik Metadata
            elif '# Start of Rik Metadata --' in line:
                subsection_id = self._extract_id(line, 'subsection_')
                i += 1
                metadata = lines[i].strip() if i < len(lines) else ""
                self._ensure_sama_exists(subsection_id)
                if self.current_sama:
                    if self.current_sama.rik_metadata:
                        self.current_sama.rik_metadata += f"  {metadata}"
                    else:
                        self.current_sama.rik_metadata = metadata
                    
            # Check for Rik Text
            elif '# Start of Rik Text --' in line:
                subsection_id = self._extract_id(line, 'subsection_')
                i += 1
                rik_text = lines[i].strip() if i < len(lines) else ""
                self._ensure_sama_exists(subsection_id)
                if self.current_sama:
                    self.current_sama.rik_text = rik_text
                    
                    # Also extract relative rik number from ॥ N ॥ if present
                    # and push to rik_ids
                    # Regex for [॥।|]{1,2} N [॥।|]{1,2}
                    rik_nums = re.findall(r'(?:॥|\|\||।।|।|\|)\s*([\d०-९]+)\s*(?:॥|\|\||।।|।|\|)', rik_text)
                    if rik_nums:
                        from utils import devanagari_to_int
                        self.current_sama.rik_ids.extend([devanagari_to_int(n) for n in rik_nums])
                    
            # Check for Mantra Sets
            elif '#Start of Mantra Sets --' in line or '# Start of Mantra Sets --' in line:
                subsection_id = self._extract_id(line, 'subsection_')
                mantra_lines = []
                i += 1
                while i < len(lines) and '#End of Mantra Sets' not in lines[i] and '# End of Mantra Sets' not in lines[i]:
                    mantra_lines.append(lines[i])
                    i += 1
                if self.current_sama:
                    self.current_sama.mantra_text = '\n'.join(mantra_lines).strip()
                continue  # Skip the i += 1 at end
                
            # Check for Footnotes
            elif '# Start of Footnote --' in line:
                footnote_lines = []
                i += 1
                while i < len(lines) and '# End of Footnote' not in lines[i]:
                    footnote_lines.append(lines[i].strip())
                    i += 1
                if self.current_sama:
                    self.current_sama.footnotes = [f for f in footnote_lines if f]
                continue
                
            i += 1
            
        # Finalize last sama if exists
        self._finalize_current_sama()
        
        return self.parvas
    
    def _read_file(self) -> str:
        """Read source file with proper encoding"""
        encodings = ['utf-8', 'utf-8-sig', 'utf-16', 'latin-1']
        for encoding in encodings:
            try:
                with open(self.source_file, 'r', encoding=encoding) as f:
                    return f.read()
            except (UnicodeDecodeError, UnicodeError):
                continue
        raise ValueError(f"Could not read file with any encoding: {self.source_file}")
    
    def _extract_id(self, line: str, prefix: str) -> str:
        """Extract ID from marker line"""
        match = re.search(rf'{prefix}(\d+)', line)
        return match.group(1) if match else ""
    
    def _start_new_parva(self, parva_id: str, title: str):
        """Start a new Parva"""
        self._finalize_current_sama()
        parva = Parva(
            id=parva_id,
            title=title,
            parva_number=len(self.parvas) + 1
        )
        self.parvas.append(parva)
        self.current_parva = parva
        self.current_kandah = None
        self.current_sama = None
        
    def _start_new_kandah(self, kandah_id: str, title: str):
        """Start a new Kandah within current Parva"""
        self._finalize_current_sama()
        if not self.current_parva:
            return
        kandah = Kandah(
            id=kandah_id,
            title=title,
            kandah_number=len(self.current_parva.kandahs) + 1
        )
        self.current_parva.kandahs.append(kandah)
        self.current_kandah = kandah
        self.current_sama = None
        
    def _start_new_sama(self, sama_id: str, title: str = ""):
        """Start a new Sama within current Kandah"""
        self._finalize_current_sama()
        if not self.current_kandah:
            return
        sama = Sama(
            id=sama_id,
            title=title,
            sama_number=len(self.current_kandah.samas) + 1
        )
        self.current_kandah.samas.append(sama)
        self.current_sama = sama
        
    def _ensure_sama_exists(self, sama_id: str):
        """Ensure a Sama exists with given ID, create if needed"""
        if self.current_sama and self.current_sama.id == sama_id:
            return
        # If we're starting metadata/text for a new sama
        self._start_new_sama(sama_id)
            
    def _finalize_current_sama(self):
        """Finalize the current Sama (generate audio filename, etc.)"""
        if self.current_sama and self.current_parva and self.current_kandah:
            parva_name = self._sanitize_for_filename(self.current_parva.title)
            self.current_sama.audio_filename = AUDIO_FILENAME_FORMAT.format(
                parva=parva_name,
                kandah=f"{self.current_kandah.kandah_number:02d}",
                sama=f"{self.current_sama.sama_number:02d}"
            )
            
    def _sanitize_for_filename(self, text: str) -> str:
        """Sanitize text for use in filename"""
        # Remove special characters, keep alphanumeric and Devanagari
        sanitized = re.sub(r'[^\w\u0900-\u097F]', '', text)
        return sanitized[:30] if sanitized else "unknown"


# --- HTML Generator Class (Rig Veda Style) ---
class WebsiteGenerator:
    """Generates static HTML website from parsed data - Rig Veda style"""
    
    def __init__(self, parvas: List[Parva], output_dir: str, audio_dir: str, mode: str = 'samhita', custom_title: str = None, font: str = 'AdishilaVedic', font_sans: str = 'AdishilaSanVedic', metadata: Dict = None, closing_mantras: List[str] = None):
        self.parvas = parvas
        self.output_dir = Path(output_dir)
        self.audio_dir = Path(audio_dir)
        self.mode = mode
        self.font = font
        self.font_sans = font_sans
        self.closing_mantras = closing_mantras or []
        
        self.is_malayalam = (self.mode == 'malayalam' or 'malayalam' in str(self.output_dir).lower() or 'malayalam' in str(self.font).lower())
        if self.is_malayalam:
            if self.mode != 'malayalam':
                self.mode = 'malayalam'
            if self.font == 'AdishilaVedic':
                self.font = 'Noto Serif Malayalam'
                self.font_sans = 'Noto Sans Malayalam'
            self.config = SITE_CONFIG['malayalam'].copy()
        else:
            self.config = SITE_CONFIG.get(mode, SITE_CONFIG['samhita']).copy()
        
        # Override title_sa if custom_title provided
        if custom_title:
            self.config['title_sa'] = custom_title
        
        self.labels = self._get_labels()
        
        # Standardize metadata - priority: passed metadata > system metadata
        from utils import get_generated_metadata
        sys_meta = get_generated_metadata()
        
        self.metadata = {
            "version": metadata.get("version", sys_meta["version"]) if metadata else sys_meta["version"],
            "generated_at": sys_meta["generated_at"],
            "last_updated": datetime.now().strftime("%Y-%m-%d")
        }
        self.generated_at = self.metadata["generated_at"]
        
        # Initialize indices and counts (populated later by _collect_indices)
        self.rishi_index = {}
        self.devata_index = {}
        self.chandas_index = {}
        self.header_index = []
        self.total_riks_classified = 0

    def _get_labels(self):
        if getattr(self, 'is_malayalam', False):
            return {
                'parva': 'പാഠഃ',
                'kandah': 'ഖണ്ഡഃ',
                'sama': 'സാമ:',
                'arsheyam': 'ആർഷേയമ്',
                'rik': 'ഋക്',
                'home': 'മുഖ്യപുറം (Home)',
                'search': '🔍 അന്വേഷണം (Search)',
                'jump_placeholder': 'ഉദാ. 1.1.1',
                'indices': 'മറ്റു വർഗ്ഗീകരണങ്ങൾ (Indices)',
                'rishi': 'ഋഷയഃ',
                'devata': 'ദേവതാഃ',
                'chandas': 'ഛന്ദാംസി',
                'anukramanika': 'അനുക്രമണിക',
                'varnanukraman': 'വർണ്ണാനുക്രമണം (Alphabetical Index)',
                'top_20': 'പ്രമുഖ (Top 20)',
            }
        else:
            return {
                'parva': 'पर्व:',
                'kandah': 'खण्ड:',
                'sama': 'साम:',
                'arsheyam': 'आर्षेयम्',
                'rik': 'ऋक्',
                'home': 'मुख्यपृष्ठम् (Home)',
                'search': '🔍 अन्वेषणम् (Search)',
                'jump_placeholder': 'e.g. 1.1.1 or 1.45',
                'indices': 'अन्य वर्गीकरणम् (Indices)',
                'rishi': 'ऋषयः',
                'devata': 'देवताः',
                'chandas': 'छन्दांसि',
                'anukramanika': 'अनुक्रमणिका',
                'varnanukraman': 'वर्णानुक्रमण (Varnanukraman)',
                'top_20': 'प्रमुखाः (Top 20)',
            }
        
    def generate(self):
        """Generate all website files"""
        # Create output directories
        self.output_dir.mkdir(parents=True, exist_ok=True)
        (self.output_dir / 'css').mkdir(exist_ok=True)
        (self.output_dir / 'js').mkdir(exist_ok=True)
        (self.output_dir / 'kandah').mkdir(exist_ok=True)
        
        # Copy JaimineeyaSwara font if in malayalam mode
        if self.is_malayalam:
            (self.output_dir / 'fonts').mkdir(exist_ok=True)
            src_font = Path('fonts/JaimineeyaSwara.ttf')
            if src_font.exists():
                import shutil
                shutil.copy2(src_font, self.output_dir / 'fonts' / 'JaimineeyaSwara.ttf')
        
        # Create audio placeholder directories
        self._create_audio_directories()
        
        # Collect index data early so counts are available for homepage
        self._collect_indices()
        
        # Generate files
        self._generate_css()
        self._generate_js()
        self._generate_search_index()
        self._generate_homepage()
        self._generate_indices()
        self._generate_kandah_pages()
        self._generate_procedure_pages()
        self._generate_metadata_json()
        
        print(f"✅ Website generated at: {self.output_dir}")
        print(f"✅ Audio placeholder directories created at: {self.audio_dir}")
        
    def _create_audio_directories(self):
        """Create audio placeholder directories for each Parva"""
        self.audio_dir.mkdir(parents=True, exist_ok=True)
        for parva in self.parvas:
            parva_folder = self._sanitize_foldername(parva.title)
            (self.audio_dir / parva_folder).mkdir(exist_ok=True)
            # Create a placeholder README
            readme_path = self.audio_dir / parva_folder / "README.md"
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(f"# {parva.title}\n\n")
                f.write(f"Place audio files for {parva.title} here.\n\n")
                f.write("## Expected Filename Format\n")
                f.write(f"`JSV_{{ParvaName}}_{{KandahNum}}_{{SamaNum}}.mp3`\n\n")
                f.write("## Kandahs in this Parva\n")
                for kandah in parva.kandahs:
                    f.write(f"- {kandah.title} ({len(kandah.samas)} Samas)\n")
                    
    def _sanitize_foldername(self, text: str) -> str:
        """Sanitize text for folder name"""
        sanitized = re.sub(r'[^\w\u0900-\u097F\s]', '', text)
        return sanitized.replace(' ', '_').strip()[:50] if sanitized else "unknown"
        
    def _generate_css(self):
        """Generate CSS stylesheet - Configured Palette"""
        # Determine font-specific offsets (matching renderPDF.py logic)
        if 'notosans' in self.font.lower():
            sw_off = '0.1em'
            ka_off = '0.1em'
            tr_off = '0.1em'
            an_off = '-0.25em'
        else: # Default/Adishila
            sw_off = '0.06em'
            ka_off = '0.06em'
            tr_off = '0.06em'
            an_off = '0.25em'

        css = '''/* Jaimineeya Samavedam Website Styles */
/* User Defined Palette */

:root {
/* Core Palette */
--color-bg-main: #F9F4E8;   /* Eggshell */
--color-bg-card: #EFE6D5;   /* Antique White */
--color-text: #2C2C2C;      /* Charcoal */
--color-accent: #FF6B35;    /* Saffron (Restored) */
--color-primary: var(--color-accent);
--color-secondary: var(--color-text);

/* Theme Semantic Mapping */
--primary-maroon: var(--color-accent); /* Headings/Links = Saffron */
--primary-gold: #C08535;    /* Earthy Gold */
--accent-orange: #D2691E;   /* Chocolate */

/* Backgrounds */
--bg-main: var(--color-bg-main);
--bg-sidebar: #FCF9F0;
--bg-hover: #E8DCC0;
--bg-card: var(--color-bg-card);
--bg-verse: var(--bg-card);

/* Text */
--text-primary: var(--color-text);
--text-secondary: #4A4A4A;
--text-muted: #6B6B6B;
--text-link: #D35400;      /* Darker Saffron for contrast */
--text-link-hover: var(--color-accent); /* Saffron on hover/active */

--border-color: #D8CCB8;
--border-light: #E8DCC0;

/* Typography */
--font-heading: '{self.font}', '{self.font_sans}', 'Noto Serif Devanagari', 'Noto Sans Devanagari', serif;
--font-body: '{self.font}', '{self.font_sans}', 'Noto Sans Devanagari', 'Inter', sans-serif;
--font-sanskrit: '{self.font}', '{self.font_sans}', 'Noto Serif Devanagari', 'Siddhanta', serif;

/* Spacing */
--spacing-xs: 0.25rem;
--spacing-sm: 0.5rem;
--spacing-md: 1rem;
--spacing-lg: 1.5rem;
--spacing-xl: 2rem;
--spacing-2xl: 3rem;

/* Layout */
--sidebar-width: 280px;
}

/* Reset & Base */
*, *::before, *::after {
box-sizing: border-box;
margin: 0;
padding: 0;
}

html {
scroll-behavior: smooth;
font-size: 16px;
}

body {
font-family: var(--font-body);
background: var(--bg-main);
color: var(--text-primary);
line-height: 1.8;
min-height: 100vh;
}

/* Typography */
h1, h2, h3, h4, h5, h6 {
font-family: var(--font-heading);
font-weight: 600;
line-height: 1.4;
margin-bottom: var(--spacing-md);
color: var(--color-secondary); /* Headings in Dark Gray */
padding-bottom: 0.1rem;
display: inline-block;
}

h1 { font-size: 2.4rem; }
h2 { font-size: 1.8rem; }
h3 { font-size: 1.4rem; }
h4 { font-size: 1.2rem; }

/* Numerals and Counts in Adishila San Vedic (Sans Look) */
.stat-value, .rishi-rank, .number, .nav-links a, .toc-list li a, .jump-links a, .footnote-ref, .stats-summary, .stats-summary strong, .count, .rishi-count, .stats, .alpha-count, .item-count, .item-refs a, .item-count-badge, .sama-id, .sama-id a, .jump-input {{
    font-family: '{self.font_sans}', 'Noto Sans Devanagari', 'Inter', sans-serif !important;
}}

.stat-label, .rik-metadata, .mantra-number, .sama-header-text, .sama-metadata-text, .classification-table th, .classification-table td, .class-value, .class-label, .page-subtitle, .sama-count, .nav-section h3, .sidebar-right h3 {{
    font-family: '{self.font}', 'Noto Serif Devanagari', serif !important;
}}

.sanskrit-text {
font-family: var(--font-sanskrit);
font-size: 1.2rem;
line-height: 2;
letter-spacing: 0.02em;
}

.sanskrit-large {
font-size: 1.4rem;
line-height: 2.2;
}

/* Links */
a {
color: var(--text-link);
text-decoration: none;
transition: all 0.2s ease;
}

a:hover {
color: var(--text-link-hover);
text-decoration: none;
}

/* Main Layout - 3 Column */
.page-container {
display: flex;
min-height: 100vh;
}

/* Left Sidebar */
.sidebar-left {
width: var(--sidebar-width);
background: var(--bg-sidebar);
border-right: 1px solid var(--border-color);
padding: var(--spacing-lg);
position: fixed;
height: 100vh;
overflow-y: auto;
box-shadow: 2px 0 10px rgba(0,0,0,0.02);
}

.sidebar-left::-webkit-scrollbar {
width: 6px;
}

.sidebar-left::-webkit-scrollbar-thumb {
background: var(--color-primary);
border-radius: 3px;
}

.logo {
margin-bottom: var(--spacing-xl);
padding-bottom: var(--spacing-lg);
border-bottom: 1px solid var(--border-color);
text-align: center;
}

.logo-text {
font-family: var(--font-heading);
font-size: 1.8rem;
color: var(--color-primary);
font-weight: 700;
}

.logo-subtitle {
font-size: 1rem;
color: var(--text-muted);
margin-top: 4px;
text-transform: capitalize !important;
letter-spacing: 0.02em;
}

.nav-section {
margin-bottom: var(--spacing-xl);
}

.nav-section h3 {
font-size: 1.15rem;
color: var(--color-secondary);
text-transform: none;
letter-spacing: normal;
margin-bottom: var(--spacing-sm);
font-weight: normal; 
border-bottom: none;
}

.nav-section h3 .number, .sidebar-right h3 .number {
    font-size: 0.85rem;
    font-weight: 500;
}

.nav-links {
display: flex;
flex-wrap: wrap;
gap: var(--spacing-xs);
}

.nav-links a {
display: inline-block;
padding: 4px 10px;
background: var(--bg-card);
border: 1px solid var(--border-color);
border-radius: 4px;
font-size: 0.7rem;
transition: all 0.2s ease;
color: var(--text-secondary);
font-weight: 500;
}

.nav-links a:hover,
.nav-links a.active {
background: var(--color-accent);
color: white;
border-color: var(--color-accent);
box-shadow: 0 2px 4px rgba(255, 107, 53, 0.3);
}

.nav-list {
list-style: none;
}

.jump-input {
    width: 100%;
    padding: 10px 12px;
    border: 1px solid var(--border-color);
    border-radius: 8px;
    font-family: 'AdishilaSanVedic', 'Adishila San Vedic', 'Noto Sans Devanagari', 'Inter', sans-serif !important;
    font-size: 0.9rem;
    margin-top: 4px;
    background: white;
    box-shadow: inset 0 1px 3px rgba(0,0,0,0.05);
}

.jump-input:focus {
    outline: none;
    border-color: var(--color-accent);
    box-shadow: 0 0 0 2px rgba(255, 107, 53, 0.1);
}

.search-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 12px;
    padding: 12px;
    background: #FFFDF8;
    border: 1px solid #C08535;
    border-radius: 10px;
    color: #8B4513;
    font-weight: 600;
    text-decoration: none !important;
    transition: all 0.2s ease;
    width: 100%;
    margin-top: 10px;
    font-family: var(--font-sanskrit);
}

.search-btn:hover {
    background: white;
    box-shadow: 0 4px 12px rgba(192, 133, 53, 0.15);
    transform: translateY(-1px);
}

.sidebar-footer {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-top: var(--spacing-xl);
    padding-top: var(--spacing-lg);
    border-top: 1px solid var(--border-color);
}

.footer-btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 0.5rem 0.8rem;
    background: #F4F1EA;
    border-radius: 6px;
    font-size: 1rem;
    color: var(--text-secondary);
    text-decoration: none !important;
    transition: all 0.2s ease;
    font-family: var(--font-sanskrit);
    min-width: 70px;
    flex: 1 1 calc(33.33% - 0.5rem);
}

.footer-btn:hover {
    background: #E8DCC0;
    color: var(--primary-maroon);
}

.nav-list li {
margin-bottom: var(--spacing-xs);
}

.nav-list a {
display: block;
padding: 8px 12px;
border-radius: 6px;
transition: background 0.2s ease;
font-family: var(--font-sanskrit);
font-size: 1.15rem;
color: var(--text-primary);
border: 1px solid transparent;
}

.nav-list a:hover {
background: var(--color-primary);
color: white;
box-shadow: 0 2px 6px rgba(255, 107, 53, 0.3);
transform: translateX(4px);
border-color: var(--color-primary);
}

/* Main Content */
.main-content {
flex: 1;
margin-left: var(--sidebar-width);
padding: var(--spacing-md) var(--spacing-2xl);
max-width: 900px;
}

/* Right Sidebar (Jump Navigation) */
.sidebar-right {
width: 220px;
padding: var(--spacing-lg);
position: fixed;
right: 0;
height: 100vh;
overflow-y: auto;
border-left: 1px solid var(--border-color);
background: var(--bg-sidebar);
}

.sidebar-right h3 {
    font-size: 0.85rem;
    color: var(--text-muted);
    text-transform: none;
    letter-spacing: normal;
    margin-bottom: var(--spacing-md);
    font-weight: normal; /* Explicitly regular */
    border-bottom: none;
}

.jump-links {
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
}

.jump-links a {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 28px;
    height: 28px;
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 4px;
    font-size: 0.7rem;
    transition: all 0.2s ease;
    color: var(--text-secondary);
    font-weight: 500;
}

.jump-links a:hover {
    background: var(--color-primary);
    color: white;
    border-color: var(--color-primary);
    text-decoration: none;
    box-shadow: 0 2px 4px rgba(255, 107, 53, 0.3);
}

/* Page Header */
.page-header {
    margin-bottom: var(--spacing-lg);
    padding-bottom: 0;
    border-bottom: none;
}

.page-header h1 {
    margin-top: 0;
    margin-bottom: var(--spacing-xs);
}

.page-subtitle {
    color: var(--text-secondary);
    font-size: 1.1rem;
    font-family: var(--font-sanskrit);
}

.page-meta {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-top: var(--spacing-sm);
}

.page-meta .page-subtitle {
    margin: 0;
}

.sama-count {
    display: inline-block;
    font-size: 1.1rem;
    color: var(--text-secondary);
}

.page-meta .number {
    font-size: 0.8rem;
    font-weight: 400;
}

/* Top Nav Links (Mukhyaprshtam / Anveshanam) */
.top-nav {
    display: flex;
    justify-content: flex-end;
    gap: 1.5rem;
    margin-bottom: var(--spacing-md);
    font-family: var(--font-heading);
}

.top-nav a {
    color: var(--text-secondary);
    font-size: 1rem;
    font-weight: 500;
    transition: all 0.2s ease;
    padding: 2px 4px;
}

.top-nav a:hover {
    color: var(--color-accent);
    transform: translateY(-1px);
}

.top-nav .nav-icon {
    margin-right: 4px;
    font-style: normal;
}

/* Breadcrumb */
.breadcrumb {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    margin-bottom: var(--spacing-lg);
    font-size: 1.25rem;
    font-family: var(--font-sanskrit);
}

.breadcrumb a {
    color: var(--text-link);
}

.breadcrumb-separator {
    color: var(--text-muted);
}

/* Table of Contents */
.toc {
    background: var(--bg-sidebar);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: var(--spacing-lg);
    margin-bottom: var(--spacing-2xl);
}

.toc h4 {
    margin-bottom: var(--spacing-md);
    font-size: 1.2rem;
}

.toc-list {
    display: flex;
    flex-wrap: wrap;
    gap: var(--spacing-xs);
    list-style: none;
}

.toc-list li a {
    display: inline-block;
    padding: 4px 12px;
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 4px;
    font-size: 0.9rem;
}

.toc-list li a:hover {
    background: var(--primary-maroon);
    color: white;
    border-color: var(--primary-maroon);
    text-decoration: none;
}

/* Sama Entry (Verse) - Rig Veda Style */
.sama-anchor, .rik-anchor {
    scroll-margin-top: 100px;
    display: block;
    height: 0;
    overflow: hidden;
    visibility: hidden;
    pointer-events: none;
}

.sama-entry {
    scroll-margin-top: 100px;
    margin-bottom: var(--spacing-2xl);
    padding-bottom: var(--spacing-xl);
    border-bottom: 1px solid var(--border-light);
}

.sama-entry:last-child {
    border-bottom: none;
}

.sama-header {
    display: flex;
    align-items: baseline;
    gap: var(--spacing-md);
    margin-bottom: var(--spacing-md);
}

.sama-id {
    font-family: var(--font-heading);
    font-size: 0.9rem;
    color: var(--primary-maroon);
    font-weight: 600;
    background: var(--bg-sidebar);
    padding: 2px 10px;
    border-radius: 4px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    height: 22px;
    line-height: normal;
    transform: translateY(5px);
}

.sama-id a {
    color: var(--primary-maroon);
}

.sama-id a:hover {
    text-decoration: none;
}

.sama-id-row {
    margin-bottom: 0rem;
    margin-top: 0.5rem;
}

/* Metadata Links (Rishi, Devata, Chandas) */
.metadata-links {
    display: flex;
    flex-wrap: wrap;
    gap: var(--spacing-sm);
    margin-bottom: var(--spacing-md);
}

.metadata-link {
    display: inline-block;
    padding: 4px 12px;
    background: var(--bg-sidebar);
    border-radius: 4px;
    font-size: 0.9rem;
    color: var(--text-secondary);
    transition: all 0.2s ease;
}

.metadata-link:hover {
    background: var(--primary-gold);
    color: var(--text-primary);
    text-decoration: none;
}

.metadata-link.rishi {
    border-left: 3px solid #8B4513;
}

.metadata-link.devata {
    border-left: 3px solid #B22222;
}

.metadata-link.chandas {
    border-left: 3px solid #DAA520;
}

/* Sama Title */
.sama-title {
    font-family: var(--font-sanskrit);
    font-size: 1.1rem;
    color: var(--text-secondary);
    margin-bottom: var(--spacing-md);
    font-style: italic;
}

/* Rik Metadata - displayed above Rik text in purple */
.rik-metadata {
    font-family: var(--font-sanskrit);
    font-size: 1.6rem;
    color: #7b1fa2;
    text-align: center;
    margin-bottom: var(--spacing-sm);
}

/* Sama Header Container - Flex row for Title + Metadata */
.sama-header-container {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: var(--spacing-md);
    flex-wrap: wrap;
    margin-bottom: var(--spacing-sm);
}

/* Sama Header Text - displayed above Sama/Mantra text in green */
.sama-header-text {
    font-family: var(--font-sanskrit);
    font-size: 1.6rem;
    color: #2e7d32;
    text-align: center;
    width: auto;
    max-width: fit-content;
}
.proc-link-text {
    font-size: 0.9rem !important;
    vertical-align: middle;
    margin-left: 10px;
    color: #2e7d32;
    text-decoration: none;
    opacity: 0.8;
}

.proc-link-text:hover {
    opacity: 1;
    text-decoration: underline;
}

.procedure-box {
    background: #F0F4F7;
    border-left: 4px solid #2e7d32;
    padding: var(--spacing-md) var(--spacing-lg);
    margin-bottom: var(--spacing-md);
    border-top-right-radius: 8px;
    border-bottom-right-radius: 8px;
}

.procedure-label {
    font-size: 0.75rem;
    color: #2e7d32;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: var(--spacing-xs);
    font-weight: 600;
}

.procedure-text {
    font-family: var(--font-sanskrit);
    font-size: 1.4rem;
    line-height: 1.8;
    color: var(--text-primary);
}

/* Sama Metadata Text - displayed above Sama/Mantra text in Brown */
.sama-metadata-text {
    font-family: var(--font-sanskrit);
    font-size: 1.6rem;
    color: #8B4513;
    text-align: center;
    width: auto;
    max-width: fit-content;
}
.proc-link-text {
    font-size: 0.9rem !important;
    vertical-align: middle;
    margin-left: 10px;
    color: #2e7d32;
    text-decoration: none;
    opacity: 0.8;
}

.proc-link-text:hover {
    opacity: 1;
    text-decoration: underline;
}

.procedure-box {
    background: #F0F4F7;
    border-left: 4px solid #2e7d32;
    padding: var(--spacing-md) var(--spacing-lg);
    margin-bottom: var(--spacing-md);
    border-top-right-radius: 8px;
    border-bottom-right-radius: 8px;
}

.procedure-label {
    font-size: 0.75rem;
    color: #2e7d32;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: var(--spacing-xs);
    font-weight: 600;
}

.procedure-text {
    font-family: var(--font-sanskrit);
    font-size: 1.4rem;
    line-height: 1.8;
    color: var(--text-primary);
}

/* Rik Text Box */
.rik-box {
    background: #FFF8DC;
    border-left: 4px solid var(--primary-gold);
    padding: var(--spacing-md) var(--spacing-lg);
    margin-bottom: var(--spacing-md);
    border-radius: 0 8px 8px 0;
}

.rik-label {
    font-size: 0.75rem;
    color: var(--primary-gold);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: var(--spacing-xs);
    font-weight: 600;
}

.rik-text {
    font-family: var(--font-sanskrit);
    font-size: 1.6rem;
    line-height: 2;
    color: #1565c0;
    text-align: center;
}

/* Mantra Text Box */
.mantra-box {
    background: var(--bg-verse);
    border-left: 4px solid var(--primary-maroon);
    padding: var(--spacing-md) var(--spacing-lg);
    margin-bottom: var(--spacing-md);
    border-radius: 0 8px 8px 0;
}

.mantra-label {
    font-size: 0.75rem;
    color: var(--primary-maroon);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: var(--spacing-xs);
    font-weight: 600;
}

.mantra-container {
    font-family: var(--font-sanskrit);
    font-size: 1.6rem;
    line-height: 2.2;
    color: var(--text-primary);
    text-align: left;
}

/* Audio Section */
.audio-section {
    margin-top: var(--spacing-md);
}

.audio-player {
    width: 100%;
    margin-top: 5px;
}

.index-list {
    column-count: 3;
    column-gap: 2.5rem;
    column-rule: 1px solid var(--border-light);
    margin-top: 2rem;
}

@media (max-width: 1200px) {
    .index-list {
        column-count: 2;
    }
}

@media (max-width: 800px) {
    .index-list {
        column-count: 1;
    }
}

.index-char-group {
    break-inside: avoid-column;
    margin-bottom: 2rem;
}

.audio-pending {
    display: inline-flex;
    align-items: center;
    gap: var(--spacing-sm);
    padding: var(--spacing-sm) var(--spacing-md);
    background: var(--bg-sidebar);
    border: 1px dashed var(--border-color);
    border-radius: 4px;
    color: var(--text-muted);
    font-size: 0.9rem;
}

/* Footnotes */
.footnotes {
    margin-top: var(--spacing-md);
    padding-top: var(--spacing-md);
    border-top: 1px dashed var(--border-color);
}

.footnotes-label {
    font-size: 0.8rem;
    color: var(--text-muted);
    margin-bottom: var(--spacing-xs);
}

.footnote-item {
    font-size: 0.9rem;
    color: var(--text-secondary);
    margin-bottom: var(--spacing-xs);
    padding-left: var(--spacing-md);
    border-left: 2px solid var(--border-color);
}

/* Homepage Styles */
.home-hero {
    text-align: center;
    padding: var(--spacing-lg) 0;
    margin-bottom: var(--spacing-xl);
    border-bottom: 1px solid var(--border-light);
}

.home-hero h1 {
    font-size: 3rem;
    margin-bottom: var(--spacing-sm);
}

.home-hero .subtitle {
    font-size: 1.5rem;
    color: var(--text-secondary);
}

.stats-row {
    display: flex;
    justify-content: center;
    gap: var(--spacing-2xl);
    margin-top: var(--spacing-xl);
}

.stat-item {
    text-align: center;
}

.stat-value {
    font-size: 2.2rem;
    font-weight: 700;
    color: var(--primary-maroon);
}

.stat-label {
    font-size: 1.3rem;
    color: var(--text-muted);
}

/* Parva Grid */
.parva-section {
    margin-bottom: var(--spacing-xl);
}

.parva-section h2 {
    margin-bottom: var(--spacing-md);
    padding-bottom: 4px;
    border-bottom: none;
}

.kandah-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: var(--spacing-md);
}

.kandah-card {
    display: block;
    padding: var(--spacing-md);
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    transition: all 0.2s ease;
}

.kandah-card:hover {
    border-color: var(--primary-maroon);
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    text-decoration: none;
}

.kandah-card .number {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--primary-maroon);
}

.kandah-card .title {
    font-family: var(--font-sanskrit);
    font-size: 1.4rem;
    color: var(--text-primary);
    margin: var(--spacing-xs) 0;
}

.kandah-card .count {
    font-size: 0.85rem;
    color: var(--text-muted);
}

/* Footer */
.footer {
    margin-top: var(--spacing-2xl);
    padding: var(--spacing-xl);
    border-top: 1px solid var(--border-color);
    text-align: center;
    color: var(--text-muted);
    font-size: 0.9rem;
}

/* Search Modal */
.search-overlay {
    display: none;
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    z-index: 9998;
}

.search-overlay.active {
    display: block;
}

.search-modal {
    display: none;
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 90%;
    max-width: 700px;
    max-height: 80vh;
    background: var(--bg-main);
    border-radius: 12px;
    z-index: 9999;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
    overflow: hidden;
    flex-direction: column;
}

.search-modal.active {
    display: flex;
}

.search-modal-content {
    display: flex;
    flex-direction: column;
    height: 100%;
    min-height: 0;
}

.search-modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 20px;
    background: var(--bg-sidebar);
    border-bottom: 1px solid var(--border-color);
}

.search-modal-header h3 {
    margin: 0;
    font-family: var(--font-sanskrit);
    font-size: 1.2rem;
    color: var(--text-primary);
}

.search-close {
    background: none;
    border: none;
    font-size: 1.8rem;
    cursor: pointer;
    color: var(--text-muted);
    line-height: 1;
    padding: 0 4px;
}

.search-close:hover {
    color: var(--color-accent);
}

.search-input-container {
    padding: 16px 20px 8px;
}

.search-input {
    width: 100%;
    padding: 12px 16px;
    font-size: 1.2rem;
    font-family: var(--font-sanskrit);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    background: var(--bg-card);
    color: var(--text-primary);
    outline: none;
}

.search-input:focus {
    border-color: var(--color-accent);
    box-shadow: 0 0 0 2px rgba(255, 107, 53, 0.15);
}

.search-hint {
    display: block;
    font-size: 0.8rem;
    color: var(--text-muted);
    margin-top: 6px;
    padding-left: 4px;
}

.search-results {
    overflow-y: auto;
    padding: 12px;
    flex: 1;
    user-select: text;
    -webkit-user-select: text;
}

.search-result-item {
    padding: 12px 16px;
    margin-bottom: 8px;
    background: var(--bg-card);
    border-left: 3px solid transparent;
    border-radius: 4px;
    transition: all 0.2s ease;
    user-select: text;
    -webkit-user-select: text;
    -moz-user-select: text;
    -ms-user-select: text;
    display: block;
    text-decoration: none;
    cursor: pointer;
}

.search-result-item:hover {
    border-left-color: var(--color-accent);
    background: rgba(255, 107, 53, 0.08);
}

.search-result-item a {
    text-decoration: none;
    color: inherit;
    pointer-events: auto;
}

.search-result-ref {
    font-weight: 600;
    color: var(--color-accent);
    font-size: 0.85rem;
    margin-bottom: 2px;
}

.search-result-ref a {
    color: var(--color-accent);
    text-decoration: none;
}

.search-result-ref a:hover {
    text-decoration: underline;
}

.search-result-meta {
    font-size: 0.75rem;
    color: var(--text-muted);
    margin-bottom: 6px;
}

.search-result-text {
    font-family: var(--font-sanskrit);
    font-size: 1.2rem;
    color: var(--text-primary);
    line-height: 1.8;
    word-wrap: break-word;
    overflow-wrap: break-word;
    user-select: text;
    -webkit-user-select: text;
    -moz-user-select: text;
    -ms-user-select: text;
}

.search-result-text mark {
    background-color: #ffeb3b; 
    color: #000;
    padding: 0 2px;
    border-radius: 2px;
    font-weight: 600;
}

.search-result-field {
    margin-bottom: 8px;
    padding: 6px 10px;
    background: rgba(255,255,255,0.5);
    border-radius: 4px;
}

.search-result-field:last-child {
    margin-bottom: 0;
}

.search-result-field-label {
    font-size: 0.75rem;
    font-weight: 600;
    color: var(--color-accent);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 2px;
    display: block;
}

.search-result-text mark {
    background: #ffff00;
    color: #000;
    padding: 0 2px;
    border-radius: 2px;
    font-weight: 500;
}

.search-no-results {
    text-align: center;
    padding: 40px 20px;
    color: var(--text-muted);
}

.search-no-results .icon {
    font-size: 2.5rem;
    margin-bottom: 12px;
}

.search-loading {
    text-align: center;
    padding: 40px 20px;
    color: var(--text-muted);
}

/* Responsive */
@media (max-width: 1200px) {
    .sidebar-right {
        display: none;
    }
}

@media (max-width: 900px) {
    .sidebar-left {
        position: static;
        width: 100%;
        height: auto;
        border-right: none;
        border-bottom: 1px solid var(--border-color);
    }
    
    .main-content {
        margin-left: 0;
        padding: var(--spacing-lg);
    }
    
    .page-container {
        flex-direction: column;
    }
}

@media (max-width: 600px) {
    .kandah-grid {
        grid-template-columns: 1fr;
    }
    
    .stats-row {
        flex-direction: column;
        gap: var(--spacing-lg);
    }
    
    .metadata-links {
        flex-direction: column;
    }
}

/* Audio Player Styles */
.audio-section {
    margin-top: var(--spacing-lg);
    display: flex;
    justify-content: center;
    width: 100%;
}

.audio-player-container {
    width: 100%;
    max-width: 400px;
    display: flex;
    justify-content: center;
}

.audio-player {
    width: 100%;
}

/* Mantra/Swara Stacking Styles - Matching renderPDF.py output */
.mantra-break {
    flex-basis: 100%;
    height: 1rem;
    width: 100%;
}

.mantra-word {
    display: inline-flex;
    flex-direction: column;
    align-items: stretch;
    vertical-align: top;
    margin: 0;
    padding: 0;
}

.mantra-text {
    font-family: var(--font-sanskrit);
    font-size: 1.6rem;
    line-height: 1.2;
    color: #000000;
}

.swara-text {
    font-family: var(--font-sanskrit);
    color: #c62828;
    font-size: 1.3rem;
    line-height: 1;
    text-align: center;
    margin-top: -0.2em;
    min-height: 1em;
    border-right: 1px solid transparent;
    padding-right: 2px;
}

.swara-left {
    text-align: left;
}

.mantra-verse {
    margin: 5px 0;
    display: inline-flex;
    flex-wrap: wrap;
    align-items: flex-start;
    text-align: center;
    gap: 0;
}

.word-space {
    width: 0.3em;
}

/* Vedic Accent Mark Styles - Zero-width positioning */
.accent-swarita {
    display: inline-block;
    width: 0;
    overflow: visible;
    color: #1565c0;
    font-weight: bold;
    font-size: 1.2em;
    position: relative;
    left: -0.1em;
    bottom: {sw_off};
    isolation: isolate;
}

.accent-anudatta {
    display: inline-block;
    width: 0;
    overflow: visible;
    color: #1565c0;
    font-weight: bold;
    font-size: 1.2em;
    position: relative;
    left: -0.1em;
    bottom: {an_off};
    isolation: isolate;
}

.accent-kampa {
    display: inline-block;
    width: 0;
    overflow: visible;
    color: #1565c0;
    font-weight: bold;
    font-size: 1.2em;
    position: relative;
    left: -0.1em;
    bottom: {ka_off};
}

.accent-trikampa {
    display: inline-block;
    width: 0;
    overflow: visible;
    color: #1565c0;
    font-weight: bold;
    font-size: 1.2em;
    position: relative;
    left: -0.1em;
    bottom: {tr_off};
}

.footnote-separator, .closing-separator {
    border: 0;
    border-top: 1px solid var(--border-color);
    margin: var(--spacing-xl) 0;
    width: 200px;
}

.closing-mantras-section {
    margin-top: var(--spacing-2xl);
    padding: var(--spacing-xl);
    text-align: center;
    background-color: #f8fafc; /* Muted Slate-50 background */
    border-radius: 12px;
    border: 1px solid #e2e8f0; /* Muted border */
    box-shadow: 0 1px 3px rgba(0,0,0,0.02);
}

.closing-mantras-content {
    font-family: var(--font-sanskrit);
    font-size: 1.25rem;
    color: #475569; /* Muted Slate-600 */
    line-height: 2;
}

.closing-mantra-line {
    margin-bottom: 0.5rem;
}

.footer {

}

.danda {
    margin: 0 0.2em;
}

.mantra-number {
    display: inline-block;
    white-space: nowrap;
    color: var(--primary-maroon);
    font-weight: 500;
    font-size: 1.6rem;
}

/* Footnote Section Styles - matching renderPDF.py */
.footnotes {
    margin-top: var(--spacing-lg);
}

.footnote-separator {
    border: none;
    border-top: 1px solid var(--border-color);
    margin: 20px 0 10px 0;
    width: 40%;
    margin-left: 0;
}

    padding: 10px 0;
    text-align: left;
    font-size: 0.9rem;
    line-height: 1.5;
    font-family: var(--font-sanskrit);
}

.footnote-item {
    padding: 5px 0;
    display: flex;
    align-items: flex-start;
}

.footnote-item .footnote-ref {
    color: #1565c0;
    font-weight: bold;
    margin-right: 0.5em;
    min-width: 1.5em;
    font-family: var(--font-sanskrit);
}

.footnote-item .footnote-text {
    margin-left: 0.5em;
}

/* Inline footnote superscript references - matching renderPDF.py */
sup.footnote-ref {
    font-size: 0.7em;
    vertical-align: super;
    line-height: 0;
    position: relative;
    top: -0.5em;
}

sup.footnote-ref a {
    color: #1565c0;
    text-decoration: none;
    font-weight: bold;
}

sup.footnote-ref a:hover {
    text-decoration: underline;
}

/* Print Styles */
@media print {
    .sidebar-left, .sidebar-right {
        display: none;
    }
    
    .main-content {
        margin: 0;
        max-width: 100%;
    }
}
/* Classification & Index Styles */
.classification-grid {
    display: grid;
    gap: var(--spacing-xl);
    max-width: 800px;
    margin: 0 auto;
}

.class-section {
    background: var(--bg-card);
    padding: var(--spacing-xl);
    border-radius: 8px;
    border: 1px solid var(--border-color);
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.class-section h2 {
    color: var(--accent-orange);
    text-align: center;
    margin-bottom: var(--spacing-lg);
    font-size: 1.4rem;
}

.button-row {
    display: flex;
    flex-wrap: wrap;
    gap: var(--spacing-md);
    justify-content: center;
}

.index-btn {
    display: inline-block;
    padding: var(--spacing-md) var(--spacing-lg);
    background: var(--bg-card);
    color: var(--text-primary);
    border-radius: 4px;
    border: 1px solid var(--border-color);
    font-family: var(--font-heading);
    transition: all 0.2s ease;
}

.index-btn:hover {
    border-color: var(--primary-maroon);
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    color: var(--text-primary);
    text-decoration: none;
    transform: translateY(-2px);
}

.index-btn:hover {
    border-color: var(--primary-maroon);
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    color: var(--text-primary);
    text-decoration: none;
    transform: translateY(-2px);
}

.anya-vargeekaran-card {
    background: transparent;
    padding: 2.5rem 0;
    border-top: 3px solid #C08535;
    border-bottom: 3px solid #C08535;
    max-width: 900px;
    margin: 4rem auto;
    text-align: center;
}

.anya-vargeekaran-card h2 {
    color: var(--color-secondary);
    font-size: 2.2rem;
    margin-bottom: 2rem;
    border-bottom: none;
    padding-bottom: 0;
    text-transform: none;
    font-weight: 700;
}

.index-grid-homepage {
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
    gap: 0.75rem;
    margin-top: 0.5rem;
}

.index-link-item {
    display: inline-flex;
    align-items: center;
    padding: 0.5rem 1.5rem;
    background: #FFFDF8;
    border-radius: 40px;
    border: 1px solid #D8CCB8;
    text-decoration: none;
    transition: all 0.2s ease;
    color: #FF6B35;
    font-family: var(--font-sanskrit);
    font-weight: 600;
    gap: 0.6rem;
}

.index-link-item .title {
    font-size: 1.5rem;
}

.index-link-item .stats {
    font-size: 0.8rem;
    color: #888;
    position: relative;
    top: 3px; /* Align with Devanagari midline */
}

.index-link-item:hover {
    border-color: var(--primary-maroon);
    background: white;
    box-shadow: 0 3px 10px rgba(0,0,0,0.04);
    text-decoration: none;
    transform: translateY(-1px);
}


.index-list {
    max-width: 800px;
    margin: 0 auto;
}

.index-entry {
    margin-bottom: var(--spacing-lg);
    border-bottom: 1px solid var(--border-light);
    padding-bottom: var(--spacing-sm);
}

.index-term {
    font-family: var(--font-heading);
    font-size: 1.2rem;
    color: var(--primary-maroon);
    margin-bottom: var(--spacing-xs);
    font-weight: 600;
}

.index-refs {
    font-size: 0.9rem;
    line-height: 1.6;
}

.index-refs a {
    color: var(--text-link);
    margin-right: 8px;
    display: inline-block;
}

.index-char-header {
    padding-bottom: 4px;
}

/* Classification Table */
.classification-table {
    width: 100%;
    margin-top: 2px;
    margin-bottom: 15px;
    border-collapse: collapse;
    font-size: 1.1rem;
    background: rgba(255, 255, 255, 0.5);
    border-radius: 4px;
    overflow: hidden;
}

.sama-entry .number {
    font-size: 0.9rem;
}

.classification-table th, .classification-table td {
    padding: 6px 10px;
    text-align: left;
    border: 1px solid var(--border-light);
}

.classification-table th {
    background-color: var(--primary-gold);
    color: white;
    font-weight: 500;
}

.class-label {
    color: var(--text-muted);
    font-size: 0.8rem;
    font-family: var(--font-heading);
}

.class-value {
    font-family: var(--font-sanskrit);
    font-size: 1.3rem;
    color: var(--color-secondary);
}

/* Classification Grid Home */
.classification-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: var(--spacing-xl);
    margin-top: var(--spacing-2xl);
}

@media (max-width: 900px) {
    .classification-grid {
        grid-template-columns: repeat(2, 1fr);
    }
}

@media (max-width: 600px) {
    .classification-grid {
        grid-template-columns: 1fr;
    }
}

.class-card {
    background: white;
    padding: var(--spacing-xl);
    border-radius: 12px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    border: 1px solid var(--border-light);
    text-align: center;
    text-decoration: none;
    color: inherit;
    transition: all 0.3s ease;
}

.class-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 25px rgba(0,0,0,0.1);
    border-color: var(--primary-maroon);
}

.class-card h2 {
    color: var(--primary-maroon);
    font-size: 1.8rem;
    margin-bottom: var(--spacing-md);
}

.class-card .count {
    font-size: 1.1rem;
    color: var(--text-muted);
}

/* Index Summarization */

/* Index Summarization */
.index-section-header {
    font-family: var(--font-heading);
    color: var(--primary-maroon);
    margin: 2rem 0 1rem 0;
    font-size: 1.6rem;
    border-bottom: 2px solid var(--primary-gold);
    padding-bottom: 6px;
}

.top-20-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
    margin-bottom: 2rem;
}

@media (max-width: 1100px) {
    .top-20-grid {
        grid-template-columns: repeat(2, 1fr);
    }
}

@media (max-width: 768px) {
    .top-20-grid {
        grid-template-columns: 1fr;
    }
}

.alphabet-nav {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    background: #f9f9f9;
    padding: 1.5rem;
    border-radius: 10px;
    margin-bottom: 2.5rem;
    border: 1px solid var(--border-light);
    box-shadow: inset 0 2px 4px rgba(0,0,0,0.02);
}

.alpha-btn {
    display: flex;
    align-items: center;
    padding: 0.5rem 1rem;
    background: #eeeeee; /* Match image light gray */
    border: 1px solid transparent;
    border-radius: 6px;
    text-decoration: none;
    color: var(--primary-maroon);
    transition: all 0.2s ease;
    min-width: 4.5rem;
    justify-content: center;
}

.alpha-btn:hover {
    background: white;
    border-color: var(--primary-gold);
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    transform: translateY(-2px);
}

.alpha-char {
    font-family: var(--font-sanskrit);
    font-weight: 700;
    font-size: 1.2rem;
    margin-right: 8px;
    color: #b03a2e; /* Slightly brighter red for letters */
}

.alpha-count {
    font-size: 0.75rem;
    color: #666;
    font-weight: 500;
    position: relative;
    top: 2px; /* Pull down to align with Devanagari midline */
}

.index-list-container {
    background: #f9f9f9;
    padding: 1.5rem;
    border-radius: 10px;
    margin-top: 1rem;
    border: 1px solid var(--border-light);
    box-shadow: inset 0 2px 4px rgba(0,0,0,0.01);
    overflow: hidden;
}

.index-items-grid {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    width: 100%;
}

/* Maintain equal heights for the Headers Index only on home page */
.header-index-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    grid-auto-rows: 1fr;
    gap: 1rem;
    column-count: auto;
}

@media (max-width: 1100px) {
    .index-items-grid {
        grid-template-columns: repeat(2, 1fr);
    }
    .header-index-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }
}

@media (max-width: 700px) {
    .index-items-grid {
        grid-template-columns: 1fr;
    }
    .header-index-grid {
        grid-template-columns: minmax(0, 1fr);
    }
}

.index-item-card {
    background: #eeeeee;
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 0.6rem 1rem;
    display: flex;
    flex-direction: column;
    justify-content: center;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 1px 3px rgba(0,0,0,0.02);
    box-sizing: border-box;
}

/* New compact list entry for Rishi/Devata/Chandas indices */
.index-list-item {
    padding: 0.4rem 0.5rem;
    background: transparent;
    border-bottom: 1px solid #eee;
    display: block;
    width: 100%;
    box-sizing: border-box;
}

.index-list-item:hover {
    background: #fdfdfd;
    color: var(--color-primary);
}

.index-item-card:hover {
    background: white;
    border-color: var(--primary-gold);
    box-shadow: 0 6px 15px rgba(0,0,0,0.08);
    transform: translateY(-2px);
}

/* Compact version for Headers Index */
.simple-card {
    padding: 0.6rem 1rem;
    min-height: 48px;
}

.simple-card .item-main {
    align-items: center;
    overflow: hidden;
    min-width: 0;
    width: 100%;
    gap: 0.75rem;
}

.simple-card .item-name {
    font-size: 1.05rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    flex: 1;
    min-width: 0;
}

.simple-card .item-count-badge {
    padding: 1px 8px;
    font-size: 0.75rem;
}

.item-main {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 0.75rem;
    width: 100%;
    min-width: 0;
}

.item-name {
    font-family: var(--font-sanskrit);
    font-size: 1.3rem;
    color: var(--text-primary);
    font-weight: 600;
    line-height: 1.3;
}

.item-count-badge {
    background: transparent;
    color: #777;
    padding: 1px 6px;
    border-radius: 3px;
    font-size: 0.75rem;
    font-weight: 600;
    flex-shrink: 0;
}

.item-refs {
    margin-top: 0.2rem;
    display: block;
    line-height: 1.8;
}

/* Custom scrollbar for compact view */
.item-refs::-webkit-scrollbar {
    width: 3px;
}
.item-refs::-webkit-scrollbar-thumb {
    background: #ccc;
    border-radius: 10px;
}

.item-refs a {
    font-size: 0.8rem;
    color: var(--text-link);
    text-decoration: none;
    margin-right: 0.5rem;
    display: inline-block;
}

.item-count {
    font-size: 0.8rem;
    color: var(--text-muted);
    font-weight: 500;
}

.item-refs a::after {
    content: ',';
    color: #999;
}

.item-refs a:last-child::after {
    content: '';
}

.item-refs a:hover {
    text-decoration: underline;
    color: var(--primary-maroon);
}

.index-char-group {
    margin-bottom: 2rem;
    scroll-margin-top: 2rem;
}

.index-char-title {
    font-size: 1.8rem;
    color: var(--primary-maroon);
    font-family: var(--font-sanskrit);
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.8rem;
}

.index-char-title::after {
    content: '';
    flex-grow: 1;
    height: 3px;
    background: var(--primary-gold);
    border-radius: 2px;
}

.rishi-card {
    display: flex;
    align-items: center;
    background: white;
    padding: 0.5rem 0.8rem;
    border-radius: 6px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
    border: 1px solid var(--border-light);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    text-decoration: none;
    color: inherit;
    min-height: 54px;
}

.rishi-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 3px 10px rgba(0,0,0,0.08);
    border-color: var(--primary-maroon);
}

.rest-card {
    background: #f8f8f8;
    border: 2px dashed var(--border-light);
    justify-content: center;
    background-image: linear-gradient(135deg, rgba(0,0,0,0.02) 25%, transparent 25%, transparent 50%, rgba(0,0,0,0.02) 50%, rgba(0,0,0,0.02) 75%, transparent 75%, transparent);
    background-size: 20px 20px;
}

.rest-card .rishi-rank {
    background: var(--text-muted);
}

.rest-card .rishi-name {
    color: var(--text-secondary);
    font-style: italic;
}

.rest-card:hover {
    background-color: #f1f1f1;
    border-color: var(--primary-gold);
}

.rishi-rank {
    background: var(--primary-maroon);
    color: white;
    width: 28px;
    height: 28px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 500; /* Medium instead of bold */
    font-size: 0.85rem;
    margin-right: 0.8rem;
    flex-shrink: 0;
}

.rishi-info {
    flex-grow: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
    overflow: hidden;
}

.rishi-name {
    font-family: var(--font-sanskrit);
    font-weight: 400; /* Regular instead of semi-bold */
    font-size: 1.15rem;
    display: block;
    line-height: 1.2;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.rishi-count {
    color: var(--text-secondary);
    font-size: 0.8rem;
    text-align: right;
    font-weight: 400; /* Regular instead of semi-bold */
    margin-left: 1rem;
    white-space: nowrap;
}


.count-tag {
    font-size: 0.8rem;
    color: var(--text-muted);
    font-weight: 400;
    margin-left: 8px;
}


.index-char-group {
    break-inside: avoid-column;
    margin-bottom: 2rem;
}
'''
        # Replace placeholders for font and offsets
        css = css.replace('{self.font}', self.font)
        css = css.replace('{self.font_sans}', self.font_sans)
        css = css.replace('{sw_off}', sw_off)
        css = css.replace('{ka_off}', ka_off)
        css = css.replace('{tr_off}', tr_off)
        css = css.replace('{an_off}', an_off)

        if getattr(self, 'is_malayalam', False):
            font_face = '''
@font-face {
    font-family: 'JaimineeyaSwara';
    src: url('../fonts/JaimineeyaSwara.ttf') format('truetype');
    font-weight: normal;
    font-style: normal;
}
'''
            malayalam_css = '''
/* Malayalam Swara & Modifier Typography */
.mantra-word {
    display: inline-flex;
    flex-direction: column;
    align-items: center;
    justify-content: flex-end;
    vertical-align: bottom;
    position: relative;
}
.swara-text {
    font-family: 'JaimineeyaSwara', serif !important;
    color: #c62828 !important;
    font-weight: bold;
    font-size: 1.10rem !important;
    line-height: 1;
    text-align: center;
    margin-bottom: 4px;
    min-height: 1.1em;
    user-select: none;
}
.mantra-text {
    font-family: 'Noto Serif Malayalam', serif !important;
    font-size: 1.45rem;
    line-height: 1.2;
    color: #000000;
    position: relative;
}
.swara-mod {
    color: #0284c7;
    font-family: 'JaimineeyaSwara', serif !important;
    font-weight: bold;
    line-height: 1;
}
.swara-mod.mod-a {
    position: absolute;
    top: -0.28em;
    left: 100%;
    transform: translateX(-40%);
    font-size: 1.05rem;
    pointer-events: none;
}
.swara-mod.mod-a1 {
    position: absolute;
    top: -0.28em;
    left: 100%;
    transform: translateX(-40%);
    font-size: 1.25rem;
    pointer-events: none;
}
.swara-mod.mod-b {
    position: absolute;
    top: -0.22em;
    left: 100%;
    transform: translateX(-50%);
    pointer-events: none;
    display: inline-flex;
    flex-direction: column;
    align-items: center;
}
.swara-mod.mod-b .caret-glyph {
    display: block;
    color: #0284c7;
    font-size: 1.05rem;
    line-height: 1;
}
.swara-mod.mod-b .swara-on-caret {
    position: absolute;
    top: -1.70em;
    left: 50%;
    transform: translateX(-50%);
    color: #c62828 !important;
    font-size: 0.95rem;
    font-weight: bold;
    font-family: 'JaimineeyaSwara', serif !important;
    line-height: 1;
    white-space: nowrap;
}
.swara-mod.mod-c {
    position: absolute;
    top: -0.15em;
    right: -0.35em;
    font-size: 0.95rem;
}
.swara-mod.mod-d {
    position: absolute;
    top: -0.30em;
    left: 100%;
    transform: translateX(-40%);
    font-size: 1.05rem;
    pointer-events: none;
}
.swara-mod.mod-e {
    position: relative;
    margin-left: 0.15em;
    font-size: 1.15rem;
    vertical-align: -0.05em;
}
.swara-mod.mod-f {
    position: relative;
    margin-left: 0.15em;
    font-size: 1.15rem;
    vertical-align: -0.05em;
}
.swara-mod.mod-g {
    position: absolute;
    bottom: -0.38em;
    left: 28%;
    transform: translateX(-50%);
    font-size: 1.15rem;
}
.swara-mod.mod-h {
    position: absolute;
    top: -0.35em;
    left: 50%;
    transform: translateX(-50%);
    font-size: 1.05rem;
}
.mantra-punct {
    font-family: 'Noto Serif Malayalam', serif !important;
    font-size: 1.45rem;
    line-height: 1.2;
    color: #0284c7;
    margin-right: 0.05em;
}
'''
            css = font_face + css + malayalam_css

        with open(self.output_dir / 'css' / 'styles.css', 'w', encoding='utf-8') as f:
            f.write(css)
            
    def _generate_js(self):
        """Generate JavaScript for interactivity with deterministic navigation"""
        js = r'''// Jaimineeya Samavedam Website JavaScript
// Deterministic Navigation System v2.1

document.addEventListener('DOMContentLoaded', function() {
    console.log("[JS] Jaimineeya Website Loaded");

    // Centralized Scroll Handler
    const scrollToTarget = (targetId, smooth = true) => {
        if (!targetId) return;
        
        // Clean hash (strip #)
        const id = targetId.startsWith('#') ? targetId.substring(1) : targetId;
        const element = document.getElementById(id);
        
        if (element) {
            console.log("[Scroll] Navigating to:", id);
            
            // Fixed header offset (adjust based on CSS)
            const headerOffset = 100;
            const elementPosition = element.getBoundingClientRect().top;
            const offsetPosition = elementPosition + window.pageYOffset - headerOffset;

            window.scrollTo({
                top: offsetPosition,
                behavior: smooth ? 'smooth' : 'auto'
            });
            
            return true;
        }
        console.warn("[Scroll] Target not found:", id);
        return false;
    };

    // 1. Handle Initial Load Scroll (Deterministic Wait)
    window.addEventListener('load', () => {
        if (window.location.hash) {
            console.log("[Load] Initial hash detected:", window.location.hash);
            // Wait for Sanskrit web fonts and layout to finish settling
            setTimeout(() => {
                scrollToTarget(window.location.hash, false);
            }, 200);
        }
    });

    // 2. Handle Hash Changes (Link clicks, History)
    window.addEventListener('hashchange', () => {
        console.log("[HashChange] New hash:", window.location.hash);
        scrollToTarget(window.location.hash, true);
    });

    // 3. Smooth scroll for ALL internal links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const hash = this.getAttribute('href');
            if (hash === '#') return;
            
            e.preventDefault();
            // Update hash which triggers hashchange listener
            if (window.location.hash === hash) {
                // Manually trigger if hash is identical
                scrollToTarget(hash, true);
            } else {
                window.location.hash = hash;
            }
        });
    });

    // 4. Parva Map for Jump resolution
    const parvaMap = {};
    document.querySelectorAll('.parva-link').forEach(link => {
        const href = link.getAttribute('href') || '';
        const ssMatch = href.match(/kandah[/]([^/]+)[/]/);
        if (ssMatch) {
            const displayNum = parseInt(link.textContent.trim());
            if (!isNaN(displayNum)) {
                parvaMap[displayNum] = ssMatch[1];
            }
        }
    });

    // 5. Consolidated Navigation Logic (Deterministic P.K.S Resolution)
    window.resolveJump = (val, smooth = true) => {
        if (!val) return;
        
        console.log("[Navigation] Resolving reference:", val);
        const parts = val.split('.');
        
        // Resolve prefix based on current depth
        const path = window.location.pathname;
        let depth = 0;
        if (path.includes('/kandah/')) depth = 2;
        else if (path.includes('/classification/') || path.includes('/vargeekaran/')) depth = 1;
        const prefix = '../'.repeat(depth);

        if (parts.length >= 2) {
            const parvaNum = parseInt(parts[0]);
            
            // Site-aware prefix resolution (Handles Samhita vs Aaranam cross-links)
            let sitePrefix = "";
            const currentPath = window.location.pathname;
            
            // Only switch sites if the parvaNum is NOT in our local parvaMap
            if (!parvaMap[parvaNum]) {
                if (parvaNum <= 6 && currentPath.includes('/aaranam/')) {
                    sitePrefix = "../samhita/";
                } else if (parvaNum > 6 && currentPath.includes('/samhita/')) {
                    sitePrefix = "../aaranam/";
                }
            }

            const parvaId = parvaMap[parvaNum] || `supersection_${parts[0]}`;
            const kandahId = parts[1];
            
            // Deterministic hash: point to specific Samam Sequence ID (#sama-N)
            const targetHash = parts.length === 3 ? `#sama-${parts[2]}` : "";
            const targetPage = `kandah/${parvaId}/${kandahId}.html`;
            const currentPage = window.location.pathname;
            
            console.log("[Navigation] Target determined:", prefix + sitePrefix + targetPage + targetHash);

            if (currentPage.endsWith(targetPage) || currentPage.includes('/' + targetPage)) {
                // Same file: Just scroll
                if (window.location.hash === targetHash) scrollToTarget(targetHash, true);
                else window.location.hash = targetHash;
            } else {
                // Different file: Redirect
                window.location.assign(prefix + sitePrefix + targetPage + targetHash);
            }
            return true;
        }
        return false;
    };

    // Link Jump Box to Consolidated Logic
    const jumpInput = document.getElementById('sidebar-jump');
    const handleJump = () => {
        const val = jumpInput ? jumpInput.value.trim() : '';
        window.resolveJump(val, true);
    };

    // 6. Sidebar Highlighting (Intersection Observer)
    const observerOptions = {
        root: null,
        rootMargin: '-100px 0px -70% 0px',
        threshold: 0
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const samaStart = entry.target.getAttribute('data-sama-start');
                if (samaStart) {
                    document.querySelectorAll('.nav-links a.active, .jump-links a.active').forEach(l => {
                        l.classList.remove('active');
                    });
                    
                    const links = document.querySelectorAll(`.nav-links a[href="#sama-${samaStart}"], .jump-links a[href="#sama-${samaStart}"]`);
                    links.forEach(l => {
                        l.classList.add('active');
                    });
                }
            }
        });
    }, observerOptions);

    document.querySelectorAll('.sama-entry').forEach(el => observer.observe(el));

    if (jumpInput) {
        jumpInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') handleJump();
        });
    }

    // Search Interactivity (Standard)
    const searchModal = document.getElementById('search-modal');
    const searchOverlay = document.getElementById('search-overlay');
    const searchInput = document.getElementById('search-input');
    const searchClose = document.getElementById('search-close');
    const searchResults = document.getElementById('search-results');
    const searchBtn = document.querySelector('.search-btn');
    let searchIndex = null;
    
    const loadSearchIndex = () => {
        if (typeof SEARCH_INDEX !== 'undefined') {
            searchIndex = SEARCH_INDEX;
            if (searchResults) searchResults.innerHTML = '';
        } else {
            if (searchResults) searchResults.innerHTML = '<div class="search-no-results"><div class="icon">⚠️</div>Could not load search index.</div>';
        }
    };
    
    const openSearchModal = () => {
        if (searchModal) {
            searchModal.classList.add('active');
            searchOverlay.classList.add('active');
            if (searchInput) searchInput.focus();
            if (!searchIndex) loadSearchIndex();
        }
    };
    
    const closeSearchModal = () => {
        if (searchModal) searchModal.classList.remove('active');
        if (searchOverlay) searchOverlay.classList.remove('active');
    };
    
    if (searchClose) searchClose.addEventListener('click', closeSearchModal);
    if (searchOverlay) searchOverlay.addEventListener('click', closeSearchModal);
    
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') closeSearchModal();
        if (e.key === '/' && !e.ctrlKey && !e.metaKey && document.activeElement.tagName !== 'INPUT') {
            e.preventDefault();
            openSearchModal();
        }
    });
    
    if (searchBtn) {
        searchBtn.addEventListener('click', function(e) {
            e.preventDefault();
            openSearchModal();
        });
    }
    
    document.querySelectorAll('.top-nav a').forEach(link => {
        if (link.textContent.includes('Search') || link.textContent.includes('अन्वेषणम्')) {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                openSearchModal();
            });
        }
    });
    
    // Detect current page depth for relative path resolution
    const path = window.location.pathname;
    let depth = 0;
    if (path.includes('/kandah/')) depth = 2;
    else if (path.includes('/classification/') || path.includes('/vargeekaran/')) depth = 1;
    const depthPrefix = '../'.repeat(depth);
    
const highlightText = (text, query, devanagariQuery) => {
        if (!text) return text;
        if (!query && !devanagariQuery) return text;

        let searchQ = query;
        if (devanagariQuery && devanagariQuery.length > 0) {
            searchQ = devanagariQuery;
        }

        if (text.toLowerCase().indexOf(searchQ.toLowerCase()) !== -1) {
            const re = new RegExp(searchQ.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'gi');
            return text.replace(re, '<mark>$&</mark>');
        }

        return text;
    };

    const latinToDevanagari = (text) => {
        const mapping = {
            'aa': 'आ', 'ee': 'ई', 'oo': 'ऊ', 'ai': 'ऐ', 'au': 'औ', 'ri': 'ऋ', 'rii': 'ॠ',
            'kh': 'ख', 'gh': 'घ', 'ch': 'च', 'chh': 'छ', 'jh': 'झ', 'th': 'थ', 'dh': 'ध',
            'ph': 'फ', 'bh': 'भ', 'sh': 'श', 'ng': 'ङ', 'nj': 'ञ', 'nn': 'ण',
            'a': 'अ', 'i': 'इ', 'u': 'उ', 'e': 'ए', 'o': 'ओ',
            'k': 'क', 'g': 'ग', 'c': 'च', 'j': 'ज', 't': 'त', 'd': 'द', 'n': 'न',
            'p': 'प', 'b': 'ब', 'm': 'म', 'y': 'य', 'r': 'र', 'l': 'ल', 'v': 'व', 'w': 'व', 's': 'स', 'h': 'ह',
            '.': '।', '|': '॥'
        };
        let result = text.toLowerCase();
        for (const [k, v] of Object.entries(mapping).sort((a, b) => b[0].length - a[0].length)) {
            result = result.replaceAll(k, v);
        }
        return result;
    };

    const performSearch = (query, callIsLatin, callDevanagariQuery) => {
        if (!query || query.length < 2 || !searchIndex) return [];
        const q = query.toLowerCase().trim();
        const results = [];

        const isLatin = callIsLatin !== undefined ? callIsLatin : (/[a-z]/.test(q) && !/[\u0900-\u097F]/.test(q));

        const normalizeLatin = (text) => {
            if (!text) return "";
            const map = {
                'aa': 'a', 'ee': 'i', 'oo': 'u', 'ii': 'i', 'uu': 'u',
                'kh': 'k', 'gh': 'g', 'ch': 'c', 'jh': 'j', 'th': 't', 'dh': 'd', 'ph': 'p', 'bh': 'b',
                'sh': 's', 'z': 's', 'w': 'v', 'ñ': 'n', 'ṅ': 'n', 'ṇ': 'n', 'ś': 's', 'ṣ': 's',
                'ā': 'a', 'ī': 'i', 'ū': 'u', 'ṛ': 'r', 'ṭ': 't', 'ḍ': 'd', 'ḥ': 'h', 'ṃ': 'n', 'ṁ': 'n'
            };
            let result = text.toLowerCase().replace(/[^a-z]/g, '');
            for (const [k, v] of Object.entries(map)) {
                result = result.replaceAll(k, v);
            }
            return result;
        };

        // Use the passed devanagariQuery if provided, otherwise compute it
        const devanagariQuery = callDevanagariQuery !== undefined ? callDevanagariQuery : (isLatin ? latinToDevanagari(q) : null);

        for (const entry of searchIndex) {
            let score = 0;
            let matchedFields = [];
            
            const checkField = (text, fieldScore, fieldName, displayHtml) => {
                if (!text) return;
                // Remove spaces for comparison
                const wsRegex = /\s+/g;
                const textNoSpaces = text.replace(wsRegex, '');
                const qNoSpaces = q.replace(wsRegex, '');
                
                // Check exact match
                if (textNoSpaces.toLowerCase().includes(qNoSpaces)) {
                    score += fieldScore;
                    matchedFields.push({ name: fieldName, text: text, html: displayHtml });
                    return;
                }
                
                // Check permissive (diacritic-stripped) match
                // We must strip parentheses content for Samam swara ignoring
                const stripAll = (t) => t.replace(/\([^)]*\)/g, '').replace(/[\u093E-\u094D\u0951-\u0957\u1CD0-\u1CFF\u0964\u0965\u0966-\u096F0-9]/g, '');
                const textPermissive = stripAll(textNoSpaces);
                const qPermissive = stripAll(qNoSpaces);
                if (textPermissive.toLowerCase().includes(qPermissive)) {
                    score += fieldScore * 0.8;
                    matchedFields.push({ name: fieldName, text: text, html: displayHtml, matchedInDevanagari: true });
                    return;
                }
                
                // Check Latin match if input is Latin
                if (isLatin) {
                    const qLatin = normalizeLatin(qNoSpaces);
                    // Match against various latin fields found in entries
                    if (fieldName === 'Mantra' && entry.mantra_latin && entry.mantra_latin.includes(qLatin)) {
                        score += fieldScore * 0.75;
                        matchedFields.push({ name: fieldName, text: text, html: displayHtml });
                    } else if (fieldName === 'Rik' && entry.rik_latin && entry.rik_latin.includes(qLatin)) {
                        score += fieldScore * 0.75;
                        matchedFields.push({ name: fieldName, text: text, html: displayHtml });
                    } else if (fieldName === 'Title' && entry.title_latin && entry.title_latin.includes(qLatin)) {
                        score += fieldScore * 0.75;
                        matchedFields.push({ name: fieldName, text: text, html: displayHtml });
                    } else if (devanagariQuery) {
                        // Fallback: check Devanagari conversion match
                        const textLatin = textNoSpaces.replace(/[\u093E-\u094D\u0951-\u0954]/g, '');
                        const dqNoSpaces = devanagariQuery.replace(wsRegex, '');
                        if (textLatin.toLowerCase().includes(dqNoSpaces.toLowerCase())) {
                            score += fieldScore * 0.65;
                            matchedFields.push({ name: fieldName, text: text, html: displayHtml });
                        }
                    }
                }
            };
            
            checkField(entry.mantra_clean, 10, 'Mantra', entry.mantra_html);
            checkField(entry.rik_clean, 8, 'Rik', entry.rik_html);
            
            for (const c of entry.classifications) {
                checkField(c.rishi_clean, 7, 'Rishi', c.rishi);
                // Latin match for Rishi
                if (isLatin && c.rishi_latin && c.rishi_latin.includes(normalizeLatin(q))) {
                    score += 5; matchedFields.push({ name: 'Rishi', text: c.rishi_clean, html: c.rishi });
                }
                
                checkField(c.devata_clean, 6, 'Devata', c.devata);
                // Latin match for Devata
                if (isLatin && c.devata_latin && c.devata_latin.includes(normalizeLatin(q))) {
                    score += 4; matchedFields.push({ name: 'Devata', text: c.devata_clean, html: c.devata });
                }
                
                checkField(c.chandas_clean, 4, 'Chandas', c.chandas);
            }
            
            checkField(entry.title_clean, 5, 'Title', entry.title_html);
            checkField(entry.metadata_clean, 3, 'Metadata', entry.metadata_html);
            
            if (score > 0) {
                results.push({ ...entry, score, matchedFields });
            }
        }
        results.sort((a, b) => b.score - a.score);
        return results.slice(0, 50);
    };
    
    if (searchInput) {
        let debounceTimer;
        searchInput.addEventListener('input', function() {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => {
                const query = this.value.trim();
                if (!query) {
                    if (searchResults) searchResults.innerHTML = '';
                    return;
                }
                if (!searchIndex) {
                    if (searchResults) searchResults.innerHTML = '<div class="search-loading">Loading search index...</div>';
                    return;
                }
                const q = query.toLowerCase().trim();
                const isLatin = /[a-z]/.test(q) && !/[\u0900-\u097F]/.test(q);
                const devanagariQuery = isLatin ? latinToDevanagari(q) : null;
                const results = performSearch(query, isLatin, devanagariQuery);
                if (results.length === 0) {
                    searchResults.innerHTML = '<div class="search-no-results"><div class="icon">🔍</div>No results found for "' + query + '"</div>';
                    return;
                }
                let html = '';
                for (const r of results) {
                    const classInfo = r.classifications.length > 0 
                        ? r.classifications.map(c => [c.rishi, c.devata, c.chandas].filter(Boolean).join(' | ')).filter(Boolean).join('; ')
                        : '';
                    const fieldLabels = { 'Mantra': 'मन्त्र', 'Rik': 'ऋक्', 'Rishi': 'ऋषि', 'Devata': 'देवता', 'Chandas': 'छन्दस्', 'Title': 'शीर्षक', 'Metadata': 'विवरण' };
                    let fieldsHtml = '';
                    for (const mf of r.matchedFields) {
                        const highlighted = highlightText(mf.html || mf.text, query, devanagariQuery);
                        const label = fieldLabels[mf.name] || mf.name;
                        fieldsHtml += `<div class="search-result-field"><span class="search-result-field-label">${label}</span><div class="search-result-text">${highlighted}</div></div>`;
                    }
                    html += `<div class="search-result-item">
                        <div class="search-result-ref"><a href="${depthPrefix}${r.link}">${r.ref} — ${r.parva_title}, Kandah ${r.kandah_num}</a></div>
                        <div class="search-result-meta">${classInfo || ''}</div>
                        ${fieldsHtml}
                    </div>`;
                }
                searchResults.innerHTML = html;
                
                // Add click handlers to result items for navigation
                document.querySelectorAll('.search-result-item').forEach(item => {
                    let startX, startY;
                    item.addEventListener('mousedown', function(e) {
                        if (e.button !== 0) return;
                        startX = e.clientX;
                        startY = e.clientY;
                    });
                    item.addEventListener('mouseup', function(e) {
                        if (e.button !== 0) return;
                        const dx = Math.abs(e.clientX - startX);
                        const dy = Math.abs(e.clientY - startY);
                        if (dx > 5 || dy > 5) return;
                        const selection = window.getSelection();
                        if (selection && selection.toString().trim().length > 0) {
                            return;
                        }
                        const link = this.querySelector('.search-result-ref a');
                        if (link) {
                            // Extract reference from text (e.g. "1.1.1 — ...")
                            const refPart = link.textContent.split('—')[0].trim();
                            if (refPart && window.resolveJump) {
                                e.preventDefault();
                                window.resolveJump(refPart, true);
                                closeSearchModal();
                            } else {
                                window.location.href = link.href;
                            }
                        }
                    });
                    // Double-click always navigates
                    item.addEventListener('dblclick', function(e) {
                        const link = this.querySelector('.search-result-ref a');
                        if (link) {
                            window.location.href = link.href;
                        }
                    });
                });
            }, 250);
        });
    }
    
    // Audio error handling
    document.querySelectorAll('audio').forEach(audio => {
        audio.addEventListener('error', function() {
            const container = this.closest('.audio-section');
            if (container) {
                container.innerHTML = `
                    <div class="audio-pending">
                        <span>🎵</span>
                        <span>Audio coming soon</span>
                    </div>
                `;
            }
        });
    });
});
'''
        with open(self.output_dir / 'js' / 'main.js', 'w', encoding='utf-8') as f:
            f.write(js)

    def _clean_text_for_search(self, html_text: str) -> str:
        """Strip HTML tags and swara spans to get plain Devanagari text for search matching"""
        if not html_text:
            return ""
        text = re.sub(r'<[^>]+>', ' ', html_text)
        # Remove swara notation (text within parentheses) for search matching
        text = re.sub(r'\([^)]*\)', '', text)
        # Normalize various types of whitespace and remove zero-width characters
        text = re.sub(r'\s+', ' ', text)  # Convert multiple whitespace to single space
        text = text.replace('\u00A0', ' ')  # Non-breaking space to regular space
        text = text.replace('\u200B', '')   # Zero-width space
        text = text.replace('\u200C', '')   # Zero-width non-joiner
        text = text.replace('\u200D', '')   # Zero-width joiner
        text = text.replace('\u2060', '')   # Word joiner
        text = text.strip()
        return text

    def _strip_diacritics(self, text: str) -> str:
        """Remove Devanagari combining marks (diacritics) for permissive matching"""
        if not text:
            return ""
        # Remove combining marks (devanagari diacritics range)
        # Keep base characters, remove marks like ि ी े ै ो ौ etc.
        diacritics = ''.join([chr(c) for c in range(0x0900, 0x0903)])  # chandrabindu, anusvara, visarga
        diacritics += ''.join([chr(c) for c in range(0x093E, 0x094F)])  # vowel marks
        diacritics += ''.join([chr(c) for c in range(0x0951, 0x0958)])  # accent marks
        diacritics += ''.join([chr(c) for c in range(0x1CD0, 0x1D00)])  # Vedic Extensions (accents)
        diacritics += '\u0964\u0965'  # । and ॥
        diacritics += ''.join([chr(c) for c in range(0x0966, 0x0970)])  # Devanagari digits
        diacritics += '0123456789'  # ASCII digits
        result = []
        for char in text:
            if char not in diacritics:
                result.append(char)
        return ''.join(result)

    def _transliterate_to_latin(self, text: str) -> str:
        """Convert Devanagari to Super-Permissive Latin for fuzzy matching"""
        if not text:
            return ""
        # Base mapping for Super-Permissive Latin (collapses similar sounds)
        mapping = {
            'अ': 'a', 'आ': 'a', 'इ': 'i', 'ई': 'i', 'उ': 'u', 'ऊ': 'u', 'ऋ': 'r', 'ॠ': 'r',
            'ए': 'e', 'ऐ': 'ai', 'ओ': 'o', 'औ': 'au',
            'क': 'k', 'ख': 'k', 'ग': 'g', 'घ': 'g', 'ङ': 'n',
            'च': 'c', 'छ': 'c', 'ज': 'j', 'झ': 'j', 'ञ': 'n',
            'ट': 't', 'ठ': 't', 'ड': 'd', 'ढ': 'd', 'ण': 'n',
            'त': 't', 'थ': 't', 'द': 'd', 'ध': 'd', 'न': 'n',
            'प': 'p', 'फ': 'p', 'ब': 'b', 'भ': 'b', 'म': 'm',
            'य': 'y', 'र': 'r', 'ल': 'l', 'व': 'v', 'श': 's', 'ष': 's', 'स': 's', 'ह': 'h',
            # Vowel marks (all collapse to base)
            'ा': 'a', 'ि': 'i', 'ी': 'i', 'ु': 'u', 'ू': 'u', 'ृ': 'r', 'े': 'e', 'ै': 'ai', 'ो': 'o', 'ौ': 'au',
            'ं': 'n', 'ः': 'h', 'ँ': 'n',
        }
        result = []
        for char in text:
            if char in mapping:
                result.append(mapping[char])
            elif 'a' <= char.lower() <= 'z':
                result.append(char.lower())
        
        # Combine and collapse results (kh -> k, gh -> g etc)
        res_str = ''.join(result)
        # We don't need redundant replacements here as the mapping already collapsed kh/k to k
        return res_str

    def _generate_search_index(self):
        """Generate search-index.json with clean text for matching and HTML for display"""
        index = []
        for parva in self.parvas:
            for kandah in parva.kandahs:
                for sama in kandah.samas:
                    sama_ref = f"{parva.parva_number}.{kandah.kandah_number}.{sama.sama_number}"
                    link = f"kandah/{parva.id}/{kandah.kandah_number}.html#sama-{sama.sama_number}"
                    
                    rik_clean = self._clean_text_for_search(sama.rik_text)
                    mantra_clean = self._clean_text_for_search(sama.mantra_text)
                    title_clean = self._clean_text_for_search(sama.title)
                    metadata_clean = self._clean_text_for_search(sama.saman_metadata)
                    
                    # Permissive search fields
                    rik_permissive = self._strip_diacritics(rik_clean)
                    mantra_permissive = self._strip_diacritics(mantra_clean)
                    rik_latin = self._transliterate_to_latin(rik_clean)
                    mantra_latin = self._transliterate_to_latin(mantra_clean)
                    
                    classifications = []
                    for c in sama.rik_classifications:
                        rishi_clean = self._clean_text_for_search(c.get("Rishi", ""))
                        devata_clean = self._clean_text_for_search(c.get("Devata", ""))
                        chandas_clean = self._clean_text_for_search(c.get("Chandas", ""))
                        classifications.append({
                            "rishi": c.get("Rishi", ""),
                            "rishi_clean": rishi_clean,
                            "rishi_permissive": self._strip_diacritics(rishi_clean),
                            "rishi_latin": self._transliterate_to_latin(rishi_clean),
                            "devata": c.get("Devata", ""),
                            "devata_clean": devata_clean,
                            "devata_permissive": self._strip_diacritics(devata_clean),
                            "devata_latin": self._transliterate_to_latin(devata_clean),
                            "chandas": c.get("Chandas", ""),
                            "chandas_clean": chandas_clean,
                            "chandas_permissive": self._strip_diacritics(chandas_clean),
                            "chandas_latin": self._transliterate_to_latin(chandas_clean),
                            "global_num": c.get("Global_Rik_Num", "")
                        })
                    
                    entry = {
                        "ref": sama_ref,
                        "link": link,
                        "parva_num": parva.parva_number,
                        "parva_title": parva.title,
                        "kandah_num": kandah.kandah_number,
                        "sama_num": sama.sama_number,
                        "rik_html": sama.rik_text or "",
                        "mantra_html": sama.mantra_text or "",
                        "title_html": sama.title or "",
                        "metadata_html": sama.saman_metadata or "",
                        "rik_clean": rik_clean,
                        "mantra_clean": mantra_clean,
                        "title_clean": title_clean,
                        "metadata_clean": metadata_clean,
                        "rik_permissive": rik_permissive,
                        "mantra_permissive": mantra_permissive,
                        "rik_latin": rik_latin,
                        "mantra_latin": mantra_latin,
                        "title_latin": self._transliterate_to_latin(title_clean),
                        "metadata_latin": self._transliterate_to_latin(metadata_clean),
                        "classifications": classifications
                    }
                    index.append(entry)
        
        index_path = self.output_dir / 'search-index.js'
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write('const SEARCH_INDEX = ')
            json.dump(index, f, ensure_ascii=False)
            f.write(';')
        print(f"  Search index: {len(index)} entries → {index_path}")

    def _get_html_head(self, title: str, depth: int = 0) -> str:
        """Generate HTML head section"""
        prefix = '../' * depth
        full_title = f"{title} | {self.config['title_sa']}" if title != self.config['title_sa'] else title
        
        if getattr(self, 'is_malayalam', False):
            google_fonts = '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Noto+Sans+Malayalam:wght@400;500;600;700&family=Noto+Serif+Malayalam:wght@400;500;600;700&display=swap" rel="stylesheet">'
        else:
            google_fonts = '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Noto+Sans+Devanagari:wght@400;500;600&family=Noto+Serif+Devanagari:wght@400;500;600&display=swap" rel="stylesheet">'
        
        return f'''<!DOCTYPE html>
<html lang="sa">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{self.config['meta_desc']}">
    <meta name="keywords" content="{self.config['keywords']}">
    <meta name="version" content="{self.metadata['version']}">
    <title>{full_title}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    {google_fonts}
    <link rel="stylesheet" href="{prefix}css/styles.css?v={int(datetime.now().timestamp())}">
</head>'''

    def _get_top_nav_html(self, depth=0):
        """Get HTML for top-right navigation links"""
        prefix = '../' * depth
        L = self.labels
        return f'''
            <nav class="top-nav">
                <a href="https://jaimineeyasamavedam.org/"><i class="nav-icon">🏠</i>{L['home']}</a>
                <a href="#"><i class="nav-icon">🔍</i>{L['search']}</a>
            </nav>'''

    def _get_sidebar_html(self, current_parva_id: str = "", current_kandah_id: str = "", depth: int = 0) -> str:
        """Generate left sidebar with navigation"""
        prefix = '../' * depth
        L = self.labels
        
        # Parva links (like Mandala in Rig Veda)
        parva_links = ""
        for parva in self.parvas:
            active = 'active' if parva.id == current_parva_id else ''
            parva_links += f'<a href="{prefix}kandah/{parva.id}/1.html" class="parva-link {active}">{parva.parva_number}</a>\n'
        
        # Kandah links for current parva (if applicable)
        kandah_section = ""
        sama_section = ""
        
        if current_parva_id:
            current_parva = next((p for p in self.parvas if p.id == current_parva_id), None)
            if current_parva:
                # Kandah Section
                kandah_links = ""
                for kandah in current_parva.kandahs:
                    active = 'active' if kandah.id == current_kandah_id else ''
                    kandah_links += f'<a href="{prefix}kandah/{current_parva_id}/{kandah.kandah_number}.html" class="kandah-link {active}">{kandah.kandah_number}</a>\n'
                
                kandah_section = f'''
                <div class="nav-section">
                            <h3>{L['kandah']} <span class="number">({len(current_parva.kandahs)})</span></h3>
                    <div class="nav-links">
                        {kandah_links}
                    </div>
                </div>'''
                
                # Sama Section (only if a Kandah is selected)
                if current_kandah_id:
                    current_kandah = next((k for k in current_parva.kandahs if k.id == current_kandah_id), None)
                    if current_kandah:
                        import re
                        sama_links = ""
                        total_real_samams = 0
                        current_samam_start = 1
                        
                        for sama in current_kandah.samas:
                            cnt = 0
                            if sama.mantra_text:
                                matches = re.findall(r'(?:\|\||॥)\s*[\d०-९]+\s*(?:\|\||॥)', sama.mantra_text)
                                cnt = len(matches)
                            
                            if cnt == 0: cnt = 1
                            range_end = current_samam_start + cnt - 1
                            label_text = f"{current_samam_start}–{range_end}" if cnt > 1 else f"{current_samam_start}"
                            sama_links += f'<a href="#sama-{current_samam_start}" class="sama-link">{label_text}</a>\n'
                            total_real_samams += cnt
                            current_samam_start = range_end + 1
                        
                        sama_section = f'''
                        <div class="nav-section">
                            <h3>{L['sama']} <span class="number">({total_real_samams})</span></h3>
                            <div class="nav-links">
                                {sama_links}
                            </div>
                        </div>'''
        
        return f'''<aside class="sidebar-left">
    <div class="logo">
        <a href="{prefix}index.html">
            <div class="logo-text">{self.config['title_sa']}</div>
            <div class="logo-subtitle">{self.config['title_en']}</div>
            <div class="logo-version" style="font-size: 0.85em; color: var(--text-secondary); margin-top: 4px;">v{self.metadata['version']}</div>
        </a>
    </div>
    
    <div class="nav-section">
        <h3>{L['parva']}</h3>
        <div class="nav-links">
            {parva_links}
        </div>
    </div>
    {kandah_section}
    {sama_section}
    
    <div class="nav-section">
        <h3>Jump to</h3>
        <input type="text" class="jump-input" id="sidebar-jump" placeholder="{L['jump_placeholder']}">
    </div>

    <div class="nav-section">
        <a href="#" class="search-btn">
            {L['search']}
        </a>
    </div>

    <div class="sidebar-footer">
        <a href="{prefix}index.html" class="footer-btn">{self.mode.capitalize()} Home</a>
        {f'<a href="{prefix}classification/anukramanika.html" class="footer-btn">{L["anukramanika"]}</a>' if self.mode == "collection" else ""}
        {f"""<a href="{prefix}classification/rishi.html" class="footer-btn">{L['rishi']}</a>
        <a href="{prefix}classification/devata.html" class="footer-btn">{L['devata']}</a>
        <a href="{prefix}classification/chandas.html" class="footer-btn">{L['chandas']}</a>""" if self.mode != 'collection' else ""}
    </div>
</aside>'''

    def _get_jump_sidebar_html(self, samas: List[Sama]) -> str:
        """Generate right sidebar with jump links"""
        L = self.labels
        jump_links = ""
        for sama in samas:
            jump_links += f'<a href="#sama-entry-{sama.sama_number}" class="sama-link">{sama.sama_number}</a>\n'
        
        return f'''<aside class="sidebar-right">
    <h3>{L['sama']} <span class="number">({len(samas)})</span></h3>
    <div class="jump-links">
        {jump_links}
    </div>
</aside>'''


    def _generate_homepage(self):
        """Generate the homepage"""
        L = self.labels
        total_kandahs = sum(len(p.kandahs) for p in self.parvas)
        total_arsheyams = sum(len(k.samas) for p in self.parvas for k in p.kandahs)
        total_samas = sum(
            count_samams_with_fallback(s.mantra_text)
            for p in self.parvas for k in p.kandahs for s in k.samas
        )
        
        parva_sections = ""
        for parva in self.parvas:
            parva_clean = parva.title.replace('॥', '').replace('||', '').replace('|', '').strip()
            kandah_cards = ""
            parva_sama_count = 0
            for kandah in parva.kandahs:
                kandah_sama_count = sum(
                    count_samams_with_fallback(s.mantra_text)
                    for s in kandah.samas
                )
                parva_sama_count += kandah_sama_count
                kandah_clean = kandah.title.replace('॥', '').replace('||', '').replace('|', '').strip()
                
                kandah_cards += f'''
                <a href="kandah/{parva.id}/{kandah.kandah_number}.html" class="kandah-card">
                    <div class="number">{kandah.kandah_number}</div>
                    <div class="title">{kandah_clean}</div>
                    <div class="count">{kandah_sama_count} {L['sama'].replace(':', '')}</div>
                </a>'''
            
            parva_sections += f'''
            <section class="parva-section">
                <h2>{parva.parva_number}. {parva_clean}</h2>
                <div class="kandah-grid">
                    {kandah_cards}
                </div>
            </section>'''
        
        html = f'''{self._get_html_head(self.config['title_sa'])}
<body>
    <div class="page-container">
        {self._get_sidebar_html()}
        
        <main class="main-content" style="max-width: 1200px;">
            {self._get_top_nav_html()}
            <div class="home-hero">
                <h1>{self.config['title_sa']}</h1>
                <p class="subtitle">{self.config['title_en']}</p>
                
                <div class="stats-row">
                    <div class="stat-item">
                        <div class="stat-value">{len(self.parvas)}</div>
                        <div class="stat-label">{L['parva']} (Parva)</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">{total_kandahs}</div>
                        <div class="stat-label">{L['kandah']} (Kandah)</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">{total_arsheyams}</div>
                        <div class="stat-label">{L['arsheyam']} (Arsheyam)</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">{self.total_riks_classified}</div>
                        <div class="stat-label">{L['rik']} (Rik)</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">{total_samas}</div>
                        <div class="stat-label">{L['sama']} (Sama)</div>
                    </div>
                </div>
                
                {f"""
                <div class="anya-vargeekaran-card">
                    <h2>{L['indices']}</h2>
                    <div class="index-grid-homepage">
                        <a href="classification/rishi.html" class="index-link-item">
                            <span class="title">{L['rishi']}</span>
                            <span class="stats">({len(self.rishi_index)})</span>
                        </a>
                        <a href="classification/devata.html" class="index-link-item">
                            <span class="title">{L['devata']}</span>
                            <span class="stats">({len(self.devata_index)})</span>
                        </a>
                        <a href="classification/chandas.html" class="index-link-item">
                            <span class="title">{L['chandas']}</span>
                            <span class="stats">({len(self.chandas_index)})</span>
                        </a>
                        <a href="classification/anukramanika.html" class="index-link-item">
                            <span class="title">{L['anukramanika']}</span>
                            <span class="stats">({len(self.header_index)})</span>
                        </a>
                    </div>
                </div>""" if self.mode != 'collection' else ""}
            </div>
            
            {parva_sections}
            
            <footer class="footer">
                {self.config['footer_sa']}<br>
                Generated on {self.generated_at}
            </footer>
        </main>
    </div>
    <div class="search-modal" id="search-modal">
        <div class="search-modal-content">
            <div class="search-modal-header">
                <h3>{L['search']}</h3>
                <button class="search-close" id="search-close">&times;</button>
            </div>
            <div class="search-input-container">
                <input type="text" class="search-input" id="search-input" placeholder="Search (Malayalam, Devanagari, English, IAST)...">
                <span class="search-hint">Search for Mantras, Rishis, Devatas, or Chandas</span>
            </div>
            <div class="search-results" id="search-results"></div>
        </div>
    </div>
    <div class="search-overlay" id="search-overlay"></div>
    <script src="search-index.js"></script>
    <script src="js/main.js?v={int(datetime.now().timestamp())}"></script>
</body>
</html>'''
        
        with open(self.output_dir / 'index.html', 'w', encoding='utf-8') as f:
            f.write(html)

    def _to_devanagari_num(self, n: Any) -> str:
        """Convert a number to Devanagari numerals"""
        devanagari_digits = '०१२३४५६७८९'
        return "".join(devanagari_digits[int(d)] for d in str(n) if d.isdigit())

    def _normalize_index_key(self, text: str) -> str:
        """Normalize metadata keys to merge duplicates (spaces, punctuation)"""
        if not text:
            return ""
        
        # Remove common surrounding punctuation/whitespace
        # Keep the Devanagari Visarga (ः) as it's part of the name
        text = text.strip(' \t\n\r.|॥,:;()\'"')
        
        # Collapse multiple spaces
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def _collect_indices(self):
        """Collect data for all indices and track unique Rik counts"""
        self.rishi_index = defaultdict(list)
        self.devata_index = defaultdict(list)
        self.chandas_index = defaultdict(list)
        self.header_index = [] 
        
        self.total_riks_classified = 0
        all_rik_nums = set()
        
        for parva in self.parvas:
            for kandah in parva.kandahs:
                for sama in kandah.samas:
                    # Link relative to classification/ folder
                    link_rel = f"../kandah/{parva.id}/{kandah.kandah_number}.html#sama-{sama.sama_number}"
                    location = f"{parva.parva_number}.{kandah.kandah_number}.{sama.sama_number}"
                    
                    # Sama Header Index
                    if sama.title:
                        clean_title = sama.title.strip(' .|॥')
                        if clean_title:
                            self.header_index.append({
                                'text': clean_title,
                                'link': link_rel,
                                'location': location
                            })
                    
                    # Metadata Indices
                    if sama.rik_classifications:
                        for c in sama.rik_classifications:
                            rik_num = c.get('Global_Rik_Num')
                            if rik_num: all_rik_nums.add(rik_num)
                            
                            ref = {'link': link_rel, 'location': location, 'rik_num': rik_num}
                            
                            if c.get('Rishi'):
                                key = self._normalize_index_key(c['Rishi'])
                                if key: self.rishi_index[key].append(ref)
                            if c.get('Devata'):
                                key = self._normalize_index_key(c['Devata'])
                                if key: self.devata_index[key].append(ref)
                            if c.get('Chandas'):
                                key = self._normalize_index_key(c['Chandas'])
                                if key: self.chandas_index[key].append(ref)
        
        self.total_riks_classified = len(all_rik_nums)

    def _generate_indices(self):
        """Generate all index pages"""
        # (Already collected by generate())
        
        # Create classification dir
        (self.output_dir / 'classification').mkdir(exist_ok=True)
        
        self._generate_anukramanika_page()
        self._generate_index_page_generic("ऋषयः (Rishis)", self.rishi_index, "rishi.html", item_label="Rishis", show_top_20=True)
        self._generate_index_page_generic("देवताः (Devatas)", self.devata_index, "devata.html", item_label="Devatas", show_top_20=True)
        self._generate_index_page_generic("छन्दांसि (Chandas)", self.chandas_index, "chandas.html", item_label="Chandas", show_top_20=True)

    def _generate_anukramanika_page(self):
        """Generate a dedicated page for the Alphabetical Headers Index"""
        total_samas = sum(count_samams_with_fallback(s.mantra_text) for p in self.parvas for k in p.kandahs for s in k.samas)
        total_arsheyams = sum(len(k.samas) for p in self.parvas for k in p.kandahs)

        html = f'''{self._get_html_head("सामानुक्रमणिका (Alphabetical Index)", depth=1)}
<body>
    <div class="page-container">
        {self._get_sidebar_html(depth=1)}
        <main class="main-content" style="max-width: 1200px;">
            {self._get_top_nav_html(depth=1)}
            <div class="page-header">
                <h1>सामानुक्रमणिका (Alphabetical Index)</h1>
                <div class="stats-summary" style="margin-top: 0.3rem; color: var(--text-muted); font-size: 1.1rem; font-family: '{self.font}', serif;">
                    {total_arsheyams} आर्षेयम् • {total_samas} साम • {self.total_riks_classified} ऋचः
                </div>
            </div>
            
            <section class="alphabetical-section">
                {self._get_header_index_html()}
            </section>
        </main>
    </div>
    <div class="search-modal" id="search-modal">
        <div class="search-modal-content">
            <div class="search-modal-header">
                <h3>अन्वेषणम् (Search)</h3>
                <button class="search-close" id="search-close">&times;</button>
            </div>
            <div class="search-input-container">
                <input type="text" class="search-input" id="search-input" placeholder="Search (Devanagari, English, IAST)...">
                <span class="search-hint">Search for Mantras, Rishis, Devatas, or Chandas in Devanagari or English</span>
            </div>
            <div class="search-results" id="search-results"></div>
        </div>
    </div>
    <div class="search-overlay" id="search-overlay"></div>
    <script src="../search-index.js"></script>
    <script src="../js/main.js?v={int(datetime.now().timestamp())}"></script>
</body>
</html>'''
        with open(self.output_dir / 'classification' / 'anukramanika.html', 'w', encoding='utf-8') as f:
            f.write(html)

    def _generate_index_page_generic(self, title, data_dict, filename, item_label="Items", show_top_20=False):
        """Generate an enhanced index page with 3-column row grid layout"""
        total_items = len(data_dict)
        # Use a set to count unique arsheyam containers covered by this classification
        unique_arsheyams = {r['location'] for refs in data_dict.values() for r in refs}
        total_arsheyams = len(unique_arsheyams)
        
        # Determine Sanskrit label for items
        item_trans = item_label
        if "rishi" in title.lower(): item_trans = "ऋषयः"
        elif "devata" in title.lower(): item_trans = "देवताः"
        elif "chanda" in title.lower(): item_trans = "छन्दांसि"
        
        # We also want to show the global Arsheyam count if needed, 
        # but the request says show 722 if it's the global count.
        global_arsheyams = sum(len(k.samas) for p in self.parvas for k in p.kandahs)

        # 2. Prepare Top 20 (Prominent Items)
        top_20_html = ""
        if show_top_20:
            # Sort by count descending
            sorted_by_count = sorted(data_dict.items(), key=lambda x: len(x[1]), reverse=True)[:20]
            
            cards_html = ""
            for i, (name, refs) in enumerate(sorted_by_count, 1):
                safe_id = f"term-{name.replace(' ', '_')}" 
                cards_html += f'''
                <a href="#{safe_id}" class="rishi-card">
                    <div class="rishi-rank">{i}</div>
                    <div class="rishi-info">
                        <span class="rishi-name">{name}</span>
                    </div>
                    <div class="rishi-count">{len(refs)} ऋचः</div>
                </a>'''
            
            top_20_html = ""
            if len(data_dict) > 20:
                cards_html += f'''
                <a href="#char-rest" class="rishi-card rest-card">
                    <div class="rishi-rank">...</div>
                    <div class="rishi-info">
                        <span class="rishi-name">शिष्टाः / वर्णानुक्रमण</span>
                        <div class="rishi-count">Alphabetical Rest ↓</div>
                    </div>
                </a>'''
            
            top_20_html = f'''
            <section class="index-summary-section">
                <h2 class="index-section-header">प्रमुखाः {title.split(' ')[0]} (Top 20)</h2>
                <div class="top-20-grid">
                    {cards_html}
                </div>
            </section>'''

        # 3. Prepare Alphabetical Rest
        alpha_groups = defaultdict(list)
        for key in sorted(data_dict.keys()):
            char = key[0] if key else '?'
            alpha_groups[char].append(key)
            
        alpha_nav_html = ""
        for char in sorted(alpha_groups.keys()):
            count = len(alpha_groups[char])
            alpha_nav_html += f'''
            <a href="#char-{char}" class="alpha-btn">
                <span class="alpha-char">{char}</span>
                <span class="alpha-count">{count}</span>
            </a>'''
            
        # 4. List Items in Grid
        list_html = ""
        for char in sorted(alpha_groups.keys()):
            grid_items_html = ""
            for key in alpha_groups[char]:
                refs = data_dict[key]
                
                # Deduplicate locations
                unique_refs = []
                seen_locs = set()
                for r in refs:
                    if r['location'] not in seen_locs:
                        unique_refs.append(r)
                        seen_locs.add(r['location'])
                
                refs_links = " ".join([f'<a href="{r["link"]}">{r["location"]}</a>' for r in unique_refs])
                term_id = f"term-{key.replace(' ', '_')}"
                
                grid_items_html += f'''
                <div class="index-list-item" id="{term_id}">
                    <div style="display: flex; flex-wrap: wrap; align-items: baseline; gap: 0.75rem; margin-bottom: 0.2rem;">
                        <span class="item-name" style="color: var(--primary-maroon); min-width: fit-content;">{key}</span>
                        <span class="item-count">({len(refs)})</span>
                    </div>
                    <div class="item-refs">
                        {refs_links}
                    </div>
                </div>'''
            
            list_html += f'''
            <div class="index-char-group" id="char-{char}">
                <div class="index-char-title">{char}</div>
                <div class="index-items-grid">
                    {grid_items_html}
                </div>
            </div>'''

        html = f'''{self._get_html_head(title, depth=1)}
<body>
    <div class="page-container">
        {self._get_sidebar_html(depth=1)}
        <main class="main-content" style="max-width: 1200px;">
            {self._get_top_nav_html(depth=1)}
            <div class="page-header">
                <h1>{title}</h1>
                <div class="stats-summary" style="margin-top: 0.3rem; color: var(--text-muted); font-size: 1.1rem; font-family: '{self.font}', serif;">
                    {total_items} {item_trans} • {total_arsheyams} आर्षेयम्
                </div>
            </div>
            
            {top_20_html}
            
            <section class="alphabetical-section" id="char-rest">
                <h2 class="index-section-header">वर्णानुक्रमण (Varnanukraman)</h2>
                <div class="alphabet-nav">
                    {alpha_nav_html}
                </div>
                
                <div class="index-list-container">
                    {list_html}
                </div>
            </section>
        </main>
    </div>
    <div class="search-modal" id="search-modal">
        <div class="search-modal-content">
            <div class="search-modal-header">
                <h3>अन्वेषणम् (Search)</h3>
                <button class="search-close" id="search-close">&times;</button>
            </div>
            <div class="search-input-container">
                <input type="text" class="search-input" id="search-input" placeholder="Search (Devanagari, English, IAST)...">
                <span class="search-hint">Search for Mantras, Rishis, Devatas, or Chandas in Devanagari or English</span>
            </div>
            <div class="search-results" id="search-results"></div>
        </div>
    </div>
    <div class="search-overlay" id="search-overlay"></div>
    <script src="../search-index.js"></script>
    <script src="../js/main.js?v={int(datetime.now().timestamp())}"></script>
</body>
</html>'''
        with open(self.output_dir / 'classification' / filename, 'w', encoding='utf-8') as f:
            f.write(html)

    def _get_header_index_html(self):
        """Generate common HTML for Headers Index (nav + list)"""
        # Group by starting letter
        alpha_groups = defaultdict(list)
        for item in sorted(self.header_index, key=lambda x: x['text']):
            char = item['text'][0] if item['text'] else '?'
            alpha_groups[char].append(item)
            
        # 1. Alphabet Nav
        alpha_nav_html = ""
        for char in sorted(alpha_groups.keys()):
            count = len(alpha_groups[char])
            alpha_nav_html += f'''
            <a href="#char-{char}" class="alpha-btn">
                <span class="alpha-char">{char}</span>
                <span class="alpha-count">{count}</span>
            </a>'''
            
        alpha_nav_section = f'''
        <div class="alphabet-nav">
            {alpha_nav_html}
        </div>'''
        
        # 2. List Grid
        list_html = ""
        for char in sorted(alpha_groups.keys()):
            grid_items_html = ""
            for item in alpha_groups[char]:
                grid_items_html += f'''
                <a href="{item["link"]}" class="index-item-card simple-card">
                    <div class="item-main">
                        <div class="item-name">{item["text"]}</div>
                        <div class="item-count-badge">{item["location"]}</div>
                    </div>
                </a>'''
            
            list_html += f'''
            <div class="index-char-group" id="char-{char}">
                <div class="index-char-title">{char}</div>
                <div class="index-items-grid header-index-grid">
                    {grid_items_html}
                </div>
            </div>'''
            
        return f'''
        {alpha_nav_section}
        <div class="index-list-container">
            {list_html}
        </div>'''

            
    def _generate_kandah_pages(self):
        """Generate individual Kandah pages with Samas (like Sukta pages in Rig Veda)"""
        for p_idx, parva in enumerate(self.parvas):
            # Create parva directory
            parva_dir = self.output_dir / 'kandah' / parva.id
            parva_dir.mkdir(parents=True, exist_ok=True)
            
            for k_idx, kandah in enumerate(parva.kandahs):
                # Build Table of Contents
                toc_items = ""
                for sama in kandah.samas:
                    toc_items += f'<li><a href="#sama-{sama.sama_number}">{parva.parva_number}.{kandah.kandah_number}.{sama.sama_number}</a></li>\n'
                
                # Accumulator State for Kandah (Global Footnotes)
                kandah_counter = {'val': 0}
                kandah_seen_footnotes = {}  # content -> (id, display_num)
                kandah_all_footnotes = []   # list of (id, display_num, text)
                
                # Tracking Rik occurrences for unique anchors
                rik_occurrence_map = defaultdict(int)

                # Build Sama entries
                sama_entries = ""
                for sama in kandah.samas:
                    # Update: reliance on parser-assigned sama.sama_number which 
                    # now matches the starting mantra sequence ID.
                    # Parse footnote dict for this sama
                    current_footnotes_dict = {}
                    if sama.footnotes:
                        for fn in sama.footnotes:
                            # Parse "sN - text" or "sN : text"
                            # Removed local 'import re' to avoid UnboundLocalError
                            parts = re.match(r'(s\d+)\s*[-–—:]\s*(.*)', fn)
                            if parts:
                                current_footnotes_dict[parts.group(1)] = parts.group(2)
                            else:
                                # Fallback if format is just "s1 text" or other
                                # Try to grab sN at start
                                parts = re.match(r'(s\d+)\s+(.*)', fn)
                                if parts:
                                    current_footnotes_dict[parts.group(1)] = parts.group(2)
                    
                    
                    # Rik metadata (displayed above Rik text - in purple like renderPDF.py)
                    rik_metadata_html = ""
                    if sama.rik_metadata:
                        # Clean existing dandas/dots to prevent double symbols
                        # Added single danda '।' (U+0964) to the strip set
                        clean_meta = sama.rik_metadata.strip(' .|॥।\n\r\t')
                        if clean_meta:
                            # Normalize all internal danda variations (| || । ॥) to single '॥'
                            # Also handles spacing around them
                            # Removed local 'import re'
                            clean_meta = re.sub(r'\s*[|॥।]+\s*', ' ॥ ', clean_meta)
                            rik_metadata_html = f'<div class="rik-metadata">॥ {clean_meta} ॥</div>'
                    
                    # Rik text
                    rik_html = ""
                    if sama.rik_text:
                        formatted_rik, _ = format_rik_text_html(sama.rik_text, current_footnotes_dict, kandah_counter, kandah_seen_footnotes, kandah_all_footnotes)
                        rik_html = f'''
                        <div class="rik-box">
                            {rik_metadata_html}
                            <div class="rik-text sanskrit-text">{formatted_rik}</div>
                        </div>'''
                    
                    # Sama title and metadata (displayed above Sama/Mantra text - in green)
                    sama_header_items = []
                    
                    if sama.title:
                        # Clean existing dandas/dots - Added single danda '।'
                        clean_title = sama.title.strip(' .|॥।\n\r\t')
                        if clean_title:
                            # Normalize all internal danda variations
                            clean_title = re.sub(r'\s*[|॥।]+\s*', ' ॥ ', clean_title)
                            sama_header_items.append(f'<div class="sama-header-text">॥ {clean_title} ॥</div>')
                    
                    # Samam Metadata (render if present, also in green)
                    if sama.saman_metadata:
                        clean_smeta = sama.saman_metadata.strip(' .|॥।\n\r\t')
                        if clean_smeta:
                            clean_smeta = re.sub(r'\s*[|॥।]+\s*', ' ॥ ', clean_smeta)
                            sama_header_items.append(f'<div class="sama-metadata-text">॥ {clean_smeta} ॥</div>')
                    
                    sama_header_html = ""
                    # Procedure links are shown at section/supersection header level only
                    # No sama-level procedure links (subsection scope shown at header)
                    
                    sama_header_html = f'<div class="sama-header-container">{"".join(sama_header_items)}</div>'

                    
                    # Mantra text with Sama header above it
                    mantra_html = ""
                    if sama.mantra_text:
                        formatted_mantra, _ = format_mantra_text_html(sama.mantra_text, current_footnotes_dict, kandah_counter, kandah_seen_footnotes, kandah_all_footnotes)
                        mantra_html = f'''
                        <div class="mantra-box">
                            {sama_header_html}
                            <div class="mantra-container sanskrit-large">{formatted_mantra}</div>
                        </div>'''
                    
                    # Audio section
                    audio_html = ""
                    
                    # Define source directory for audio (relative to project root)
                    audio_src_root = Path('data/audio_source')
                    
                    # Output directory for this kandah's audio
                    kandah_audio_out_dir = parva_dir / 'audio'
                    kandah_audio_out_dir.mkdir(parents=True, exist_ok=True)
                    
                    # Search paths - User requested: ParvaNumber folder only
                    # Then filename 1-1.mp3 (Kandah-Sama.mp3)
                    search_paths = [
                        audio_src_root / str(parva.parva_number),
                        audio_src_root / parva.id # Fallback
                    ]
                    
                    # 1. SAMA AUDIO
                    sama_audio_filename = None
                    sama_audio_found = False
                    
                    for search_path in search_paths:
                        # User requested format: Kandah-Subsection.mp3 (e.g. 1-1.mp3)
                        candidates = [
                            f"{kandah.kandah_number}-{sama.sama_number}.mp3", 
                            f"sama_{kandah.kandah_number}-{sama.sama_number}.mp3"
                        ]
                        for cand in candidates:
                            src_file = search_path / cand
                            if src_file.exists():
                                sama_audio_found = True
                                dest_filename = f"{kandah.kandah_number}-{sama.sama_number}.mp3"
                                dist_path = kandah_audio_out_dir / dest_filename
                                import shutil
                                shutil.copy2(src_file, dist_path)
                                sama_audio_filename = f"audio/{dest_filename}"
                                break
                        if sama_audio_found: break
                    
                    # 2. RIK AUDIO
                    rik_audio_filename = None
                    rik_audio_found = False
                    
                    for search_path in search_paths:
                         # Try 'rik_K-S.mp3'
                        candidates = [
                            f"rik_{kandah.kandah_number}-{sama.sama_number}.mp3", 
                            f"Rik_{kandah.kandah_number}-{sama.sama_number}.mp3"
                        ]
                        for cand in candidates:
                             src_file = search_path / cand
                             if src_file.exists():
                                 rik_audio_found = True
                                 dest_filename = f"rik_{kandah.kandah_number}-{sama.sama_number}.mp3"
                                 dist_path = kandah_audio_out_dir / dest_filename
                                 import shutil
                                 shutil.copy2(src_file, dist_path)
                                 rik_audio_filename = f"audio/{dest_filename}"
                                 break
                        if rik_audio_found: break

                    # Generate HTML
                    if sama_audio_found or rik_audio_found:
                         audio_players = []
                         
                         if rik_audio_found:
                             audio_players.append(f'''
                                <div class="audio-player-container">
                                    <div class="audio-label">Rik Audio</div>
                                    <audio controls class="audio-player">
                                        <source src="{rik_audio_filename}" type="audio/mpeg">
                                        Your browser does not support the audio element.
                                    </audio>
                                </div>''')
                         
                         if sama_audio_found:
                             audio_players.append(f'''
                                <div class="audio-player-container">
                                    <audio controls class="audio-player">
                                        <source src="{sama_audio_filename}" type="audio/mpeg">
                                        Your browser does not support the audio element.
                                    </audio>
                                </div>''')
                                
                         audio_html = f'<div class="audio-section">{"".join(audio_players)}</div>'
                    else:
                        audio_html = '''
                        <div class="audio-section">
                            <div class="audio-pending">
                                <span>🎵</span>
                                <span>Audio missing</span>
                            </div>
                        </div>'''
                    
                    # NO per-Sama footnotes section here - accumulated at Kandah level
                    
                    # Generate Rik Anchors for Jump Navigation
                    rik_anchor_tags = ""
                    for rid in sama.rik_ids:
                        rik_occurrence_map[rid] += 1
                        occ = rik_occurrence_map[rid]
                        anchor_id = f"rik-{rid}" if occ == 1 else f"rik-{rid}_{occ}"
                        rik_anchor_tags += f'<span id="{anchor_id}" class="rik-anchor"></span>'

                    # Use parser-assigned sama_number as the anchor start
                    start_samam_for_entry = sama.sama_number
                    verse_count = count_samams_with_fallback(sama.mantra_text)
                    if verse_count == 0: verse_count = 1
                    
                    # Generate unique anchors for EVERY verse number in the current range
                    verse_anchors = ""
                    for s_num in range(start_samam_for_entry, start_samam_for_entry + verse_count):
                        verse_anchors += f'<span id="sama-{s_num}" class="sama-anchor"></span>'
                    
                    sama_entries += f'''
                    {verse_anchors}
                    <article class="sama-entry" id="sama-entry-{sama.sama_number}" data-sama-start="{start_samam_for_entry}">
                        {rik_anchor_tags}
                        <div class="sama-id-row">
                            <span class="sama-id">
                                <a href="#sama-entry-{sama.sama_number}">{parva.parva_number}.{kandah.kandah_number}.{sama.sama_number}</a>
                            </span>
                        </div>
                        
                        <!-- Classification / Vargeekaran Section -->
                        {f"""<div class="classification-container">
                            <table class="classification-table">
                                <thead>
                                    <tr>
                                        <th>Global #</th>
                                        <th>ऋषिः (Rishi)</th>
                                        <th>देवता (Devata)</th>
                                        <th>छन्दः (Chandas)</th>
                                    </tr>
                                </thead>
                                {"".join([f'''
                                    <tr>
                                        <td><span class="number">{c['Global_Rik_Num']}</span></td>
                                        <td class="class-value">{c['Rishi']}</td>
                                        <td class="class-value">{c['Devata']}</td>
                                        <td class="class-value">{c['Chandas']}</td>
                                    </tr>''' for c in sama.rik_classifications])}
                            </table>
                        </div>""" if self.mode != 'collection' and sama.rik_classifications else ""}

                        {rik_html}
                        {mantra_html}
                        {audio_html}
                    </article>'''
                
                # Render accumulated footnotes for the Kandah
                kandah_footnotes_html = ""
                if kandah_all_footnotes:
                    fn_items = ""
                    for unique_id, display_num, text in kandah_all_footnotes:
                        fn_items += f'<div class="footnote-item" id="{unique_id}"><span class="footnote-ref">{display_num}</span><span class="footnote-text">{text}</span></div>'
                    
                    kandah_footnotes_html = f'''
                    <div class="footnotes">
                        <hr class="footnote-separator">
                        <div class="footnote-section">
                            {fn_items}
                        </div>
                    </div>'''

                # Render Closing Mantras (Only on the last page of the entire collection)
                closing_mantras_html = ""
                if p_idx == len(self.parvas) - 1 and k_idx == len(parva.kandahs) - 1 and self.closing_mantras:
                    cm_lines = "".join([f'<p class="closing-mantra-line">{line}</p>' for line in self.closing_mantras])
                    closing_mantras_html = f'''
                    <section class="closing-mantras-section">
                        <div class="closing-mantras-content">
                            {cm_lines}
                        </div>
                    </section>'''
                
                parva_clean = parva.title.replace('॥', '').replace('||', '').replace('|', '').strip()
                kandah_clean = kandah.title.replace('॥', '').replace('||', '').replace('|', '').strip()
                
                # Calculate real sama count for this Kandah
                kandah_sama_count = sum(count_samams_with_fallback(s.mantra_text) for s in kandah.samas)
                
                # Check for procedure_ref at Kandah (section) or Parva (supersection) level
                procedure_link = ""
                for sama in kandah.samas:
                    if sama.procedure_ref:
                        scope = sama.procedure_ref.get('scope', '')
                        if scope == 'section':
                            # This procedure applies to the entire Kandah
                            slug = Path(sama.procedure_ref.get('file', '')).stem
                            proc_anchor = f"../../prayoga/{slug}.html"
                            proc_title = sama.procedure_ref.get('title', 'विधिः')
                            procedure_link = f'<div class="procedure-box"><span class="procedure-label">विधिः</span><a href="{proc_anchor}" class="procedure-text">{proc_title}</a></div>'
                            break
                        elif scope == 'supersection':
                            # Show supersection procedure on each Kandah page
                            slug = Path(sama.procedure_ref.get('file', '')).stem
                            proc_anchor = f"../../prayoga/{slug}.html"
                            proc_title = sama.procedure_ref.get('title', 'विधिः')
                            procedure_link = f'<div class="procedure-box"><span class="procedure-label">विधिः</span><a href="{proc_anchor}" class="procedure-text">{proc_title}</a></div>'
                            break
                
                L = self.labels
                home_title = L['home'].split(' ')[0]
                all_kandah_text = L.get('all_kandah', 'सम्पूर्णम्') if getattr(self, 'is_malayalam', False) else 'सम्पूर्णम्'
                if getattr(self, 'is_malayalam', False):
                    all_kandah_text = 'സമ്പൂർണ്ണം'
                
                html = f'''{self._get_html_head(f"{parva_clean} - {kandah_clean}", depth=2)}
<body>
    <div class="page-container">
        {self._get_sidebar_html(current_parva_id=parva.id, current_kandah_id=kandah.id, depth=2)}
        
        <main class="main-content">
            {self._get_top_nav_html(depth=2)}
            <nav class="breadcrumb">
                <a href="../../index.html">{home_title}</a>
                <span class="breadcrumb-separator">›</span>
                <span>{parva_clean}</span>
                <span class="breadcrumb-separator">›</span>
                <span>{kandah_clean}</span>
            </nav>
            
            <header class="page-header">
                <h1>{parva_clean} - {kandah_clean}</h1>
                <div class="page-meta">
                    <p class="page-subtitle">{L['parva']} <span class="number">{parva.parva_number}</span> | {L['kandah']} <span class="number">{kandah.kandah_number}</span> | {L['sama']} <span class="number">{kandah_sama_count}</span></p>
                </div>
                {procedure_link}
            </header>
            
            <div class="toc">
                <h4>{L['kandah']} {kandah.kandah_number} - {all_kandah_text}</h4>
                <ul class="toc-list">
                    {toc_items}
                </ul>
            </div>
            
            {sama_entries}
            
            {kandah_footnotes_html}
            
            {closing_mantras_html}
            
            <footer class="footer">
                {self.config['footer_sa']}
            </footer>
        </main>
        
    </div>
    <div class="search-modal" id="search-modal">
        <div class="search-modal-content">
            <div class="search-modal-header">
                <h3>अन्वेषणम् (Search)</h3>
                <button class="search-close" id="search-close">&times;</button>
            </div>
            <div class="search-input-container">
                <input type="text" class="search-input" id="search-input" placeholder="Search (Devanagari, English, IAST)...">
                <span class="search-hint">Search for Mantras, Rishis, Devatas, or Chandas in Devanagari or English</span>
            </div>
            <div class="search-results" id="search-results"></div>
        </div>
    </div>
    <div class="search-overlay" id="search-overlay"></div>
    <script src="../../search-index.js"></script>
    <script src="../../js/main.js?v={int(datetime.now().timestamp())}"></script>
</body>
</html>'''
                
                with open(parva_dir / f'{kandah.kandah_number}.html', 'w', encoding='utf-8') as f:
                    f.write(html)
                    
    def _generate_procedure_pages(self):
        """Generate standalone HTML pages for procedures from Markdown files"""
        prayoga_dir = self.output_dir / 'prayoga'
        prayoga_dir.mkdir(parents=True, exist_ok=True)
        
        # Collect all unique procedure Markdown files from Samas
        procedures = {}
        for parva in self.parvas:
            for kandah in parva.kandahs:
                for sama in kandah.samas:
                    if sama.procedure_ref:
                        file_path = sama.procedure_ref.get('file', '')
                        if file_path and file_path.endswith('.md'):
                            slug = Path(file_path).stem
                            title_meta = sama.procedure_ref.get('title', 'विधिः')
                            # Also build the backlink for the very first Sama that links to this procedure
                            backlink = f"../kandah/{parva.id}/{kandah.kandah_number}.html#sama-{sama.sama_number}"
                            if file_path not in procedures:
                                procedures[file_path] = {
                                    'slug': slug, 
                                    'title': title_meta, 
                                    'backlink': backlink, 
                                    'backlink_title': f"{parva.title} - {kandah.title}"
                                }

        # Render each markdown file
        for file_path, proc_info in procedures.items():
            full_md_path = Path("data/input/prayoga") / file_path
            if not full_md_path.exists():
                print(f"[WARNING] Procedure file not found: {full_md_path}")
                continue
            
            with open(full_md_path, 'r', encoding='utf-8') as f:
                md_content = f.read()

            # Frontmatter stripping
            if md_content.startswith('---'):
                parts = md_content.split('---', 2)
                if len(parts) >= 3:
                    md_content = parts[2].strip()

            html_content = markdown.markdown(md_content, extensions=['tables'])

            # Render page layout with base styling
            title = proc_info['title']
            html = f'''{self._get_html_head(title, depth=1)}
<body>
    <div class="page-container">
        {self._get_sidebar_html(depth=1)}
        <main class="main-content" style="max-width: 1200px;">
            {self._get_top_nav_html(depth=1)}
            <div class="page-header" style="text-align: left; margin-bottom: 20px;">
                <a href="{proc_info['backlink']}" style="color: #2e7d32; text-decoration: none; font-weight: 500;">← Back to {proc_info['backlink_title']}</a>
                <h1>{title}</h1>
            </div>
            
            <div class="procedure-markdown-content" style="background: white; padding: 2.5rem; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); font-size: 1.15rem; line-height: 1.7; color: #333;">
                <style>
                    .procedure-markdown-content h1, .procedure-markdown-content h2, .procedure-markdown-content h3 {{
                        color: #5c3a21;
                        margin-top: 1.5em;
                        margin-bottom: 0.5em;
                    }}
                    .procedure-markdown-content h1 {{ font-size: 2rem; border-bottom: 2px solid #f0f0f0; padding-bottom: 0.3em; }}
                    .procedure-markdown-content h2 {{ font-size: 1.5rem; }}
                    .procedure-markdown-content p {{ margin-bottom: 1.2em; }}
                    .procedure-markdown-content ul, .procedure-markdown-content ol {{ margin-bottom: 1.2em; padding-left: 2em; }}
                    .procedure-markdown-content li {{ margin-bottom: 0.5em; }}
                    .procedure-markdown-content strong {{ color: #2e7d32; }}
                </style>
                {html_content}
            </div>
        </main>
    </div>
</body>
</html>'''
            
            out_path = prayoga_dir / f"{proc_info['slug']}.html"
            with open(out_path, 'w', encoding='utf-8') as f:
                f.write(html)


    def _generate_metadata_json(self):
        """Generate metadata.json for reference"""
        metadata = {
            "title": self.config['title_sa'],
            "title_en": self.config['title_en'],
            "version": self.metadata["version"],
            "generated_at": self.generated_at,
            "hierarchy": "Parva → Kandah → Sama",
            "stats": {
                "total_parvas": len(self.parvas),
                "total_kandahs": sum(len(p.kandahs) for p in self.parvas),
                "total_samas": sum(sum(len(k.samas) for k in p.kandahs) for p in self.parvas)
            },
            "parvas": []
        }
        
        for parva in self.parvas:
            parva_data = {
                "id": parva.id,
                "number": parva.parva_number,
                "title": parva.title,
                "kandahs": []
            }
            for kandah in parva.kandahs:
                kandah_data = {
                    "id": kandah.id,
                    "number": kandah.kandah_number,
                    "title": kandah.title,
                    "sama_count": len(kandah.samas),
                    "samas": [
                        {
                            "id": sama.id,
                            "number": sama.sama_number,
                            "title": sama.title,
                            "audio_filename": sama.audio_filename
                        }
                        for sama in kandah.samas
                    ]
                }
                parva_data["kandahs"].append(kandah_data)
            metadata["parvas"].append(parva_data)
        
        with open(self.output_dir / 'metadata.json', 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)


# --- Main Entry Point ---
def main():
    """Main function to run the website generator"""
    # 0. Load Configuration
    pipeline_cfg = load_pipeline_config()
    web_cfg = pipeline_cfg.get('generate_website', {})

    parser = argparse.ArgumentParser(
        description='Jaimineeya Samavedam Website Generator (v2.0)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python generate_website.py --samhita
  python generate_website.py -a --source-file aranam.json
        '''
    )
    
    # Get the project root directory
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    # Default paths (used if not specified by CLI or config)
    default_source = project_root / 'data' / 'output' / 'Vargeekaran.json'
    default_output = project_root / 'docs'
    default_audio = project_root / 'data' / 'input' / 'Audio_Placeholders'
    
    parser.add_argument(
        '--source-file', '-s',
        type=str,
        default=None,
        help='Path to the source text file'
    )
    
    parser.add_argument(
        '--output_dir', '-o',
        type=str,
        default=None,
        help='Output directory for generated website'
    )
    
    parser.add_argument(
        '--audio-dir', '-d',
        type=str,
        default=None,
        help='Directory for audio placeholder folders'
    )
    
    # Mode selection group
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '-m', '--samhita',
        action='store_true',
        help='Generate for Samhita'
    )
    group.add_argument(
        '-a', '--aaranam',
        action='store_true',
        help='Generate for Aaranam'
    )
    group.add_argument(
        '-c', '--collection',
        action='store_true',
        help='Generate for Collection (Jaimineeya Sama Sangraha)'
    )
    group.add_argument(
        '-ml', '--malayalam',
        action='store_true',
        help='Generate for Malayalam Samhita'
    )
    parser.add_argument(
        '--title',
        type=str,
        default=None,
        help='Custom title for collection mode (e.g., "जैमिनीय साम सङ्ग्रहः")'
    )
    
    parser.add_argument(
        '--font',
        type=str,
        default=None,
        help='Primary font for the website (default: AdishilaVedic)'
    )
    
    args = parser.parse_args()
    
    # Determine mode: Priority CLI flags > Config (default: aaranam)
    if args.malayalam:
        mode = 'malayalam'
    elif args.aaranam:
        mode = 'aaranam'
    elif args.samhita:
        mode = 'samhita'
    elif args.collection:
        mode = 'collection'
    else:
        mode = web_cfg.get('default_type', 'aaranam')

    type_cfg = web_cfg.get(mode, {})
    
    # Defaults for Malayalam mode
    if mode == 'malayalam':
        default_ml_source = project_root / 'data' / 'output' / 'malayalam' / 'Samhita_Malayalam.json'
        default_ml_output = project_root / 'docs' / 'malayalam'
        default_ml_audio = project_root / 'docs' / 'malayalam' / 'audio'
        source_file = args.source_file or type_cfg.get('source') or str(default_ml_source)
        output_dir = args.output_dir or type_cfg.get('output_dir') or str(default_ml_output)
        audio_dir = args.audio_dir or type_cfg.get('audio_dir') or str(default_ml_audio)
        font = args.font or type_cfg.get('font') or 'Noto Serif Malayalam'
        font_sans = 'Noto Sans Malayalam'
    else:
        # Priority: CLI > Config Type > Config Global > Hardcoded Default
        source_file = args.source_file or type_cfg.get('source') or web_cfg.get('source') or str(default_source)
        output_dir = args.output_dir or type_cfg.get('output_dir') or web_cfg.get('output_dir') or str(default_output)
        audio_dir = args.audio_dir or type_cfg.get('audio_dir') or web_cfg.get('audio_dir') or str(default_audio)
        font = args.font or type_cfg.get('font') or web_cfg.get('font') or 'AdishilaVedic'
        font_sans = 'AdishilaSanVedic'
    
    # Custom title for collection mode: CLI > Config > Default
    custom_title = args.title or type_cfg.get('title') or None
    
    # Validate source file exists
    source_path = Path(source_file)
    if not source_path.exists():
        print(f"[ERROR] Source file not found: {source_path}")
        return 1
    
    print("=" * 60)
    print("  Jaimineeya Samavedam Website Generator (v2.0)")
    print("  Design: Inspired by rigveda.sanatana.in")
    print("=" * 60)
    print(f"\n[INFO] Source file: {source_path}")
    print(f"[INFO] Output directory: {output_dir}")
    print(f"[INFO] Audio placeholders: {audio_dir}")
    print(f"[INFO] Mode: {mode.upper()}")
    print()
    
    # Parse the source file
    print("[INFO] Parsing source file...")
    parser_obj = JSVParser(str(source_path))
    parvas = parser_obj.parse()
    
    # Print statistics
    total_kandahs = sum(len(p.kandahs) for p in parvas)
    total_samas = sum(sum(len(k.samas) for k in p.kandahs) for p in parvas)
    
    print(f"\n[STATS] Parsed Structure:")
    print(f"   - {len(parvas)} Parvas (Patha)")
    print(f"   - {total_kandahs} Kandahs (Khanda)")
    print(f"   - {total_samas} Samas (Sama)")
    
    import sys
    import io
    if sys.stdout.encoding != 'utf-8':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    
    for parva in parvas:
        print(f"\n   {parva.parva_number}. {parva.title}")
        print(f"      └─ {len(parva.kandahs)} Kandahs, {sum(len(k.samas) for k in parva.kandahs)} Samas")
    
    # Generate website
    print("\n[INFO] Generating website (Rig Veda style)...")
    generator = WebsiteGenerator(parvas, output_dir, audio_dir, mode=mode, custom_title=custom_title, font=font, metadata=parser_obj.metadata, closing_mantras=parser_obj.closing_mantras)
    generator.generate()
    
    # Run post-processing patches automatically
    try:
        from patch_highlight_js import run_patcher
        run_patcher()
    except ImportError:
        print("\n[WARNING] Could not find patch_highlight_js.py - skipping automatic patches.")
    
    print("\n" + "=" * 60)
    print("  ✨ Website generation complete!")
    print("=" * 60)
    print(f"\nOpen {output_dir}/index.html to view the website.")
    
    return 0


if __name__ == '__main__':
    exit(main())
