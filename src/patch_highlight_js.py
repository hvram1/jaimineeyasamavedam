"""
Post-processing script v4: Patches generated main.js files.
Two independent patches applied in separate passes.

Run AFTER generate_website.py:
  python src/generate_website.py --samhita
  python src/generate_website.py --aaranam
  python src/patch_highlight_js.py
"""
import pathlib

DOCS_DIR = pathlib.Path(__file__).parent.parent / 'docs'

def patch_file(js_path):
    content = js_path.read_text(encoding='utf-8')
    patches = []
    
    # === PATCH A: Fix wsRegex ===
    # Find ANY line with wsRegex and new RegExp, replace with regex literal
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if 'wsRegex' in line and 'new RegExp' in line:
            indent = line[:len(line) - len(line.lstrip())]
            lines[i] = indent + "const wsRegex = /\\s+/g;"
            patches.append(f"  Patch A: Fixed wsRegex on line {i+1}")
    content = '\n'.join(lines)
    
    # === PATCH B: Replace highlighter ===
    # Find the old simple highlighter by its unique signature
    OLD_MARKER = "let searchQ = query;"
    if OLD_MARKER in content:
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if OLD_MARKER in line.strip():
                # Find function start
                start = i
                for j in range(i, max(i-5, 0), -1):
                    if 'highlightText' in lines[j]:
                        start = j
                        break
                # Find function end
                end = i
                for j in range(i, min(i+20, len(lines))):
                    if lines[j].strip() == '};':
                        end = j
                        break
                
                # The replacement highlighter
                ind = "    "
                new_fn_lines = [
                    f'{ind}const highlightText = (text, query, devanagariQuery) => {{',
                    f'{ind}    if (!text) return text;',
                    f'{ind}    if (!query && !devanagariQuery) return text;',
                    f'{ind}',
                    f'{ind}    // Filler regex: skip virama, accents, dandas, whitespace, swara labels, HTML tags',
                    f'{ind}    const FILLER = /[\\u094D\\u0951-\\u0957\\u0964\\u0965\\u1CD0-\\u1CFF\\s]|\\([^)]*\\)|<[^>]+>/;',
                    f'{ind}    const fillerPat = "(?:" + FILLER.source + ")*";',
                    f'{ind}',
                    f'{ind}    // Vowel-matra equivalence for cross-script highlighting',
                    f'{ind}    const vowelMap = new Map([',
                    f'{ind}        ["\\u0905", "(?:\\u0905|\\u093E)?"],',
                    f'{ind}        ["\\u0906", "(?:\\u0906|\\u093E)"],',
                    f'{ind}        ["\\u0907", "(?:\\u0907|\\u093F)"],',
                    f'{ind}        ["\\u0908", "(?:\\u0908|\\u0940)"],',
                    f'{ind}        ["\\u0909", "(?:\\u0909|\\u0941)"],',
                    f'{ind}        ["\\u090A", "(?:\\u090A|\\u0942)"],',
                    f'{ind}        ["\\u090B", "(?:\\u090B|\\u0943)"],',
                    f'{ind}        ["\\u090F", "(?:\\u090F|\\u0947)"],',
                    f'{ind}        ["\\u0910", "(?:\\u0910|\\u0948)"],',
                    f'{ind}        ["\\u0913", "(?:\\u0913|\\u094B)"],',
                    f'{ind}        ["\\u0914", "(?:\\u0914|\\u094C)"],',
                    f'{ind}    ]);',
                    f'{ind}',
                    f'{ind}    const createPermissiveRegex = (q) => {{',
                    f'{ind}        if (!q) return null;',
                    f'{ind}        const baseQ = q.replace(/\\([^)]*\\)/g, "").replace(/[\\u0951-\\u0957\\u1CD0-\\u1CFF\\u0964\\u0965\\s]/g, "").trim();',
                    f'{ind}        if (!baseQ) return null;',
                    f'{ind}        const pattern = baseQ.split("").map(char => {{',
                    f'{ind}            const vm = vowelMap.get(char);',
                    f'{ind}            if (vm) return vm + fillerPat;',
                    f'{ind}            const escaped = char.replace(/[.*+?^${{}}()|[\\]\\\\]/g, "\\\\$&");',
                    f'{ind}            return escaped + fillerPat;',
                    f'{ind}        }}).join("");',
                    f'{ind}        return new RegExp(pattern, "gi");',
                    f'{ind}    }};',
                    f'{ind}',
                    f'{ind}    const isDevanagariField = /[\\u0900-\\u097F]/.test(text);',
                    f'{ind}    const effectiveQuery = (isDevanagariField && devanagariQuery) ? devanagariQuery : query;',
                    f'{ind}',
                    f'{ind}    const regex = createPermissiveRegex(effectiveQuery);',
                    f'{ind}    if (!regex) return text;',
                    f'{ind}',
                    f'{ind}    return text.replace(regex, (match) => "<mark>" + match + "</mark>");',
                    f'{ind}}};',
                ]
                lines[start:end+1] = new_fn_lines
                patches.append(f"  Patch B: Replaced highlighter (lines {start+1}-{end+1})")
                content = '\n'.join(lines)
                break
    elif 'fillerPat' in content:
        patches.append("  Patch B: Already applied")
    
    js_path.write_text(content, encoding='utf-8')
    return patches

def run_patcher():
    """Main entry point to patch all sites."""
    print("\n[POST-PROCESS] Applying visual and search patches...")
    for site in ['samhita', 'aaranam']:
        js_path = DOCS_DIR / site / 'js' / 'main.js'
        if not js_path.exists():
            print(f"  SKIP: {js_path}")
            continue
        
        result = patch_file(js_path)
        print(f"[{site}]")
        for p in result:
            print(p)
    print("\nDone. Refresh browser (Ctrl+Shift+R) to test.")

if __name__ == '__main__':
    run_patcher()
