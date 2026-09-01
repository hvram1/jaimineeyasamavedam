"""Full Samhita benchmark: reports modifier coverage across all 722 subsections."""

import re
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

REPO = Path(__file__).resolve().parents[2]
MASTER = REPO / "data/input/Malayalam/Samam_Malayalam_Unicode.txt"

MODIFIER_RE = re.compile(r"\(([A-HJ-Z][0-9_]?)\)")
GRANTHA_RE = re.compile(r"[\u11300-\u1137F]+")

SUBSECTION_RE = re.compile(
    r"#Start of Mantra Sets -- (subsection_\d+) ## DO NOT EDIT\s*\n(.*?)\n"
    r"#End of Mantra Sets -- \1 ## DO NOT EDIT",
    re.DOTALL,
)

SUPERSECTION_MAP = {
    range(1, 126): "Agneyam (SS1)",
    range(127, 251): "Tadva (SS2)",
    range(252, 347): "Bruhati (SS3)",
    range(348, 412): "Asaavi (SS4)",
    range(519, 728): "Pavamana (SS6)",
    range(1413, 1518): "Aindra (SS5)",
}


def get_supersection(snum: int) -> str:
    for r, name in SUPERSECTION_MAP.items():
        if snum in r:
            return name
    return f"Unknown (sub_{snum})"


def main():
    text = MASTER.read_text(encoding="utf-8")

    total = 0
    with_mods = 0
    without_mods = []
    modifier_counts: dict[str, int] = {}
    ss_stats: dict[str, dict] = {}

    for m in SUBSECTION_RE.finditer(text):
        sub_id = m.group(1)
        body = m.group(2)
        snum = int(sub_id.split("_")[1])
        total += 1

        mods = MODIFIER_RE.findall(body)
        grantha = GRANTHA_RE.findall(body)
        ss = get_supersection(snum)

        if ss not in ss_stats:
            ss_stats[ss] = {"total": 0, "done": 0, "grantha": 0, "mods": 0}
        ss_stats[ss]["total"] += 1
        ss_stats[ss]["grantha"] += len(grantha)

        if mods:
            with_mods += 1
            ss_stats[ss]["done"] += 1
            ss_stats[ss]["mods"] += len(mods)
            for mod in mods:
                modifier_counts[mod] = modifier_counts.get(mod, 0) + 1
        else:
            without_mods.append(snum)

    coverage = 100.0 * with_mods / total if total else 0

    print("=" * 72)
    print("FULL SAMHITA BENCHMARK REPORT")
    print(f"  Master file : {MASTER.relative_to(REPO)}")
    print(f"  Total subsections : {total}")
    print(f"  With modifiers    : {with_mods}  ({coverage:.1f}%)")
    print(f"  Without modifiers : {total - with_mods}")
    print()
    print(f"{'SuperSection':<22} {'Subs':>5} {'Done':>6} {'%':>6} {'Grantha':>8} {'Mods':>6}")
    print("-" * 60)
    for ss, stats in sorted(ss_stats.items()):
        pct = 100.0 * stats["done"] / stats["total"] if stats["total"] else 0
        print(f"{ss:<22} {stats['total']:>5} {stats['done']:>6} {pct:>5.1f}% "
              f"{stats['grantha']:>8} {stats['mods']:>6}")
    print()
    print("MODIFIER DISTRIBUTION:")
    for mod, count in sorted(modifier_counts.items(), key=lambda x: -x[1]):
        print(f"  ({mod:>2}) : {count:>5} occurrences")
    print()
    if without_mods:
        ranges = []
        start = prev = without_mods[0]
        for n in without_mods[1:]:
            if n == prev + 1:
                prev = n
            else:
                ranges.append(f"{start}-{prev}" if start != prev else str(start))
                start = prev = n
        ranges.append(f"{start}-{prev}" if start != prev else str(start))
        print(f"Subsections still needing modifiers ({len(without_mods)}):")
        print("  " + ", ".join(ranges[:30]))
        if len(ranges) > 30:
            print(f"  ... and {len(ranges)-30} more ranges")
    print("=" * 72)


if __name__ == "__main__":
    main()
