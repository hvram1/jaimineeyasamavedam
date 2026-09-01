"""Prepare self-contained prompt packages for external LLM visual swara extraction.

Usage:
    python Malayalam_JSV/extraction/prepare_external_llm_batch.py --start 127 --end 140 --name Tadva_K1_sub127_140 --pages 48 49 50 51
"""

import argparse
import re
import shutil
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

REPO = Path(__file__).resolve().parents[2]
MASTER = REPO / "data/input/Malayalam/Samam_Malayalam_Unicode.txt"
SCANS_DIR = REPO / "Malayalam_JSV/scans"
BATCHES_DIR = REPO / "Malayalam_JSV/stage_output/batches"

SUBSECTION_RE = re.compile(
    r"#Start of Mantra Sets -- (subsection_\d+) ## DO NOT EDIT\s*\n(.*?)\n"
    r"#End of Mantra Sets -- \1 ## DO NOT EDIT",
    re.DOTALL,
)


def main():
    parser = argparse.ArgumentParser(description="Package batch for external LLM extraction")
    parser.add_argument("--start", type=int, required=True, help="Starting subsection number (e.g. 127)")
    parser.add_argument("--end", type=int, required=True, help="Ending subsection number (e.g. 140)")
    parser.add_argument("--name", type=str, default=None, help="Batch name (e.g. Tadva_K1_sub127_140)")
    parser.add_argument("--pages", type=int, nargs="*", default=[], help="Manuscript page numbers (e.g. 48 49 50)")
    args = parser.parse_args()

    batch_name = args.name or f"batch_sub{args.start}_{args.end}"
    batch_dir = BATCHES_DIR / batch_name
    batch_dir.mkdir(parents=True, exist_ok=True)
    images_dir = batch_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    # Read master text and slice requested subsections
    master_text = MASTER.read_text(encoding="utf-8")
    master_subs = {}
    for m in SUBSECTION_RE.finditer(master_text):
        sid = m.group(1)
        snum = int(sid.split("_")[1])
        master_subs[snum] = (sid, m.group(2).strip())

    requested_blocks = []
    missing = []
    for s in range(args.start, args.end + 1):
        if s in master_subs:
            sid, body = master_subs[s]
            requested_blocks.append(
                f"#Start of Mantra Sets -- {sid} ## DO NOT EDIT\n{body}\n#End of Mantra Sets -- {sid} ## DO NOT EDIT"
            )
        else:
            missing.append(s)

    if missing:
        print(f"WARNING: Subsections not found in master: {missing}")

    # Copy images if specified
    copied_images = []
    for p in args.pages:
        scan_file = SCANS_DIR / f"page_{p:04d}.png"
        if scan_file.exists():
            dest = images_dir / f"page_{p:04d}.png"
            shutil.copy2(str(scan_file), str(dest))
            copied_images.append(dest.name)
        else:
            print(f"WARNING: Scan file {scan_file.name} not found in {SCANS_DIR}")

    # Generate prompt markdown file
    prompt_content = f"""# Visual Swara Extraction Prompt — Batch: {batch_name}

You are an expert Vedic epigraphist and Sanskrit/Malayalam manuscript transcriber specializing in Jaimineeya Samavedam (JSV) musical notations.

## TASK
Inspect the attached scanned manuscript page(s) and insert the visual swara modifiers into the provided Malayalam master text block.

## STRICT RULES
1. **COLOR RULE (CRITICAL)**: **IGNORE RED INK completely.**
   - Red ink marks are Grantha swara letters (e.g. തി, ത്ത്, ഖ, ടു) which are **already present** as Unicode Grantha tokens (like `(𑌤𑌿)`) in the text.
   - Look **ONLY for non-base BLACK INK marks** (slashes, dots, vertical bars, arcs, roofs, underbars, commas).
2. **ZERO-REGRESSION ON BASE TEXT**:
   - Do **NOT** alter base Malayalam letters, Grantha tokens, punctuation (`।`, `॥`), verse numbers, or spacing.
   - You **ONLY** insert visual modifier tokens into the text.
3. **TOKEN LEXICON**:
   - `(G)` : Descending slash attached below bottom-right of an akshara (e.g., `അ(G)ഗ്നേ`)
   - `(C)` : Raised shoulder dot at top-right of an akshara (e.g., `ദേ(C)വാ`)
   - `(H)` : Vertical swarita bar centered directly above an akshara (e.g., `മാ(H)നോ`)
   - `(A)` : Syllable-spanning arc above the line
   - `(A1)`: Arc over danda `।`
   - `(B)` : Peak caret roof `^` above syllable
   - `(D)` : Wide chevron roof `Ʌ` above line spanning 2+ syllables
   - `_`   : Sustain underbar connector between words at baseline
   - `.`   : Pause dot inline at baseline
   - `,`   : Low comma inline at baseline

## ATTACHED MANUSCRIPT IMAGES
{', '.join(copied_images) if copied_images else '[Attach relevant scanned manuscript page images]'}

---

## MASTER TEXT TO ANNOTATE:

```text
{chr(10).join(requested_blocks)}
```

---

## OUTPUT FORMAT:
Return **ONLY** the fully annotated text preserving the `#Start of Mantra Sets` and `#End of Mantra Sets` tags. Do not wrap in conversational fluff or additional markdown tags.
"""

    prompt_path = batch_dir / "PROMPT.md"
    prompt_path.write_text(prompt_content, encoding="utf-8")

    # Also save raw master text template for easy reference
    master_template_path = batch_dir / "master_template.txt"
    master_template_path.write_text("\n\n".join(requested_blocks) + "\n", encoding="utf-8")

    print("=" * 60)
    print(f"BATCH PACKAGE CREATED: {batch_name}")
    print(f"  Subsections : {args.start} to {args.end} ({len(requested_blocks)} total)")
    print(f"  Prompt File : {prompt_path}")
    print(f"  Images Copied: {len(copied_images)} images into {images_dir}")
    print("=" * 60)
    print("\nHOW TO USE:")
    print(f"1. Open {prompt_path} and copy the prompt.")
    print(f"2. Attach the images from {images_dir} and send to Claude 3.5 Sonnet / GPT-4o / Gemini.")
    print(f"3. Save the returned text into: Malayalam_JSV/stage_output/candidates/{batch_name}_candidate.txt")
    print(f"4. Run: python Malayalam_JSV/extraction/merge_candidates.py")


if __name__ == "__main__":
    main()
