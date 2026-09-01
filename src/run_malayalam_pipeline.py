#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Malayalam Jaimineeya Samavedam Pipeline Runner.

Automates the complete Malayalam pipeline:
  1. Plain-text parsing to JSON AST (via src/generate_json.py)
  2. Multi-mode rendering (Combined, Separate, NoMeta) to HTML, PDF, Malayalam TXT,
     and Transliterated Devanagari TXT (via src/render_pdf.py --script malayalam)
  3. Optional sync to docs/ directory for GitHub Pages live preview

Usage:
    python src/run_malayalam_pipeline.py
    python src/run_malayalam_pipeline.py data/input/Malayalam/Samam_Malayalam_Unicode.txt
    python src/run_malayalam_pipeline.py --html-only --publish
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]

DEFAULT_INPUT_TXT = ROOT_DIR / "data" / "input" / "Malayalam" / "Samam_Malayalam_Unicode.txt"
DEFAULT_JSON_OUT = ROOT_DIR / "Malayalam_JSV" / "malayalam" / "Samam_Malayalam_out.json"
DEFAULT_OUTPUT_BASE = ROOT_DIR / "data" / "output" / "Samam_Malayalam"
DOCS_DIR = ROOT_DIR / "docs"


def run_cmd(cmd_list, description=""):
    """Run a subprocess command with UTF-8 encoding and check return code."""
    if description:
        print(f"\n[PIPELINE] {description}...")
    print(f"  $ {' '.join(str(x) for x in cmd_list)}")
    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    res = subprocess.run(cmd_list, cwd=str(ROOT_DIR), env=env)
    if res.returncode != 0:
        print(f"[ERROR] Step failed with exit code {res.returncode}: {description}", file=sys.stderr)
        sys.exit(res.returncode)


def main():
    parser = argparse.ArgumentParser(description="Run the full Malayalam Jaimineeya Samavedam pipeline.")
    parser.add_argument(
        "input_file",
        nargs="?",
        default=str(DEFAULT_INPUT_TXT),
        help=f"Input Malayalam plain text file (default: {DEFAULT_INPUT_TXT.relative_to(ROOT_DIR)})",
    )
    parser.add_argument(
        "--json-output",
        "-j",
        default=str(DEFAULT_JSON_OUT),
        help=f"Output JSON AST path (default: {DEFAULT_JSON_OUT.relative_to(ROOT_DIR)})",
    )
    parser.add_argument(
        "--output",
        "-o",
        default=str(DEFAULT_OUTPUT_BASE),
        help=f"Output file basename or prefix (default: {DEFAULT_OUTPUT_BASE.relative_to(ROOT_DIR)})",
    )
    parser.add_argument(
        "--modes",
        nargs="+",
        choices=["combined", "separate", "nometa"],
        default=["combined", "separate", "nometa"],
        help="Output modes to render (default: combined separate nometa)",
    )
    parser.add_argument(
        "--html-only",
        action="store_true",
        help="Generate only HTML and text outputs (skip PDF compilation)",
    )
    parser.add_argument(
        "--pdf-only",
        action="store_true",
        help="Generate only PDF outputs",
    )
    parser.add_argument(
        "--publish",
        action="store_true",
        help="Copy generated HTML files to docs/ folder for GitHub Pages publishing",
    )

    args = parser.parse_args()

    input_path = Path(args.input_file).resolve()
    json_path = Path(args.json_output).resolve()
    output_prefix = Path(args.output).resolve()

    if not input_path.exists():
        print(f"[ERROR] Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    json_path.parent.mkdir(parents=True, exist_ok=True)
    output_prefix.parent.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print(" Malayalam Jaimineeya Samavedam Pipeline")
    print("=" * 60)
    print(f" Input File : {input_path.relative_to(ROOT_DIR)}")
    print(f" JSON AST   : {json_path.relative_to(ROOT_DIR)}")
    print(f" Output Pfx : {output_prefix.relative_to(ROOT_DIR)}")
    print(f" Modes      : {', '.join(args.modes)}")
    if args.html_only:
        print(" Flags      : --html-only")
    elif args.pdf_only:
        print(" Flags      : --pdf-only")
    print("=" * 60)

    # 1. JSON Generation
    generate_json_cmd = [
        sys.executable,
        str(ROOT_DIR / "src" / "generate_json.py"),
        str(input_path),
        "--output",
        str(json_path),
    ]
    run_cmd(generate_json_cmd, description="Step 1: Generating JSON AST")

    # 2. Rendering across selected modes
    extra_flags = []
    if args.html_only:
        extra_flags.append("--html-only")
    elif args.pdf_only:
        extra_flags.append("--pdf-only")

    for mode in args.modes:
        render_cmd = [
            sys.executable,
            str(ROOT_DIR / "src" / "render_pdf.py"),
            str(json_path),
            "--script",
            "malayalam",
            "--output-mode",
            mode,
            "-o",
            str(output_prefix),
        ] + extra_flags
        run_cmd(render_cmd, description=f"Step 2: Rendering in '{mode}' mode")

    # 3. Optional publish to docs/
    if args.publish:
        print("\n[PIPELINE] Step 3: Publishing HTML files to docs/...")
        DOCS_DIR.mkdir(parents=True, exist_ok=True)
        malayalam_docs_dir = DOCS_DIR / "malayalam"
        malayalam_docs_dir.mkdir(parents=True, exist_ok=True)

        copied = []
        for html_file in output_prefix.parent.glob(f"{output_prefix.name}*.html"):
            target = malayalam_docs_dir / html_file.name
            shutil.copy2(html_file, target)
            copied.append(target)
            print(f"  Copied -> {target.relative_to(ROOT_DIR)}")

        if copied:
            print(f"[INFO] Published {len(copied)} HTML files to docs/malayalam/")

    print("\n" + "=" * 60)
    print(" Pipeline completed successfully!")
    print("=" * 60)
    print(" Generated Artifacts:")
    print(f"  - Malayalam HTMLs : {output_prefix.parent / 'html' / 'Malayalam'}")
    print(f"  - Plaintext TXTs  : {output_prefix.parent / 'txt' / 'Malayalam'}")
    print(f"  - Devanagari TXTs : {output_prefix.parent / 'txt' / 'Devanagari'}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
