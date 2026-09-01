"""Devanagari -> Malayalam transliteration for the Jaimineeya Samaveda.

Wraps aksharamukha with the edge-case fixes ported from pdfconverter
(convert_devanagari_to_malayalam.py): danda preservation, dotted-circle
orphan cleanup, Malayalam O/AU canonicalization, word-final "മ്" -> "ം",
and syllable/grapheme counting used to assert transliteration alignment.

Swara markers (Word(Swara)) are masked before transliteration so the base
word and the marker are processed independently; ml_text.py re-attaches the
resolved Grantha marker.
"""

import re
import unicodedata
from functools import lru_cache

try:
    from aksharamukha import transliterate
except ImportError:  # pragma: no cover
    transliterate = None

try:
    import grapheme
except ImportError:
    grapheme = None

from utils import combine_ardhaksharas

# --- Danda placeholders (same scheme as pdfconverter) ---
_DANDA1 = "\u00A6\u00A6\u00A6"
_DANDA2 = "\u00A6\u00A6\u00A6\u00A6"

_MALAYALAM_VIROMA = "\u0D4D"
_DEVANAGARI_VIROMA = "\u094D"

# --- Script ranges ---
_DEVANAGARI_RE = re.compile(r"[\u0900-\u097F\u1CD0-\u1CF9\uA8E0-\uA8FF]+")
_MALAYALAM_MATRA = r"\u0D3E-\u0D57\u0D66-\u0D6F"


def _transliterate_devanagari_to_malayalam(text: str) -> str:
    if transliterate is None:
        raise RuntimeError(
            "aksharamukha is not installed. Install with: pip install aksharamukha"
        )
    return transliterate.process("Devanagari", "Malayalam", text)


@lru_cache(maxsize=1)
def _transliterate_devanagari_to_grantha(text: str) -> str:
    """Fallback for markers not present in the frozen lookup (render literally)."""
    if transliterate is None:
        raise RuntimeError(
            "aksharamukha is not installed. Install with: pip install aksharamukha"
        )
    return transliterate.process("Devanagari", "Grantha", text)


def devanagari_to_grantha(text: str) -> str:
    return _transliterate_devanagari_to_grantha(text)


def normalize_combining_marks(text: str) -> str:
    """Eliminate dotted-circle artifacts (ported from pdfconverter): spurious
    virama before a matra, spaces detaching a combining mark, and
    NFD-decomposed matra pairs."""
    text = re.sub(
        r"([\u0D15-\u0D39])\u0D4D([" + _MALAYALAM_MATRA + r"\u0D02\u0D03\u0D01])",
        r"\1\2",
        text,
    )
    text = re.sub(
        r"([\u0900-\u097F\u0D00-\u0D7F])\s+([\u0D3E-\u0D57\u0D66-\u0D6F\u0D00-\u0D03])",
        r"\1\2",
        text,
    )
    text = unicodedata.normalize("NFC", text)
    # Malayalam O/AU do not NFC-recompose; collapse explicitly.
    text = text.replace("\u0D3E\u0D46", "\u0D4B")  # ാെ -> ോ
    text = text.replace("\u0D3E\u0D47", "\u0D4C")  # ാേ -> ൌ
    return text


# Translate Devanagari and Malayalam numerals (excluding ൪ which is used for Vedic repha) to English ASCII digits
_DIGITS_TO_ENGLISH = str.maketrans("०१२३४५६७८९൦൧൨൩൫൬൭൮൯", "0123456789012356789")


def post_process_malayalam(text: str) -> str:
    """Cleanup applied after aksharamukha transliteration (ported edge cases)."""
    text = normalize_combining_marks(text)
    # Vedic transliteration rule 2: Devanagari ळ (U+0933) -> Malayalam ഴ (U+0D34)
    text = text.replace("ള", "ഴ").replace("ൾ", "ഴ്")
    # Vedic transliteration rule 1: Vocalic r / Repha before consonants (e.g. र्हा -> ൪ഹാ)
    text = re.sub(r"(?:ർ|ര\u0D4D)(?=[ക-ഹ])", "൪", text)
    # Vedic transliteration rule 3: Word-final AA swara / matra -> short vowel (അ)
    # e.g. സംഹിതാ -> സംഹിത, മാലാ -> മാല, സൂക്തമാലാ -> സൂക്തമാല
    text = re.sub(r"ാ(?=[\s।॥\?!\.,;\)\"']|$)", "", text)
    text = re.sub(r"ആ(?=[\s।॥\?!\.,;\)\"']|$)", "അ", text)
    # Word-final halant ma -> anusvara (e.g. സൂക്തമ് -> സൂക്തം)
    text = re.sub(r"മ്(?=[\s।॥\?!\.,;\)]|$)", "ം", text)
    # Vedic transliteration rule 4: Word-final halant na -> chillu-n (ൻ) (e.g. ന്। -> ൻ।, ന്॥ -> ൻ॥)
    text = re.sub(r"ന്(?=[\s।॥\?!\.,;\)]|$)", "ൻ", text)
    # Collapse duplicated AA matras
    text = re.sub(r"ാ+", "ാ", text)
    # Virama before ൃ/ൄ (ക്ിൃ -> കൃ)
    text = text.replace("്ൃ", "ൃ").replace("്ൄ", "ൄ")
    # Convert all numerals to English ASCII digits
    text = text.translate(_DIGITS_TO_ENGLISH)
    return text


def devanagari_to_malayalam(text: str) -> str:
    """Transliterate a Devanagari run to Malayalam, preserving dandas.

    The caller is responsible for masking swara markers (ml_text.py).
    Non-Devanagari runs (spaces, dandas, footnote markers) are preserved.
    """
    text = text.replace("।।", "॥").replace("||", "॥")
    text = text.replace("॥", _DANDA2).replace("।", _DANDA1)
    tokens = _DEVANAGARI_RE.split(text)
    parts = _DEVANAGARI_RE.findall(text)
    out = []
    for i, token in enumerate(tokens):
        if token:
            out.append(token)
        if i < len(parts):
            out.append(post_process_malayalam(_transliterate_devanagari_to_malayalam(parts[i])))
    result = "".join(out)
    result = result.replace(_DANDA2, "॥").replace(_DANDA1, "।").replace("\u00A6", "")
    return result


def devanagari_syllable_count(text: str) -> int:
    """Number of Devanagari syllables (combine_ardhaksharas) in a word.

    A word-final 'म्' is an anusvara (source convention writes it as a
    separate token that the pipeline merges into the word), not a syllable.
    """
    parts = combine_ardhaksharas(text)
    count = len(parts)
    if parts and parts[-1] == "\u092E\u094D":
        count -= 1
    return count


def malayalam_grapheme_count(text: str) -> int:
    """Number of Malayalam grapheme clusters in a word."""
    return len(split_malayalam_graphemes(text))


def malayalam_syllable_count(text: str) -> int:
    """Number of Malayalam syllables (conjuncts merged) in a word."""
    return len(split_malayalam_syllables(text))


def split_malayalam_graphemes(text: str) -> list[str]:
    """Split a Malayalam word into grapheme clusters (raw, unmerged)."""
    if grapheme is None:
        result: list[str] = []
        buf = ""
        for ch in text:
            if unicodedata.combining(ch):
                buf += ch
            else:
                if buf:
                    result.append(buf)
                buf = ch
        if buf:
            result.append(buf)
        return result
    return list(grapheme.graphemes(text))


def split_malayalam_syllables(text: str) -> list[str]:
    """Split a Malayalam word into syllables (conjuncts merged).

    Malayalam writes conjuncts as C+virama+C, so raw grapheme clusters like
    ['ഗ്', 'നാ'] are one syllable. Chillu letters (U+0D7A-U+0D7F) carry an
    implicit virama and merge with the following cluster the same way, e.g.
    ഇർമാ = [ഇ][ർ][മാ] -> [ഇ][ർമാ]. This mirrors utils.combine_halants for
    Devanagari and is the unit a swara marker attaches to in the PDF.
    """
    clusters = split_malayalam_graphemes(text)
    merged: list[str] = []
    for cluster in clusters:
        if merged and (
            merged[-1].endswith(_MALAYALAM_VIROMA)
            or (len(merged[-1]) == 1 and "\u0D7A" <= merged[-1] <= "\u0D7F")
        ):
            merged[-1] += cluster
        else:
            merged.append(cluster)
    return merged


# Reverse Grantha/Malayalam -> Devanagari swara marker lookup
_GRANTHA_TO_DEVA_MARKER = {}

def _get_grantha_to_deva_map():
    global _GRANTHA_TO_DEVA_MARKER
    if not _GRANTHA_TO_DEVA_MARKER:
        try:
            from malayalam.ml_map import load_lookup
            lookup = load_lookup().get("lookup", {})
            for deva_key, entry in lookup.items():
                g_text = entry.get("grantha_text")
                if g_text and g_text not in _GRANTHA_TO_DEVA_MARKER:
                    _GRANTHA_TO_DEVA_MARKER[g_text] = deva_key
        except Exception:
            pass
    return _GRANTHA_TO_DEVA_MARKER


def grantha_or_mal_to_deva_marker(marker_str: str) -> str:
    """Map a Grantha or Malayalam swara marker string to its canonical Devanagari equivalent."""
    rev = _get_grantha_to_deva_map()
    if marker_str in rev:
        return rev[marker_str]
    if transliterate is not None:
        try:
            res = transliterate.process("Grantha", "Devanagari", marker_str)
            if res:
                return res
        except Exception:
            pass
        try:
            res = transliterate.process("Malayalam", "Devanagari", marker_str)
            if res:
                return res
        except Exception:
            pass
    return marker_str


_MOD_CODE_TO_UNICODE = {
    'C': '·', 'c': '·', '\uE001': '·', 'ॱ': '·',
    'H': '|', 'h': '|', '\uE00C': '|', 'L': '|', 'l': '|',
    'A': '⁀', 'a': '⁀', '\uE004': '⁀', '╭╮': '⁀',
    'A1': '⁀', 'a1': '⁀', 'A_1': '⁀', 'a_1': '⁀', '\uE00D': '⁀',
    'B': '^', 'b': '^', '\uE005': '^',
    'D': '∧', 'd': '∧', '\uE006': '∧', 'Ʌ': '∧',
    'D1': '↗', 'd1': '↗', 'D_1': '↗', 'd_1': '↗', '\uE00E': '↗', '↗': '↗',
    'D2': '✓', 'd2': '✓', 'D_2': '✓', 'd_2': '✓', '\uE00F': '✓', '✓': '✓',
    'I': '⫽', 'i': '⫽', '\uE02A': '⫽',
    'J': '¯', 'j': '¯', '\uE02B': '¯',
    'B1': '/', 'b1': '/', 'B_1': '/', 'b_1': '/', '\uE02C': '/',
    'K': '⨯', 'k': '⨯', '\uE02D': '⨯',
    'E': '┃', 'e': '┃', '\uE002': '┃', '┃': '┃',
    'F': '╷', 'f': '╷', '\uE008': '╷', '╷': '╷',
    'G': '\\', 'g': '\\', '\uE003': '\\', '\\': '\\',
}


def malayalam_to_devanagari_mantra_line(line: str) -> str:
    """Convert a Malayalam Samam mantra line (with Grantha swara markers and modifiers) to Devanagari."""
    if not line:
        return ""
    
    # 1. Normalize PUA Grantha characters if any
    pua_to_grantha = {
        '\uE010': '𑌶𑌾', '\uE011': '𑌶𑌿', '\uE012': '𑌶𑍀', '\uE013': '𑌶𑍍',
        '\uE015': '𑌶𑍁', '\uE016': '𑌶𑍂', '\uE020': '𑌪𑍍𑌲', '\uE021': '𑌪𑍍𑌲𑌾',
        '\uE022': '𑌪𑍍𑌲𑌿', '\uE023': '𑌪𑍍𑌲𑍀', '\uE027': '𑌶𑍍𑌰𑍂', '\uE028': '𑌷𑍃',
        '\uE029': '𑌣𑍁',
    }
    for pua, gran in pua_to_grantha.items():
        line = line.replace(pua, gran)
        
    # 2. Replace swara markers and modifiers inside parentheses
    def _rep_marker(m):
        inner = m.group(1)
        # Keep numeric accents like (1), (2), (3), (4) or footnotes (s1) intact
        if re.match(r'^\d+$|^s\d+$', inner):
            return m.group(0)
        # If it's a known modifier code, map to canonical Unicode modifier symbol
        if inner in _MOD_CODE_TO_UNICODE:
            return f"({_MOD_CODE_TO_UNICODE[inner]})"
        # Convert Grantha/Malayalam swara letter to Devanagari
        deva_sw = grantha_or_mal_to_deva_marker(inner)
        return f"({deva_sw})"
    
    line = re.sub(r'\(([^)]+)\)', _rep_marker, line)
    
    # 3. Handle Vedic repha ൪ before consonants in base words
    line = re.sub(r'൪(?=[ക-ഹ])', 'ര്', line)
    
    # 4. Transliterate Malayalam base text tokens to Devanagari
    tokens = re.split(r'(\s+|[।॥]|\([^)]+\)|_|\.)', line)
    out = []
    for tok in tokens:
        if not tok:
            continue
        if (tok.startswith('(') and tok.endswith(')')) or tok in ('।', '॥', '_', '.', ' ') or tok.isspace():
            out.append(tok)
        else:
            if transliterate is not None:
                try:
                    deva_word = transliterate.process("Malayalam", "Devanagari", tok)
                    # Convert Malayalam ഴ (zha) / Vedic ळ if any
                    deva_word = deva_word.replace('ळ्', 'ळ्').replace('ऴ्', 'ळ्').replace('ऴ', 'ळ')
                    out.append(deva_word)
                except Exception:
                    out.append(tok)
            else:
                out.append(tok)
                
    result = "".join(out)
    # Clean up verse numbers to Devanagari digits
    _MAL_DIGITS_TO_DEVA = str.maketrans("0123456789൦൧൨൩൪൫൬൭൮൯", "०१२३४५६७८९०१२३४५६७८९")
    result = re.sub(r'॥\s*([०-९\d൦-൯]+)\s*॥', lambda m: f"॥{m.group(1).translate(_MAL_DIGITS_TO_DEVA)}॥", result)
    return result


def malayalam_to_devanagari(text: str) -> str:
    """General purpose transliteration from Malayalam text to Devanagari."""
    if not text:
        return ""
    if transliterate is None:
        return text
    try:
        # Handle Vedic repha ൪ before consonants in headers / words
        t = re.sub(r'൪(?=[ക-ഹ])', 'ര്', text)
        res = transliterate.process("Malayalam", "Devanagari", t)
        # Convert Malayalam ഴ / ऴ -> ळ
        res = res.replace('ऴ्', 'ळ्').replace('ऴ', 'ळ')
        return res
    except Exception:
        return text


def convert_malayalam_data_to_devanagari(data: dict) -> dict:
    """Clone a supersections tree and convert all Malayalam fields/mantras into Devanagari."""
    import copy
    deva_data = copy.deepcopy(data)
    
    MALAYALAM_CHAR_RE = re.compile(r'[\u0D00-\u0D7F]')
    
    for super_k, super_v in deva_data.items():
        if not isinstance(super_v, dict):
            continue
        if 'supersection_title' in super_v and MALAYALAM_CHAR_RE.search(super_v['supersection_title']):
            super_v['supersection_title'] = malayalam_to_devanagari(super_v['supersection_title'])
            
        for sec_k, sec_v in super_v.get('sections', {}).items():
            if not isinstance(sec_v, dict):
                continue
            if 'section_title' in sec_v and MALAYALAM_CHAR_RE.search(sec_v['section_title']):
                sec_v['section_title'] = malayalam_to_devanagari(sec_v['section_title'])
                
            for sub_k, sub_v in sec_v.get('subsections', {}).items():
                if not isinstance(sub_v, dict):
                    continue
                # 1. Header
                if 'header' in sub_v and isinstance(sub_v['header'], dict):
                    h_text = sub_v['header'].get('header', '')
                    if MALAYALAM_CHAR_RE.search(h_text):
                        sub_v['header']['header'] = malayalam_to_devanagari(h_text)
                elif 'header' in sub_v and isinstance(sub_v['header'], str):
                    if MALAYALAM_CHAR_RE.search(sub_v['header']):
                        sub_v['header'] = malayalam_to_devanagari(sub_v['header'])
                        
                # 2. Metadata
                for meta_key in ('saman_metadata', 'rik_metadata', 'rik_text'):
                    if meta_key in sub_v and sub_v[meta_key] and MALAYALAM_CHAR_RE.search(sub_v[meta_key]):
                        sub_v[meta_key] = malayalam_to_devanagari(sub_v[meta_key])
                        
                # 3. Footnotes
                if 'footnotes' in sub_v and isinstance(sub_v['footnotes'], dict):
                    new_fn = {}
                    for fn_k, fn_v in sub_v['footnotes'].items():
                        new_fn[fn_k] = malayalam_to_devanagari(fn_v) if MALAYALAM_CHAR_RE.search(fn_v) else fn_v
                    sub_v['footnotes'] = new_fn
                    
                # 4. Mantras (convert malayalam-mantra-sets to Devanagari with all swara modifiers)
                source_lines = []
                for m_set in sub_v.get('malayalam-mantra-sets', []):
                    m_line = m_set.get('malayalam-mantra', '')
                    if m_line:
                        source_lines.append(m_line)
                if not source_lines:
                    for m_set in sub_v.get('corrected-mantra_sets', []):
                        m_line = m_set.get('corrected-mantra', '')
                        if m_line:
                            source_lines.append(m_line)
                if not source_lines:
                    for m_set in sub_v.get('mantra_sets', []):
                        words = []
                        for w_dict in m_set.get('mantra-words', []):
                            w = w_dict.get('word', '')
                            sw = w_dict.get('swara', '')
                            if sw:
                                words.append(f"{w}({sw})")
                            else:
                                words.append(w)
                        if words:
                            source_lines.append(" ".join(words))
                            
                new_corrected = []
                for line in source_lines:
                    deva_line = malayalam_to_devanagari_mantra_line(line)
                    if deva_line:
                        new_corrected.append({'corrected-mantra': deva_line})
                if new_corrected:
                    sub_v['corrected-mantra_sets'] = new_corrected
                if 'malayalam-mantra-sets' in sub_v:
                    del sub_v['malayalam-mantra-sets']
                        
    return deva_data