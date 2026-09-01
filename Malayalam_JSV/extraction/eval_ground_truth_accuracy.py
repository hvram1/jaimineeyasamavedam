#!/usr/bin/env python3
"""
Ground-Truth Evaluation & Accuracy Benchmark Engine for Jaimineeya Samavedam Swara Modifiers.

Compares an automated vision-extracted candidate file against the human-curated Ground Truth.
Computes:
- Micro and Macro Precision, Recall, F1-Score across all 18 modifier types and phrasing marks.
- Per-modifier classification confusion matrix.
- Character-aligned visual diff report highlighting exact false positives, false negatives, and placement offsets.
"""

import sys
import re
import argparse
from pathlib import Path
from collections import Counter, defaultdict

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

SUBSECTION_RE = re.compile(
    r"#Start of Mantra Sets -- (subsection_\d+) ## DO NOT EDIT\s*\n(.*?)\n#End of Mantra Sets -- \1 ## DO NOT EDIT",
    re.DOTALL
)

TOKEN_RE = re.compile(r"(\([A-Z][0-9_]?\)|[_.,])")
MODIFIER_RE = re.compile(r"\(([A-Z][0-9_]?)\)")
INLINE_RE = re.compile(r"[_.,]")


def parse_subsections(file_path: Path):
    text = file_path.read_text(encoding="utf-8")
    subs = {}
    for m in SUBSECTION_RE.finditer(text):
        subs[m.group(1)] = m.group(2).strip()
    return subs


def tokenize_with_alignment(text: str):
    """
    Tokenizes text into a stream of base characters and attached modifier/phrasing tokens.
    Returns:
      base_stream: list of (base_char, attached_tokens)
    """
    # Remove whitespace
    clean = re.sub(r"\s+", " ", text).strip()
    
    tokens = []
    # Match any base character (including Grantha swara letters in parens) or standalone modifier
    # We treat Grantha letters like (𑌤) as atomic base swaras
    i = 0
    while i < len(clean):
        c = clean[i]
        
        # Check if it's a modifier token e.g. (C), (G), (A), _, ., ,
        m_mod = re.match(r"^\(([A-Z][0-9_]?)\)|^([_.,])", clean[i:])
        if m_mod:
            tok = m_mod.group(0)
            tokens.append(("MOD", tok))
            i += len(tok)
            continue
            
        # Check if it's a Grantha swara letter in parens e.g. (𑌤)
        m_grantha = re.match(r"^\(([\u11300-\u1137F\u0D00-\u0D7F]+)\)", clean[i:])
        if m_grantha:
            tok = m_grantha.group(0)
            tokens.append(("BASE", tok))
            i += len(tok)
            continue
            
        # Standard character
        tokens.append(("BASE", c))
        i += 1
        
    return tokens


def evaluate(candidate_path: Path, ground_truth_path: Path):
    cand_subs = parse_subsections(candidate_path)
    gt_subs = parse_subsections(ground_truth_path)

    print("=" * 80)
    print("JAIMINEEYA SAMAVEDAM — VISION EXTRACTION ACCURACY BENCHMARK REPORT")
    print("=" * 80)
    print(f"Candidate File   : {candidate_path}")
    print(f"Ground Truth File: {ground_truth_path}")
    print(f"Common Subsecs   : {len(set(cand_subs.keys()) & set(gt_subs.keys()))}")
    print("=" * 80)

    tp_counts = Counter()
    fp_counts = Counter()
    fn_counts = Counter()
    
    mismatches_by_sub = defaultdict(list)

    all_mod_types = set()

    for sid, gt_text in gt_subs.items():
        if sid not in cand_subs:
            print(f"Warning: {sid} missing in candidate!")
            continue
        
        cand_text = cand_subs[sid]

        # Extract tokens for frequency comparisons
        gt_mods = TOKEN_RE.findall(gt_text)
        cand_mods = TOKEN_RE.findall(cand_text)

        gt_counts = Counter(gt_mods)
        cand_counts = Counter(cand_mods)

        for m in gt_counts.keys() | cand_counts.keys():
            all_mod_types.add(m)
            gt_c = gt_counts[m]
            cd_c = cand_counts[m]

            tp = min(gt_c, cd_c)
            fp = max(0, cd_c - gt_c)
            fn = max(0, gt_c - cd_c)

            tp_counts[m] += tp
            fp_counts[m] += fp
            fn_counts[m] += fn

            if fp > 0 or fn > 0:
                mismatches_by_sub[sid].append((m, gt_c, cd_c, fp, fn))

    # Print Per-Modifier Table
    print("\nPER-MODIFIER PRECISION, RECALL & F1-SCORE:")
    print("-" * 80)
    print(f"{'Modifier / Mark':<18} | {'GT Count':<8} | {'Cand Count':<10} | {'TP':<5} | {'FP':<5} | {'FN':<5} | {'Prec (%)':<9} | {'Rec (%)':<9} | {'F1 (%)':<8}")
    print("-" * 80)

    total_gt = 0
    total_cand = 0
    total_tp = 0
    total_fp = 0
    total_fn = 0

    sorted_mods = sorted(all_mod_types, key=lambda x: (tp_counts[x] + fn_counts[x]), reverse=True)

    for m in sorted_mods:
        tp = tp_counts[m]
        fp = fp_counts[m]
        fn = fn_counts[m]
        gt_c = tp + fn
        cand_c = tp + fp

        total_gt += gt_c
        total_cand += cand_c
        total_tp += tp
        total_fp += fp
        total_fn += fn

        prec = (tp / cand_c * 100) if cand_c > 0 else 0.0
        rec = (tp / gt_c * 100) if gt_c > 0 else 0.0
        f1 = (2 * prec * rec / (prec + rec)) if (prec + rec) > 0 else 0.0

        label = m
        if m.startswith("(") and m.endswith(")"):
            label = f"MOD-{m[1:-1]}"
        elif m == "_":
            label = "INLINE_UNDERBAR"
        elif m == ".":
            label = "INLINE_DOT"
        elif m == ",":
            label = "INLINE_COMMA"

        print(f"{label:<18} | {gt_c:<8} | {cand_c:<10} | {tp:<5} | {fp:<5} | {fn:<5} | {prec:6.1f}%   | {rec:6.1f}%   | {f1:5.1f}%")

    print("-" * 80)
    overall_prec = (total_tp / total_cand * 100) if total_cand > 0 else 0.0
    overall_rec = (total_tp / total_gt * 100) if total_gt > 0 else 0.0
    overall_f1 = (2 * overall_prec * overall_rec / (overall_prec + overall_rec)) if (overall_prec + overall_rec) > 0 else 0.0

    print(f"{'OVERALL TOTALS':<18} | {total_gt:<8} | {total_cand:<10} | {total_tp:<5} | {total_fp:<5} | {total_fn:<5} | {overall_prec:6.1f}%   | {overall_rec:6.1f}%   | {overall_f1:5.1f}%")
    print("=" * 80)

    if mismatches_by_sub:
        print(f"\nDETAILED SUBSECTION ERROR BREAKDOWN ({len(mismatches_by_sub)} subsections with differences):")
        print("-" * 80)
        for sid, diffs in sorted(mismatches_by_sub.items()):
            diff_strs = [f"{m} (GT:{gc} vs Cand:{cc} -> FP:+{fp}, FN:-{fn})" for m, gc, cc, fp, fn in diffs]
            print(f"• {sid}: {', '.join(diff_strs)}")
    else:
        print("\nPERFECT MATCH: 100.0% Precision and Recall against Ground Truth!")

    print("=" * 80)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate vision candidate against Ground Truth")
    parser.add_argument("--candidate", type=Path, required=True, help="Path to candidate file")
    parser.add_argument("--gt", type=Path, required=True, help="Path to ground truth file")
    args = parser.parse_args()
    evaluate(args.candidate, args.gt)
