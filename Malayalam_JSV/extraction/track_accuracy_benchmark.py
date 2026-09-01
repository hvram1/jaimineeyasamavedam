"""
Iterative Accuracy Tracking Engine for Jaimineeya Samavedam Swara Modifier Extraction.

Tracks the active learning loop:
  1) Initial Extraction
  2) Human Ground Truth Update
  3) Accuracy (A) - Initial Extraction vs Updated GT
  4) Re-extraction with Prompt Learnings -> Accuracy (B) - Re-extracted vs Updated GT
  5) Persistent logging and comparative ASCII / Markdown progression chart.

Usage:
  python -X utf8 Malayalam_JSV/extraction/track_accuracy_benchmark.py \
      --kandah "Agneyam_K2" \
      --initial-cand Malayalam_JSV/stage_output/candidates/Agneyam_K2_candidate.txt \
      --reprocessed-cand Malayalam_JSV/stage_output/candidates/Agneyam_K2_reprocessed_candidate.txt \
      --gt data/input/Malayalam/Samam_Malayalam_Unicode.txt
"""

import argparse
import difflib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parents[2]
HISTORY_FILE = REPO_ROOT / "Malayalam_JSV" / "stage_output" / "benchmark_history.json"

SUBSECTION_RE = re.compile(
    r"#Start of Mantra Sets -- (subsection_\d+) ## DO NOT EDIT\s*\n(.*?)\n"
    r"#End of Mantra Sets -- \1 ## DO NOT EDIT",
    re.DOTALL,
)
MODIFIER_RE = re.compile(r"\(([A-Z][0-9_]?)\)")


def parse_subsections(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    return {m.group(1): m.group(2).strip() for m in SUBSECTION_RE.finditer(text)}


def evaluate_stream(cand_subs: dict, gt_subs: dict) -> dict:
    common_subs = sorted(set(cand_subs.keys()) & set(gt_subs.keys()), key=lambda x: int(x.split("_")[1]))
    if not common_subs:
        return {"error": "No common subsections found"}

    tp = Counter()
    fp = Counter()
    fn = Counter()
    conf = Counter()
    inline_cand = Counter()
    inline_gt = Counter()

    for sid in common_subs:
        c_text = cand_subs[sid]
        g_text = gt_subs[sid]

        for mark in ["_", ".", ","]:
            inline_cand[mark] += c_text.count(mark)
            inline_gt[mark] += g_text.count(mark)

        c_mods = MODIFIER_RE.findall(c_text)
        g_mods = MODIFIER_RE.findall(g_text)

        sm = difflib.SequenceMatcher(a=g_mods, b=c_mods, autojunk=False)
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag == "equal":
                for t in g_mods[i1:i2]:
                    tp[t] += 1
            elif tag == "replace":
                for t in g_mods[i1:i2]:
                    fn[t] += 1
                for t in c_mods[j1:j2]:
                    fp[t] += 1
                for r, c in zip(g_mods[i1:i2], c_mods[j1:j2]):
                    if r != c:
                        conf[(r, c)] += 1
            elif tag == "delete":
                for t in g_mods[i1:i2]:
                    fn[t] += 1
            elif tag == "insert":
                for t in c_mods[j1:j2]:
                    fp[t] += 1

    total_tp = sum(tp.values())
    total_fp = sum(fp.values())
    total_fn = sum(fn.values())
    total_gt = total_tp + total_fn

    prec = (total_tp / (total_tp + total_fp) * 100) if (total_tp + total_fp) else 0.0
    rec = (total_tp / (total_tp + total_fn) * 100) if (total_tp + total_fn) else 0.0
    f1 = (2 * prec * rec / (prec + rec)) if (prec + rec) else 0.0

    return {
        "num_subsections": len(common_subs),
        "total_gt_mods": total_gt,
        "total_cand_mods": total_tp + total_fp,
        "tp": total_tp,
        "fp": total_fp,
        "fn": total_fn,
        "precision": round(prec, 1),
        "recall": round(rec, 1),
        "f1": round(f1, 1),
        "per_mod_tp": dict(tp),
        "per_mod_fp": dict(fp),
        "per_mod_fn": dict(fn),
        "confusion": {f"{r}->{c}": n for (r, c), n in conf.items()},
        "inline_cand": dict(inline_cand),
        "inline_gt": dict(inline_gt),
    }


def load_history():
    if HISTORY_FILE.exists():
        try:
            return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []


def save_history(history):
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    HISTORY_FILE.write_text(json.dumps(history, indent=2, ensure_ascii=False), encoding="utf-8")


def render_ascii_bar(pct, width=25):
    filled = int(round((pct / 100) * width))
    filled = max(0, min(width, filled))
    return "█" * filled + "░" * (width - filled)


def print_comparison_dashboard(entry):
    print("=" * 80)
    print(f"🎯 ACCURACY PROGRESSION DASHBOARD — {entry['kandah']}")
    print("=" * 80)
    print(f"Subsections Tracked : {entry['metrics_a']['num_subsections']}")
    print(f"Ground Truth Targets: {entry['metrics_a']['total_gt_mods']} modifiers")
    print("-" * 80)

    f1_a = entry['metrics_a']['f1']
    rec_a = entry['metrics_a']['recall']
    prec_a = entry['metrics_a']['precision']

    f1_b = entry['metrics_b']['f1']
    rec_b = entry['metrics_b']['recall']
    prec_b = entry['metrics_b']['precision']

    print(f"Initial Extraction (A)   : Precision={prec_a:5.1f}% | Recall={rec_a:5.1f}% | F1={f1_a:5.1f}%")
    print(f"  F1 Bar (A) : [{render_ascii_bar(f1_a)}] {f1_a:.1f}%")
    print()
    print(f"Reprocessed with GT (B)  : Precision={prec_b:5.1f}% | Recall={rec_b:5.1f}% | F1={f1_b:5.1f}%")
    print(f"  F1 Bar (B) : [{render_ascii_bar(f1_b)}] {f1_b:.1f}%")
    print("-" * 80)
    delta_f1 = f1_b - f1_a
    delta_rec = rec_b - rec_a
    delta_prec = prec_b - prec_a
    print(f"🚀 NET GAIN  : F1: {'+' if delta_f1 >= 0 else ''}{delta_f1:.1f}% | Recall: {'+' if delta_rec >= 0 else ''}{delta_rec:.1f}% | Precision: {'+' if delta_prec >= 0 else ''}{delta_prec:.1f}%")
    print("=" * 80)


def main():
    parser = argparse.ArgumentParser(description="Accuracy tracker for iterative active learning cycles.")
    parser.add_argument("--kandah", required=True, help="Kandah label (e.g. Agneyam_K2, Agneyam_K3)")
    parser.add_argument("--initial-cand", required=True, type=Path, help="Initial candidate file path (Cycle A)")
    parser.add_argument("--reprocessed-cand", required=True, type=Path, help="Reprocessed candidate file path (Cycle B)")
    parser.add_argument("--gt", required=True, type=Path, help="Ground truth master file path")
    args = parser.parse_args()

    gt_subs = parse_subsections(args.gt)
    cand_a_subs = parse_subsections(args.initial_cand)
    cand_b_subs = parse_subsections(args.reprocessed_cand)

    metrics_a = evaluate_stream(cand_a_subs, gt_subs)
    metrics_b = evaluate_stream(cand_b_subs, gt_subs)

    entry = {
        "kandah": args.kandah,
        "initial_cand_path": str(args.initial_cand),
        "reprocessed_cand_path": str(args.reprocessed_cand),
        "metrics_a": metrics_a,
        "metrics_b": metrics_b,
    }

    history = load_history()
    # update or append
    history = [h for h in history if h.get("kandah") != args.kandah]
    history.append(entry)
    save_history(history)

    print_comparison_dashboard(entry)


if __name__ == "__main__":
    main()
