import re
from pathlib import Path
from collections import Counter

MASTER = Path('data/input/Malayalam/Samam_Malayalam_Unicode.txt')
text = MASTER.read_text(encoding='utf-8')

SUBSECTION_RE = re.compile(
    r'#Start of Mantra Sets -- (subsection_(\d+)) ## DO NOT EDIT\s*\n(.*?)\n#End of Mantra Sets -- \1 ## DO NOT EDIT',
    re.DOTALL
)

mod_re = re.compile(r'\(([A-Z][0-9_]?)\)')
inline_re = re.compile(r'[_.,]')
grantha_re = re.compile(r'\(([\u11300-\u1137F\u0D00-\u0D7F]+)\)')

sections = [
    ('Kandah 1 (sub_1..13)', 1, 13),
    ('Kandah 2 (sub_14..24)', 14, 24),
    ('Agneyam Remainder (sub_25..126)', 25, 126),
    ('Tadva (sub_127..251)', 127, 251),
    ('Bruhati (sub_252..346)', 252, 346),
    ('Asaavi (sub_348..411)', 348, 411),
    ('Aindra (sub_1413..1517)', 1413, 1517),
    ('Pavamana (sub_519..727)', 519, 727),
]

stats = {name: {'subs': 0, 'subs_with_mods': 0, 'mods': Counter(), 'inlines': Counter(), 'grantha': 0} for name, _, _ in sections}
stats['Other'] = {'subs': 0, 'subs_with_mods': 0, 'mods': Counter(), 'inlines': Counter(), 'grantha': 0}

overall_mods = Counter()
overall_inlines = Counter()

for m in SUBSECTION_RE.finditer(text):
    sid = m.group(1)
    snum = int(m.group(2))
    body = m.group(3).strip()
    
    sec_name = 'Other'
    for name, start, end in sections:
        if start <= snum <= end:
            sec_name = name
            break
            
    stats[sec_name]['subs'] += 1
    
    mods = mod_re.findall(body)
    inlines = inline_re.findall(body)
    grantha = grantha_re.findall(body)
    
    if mods or inlines:
        stats[sec_name]['subs_with_mods'] += 1
        
    for mod in mods:
        stats[sec_name]['mods'][mod] += 1
        overall_mods[mod] += 1
        
    for inl in inlines:
        stats[sec_name]['inlines'][inl] += 1
        overall_inlines[inl] += 1
        
    stats[sec_name]['grantha'] += len(grantha)

print('=' * 80)
print('DETAILED INVENTORY: SWARA MODIFIERS & INLINE DETECTION ACROSS SECTIONS')
print('=' * 80)

for sec_name, data in stats.items():
    if data['subs'] == 0:
        continue
    pct = (data['subs_with_mods'] / data['subs']) * 100
    tot_mods = sum(data['mods'].values())
    tot_inlines = sum(data['inlines'].values())
    print(f'\n### {sec_name}')
    print(f"  Total Subsections: {data['subs']}")
    print(f"  Annotated Subsections: {data['subs_with_mods']} ({pct:.1f}%)")
    print(f"  Total Swara Modifiers: {tot_mods}")
    print(f"  Total Inline Phrasing Marks: {tot_inlines}")
    print(f"  Grantha Swara Letters: {data['grantha']}")
    print(f"  Modifier Breakdown: {dict(data['mods'].most_common())}")
    print(f"  Inline Breakdown:   {dict(data['inlines'].most_common())}")

print('\n' + '=' * 80)
print('OVERALL CORPUS SUMMARY:')
print(f"  Total Subsections in Samhita: {sum(d['subs'] for d in stats.values())}")
print(f"  Total Swara Modifiers:        {sum(overall_mods.values())}")
print(f"  Swara Modifiers Frequencies:  {dict(overall_mods.most_common())}")
print(f"  Total Inline Phrasing Marks:  {sum(overall_inlines.values())}")
print(f"  Inline Marks Frequencies:     {dict(overall_inlines.most_common())}")
print('=' * 80)
