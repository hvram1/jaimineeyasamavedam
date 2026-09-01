import mammoth
import os
import sys
import datetime

# --- Site Template ---
# Updated with Parchment Paper Effect and Adishila Font Focus
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="sa">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Noto+Sans+Devanagari:wght@400;500;600&family=Noto+Serif+Devanagari:wght@400;500;600&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="{css_path}">
    <style>
        :root {{
            --parchment-base: #fcf5e5;
            --parchment-grain: rgba(0, 0, 0, 0.03);
            --font-adishila: 'AdishilaVedic', 'AdishilaSanVedic', 'Noto Serif Devanagari', serif;
        }}

        body {{
            background-color: var(--color-bg-main);
            font-family: var(--font-adishila);
        }}

        /* Parchment Paper Container */
        .main-content {{
            background-color: var(--parchment-base);
            background-image: 
                radial-gradient(var(--parchment-grain) 1px, transparent 0),
                linear-gradient(to right, rgba(0,0,0,0.01) 1px, transparent 1px),
                linear-gradient(to bottom, rgba(0,0,0,0.01) 1px, transparent 1px);
            background-size: 20px 20px, 100% 2px, 2px 100%;
            padding: 4rem 3rem;
            border-radius: 4px;
            box-shadow: 
                2px 2px 10px rgba(0,0,0,0.1),
                -1px -1px 2px rgba(255,255,255,0.5),
                inset 0 0 100px rgba(133, 42, 42, 0.05);
            border: 1px solid #d8ccb8;
            margin-top: 2rem;
            margin-bottom: 4rem;
            position: relative;
            overflow: hidden;
        }}

        /* Subtle Paper "Edge" */
        .main-content::after {{
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0; bottom: 0;
            pointer-events: none;
            box-shadow: inset 0 0 20px rgba(0,0,0,0.02);
            border: 15px solid transparent;
            border-image: radial-gradient(circle, #00000005 1%, transparent 100%) 30;
        }}

        .ritual-content {{
            font-family: var(--font-adishila);
            color: var(--color-text);
            max-width: 800px;
            margin: 0 auto;
        }}

        .ritual-content p {{
            margin-bottom: 1.5rem;
            font-size: 1.4rem;
            line-height: 2.2;
            text-align: justify;
        }}

        .ritual-content h1, .ritual-content h2 {{
            font-family: var(--font-adishila);
            color: var(--deep-maroon, #852a2a);
            text-align: center;
            border-bottom: 1px solid var(--color-accent);
            padding-bottom: 1rem;
            margin-bottom: 2rem;
            margin-top: 3rem;
            display: block;
        }}

        .ritual-content ul, .ritual-content ol {{
            margin: 2rem 0;
            padding-left: 2.5rem;
            list-style-type: square;
        }}

        .ritual-content li {{
            margin-bottom: 1rem;
            font-size: 1.25rem;
            color: var(--text-main);
            font-weight: 500;
        }}

        /* Instructions in Italics */
        .ritual-content em, .ritual-content i {{
            color: var(--text-muted);
            font-style: italic;
            font-size: 0.9em;
        }}

        /* Header logo tweak */
        .logo-text {{
            font-family: var(--font-adishila);
        }}

        /* Vedic Accent Spans */
        .accent-swarita, .accent-anudatta, .accent-kampa {{
            color: var(--swara-red, #b71c1c);
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <div class="page-container">
        <aside class="sidebar-left">
            <div class="logo">
                <a href="{home_path}">
                    <div class="logo-text">जैमिनीय साम सङ्ग्रहः</div>
                    <div class="logo-subtitle">Jaimineeya Sama Sangraha</div>
                    <div class="logo-version">v{version}</div>
                </a>
            </div>
            
            <div class="nav-section">
                <a href="{index_path}" class="search-btn">
                    ⬅ back to Collection
                </a>
            </div>

            <div class="sidebar-footer">
                <a href="{home_path}" class="footer-btn">Home</a>
            </div>
        </aside>
        
        <main class="main-content">
            <div class="ritual-content sanskrit-text">
                {content}
            </div>
            
            <footer class="footer" style="margin-top: 5rem; border-top: 1px dashed var(--border-color); padding-top: 2rem; text-align: center; color: var(--text-muted); font-size: 0.9rem;">
                जैमिनीय सामवेदः | Published: {date}
            </footer>
        </main>
    </div>
</body>
</html>
"""

def get_version():
    try:
        root = os.getcwd()
        version_path = os.path.join(root, "src", "VERSION")
        if os.path.exists(version_path):
            with open(version_path, "r") as f:
                return f.read().strip()
    except:
        pass
    return "3.2"

def get_relative_paths(output_path):
    abs_output = os.path.abspath(output_path)
    parts = abs_output.split(os.sep)
    
    try:
        docs_idx = parts.index("docs")
        depth = len(parts) - docs_idx - 1
        rel_prefix = "../" * depth
        
        if "prayogamala-purva" in parts:
            p_idx = parts.index("prayogamala-purva")
            p_depth = len(parts) - p_idx - 1
            p_prefix = "../" * p_depth
            return {
                "css": p_prefix + "css/styles.css",
                "home": p_prefix + "../../index.html",
                "index": p_prefix + "index.html"
            }
            
        return {
            "css": rel_prefix + "collection/prayogamala-purva/css/styles.css",
            "home": rel_prefix + "index.html",
            "index": rel_prefix + "collection/prayogamala-purva/index.html"
        }
    except ValueError:
        return {
            "css": "styles.css",
            "home": "index.html",
            "index": "index.html"
        }

def convert_docx_to_html(input_file, output_path):
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    # Mammoth Style Map for semantic conversion
    # Added missing accent styles
    style_map = """
    p[style-name='Normal (Web)'] => p
    p[style-name='Heading 1'] => h1
    p[style-name='Heading 2'] => h2
    r[style-name='accent-swarita'] => span.accent-swarita
    r[style-name='accent-anudatta'] => span.accent-anudatta
    r[style-name='accent-kampa'] => span.accent-kampa
    r[style-name='danda'] => span.danda
    r[style-name='mantra-number'] => span.mantra-number
    """
    
    with open(input_file, "rb") as docx_file:
        result = mammoth.convert_to_html(docx_file, style_map=style_map)
        inner_html = result.value
        messages = result.messages
        
    paths = get_relative_paths(output_path)
    version = get_version()
    title = os.path.splitext(os.path.basename(input_file))[0].replace("_", " ")
    
    full_html = HTML_TEMPLATE.format(
        title=title,
        content=inner_html,
        css_path=paths["css"],
        home_path=paths["home"],
        index_path=paths["index"],
        version=version,
        date=datetime.datetime.now().strftime("%d %B %Y")
    )
    
    with open(output_path, "w", encoding="utf-8") as html_file:
        html_file.write(full_html)
        
    print(f"Successfully converted {input_file} to {output_path}")
    if messages:
        print("Mammoth messages:")
        for msg in messages:
            print(f"- {msg}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python src/tools/convert_docx.py <input_file.docx> [output_file.html]")
        sys.exit(1)
        
    input_file = sys.argv[1]
    
    if len(sys.argv) >= 3:
        output_file = sys.argv[2]
    else:
        base_name = os.path.splitext(os.path.basename(input_file))[0]
        if "prayoga" in input_file:
             output_file = os.path.join("docs", "collection", "prayogamala-purva", "prayoga", base_name + ".html")
        else:
            output_file = base_name + ".html"
        
    if not os.path.exists(input_file):
        print(f"Error: File not found: {input_file}")
        sys.exit(1)
        
    convert_docx_to_html(input_file, output_file)
