"""Generate comprehensive Publication Blog in Markdown (.md) and Standalone HTML (.html)
for the Jaimineeya Samaveda Malayalam Digitization Project.
(Palm-Leaf Heritage Edition)
"""

import base64
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FONT_PATH = ROOT / "fonts" / "JaimineeyaSwara.ttf"
OUT_MD = ROOT / "docs" / "blog" / "Malayalam_JSV_Publication_Blog.md"
OUT_HTML = ROOT / "docs" / "blog" / "Malayalam_JSV_Publication_Blog.html"
ARTIFACT_DIR = Path(r"C:\Users\sekha\.gemini\antigravity-ide\brain\33a78242-ade0-47ff-b909-95b423204936")

# 1. Base64 font encoding
b64_font = ""
if FONT_PATH.exists():
    with open(FONT_PATH, "rb") as f:
        b64_font = base64.b64encode(f.read()).decode("ascii")

# 2. Read existing Markdown content
if OUT_MD.exists():
    md_content = OUT_MD.read_text(encoding="utf-8")
else:
    md_content = ""

# 3. HTML Template with Palm-Leaf Heritage Aesthetic
html_template = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Revitalizing the Jaimineeya Samaveda in Malayalam Script | Publication Blog</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Noto+Serif+Malayalam:wght@400;500;600;700&family=Fira+Code:wght@400;500;600&display=swap" rel="stylesheet">
<style>
    @font-face {
        font-family: 'JaimineeyaSwara';
        src: url('data:font/truetype;charset=utf-8;base64,__BASE64_FONT__') format('truetype');
    }

    :root {
        --bg-page: #fbf7ee;
        --bg-card: #fffdf9;
        --text-primary: #2d2419;
        --text-secondary: #5c4b37;
        --text-muted: #8c7355;
        --brand-blue: #78350f;
        --sky-blue: #0284c7;
        --brand-accent: #b45309;
        --swara-red: #c62828;
        --border-subtle: #e7dfd0;
        --border-card: #dfd4be;
        --shadow-elevation: 0 10px 25px -5px rgba(69, 26, 3, 0.06), 0 8px 10px -6px rgba(69, 26, 3, 0.03);
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }

    body {
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
        background-color: var(--bg-page);
        color: var(--text-primary);
        line-height: 1.75;
        font-size: 17px;
    }

    /* Hero Banner - Palm Leaf Warm Wood Gradient */
    .hero-banner {
        background: linear-gradient(135deg, #3b1403 0%, #692c0c 50%, #8c3b10 100%);
        color: white;
        padding: 75px 20px 85px;
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    .hero-banner::after {
        content: '';
        position: absolute;
        bottom: 0; left: 0; right: 0;
        height: 40px;
        background: var(--bg-page);
        clip-path: polygon(0 100%, 100% 100%, 100% 0, 0 100%);
    }
    .hero-content {
        max-width: 900px;
        margin: 0 auto;
    }
    h1 {
        font-size: clamp(30px, 4.5vw, 44px);
        font-weight: 800;
        line-height: 1.25;
        letter-spacing: -0.02em;
        margin-bottom: 18px;
        text-shadow: 0 2px 10px rgba(0,0,0,0.35);
    }
    .hero-subtitle {
        font-size: clamp(17px, 2vw, 20px);
        color: #fde68a;
        max-width: 780px;
        margin: 0 auto 25px;
        font-weight: 400;
        line-height: 1.55;
    }
    .meta-bar {
        display: flex;
        justify-content: center;
        gap: 22px;
        color: #fed7aa;
        font-size: 14px;
        font-weight: 500;
        flex-wrap: wrap;
    }

    /* Main Article Container */
    .article-container {
        max-width: 960px;
        margin: -30px auto 0;
        background: var(--bg-card);
        border-radius: 16px;
        box-shadow: var(--shadow-elevation);
        padding: 50px 60px;
        border: 1px solid var(--border-subtle);
    }

    h2 {
        font-size: 26px;
        font-weight: 800;
        color: var(--brand-blue);
        margin: 45px 0 18px;
        padding-bottom: 10px;
        border-bottom: 2px solid var(--border-card);
    }
    h3 {
        font-size: 20px;
        font-weight: 700;
        color: #451a03;
        margin: 28px 0 12px;
    }
    p {
        margin-bottom: 20px;
        color: var(--text-secondary);
    }

    .callout {
        background: #fdf8ed;
        border-left: 4px solid var(--brand-accent);
        padding: 22px 26px;
        border-radius: 0 12px 12px 0;
        margin: 28px 0;
        border-top: 1px solid #f4ecda;
        border-right: 1px solid #f4ecda;
        border-bottom: 1px solid #f4ecda;
    }
    .callout-title {
        font-weight: 700;
        color: var(--brand-blue);
        font-size: 17px;
        margin-bottom: 8px;
    }

    ul, ol {
        margin-bottom: 22px;
        padding-left: 26px;
        color: var(--text-secondary);
    }
    li {
        margin-bottom: 8px;
    }

    /* Live Interactive Sandbox Playground */
    .interactive-playground {
        background: #f5eedc;
        border: 2px solid var(--border-card);
        border-radius: 16px;
        padding: 30px;
        margin: 35px 0;
        box-shadow: inset 0 2px 4px rgba(69, 26, 3, 0.03);
    }
    .playground-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
        flex-wrap: wrap;
        gap: 12px;
    }
    .playground-title {
        font-size: 18px;
        font-weight: 800;
        color: var(--brand-blue);
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .sample-buttons {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
    }
    .sample-chip {
        background: #fffdfa;
        border: 1px solid #d8cbaf;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 600;
        color: #5c4b37;
        cursor: pointer;
        transition: all 0.15s ease;
    }
    .sample-chip:hover {
        background: var(--brand-blue);
        color: white;
        border-color: var(--brand-blue);
    }
    .input-box-wrapper {
        margin-bottom: 20px;
    }
    .mantra-input {
        width: 100%;
        padding: 14px 18px;
        border-radius: 10px;
        border: 2px solid #c9bba2;
        font-family: 'Fira Code', 'Noto Serif Malayalam', monospace;
        font-size: 16px;
        color: #2d2419;
        background: #fffdfa;
        transition: border-color 0.2s ease;
        outline: none;
    }
    .mantra-input:focus {
        border-color: var(--brand-accent);
        box-shadow: 0 0 0 3px rgba(180, 83, 9, 0.15);
    }
    .render-output-stage {
        background: #fffdf9;
        border: 1px solid #e5dac4;
        border-radius: 12px;
        padding: 30px 20px;
        min-height: 120px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 6px -1px rgba(69, 26, 3, 0.04);
    }

    /* Live Mantra Flexbox Display */
    .mantra-display {
        display: inline-flex;
        flex-wrap: wrap;
        align-items: flex-end;
        background: #fffdf9;
        padding: 14px 24px;
        border-radius: 10px;
    }
    .mantra-word {
        display: inline-flex;
        flex-direction: column;
        align-items: center;
        justify-content: flex-end;
        vertical-align: bottom;
        position: relative;
        font-size: 1.75rem;
    }
    .swara-text {
        font-family: 'JaimineeyaSwara', serif;
        font-size: 1.10rem;
        color: var(--swara-red);
        line-height: 1;
        margin-bottom: 4px;
        font-weight: bold;
        min-height: 1.1em;
        user-select: none;
        text-align: center;
    }
    .mantra-text {
        font-family: 'Noto Serif Malayalam', serif;
        font-size: 1.75rem;
        font-weight: 500;
        line-height: 1.1;
        color: var(--text-primary);
        position: relative;
    }
    .mantra-danda-block {
        margin: 0 0.25em;
    }
    .mantra-danda {
        color: var(--sky-blue);
        font-weight: bold;
    }
    .word-space {
        width: 0.45em;
        display: inline-block;
    }
    .swara-mod {
        color: var(--sky-blue);
        font-family: 'JaimineeyaSwara', serif;
        font-weight: bold;
    }
    .swara-mod.mod-a {
        position: absolute;
        top: -0.28em;
        left: 100%;
        transform: translateX(-40%);
        font-size: 1.20rem;
        pointer-events: none;
    }
    .swara-mod.mod-a1 {
        position: absolute;
        top: -0.28em;
        left: 100%;
        transform: translateX(-40%);
        font-size: 1.40rem;
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
        color: var(--sky-blue);
        font-size: 1.20rem;
        line-height: 1;
    }
    .swara-mod.mod-b .swara-on-caret {
        position: absolute;
        top: -1.15em;
        left: 50%;
        transform: translateX(-50%);
        color: var(--swara-red);
        font-size: 1.05rem;
        font-weight: bold;
        font-family: 'JaimineeyaSwara', serif;
        line-height: 1;
        white-space: nowrap;
    }
    .swara-mod.mod-c {
        position: absolute;
        top: -0.15em;
        right: -0.35em;
        font-size: 1.10rem;
    }
    .swara-mod.mod-d {
        position: absolute;
        top: -0.30em;
        left: 100%;
        transform: translateX(-40%);
        font-size: 1.20rem;
        pointer-events: none;
    }
    .swara-mod.mod-e {
        position: relative;
        margin-left: 0.15em;
        font-size: 1.35rem;
        vertical-align: -0.05em;
    }
    .swara-mod.mod-f {
        position: relative;
        margin-left: 0.15em;
        font-size: 1.35rem;
        vertical-align: -0.05em;
    }
    .swara-mod.mod-g {
        position: absolute;
        bottom: -0.30em;
        left: 50%;
        transform: translateX(-50%);
        font-size: 1.35rem;
    }
    .swara-mod.mod-h {
        position: absolute;
        top: -0.35em;
        left: 50%;
        transform: translateX(-50%);
        font-size: 1.20rem;
    }
    .swara-mod.mod-dot {
        position: relative;
        margin-left: 0.15em;
        font-size: 1.10rem;
        vertical-align: baseline;
    }
    .swara-mod.mod-underbar {
        position: relative;
        margin-left: 0.10em;
        font-size: 1.25rem;
        vertical-align: -0.15em;
    }
    .swara-mod.mod-comma {
        position: relative;
        margin-left: 0.10em;
        font-size: 1.20rem;
        vertical-align: baseline;
    }
    .mantra-punct {
        font-family: 'Noto Serif Malayalam', serif;
        font-size: 1.75rem;
        line-height: 1.1;
        color: var(--sky-blue);
        margin-right: 0.05em;
    }

    /* Tables */
    table {
        width: 100%;
        border-collapse: collapse;
        margin: 25px 0;
        font-size: 15px;
    }
    th {
        background: #f4ecda;
        color: #451a03;
        font-weight: 700;
        text-align: left;
        padding: 12px 16px;
        border-bottom: 2px solid #dfd4be;
    }
    td {
        padding: 12px 16px;
        border-bottom: 1px solid #efe6d5;
        vertical-align: middle;
    }
    tr:hover td {
        background: #fdf8ed;
    }
    .glyph-sample {
        font-family: 'JaimineeyaSwara', serif;
        font-size: 28px;
        color: var(--sky-blue);
        font-weight: bold;
    }
    .badge-above { background: #fef3c7; color: #78350f; padding: 4px 8px; border-radius: 4px; font-weight: 700; font-size: 11px; text-transform: uppercase; border: 1px solid #fde68a; }
    .badge-below { background: #ffedd5; color: #9a3412; padding: 4px 8px; border-radius: 4px; font-weight: 700; font-size: 11px; text-transform: uppercase; border: 1px solid #fed7aa; }
    .badge-shoulder { background: #fae8ff; color: #701a75; padding: 4px 8px; border-radius: 4px; font-weight: 700; font-size: 11px; text-transform: uppercase; border: 1px solid #f5d0fe; }
    .badge-inline { background: #f5eedc; color: #5c4b37; padding: 4px 8px; border-radius: 4px; font-weight: 700; font-size: 11px; text-transform: uppercase; border: 1px solid #e5dac4; }

    /* Workflow Stepper */
    .step-grid {
        display: grid;
        grid-template-columns: 1fr 1fr 1fr;
        gap: 18px;
        margin: 28px 0;
    }
    .step-card {
        background: #fbf7ee;
        border: 1px solid var(--border-subtle);
        border-radius: 12px;
        padding: 22px 18px;
        text-align: center;
    }
    .step-num {
        width: 34px;
        height: 34px;
        background: var(--brand-blue);
        color: white;
        font-weight: 800;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 12px;
    }
    .step-title {
        font-size: 16px;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 6px;
    }
    .step-desc {
        font-size: 13px;
        color: var(--text-muted);
        line-height: 1.45;
    }

    footer {
        margin-top: 50px;
        padding-top: 30px;
        border-top: 1px solid var(--border-subtle);
        text-align: center;
        font-size: 14px;
        color: var(--text-muted);
    }
    .ornament {
        color: #ea580c;
        font-weight: 700;
        font-size: 1.15em;
        margin: 0 8px;
        display: inline-block;
        vertical-align: middle;
    }
    a { color: #9a3412; text-decoration: none; font-weight: 600; }
    a:hover { text-decoration: underline; color: #7c2d12; }
</style>
</head>
<body>

<div class="hero-banner">
    <div class="hero-content">
        <h1>Revitalizing Jaimineeya Samaveda in Malayalam Script</h1>
        <div class="hero-subtitle">
            Typographic Innovation, Custom Grantha Font Engineering, and a Unified Multi-Format Publishing Pipeline for Jaimineeya Samavedam
        </div>
        <div class="meta-bar">
            <span>📅 August 2026</span>
            <span>🏛️ Jaimineeya Samaveda Digitization Project</span>
            <span>📜 Open Access</span>
        </div>
    </div>
</div>

<article class="article-container">

    <div class="callout">
        <div class="callout-title">The Sacred Jaimineeya Shakha Heritage & The Kodunthirapully Paddhati</div>
        The <em>Jaiminīya Sāmaveda</em> represents one of the oldest and most musically intricate traditions of Vedic chanting. Preserved by the lineages of <strong>Tamil Nadu and the Namboodiri tradition of Kerala</strong>, this shakha was saved from the brink of extinction through the divine vision of Kanchi Mahaperiyava and the lifelong dedication of <strong>Brahmasri Makarabhushanam Iyengar (Guruji)</strong>, who founded the Thogur Jaimineeya Samaveda Patashala nearly fifty years ago.
    </div>

    <h2>1. Executive Summary & The Sacred Heritage</h2>
    <p>
        The Jaimineeya Samaveda employs a sophisticated system of Yugma and Ayugma swaras (<em>Dharalakshanam of Sabhapati</em>) for phonetic encoding of its Samagana. 
    </p>
    <p>
        Following a migration of Jaimini Samavedins from the Kaveri delta (Anbil, Tiruchi) to Kerala around 250–300 years ago, a prominent community settled in <strong>Kodunthirapully Agraharam in Palakkad</strong>. In this tradition, <strong>Brahmasri Sahasranama Iyer</strong> meticulously hand-wrote the Samhita and Aranyam portions using a unique and effective scheme: Malayalam mantraksharas, Grantha and mixed Grantha-Malayalam swara markers, and a set of graphical swara modifier mnemonics to facilitate fluent recitation. Even today, young and old scholars in Kodunthirapully chant from paper copies of these revered manuscripts.
    </p>
    <p>
        As part of our overall digitization efforts of Jaimineeya Samaveda, we have now implemented the digital <strong>"Kodunthirapully Paddhati"</strong>. We believe this effort will support the living tradition of Sama Veda chanting in the Agraharam in today's digital world. To overcome the technical challenges of mixed Grantha/Malayalam typography and complex visual mnemonics, we engineered the <strong>JaimineeyaSwara</strong> font and built an automated multi-format publishing pipeline delivering:
    </p>
    
        📄 <strong>Publication quality Jaimineeya Samaveda in Malayalam (PDF):</strong> With sub-point kerning, authentic manuscript ligatures, and vector-perfect typography.<br>
        🌐 <strong>Interactive Web Edition (HTML5):</strong> An easy to navigate Website with advanced search and hyperlink features.<br>
        📝 <strong>Universal Unicode Plaintext (.txt):</strong> With standard Grantha codepoints and intuitive modifier mnemonics to enable ongoing curation and scholarship.<br>
    

    <h2>2. The Typographic Challenge</h2>
    <p>
        Rendering authentic Malayalam Jaimineeya Samaveda requires solving three distinct challenges:
    </p>
    <ul>
        <li><strong>Subscript Svara Markers:</strong> 19 distinct pitch markers written in archaic Grantha script layered directly over Malayalam syllables.</li>
        <li><strong>Manuscript Overrides:</strong> Kerala manuscripts use a unique hybrid <em>Pla</em> base (combining Grantha Pa with Malayalam subscript La) and a Malayalam <em>Sha</em> base with detached Grantha vowel arms.</li>
        <li><strong>Multi-Syllable Spanning Modifiers:</strong> Tonal arches and roof chevrons that visually span across the inter-word space between adjacent syllables.</li>
    </ul>

    <!-- INTERACTIVE MANTRA PLAYGROUND -->
    <h2>3. Live Interactive Mantra Sandbox</h2>
    <p>
        Test the live stacking engine in real-time. Type or click any sample below to see how our custom font and dynamic anchoring render your text:
    </p>

    <div class="interactive-playground">
        <div class="playground-header">
            <div class="playground-title">
                <span>⚡ Live Stacking & Modifier Engine</span>
            </div>
            <div class="sample-buttons">
                <button class="sample-chip" onclick="loadSample('ഹോ(𑌖)(A) ബാ(𑌪𑍍𑌲) മാ(𑌕)(B) യാ')">Sample 1: Arc + Caret</button>
                <button class="sample-chip" onclick="loadSample('തൊ(𑌤)(A1) । ഹാ(𑌟𑌾) ഇ')">Sample 1b: Arc over Danda (MOD-A1)</button>
                <button class="sample-chip" onclick="loadSample('ഓ(𑌤)(C) ഗ്നാ(𑌤) ബാ(𑌪𑍍𑌲)(G)')">Sample 2: Dot + Slash</button>
                <button class="sample-chip" onclick="loadSample('ഹോ(𑌪𑍍𑌲)(D) ഇഴാ(𑌶𑌾) ദാ(𑌚𑌿)(H)')">Sample 3: Chevron + Swarita</button>
                <button class="sample-chip" onclick="loadSample('വാ(𑌚)(E) ഇ(𑌚)(F)')">Sample 4: Phrasing Dandas</button>
                <button class="sample-chip" onclick="loadSample('വാ(𑌚). ഇ(𑌚)_ ദാ(𑌚),')">Sample 5: Inline Marks ( . _ , )</button>
            </div>
        </div>

        <div class="input-box-wrapper">
            <input type="text" id="mantraInput" class="mantra-input" value="ഹോ(𑌖)(A) ബാ(𑌪𑍍𑌲) മാ(𑌕)(B) യാ ഓ(𑌤)(C) ഗ്നാ(𑌤) ബാ(𑌪𑍍𑌲)(G) ദാ(𑌚𑌿)(H) വാ(𑌚). ഇ(𑌚)_ ദാ(𑌚)," oninput="renderPlayground()" placeholder="Type mantra text with (Swara), (A..H), (.), (_), (,)..." />
        </div>

        <div class="render-output-stage" id="playgroundOutput">
            <!-- Dynamic Live Render Target -->
        </div>
    </div>

    <h2>4. The Canonical 8 Vedic Swara Modifiers & Inline Marks</h2>
    <table>
        <thead>
            <tr>
                <th>ID / Mark</th>
                <th>Shortcut</th>
                <th>Modifier Name</th>
                <th style="text-align:center;">Glyph</th>
                <th>Codepoints</th>
                <th>Position</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><strong>MOD-A</strong></td>
                <td><code>(A) / (⁀)</code></td>
                <td>Syllable Spanning Arc (Smooth Flat)</td>
                <td style="text-align:center;" class="glyph-sample">&#xE004;</td>
                <td><code>U+E004 / U+2040</code></td>
                <td><span class="badge-above">Above (2 Syllables)</span></td>
            </tr>
            <tr>
                <td><strong>MOD-A1</strong></td>
                <td><code>(A1) / (A_1)</code></td>
                <td>Syllable Spanning Arc over Danda</td>
                <td style="text-align:center;" class="glyph-sample">&#xE00D;</td>
                <td><code>U+E00D / (A1)</code></td>
                <td><span class="badge-above">Above (2 Syllables + Danda)</span></td>
            </tr>
            <tr>
                <td><strong>MOD-B</strong></td>
                <td><code>(B) / (∧)</code></td>
                <td>Peak Elevation Caret</td>
                <td style="text-align:center;" class="glyph-sample">&#xE005;</td>
                <td><code>U+E005 / U+2227</code></td>
                <td><span class="badge-above">Above (2 Syllables)</span></td>
            </tr>
            <tr>
                <td><strong>MOD-C</strong></td>
                <td><code>(C) / (·)</code></td>
                <td>Shoulder Pause Dot</td>
                <td style="text-align:center;" class="glyph-sample">&#xE001;</td>
                <td><code>U+E001 / U+00B7</code></td>
                <td><span class="badge-shoulder">Shoulder</span></td>
            </tr>
            <tr>
                <td><strong>MOD-D</strong></td>
                <td><code>(D) / (Ʌ)</code></td>
                <td>Chevron Roof</td>
                <td style="text-align:center;" class="glyph-sample">&#xE006;</td>
                <td><code>U+E006 / U+0245</code></td>
                <td><span class="badge-above">Above (2 Syllables)</span></td>
            </tr>
            <tr>
                <td><strong>MOD-E</strong></td>
                <td><code>(E) / (┃)</code></td>
                <td>Phrasing Heavy Danda</td>
                <td style="text-align:center;" class="glyph-sample">&#xE002;</td>
                <td><code>U+E002 / U+2503</code></td>
                <td><span class="badge-inline">Inline</span></td>
            </tr>
            <tr>
                <td><strong>MOD-F</strong></td>
                <td><code>(F) / (╷)</code></td>
                <td>Light Vertical Line</td>
                <td style="text-align:center;" class="glyph-sample">&#x2577;</td>
                <td><code>U+E002 / U+2577</code></td>
                <td><span class="badge-inline">Inline</span></td>
            </tr>
            <tr>
                <td><strong>MOD-G</strong></td>
                <td><code>(G) / (\\)</code></td>
                <td>Descending Tone Slash</td>
                <td style="text-align:center;" class="glyph-sample">&#xE003;</td>
                <td><code>U+E003 / U+005C</code></td>
                <td><span class="badge-below">Center Bottom</span></td>
            </tr>
            <tr>
                <td><strong>MOD-H</strong></td>
                <td><code>(H) / (|)</code></td>
                <td>Overhead Swarita</td>
                <td style="text-align:center;" class="glyph-sample">&#xE00C;</td>
                <td><code>U+E00C / U+007C</code></td>
                <td><span class="badge-above">Above Consonant</span></td>
            </tr>
            <tr>
                <td><strong>Dot (<code>.</code>)</strong></td>
                <td><code>. / (.)</code></td>
                <td>Pause Dot</td>
                <td style="text-align:center;" class="glyph-sample">&#xE001;</td>
                <td><code>U+E001 / U+002E</code></td>
                <td><span class="badge-inline">Inline</span></td>
            </tr>
            <tr>
                <td><strong>Underbar (<code>_</code>)</strong></td>
                <td><code>_ / (_)</code></td>
                <td>Elongation / Low Line</td>
                <td style="text-align:center;" class="glyph-sample">&#xE007;</td>
                <td><code>U+E007 / U+005F</code></td>
                <td><span class="badge-inline">Inline</span></td>
            </tr>
            <tr>
                <td><strong>Comma (<code>,</code>)</strong></td>
                <td><code>, / (,)</code></td>
                <td>Low Comma</td>
                <td style="text-align:center;" class="glyph-sample">&#xE00A;</td>
                <td><code>U+E00A / U+002C</code></td>
                <td><span class="badge-inline">Inline</span></td>
            </tr>
        </tbody>
    </table>

    <h2>5. The 3-Step Scholar Proofreading Workflow</h2>
    <div class="step-grid">
        <div class="step-card">
            <div class="step-num">1</div>
            <div class="step-title">Unicode Export</div>
            <div class="step-desc">Export pristine Unicode plaintext with Grantha swaras and English numerals.</div>
        </div>
        <div class="step-card">
            <div class="step-num">2</div>
            <div class="step-title">Hand Annotation</div>
            <div class="step-desc">Scholars enter intuitive modifier tags <code>(A)</code>–<code>(H)</code> and inline marks in any text editor.</div>
        </div>
        <div class="step-card">
            <div class="step-num">3</div>
            <div class="step-title">Multi-Format Build</div>
            <div class="step-desc">One command compiles to Web HTML and archival LuaLaTeX PDF.</div>
        </div>
    </div>

    <h2>6. Project Resources</h2>
    <p>
        Explore the repository, test the tools, and contribute to the digitization of the sacred Jaimineeya heritage:
    </p>
    <ul>
        <li>💻 <strong>GitHub Repository:</strong> <a href="https://github.com/sekharnarayanaswamy-del/jaimineeyasamavedam" target="_blank">github.com/sekharnarayanaswamy-del/jaimineeyasamavedam</a></li>
        <li>📄 <strong>Digital publishing of Jaimineeya Samaveda in Malayalam (PDF):</strong> <a href="https://github.com/sekharnarayanaswamy-del/jaimineeyasamavedam/blob/format-mantras/data/output/pdf/Malayalam/Samam_Malayalam.pdf" target="_blank"><code>Samhita_Malayalam</code></a></li>
        <li>🔤 <strong>Custom Font:</strong> <a href="https://github.com/sekharnarayanaswamy-del/jaimineeyasamavedam/blob/format-mantras/fonts/JaimineeyaSwara.ttf" target="_blank"><code>fonts/JaimineeyaSwara.ttf</code></a></li>
        <li>📖 <strong>Specification & Developer Guide:</strong> <a href="https://github.com/sekharnarayanaswamy-del/jaimineeyasamavedam/blob/format-mantras/Malayalam_JSV/spec.md" target="_blank"><code>Malayalam_JSV/spec.md</code></a></li>
        <li>🎨 <strong>Interactive Glyph Table:</strong> <a href="https://github.com/sekharnarayanaswamy-del/jaimineeyasamavedam/blob/format-mantras/data/output/malayalam/glyph_table.html" target="_blank"><code>Glyph_table</code></a></li>
        <li>🌐 <strong>Malayalam Digital Static Website:</strong> <em>(Work in progress)</em></li>
    </ul>

    <footer>
        <span class="ornament">ॐ</span> Jaimineeya Samaveda Digitization Project &bull; Preserving Vedic Heritage Through Open Typographic Engineering <span class="ornament">ॐ</span>
    </footer>

</article>

<script>
function loadSample(text) {
    document.getElementById('mantraInput').value = text;
    renderPlayground();
}

function renderPlayground() {
    const raw = document.getElementById('mantraInput').value;
    const container = document.getElementById('playgroundOutput');
    
    // Syllable-level akshara segmentation to align each swara precisely over its target syllable
    const tokenRegex = /(?:[।॥]+[0-9०-९IVXLCDMivxlcdm]*[।॥]*|(?:\u0D6A|[\\u0D05-\\u0D14]|(?:[\\u0D15-\\u0D3A\\u0D7A-\\u0D7F](?:\\u0D4D[\\u0D15-\\u0D3A])*))(?:[\\u0D3E-\\u0D4C\\u0D57\\u0D62\\u0D63\\u0D01-\\u0D03\\u0D3B\\u0D3C\\u0D4D]|_|,|\\.)*(?:\\([^)]+\\)|[.,_])*|[^\\s()।॥]+(?:\\([^)]+\\)|[.,_])*|\\s+)/g;
    const tokens = raw.match(tokenRegex) || [];
    let html = '<div class="mantra-display">';

    const modMap = {
        'A': { cls: 'mod-a', glyph: '&#xE004;' },
        'a': { cls: 'mod-a', glyph: '&#xE004;' },
        '⁀': { cls: 'mod-a', glyph: '&#xE004;' },
        'A1': { cls: 'mod-a1', glyph: '&#xE00D;' },
        'a1': { cls: 'mod-a1', glyph: '&#xE00D;' },
        'A_1': { cls: 'mod-a1', glyph: '&#xE00D;' },
        'a_1': { cls: 'mod-a1', glyph: '&#xE00D;' },
        'B': { cls: 'mod-b', glyph: '&#xE005;' },
        'b': { cls: 'mod-b', glyph: '&#xE005;' },
        '∧': { cls: 'mod-b', glyph: '&#xE005;' },
        '^': { cls: 'mod-b', glyph: '&#xE005;' },
        'C': { cls: 'mod-c', glyph: '&#xE001;' },
        'c': { cls: 'mod-c', glyph: '&#xE001;' },
        '·': { cls: 'mod-c', glyph: '&#xE001;' },
        'D': { cls: 'mod-d', glyph: '&#xE006;' },
        'd': { cls: 'mod-d', glyph: '&#xE006;' },
        'Ʌ': { cls: 'mod-d', glyph: '&#xE006;' },
        'E': { cls: 'mod-e', glyph: '&#xE002;' },
        'e': { cls: 'mod-e', glyph: '&#xE002;' },
        '┃': { cls: 'mod-e', glyph: '&#xE002;' },
        'F': { cls: 'mod-f', glyph: '&#x2577;' },
        'f': { cls: 'mod-f', glyph: '&#x2577;' },
        '╷': { cls: 'mod-f', glyph: '&#x2577;' },
        'G': { cls: 'mod-g', glyph: '&#xE003;' },
        'g': { cls: 'mod-g', glyph: '&#xE003;' },
        '\\\\': { cls: 'mod-g', glyph: '&#xE003;' },
        'H': { cls: 'mod-h', glyph: '&#xE00C;' },
        'h': { cls: 'mod-h', glyph: '&#xE00C;' },
        '|': { cls: 'mod-h', glyph: '&#xE00C;' },
        '.': { cls: 'mod-dot', glyph: '&#xE001;' },
        '_': { cls: 'mod-underbar', glyph: '&#xE007;' },
        ',': { cls: 'mod-comma', glyph: '&#xE00A;' },
    };

    const swaraSubs = {
        '𑌪𑍍𑌲': '&#xE020;',
        'Pla': '&#xE020;',
        'പ്ല': '&#xE020;',
        '𑌪𑍍𑌲𑌾': '&#xE021;',
        'Plaa': '&#xE021;',
        'പ്ലാ': '&#xE021;',
        '𑌪𑍍𑌲𑌿': '&#xE022;',
        'Pli': '&#xE022;',
        'പ്ലി': '&#xE022;',
        '𑌪𑍍𑌲𑍀': '&#xE023;',
        'Plii': '&#xE023;',
        'പ്ലീ': '&#xE023;',
        'ശ𑌾': '&#xE010;',
        'ശാ': '&#xE010;',
        'Shaa': '&#xE010;',
        'ശ𑌿': '&#xE011;',
        'ശി': '&#xE011;',
        'Shi': '&#xE011;',
        'ശ𑍀': '&#xE012;',
        'ശീ': '&#xE012;',
        'Shii': '&#xE012;',
        'ശ്': '&#xE013;',
        'ശ𑍍': '&#xE013;',
        'Sh': '&#xE013;',
        'ശ്രൂ': '&#xE027;',
        'ശ്ര𑍂': '&#xE027;',
        'Shruu': '&#xE027;',
        'ശൄ': '&#xE028;',
        'ശ്രൄ': '&#xE028;',
        'Shrr': '&#xE028;',
        'ണു': '&#xE029;',
        'ണ𑍁': '&#xE029;',
        'Nnu': '&#xE029;',
        'ത്ര': '&#xE01D;',
        'Tra': '&#xE01D;',
        'ക്ര': '&#xE01E;',
        'Kra': '&#xE01E;',
    };

    for (let i = 0; i < tokens.length; i++) {
        let t = tokens[i];
        
        // Handle whitespace: retain explicit spaces entered by user
        if (/^\\s+$/.test(t)) {
            html += '<span class="word-space">&nbsp;</span>';
            continue;
        }

        // If it's a danda / verse number
        if (/^[।॥0-9०-९IVXLCDMivxlcdm\\s]+$/.test(t)) {
            html += `<span class="mantra-word mantra-danda-block"><span class="swara-text">&nbsp;</span><span class="mantra-text mantra-danda">${t}</span></span>`;
            continue;
        }

        let swara = '';
        let mod = '';
        let base = t;

        // Check for trailing punctuation marks
        if (base.endsWith('.') && !base.includes('(')) {
            mod = modMap['.'];
            base = base.slice(0, -1);
        } else if (base.endsWith('_') && !base.includes('(')) {
            mod = modMap['_'];
            base = base.slice(0, -1);
        } else if (base.endsWith(',') && !base.includes('(')) {
            mod = modMap[','];
            base = base.slice(0, -1);
        }

        // Check for swara and modifier in parenthetical groups
        const swMatch = base.match(/\\(([^)]+)\\)/g);
        if (swMatch) {
            for (let m of swMatch) {
                const inner = m.replace(/[()]/g, '');
                if (modMap[inner]) {
                    mod = modMap[inner];
                } else {
                    swara = swaraSubs[inner] || inner;
                }
                base = base.replace(m, '');
            }
        }

        // Check again for trailing punctuation
        if (base.endsWith('.')) {
            if (!mod) mod = modMap['.'];
            base = base.slice(0, -1);
        } else if (base.endsWith('_')) {
            if (!mod) mod = modMap['_'];
            base = base.slice(0, -1);
        } else if (base.endsWith(',')) {
            if (!mod) mod = modMap[','];
            base = base.slice(0, -1);
        }

        // Normalize pre-consonantal R to Repha
        base = base.replace(/ർ/g, '൪').replace(/ര്/g, '൪');

        let modHtml = '';
        if (mod) {
            if (mod.cls === 'mod-b') {
                modHtml = `<span class="swara-mod mod-b"><span class="caret-glyph">&#xE005;</span><span class="swara-on-caret">${swara || '&nbsp;'}</span></span>`;
                swara = '';
            } else {
                modHtml = `<span class="swara-mod ${mod.cls}">${mod.glyph}</span>`;
            }
        }

        html += `
        <span class="mantra-word">
            <span class="swara-text">${swara || '&nbsp;'}</span>
            <span class="mantra-text">${base}${modHtml}</span>
        </span>
        `;
    }

    html += '</div>';
    container.innerHTML = html;
}

// Initial render
window.onload = renderPlayground;
</script>
</body>
</html>
"""

html_content = html_template.replace("__BASE64_FONT__", b64_font)

# Write outputs
OUT_MD.parent.mkdir(parents=True, exist_ok=True)
OUT_MD.write_text(md_content, encoding="utf-8")
print(f"Preserved Markdown Blog: {OUT_MD}")

OUT_HTML.write_text(html_content, encoding="utf-8")
print(f"Generated Palm-Leaf HTML Blog: {OUT_HTML}")

# Copy to artifacts directory
try:
    if ARTIFACT_DIR.exists():
        art_md = ARTIFACT_DIR / "Malayalam_JSV_Publication_Blog.md"
        art_html = ARTIFACT_DIR / "Malayalam_JSV_Publication_Blog.html"
        shutil.copy(OUT_MD, art_md)
        shutil.copy(OUT_HTML, art_html)
        print(f"Copied to artifacts: {art_md}, {art_html}")
except Exception as e:
    print(f"Artifact copy notice: {e}")
