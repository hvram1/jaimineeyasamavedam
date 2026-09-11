"""VedaVMS Reader Generator: Converts Baraha DOCX documents into standalone responsive Vedic HTML Readers.

Features:
- DOCX paragraph extraction via standard library (zipfile + xml.etree.ElementTree).
- Phonetic and Vedic svara transliteration via transliterate.py.
- Chapter and Anuvaka TOC navigation tree.
- Dynamic font switcher (Noto Serif Devanagari, Tiro Devanagari Sanskrit, Noto Sans).
- Font-size scaling controls (A+ / A-) and print layout styles.
- Zero external package dependencies.
"""

import os
import sys
import re
import json
import zipfile
import argparse
from pathlib import Path
import xml.etree.ElementTree as ET

try:
    from .transliterate import baraha_to_devanagari
except ImportError:
    try:
        from transliterate import baraha_to_devanagari
    except ImportError:
        _cur = Path(__file__).resolve().parent
        for _p in [_cur, _cur.parent / "src", _cur.parent / "vedavms_html"]:
            if str(_p) not in sys.path:
                sys.path.insert(0, str(_p))
        from transliterate import baraha_to_devanagari

DOCX_NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}


def esc(text: str) -> str:
    """Escape text for HTML attribute values."""
    return text.replace('&', '&amp;').replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;')


def extract_docx_paragraphs(docx_path: str | Path) -> list[str]:
    """Extract raw paragraphs from a Word (.docx) document."""
    docx_path = Path(docx_path)
    if not docx_path.exists():
        for cand in [Path("vedavms_html") / docx_path, Path(__file__).parent / docx_path, Path(__file__).parent.parent / "vedavms_html" / docx_path]:
            if cand.exists():
                docx_path = cand
                break
        else:
            raise FileNotFoundError(f"Input document not found: {docx_path}")

    with zipfile.ZipFile(docx_path, 'r') as z:
        doc_xml = z.read('word/document.xml')

    root = ET.fromstring(doc_xml)
    paras = []
    for p in root.findall('.//w:p', DOCX_NS):
        text = ''.join([node.text for node in p.findall('.//w:t', DOCX_NS) if node.text]).strip()
        if text:
            paras.append(text)

    return paras


def parse_chapters_and_sections(raw_paras: list[str], chapter_regex: str) -> list[dict]:
    """Parse raw paragraphs into structured chapters and anuvaka sections."""
    ch_pattern = re.compile(chapter_regex, re.I)

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
                'title_display_deva': f"{ch_num}. {ch_deva}",
                'title_display_raw': f"{ch_num}. {ch_raw_title}",
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
                'title_raw': sec_name,
                'title_deva': sec_deva,
                'ta_code': '',
                'content_deva': [],
                'content_raw': []
            }
            current_chapter['sections'].append(current_section)
            continue
        elif current_chapter['num'] == 6 and tb_m:
            sec_num = tb_m.group(1)
            current_section = {
                'num': sec_num,
                'title_raw': '',
                'title_deva': '',
                'ta_code': sec_num,
                'content_deva': [],
                'content_raw': []
            }
            current_chapter['sections'].append(current_section)
            continue

        if p.startswith('T.A.'):
            if current_section:
                current_section['ta_code'] = p
            continue

        if current_section is not None:
            current_section['content_raw'].append(p)
            current_section['content_deva'].append(baraha_to_devanagari(p))
        elif current_chapter is not None:
            if not current_chapter['sections']:
                current_section = {
                    'num': f"{current_chapter['num']}.1",
                    'title_raw': '',
                    'title_deva': 'प्रारम्भः',
                    'ta_code': '',
                    'content_raw': [p],
                    'content_deva': [baraha_to_devanagari(p)]
                }
                current_chapter['sections'].append(current_section)
            else:
                current_chapter['sections'][-1]['content_raw'].append(p)
                current_chapter['sections'][-1]['content_deva'].append(baraha_to_devanagari(p))

    return chapters


def generate_reader_html(book_meta: dict, chapters: list[dict], fonts: list[dict], default_font_size: float = 1.35) -> str:
    """Generate standalone responsive HTML reader with TOC navigation and typography controls."""
    title = book_meta.get("title", "Vedic Sanskrit Reader")
    subtitle = book_meta.get("subtitle", "कृष्ण यजुर्वेदीय आरण्यकम्")
    back_link = book_meta.get("back_link", "documents.html")
    back_label = book_meta.get("back_label", "← Documents Index")

    fonts_js = json.dumps(fonts, ensure_ascii=False)

    html_parts = []
    html_parts.append(f'''<!DOCTYPE html>
<html lang="sa">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Sanskrit Vedic Text</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Serif+Devanagari:wght@400;500;600;700&family=Tiro+Devanagari+Sanskrit:ital@0;1&family=Noto+Sans+Devanagari:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --saffron: #D84315;
            --maroon: #7B1113;
            --cream: #FFFDF9;
            --gold: #C68A1E;
            --dark-brown: #2D1E18;
            --white: #FFFFFF;
            --card-bg: #FFFFFF;
            --border-color: #EADDC9;
            --accent-bg: #FFF3E0;
            --font-size: {default_font_size}rem;
            --verse-font: 'Noto Serif Devanagari', 'Tiro Devanagari Sanskrit', serif;
            --verse-weight: 500;
        }}

        html {{
            scroll-behavior: smooth;
            scroll-padding-top: 5rem;
        }}

        .chapter-container, .anuvaka-block, [id] {{
            scroll-margin-top: 5rem;
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: var(--verse-font);
            font-weight: var(--verse-weight);
            background: var(--cream);
            color: var(--dark-brown);
            line-height: 2.1;
            font-size: var(--font-size);
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }}

        .header {{
            background: linear-gradient(135deg, #153E75 0%, #1D5296 50%, #2563A8 100%);
            color: white;
            padding: 1rem;
            text-align: center;
            border-bottom: 3px solid var(--gold);
            position: sticky;
            top: 0;
            z-index: 1000;
            box-shadow: 0 3px 12px rgba(0,0,0,0.18);
        }}

        .header-content {{
            max-width: 1240px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 1rem;
        }}

        .logo {{
            font-family: 'Noto Serif Devanagari', serif;
            font-size: 1.6rem;
            font-weight: 700;
            color: white;
            text-decoration: none;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}

        .om-symbol {{
            color: #FFD54F;
            font-size: 1.8rem;
        }}

        .controls {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}

        .btn-ctrl {{
            background: rgba(255,255,255,0.18);
            color: white;
            border: 1px solid rgba(255,255,255,0.35);
            border-radius: 6px;
            padding: 0.4rem 0.85rem;
            cursor: pointer;
            font-weight: 600;
            font-size: 0.95rem;
            transition: all 0.2s;
            text-decoration: none;
            font-family: sans-serif;
        }}

        .btn-ctrl:hover {{
            background: rgba(255,255,255,0.32);
            transform: translateY(-1px);
        }}

        .layout {{
            max-width: 1240px;
            margin: 1.75rem auto;
            padding: 0 1rem;
            display: grid;
            grid-template-columns: 290px 1fr;
            gap: 2rem;
            align-items: flex-start;
        }}

        .toc-sidebar {{
            background: var(--white);
            border: 1px solid var(--border-color);
            border-radius: 10px;
            padding: 1.25rem;
            position: sticky;
            top: 5.5rem;
            max-height: calc(100vh - 7rem);
            overflow-y: auto;
            box-shadow: 0 4px 14px rgba(0,0,0,0.06);
        }}

        .toc-title {{
            font-size: 1.15rem;
            font-weight: 700;
            color: var(--maroon);
            margin-bottom: 0.85rem;
            border-bottom: 2px solid var(--saffron);
            padding-bottom: 0.4rem;
            font-family: 'Noto Serif Devanagari', serif;
        }}

        .toc-list {{
            list-style: none;
        }}

        .toc-chapter {{
            margin-bottom: 0.5rem;
        }}

        .toc-ch-header {{
            display: flex;
            align-items: center;
            gap: 0.4rem;
            cursor: pointer;
            padding: 0.3rem 0.4rem;
            border-radius: 4px;
            transition: background 0.15s;
        }}

        .toc-ch-header:hover {{
            background: var(--accent-bg);
        }}

        .toc-ch-title {{
            font-weight: 700;
            color: var(--dark-brown);
            font-size: 1rem;
            flex: 1;
        }}

        .toc-ch-title a {{
            color: var(--maroon);
            text-decoration: none;
        }}

        .toc-ch-toggle {{
            font-size: 0.7rem;
            color: #888;
            transition: transform 0.2s;
        }}

        .toc-chapter.collapsed .toc-ch-toggle {{
            transform: rotate(-90deg);
        }}

        .toc-sub-list {{
            list-style: none;
            padding-left: 0.85rem;
            overflow: hidden;
            max-height: 2000px;
            transition: max-height 0.3s ease;
        }}

        .toc-chapter.collapsed .toc-sub-list {{
            max-height: 0;
            padding-top: 0;
            padding-bottom: 0;
        }}

        .toc-sub-list li {{
            margin-bottom: 0.3rem;
        }}

        .toc-sub-list a {{
            color: #4A4A4A;
            text-decoration: none;
            font-size: 0.9rem;
            display: block;
            padding: 0.2rem 0.4rem;
            border-radius: 4px;
            transition: all 0.15s;
        }}

        .toc-sub-list a:hover {{
            background: var(--accent-bg);
            color: var(--saffron);
            font-weight: 600;
        }}

        .toc-sub-list a.active {{
            background: #FFE8D1 !important;
            color: #B23600 !important;
            font-weight: 700 !important;
            border-left: 3.5px solid var(--saffron);
            padding-left: 0.6rem;
            border-radius: 0 4px 4px 0;
            box-shadow: 0 1px 3px rgba(216, 67, 21, 0.12);
        }}

        /* Collapsible sidebar styles */
        .layout.sidebar-collapsed {{
            grid-template-columns: 0 1fr;
            gap: 0;
        }}

        .layout.sidebar-collapsed .toc-sidebar {{
            width: 0;
            min-width: 0;
            padding: 0;
            overflow: hidden;
            border: none;
            opacity: 0;
            pointer-events: none;
        }}

        .toggle-sidebar-btn {{
            background: rgba(255,255,255,0.18);
            color: white;
            border: 1px solid rgba(255,255,255,0.35);
            border-radius: 6px;
            padding: 0.4rem 0.85rem;
            cursor: pointer;
            font-weight: 600;
            font-size: 0.95rem;
            transition: all 0.2s;
            font-family: sans-serif;
            white-space: nowrap;
        }}

        .toggle-sidebar-btn:hover {{
            background: rgba(255,255,255,0.32);
            transform: translateY(-1px);
        }}

        .main-content {{
            background: var(--white);
            border: 1px solid var(--border-color);
            border-radius: 10px;
            padding: 2.25rem 2.75rem;
            box-shadow: 0 4px 16px rgba(0,0,0,0.06);
            --font-size: {default_font_size}rem;
            font-size: var(--font-size);
        }}

        .back-to-top {{
            position: fixed;
            bottom: 1.75rem;
            right: 1.75rem;
            width: 44px;
            height: 44px;
            background: var(--saffron);
            color: white;
            border: none;
            border-radius: 50%;
            font-size: 1.25rem;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 4px 12px rgba(216,67,21,0.35);
            opacity: 0;
            visibility: hidden;
            transition: all 0.25s ease;
            z-index: 999;
        }}
        .back-to-top.visible {{
            opacity: 1;
            visibility: visible;
        }}
        .back-to-top:hover {{
            background: var(--maroon);
            transform: translateY(-2px);
        }}

        .main-title {{
            text-align: center;
            margin-bottom: 2.5rem;
            padding-bottom: 1.25rem;
            border-bottom: 2px solid var(--gold);
        }}

        .main-title h1 {{
            font-family: 'Noto Serif Devanagari', serif;
            font-size: 2.25rem;
            color: var(--maroon);
            margin-bottom: 0.5rem;
            letter-spacing: 0.5px;
        }}

        .main-title .sub-heading {{
            font-size: 1.15rem;
            color: var(--saffron);
            font-weight: 600;
        }}

        .chapter-container {{
            margin-bottom: 3.5rem;
        }}

        .chapter-heading {{
            background: linear-gradient(90deg, #7B1113 0%, #A52A2A 100%);
            color: white;
            padding: 0.9rem 1.6rem;
            border-radius: 8px;
            font-size: 1.5rem;
            margin-bottom: 1.75rem;
            font-family: 'Noto Serif Devanagari', serif;
            box-shadow: 0 3px 8px rgba(123,17,19,0.25);
        }}

        .anuvaka-block {{
            background: #FFFAF5;
            border: 1px solid #F0E6D8;
            border-left: 5px solid var(--saffron);
            border-radius: 8px;
            padding: 1.35rem 1.6rem;
            margin-bottom: 2rem;
            box-shadow: 0 2px 6px rgba(0,0,0,0.03);
            content-visibility: auto;
            contain-intrinsic-size: auto 220px;
        }}

        .anuvaka-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px dashed #E0D0C0;
            padding-bottom: 0.6rem;
            margin-bottom: 1.15rem;
        }}

        .anuvaka-num {{
            font-weight: 700;
            color: var(--maroon);
            font-size: 1.15rem;
            font-family: 'Noto Serif Devanagari', serif;
        }}

        .anuvaka-code {{
            font-size: 0.82rem;
            color: #777;
            background: #EFEFEF;
            padding: 0.2rem 0.55rem;
            border-radius: 4px;
            font-family: monospace;
        }}

        .verse-text {{
            font-family: var(--verse-font);
            font-weight: var(--verse-weight);
            font-size: var(--font-size);
            line-height: 2.1;
            letter-spacing: 0.005em;
            color: #111111;
            text-align: justify;
        }}

        .verse-p {{
            margin-bottom: 1rem;
            text-indent: 0;
        }}

        .verse-p:last-child {{
            margin-bottom: 0;
        }}

        @media (max-width: 850px) {{
            .layout {{
                grid-template-columns: 1fr;
            }}
            .toc-sidebar {{
                display: none;
            }}
            .main-content {{
                padding: 1.35rem;
            }}
            .main-title h1 {{
                font-size: 1.75rem;
            }}
        }}
    </style>
</head>
<body>
    <header class="header">
        <div class="header-content">
            <a href="#" class="logo" onclick="window.scrollTo({{top: 0, behavior: 'smooth'}}); return false;" title="Go to top of page">
                <span class="om-symbol">ॐ</span>
                <span>VedaVMS</span>
            </a>
            <div class="controls">
                <button class="toggle-sidebar-btn" onclick="toggleSidebar()" title="Toggle Contents Panel" id="sidebar-toggle-btn">☰ सूची</button>
                <a href="{back_link}" class="btn-ctrl">{back_label}</a>
                <button class="btn-ctrl" id="font-toggle-btn" onclick="toggleFont()" title="Toggle Sanskrit Font">Font: Noto Serif</button>
                <button class="btn-ctrl" onclick="adjustFont(-1)" title="Decrease Font Size (A-)">A-</button>
                <span id="font-size-val" onclick="resetFontSize()" style="font-size: 0.85rem; padding: 0.15rem 0.45rem; color: #FFF; font-family: monospace; font-weight: 600; min-width: 44px; text-align: center; display: inline-block; cursor: pointer; border-radius: 4px; background: rgba(255,255,255,0.14); transition: transform 0.15s ease;" title="Click to reset font size to 100%">100%</span>
                <button class="btn-ctrl" onclick="adjustFont(1)" title="Increase Font Size (A+)">A+</button>
                <button class="btn-ctrl" onclick="window.print()" title="Print / Save PDF">🖨️ Print</button>
                <button class="btn-ctrl" onclick="window.scrollTo({{top: 0, behavior: 'smooth'}})" title="Go to top of page">▲ Top</button>
            </div>
        </div>
    </header>

    <div class="layout">
        <!-- Sidebar Navigation -->
        <aside class="toc-sidebar">
            <div class="toc-title">सूची (Contents)</div>
            <ul class="toc-list">
''')

    for ch in chapters:
        ch_id = f"chapter-{ch['num']}"
        html_parts.append(f'''                <li class="toc-chapter" id="toc-{ch_id}">
                    <div class="toc-ch-header" onclick="toggleTocChapter('toc-{ch_id}')">
                        <div class="toc-ch-title"><a href="#{ch_id}">{ch['title_deva']}</a></div>
                        <span class="toc-ch-toggle">▼</span>
                    </div>
                    <ul class="toc-sub-list">
''')
        for sec in ch["sections"]:
            sec_id = f"sec-{sec['num'].replace('.', '-')}"
            title_disp = f"{sec['num']} {sec['title_deva']}".strip()
            html_parts.append(f'                        <li><a href="#{sec_id}">{title_disp}</a></li>\n')
        html_parts.append('''                    </ul>
                </li>
''')

    html_parts.append(f'''            </ul>
        </aside>

        <!-- Main Content -->
        <main class="main-content">
            <div class="main-title">
                <h1>{title}</h1>
                <div class="sub-heading">{subtitle}</div>
            </div>
''')

    for ch in chapters:
        ch_id = f"chapter-{ch['num']}"
        html_parts.append(f'''            <section class="chapter-container" id="{ch_id}">
                <h2 class="chapter-heading">{ch['title_deva']}</h2>
''')
        for sec in ch["sections"]:
            sec_id = f"sec-{sec['num'].replace('.', '-')}"
            title_disp_deva = f"{sec['num']} {sec['title_deva']}".strip()
            code_span = f'<span class="anuvaka-code">{sec["ta_code"]}</span>' if sec["ta_code"] else ''
            html_parts.append(f'''                <div class="anuvaka-block" id="{sec_id}">
                    <div class="anuvaka-header">
                        <span class="anuvaka-num">{title_disp_deva}</span>
                        {code_span}
                    </div>
                    <div class="verse-text">
''')
            for deva_line in sec["content_deva"]:
                html_parts.append(f'                        <p class="verse-p">{deva_line}</p>\n')
            html_parts.append('''                    </div>
                </div>
''')
        html_parts.append('''            </section>
''')

    html_parts.append(f'''        </main>
    </div>

    <script>
        const defaultSize = {default_font_size};
        let currentSize = defaultSize;

        function updateFontSizeDisplay() {{
            const pct = Math.round((currentSize / defaultSize) * 100);
            const valEl = document.getElementById('font-size-val');
            if (valEl) {{
                valEl.textContent = pct + '%';
                valEl.style.transform = 'scale(1.18)';
                setTimeout(() => {{ valEl.style.transform = 'scale(1)'; }}, 150);
            }}
        }}

        function applyFontSize() {{
            const mainEl = document.querySelector('.main-content');
            if (mainEl) mainEl.style.setProperty('--font-size', currentSize + 'rem');
            document.documentElement.style.setProperty('--font-size', currentSize + 'rem');
            updateFontSizeDisplay();
            localStorage.setItem('reader-font-size', currentSize);
        }}

        function adjustFont(delta) {{
            currentSize = Math.max(0.9, Math.min(2.4, +(currentSize + (delta * 0.15)).toFixed(2)));
            applyFontSize();
        }}

        function resetFontSize() {{
            currentSize = defaultSize;
            applyFontSize();
        }}

        const fontList = {fonts_js};
        let currentFontIndex = 0;
        function setFont(idx) {{
            currentFontIndex = ((idx % fontList.length) + fontList.length) % fontList.length;
            const chosen = fontList[currentFontIndex];
            document.documentElement.style.setProperty('--verse-font', chosen.font);
            document.documentElement.style.setProperty('--verse-weight', chosen.weight);
            const btn = document.getElementById('font-toggle-btn');
            if (btn) btn.innerText = 'Font: ' + chosen.label;
            localStorage.setItem('reader-font-idx', currentFontIndex);
        }}
        function toggleFont() {{
            setFont(currentFontIndex + 1);
        }}

        function toggleTocChapter(id) {{
            const el = document.getElementById(id);
            if (!el) return;
            el.classList.toggle('collapsed');
            const collapsed = el.classList.contains('collapsed');
            const state = JSON.parse(localStorage.getItem('toc-chapters') || '{{}}');
            state[id] = collapsed;
            localStorage.setItem('toc-chapters', JSON.stringify(state));
        }}

        function toggleSidebar() {{
            const layout = document.querySelector('.layout');
            const btn = document.getElementById('sidebar-toggle-btn');
            layout.classList.toggle('sidebar-collapsed');
            const collapsed = layout.classList.contains('sidebar-collapsed');
            localStorage.setItem('sidebar-collapsed', collapsed);
            btn.textContent = collapsed ? '☰' : '☰ सूची';
        }}

        /* Context-aware Suchi / Index Scroll Synchronization */
        let activeAnuvakaId = null;
        let isUserInteractingWithToc = false;

        function scrollSidebarToTarget(targetLink) {{
            const sidebar = document.querySelector('.toc-sidebar');
            if (!sidebar || isUserInteractingWithToc) return;
            const linkRect = targetLink.getBoundingClientRect();
            const sideRect = sidebar.getBoundingClientRect();
            const margin = Math.min(70, sideRect.height * 0.2);
            if (linkRect.top < sideRect.top + margin || linkRect.bottom > sideRect.bottom - margin) {{
                const currentScroll = sidebar.scrollTop;
                const offset = (linkRect.top - sideRect.top) - (sideRect.height / 2) + (linkRect.height / 2);
                sidebar.scrollTo({{
                    top: Math.max(0, currentScroll + offset),
                    behavior: 'smooth'
                }});
            }}
        }}

        function highlightAnuvakaInToc(anuvakaId) {{
            if (!anuvakaId || anuvakaId === activeAnuvakaId) return;
            activeAnuvakaId = anuvakaId;

            const targetLink = document.querySelector(`.toc-sub-list a[href="#${{anuvakaId}}"]`);
            if (!targetLink) return;

            document.querySelectorAll('.toc-sub-list a.active').forEach(el => el.classList.remove('active'));
            targetLink.classList.add('active');

            let wasCollapsed = false;
            const parentCh = targetLink.closest('.toc-chapter');
            if (parentCh && parentCh.classList.contains('collapsed')) {{
                parentCh.classList.remove('collapsed');
                wasCollapsed = true;
            }}

            if (wasCollapsed) {{
                setTimeout(() => scrollSidebarToTarget(targetLink), 150);
            }} else {{
                scrollSidebarToTarget(targetLink);
            }}
        }}

        document.addEventListener('DOMContentLoaded', function() {{
            // IntersectionObserver for tracking active Anuvaka during scroll
            const anuvakaObserver = new IntersectionObserver((entries) => {{
                let bestEntry = null;
                let minDistance = Infinity;

                entries.forEach(entry => {{
                    if (entry.isIntersecting) {{
                        const dist = Math.abs(entry.boundingClientRect.top - 85);
                        if (dist < minDistance) {{
                            minDistance = dist;
                            bestEntry = entry;
                        }}
                    }}
                }});

                if (bestEntry) {{
                    highlightAnuvakaInToc(bestEntry.target.id);
                }}
            }}, {{ rootMargin: '-75px 0px -75% 0px', threshold: 0 }});

            document.querySelectorAll('.anuvaka-block').forEach(el => anuvakaObserver.observe(el));

            // Direct click on Suchi item immediately highlights without waiting
            document.querySelectorAll('.toc-sub-list a').forEach(link => {{
                link.addEventListener('click', function() {{
                    const href = this.getAttribute('href');
                    if (href && href.startsWith('#')) {{
                        highlightAnuvakaInToc(href.slice(1));
                    }}
                }});
            }});

            const sidebar = document.querySelector('.toc-sidebar');
            if (sidebar) {{
                let tocTimeout;
                sidebar.addEventListener('wheel', () => {{
                    isUserInteractingWithToc = true;
                    clearTimeout(tocTimeout);
                    tocTimeout = setTimeout(() => {{ isUserInteractingWithToc = false; }}, 1500);
                }}, {{ passive: true }});
            }}

            // Restore saved states
            const collapsed = localStorage.getItem('sidebar-collapsed') === 'true';
            if (collapsed) {{
                document.querySelector('.layout').classList.add('sidebar-collapsed');
                const btn = document.getElementById('sidebar-toggle-btn');
                if (btn) btn.textContent = '☰';
            }}
            const tocState = JSON.parse(localStorage.getItem('toc-chapters') || '{{}}');
            for (const [id, isCollapsed] of Object.entries(tocState)) {{
                if (isCollapsed) {{
                    const el = document.getElementById(id);
                    if (el) el.classList.add('collapsed');
                }}
            }}
            const savedFont = localStorage.getItem('reader-font-idx');
            if (savedFont !== null) {{
                setFont(parseInt(savedFont, 10) || 0);
            }}
            const savedSize = localStorage.getItem('reader-font-size');
            if (savedSize !== null) {{
                currentSize = parseFloat(savedSize) || defaultSize;
                applyFontSize();
            }} else {{
                updateFontSizeDisplay();
            }}
        }});

        window.addEventListener('scroll', function() {{
            const btn = document.getElementById('back-to-top');
            if (btn) {{
                if (window.scrollY > 350) btn.classList.add('visible');
                else btn.classList.remove('visible');
            }}
        }});
    </script>
    <button id="back-to-top" class="back-to-top" onclick="window.scrollTo({{top: 0, behavior: 'smooth'}})" title="Go to top of page">▲</button>
</body>
</html>
''')

    return "".join(html_parts)


def ast_to_chapters(ast_data: dict) -> list[dict]:
    """Convert AST structure into chapters format for generate_reader_html."""
    supersections = ast_data.get('supersections', ast_data.get('supersection', {}))
    chapters = []
    for ss_key, ss_data in supersections.items():
        if ss_key == 'count':
            continue
        for sec_key, sec_data in ss_data.get('sections', {}).items():
            if sec_key == 'count':
                continue
            sec_title = sec_data.get('section_title', '')
            num_m = re.match(r'^(\d+)\.\s*(.*)', sec_title)
            ch_num = int(num_m.group(1)) if num_m else (len(chapters) + 1)

            sections = []
            for sub_key, sub_data in sec_data.get('subsections', {}).items():
                if sub_key == 'count':
                    continue
                header = sub_data.get('header', {}).get('header', '')
                h_m = re.match(r'^(\d+\.\d+(?:\.\d+)?)\s*(.*)', header)
                if h_m:
                    sub_num = h_m.group(1)
                    sub_title = h_m.group(2).strip()
                else:
                    sub_num = f"{ch_num}.{len(sections)+1}"
                    sub_title = header
                ta_code = sub_data.get('ta_code', '')
                content = sub_data.get('content_lines', [])
                sections.append({
                    'num': sub_num,
                    'title_deva': sub_title,
                    'ta_code': ta_code,
                    'content_deva': content
                })
            chapters.append({
                'num': ch_num,
                'title_deva': sec_title,
                'sections': sections
            })
    return chapters


def build_book(book_id: str, config: dict, input_override: str = None, output_override: str = None) -> Path:
    """Build reader HTML for a given book configuration."""
    books = config.get("books", {})
    if book_id not in books:
        raise ValueError(f"Book '{book_id}' not found in configuration. Available: {list(books.keys())}")

    book_meta = books[book_id]
    input_file = input_override or book_meta.get("input_docx")
    output_file = output_override or book_meta.get("output_html")
    chapter_regex = book_meta.get("chapter_regex", r"^([1-6])(?!\.)\s*(.*)$")
    fonts = config.get("fonts", [])
    default_size = config.get("default_font_size_rem", 1.35)

    print(f"\n--- Building '{book_id}' ---")
    print(f"Loading DOCX: {input_file}")
    raw_paras = extract_docx_paragraphs(input_file)
    print(f"Loaded {len(raw_paras)} paragraphs.")

    chapters = parse_chapters_and_sections(raw_paras, chapter_regex)
    print(f"Extracted {len(chapters)} chapters:")
    for ch in chapters:
        print(f"  Chapter {ch['num']}: {ch['title_deva']} ({len(ch['sections'])} sections)")

    html_content = generate_reader_html(book_meta, chapters, fonts, default_size)

    out_path = Path(output_file)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"Successfully generated {out_path} ({os.path.getsize(out_path):,} bytes)")
    return out_path


def main():
    parser = argparse.ArgumentParser(description="Generate VedaVMS Sanskrit Vedic Readers from Baraha DOCX.")
    parser.add_argument("--book", type=str, default="taittiriya_upanishad", help="Book identifier from config.json")
    parser.add_argument("--all", action="store_true", help="Build all books in config.json")
    parser.add_argument("--config", type=str, default=None, help="Path to config.json")
    parser.add_argument("--input", type=str, default=None, help="Override input DOCX path")
    parser.add_argument("--output", type=str, default=None, help="Override output HTML path")

    args = parser.parse_args()

    # Locate config file
    if args.config:
        config_path = Path(args.config)
    else:
        candidates = [
            Path(__file__).parent / "config.json",
            Path("src/config.json"),
            Path("vedavms_html/config.json"),
        ]
        config_path = next((p for p in candidates if p.exists()), Path("src/config.json"))

    if not config_path.exists():
        print(f"Error: Configuration file not found at {config_path}", file=sys.stderr)
        sys.exit(1)

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    if args.all:
        for b_id in config.get("books", {}):
            build_book(b_id, config)
    else:
        build_book(args.book, config, args.input, args.output)


if __name__ == "__main__":
    main()
