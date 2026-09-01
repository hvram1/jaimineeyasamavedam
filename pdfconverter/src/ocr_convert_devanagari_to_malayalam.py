import sys
import os
import argparse
import re
import subprocess
from pathlib import Path

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

try:
    from pdf2image import convert_from_path
except ImportError:
    print("pdf2image not installed. Run: pip install pdf2image")
    sys.exit(1)

try:
    import pytesseract
    from pytesseract import Output
except ImportError:
    print("pytesseract not installed. Run: pip install pytesseract")
    sys.exit(1)

try:
    from aksharamukha import transliterate
except ImportError:
    transliterate = None
    print("aksharamukha not installed. Run: pip install aksharamukha")
    sys.exit(1)


def find_tesseract():
    tesseract_candidates = [
        r'C:\Program Files\Tesseract-OCR\tesseract.exe',
        r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
    ]
    for p in tesseract_candidates:
        if os.path.exists(p):
            pytesseract.pytesseract.tesseract_cmd = p
            return p
    return None


def check_tesseract_langs():
    try:
        langs = pytesseract.get_languages()
        return langs
    except Exception:
        return []


supported_ocr_langs = ['san', 'hin', 'eng']


def ocr_page(image, lang='san+eng'):
    text = pytesseract.image_to_string(image, lang=lang, config='--psm 3')
    lines = []
    for line in text.splitlines():
        line = line.strip()
        if line:
            lines.append({'text': line, 'y': 0})
    return lines


def devanagari_to_malayalam(text):
    if not text.strip():
        return text
    if not transliterate:
        raise RuntimeError("aksharamukha library not available.")
    if not re.search(r'[\u0900-\u097F]', text):
        return text
    return transliterate.process('Devanagari', 'Malayalam', text)


def generate_ocr_html(pages_ocr, title="Vedic Document"):
    mal_pages = []
    dev_pages = []
    for p in pages_ocr:
        dev_lines = ''.join(f'<div class="line dev-text">{l["dev_text"]}</div>' for l in p['lines'])
        mal_lines = ''.join(f'<div class="line mal-text">{l["mal_text"]}</div>' for l in p['lines'])
        dev_pages.append(f'''<div class="page"><div class="page-body">{dev_lines}</div></div><div class="pb"></div>''')
        mal_pages.append(f'''<div class="page"><div class="page-body">{mal_lines}</div></div><div class="pb"></div>''')

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{title}</title>
<style>
@page {{ size: A4; margin: 15mm; }}
body {{ background: #f3f4f6; color: #111; font-family: 'Inter', sans-serif; margin: 0; padding: 1.5rem; display: flex; flex-direction: column; align-items: center; }}
.page {{ background: #fff; width: 100%; max-width: 900px; min-height: 1100px; padding: 2.2rem 2.8rem; box-shadow: 0 10px 30px rgba(0,0,0,0.08); border-radius: 4px; box-sizing: border-box; margin-bottom: 2rem; }}
.line {{ line-height: 2.2; white-space: pre-wrap; margin-bottom: 0.2rem; font-size: 1rem; }}
.dev-text {{ font-family: 'Noto Serif Devanagari', serif; color: #0f172a; }}
.mal-text {{ font-family: 'Noto Serif Malayalam', 'Noto Serif Devanagari', serif; color: #0f172a; }}
.pb {{ page-break-after: always; }}
.no-print {{ display: flex; gap: 0.75rem; margin-bottom: 1.5rem; }}
.btn {{ background: #f9fafb; color: #374151; border: 1px solid #d1d5db; padding: 0.5rem 1.2rem; border-radius: 9999px; cursor: pointer; font-size: 0.9rem; }}
.btn.active {{ background: #1d4ed8; color: #fff; border-color: #1d4ed8; }}
@media print {{ body {{ background: #fff; padding: 0; }} .no-print {{ display: none; }} .page {{ box-shadow: none; padding: 0; margin-bottom: 0; }} }}
</style>
</head>
<body>
<div class="no-print">
<button class="btn active" onclick="showDoc('mal')">Malayalam</button>
<button class="btn" onclick="showDoc('dev')">Devanagari</button>
</div>
<div id="doc-mal">{''.join(mal_pages)}</div>
<div id="doc-dev" style="display:none">{''.join(dev_pages)}</div>
<script>
function showDoc(m) {{ document.getElementById('doc-mal').style.display = m === 'mal' ? 'block' : 'none'; document.getElementById('doc-dev').style.display = m === 'dev' ? 'block' : 'none'; }}
</script>
</body>
</html>'''
    return html


def convert_html_to_pdf(html_path, pdf_path):
    browsers = [
        r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
        r'C:\Program Files\Microsoft\Edge\Application\msedge.exe',
        r'C:\Program Files\Google\Chrome\Application\chrome.exe',
        r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
    ]
    browser = None
    for b in browsers:
        if os.path.exists(b):
            browser = b
            break
    if not browser:
        print("Warning: No browser found for PDF rendering.", file=sys.stderr)
        return False
    html_uri = Path(html_path).resolve().as_uri()
    pdf_abs = Path(pdf_path).resolve()
    cmd = [browser, '--headless', '--disable-gpu', '--no-pdf-header-footer', f'--print-to-pdf={pdf_abs}', html_uri]
    try:
        res = subprocess.run(cmd, capture_output=True, timeout=120)
        if res.returncode == 0 and pdf_abs.exists():
            print(f"Saved: {pdf_path}")
            return True
        print(f"PDF failed: {res.stderr.decode('utf-8', 'ignore')}", file=sys.stderr)
        return False
    except subprocess.TimeoutExpired:
        print("PDF generation timed out.", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(description="OCR-based Devanagari PDF to Malayalam PDF converter")
    parser.add_argument("--input", "-i", required=True, help="Input PDF (scanned/image-based)")
    parser.add_argument("--output", "-o", help="Output Malayalam text file")
    parser.add_argument("--html", help="Output HTML viewer file")
    parser.add_argument("--pdf", "-p", help="Output PDF file")
    parser.add_argument("--lang", default="san", help="Tesseract OCR language(s) (default: san)")
    parser.add_argument("--dpi", type=int, default=300, help="DPI for PDF-to-image conversion (default: 300)")
    parser.add_argument("--pages", help="Page range e.g. '1-10', '5', 'all'")
    parser.add_argument("--no-html", action="store_true", help="Skip HTML generation")
    parser.add_argument("--no-pdf", action="store_true", help="Skip PDF generation")
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"File not found: {args.input}")
        sys.exit(1)

    tesseract_bin = find_tesseract()
    if not tesseract_bin:
        print("Tesseract not found at expected paths.", file=sys.stderr)
        sys.exit(1)

    avail = check_tesseract_langs()
    print(f"Tesseract: {pytesseract.pytesseract.tesseract_cmd}")
    print(f"Available languages: {avail}")
    ocr_lang = args.lang
    for lang_part in ocr_lang.split('+'):
        if lang_part not in avail:
            print(f"Warning: language '{lang_part}' not installed for Tesseract.")
    print(f"Using OCR languages: {ocr_lang}")

    # Parse page range
    from pdf2image import pdfinfo_from_path
    info = pdfinfo_from_path(args.input)
    total = info['Pages']
    print(f"PDF has {total} pages")

    if args.pages and args.pages.lower() != 'all':
        indices = []
        for part in args.pages.split(','):
            part = part.strip()
            if '-' in part:
                a, b = part.split('-')
                indices.extend(range(max(1, int(a)), min(total, int(b)) + 1))
            else:
                indices.append(int(part))
    else:
        indices = list(range(1, total + 1))

    stem = Path(args.input).stem
    out_dir = Path(args.output).parent if args.output else Path.cwd()
    os.makedirs(out_dir, exist_ok=True)

    # Process pages
    pages_ocr = []
    batch_size = 5
    for batch_start in range(0, len(indices), batch_size):
        batch = indices[batch_start:batch_start + batch_size]
        first, last = batch[0], batch[-1]
        print(f"Processing pages {first}-{last} ({batch_start + len(batch)}/{len(indices)})...")
        images = convert_from_path(args.input, first_page=first, last_page=last, dpi=args.dpi)
        for img, page_num in zip(images, batch):
            raw_lines = ocr_page(img, lang=ocr_lang)
            lines = []
            for rl in raw_lines:
                dt = rl['text']
                mt = devanagari_to_malayalam(dt)
                lines.append({'dev_text': dt, 'mal_text': mt, 'y': rl['y']})
            pages_ocr.append({'page': page_num, 'lines': lines})

    # Save text output
    if not args.output:
        args.output = out_dir / f"{stem}_malayalam.txt"
    with open(args.output, 'w', encoding='utf-8') as f:
        for p in pages_ocr:
            for l in p['lines']:
                f.write(l['mal_text'] + '\n')
            f.write('\n')
    print(f"Saved: {args.output}")

    # HTML + PDF
    if not args.no_html:
        if not args.html:
            args.html = out_dir / f"{stem}_malayalam.html"
        html_content = generate_ocr_html(pages_ocr, title=f"OCR Conversion: {stem}")
        with open(args.html, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"Saved: {args.html}")

        if not args.no_pdf:
            if not args.pdf:
                args.pdf = out_dir / f"{stem}_malayalam.pdf"
            convert_html_to_pdf(str(args.html), str(args.pdf))

    print("Done!")


if __name__ == "__main__":
    main()
