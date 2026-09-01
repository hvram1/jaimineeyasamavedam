#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
copy_rik_ids.py — Copy rik_id and rik_ids from a source JSON to a target JSON.

This utility copies the `rik_id` and `rik_ids` fields from one JSV output JSON
(e.g. Agneyam-Pavamanam_corrected_out.json) to another
(e.g. Samhita_Devanagari_Unicode_out.json), matching entries by their
subsection keys (subsection_1, subsection_2, ...).

Optionally it can also copy `rik_metadata` and `rik_text`.

Usage:
    python src/tools/copy_rik_ids.py <source_json> <target_json> [options]

Examples:
    # Copy rik_id and rik_ids (in-place update of target):
    python src/tools/copy_rik_ids.py \
        data/output/Agneyam-Pavamanam_corrected_out.json \
        data/output/Samhita_Devanagari_Unicode_out.json

    # Write to a separate output file instead of overwriting target:
    python src/tools/copy_rik_ids.py \
        data/output/Agneyam-Pavamanam_corrected_out.json \
        data/output/Samhita_Devanagari_Unicode_out.json \
        -o data/output/Samhita_merged.json

    # Also copy rik_metadata and rik_text:
    python src/tools/copy_rik_ids.py \
        data/output/Agneyam-Pavamanam_corrected_out.json \
        data/output/Samhita_Devanagari_Unicode_out.json \
        --copy-metadata --copy-text

    # Dry run (preview changes without writing):
    python src/tools/copy_rik_ids.py \
        data/output/Agneyam-Pavamanam_corrected_out.json \
        data/output/Samhita_Devanagari_Unicode_out.json \
        --dry-run
"""

import argparse
import json
import os
import shutil
import sys
from datetime import datetime


def load_json(path):
    """Load a JSON file with UTF-8 encoding."""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(data, path):
    """Save data to a JSON file with UTF-8 encoding and pretty formatting."""
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def iterate_subsections(data):
    """
    Generator that yields (path_tuple, subsection_dict) for every subsection
    in a JSV JSON structure.
    
    path_tuple is (supersection_key, section_key, subsection_key).
    """
    supersections = data.get("supersection", {})
    for ss_key, ss_val in supersections.items():
        if not isinstance(ss_val, dict):
            continue
        sections = ss_val.get("sections", {})
        for sec_key, sec_val in sections.items():
            if not isinstance(sec_val, dict) or "subsections" not in sec_val:
                continue
            for sub_key, sub_val in sec_val["subsections"].items():
                if isinstance(sub_val, dict):
                    yield (ss_key, sec_key, sub_key), sub_val


def build_subsection_index(data):
    """
    Build a dict mapping (supersection_key, section_key, subsection_key) -> subsection_dict
    for quick lookups.
    """
    return {path: sub for path, sub in iterate_subsections(data)}


def copy_rik_ids(source_path, target_path, output_path=None,
                 copy_metadata=False, copy_text=False, dry_run=False,
                 no_backup=False):
    """
    Copy rik_id and rik_ids (and optionally rik_metadata, rik_text) from source
    to target JSON, matched by subsection key.

    Args:
        source_path: Path to the source JSON (has correct rik_id / rik_ids).
        target_path: Path to the target JSON to be updated.
        output_path: If given, write merged result here; otherwise overwrite target.
        copy_metadata: Also copy rik_metadata from source.
        copy_text: Also copy rik_text from source.
        dry_run: If True, print what would change but don't write any file.
        no_backup: If True, skip creating a .bak file.

    Returns:
        A dict with summary stats: updated, skipped_missing, skipped_no_field, total_target.
    """
    # Determine actual output destination
    if output_path is None:
        output_path = target_path

    # Load data
    print(f"Loading source : {source_path}")
    source_data = load_json(source_path)

    print(f"Loading target : {target_path}")
    target_data = load_json(target_path)

    # Build lookup from source
    source_index = build_subsection_index(source_data)

    # Determine which fields to copy
    fields_to_copy = ["rik_id", "rik_ids"]
    if copy_metadata:
        fields_to_copy.append("rik_metadata")
    if copy_text:
        fields_to_copy.append("rik_text")

    print(f"Fields to copy : {', '.join(fields_to_copy)}")
    print()

    # Walk target and patch
    stats = {
        "updated": 0,
        "skipped_missing": 0,
        "skipped_no_field": 0,
        "total_target": 0,
        "changes": [],  # list of change dicts for reporting
    }

    for path, target_sub in iterate_subsections(target_data):
        stats["total_target"] += 1
        ss_key, sec_key, sub_key = path

        if path not in source_index:
            stats["skipped_missing"] += 1
            continue

        source_sub = source_index[path]
        change = {"path": f"{ss_key}/{sec_key}/{sub_key}", "fields": {}}

        any_update = False
        for field in fields_to_copy:
            if field in source_sub:
                old_val = target_sub.get(field)
                new_val = source_sub[field]
                if old_val != new_val:
                    change["fields"][field] = {"old": old_val, "new": new_val}
                    if not dry_run:
                        target_sub[field] = new_val
                    any_update = True
            else:
                stats["skipped_no_field"] += 1

        if any_update:
            stats["updated"] += 1
            stats["changes"].append(change)

    # Print summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"  Total target subsections : {stats['total_target']}")
    print(f"  Updated                  : {stats['updated']}")
    print(f"  Skipped (not in source)  : {stats['skipped_missing']}")
    if stats["skipped_no_field"]:
        print(f"  Skipped (field missing)  : {stats['skipped_no_field']}")
    print()

    # Show first few changes as examples
    if stats["changes"]:
        preview_count = min(10, len(stats["changes"]))
        print(f"First {preview_count} changes:")
        for ch in stats["changes"][:preview_count]:
            print(f"  {ch['path']}:")
            for fld, vals in ch["fields"].items():
                print(f"    {fld}: {vals['old']} -> {vals['new']}")
        if len(stats["changes"]) > preview_count:
            print(f"  ... and {len(stats['changes']) - preview_count} more.")
        print()

    if dry_run:
        print("[DRY RUN] No files were written.")
        return stats

    # Backup
    if not no_backup and output_path == target_path:
        bak_path = target_path + ".bak"
        shutil.copy2(target_path, bak_path)
        print(f"Backup created : {bak_path}")

    # Save
    save_json(target_data, output_path)
    print(f"Output saved   : {output_path}")

    return stats


def main():
    parser = argparse.ArgumentParser(
        description="Copy rik_id and rik_ids from a source JSON to a target JSON, "
                    "matching by subsection key.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  python src/tools/copy_rik_ids.py \\
      data/output/Agneyam-Pavamanam_corrected_out.json \\
      data/output/Samhita_Devanagari_Unicode_out.json

  python src/tools/copy_rik_ids.py \\
      data/output/Agneyam-Pavamanam_corrected_out.json \\
      data/output/Samhita_Devanagari_Unicode_out.json \\
      --copy-metadata --dry-run
        """,
    )
    parser.add_argument("source",
                        help="Source JSON file (has correct rik_id / rik_ids)")
    parser.add_argument("target",
                        help="Target JSON file to update")
    parser.add_argument("-o", "--output",
                        help="Output file path (default: overwrite target in-place)")
    parser.add_argument("--copy-metadata", action="store_true",
                        help="Also copy rik_metadata from source")
    parser.add_argument("--copy-text", action="store_true",
                        help="Also copy rik_text from source")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview changes without writing any file")
    parser.add_argument("--no-backup", action="store_true",
                        help="Skip creating a .bak backup of the target")

    args = parser.parse_args()

    # Validate paths
    if not os.path.isfile(args.source):
        print(f"Error: Source file not found: {args.source}", file=sys.stderr)
        sys.exit(1)
    if not os.path.isfile(args.target):
        print(f"Error: Target file not found: {args.target}", file=sys.stderr)
        sys.exit(1)

    stats = copy_rik_ids(
        source_path=args.source,
        target_path=args.target,
        output_path=args.output,
        copy_metadata=args.copy_metadata,
        copy_text=args.copy_text,
        dry_run=args.dry_run,
        no_backup=args.no_backup,
    )

    if stats["updated"] == 0 and not args.dry_run:
        print("No changes were needed — the files are already in sync.")


if __name__ == "__main__":
    main()
