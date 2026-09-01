"""Detailed audit tool for Agneyam Kandah 1 swara modifiers."""

import sys
import re
from pathlib import Path

# Ensure UTF-8 output on Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

SAMAM_MALAYALAM_UNICODE = Path("data/input/Malayalam/Samam_Malayalam_Unicode.txt")
AGNEYAM_K1_EXTRACT = Path("data/input/Malayalam/Agneyam_K1_extract.txt")


def parse_kandah1(file_path: Path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Extract subsection 1 through 13
    pattern = re.compile(
        r"# Start of SubSection Title -- (subsection_\d+) ## DO NOT EDIT\s*\n(.*?)\n# End of SubSection Title -- \1 ## DO NOT EDIT.*?"
        r"#Start of Mantra Sets -- \1 ## DO NOT EDIT\s*\n(.*?)\n#End of Mantra Sets -- \1 ## DO NOT EDIT",
        re.DOTALL
    )
    
    subsections = {}
    for match in pattern.finditer(content):
        sub_id = match.group(1)
        sub_num = int(sub_id.split("_")[1])
        if sub_num <= 13:
            subsections[sub_id] = {
                "title": match.group(2).strip(),
                "mantra": match.group(3).strip()
            }
    return subsections


def analyze_modifiers(mantra_text: str):
    """List all modifiers and phrasing marks in the mantra text."""
    modifiers_found = []
    
    # Check parenthesized modifiers
    paren_mods = re.findall(r"\(([A-HJ-Z][0-9_]?)\)", mantra_text)
    modifiers_found.extend([f"({m})" for m in paren_mods])
    
    # Check inline marks
    if "_" in mantra_text:
        modifiers_found.append(f"_ (low line, count={mantra_text.count('_')})")
    if "." in mantra_text:
        modifiers_found.append(f". (pause dot, count={mantra_text.count('.')})")
    if "," in mantra_text:
        modifiers_found.append(f", (comma, count={mantra_text.count(',')})")
        
    return modifiers_found


def main():
    subs = parse_kandah1(AGNEYAM_K1_EXTRACT)
    print(f"Total Subsections in Kandah 1: {len(subs)}")
    print("=" * 80)
    for sub_id, data in subs.items():
        print(f"\n[{sub_id}] {data['title']}")
        print(f"Mantra:\n{data['mantra']}")
        mods = analyze_modifiers(data['mantra'])
        print(f"Modifiers: {', '.join(mods)}")
    print("=" * 80)


if __name__ == "__main__":
    main()
