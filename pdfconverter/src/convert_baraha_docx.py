"""
Pass 1: Baraha DOCX → Devanagari → Malayalam → HTML + PDF

Pipeline:
  1. Extract raw text from s.docx (mammoth)
  2. Parse Baraha-encoded Sanskrit → Unicode Devanagari (baraha_to_devanagari)
  3. Transliterate Devanagari → Malayalam (aksharamukha via VedicTransliterate)
  4. Generate parallel-view HTML
  5. Generate PDF via headless browser

Usage:
  python src/tools/convert_baraha_docx.py s.docx [--output output_stem]
"""

import sys
import os
import re
import io
import argparse
import subprocess
from pathlib import Path

import mammoth

sys.path.insert(0, os.path.dirname(__file__))
from baraha_to_devanagari import parse_baraha_document
from convert_devanagari_to_malayalam import VedicTransliterate, clean_accent_spaces, format_accents_html, convert_html_to_pdf


def extract_docx_text(docx_path: str) -> str:
    """Extract raw text from a .docx file using mammoth."""
    with open(docx_path, 'rb') as f:
        result = mammoth.extract_raw_text(f)
        return result.value


def split_into_lines(text: str) -> list:
    """Split text into lines, preserving empty lines for spacing."""
    return text.split('\n')


def transliterate_to_malayalam(dev_text: str) -> str:
    """Transliterate Devanagari text to Malayalam preserving Vedic accents."""
    lines = dev_text.split('\n')
    mal_lines = []
    for line in lines:
        if re.search(r'[\u0900-\u097F\u1CD0-\u1CF9\uA8E0-\uA8FF]', line):
            mal = VedicTransliterate.devanagari_to_malayalam(line, nasal_mode='symbol')
            mal_lines.append(mal)
        else:
            mal_lines.append(line)
    return '\n'.join(mal_lines)


def generate_html(dev_text: str, mal_text: str, title: str = "Vedic Document") -> str:
    """Generate parallel-view HTML from Devanagari and Malayalam text."""
    dev_lines = dev_text.split('\n')
    mal_lines = mal_text.split('\n')

    def escape_html(s):
        return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

    dev_body = []
    mal_body = []
    for d_line, m_line in zip(dev_lines, mal_lines):
        d_escaped = escape_html(d_line)
        m_escaped = escape_html(m_line)
        m_escaped = format_accents_html(m_escaped, wrap_anudatta=True)

        is_english = not re.search(r'[\u0900-\u097F\u0D00-\u0D7F]', d_line)
        cls_dev = 'line devanagari-text' + (' english-line' if is_english else '')
        cls_mal = 'line malayalam-text' + (' english-line' if is_english else '')

        dev_body.append(f'<div class="{cls_dev}">{d_escaped}</div>')
        mal_body.append(f'<div class="{cls_mal}">{m_escaped}</div>')

    mal_content = '\n'.join(mal_body)
    dev_content = '\n'.join(dev_body)

    html = f"""<!DOCTYPE html>
<html lang="sa">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Serif+Devanagari:wght@400;600;700&family=Noto+Serif+Malayalam:wght@400;600;700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        @page {{
            size: A4;
            margin: 15mm 15mm;
        }}
        body {{
            background-color: #f3f4f6;
            color: #111827;
            font-family: 'Inter', sans-serif;
            margin: 0;
            padding: 1.5rem;
            display: flex;
            flex-direction: column;
            align-items: center;
        }}
        .no-print {{
            display: flex;
            gap: 0.75rem;
            margin-bottom: 1.5rem;
            background: #ffffff;
            padding: 0.75rem 1.25rem;
            border-radius: 9999px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.06);
            border: 1px solid #e5e7eb;
        }}
        .btn {{
            background: #f9fafb;
            color: #374151;
            border: 1px solid #d1d5db;
            padding: 0.5rem 1.2rem;
            border-radius: 9999px;
            cursor: pointer;
            font-size: 0.9rem;
            font-weight: 500;
            transition: all 0.15s ease;
        }}
        .btn:hover, .btn.active {{
            background: #1d4ed8;
            color: #ffffff;
            border-color: #1d4ed8;
        }}
        .document-container {{
            background: #ffffff;
            width: 100%;
            max-width: 900px;
            padding: 2.2rem 2.8rem;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
            border-radius: 4px;
            box-sizing: border-box;
            margin-bottom: 2rem;
        }}
        .line {{
            line-height: 2.5;
            white-space: pre-wrap;
            margin-bottom: 0.3rem;
        }}
        .devanagari-text {{
            font-family: 'Noto Serif Devanagari', serif;
            color: #0f172a;
        }}
        .malayalam-text {{
            font-family: 'Noto Serif Malayalam', 'Noto Serif Devanagari', serif;
            color: #0f172a;
        }}
        .english-line {{
            font-family: 'Inter', sans-serif;
            color: #4b5563;
            font-size: 0.9rem;
        }}
        .anudatta-bar {{
            display: inline-block;
            width: 0;
            overflow: visible;
            position: relative;
            left: -0.35em;
            vertical-align: -0.52em;
            font-weight: 700;
            white-space: nowrap;
        }}
        @media print {{
            body {{
                background: #ffffff;
                padding: 0;
            }}
            .no-print {{
                display: none;
            }}
            .document-container {{
                box-shadow: none;
                padding: 0;
                width: 100%;
                margin-bottom: 0;
            }}
        }}
    </style>
</head>
<body>
    <div class="no-print">
        <button class="btn active" id="btn-mal" onclick="showDoc('mal')">Malayalam</button>
        <button class="btn" id="btn-dev" onclick="showDoc('dev')">Devanagari</button>
    </div>

    <div class="document-container" id="doc-mal" style="width: 100%; max-width: 900px;">
        {mal_content}
    </div>

    <div class="document-container" id="doc-dev" style="width: 100%; max-width: 900px; display: none;">
        {dev_content}
    </div>

    <script>
        function showDoc(mode) {{
            document.getElementById('doc-mal').style.display = mode === 'mal' ? 'block' : 'none';
            document.getElementById('doc-dev').style.display = mode === 'dev' ? 'block' : 'none';
            document.getElementById('btn-mal').classList.toggle('active', mode === 'mal');
            document.getElementById('btn-dev').classList.toggle('active', mode === 'dev');
        }}
    </script>
</body>
</html>"""
    return html


def convert_baraha_docx(docx_path: str, output_stem: str = None):
    """End-to-end conversion: docx → Devanagari → Malayalam → HTML → PDF."""
    if not os.path.exists(docx_path):
        raise FileNotFoundError(f"Input file not found: {docx_path}")

    if output_stem is None:
        output_stem = Path(docx_path).stem

    print(f"[1/5] Extracting text from {docx_path}...")
    raw_text = extract_docx_text(docx_path)
    print(f"  Extracted {len(raw_text)} characters")

    print(f"[2/5] Parsing Baraha → Devanagari...")
    dev_text = parse_baraha_document(raw_text)
    print(f"  Generated {len(dev_text)} characters Devanagari")

    print(f"[3/5] Transliterating Devanagari → Malayalam...")
    mal_text = transliterate_to_malayalam(dev_text)
    print(f"  Generated {len(mal_text)} characters Malayalam")

    # Save text outputs
    dev_txt_path = f"{output_stem}_devanagari.txt"
    mal_txt_path = f"{output_stem}_malayalam.txt"
    with io.open(dev_txt_path, 'w', encoding='utf-8') as f:
        f.write(dev_text)
    print(f"  Saved Devanagari text: {dev_txt_path}")
    with io.open(mal_txt_path, 'w', encoding='utf-8') as f:
        f.write(mal_text)
    print(f"  Saved Malayalam text: {mal_txt_path}")

    print(f"[4/5] Generating HTML...")
    html_path = f"{output_stem}_malayalam.html"
    html_content = generate_html(dev_text, mal_text, title=f"Vedic Document: {output_stem}")
    with io.open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"  Saved HTML: {html_path}")

    print(f"[5/5] Generating PDF...")
    pdf_path = f"{output_stem}_malayalam.pdf"
    ok = convert_html_to_pdf(html_path, pdf_path)
    if ok:
        print(f"  Saved PDF: {pdf_path}")
    else:
        print("  PDF generation skipped (no browser available)")

    print("Conversion completed successfully!")


def main():
    parser = argparse.ArgumentParser(description="Convert Baraha DOCX to Devanagari/Malayalam HTML+PDF")
    parser.add_argument("input", help="Path to Baraha .docx file")
    parser.add_argument("--output", "-o", help="Output stem (default: input filename stem)")
    args = parser.parse_args()

    try:
        convert_baraha_docx(args.input, args.output)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
