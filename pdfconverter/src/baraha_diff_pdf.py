"""
Pass 2: Diff Baraha-derived Devanagari against s.pdf reference.

Strategy: extract all Sanskrit text from both sources as character streams
(no line structure), then do a character-level diff to find real content
differences (parser bugs, missing mappings, etc.).

Usage:
  python src/tools/baraha_diff_pdf.py s.pdf pass1_devanagari.txt --output diff_report.txt
"""

import sys
import os
import re
import json
import io
import argparse
import unicodedata
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))
from convert_devanagari_to_malayalam import BRHDevanagariDecoder, clean_accent_spaces
from PyPDF2 import PdfReader


# ── Sanskrit extraction from PDF ────────────────────────────────────────

def is_clean_dev_line(text: str) -> bool:
    """True if line is clean Devanagari content (no BRH leftovers, enough Devanagari chars)."""
    text = text.strip()
    if not text:
        return False
    # Skip page numbers / headers / footers
    if re.search(r'(Page\s+\d+|www\.|vedavms|gmail)', text, re.IGNORECASE):
        return False
    # Any ASCII letter = unconverted BRH glyph → garbage
    if any('a' <= ch <= 'z' or 'A' <= ch <= 'Z' for ch in text):
        return False
    dev = sum(1 for ch in text if 0x0900 <= ord(ch) <= 0x097F)
    # Require at least 8 Devanagari chars
    if dev < 8:
        return False
    return True


def extract_pdf_sanskrit(pdf_path: str) -> str:
    """Extract all Sanskrit from PDF as a single character stream (no spaces/punctuation)."""
    reader = PdfReader(pdf_path)
    all_sans = []
    for page_idx in range(len(reader.pages)):
        raw = reader.pages[page_idx].extract_text() or ''
        dev = BRHDevanagariDecoder.decode(raw)
        dev = clean_accent_spaces(dev)
        for line in dev.split('\n'):
            if is_clean_dev_line(line):
                # Normalize: NFC, strip spaces, keep only Devanagari + Vedic accents + dandas
                s = unicodedata.normalize('NFC', line.strip())
                s = re.sub(r'\s+', '', s)  # remove ALL whitespace
                all_sans.append(s)
    return '\n'.join(all_sans)


def load_pass1_sanskrit(path: str) -> str:
    """Load Pass 1 Devanagari, extract Sanskrit-only content."""
    lines = []
    with io.open(path, 'r', encoding='utf-8') as f:
        for line in f:
            s = line.strip()
            if not s:
                continue
            if not is_clean_dev_line(s):
                continue
            s = unicodedata.normalize('NFC', s)
            s = re.sub(r'\s+', '', s)
            lines.append(s)
    return '\n'.join(lines)


# ── Character-level diff ───────────────────────────────────────────────

def find_differences_simple(ref_text: str, p1_text: str) -> list:
    """
    Find differences by sliding-window matching.
    Since full string diff is O(n²) and these are 100K+ char strings,
    we use a simplification: compare line by line where possible,
    and only flag substantial mismatches.
    
    Returns list of (ref_snippet, p1_snippet, context) tuples.
    """
    ref_lines = ref_text.split('\n')
    p1_lines = p1_text.split('\n')
    
    from difflib import SequenceMatcher
    
    matcher = SequenceMatcher(None, ref_lines, p1_lines, autojunk=False)
    diffs = []
    for tag, ri, rj, pi, pj in matcher.get_opcodes():
        if tag == 'equal':
            continue
        # Collect a few lines of context
        ctx_ref = '\n'.join(ref_lines[max(0, ri - 2):ri])
        ctx_p1 = '\n'.join(p1_lines[max(0, pi - 2):pi])
        snippet_ref = '\n'.join(ref_lines[ri:rj])[:200]
        snippet_p1 = '\n'.join(p1_lines[pi:pj])[:200]
        if tag == 'replace':
            diffs.append(('change', snippet_ref, snippet_p1, ctx_ref, ctx_p1))
        elif tag == 'delete':
            diffs.append(('only_in_ref', snippet_ref, '', ctx_ref, ''))
        elif tag == 'insert':
            diffs.append(('only_in_p1', '', snippet_p1, '', ctx_p1))
    
    return diffs


def extract_correction_pairs(diffs: list) -> list:
    """
    Extract (ref_snippet, p1_snippet) pairs from change entries that represent
    real textual differences (not just structural/section-header changes).
    Returns pairs where both sides have substantial Devanagari content.
    """
    pairs = []
    for tag, ref, p1, ctx_ref, ctx_p1 in diffs:
        if tag != 'change':
            continue
        if not ref or not p1:
            continue
        # Skip structural differences (section numbers, headers)
        ref_dev = sum(1 for ch in ref if 0x0900 <= ord(ch) <= 0x097F)
        p1_dev = sum(1 for ch in p1 if 0x0900 <= ord(ch) <= 0x097F)
        if ref_dev < 5 and p1_dev < 5:
            continue
        pairs.append((ref, p1, ctx_ref, ctx_p1))
    return pairs


def generate_diff_report(diffs: list, max_items: int = 200) -> str:
    """Generate human-readable diff report."""
    lines = []
    lines.append("=" * 70)
    lines.append("PASS 2 DIFF: Baraha-derived Devanagari vs s.pdf reference")
    lines.append("=" * 70)
    lines.append(f"Total differences found: {len(diffs)}")
    lines.append(f"Showing first {min(max_items, len(diffs))}")
    lines.append("")
    
    shown = 0
    for tag, ref, p1, ctx_ref, ctx_p1 in diffs:
        if shown >= max_items:
            break
        shown += 1
        lines.append(f"[{'CHANGE' if tag == 'change' else 'PDF ONLY' if tag == 'only_in_ref' else 'PASS1 ONLY'} #{shown}]")
        if ctx_ref or ctx_p1:
            lines.append(f"  ...context (ref):  {ctx_ref[:80]}")
            lines.append(f"  ...context (p1):   {ctx_p1[:80]}")
        if ref:
            lines.append(f"  PDF ref:   {ref[:150]}")
        if p1:
            lines.append(f"  Pass 1:    {p1[:150]}")
        lines.append("")
    
    lines.append("-" * 70)
    changes = sum(1 for d in diffs if d[0] == 'change')
    ref_only = sum(1 for d in diffs if d[0] == 'only_in_ref')
    p1_only = sum(1 for d in diffs if d[0] == 'only_in_p1')
    lines.append(f"Summary: {changes} changes, {ref_only} only in PDF, {p1_only} only in Pass1")
    lines.append("")
    return '\n'.join(lines)


# ── Main ────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Diff Baraha Devanagari vs PDF reference")
    parser.add_argument("pdf", help="Path to reference PDF (s.pdf)")
    parser.add_argument("devanagari", help="Path to Pass 1 Devanagari text")
    parser.add_argument("--output", "-o", default="diff_report.txt", help="Output diff report path")
    parser.add_argument("--max", type=int, default=200, help="Max diffs to show")
    args = parser.parse_args()

    if not os.path.exists(args.pdf):
        print(f"Error: PDF not found: {args.pdf}", file=sys.stderr)
        sys.exit(1)
    if not os.path.exists(args.devanagari):
        print(f"Error: Devanagari text not found: {args.devanagari}", file=sys.stderr)
        sys.exit(1)

    print("Extracting Sanskrit from PDF...")
    ref = extract_pdf_sanskrit(args.pdf)
    print(f"  Extracted {len(ref)} chars")

    print("Loading Pass 1 Devanagari...")
    p1 = load_pass1_sanskrit(args.devanagari)
    print(f"  Loaded {len(p1)} chars")

    print("Finding differences...")
    diffs = find_differences_simple(ref, p1)

    print("Generating report...")
    report = generate_diff_report(diffs, max_items=args.max)
    with io.open(args.output, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"  Saved: {args.output}")

    # Generate corrections JSON
    pairs = extract_correction_pairs(diffs)
    corrections = []
    for ref_snip, p1_snip, ctx_ref, ctx_p1 in pairs:
        corrections.append({
            "pdf_reference": ref_snip[:200],
            "pass1": p1_snip[:200],
            "context_ref": ctx_ref[:100],
            "context_p1": ctx_p1[:100]
        })
    corr_path = args.output.replace('.txt', '_corrections.json')
    with io.open(corr_path, 'w', encoding='utf-8') as f:
        json.dump(corrections, f, ensure_ascii=False, indent=2)
    print(f"  Saved corrections: {corr_path}")

    changes = sum(1 for d in diffs if d[0] == 'change')
    ref_only = sum(1 for d in diffs if d[0] == 'only_in_ref')
    p1_only = sum(1 for d in diffs if d[0] == 'only_in_p1')
    print(f"\nSummary: {changes} changes, {ref_only} only in PDF, {p1_only} only in Pass1")


if __name__ == '__main__':
    main()
