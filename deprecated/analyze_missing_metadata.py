import csv

input_csv = r'data\output\JSV_Missing_Metadata.csv'

rik_missing = []
samam_missing = []
both_missing = []
total_count = 0

try:
    with open(input_csv, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            total_count += 1
            missing = row['Missing']
            is_rik = 'Rik_' in missing
            is_samam = 'Samam_' in missing
            
            entry = f"| {row['Patha']} | {row['Khanda']} | Rik {row['Rik_ID']} | Samam {row['Samam_Num']} | {missing} |"
            
            if is_rik and is_samam:
                both_missing.append(entry)
            elif is_rik:
                rik_missing.append(entry)
            elif is_samam:
                samam_missing.append(entry)
except FileNotFoundError:
    print(f"Error: {input_csv} not found.")
    exit()

print(f"\nAnalysis of {total_count} missing metadata entries:\n")

print('### 🔴 Rows Missing RIK Metadata (Critical)')
print('These rows are missing fundamental Rik information (Rishi, Devata, or Chandas).')
print('| Patha | Khanda | Rik ID | Samam Num | Missing Fields |')
print('|---|---|---|---|---|')
if not rik_missing and not both_missing:
    print("| - | - | - | - | None |")
else:
    for row in rik_missing:
        print(row)
    for row in both_missing:
        print(row)

total_rik_issues = len(rik_missing) + len(both_missing)
print(f'\n**(Total Rik Issues: {total_rik_issues})**')

print('\n### 🟠 Rows Missing Only SAMAM Metadata')
print('These rows have valid Rik info but are missing specific Samam metadata (usually Chandas).')
print(f'**(Total Samam-Only Issues: {len(samam_missing)})**')

if samam_missing:
    print('\nShowing first 20 examples:')
    print('| Patha | Khanda | Rik ID | Samam Num | Missing Fields |')
    print('|---|---|---|---|---|')
    for row in samam_missing[:20]:
        print(row)
    if len(samam_missing) > 20:
        print(f"| ... | ... | ... | ... | ... ({len(samam_missing) - 20} more) |")
