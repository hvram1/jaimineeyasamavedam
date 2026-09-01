import sys, re
from pathlib import Path

MASTER = Path('data/input/Malayalam/Samam_Malayalam_Unicode.txt')
text = MASTER.read_text(encoding='utf-8')

SEC_RE = re.compile(r'# Start of Section Title -- (section_\d+) ## DO NOT EDIT\s*\n(.*?)\n# End of Section Title -- \1 ## DO NOT EDIT', re.DOTALL)
SUB_RE = re.compile(r'#Start of Mantra Sets -- (subsection_\d+) ## DO NOT EDIT')

sections = list(SEC_RE.finditer(text))

SUPERSECTIONS = [
    (1, 12, "Agneyam (SS1)", 3, 38),
    (13, 25, "Tadva (SS2)", 39, 83),
    (26, 34, "Bruhati (SS3)", 84, 130),
    (35, 41, "Asaavi (SS4)", 131, 160),
    (42, 52, "Aindram (SS5)", 161, 210),
    (53, 64, "Pavamanam (SS6)", 211, 324),
]

sec_list = []
for i, s in enumerate(sections):
    sec_id = s.group(1)
    sec_num = int(sec_id.split('_')[1])
    sec_title = s.group(2).strip()
    start_pos = s.end()
    end_pos = sections[i+1].start() if i+1 < len(sections) else len(text)
    sec_content = text[start_pos:end_pos]
    subs = SUB_RE.findall(sec_content)
    sub_nums = [int(x.split('_')[1]) for x in subs]
    if sub_nums:
        # Determine which Parva
        parva = "Unknown"
        p_start, p_end = 3, 324
        for ps, pe, pname, pg_s, pg_e in SUPERSECTIONS:
            if ps <= sec_num <= pe:
                parva = pname
                p_start, p_end = pg_s, pg_e
                break
                
        sec_list.append({
            "num": sec_num,
            "id": sec_id,
            "title": sec_title,
            "sub_start": min(sub_nums),
            "sub_end": max(sub_nums),
            "sub_count": len(sub_nums),
            "parva": parva,
            "parva_page_start": p_start,
            "parva_page_end": p_end
        })

with open('Malayalam_JSV/stage_output/section_page_index.txt', 'w', encoding='utf-8') as f:
    f.write("EXACT SECTION AND PARVA GROUND-TRUTH PAGE INDEX\n")
    f.write("=" * 80 + "\n")
    for s in sec_list:
        f.write(f"Section {s['num']:02d} [{s['id']}] ({s['parva']}): {s['title']} | Subsections: {s['sub_start']}..{s['sub_end']} ({s['sub_count']} subs) | Parva Pages: {s['parva_page_start']}..{s['parva_page_end']}\n")

print(f"Generated section index with {len(sec_list)} sections.")
