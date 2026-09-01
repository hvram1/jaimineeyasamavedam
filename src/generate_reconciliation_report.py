"""
Generate the JSV_Samhita_Reconciliation_Report.md based on latest output files.
Reads:
- data/output/JSV_Structure_Summary.csv
- data/output/JSON_Samam_Continuity_Report.txt
- data/output/JSV_Samam_Granular_Table.csv
"""
import csv
import datetime
import os

OUTPUT_MD = r'data\output\JSV_Samhita_Reconciliation_Report.md'
CONTINUITY_REPORT = r'data\output\JSON_Samam_Continuity_Report.txt'
GRANULAR_TABLE = r'data\output\JSV_Samam_Granular_Table.csv'

def generate_report():
    print("Generating Reconciliation Report...")
    
    # 1. Read Granular Table for counts
    rows = []
    with open(GRANULAR_TABLE, 'r', encoding='utf-8-sig') as f:
        f.readline() # Skip metadata line
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
            
    total_samams = len(rows)
    
    # Unique Khandas
    khandas = set()
    for r in rows:
        khandas.add((r['Patha_Name'], r['Khanda']))
    total_khandas = len(khandas)
    
    # Unique Pathas
    pathas = set()
    for r in rows:
        pathas.add(r['Patha_Name'])
    total_pathas = len(pathas)
    
    # Group by Patha
    patha_counts = {}
    for r in rows:
        p = r['Patha_Name']
        patha_counts[p] = patha_counts.get(p, 0) + 1
    
    # Patha Order
    order = ['आग्नेयपाठः', 'तद्वपाठः', 'बृहतिपाठः', 'असाविपाठः', 'ऐन्द्रपाठः', 'पवमानपाठः']
    
    # 2. Read Continuity Report
    continuity_status = "✅ **PASS**"
    continuity_issues = []
    if os.path.exists(CONTINUITY_REPORT):
        with open(CONTINUITY_REPORT, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines:
                if "ISSUES FOUND" in line:
                    continuity_status = "⚠️ **ISSUES FOUND**"
                if "Duplicates" in line or "Gaps" in line or "Starts at" in line:
                    continuity_issues.append(line.strip())
    
    # 3. Generate Markdown
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    md = f"""# Jaimineeya Samaveda Samhita - Data Reconciliation Report

**Generated:** {timestamp}

---

## Executive Summary

This report summarizes the data reconciliation analysis performed on the Jaimineeya Samaveda Samhita source text and its various processed outputs.

### Overall Structure

| Metric | Value |
|--------|-------|
| **Pathas (SuperSections)** | {total_pathas} |
| **Khandas (Sections)** | {total_khandas} |
| **Samams** | {total_samams:,} |

**Numbering Continuity:** {continuity_status}

---

## Section 1: Patha-wise Breakdown

| Patha | Samams |
|-------|--------|
"""
    
    # Statistics Table
    for p_name in order:
        if p_name in patha_counts:
            md += f"| {p_name} | {patha_counts[p_name]} |\n"
            
    # Check for any pathas not in standard order
    for p_name in patha_counts:
        if p_name not in order:
             md += f"| {p_name} | {patha_counts[p_name]} |\n"

    md += f"| **TOTAL** | **{total_samams:,}** |\n\n"
    
    md += """---

## Section 2: Continuity & Integrity Checks

Derived from `JSON_Samam_Continuity_Report.txt`.

"""
    if continuity_issues:
        md += "### ⚠️ Identified Issues\n"
        md += "The following numbering inconsistencies were detected in the text:\n\n"
        for issue in continuity_issues:
            md += f"- {issue}\n"
        md += "\n**Action Required:** Specific corrections in the source text/CSV to resolve these duplicates or gaps.\n"
    else:
        md += "### ✅ No Issues Found\n"
        md += "All Khandas have contiguous Samam numbering starting from 1.\n"
        
    md += f"""
---

## Section 3: Output Files Generated

| File | Description | Status |
|------|-------------|--------|
| `JSV_Structure_Summary.csv` | Aggregated counts | Updated |
| `JSV_Samam_Granular_Table.csv` | Full Samam list ({total_samams} rows) | Updated |
| `JSON_Samam_Continuity_Report.txt` | Detailed checks | Updated |

---

## Conclusion

| Check | Status | Note |
|-------|--------|------|
| **Total Count** | {total_samams} | Based on '॥N॥' markers |
| **Continuity** | {continuity_status} | See Section 2 |

*Report generated automatically by `src/generate_reconciliation_report.py`*
"""

    with open(OUTPUT_MD, 'w', encoding='utf-8') as f:
        f.write(md)
    
    print(f"Report generated: {OUTPUT_MD}")

if __name__ == "__main__":
    generate_report()
