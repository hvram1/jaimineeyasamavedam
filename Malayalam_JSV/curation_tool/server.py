"""
Jaimineeya Sama Veda - Interactive Visual Curation & Benchmarking Server
Serves a split-view curation tool linking manuscript scans with Unicode text.
"""

import http.server
import json
import os
import re
import socketserver
import subprocess
import sys
import urllib.parse
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_FILE = BASE_DIR / "data" / "input" / "Malayalam" / "Samam_Malayalam_Unicode.txt"
JSON_FILE = BASE_DIR / "Malayalam_JSV" / "malayalam" / "Samam_Malayalam_json.json"
SCANS_DIR = BASE_DIR / "Malayalam_JSV" / "scans"
PDF_PATH = Path(r"G:\My Drive\Jaimineeya Sama Veda Archive\Archives\JSV Samhita Malayalam.pdf")
STATIC_DIR = Path(__file__).resolve().parent / "static"

# Ensure scans directory exists
SCANS_DIR.mkdir(parents=True, exist_ok=True)

# Grantha Swara regex & Modifiers
SWARA_CHARS = r"[\U00011300-\U0001137F]"
MOD_REGEX = re.compile(r"\((?:[CDGBHE]|A1?)\)")

SUPERSECTION_INFO = [
    (1, 12, "SuperSection 1: Agneyam (ആഗ്നേയം)", "SS1"),
    (13, 25, "SuperSection 2: Tadva / Aindram (തദ്വാ)", "SS2"),
    (26, 34, "SuperSection 3: Bruhati (ബൃഹതീ)", "SS3"),
    (35, 41, "SuperSection 4: Asaavi (അസാവി)", "SS4"),
    (42, 52, "SuperSection 5: Aindram (ഐന്ദ്രം)", "SS5"),
    (53, 64, "SuperSection 6: Pavamanam (പവമാനം)", "SS6"),
]

PAGE_ESTIMATES = {
    # SS1: Agneyam
    "section_1": 3,
    "section_2": 6,
    "section_3": 9,
    "section_4": 13,
    "section_5": 19,
    "section_6": 25,
    "section_7": 27,
    "section_8": 29,
    "section_9": 31,
    "section_10": 33,
    "section_11": 35,
    "section_12": 37,
    # SS2: Tadva
    "section_13": 39,
    # SS3: Bruhati
    "section_26": 84,
    # SS4: Asaavi
    "section_35": 131,
    # SS5: Aindram
    "section_42": 161,
    # SS6: Pavamanam
    "section_53": 211,
}


def get_supersection_meta(sec_id_or_num):
    if isinstance(sec_id_or_num, str):
        m = re.search(r"\d+", sec_id_or_num)
        snum = int(m.group(0)) if m else 1
    else:
        snum = int(sec_id_or_num)
    for start, end, title, tag in SUPERSECTION_INFO:
        if start <= snum <= end:
            return {"title": title, "tag": tag, "id": f"supersection_{tag}"}
    return {"title": "General", "tag": "GEN", "id": "supersection_0"}


def parse_master_file():
    """Parses Samam_Malayalam_Unicode.txt into structured sections, subsections, and samams."""
    if not DATA_FILE.exists():
        return {"error": "Master file not found"}

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()

    sections = []
    current_sec = None
    current_subsec = None
    in_mantra = False
    mantra_lines = []

    sec_counter = 0

    for idx, line in enumerate(lines):
        line_str = line.strip()

        # Section marker
        m_sec_start = re.match(r"^# Start of Section Title -- (section_\d+)", line_str)
        if m_sec_start:
            sec_id = m_sec_start.group(1)
            sec_num = int(sec_id.split("_")[1])
            sec_counter += 1
            ss_meta = get_supersection_meta(sec_num)
            current_sec = {
                "id": sec_id,
                "number": sec_num,
                "title": "",
                "supersection": ss_meta["title"],
                "supersection_tag": ss_meta["tag"],
                "subsections": [],
                "page": PAGE_ESTIMATES.get(sec_id, 4 + sec_counter * 3)
            }
            sections.append(current_sec)
            continue

        if current_sec and not current_sec["title"] and not line_str.startswith("#"):
            current_sec["title"] = line_str
            continue

        # Subsection marker
        m_subsec_start = re.match(r"^# Start of SubSection Title -- (subsection_\d+)", line_str)
        if m_subsec_start:
            subsec_id = m_subsec_start.group(1)
            subsec_num = int(subsec_id.split("_")[1])
            current_subsec = {
                "id": subsec_id,
                "number": subsec_num,
                "title": "",
                "samams": [],
                "line_start": idx + 1
            }
            if current_sec is None:
                ss_meta = get_supersection_meta(1)
                current_sec = {
                    "id": "section_1",
                    "number": 1,
                    "title": "പ്രഥമ ഖണ്ഡഃ",
                    "supersection": ss_meta["title"],
                    "supersection_tag": ss_meta["tag"],
                    "subsections": [],
                    "page": 4
                }
                sections.append(current_sec)
            current_sec["subsections"].append(current_subsec)
            continue

        if current_subsec and not current_subsec["title"] and not line_str.startswith("#"):
            current_subsec["title"] = line_str
            continue

        # Mantra sets
        if "#Start of Mantra Sets" in line_str:
            in_mantra = True
            mantra_lines = []
            continue

        if "#End of Mantra Sets" in line_str:
            in_mantra = False
            full_text = " ".join(mantra_lines).strip()
            if current_subsec:
                current_subsec["raw_text"] = full_text
                # Split into individual samams by danda numbering (e.g. ॥१॥, ॥२॥)
                samam_tokens = re.split(r"(॥[०-९\d]+॥)", full_text)
                samams = []
                cur_samam_text = ""
                samam_num = 1
                for tok in samam_tokens:
                    if re.match(r"^॥[०-९\d]+॥$", tok):
                        cur_samam_text += tok
                        samams.append({
                            "num": samam_num,
                            "danda": tok,
                            "text": cur_samam_text.strip(),
                            "id": f"{current_subsec['id']}_s{samam_num}"
                        })
                        samam_num += 1
                        cur_samam_text = ""
                    else:
                        cur_samam_text += tok
                if cur_samam_text.strip():
                    samams.append({
                        "num": samam_num,
                        "danda": "",
                        "text": cur_samam_text.strip(),
                        "id": f"{current_subsec['id']}_s{samam_num}"
                    })
                current_subsec["samams"] = samams
            continue

        if in_mantra:
            mantra_lines.append(line_str)

    return {"sections": sections}


def save_samam_edit(subsec_id, samam_num, new_text):
    """Saves edited Samam text back into the master file with safety validation."""
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # Locate subsection block
    subsec_pattern = re.compile(
        rf"(#Start of Mantra Sets -- {subsec_id} ## DO NOT EDIT\n)(.*?)(\n#End of Mantra Sets -- {subsec_id} ## DO NOT EDIT)",
        re.DOTALL
    )
    match = subsec_pattern.search(content)
    if not match:
        return {"success": False, "error": f"Subsection {subsec_id} not found in master file"}

    header, raw_text, footer = match.groups()
    samam_tokens = re.split(r"(॥[०-९\d]+॥)", raw_text)

    # Reassemble with modified samam
    new_samams = []
    cur_text = ""
    curr_num = 1
    for tok in samam_tokens:
        if re.match(r"^॥[०-९\d]+॥$", tok):
            cur_text += tok
            if curr_num == samam_num:
                new_samams.append(new_text.strip())
            else:
                new_samams.append(cur_text.strip())
            curr_num += 1
            cur_text = ""
        else:
            cur_text += tok

    if cur_text.strip() and curr_num == samam_num:
        new_samams.append(new_text.strip())
    elif cur_text.strip():
        new_samams.append(cur_text.strip())

    updated_raw = " ".join(new_samams)
    updated_content = content[:match.start()] + header + updated_raw + footer + content[match.end():]

    # Write to temp file and validate
    temp_file = BASE_DIR / "Malayalam_JSV" / "temp_validate.txt"
    with open(temp_file, "w", encoding="utf-8") as f:
        f.write(updated_content)

    # Validate
    val_script = BASE_DIR / "Malayalam_JSV" / "extraction" / "validate_modifiers.py"
    res = subprocess.run(
        [sys.executable, "-X", "utf8", str(val_script), str(temp_file), str(temp_file)],
        capture_output=True,
        text=True
    )

    if res.returncode != 0:
        if temp_file.exists():
            temp_file.unlink()
        return {"success": False, "error": f"Validation failed:\n{res.stderr or res.stdout}"}

    # If valid, write to master file
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        f.write(updated_content)

    if temp_file.exists():
        temp_file.unlink()

    # Trigger background JSON rebuild
    gen_script = BASE_DIR / "src" / "generate_json.py"
    subprocess.Popen([sys.executable, "-X", "utf8", str(gen_script), str(DATA_FILE), "--output", str(JSON_FILE)])

    return {"success": True, "message": "Updated and validated successfully"}


def ensure_page_scan(page_num):
    """Ensures 300 DPI scan image exists for page_num, extracting from PDF if needed."""
    page_img_path = SCANS_DIR / f"page_{page_num:03d}.png"
    if page_img_path.exists():
        return page_img_path

    if not PDF_PATH.exists():
        return None

    try:
        import pypdfium2 as pdfium
        pdf = pdfium.PdfDocument(str(PDF_PATH))
        if 0 <= page_num - 1 < len(pdf):
            page = pdf.get_page(page_num - 1)
            img = page.render(scale=300 / 72).to_pil()
            img.save(page_img_path)
            return page_img_path
    except Exception as e:
        print(f"Error extracting page {page_num}: {e}")

    return None


class CurationHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(STATIC_DIR), **kwargs)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/api/samams":
            data = parse_master_file()
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))
            return

        if path.startswith("/api/page/"):
            try:
                page_num = int(path.split("/api/page/")[1].split("?")[0].replace(".png", ""))
                img_path = ensure_page_scan(page_num)
                if img_path and img_path.exists():
                    self.send_response(200)
                    self.send_header("Content-Type", "image/png")
                    self.send_header("Cache-Control", "public, max-age=86400")
                    self.end_headers()
                    with open(img_path, "rb") as f:
                        self.wfile.write(f.read())
                    return
                else:
                    self.send_error(404, "Page scan not found")
                    return
            except Exception as e:
                self.send_error(500, str(e))
                return

        if path.startswith("/fonts/"):
            font_name = os.path.basename(path.split("?")[0])
            font_path = BASE_DIR / "fonts" / font_name
            if not font_path.exists():
                font_path = BASE_DIR / "docs" / "malayalam" / "fonts" / font_name
            if font_path.exists():
                self.send_response(200)
                if font_name.endswith(".woff2"):
                    self.send_header("Content-Type", "font/woff2")
                elif font_name.endswith(".woff"):
                    self.send_header("Content-Type", "font/woff")
                elif font_name.endswith(".otf"):
                    self.send_header("Content-Type", "font/otf")
                else:
                    self.send_header("Content-Type", "font/ttf")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Cache-Control", "no-cache, must-revalidate")
                self.end_headers()
                with open(font_path, "rb") as f:
                    self.wfile.write(f.read())
                return
            else:
                self.send_error(404, "Font not found")
                return

        return super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/api/save":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            req_data = json.loads(body.decode("utf-8"))

            subsec_id = req_data.get("subsec_id")
            samam_num = int(req_data.get("samam_num", 1))
            new_text = req_data.get("new_text", "")

            result = save_samam_edit(subsec_id, samam_num, new_text)

            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(result, ensure_ascii=False).encode("utf-8"))
            return

        self.send_error(404, "Endpoint not found")


def run_server(port=8080):
    STATIC_DIR.mkdir(parents=True, exist_ok=True)
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", port), CurationHandler) as httpd:
        print(f"==================================================")
        print(f" JSV Visual Curation Server running at:")
        print(f" http://localhost:{port}/")
        print(f"==================================================")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server.")


if __name__ == "__main__":
    port = 8080
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        port = int(sys.argv[1])
    run_server(port)
