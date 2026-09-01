"""Merge validated modifier candidate files into Samam_Malayalam_Unicode.txt.

For each subsection in any candidate .txt file:
  1. Strips modifiers from the candidate to get base + Grantha text.
  2. Verifies that base + Grantha exactly matches the baseline in the master file.
  3. If validation passes, replaces the subsection body in the master file.

Writes a merge report to stage_output/merge_report.txt.
"""

import re
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

REPO = Path(__file__).resolve().parents[2]
MASTER = REPO / "data/input/Malayalam/Samam_Malayalam_Unicode.txt"
CANDIDATES_DIR = REPO / "Malayalam_JSV/stage_output/candidates"
REPORT = REPO / "Malayalam_JSV/stage_output/merge_report.txt"

# Canonical modifier token pattern (A), (B), (B1), (C), (D), (D1), (D2), (I), (J), (K), etc.
MODIFIER_RE = re.compile(r"\(([A-Z][0-9_]?)\)")
FOOTNOTE_RE = re.compile(r"\(s\d+\)")

SUBSECTION_RE = re.compile(
    r"(#Start of Mantra Sets -- (subsection_\d+) ## DO NOT EDIT\s*\n)"
    r"(.*?)"
    r"(\n#End of Mantra Sets -- \2 ## DO NOT EDIT)",
    re.DOTALL,
)


def strip_modifiers(text: str) -> str:
    """Remove modifier tokens, footnotes, phrasing marks, and extra whitespace for comparison."""
    t = MODIFIER_RE.sub("", text)
    t = FOOTNOTE_RE.sub("", t)
    # Also strip inline phrasing marks for base comparison
    t = re.sub(r"[_.,]", "", t)
    t = re.sub(r" +", " ", t)
    t = re.sub(r"\n +", "\n", t)
    t = re.sub(r" +\n", "\n", t)
    return t.strip()


def parse_candidate(path: Path) -> dict:
    """Return {subsection_id: body_text} from a candidate file."""
    text = path.read_text(encoding="utf-8")
    results = {}
    for m in SUBSECTION_RE.finditer(text):
        results[m.group(2)] = m.group(3).strip()
    return results


def main():
    if not MASTER.exists():
        print(f"ERROR: master file not found: {MASTER}")
        sys.exit(1)

    master_text = MASTER.read_text(encoding="utf-8")
    master_bodies = {}
    for m in SUBSECTION_RE.finditer(master_text):
        master_bodies[m.group(2)] = m.group(3).strip()

    candidates = sorted(CANDIDATES_DIR.glob("*.txt"))
    if not candidates:
        print("No candidate files found in", CANDIDATES_DIR)
        sys.exit(0)

    report_lines = []
    merged = 0
    skipped = 0
    errors = 0
    patched_text = master_text

    for cand_path in candidates:
        print(f"\nProcessing {cand_path.name} ...")
        candidate = parse_candidate(cand_path)

        for sub_id, cand_body in sorted(candidate.items(),
                                        key=lambda x: int(x[0].split("_")[1])):
            if sub_id not in master_bodies:
                report_lines.append(f"SKIP {sub_id}: not in master file")
                skipped += 1
                continue

            cand_stripped = strip_modifiers(cand_body)
            master_stripped = strip_modifiers(master_bodies[sub_id])

            if cand_stripped != master_stripped:
                report_lines.append(
                    f"ERROR {sub_id}: base/Grantha mismatch\n"
                    f"  CAND  : {cand_stripped[:120]!r}\n"
                    f"  MASTER: {master_stripped[:120]!r}"
                )
                errors += 1
                continue

            # Check if candidate has modifications
            if cand_body == master_bodies[sub_id]:
                report_lines.append(f"SKIP {sub_id}: no changes (identical to master)")
                skipped += 1
                continue

            def replacer(m, sid=sub_id, body=cand_body):
                if m.group(2) == sid:
                    return m.group(1) + body + m.group(4)
                return m.group(0)

            new_text = SUBSECTION_RE.sub(replacer, patched_text)
            if new_text == patched_text:
                report_lines.append(f"SKIP {sub_id}: no change after patch")
                skipped += 1
                continue

            new_mods = MODIFIER_RE.findall(cand_body)
            master_mods = MODIFIER_RE.findall(master_bodies[sub_id])

            patched_text = new_text
            master_bodies[sub_id] = cand_body
            report_lines.append(
                f"MERGE {sub_id}: +{len(new_mods)} modifiers "
                f"(was {len(master_mods)})"
            )
            merged += 1

    MASTER.write_text(patched_text, encoding="utf-8")

    report = "\n".join([
        "=" * 70,
        "MERGE REPORT",
        f"  Candidates processed : {len(candidates)}",
        f"  Subsections merged   : {merged}",
        f"  Subsections skipped  : {skipped}",
        f"  Validation errors    : {errors}",
        "=" * 70,
        "",
    ] + report_lines)

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
