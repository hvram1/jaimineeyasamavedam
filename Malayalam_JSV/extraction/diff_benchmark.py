"""Benchmark diff tool for comparing candidate extraction with ground truth."""

import sys
import re
import difflib
from pathlib import Path

# Ensure UTF-8 output on Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


def parse_mantra_sets(file_path: Path) -> dict:
    """Extract mantra sets per subsection."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    results = {}
    pattern = re.compile(
        r"#Start of Mantra Sets -- (subsection_\d+) ## DO NOT EDIT\s*\n(.*?)\n#End of Mantra Sets -- \1 ## DO NOT EDIT",
        re.DOTALL
    )
    for match in pattern.finditer(content):
        sub_id = match.group(1)
        mantra = match.group(2).strip()
        results[sub_id] = mantra
    return results


def display_diff(cand_path: Path, ref_path: Path):
    cand_sets = parse_mantra_sets(cand_path)
    ref_sets = parse_mantra_sets(ref_path)

    print(f"Comparing:")
    print(f"  Candidate : {cand_path.name}")
    print(f"  Reference : {ref_path.name}\n")
    print("=" * 80)

    total_subs = len(ref_sets)
    matched_subs = 0

    for sub_id, ref_text in ref_sets.items():
        cand_text = cand_sets.get(sub_id, "")
        if not cand_text:
            print(f"[{sub_id}] MISSING in candidate\n")
            continue

        if cand_text == ref_text:
            print(f"[{sub_id}] MATCH [100%]\n")
            matched_subs += 1
        else:
            print(f"[{sub_id}] DIFF:")
            cand_lines = cand_text.splitlines(keepends=True)
            ref_lines = ref_text.splitlines(keepends=True)
            diff = list(difflib.unified_diff(
                ref_lines,
                cand_lines,
                fromfile="Reference",
                tofile="Candidate",
                lineterm=""
            ))
            for line in diff:
                print(f"  {line}")
            print()

    print("=" * 80)
    print(f"Summary: {matched_subs}/{total_subs} subsections matched exactly.")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python -X utf8 diff_benchmark.py <candidate.txt> <reference.txt>")
        sys.exit(1)

    display_diff(Path(sys.argv[1]), Path(sys.argv[2]))
