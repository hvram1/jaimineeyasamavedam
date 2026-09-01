#!/usr/bin/env python3
"""
Extract Devanagari Swara Symbols with Danda Separators for Jaimineeya Samavedam (Samhita).

Outputs generated:
1. data/output/Samhita_Devanagari_Swara_Table.csv (Granular table with Sl No, swaras and sentence danda separators '|')
2. data/output/Samhita_Devanagari_Swara_By_Sama.csv (Per-Sama summary with Sl No, dandas separating sentence swara chunks)
3. data/output/swara_devanagari/samhita_devanagari_swara_table.md (Markdown report in 2-line document format)
4. data/output/swara_devanagari/samhita_devanagari_swara_table.html (Interactive HTML report in 2-line document format)
5. data/output/swara_devanagari/samhita_devanagari_swara_table.pdf (Print-ready PDF report in 2-line document format)
"""

import os
import sys
import json
import re
import csv
import subprocess
from pathlib import Path

# Base Paths
REPO_ROOT = Path(__file__).resolve().parent.parent
INPUT_JSON = REPO_ROOT / "data" / "output" / "Samhita_corrected_out.json"
OUTPUT_DIR_CSV = REPO_ROOT / "data" / "output"
OUTPUT_DIR_SWARA = REPO_ROOT / "data" / "output" / "swara_devanagari"

GRANULAR_CSV = OUTPUT_DIR_CSV / "Samhita_Devanagari_Swara_Table.csv"
PER_SAMA_CSV = OUTPUT_DIR_CSV / "Samhita_Devanagari_Swara_By_Sama.csv"
SWARA_MD = OUTPUT_DIR_SWARA / "samhita_devanagari_swara_table.md"
SWARA_HTML = OUTPUT_DIR_SWARA / "samhita_devanagari_swara_table.html"
SWARA_PDF = OUTPUT_DIR_SWARA / "samhita_devanagari_swara_table.pdf"


def clean_text_for_swaras(text: str) -> str:
    """Fix any known typos or unclosed parentheses before punctuation."""
    text = text.replace('(शि।', '(शि)।')
    text = text.replace('(चा।', '(चा)।')
    return text


def find_browser_executable() -> str:
    """Locate Microsoft Edge or Google Chrome executable for PDF compilation."""
    candidates = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return ""


def export_html_to_pdf(html_path: Path, pdf_path: Path):
    """Compile HTML to high-fidelity print PDF using headless Edge/Chrome."""
    browser_exe = find_browser_executable()
    if not browser_exe:
        print("Warning: Neither Edge nor Chrome was found. Skipping automated PDF compilation.")
        return False

    print(f"Compiling PDF via headless browser: {browser_exe}")
    cmd = [
        browser_exe,
        "--headless",
        "--disable-gpu",
        "--run-all-compositor-stages-before-draw",
        f"--print-to-pdf={pdf_path}",
        "--no-pdf-header-footer",
        str(html_path.resolve())
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if res.returncode == 0 and pdf_path.exists():
            size_mb = pdf_path.stat().st_size / (1024 * 1024)
            print(f"PDF generated successfully: {pdf_path} ({size_mb:.2f} MB)")
            return True
        else:
            print(f"PDF generation exited with code {res.returncode}. Stderr: {res.stderr}")
            return False
    except Exception as e:
        print(f"Error during PDF compilation: {e}")
        return False


def extract_devanagari_swaras():
    print(f"Loading input JSON: {INPUT_JSON}")
    if not INPUT_JSON.exists():
        raise FileNotFoundError(f"Input file not found: {INPUT_JSON}")

    with open(INPUT_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    granular_rows = []
    per_sama_rows = []
    hierarchy = []

    total_samas = 0
    total_swaras_count = 0
    total_dandas_count = 0
    granular_sl_no = 0

    supersections = data.get("supersection", {})

    for ss_idx, (ss_key, ss_val) in enumerate(supersections.items(), 1):
        parva_name = ss_val.get("supersection_title", f"Parva {ss_idx}")
        sections = ss_val.get("sections", {})
        
        parva_samas_start = total_samas + 1
        parva_swara_count = 0
        parva_danda_count = 0
        parva_samas_count = 0
        parva_kandahs_list = []

        for s_idx, (s_key, s_val) in enumerate(sections.items(), 1):
            kandah_label = f"Kandah {s_idx}"
            kandah_name = s_val.get("section_title", kandah_label)
            subsections = s_val.get("subsections", {})

            kandah_samas_start = total_samas + 1
            kandah_rows = []

            for sub_key, sub_val in subsections.items():
                total_samas += 1
                parva_samas_count += 1

                h_title = sub_val.get("header", {}).get("header", "").strip("॥").strip()
                if not h_title:
                    h_title = f"Sama {total_samas}"

                mantras = sub_val.get("corrected-mantra_sets", []) or sub_val.get("mantra_sets", [])

                sama_sentence_chunks = []

                for m in mantras:
                    raw_text = m.get("corrected-mantra", "") or m.get("mantra", "")
                    text = clean_text_for_swaras(raw_text)

                    # Split sentences by । or ॥
                    sentences = re.split(r"[।॥]", text)
                    for sent in sentences:
                        sent = sent.strip()
                        if not sent:
                            continue
                        # Remove standalone verse numbering (e.g. '१', '२')
                        sent_clean = re.sub(r"^\d+$", "", sent).strip()
                        if not sent_clean:
                            continue

                        # Extract swaras within parentheses
                        swaras = re.findall(r"\(([^()]+)\)", sent_clean)
                        swaras = [s.strip() for s in swaras if s.strip()]

                        if swaras:
                            for sw in swaras:
                                granular_sl_no += 1
                                granular_rows.append({
                                    "Sl No": granular_sl_no,
                                    "Parva": parva_name,
                                    "Kandah <M>": kandah_label,
                                    "Sama Name": h_title,
                                    "Swara symbol": sw
                                })
                                total_swaras_count += 1
                                parva_swara_count += 1

                            # Insert danda separator row
                            granular_sl_no += 1
                            granular_rows.append({
                                "Sl No": granular_sl_no,
                                "Parva": parva_name,
                                "Kandah <M>": kandah_label,
                                "Sama Name": h_title,
                                "Swara symbol": "|"
                            })
                            total_dandas_count += 1
                            parva_danda_count += 1

                            sama_sentence_chunks.append(" ".join(swaras))

                # Format per-sama swara sequence
                # Example: 'त त श | थाच् चा श | टा श टि श | चा श चि | टा श टि श | कि च | ट ट खा शि | ख श |'
                formatted_swaras = " | ".join(sama_sentence_chunks) + " |" if sama_sentence_chunks else ""

                row_dict = {
                    "Sl No": total_samas,
                    "Parva": parva_name,
                    "Kandah <M>": kandah_label,
                    "Kandah Name": kandah_name,
                    "Sama Name": h_title,
                    "Swara Symbols": formatted_swaras
                }
                per_sama_rows.append(row_dict)
                kandah_rows.append(row_dict)

            kandah_samas_end = total_samas
            kandah_range_str = f"Sama {kandah_samas_start} – {kandah_samas_end}" if len(kandah_rows) > 1 else f"Sama {kandah_samas_start}"
            parva_kandahs_list.append({
                "kandah_label": kandah_label,
                "kandah_name": kandah_name,
                "sama_range": kandah_range_str,
                "samas_count": len(kandah_rows),
                "rows": kandah_rows
            })

        parva_samas_end = total_samas
        parva_range_str = f"Sama {parva_samas_start} – {parva_samas_end}" if parva_samas_count > 1 else f"Sama {parva_samas_start}"
        hierarchy.append({
            "parva_idx": ss_idx,
            "parva_name": parva_name,
            "kandahs_count": len(sections),
            "sama_range": parva_range_str,
            "total_samas": parva_samas_count,
            "total_swaras": parva_swara_count,
            "total_dandas": parva_danda_count,
            "total_rows": parva_swara_count + parva_danda_count,
            "kandahs": parva_kandahs_list
        })

    # Ensure output directories exist
    OUTPUT_DIR_CSV.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR_SWARA.mkdir(parents=True, exist_ok=True)

    # 1. Write Granular CSV (with Sl No)
    print(f"Writing Granular CSV: {GRANULAR_CSV} ({len(granular_rows):,} rows)")
    with open(GRANULAR_CSV, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["Sl No", "Parva", "Kandah <M>", "Sama Name", "Swara symbol"])
        writer.writeheader()
        writer.writerows(granular_rows)

    # 2. Write Per-Sama CSV (with Sl No)
    print(f"Writing Per-Sama CSV: {PER_SAMA_CSV} ({len(per_sama_rows):,} rows)")
    with open(PER_SAMA_CSV, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["Sl No", "Parva", "Kandah <M>", "Kandah Name", "Sama Name", "Swara Symbols"])
        writer.writeheader()
        writer.writerows(per_sama_rows)

    # 3. Generate Markdown documentation (Document Format)
    print(f"Writing Markdown documentation: {SWARA_MD}")
    md_content = generate_markdown_content(hierarchy, total_samas, total_swaras_count, total_dandas_count, granular_rows, per_sama_rows)
    with open(SWARA_MD, "w", encoding="utf-8") as f:
        f.write(md_content)

    # 4. Generate HTML interactive report (Document Format)
    print(f"Writing HTML interactive report: {SWARA_HTML}")
    html_content = generate_html_content(hierarchy, total_samas, total_swaras_count, total_dandas_count, granular_rows, per_sama_rows)
    with open(SWARA_HTML, "w", encoding="utf-8") as f:
        f.write(html_content)

    # 5. Export to PDF
    export_html_to_pdf(SWARA_HTML, SWARA_PDF)

    print("\nExtraction & generation completed successfully!")
    print(f"  - Total Parvas: {len(hierarchy)}")
    print(f"  - Total Kandahs: {sum(p['kandahs_count'] for p in hierarchy)}")
    print(f"  - Total Samas: {total_samas}")
    print(f"  - Total Swara Occurrences: {total_swaras_count:,}")
    print(f"  - Total Danda Separators: {total_dandas_count:,}")
    print(f"  - Total Granular CSV Rows: {len(granular_rows):,}")


def generate_markdown_content(hierarchy, total_samas, total_swaras, total_dandas, granular_rows, per_sama_rows):
    lines = []
    lines.append("# Jaimineeya Samavedam: Devanagari Samhita Swaras\n")
    lines.append("This document presents the swara symbols occurring in **Samhita** in Devanagari script structured in a **sequential 2-line document format**:\n")
    lines.append("- **Line 1**: `<Sl No>. <Name of Samam>`")
    lines.append("- **Line 2**: `<Swaras in the Samam>` (with explicit `|` sentence separators)\n")

    total_kandahs = sum(p["kandahs_count"] for p in hierarchy)
    lines.append("## 1. Summary Statistics\n")
    lines.append(f"- **Total Parvas**: {len(hierarchy)}")
    lines.append(f"- **Total Kandahs**: {total_kandahs}")
    lines.append(f"- **Total Samas**: {total_samas}")
    lines.append(f"- **Total Swara Occurrences**: {total_swaras:,}")
    lines.append(f"- **Total Sentence Dandas (`|`)**: {total_dandas:,}")
    lines.append(f"- **Total Granular Rows**: {len(granular_rows):,}\n")

    lines.append("### Breakdown by Parva\n")
    lines.append("| Parva (Supersection) | Kandahs | Sama Range | Total Samas | Swaras | Dandas (`|`) | Total Granular Rows |")
    lines.append("| :--- | :---: | :--- | :---: | :---: | :---: | :---: |")
    for p in hierarchy:
        lines.append(f"| **{p['parva_name']}** | Kandah 1 – {p['kandahs_count']} | {p['sama_range']} | {p['total_samas']} | {p['total_swaras']:,} | {p['total_dandas']:,} | {p['total_rows']:,} |")
    lines.append(f"| **Total** | **{total_kandahs} Kandahs** | | **{total_samas}** | **{total_swaras:,}** | **{total_dandas:,}** | **{len(granular_rows):,}** |")
    lines.append("\n---\n")

    lines.append("## 2. Generated Datasets\n")
    lines.append(f"1. **Per-Sama CSV** (`Sl No, Parva, Kandah <M>, Kandah Name, Sama Name, Swara Symbols`):")
    lines.append("   - [`Samhita_Devanagari_Swara_By_Sama.csv`](file:///c:/Users/sekha/OneDrive/Documents/GitHub/jaimineeyasamavedam/data/output/Samhita_Devanagari_Swara_By_Sama.csv)")
    lines.append(f"2. **Granular CSV** (`Sl No, Parva, Kandah <M>, Sama Name, Swara symbol`):")
    lines.append("   - [`Samhita_Devanagari_Swara_Table.csv`](file:///c:/Users/sekha/OneDrive/Documents/GitHub/jaimineeyasamavedam/data/output/Samhita_Devanagari_Swara_Table.csv)")
    lines.append(f"3. **Print-Ready PDF Document**:")
    lines.append("   - [`samhita_devanagari_swara_table.pdf`](file:///c:/Users/sekha/OneDrive/Documents/GitHub/jaimineeyasamavedam/data/output/swara_devanagari/samhita_devanagari_swara_table.pdf)")
    lines.append("\n---\n")

    lines.append("## 3. Sequential Swara Document\n")

    for p in hierarchy:
        lines.append(f"\n# {p['parva_idx']}. {p['parva_name']} ({p['sama_range']})\n")
        for k in p["kandahs"]:
            lines.append(f"## {k['kandah_label']}: {k['kandah_name']} ({k['sama_range']} — {k['samas_count']} Samas)\n")
            for r in k["rows"]:
                lines.append(f"**{r['Sl No']}. {r['Sama Name']}**  ")
                lines.append(f"`{r['Swara Symbols']}`\n")

    return "\n".join(lines)


def generate_html_content(hierarchy, total_samas, total_swaras, total_dandas, granular_rows, per_sama_rows):
    total_kandahs = sum(p["kandahs_count"] for p in hierarchy)

    # Parva breakdown rows
    breakdown_rows_html = ""
    for p in hierarchy:
        breakdown_rows_html += f"""
        <tr>
            <td style="font-weight: bold;"><a href="#parva-{p['parva_idx']}" style="color: #1a237e; text-decoration: none;">{p['parva_name']}</a></td>
            <td style="text-align:center;">Kandah 1 – {p['kandahs_count']}</td>
            <td>{p['sama_range']}</td>
            <td style="text-align:center;">{p['total_samas']}</td>
            <td style="text-align:center;">{p['total_swaras']:,}</td>
            <td style="text-align:center;">{p['total_dandas']:,}</td>
            <td style="text-align:center; font-weight: 600;">{p['total_rows']:,}</td>
        </tr>"""

    # Document Entries HTML
    parvas_sections_html = ""
    toc_links_html = ""

    for p in hierarchy:
        toc_kandah_links = " ".join([
            f'<a class="toc-kandah-chip" href="#parva-{p["parva_idx"]}-kandah-{k_idx}">{k["kandah_label"]}</a>'
            for k_idx, k in enumerate(p["kandahs"], 1)
        ])

        toc_links_html += f"""
        <div class="toc-card">
            <h4><a href="#parva-{p['parva_idx']}">{p['parva_idx']}. {p['parva_name']}</a> <span class="toc-badge">{p['sama_range']}</span></h4>
            <div class="toc-chips">{toc_kandah_links}</div>
        </div>"""

        kandah_blocks_html = ""
        for k_idx, k in enumerate(p["kandahs"], 1):
            sama_entries_html = ""
            for r in k["rows"]:
                # Colorize danda badges in the swara sequence
                tokens = r['Swara Symbols'].split()
                formatted_tokens = []
                for tok in tokens:
                    if tok == '|':
                        formatted_tokens.append('<span class="danda-badge">|</span>')
                    else:
                        formatted_tokens.append(f'<span class="swara-token">{tok}</span>')
                swaras_html = " ".join(formatted_tokens)

                sama_entries_html += f"""
                <div class="sama-item" data-sama-name="{r['Sama Name']}" data-sl-no="{r['Sl No']}">
                    <div class="sama-header-line">
                        <span class="sama-num">{r['Sl No']}.</span>
                        <span class="sama-title">{r['Sama Name']}</span>
                    </div>
                    <div class="sama-swara-line">{swaras_html}</div>
                </div>"""

            kandah_blocks_html += f"""
            <div class="kandah-block" id="parva-{p['parva_idx']}-kandah-{k_idx}">
                <div class="kandah-header">
                    <span class="kandah-title">{k['kandah_label']}: {k['kandah_name']}</span>
                    <span class="kandah-meta">{k['sama_range']} &bull; {k['samas_count']} Samas</span>
                </div>
                <div class="kandah-content">
                    {sama_entries_html}
                </div>
            </div>"""

        parvas_sections_html += f"""
        <section class="parva-section" id="parva-{p['parva_idx']}">
            <div class="parva-header">
                <h2>{p['parva_idx']}. {p['parva_name']}</h2>
                <span class="parva-meta">{p['kandahs_count']} Kandahs &bull; {p['sama_range']} ({p['total_samas']} Samas)</span>
            </div>
            {kandah_blocks_html}
        </section>"""

    return f"""<!DOCTYPE html>
<html lang="sa">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Jaimineeya Samavedam: Devanagari Swara Document</title>
    <style>
        :root {{
            --primary: #1a237e;
            --primary-dark: #0d47a1;
            --primary-light: #e8eaf6;
            --accent: #b71c1c;
            --danda-color: #d32f2f;
            --bg: #f4f6f9;
            --card-bg: #ffffff;
            --border: #e0e0e0;
            --text: #212121;
        }}
        * {{
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background-color: var(--bg);
            color: var(--text);
            margin: 0;
            padding: 0;
            line-height: 1.6;
            -webkit-print-color-adjust: exact !important;
            print-color-adjust: exact !important;
        }}
        .top-nav {{
            position: sticky;
            top: 0;
            background: var(--primary);
            color: white;
            padding: 12px 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            z-index: 1000;
            box-shadow: 0 2px 10px rgba(0,0,0,0.15);
        }}
        .top-nav-left {{
            display: flex;
            align-items: center;
            gap: 16px;
        }}
        .top-nav h3 {{
            margin: 0;
            font-size: 1.2rem;
            font-weight: 600;
        }}
        .top-nav-right {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        .search-box {{
            padding: 8px 14px;
            border-radius: 20px;
            border: 1px solid rgba(255,255,255,0.4);
            background: rgba(255,255,255,0.15);
            color: white;
            width: 260px;
            font-size: 0.95rem;
            outline: none;
            transition: all 0.2s;
        }}
        .search-box::placeholder {{
            color: rgba(255,255,255,0.7);
        }}
        .search-box:focus {{
            background: white;
            color: var(--text);
            border-color: white;
        }}
        .print-btn {{
            background: white;
            color: var(--primary);
            border: none;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 0.9rem;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 6px;
            transition: all 0.2s;
            box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        }}
        .print-btn:hover {{
            background: #e8eaf6;
            transform: translateY(-1px);
        }}
        .container {{
            max-width: 1200px;
            margin: 24px auto;
            padding: 0 20px;
        }}
        .main-card {{
            background: var(--card-bg);
            border-radius: 12px;
            padding: 32px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.06);
            margin-bottom: 24px;
        }}
        h1 {{
            color: var(--primary);
            font-size: 2rem;
            margin-top: 0;
            border-bottom: 3px solid var(--primary);
            padding-bottom: 12px;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
            gap: 16px;
            margin: 24px 0;
        }}
        .stat-card {{
            background: var(--primary-light);
            padding: 16px;
            border-radius: 8px;
            text-align: center;
            border-left: 4px solid var(--primary);
        }}
        .stat-card .val {{
            font-size: 1.7rem;
            font-weight: bold;
            color: var(--primary);
        }}
        .stat-card .label {{
            font-size: 0.85rem;
            color: #555;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .toc-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(360px, 1fr));
            gap: 16px;
            margin: 24px 0;
        }}
        .toc-card {{
            background: #fafafa;
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 14px 18px;
        }}
        .toc-card h4 {{
            margin: 0 0 10px 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .toc-card h4 a {{
            color: var(--primary);
            text-decoration: none;
            font-size: 1.05rem;
        }}
        .toc-badge {{
            font-size: 0.8rem;
            background: var(--primary-light);
            color: var(--primary);
            padding: 2px 8px;
            border-radius: 4px;
        }}
        .toc-chips {{
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
        }}
        .toc-kandah-chip {{
            display: inline-block;
            padding: 3px 8px;
            background: white;
            border: 1px solid #ccc;
            border-radius: 4px;
            font-size: 0.8rem;
            color: #333;
            text-decoration: none;
            transition: all 0.15s;
        }}
        .toc-kandah-chip:hover {{
            background: var(--primary);
            color: white;
            border-color: var(--primary);
        }}
        .parva-section {{
            margin-top: 40px;
        }}
        .parva-header {{
            background: linear-gradient(135deg, var(--primary), var(--primary-dark));
            color: white;
            padding: 16px 24px;
            border-radius: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            box-shadow: 0 3px 10px rgba(0,0,0,0.1);
        }}
        .parva-header h2 {{
            margin: 0;
            font-size: 1.4rem;
        }}
        .parva-meta {{
            font-size: 0.95rem;
            opacity: 0.9;
        }}
        .kandah-block {{
            background: white;
            border: 1px solid var(--border);
            border-radius: 8px;
            margin-bottom: 24px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        }}
        .kandah-header {{
            background: #eceff1;
            padding: 12px 18px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--border);
        }}
        .kandah-title {{
            font-weight: bold;
            font-size: 1.1rem;
            color: #263238;
        }}
        .kandah-meta {{
            font-size: 0.9rem;
            color: #546e7a;
            font-weight: 500;
        }}
        .kandah-content {{
            padding: 16px 20px;
        }}
        .sama-item {{
            padding: 12px 0;
            border-bottom: 1px solid #f0f0f0;
        }}
        .sama-item:last-child {{
            border-bottom: none;
        }}
        .sama-header-line {{
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 6px;
        }}
        .sama-num {{
            font-weight: bold;
            color: #000000;
            font-size: 1.05rem;
            min-width: 32px;
        }}
        .sama-title {{
            font-weight: bold;
            font-size: 1.15rem;
            color: #000000;
        }}
        .sama-swara-line {{
            padding-left: 36px;
            font-family: inherit;
            line-height: 2.2;
            color: #000000;
        }}
        .swara-token {{
            display: inline-block;
            background: #f5f5f5;
            color: #000000;
            padding: 2px 8px;
            border-radius: 4px;
            margin: 2px 3px;
            font-size: 1.05rem;
            font-weight: 500;
        }}
        .danda-badge {{
            display: inline-block;
            background: #e0e0e0;
            color: #000000;
            font-weight: bold;
            padding: 2px 9px;
            border-radius: 4px;
            margin: 2px 4px;
            font-size: 1.05rem;
        }}
        table.summary-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.95rem;
            margin-top: 16px;
        }}
        table.summary-table th {{
            background: var(--primary-light);
            color: var(--primary);
            font-weight: 600;
            padding: 10px 14px;
            border: 1px solid var(--border);
            text-align: left;
        }}
        table.summary-table td {{
            padding: 10px 14px;
            border: 1px solid var(--border);
        }}
        .file-links-list {{
            list-style: none;
            padding-left: 0;
        }}
        .file-links-list li {{
            padding: 6px 0;
        }}
        .file-links-list a {{
            color: #0d47a1;
            font-weight: bold;
            text-decoration: none;
        }}
        .file-links-list a:hover {{
            text-decoration: underline;
        }}

        /* Print Specific Styling (Pure Black and White) */
        @media print {{
            @page {{
                size: A4 portrait;
                margin: 14mm 12mm;
            }}
            body {{
                background: #ffffff !important;
                color: #000000 !important;
                font-size: 10pt;
            }}
            .top-nav, .search-box, .print-btn, .toc-grid, .file-links-list {{
                display: none !important;
            }}
            .container {{
                max-width: 100%;
                margin: 0;
                padding: 0;
            }}
            .main-card {{
                box-shadow: none;
                padding: 0 0 16px 0;
                margin-bottom: 16px;
                border-bottom: 2px solid #000000;
                page-break-after: always;
                break-after: page;
            }}
            .parva-section {{
                margin-top: 0;
                page-break-before: always;
                break-before: page;
            }}
            .parva-section:first-of-type {{
                page-break-before: always;
                break-before: page;
            }}
            .parva-header {{
                background: #000000 !important;
                color: #ffffff !important;
                -webkit-print-color-adjust: exact !important;
                print-color-adjust: exact !important;
                box-shadow: none;
                padding: 8px 14px;
                margin-bottom: 12px;
                page-break-after: avoid !important;
                break-after: avoid !important;
            }}
            .parva-header h2 {{
                color: #ffffff !important;
            }}
            .parva-meta {{
                color: #ffffff !important;
            }}
            .kandah-block {{
                box-shadow: none;
                border: 1px solid #000000;
                margin-bottom: 14px;
                page-break-before: always;
                break-before: page;
                page-break-inside: auto;
                break-inside: auto;
            }}
            /* Keep Parva header together with the subsequent first Kandah */
            .parva-header + .kandah-block,
            .parva-section > .kandah-block:first-of-type {{
                page-break-before: avoid !important;
                break-before: avoid !important;
            }}
            .kandah-header {{
                background: #f0f0f0 !important;
                color: #000000 !important;
                border-bottom: 1px solid #000000;
                -webkit-print-color-adjust: exact !important;
                print-color-adjust: exact !important;
                padding: 6px 12px;
                page-break-after: avoid !important;
                break-after: avoid !important;
            }}
            .kandah-title {{
                color: #000000 !important;
            }}
            .kandah-meta {{
                color: #333333 !important;
            }}
            .sama-item {{
                page-break-inside: avoid;
                break-inside: avoid;
                padding: 6px 0;
                border-bottom: 1px solid #e0e0e0;
            }}
            .sama-item:last-child {{
                border-bottom: none;
            }}
            .sama-num {{
                color: #000000 !important;
                font-weight: bold;
            }}
            .sama-title {{
                color: #000000 !important;
                font-weight: bold;
            }}
            .sama-swara-line {{
                padding-left: 20px;
                line-height: 1.9;
                color: #000000 !important;
            }}
            .swara-token {{
                background: none !important;
                color: #000000 !important;
                font-size: 9.5pt;
                padding: 0 2px;
                margin: 0 1px;
                font-weight: normal;
            }}
            .danda-badge {{
                background: none !important;
                color: #000000 !important;
                font-weight: bold;
                font-size: 9.5pt;
                padding: 0 4px;
                margin: 0 2px;
            }}
        }}
    </style>
</head>
<body>
    <nav class="top-nav">
        <div class="top-nav-left">
            <h3>॥ जैमिनीय साम संहिता ॥ Devanagari Swara Explorer</h3>
        </div>
        <div class="top-nav-right">
            <input type="text" id="searchInput" class="search-box" placeholder="Search Sama name or Sl No..." onkeyup="filterSamaDocument()">
            <button class="print-btn" onclick="window.print()">🖨️ Print / Save PDF</button>
        </div>
    </nav>

    <div class="container">
        <div class="main-card">
            <h1>Devanagari Swara Document (Line 1: Title | Line 2: Swaras)</h1>
            <p>This document presents the complete <strong>Samhita Swara Dataset</strong> structured in a clean, sequential 2-line document layout: <strong>Line 1:</strong> <code>&lt;Sl No&gt;. &lt;Sama Name&gt;</code> &bull; <strong>Line 2:</strong> <code>&lt;Swaras in the Samam&gt;</code> with explicit sentence <strong>danda separators (<code>|</code>)</strong>.</p>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="val">{len(hierarchy)}</div>
                    <div class="label">Parvas</div>
                </div>
                <div class="stat-card">
                    <div class="val">{total_kandahs}</div>
                    <div class="label">Kandahs</div>
                </div>
                <div class="stat-card">
                    <div class="val">{total_samas}</div>
                    <div class="label">Samas</div>
                </div>
                <div class="stat-card">
                    <div class="val">{total_swaras:,}</div>
                    <div class="label">Swara Symbols</div>
                </div>
                <div class="stat-card">
                    <div class="val">{total_dandas:,}</div>
                    <div class="label">Dandas (|)</div>
                </div>
                <div class="stat-card">
                    <div class="val">{len(granular_rows):,}</div>
                    <div class="label">Total Granular Rows</div>
                </div>
            </div>

            <h3>Generated Downloads</h3>
            <ul class="file-links-list">
                <li>📄 <strong>Print-Ready PDF Document</strong>: <a href="samhita_devanagari_swara_table.pdf" target="_blank">samhita_devanagari_swara_table.pdf</a></li>
                <li>📊 <strong>Per-Sama CSV ({len(per_sama_rows):,} rows with Sl No)</strong>: <a href="../Samhita_Devanagari_Swara_By_Sama.csv">Samhita_Devanagari_Swara_By_Sama.csv</a> &nbsp; <code>[Sl No, Parva, Kandah &lt;M&gt;, Kandah Name, Sama Name, Swara Symbols]</code></li>
                <li>📑 <strong>Granular Succession CSV ({len(granular_rows):,} rows with Sl No &amp; Dandas)</strong>: <a href="../Samhita_Devanagari_Swara_Table.csv">Samhita_Devanagari_Swara_Table.csv</a> &nbsp; <code>[Sl No, Parva, Kandah &lt;M&gt;, Sama Name, Swara symbol]</code></li>
            </ul>

            <h3>Table of Contents (Jump to Parva / Kandah)</h3>
            <div class="toc-grid">
                {toc_links_html}
            </div>

            <h3>1. Parva Summary Statistics</h3>
            <table class="summary-table">
                <thead>
                    <tr>
                        <th>Parva (Supersection)</th>
                        <th style="text-align:center;">Kandahs</th>
                        <th>Sama Range</th>
                        <th style="text-align:center;">Total Samas</th>
                        <th style="text-align:center;">Swaras</th>
                        <th style="text-align:center;">Dandas (|)</th>
                        <th style="text-align:center;">Total Granular Rows</th>
                    </tr>
                </thead>
                <tbody>
                    {breakdown_rows_html}
                    <tr style="background: var(--primary-light); font-weight: bold;">
                        <td>Total</td>
                        <td style="text-align:center;">{total_kandahs} Kandahs</td>
                        <td>Sama 1 – 722</td>
                        <td style="text-align:center;">{total_samas}</td>
                        <td style="text-align:center;">{total_swaras:,}</td>
                        <td style="text-align:center;">{total_dandas:,}</td>
                        <td style="text-align:center;">{len(granular_rows):,}</td>
                    </tr>
                </tbody>
            </table>
        </div>

        <!-- Sequential Swara Document Blocks -->
        {parvas_sections_html}
    </div>

    <script>
    function filterSamaDocument() {{
        const q = document.getElementById('searchInput').value.toLowerCase().trim();
        const items = document.querySelectorAll('.sama-item');
        const kandahBlocks = document.querySelectorAll('.kandah-block');
        const parvaSections = document.querySelectorAll('.parva-section');

        if (!q) {{
            items.forEach(it => it.style.display = '');
            kandahBlocks.forEach(b => b.style.display = '');
            parvaSections.forEach(p => p.style.display = '');
            return;
        }}

        items.forEach(it => {{
            const name = (it.getAttribute('data-sama-name') || '').toLowerCase();
            const slNo = (it.getAttribute('data-sl-no') || '').toLowerCase();
            const text = it.textContent.toLowerCase();
            if (name.includes(q) || slNo.includes(q) || text.includes(q)) {{
                it.style.display = '';
            }} else {{
                it.style.display = 'none';
            }}
        }});

        kandahBlocks.forEach(b => {{
            const visibleItems = b.querySelectorAll('.sama-item:not([style*="display: none"])');
            b.style.display = visibleItems.length > 0 ? '' : 'none';
        }});

        parvaSections.forEach(p => {{
            const visibleKandahs = p.querySelectorAll('.kandah-block:not([style*="display: none"])');
            p.style.display = visibleKandahs.length > 0 ? '' : 'none';
        }});
    }}
    </script>
</body>
</html>"""


if __name__ == "__main__":
    extract_devanagari_swaras()
