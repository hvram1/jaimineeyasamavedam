"""Frozen swara-marker -> Grantha lookup for the Malayalam pipeline.

Reads the reviewed-and-frozen lookup table (Malayalam_JSV/swara_lookup_frozen.json),
which was generated from the Google Sheet export + per-letter resolution
(see Malayalam_JSV/generate_marker_review.py and spec.md section 6). The
pipeline never reads the live sheet: the frozen JSON is the single source
of truth for Phase 1.
"""

import json
import re
from functools import lru_cache
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
FROZEN_LOOKUP = REPO_ROOT / "Malayalam_JSV" / "swara_lookup_frozen.json"

# Same tokenizer convention as utils.py / render_pdf.py: a swara marker is
# the parenthesised run after a word: Word(Swara). Footnote markers are
# (sN) and are handled separately.
MARKER_RE = re.compile(r"\(([^)]+)\)")
FOOTNOTE_RE = re.compile(r"^s\d+$")


@lru_cache(maxsize=1)
def load_lookup() -> dict:
    """Load the frozen lookup table once. Raises FileNotFoundError with a
    helpful message if the reviewed table is missing."""
    if not FROZEN_LOOKUP.exists():
        raise FileNotFoundError(
            f"Frozen swara lookup not found: {FROZEN_LOOKUP}. "
            "Run Malayalam_JSV/generate_marker_review.py first."
        )
    with open(FROZEN_LOOKUP, encoding="utf-8") as fh:
        return json.load(fh)


def marker_to_grantha(marker: str) -> str:
    """Resolve a swara marker string to its frozen Grantha text.

    Prefers the reviewed 'grantha_text' characters (may include non-Grantha
    script characters, e.g. A13 Saa resolves to Malayalam ശ per the reference
    manuscript); falls back to assembling from grantha_codepoints.

    Unknown markers (not present in the frozen table) raise KeyError; the
    caller decides the fallback (spec: render literally / QA flag).
    """
    entry = load_lookup()["lookup"][marker]
    text = entry.get("grantha_text")
    if text:
        return text
    return "".join(chr(int(cp, 16)) for cp in entry["grantha_codepoints"])


def marker_source(marker: str) -> str:
    """'sheet', 'fallback', 'decided' or 'corrupt' provenance of a marker."""
    return load_lookup()["lookup"][marker]["source"]


def is_footnote_marker(marker: str) -> bool:
    return bool(FOOTNOTE_RE.match(marker))


def coverage_report(markers: set[str]) -> dict:
    """QA helper: which markers are unmapped, and per-source counts."""
    lookup = load_lookup()["lookup"]
    unknown = sorted(m for m in markers if m not in lookup)
    sources: dict[str, int] = {}
    for m, entry in lookup.items():
        sources[entry["source"]] = sources.get(entry["source"], 0) + 1
    return {"unknown": unknown, "sources": sources}