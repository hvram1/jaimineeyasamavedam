"""Deterministic validator guardrail for Malayalam swara modifier extraction.

Ensures that:
1. Base Malayalam text and syllables match baseline 100% (zero hallucination).
2. Grantha swara codes match baseline 100%.
3. All inserted modifiers belong to the canonical modifier lexicon.
"""

import sys
import re
import unicodedata
from pathlib import Path
from typing import Dict, List, Tuple

# Ensure UTF-8 output on Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

# Canonical swara modifiers and inline phrasing marks per spec.md
VALID_MODIFIERS = {
    "A", "A1", "A_1", "B", "B1", "B_1", "C", "D", "D1", "D_1", "D2", "D_2",
    "E", "F", "G", "H", "I", "J", "K", "L",
    "\\", "|", "^", "·", "⨯", "x", "X", "¯", "⫽", "═", "✓", "⋀", "↗"
}

# Modifiers regex pattern: (A), (C), (H), (G), (B1), (D1), (D2), (I), (J), (K), etc.
MODIFIER_TOKEN_RE = re.compile(r"\(([A-Z][0-9_]?)\)")
FOOTNOTE_TOKEN_RE = re.compile(r"\(s\d+\)")
INLINE_MARKS_RE = re.compile(r"[_.,\uE001-\uE00A\u00B7]")
GRANTHA_MARKER_RE = re.compile(r"\(([\u11300-\u1137F\u0D36\u0D37\u0D2A\u0D4D\u0D32\u0D24\u0D4D\u0D30\u0D15\u0D4D\u0D30a-zA-Z0-9\u0900-\u097F\uE000-\uE0FF]+)\)")

# Normalization mapping for PUA / legacy chars to canonical Unicode
PUA_TO_CANONICAL = {
    "\uE010": "\u0D36\u0D3E",      # ശ + ാ
    "\uE020": "\u0D2A\u0D4D\u0D32",  # പ്ല
    "\uE021": "\u0D2A\u0D4D\u0D32\u0D3E", # പ്ലാ
    "\uE022": "\u0D2A\u0D4D\u0D32\u0D3F", # പ്ലി
}


def normalize_swaras(text: str) -> str:
    """Normalize Malayalam Grantha vs Malayalam native swara representations."""
    # Convert Malayalam swara markers to Grantha if needed or vice versa
    t = text
    for pua, repl in PUA_TO_CANONICAL.items():
        t = t.replace(pua, repl)
    # Normalize (ശ) <-> (𑌶), (ശാ) <-> (𑌶𑌾)
    t = t.replace("\u0D36", "\u11336").replace("\u11336", "\u0D36")
    return t


def normalize_text_for_comparison(text: str) -> str:
    """Strip modifiers, inline marks, and extra spaces to check base text equality."""
    t = text
    # Remove footnotes
    t = FOOTNOTE_TOKEN_RE.sub("", t)
    # Remove uppercase modifiers in parens e.g. (C), (H), (G), (A), (A1), (B1), (D1), (D2), (I), (J), (K), (D), (L)
    t = re.sub(r"\(([A-Z][0-9_]?)\)", "", t)
    # Remove inline phrasing marks: _, ., ,
    t = re.sub(r"[_.,]", "", t)
    # Normalize swaras & PUA
    t = normalize_swaras(t)
    # Normalize whitespace
    t = re.sub(r"\s+", " ", t).strip()
    return t


def validate_mantra_block(candidate_lines: List[str], baseline_lines: List[str]) -> Tuple[bool, List[str]]:
    """Validate candidate mantra lines against baseline lines."""
    errors = []
    
    cand_norm = [normalize_text_for_comparison(l) for l in candidate_lines if l.strip()]
    base_norm = [normalize_text_for_comparison(l) for l in baseline_lines if l.strip()]
    
    cand_str = " ".join(cand_norm)
    base_str = " ".join(base_norm)
    
    if cand_str != base_str:
        errors.append(
            f"Base text mismatch:\n"
            f"  Candidate : {cand_str}\n"
            f"  Baseline  : {base_str}"
        )
        return False, errors

    # Check that all modifiers in candidate are valid
    for line_idx, line in enumerate(candidate_lines):
        for match in MODIFIER_TOKEN_RE.finditer(line):
            mod = match.group(1)
            if mod not in VALID_MODIFIERS:
                errors.append(f"Line {line_idx+1}: Unknown modifier marker '({mod})'")

    is_valid = len(errors) == 0
    return is_valid, errors


def parse_sections(file_path: Path) -> Dict[str, Dict[str, str]]:
    """Parse text file into structured subsections and mantra sets."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    subsections = {}
    sub_blocks = re.findall(
        r"# Start of SubSection Title -- (subsection_\d+) ## DO NOT EDIT\s*\n(.*?)\n# End of SubSection Title -- \1 ## DO NOT EDIT.*?"
        r"#Start of Mantra Sets -- \1 ## DO NOT EDIT\s*\n(.*?)\n#End of Mantra Sets -- \1 ## DO NOT EDIT",
        content,
        re.DOTALL
    )

    for sub_id, title, mantra in sub_blocks:
        subsections[sub_id] = {
            "title": title.strip(),
            "mantra": mantra.strip()
        }

    return subsections


def validate_files(candidate_path: Path, baseline_path: Path) -> Tuple[bool, Dict]:
    """Compare candidate subsections against baseline file."""
    cand_subs = parse_sections(candidate_path)
    base_subs = parse_sections(baseline_path)

    report = {"passed": True, "details": {}}

    for sub_id, cand_data in cand_subs.items():
        if sub_id not in base_subs:
            report["passed"] = False
            report["details"][sub_id] = {"status": "EXTRA_SUBSECTION_NOT_IN_BASELINE"}
            continue

        base_data = base_subs[sub_id]
        cand_lines = cand_data["mantra"].splitlines()
        base_lines = base_data["mantra"].splitlines()

        is_valid, errors = validate_mantra_block(cand_lines, base_lines)
        if not is_valid:
            report["passed"] = False
            report["details"][sub_id] = {
                "status": "FAIL",
                "errors": errors
            }
        else:
            report["details"][sub_id] = {"status": "PASS"}

    return report["passed"], report


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python validate_modifiers.py <candidate.txt> <baseline.txt>")
        sys.exit(1)

    cand_file = Path(sys.argv[1])
    base_file = Path(sys.argv[2])

    passed, res = validate_files(cand_file, base_file)
    print(f"Validation {'PASSED [OK]' if passed else 'FAILED [ERRORS]'}")
    for sub, info in res["details"].items():
        print(f"  {sub}: {info['status']}")
        if "errors" in info:
            for err in info["errors"]:
                print(f"    - {err}")
