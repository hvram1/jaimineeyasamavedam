"""Token-level evaluator for Malayalam swara-modifier extraction.

Compares a candidate file against the curated master (ground truth) and
reports per-modifier-type precision / recall / F1, confusion pairs, and
inline-mark (`_` `.` `,`) metrics. Report-only; exits 0.

Usage:
  python -X utf8 Malayalam_JSV/extraction/eval_modifiers.py \
      --candidate <cand.txt> --reference <master.txt> [--label v2] \
      [--compare <other_cand.txt>] [--compare-label v1]
"""

import argparse
import difflib
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

REPO = Path(__file__).resolve().parents[2]

MODIFIER_RE = re.compile(r"\(([A-H][0-9_]?)\)")
SUBSECTION_RE = re.compile(
    r"#Start of Mantra Sets -- (subsection_\d+) ## DO NOT EDIT\s*\n(.*?)\n"
    r"#End of Mantra Sets -- \1 ## DO NOT EDIT",
    re.DOTALL,
)


def parse_mantra_sets(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    return {m.group(1): m.group(2).strip() for m in SUBSECTION_RE.finditer(text)}


def ordered_modifiers(body: str) -> list:
    """Ordered list of modifier tokens in a mantra body."""
    return MODIFIER_RE.findall(body)


def inline_counts(body: str) -> dict:
    return {"_": body.count("_"), ".": body.count("."), ",": body.count(",")}


def align_tokens(ref: list, cand: list) -> dict:
    """Align two ordered token lists; return TP/FP/FN + confusion pairs."""
    sm = difflib.SequenceMatcher(a=ref, b=cand, autojunk=False)
    tp = Counter()
    fp = Counter()
    fn = Counter()
    confusion = Counter()  # (ref_tok, cand_tok) pairs at substitutions
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            for t in ref[i1:i2]:
                tp[t] += 1
        elif tag == "replace":
            for t in ref[i1:i2]:
                fn[t] += 1
            for t in cand[j1:j2]:
                fp[t] += 1
            # pair up substituted tokens positionally
            for r, c in zip(ref[i1:i2], cand[j1:j2]):
                if r != c:
                    confusion[(r, c)] += 1
            # unpaired extras
            extra_r = max(0, (i2 - i1) - (j2 - j1))
            extra_c = max(0, (j2 - j1) - (i2 - i1))
            for t in ref[i1 + (j2 - j1):i2]:
                fn[t] += extra_r and 0  # already counted above; keep fn faithful
        elif tag == "delete":
            for t in ref[i1:i2]:
                fn[t] += 1
        elif tag == "insert":
            for t in cand[j1:j2]:
                fp[t] += 1
    return {"tp": tp, "fp": fp, "fn": fn, "confusion": confusion}


def aggregate(per_sub: dict) -> dict:
    tp = Counter()
    fp = Counter()
    fn = Counter()
    confusion = Counter()
    for sub_id, a in per_sub.items():
        tp.update(a["tp"])
        fp.update(a["fp"])
        fn.update(a["fn"])
        confusion.update(a["confusion"])
    return {"tp": tp, "fp": fp, "fn": fn, "confusion": confusion}


def metrics(tok: str, agg: dict) -> dict:
    tp = agg["tp"].get(tok, 0)
    fp = agg["fp"].get(tok, 0)
    fn = agg["fn"].get(tok, 0)
    prec = tp / (tp + fp) if (tp + fp) else 0.0
    rec = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
    return {"tp": tp, "fp": fp, "fn": fn, "prec": prec, "rec": rec, "f1": f1}


def fmt_pct(x):
    return f"{x*100:5.1f}%"


def print_report(label, ref_sets, cand_sets):
    per_sub = {}
    inline_total_ref = Counter()
    inline_total_cand = Counter()
    for sub_id, ref_body in sorted(ref_sets.items(), key=lambda x: int(x[0].split("_")[1])):
        if sub_id not in cand_sets:
            continue  # only score subsections present in the candidate
        cand_body = cand_sets.get(sub_id, "")
        ref_toks = ordered_modifiers(ref_body)
        cand_toks = ordered_modifiers(cand_body)
        per_sub[sub_id] = align_tokens(ref_toks, cand_toks)
        inline_total_ref.update(inline_counts(ref_body))
        inline_total_cand.update(inline_counts(cand_body))
    agg = aggregate(per_sub)

    all_types = sorted(set(agg["tp"]) | set(agg["fp"]) | set(agg["fn"]))
    total_tp = sum(agg["tp"].values())
    total_fp = sum(agg["fp"].values())
    total_fn = sum(agg["fn"].values())
    total_ref = total_tp + total_fn
    overall = metrics("__all__", {"tp": Counter({"__all__": total_tp}),
                                  "fp": Counter({"__all__": total_fp}),
                                  "fn": Counter({"__all__": total_fn})})

    print("=" * 72)
    print(f"EVALUATION REPORT — {label}")
    print(f"  Candidate : {cand_sets and '<loaded>' or '<missing>'}")
    print(f"  Reference : master ground truth")
    print(f"  Subsections compared : {len(per_sub)}")
    print("=" * 72)
    print(f"{'Type':<6} {'TP':>4} {'FP':>4} {'FN':>4} {'Prec':>7} {'Rec':>7} {'F1':>7}")
    print("-" * 72)
    for t in all_types:
        m = metrics(t, agg)
        print(f"({t:<4}) {m['tp']:>4} {m['fp']:>4} {m['fn']:>4} "
              f"{fmt_pct(m['prec']):>7} {fmt_pct(m['rec']):>7} {fmt_pct(m['f1']):>7}")
    print("-" * 72)
    print(f"{'TOTAL':<6} {total_tp:>4} {total_fp:>4} {total_fn:>4} "
          f"{fmt_pct(overall['prec']):>7} {fmt_pct(overall['rec']):>7} "
          f"{fmt_pct(overall['f1']):>7}   (ref total = {total_ref})")
    print()
    print("Inline marks:")
    for m in ("_", ".", ","):
        r = inline_total_ref.get(m, 0)
        c = inline_total_cand.get(m, 0)
        print(f"  {m!r:<5} ref={r:<4} cand={c:<4} "
              f"diff={c - r:+d}")
    print()
    if agg["confusion"]:
        print("Confusion pairs (ref -> cand):")
        for (r, c), n in agg["confusion"].most_common(10):
            print(f"  ({r}) -> ({c}) : {n}")
    print("=" * 72)
    return {"agg": agg, "overall": overall, "inline_ref": inline_total_ref,
            "inline_cand": inline_total_cand}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate", required=True)
    ap.add_argument("--reference", required=True)
    ap.add_argument("--label", default="candidate")
    ap.add_argument("--compare", default=None)
    ap.add_argument("--compare-label", default="v1")
    args = ap.parse_args()

    ref_sets = parse_mantra_sets(Path(args.reference))
    cand_sets = parse_mantra_sets(Path(args.candidate))
    print_report(args.label, ref_sets, cand_sets)

    if args.compare:
        print("\n")
        comp_sets = parse_mantra_sets(Path(args.compare))
        print_report(args.compare_label, ref_sets, comp_sets)


if __name__ == "__main__":
    main()
