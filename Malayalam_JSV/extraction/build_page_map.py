"""Generate page-to-subsection map for JSV Samhita Malayalam manuscript."""

import re
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MASTER = REPO / "data/input/Malayalam/Samam_Malayalam_Unicode.txt"
OUTPUT = REPO / "Malayalam_JSV/stage_output/page_map.json"

text = MASTER.read_text(encoding="utf-8")

# Extract all sections and subsections
sub_re = re.compile(
    r'#Start of Mantra Sets -- (subsection_\d+) ## DO NOT EDIT\s*\n(.*?)\n#End of Mantra Sets -- \1 ## DO NOT EDIT',
    re.DOTALL
)

subsections = []
for m in sub_re.finditer(text):
    sid = m.group(1)
    snum = int(sid.split('_')[1])
    body = m.group(2).strip()
    first_line = body.split('\n')[0]
    subsections.append({
        "id": sid,
        "number": snum,
        "first_line": first_line[:60]
    })

print(f"Total subsections extracted: {len(subsections)}")

# We will save the base metadata index
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
with open(OUTPUT, 'w', encoding='utf-8') as f:
    json.dump(subsections, f, ensure_ascii=False, indent=2)

print(f"Saved {OUTPUT.name}")
