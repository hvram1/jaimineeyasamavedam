import json

data = json.load(open('Agneyam-Pavamanam_latest_out.json', encoding='utf-8'))

# Find subsection_1488 and show all its Rik info  
for ss_id, ss in data.get('supersection', {}).items():
    for sec_id, sec in ss.get('sections', {}).items():
        if sec_id == 'count':
            continue
        subs = sec.get('subsections', {})
        for k, v in subs.items():
            if k == 'subsection_1488':
                print(f"Found {k} in {sec_id}:")
                print(f"  rik_id (first): {v.get('rik_id')}")
                print(f"  rik_ids (all): {v.get('rik_ids')}")
                rik_text = v.get('rik_text', '')
                if rik_text:
                    lines = rik_text.split('\n')
                    print(f"  rik_text has {len(lines)} separate Rik texts:")
                    for i, line in enumerate(lines):
                        # Show start to identify which Rik
                        print(f"    Rik {i+1}: {line[:60]}")
                else:
                    print("  rik_text: None")
