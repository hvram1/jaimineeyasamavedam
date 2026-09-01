"""One-time migration: convert Samam numerals in Samam_Malayalam_Unicode.txt
from Devanagari digits (॥१॥) to ASCII digits (॥1॥).

Uses the canonical converter from src/malayalam/ml_text.py so future
regenerations of the input file stay consistent.

Guardrails:
  1. Only digit characters inside ॥N॥ markers may change.
  2. Marker count must be preserved.
  3. Idempotent: re-running on a converted file is a no-op.

Writes a report to stage_output/numeral_migration_report.txt.
"""

import os
import re
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from malayalam.ml_text import SAMAM_NUMERAL_RE, normalize_malayalam_samam_numerals

MASTER = REPO / "data/input/Malayalam/Samam_Malayalam_Unicode.txt"
REPORT = REPO / "Malayalam_JSV/stage_output/numeral_migration_report.txt"

DEVA_DIGIT_RE = re.compile(r"[०-९]")


def main():
    if not MASTER.exists():
        print(f"ERROR: master file not found: {MASTER}")
        sys.exit(1)

    original = MASTER.read_text(encoding="utf-8")
    converted = normalize_malayalam_samam_numerals(original)

    markers_before = len(SAMAM_NUMERAL_RE.findall(original))
    markers_after = len(SAMAM_NUMERAL_RE.findall(converted))
    deva_before = len(DEVA_DIGIT_RE.findall(original))
    deva_after = len(DEVA_DIGIT_RE.findall(converted))

    # Guardrail 1: strip all digits (both scripts) -> remainder must be identical
    def strip_digits(t: str) -> str:
        t = SAMAM_NUMERAL_RE.sub(lambda m: m.group(1) + m.group(3), t)
        return DEVA_DIGIT_RE.sub("", t)

    base_preserved = strip_digits(original) == strip_digits(converted)

    # Guardrail 3: idempotency
    idempotent = normalize_malayalam_samam_numerals(converted) == converted

    errors = []
    if markers_before != markers_after:
        errors.append(f"marker count changed: {markers_before} -> {markers_after}")
    if not base_preserved:
        errors.append("non-digit characters were modified")
    if not idempotent:
        errors.append("conversion is not idempotent")

    lines = [
        "=" * 70,
        "SAMAM NUMERAL MIGRATION REPORT",
        "=" * 70,
        f"File                      : {MASTER}",
        f"File chars                : {len(original):,}",
        f"Danda-numeral markers     : {markers_before} (after: {markers_after})",
        f"Devanagari digit chars    : {deva_before} (after: {deva_after})",
        f"Non-digit text preserved  : {'YES' if base_preserved else 'NO'}",
        f"Idempotent                : {'YES' if idempotent else 'NO'}",
    ]

    if errors:
        lines.append(f"RESULT                    : FAILED — {errors}")
        lines.append("Master file NOT modified.")
        REPORT.parent.mkdir(parents=True, exist_ok=True)
        REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print("\n".join(lines))
        sys.exit(2)

    already_done = deva_before == 0
    if already_done:
        lines.append("RESULT                    : NO-OP (file already ASCII)")
    else:
        tmp = MASTER.with_suffix(".txt.tmp")
        tmp.write_text(converted, encoding="utf-8", newline="")
        os.replace(tmp, MASTER)
        lines.append("RESULT                    : SUCCESS — master file updated")

    lines.append("=" * 70)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
