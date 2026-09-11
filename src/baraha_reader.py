"""Baraha DOCX extraction, Vedic transliteration, and AST generator for render_pdf.py.

Converts Baraha-encoded Vedic documents into hierarchical AST suitable for rendering
via render_pdf.py into Devanagari HTML and PDF with authentic Vedic typography and accents.
"""

import os
import sys
import re
import zipfile
from pathlib import Path
import xml.etree.ElementTree as ET

# Try importing from 'vedavms html/transliterate.py' if available
try:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "vedavms html"))
    from transliterate import baraha_to_devanagari
except Exception:
    # Standalone fallback definition
    CONSONANTS = {
        'k': 'क्', 'kh': 'ख्', 'K': 'ख्', 'g': 'ग्', 'gh': 'घ्', 'G': 'घ्', '~g': 'ङ्', '~G': 'ङ्',
        'c': 'च्', 'ch': 'च्', 'Ch': 'छ्', 'C': 'छ्', 'j': 'ज्', 'jh': 'झ्', 'J': 'झ्', '~j': 'ञ्', '~J': 'ञ्',
        'T': 'ट्', 'Th': 'ठ्', 'TH': 'ठ्', 'D': 'ड्', 'Dh': 'ढ्', 'DH': 'ढ्', 'N': 'ण्',
        't': 'त्', 'th': 'थ्', 'd': 'द्', 'dh': 'ध्', 'n': 'न्',
        'p': 'प्', 'ph': 'फ्', 'P': 'फ्', 'b': 'ब्', 'bh': 'भ्', 'B': 'भ्', 'm': 'म्',
        'y': 'य्', 'r': 'र्', 'l': 'ल्', 'v': 'व्', 'w': 'व्',
        'S': 'श्', 'sh': 'श्', 'Sh': 'ष्', 'shh': 'ष्', 's': 'स्', 'h': 'ह्', 'L': 'ळ्',
        'x': 'क्ष्', 'kSh': 'क्ष्', 'j~j': 'ज्ञ्', 'GY': 'ज्ञ्',
    }

    VOWEL_SIGNS = {
        'a': '', 'A': 'ा', 'aa': 'ा', 'i': 'ि', 'I': 'ी', 'ee': 'ी',
        'u': 'ु', 'U': 'ू', 'oo': 'ू', 'Ru': 'ृ', 'ru': 'ृ', 'RU': 'ॄ',
        'e': 'े', 'E': 'े', 'ai': 'ै', 'o': 'ो', 'O': 'ो', 'au': 'ौ',
    }

    INDEPENDENT_VOWELS = {
        'a': 'अ', 'A': 'आ', 'aa': 'आ', 'i': 'इ', 'I': 'ई', 'ee': 'ई',
        'u': 'उ', 'U': 'ऊ', 'oo': 'ऊ', 'Ru': 'ऋ', 'ru': 'ऋ', 'RU': 'ॠ',
        'e': 'ए', 'E': 'ए', 'ai': 'ऐ', 'o': 'ओ', 'O': 'ओ', 'au': 'औ',
    }

    CONSONANT_KEYS = sorted(CONSONANTS.keys(), key=len, reverse=True)
    VOWEL_KEYS = sorted(VOWEL_SIGNS.keys(), key=len, reverse=True)

    def baraha_to_devanagari(text: str) -> str:
        if not text:
            return ""
        placeholders = []
        def repl_eng(m):
            placeholders.append(m.group(0))
            return f'\uE000{len(placeholders)-1}\uE001'

        if re.search(r'\b(Korvai|Padam|Prapaataka|Series|Dasinis|Special|First and Last|Notes for Users)\b', text, re.I):
            return text

        text = re.sub(r'\([A-Za-z]+\d+[a-z]?\)', repl_eng, text)
        text = re.sub(r'\b[A-Za-z]\d+\b', repl_eng, text)
        text = re.sub(r'\b[A-Z]\.[A-Z0-9\.]+\b', repl_eng, text)

        text = re.sub(r'\s+([q#$HM]+)', r'\1', text)
        text = text.replace('~g', 'ङ्').replace('~G', 'ङ्').replace('~j', 'ञ्').replace('~J', 'ञ्')
        text = re.sub(r'\(gm~?\)', '\uA8F3', text, flags=re.I)
        text = re.sub(r'\(gg\)', '\u1CFA', text, flags=re.I)
        text = text.replace('~M', '\u00A0\u0901')
        text = text.replace('&', 'ऽ').replace('||', '॥').replace('|', '।')
        text = re.sub(r'\^+', '\u200C', text)

        text = re.sub(r'([q#$]+)H', r'H\1', text)
        text = re.sub(r'([q#$]+)M', r'M\1', text)

        out = []
        i = 0
        n = len(text)
        while i < n:
            if text[i] == '\uE000':
                end_p = text.find('\uE001', i)
                if end_p != -1:
                    idx = int(text[i + 1:end_p])
                    out.append(placeholders[idx])
                    i = end_p + 1
                    continue

            if text[i] == 'q':
                out.append('॒')
                i += 1
                continue
            elif text[i] == '#':
                out.append('॑')
                i += 1
                continue
            elif text[i] == '$':
                out.append('᳚')
                i += 1
                continue
            elif text[i] == 'H':
                out.append('ः')
                i += 1
                continue
            elif text[i] == 'M':
                out.append('ं')
                i += 1
                continue
            elif text[i] == '\u200C':
                out.append('\u200C')
                i += 1
                continue
            elif text[i] in ' \t\n\r।,॥():-0123456789.[]{}~/\\+*\uA8F3\uA8F2\uA8F4\u1CFA\u00A0\u0901':
                out.append(text[i])
                i += 1
                continue

            matched_c = None
            for c in CONSONANT_KEYS:
                if text.startswith(c, i):
                    matched_c = c
                    break

            if matched_c:
                i += len(matched_c)
                matched_v = None
                for v in VOWEL_KEYS:
                    if text.startswith(v, i):
                        matched_v = v
                        break

                if matched_v:
                    i += len(matched_v)
                    cons_char = CONSONANTS[matched_c][:-1]
                    v_sign = VOWEL_SIGNS[matched_v]
                    out.append(cons_char + v_sign)
                else:
                    out.append(CONSONANTS[matched_c])
                continue

            matched_v = None
            for v in VOWEL_KEYS:
                if text.startswith(v, i):
                    matched_v = v
                    break

            if matched_v:
                i += len(matched_v)
                out.append(INDEPENDENT_VOWELS[matched_v])
                continue

            out.append(text[i])
            i += 1

        res = ''.join(out)
        res = re.sub(r'\u094D+', '्', res)
        res = re.sub(r'([\u0951\u0952\u1CDA])(ः)', r'\2\1', res)
        res = re.sub(r'([\u0951\u0952\u1CDA])(ं)', r'\2\1', res)
        res = re.sub(r'\s+ँ', '\u00A0ँ', res)
        res = re.sub(r'([ \t\n।,॥\(\)\[\]\{\}\-])([\u0951\u0952\u1CDA]+)', r'\1', res)
        return res


DOCX_NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}


def extract_docx_paragraphs(docx_path: str | Path) -> list[str]:
    """Extract raw paragraphs from a Word (.docx) document using standard library zipfile."""
    docx_path = Path(docx_path)
    if not docx_path.exists():
        raise FileNotFoundError(f"Input DOCX file not found: {docx_path}")

    with zipfile.ZipFile(docx_path, 'r') as z:
        doc_xml = z.read('word/document.xml')

    root = ET.fromstring(doc_xml)
    paras = []
    for p in root.findall('.//w:p', DOCX_NS):
        text = ''.join([n.text for n in p.findall('.//w:t', DOCX_NS) if n.text]).strip()
        if text:
            paras.append(text)

    return paras


def parse_baraha_docx_to_ast(docx_path: str | Path, title: str = None, jsv_version: str = None, generated_at: str = None, chapter_regex: str = None) -> tuple[dict, str]:
    """
    Parses a Baraha-encoded Word DOCX document into the structured AST format expected by render_pdf.py.
    
    Returns:
        (ast_data, doc_title_sa)
    """
    raw_paras = extract_docx_paragraphs(docx_path)
    
    # Default chapter regex covers standard Upanishad / Aranyakam / Brahmana numbering
    ch_pattern = re.compile(chapter_regex or r'^([1-6])(?!\.)\s*(.*(?:vall[iI]|nArAyaN|aruNa|triNAcikE|kANDa|ashtaka|adhyAya|prapathaka).*)$', re.I)

    chapters = []
    current_chapter = None
    current_section = None

    for p in raw_paras:
        ch_m = ch_pattern.match(p)
        if ch_m:
            ch_num = int(ch_m.group(1))
            ch_raw_title = ch_m.group(2).strip()
            ch_deva = baraha_to_devanagari(ch_raw_title)
            current_chapter = {
                'num': ch_num,
                'title_raw': ch_raw_title,
                'title_deva': f"{ch_num}. {ch_deva}",
                'sections': []
            }
            chapters.append(current_chapter)
            current_section = None
            continue

        if current_chapter is None:
            continue

        sec_m = re.match(r'^(\d+\.\d+(?:\.\d+)?)\s*(.*)', p)
        tb_m = re.match(r'^(T\.B\.\d+\.\d+\.\d+\.\d+)', p)

        if sec_m:
            sec_num = sec_m.group(1)
            sec_name = sec_m.group(2).strip()
            sec_deva = baraha_to_devanagari(sec_name) if sec_name else ''
            current_section = {
                'num': sec_num,
                'title_deva': sec_deva,
                'ta_code': '',
                'content': []
            }
            current_chapter['sections'].append(current_section)
            continue
        elif current_chapter['num'] == 6 and tb_m:
            sec_num = tb_m.group(1)
            current_section = {
                'num': sec_num,
                'title_deva': '',
                'ta_code': sec_num,
                'content': []
            }
            current_chapter['sections'].append(current_section)
            continue

        if p.startswith('T.A.'):
            if current_section:
                current_section['ta_code'] = p
            continue

        if current_section is not None:
            deva_p = baraha_to_devanagari(p)
            current_section['content'].append(deva_p)
        elif current_chapter is not None:
            deva_p = baraha_to_devanagari(p)
            if not current_chapter['sections']:
                current_section = {
                    'num': f"{current_chapter['num']}.1",
                    'title_deva': 'प्रारम्भः',
                    'ta_code': '',
                    'content': [deva_p]
                }
                current_chapter['sections'].append(current_section)
            else:
                current_chapter['sections'][-1]['content'].append(deva_p)

    doc_title_sa = title or "तैत्तिरीयोपनिषत्, अरुणप्रश्नम्, तृणाचिकेतम्"

    # Build flattened AST: one supersection (doc title) -> sections (chapters) -> subsections
    sections = {}
    for ch in chapters:
        sec_key = f"section_{ch['num']}"
        sec_data = {
            'section_title': ch['title_deva'],
            'subsections': {}
        }
        for sub_idx, sec in enumerate(ch['sections'], 1):
            sub_key = f"subsection_{sub_idx}"
            sub_title_parts = [sec['num']]
            if sec['title_deva']:
                sub_title_parts.append(sec['title_deva'])
            full_sub_title = " ".join(sub_title_parts)
            sec_data['subsections'][sub_key] = {
                'header': {'header': full_sub_title},
                'ta_code': sec.get('ta_code', ''),
                'content_lines': sec['content'],
            }
        sec_data['Count'] = str(sum(
            len(sub.get('content_lines', []))
            for sub in sec_data['subsections'].values()
        ))
        sections[sec_key] = sec_data

    supersections = {
        'supersection_1': {
            'supersection_title': doc_title_sa,
            'sections': sections
        }
    }

    ast_data = {
        'meta': {
            'title': doc_title_sa,
            'version': jsv_version or '1.0.0',
            'generated_at': generated_at or '',
            'source': str(docx_path)
        },
        'supersections': supersections
    }

    return ast_data, doc_title_sa


if __name__ == '__main__':
    import argparse
    import json

    parser = argparse.ArgumentParser(
        description='Convert Baraha DOCX to JSON for render_pdf.py',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python src/baraha_reader.py "vedavms html/tu_baraha.docx"
  python src/baraha_reader.py "vedavms html/tu_baraha.docx" -o "vedavms html/tu_baraha.json"
        """
    )
    parser.add_argument('input_docx', help='Input Baraha .docx file')
    parser.add_argument('-o', '--output', default=None,
                        help='Output JSON file path (default: same name as input with .json extension)')
    parser.add_argument('--title', default=None,
                        help='Custom Sanskrit/Devanagari title for the document')
    parser.add_argument('--html', action='store_true',
                        help='Also generate standalone responsive VedaVMS reader HTML')
    parser.add_argument('--html-output', default=None,
                        help='Output HTML path if --html is specified')

    args = parser.parse_args()

    input_path = Path(args.input_docx)
    if not input_path.exists():
        print(f"[ERROR] Input file not found: {input_path}")
        sys.exit(1)

    output_path = Path(args.output) if args.output else input_path.with_suffix('.json')

    from utils import get_generated_metadata
    generated_at = get_generated_metadata()['generated_at']

    ast_data, doc_title = parse_baraha_docx_to_ast(
        input_path, title=args.title, generated_at=generated_at
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(ast_data, f, ensure_ascii=False, indent=2)

    print(f"[INFO] Converted: {input_path} -> {output_path}")
    print(f"[INFO] Title: {doc_title}")

    if args.html or args.html_output:
        try:
            try:
                from build_reader import ast_to_chapters, generate_reader_html
            except ImportError:
                sys.path.insert(0, str(Path(__file__).resolve().parent))
                from build_reader import ast_to_chapters, generate_reader_html

            html_out_path = Path(args.html_output) if args.html_output else input_path.with_suffix('.html')
            chapters = ast_to_chapters(ast_data)
            fonts = [
                {"label": "Noto Serif", "font": "'Noto Serif Devanagari', 'Tiro Devanagari Sanskrit', serif", "weight": "500"},
                {"label": "Tiro Sanskrit", "font": "'Tiro Devanagari Sanskrit', 'Noto Serif Devanagari', serif", "weight": "400"},
                {"label": "Noto Sans", "font": "'Noto Sans Devanagari', sans-serif", "weight": "500"}
            ]
            book_meta = {
                "title": doc_title,
                "subtitle": "कृष्ण यजुर्वेदीय तैत्तिरीय आरण्यकम् (वेदमन्त्राः सस्वराः)" if "तैत्तिरीय" in doc_title else doc_title,
                "back_link": "documents.html",
                "back_label": "← Documents Index"
            }
            reader_html = generate_reader_html(book_meta, chapters, fonts)
            html_out_path.parent.mkdir(parents=True, exist_ok=True)
            with open(html_out_path, 'w', encoding='utf-8') as f:
                f.write(reader_html)
            print(f"[INFO] Generated VedaVMS Reader HTML: {html_out_path} ({os.path.getsize(html_out_path):,} bytes)")
        except Exception as e:
            print(f"[ERROR] Failed to generate HTML reader: {e}")
