"""Samam text -> Malayalam intermediate text (Word(GranthaSwara) format).

Phase 1 pipeline (Samam path only, per spec.md):
  1. Tokenize each corrected mantra line into Word(Swara) pairs, dandas,
     mantra numbers and footnote markers (same conventions as utils.py).
  2. Transliterate each Word via aksharamukha (ml_transliterate).
  3. Resolve each Swara marker to Grantha via the frozen lookup (ml_map);
     unknown markers fall back to a literal Devanagari->Grantha
     transliteration and are recorded as QA warnings.
  4. Assert syllable-count alignment per marked word (Devanagari syllables
     vs Malayalam grapheme clusters); mismatches are QA warnings.

The output 'malayalam-mantra' lines keep the exact Word(Swara) markup so
they round-trip through generate_json.py correction mode, and the
transformed AST is what render_pdf.py --script malayalam renders to
Unicode text and PDF.

Usage:
    .venv\\Scripts\\python.exe -X utf8 -m malayalam.ml_text \
        --input data/output/Vargeekaran.json \
        --output data/output/malayalam/Samhita_Malayalam.json
"""

import argparse
import copy
import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from malayalam.ml_map import is_footnote_marker, marker_to_grantha, marker_source
from malayalam.ml_transliterate import (
    devanagari_syllable_count,
    devanagari_to_grantha,
    devanagari_to_malayalam,
    malayalam_syllable_count,
)

WORD_RE = re.compile(r"([^\s()।॥]+)((?:\([^)]+\))+)?([ः:]?)")
DEVANAGARI_NUMERAL_RE = re.compile(r"^[०-९]+$")

# Canonical Devanagari/Malayalam -> ASCII digit conversion for Samam
# numerals inside danda markers (॥१॥ -> ॥1॥). Spacing is preserved
# verbatim so only the digit characters change.
ENGLISH_DIGITS = str.maketrans("०१२३४५६७८९൦൧൨൩൪൫൬൭൮൯", "01234567890123456789")
SAMAM_NUMERAL_RE = re.compile(r"(॥\s*)([०-९\d]+)(\s*॥)")


def normalize_malayalam_samam_numerals(text: str) -> str:
    """Convert Devanagari/Malayalam digits inside ॥N॥ markers to ASCII."""
    if not text:
        return text
    return SAMAM_NUMERAL_RE.sub(
        lambda m: m.group(1) + m.group(2).translate(ENGLISH_DIGITS) + m.group(3),
        text,
    )

# Source convention: a word-final anusvara is written as a separate 'म्'
# token (e.g. 'ता(त) म् ।'). Merging it into the preceding word is
# orthographically correct (ताम्) and required for rendering: a standalone
# Malayalam anusvara (U+0D02) is a combining mark with no base and renders
# as a dotted circle in the PDF.
ANUSVARA_FORMS = {"\u092E\u094D", "\u0902", "\u092E\u094D\u0903"}  # म्, ं, म्ः


def tokenize_mantra_line(text: str) -> list[dict]:
    """Split a mantra line into ordered tokens.

    Token types: word (with optional swara marker + trailing visarga),
    danda, footnote ((sN)), marker (standalone swara), space, other.
    """
    tokens: list[dict] = []
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        if ch.isspace():
            tokens.append({"type": "space"})
            i += 1
            continue
        if ch in "।॥|":
            tokens.append({"type": "danda", "char": ch})
            i += 1
            continue
        if ch == "(":
            m = re.match(r"\(s\d+\)", text[i:])
            if m:
                tokens.append({"type": "footnote", "text": m.group(0)})
                i += len(m.group(0))
                continue
            m = re.match(r"\(([^)]+)\)", text[i:])
            if m:
                tokens.append({"type": "marker", "marker": m.group(1)})
                i += len(m.group(0))
                continue
            tokens.append({"type": "other", "text": ch})
            i += 1
            continue
        m = WORD_RE.match(text[i:])
        if m and m.group(1):
            swara_group = m.group(2) or ""
            fn_tokens = []
            if swara_group:
                all_parens = re.findall(r"\(([^)]+)\)", swara_group)
                swara_markers = []
                for p in all_parens:
                    if re.match(r"^s\d+$", p):
                        fn_tokens.append(f"({p})")
                    else:
                        swara_markers.append(p)
                swara_val = "".join(f"({m_val})" for m_val in swara_markers) if len(swara_markers) > 1 else (swara_markers[0] if swara_markers else None)
            else:
                swara_val = None
            matched_len = m.end()
            word_str = m.group(1)
            # If immediately followed by underscore after swara, attach _ as suffix to word
            if i + matched_len < n and text[i + matched_len] == "_" and swara_group:
                word_str += "_"
                matched_len += 1

            tokens.append(
                {
                    "type": "word",
                    "word": word_str,
                    "swara": swara_val,
                    "visarga": m.group(3),
                }
            )
            for fn in fn_tokens:
                tokens.append({"type": "footnote", "text": fn})
            i += matched_len
            continue
        tokens.append({"type": "other", "text": ch})
        i += 1
    return tokens


MODIFIER_DIRECT_MAP = {
    # Modifiers from updated Google Sheet & Curation Tool (A..K)
    "A": "\uE004",   # Syllable Arc (Tie) ╭╮ / ⁀
    "A1": "\uE00D",  # Arc over Danda
    "B": "\uE005",   # Caret / Peak /\ / ^
    "B1": "\uE02C",  # Diagonal Bridging Slash /
    "C": "\uE001",   # High/Mid-Dot ॱ / ·
    "D": "\uE006",   # Chevron Roof Ʌ
    "D1": "\uE00E",  # Rising Stroke / Hooked Rise ↗ / ⋀
    "D2": "\uE00F",  # Check Tick ✓
    "E": "\uE002",   # Heavy Vertical ┃
    "F": "\uE008",   # Phrasing Danda with overhead dot ╷
    "G": "\uE003",   # Descending Tone \ / ⟍
    "H": "\uE00C",   # Swarita ॑ / |
    "I": "\uE02A",   # Double Shoulder Dash ⫽
    "J": "\uE02B",   # Horizontal Shoulder Bar —
    "K": "\uE02D",   # Shoulder Cross Mark ⨯
    "L": "\uE00C",   # Swarita ॑ / |

    # Lowercase variants
    "a": "\uE004", "a1": "\uE00D", "b": "\uE005", "b1": "\uE02C",
    "c": "\uE001", "d": "\uE006", "d1": "\uE00E", "d2": "\uE00F",
    "e": "\uE002", "f": "\uE008", "g": "\uE003", "h": "\uE00C",
    "i": "\uE02A", "j": "\uE02B", "k": "\uE02D", "l": "\uE00C",

    # Direct Symbols matching "How to enter" column
    "^": "\uE005", "˄": "\uE005",
    "Ʌ": "\uE006", "/\\": "\uE006", "∧": "\uE006",
    "⁀": "\uE004", "͡": "\uE004", "╭╮": "\uE004",
    "ͦ": "\uE009", "˚": "\uE009",
    "ॱ": "\uE001", "·": "\uE001",
    "_": "\uE007",
    "|": "\uE00C", "│": "\uE00C", "।": "।",
    "┃": "\uE002", "╷": "\uE002", "⃓": "\uE002",
    "\\": "\uE003", "╲": "\uE003", "⟍": "\uE003",
    "/": "\uE008",
    ",": "\uE00A", "ˏ": "\uE00A", "̦": "\uE00A",
    "||": "\uE00B", "॥": "\uE00B",
    "॑": "\uE00C", "ˈ": "\uE00C",
}


def resolve_swara(marker: str, warnings: list, stats: Counter) -> str:
    """Resolve a Devanagari swara marker to Grantha.

    Checks:
      1. Compound / multiple markers (e.g. '(𑌤)(G)')
      2. Direct letter/symbol modifier map (A..L)
      3. Passthrough for raw Grantha / PUA characters
      4. ml_map frozen dictionary
      5. Literal transliteration fallback (recorded as QA warning)
    """
    if not marker:
        return ""
    if "(" in marker:
        sub_markers = re.findall(r"\(([^)]+)\)", marker)
        if sub_markers:
            return "".join(resolve_swara(sm, warnings, stats) for sm in sub_markers)
    if marker in MODIFIER_DIRECT_MAP:
        return MODIFIER_DIRECT_MAP[marker]
    if any(0x11300 <= ord(c) <= 0x1137F or 0xE000 <= ord(c) <= 0xF8FF for c in marker):
        return marker
    stats["markers"][marker] += 1
    try:
        grantha = marker_to_grantha(marker)
        stats["marker_sources"][marker_source(marker)] += 1
        return grantha
    except KeyError:
        grantha = devanagari_to_grantha(marker)
        warnings.append(
            f"marker not in frozen lookup (literal fallback): {marker!r} -> {grantha!r}"
        )
        stats["marker_sources"]["fallback_unknown"] += 1
        return grantha


def transform_line(text: str, warnings: list, stats: Counter) -> str:
    """Transliterate one mantra line: Devanagari words -> Malayalam, swara
    markers -> Grantha, preserving markup (dandas, numbers, footnotes)."""
    tokens = []
    last_word_idx = None
    for tok in tokenize_mantra_line(text):
        if (
            tok["type"] == "word"
            and not tok["swara"]
            and tok["word"] in ANUSVARA_FORMS
            and last_word_idx is not None
        ):
            prev = tokens[last_word_idx]
            if not DEVANAGARI_NUMERAL_RE.match(prev["word"]):
                prev["word"] = prev["word"] + tok["word"]
                continue
        tokens.append(tok)
        if tok["type"] == "word":
            last_word_idx = len(tokens) - 1
    out: list[str] = []
    for tok in tokens:
        t = tok["type"]
        if t == "space":
            out.append(" ")
        elif t == "danda":
            out.append(tok["char"])
        elif t == "footnote":
            out.append(tok["text"])
        elif t == "marker":
            out.append(f"({resolve_swara(tok['marker'], warnings, stats)})")
        elif t == "word":
            word = tok["word"].replace(":", "ः")
            if DEVANAGARI_NUMERAL_RE.match(word):
                out.append(word)  # mantra numbers (॥१॥) stay verbatim
                continue
            if tok["swara"] and not is_footnote_marker(tok["swara"]):
                dev_word = word + (tok["visarga"] or "")
                ml_word = devanagari_to_malayalam(dev_word)
                stats["marked_words"] += 1
                d_syl = devanagari_syllable_count(dev_word)
                m_syl = malayalam_syllable_count(ml_word)
                if d_syl != m_syl:
                    warnings.append(
                        f"syllable mismatch: {dev_word!r} dev={d_syl} mal={m_syl} "
                        f"-> {ml_word!r}"
                    )
                    stats["syllable_mismatches"] += 1
                if "(" in tok["swara"]:
                    sub_markers = re.findall(r"\(([^)]+)\)", tok["swara"])
                    if sub_markers:
                        resolved_groups = "".join(f"({resolve_swara(sm, warnings, stats)})" for sm in sub_markers)
                        out.append(f"{ml_word}{resolved_groups}")
                    else:
                        grantha = resolve_swara(tok["swara"], warnings, stats)
                        out.append(f"{ml_word}({grantha})")
                else:
                    grantha = resolve_swara(tok["swara"], warnings, stats)
                    out.append(f"{ml_word}({grantha})")
            else:
                out.append(devanagari_to_malayalam(word + (tok["visarga"] or "")))
        else:
            out.append(tok["text"])
    return "".join(out)


def transform_subsection(subsection: dict, warnings: list, stats: Counter) -> dict:
    """Add 'malayalam-mantra-sets' and transliterate Rik/Saman metadata to a subsection copy."""
    sub = copy.deepcopy(subsection)
    if sub.get("rik_text"):
        try:
            sub["rik_text"] = devanagari_to_malayalam(sub["rik_text"])
        except Exception:
            pass
    if sub.get("rik_metadata"):
        try:
            sub["rik_metadata"] = devanagari_to_malayalam(sub["rik_metadata"])
        except Exception:
            pass
    if sub.get("saman_metadata"):
        try:
            sub["saman_metadata"] = devanagari_to_malayalam(sub["saman_metadata"])
        except Exception:
            pass
    if sub.get("footnotes"):
        try:
            sub["footnotes"] = {
                k: devanagari_to_malayalam(v) if isinstance(v, str) else v
                for k, v in sub["footnotes"].items()
            }
        except Exception:
            pass
    if sub.get("malayalam-mantra-sets"):
        return sub
        
    mantra_sets = sub.get("corrected-mantra_sets") or sub.get("mantra_sets") or []
    malayalam_sets = []
    for mantra_set in mantra_sets:
        mantra = mantra_set.get("corrected-mantra", "")
        if not mantra:
            mantra = " ".join(
                w.get("word", "") for w in mantra_set.get("mantra-words", [])
            )
        malayalam_sets.append(
            {
                "malayalam-mantra": transform_line(mantra, warnings, stats),
                "devanagari-mantra": mantra,
            }
        )
    sub["malayalam-mantra-sets"] = malayalam_sets
    return sub


def _supersections(data: dict) -> dict:
    """AST container key: 'supersections' (new) or 'supersection' (legacy)."""
    return data.get("supersections") or data.get("supersection") or {}


def transform_ast(data: dict, warnings: list = None, stats: Counter = None):
    """Deep-copy the AST adding malayalam-mantra-sets and transliterating titles to every subsection.

    Returns (new_data, warnings, stats).
    """
    warnings = warnings if warnings is not None else []
    stats = stats if stats is not None else Counter(markers=Counter(), marker_sources=Counter())
    out = copy.deepcopy(data)
    for supersection in _supersections(out).values():
        if supersection.get("supersection_title"):
            try:
                supersection["supersection_title"] = devanagari_to_malayalam(supersection["supersection_title"])
            except Exception:
                pass
        for section in supersection.get("sections", {}).values():
            if not isinstance(section, dict):
                continue
            if section.get("section_title"):
                try:
                    section["section_title"] = devanagari_to_malayalam(section["section_title"])
                except Exception:
                    pass
            for key, subsection in list(section.get("subsections", {}).items()):
                transformed = transform_subsection(subsection, warnings, stats)
                if transformed.get("header") and isinstance(transformed["header"], dict):
                    h = transformed["header"].get("header", "")
                    if h:
                        try:
                            transformed["header"]["header"] = devanagari_to_malayalam(h)
                        except Exception:
                            pass
                section["subsections"][key] = transformed
    return out, warnings, stats


def render_intermediate_text(data: dict) -> str:
    """Plain-text artifact with the same # Start/End structure as the
    Devanagari text files (including Rik metadata, Rik text, SubSection title, Saman metadata, and Mantra sets in Malayalam)."""
    lines: list[str] = []
    for i, supersection in _supersections(data).items():
        title = supersection.get("supersection_title", "")
        lines.append(f"# Start of SuperSection Title -- {i} ## DO NOT EDIT")
        lines.append(title)
        lines.append(f"# End of SuperSection Title -- {i} ## DO NOT EDIT")
        lines.append("")
        for j, section in supersection.get("sections", {}).items():
            stitle = section.get("section_title", "")
            lines.append(f"# Start of Section Title -- {j} ## DO NOT EDIT")
            lines.append(stitle)
            lines.append(f"# End of Section Title -- {j} ## DO NOT EDIT")
            lines.append("")
            prev_rik_id = None
            for k, subsection in section.get("subsections", {}).items():
                rik_id = subsection.get("rik_id")
                rik_ids = subsection.get("rik_ids", [rik_id] if rik_id else [])
                max_rik_id = max(rik_ids) if rik_ids else None
                show_rik = (prev_rik_id is None) or (rik_id != prev_rik_id) or (len(rik_ids) > 1 and max_rik_id != prev_rik_id)
                
                # Rik Metadata (Rishi, Devata, Chandas)
                rik_metadata = subsection.get("rik_metadata", "")
                if show_rik and rik_metadata:
                    lines.append(f"# Start of Rik Metadata -- {k} ## DO NOT EDIT")
                    lines.append(rik_metadata)
                    lines.append(f"# End of Rik Metadata -- {k} ## DO NOT EDIT")
                
                # Rik Text
                rik_text = subsection.get("rik_text", "")
                if show_rik and rik_text:
                    lines.append(f"# Start of Rik Text -- {k} ## DO NOT EDIT")
                    lines.append(normalize_malayalam_samam_numerals(rik_text))
                    lines.append(f"# End of Rik Text -- {k} ## DO NOT EDIT")
                    lines.append("")

                # SubSection Title
                header = subsection.get("header", {}).get("header", "")
                lines.append(f"# Start of SubSection Title -- {k} ## DO NOT EDIT")
                lines.append(header)
                lines.append(f"# End of SubSection Title -- {k} ## DO NOT EDIT")

                # Samam Metadata
                saman_metadata = subsection.get("saman_metadata", "")
                if saman_metadata:
                    lines.append(f"# Start of Samam Metadata -- {k} ## DO NOT EDIT")
                    lines.append(saman_metadata)
                    lines.append(f"# End of Samam Metadata -- {k} ## DO NOT EDIT")

                # Mantra Sets
                lines.append(f"#Start of Mantra Sets -- {k} ## DO NOT EDIT")
                for mantra_set in subsection.get("malayalam-mantra-sets", []):
                    lines.append(
                        normalize_malayalam_samam_numerals(mantra_set["malayalam-mantra"])
                    )
                lines.append(f"#End of Mantra Sets -- {k} ## DO NOT EDIT")

                # Footnotes
                footnotes = subsection.get("footnotes", {})
                if footnotes:
                    lines.append(f"# Start of Footnote -- {k} ## DO NOT EDIT")
                    for fn_k, fn_v in footnotes.items():
                        lines.append(f"{fn_k} - {fn_v}")
                    lines.append(f"# End of Footnote -- {k} ## DO NOT EDIT")

                lines.append("")
                prev_rik_id = max_rik_id if max_rik_id is not None else rik_id
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="JSV Samam -> Malayalam intermediate text")
    parser.add_argument("--input", required=True, help="Devanagari AST JSON (Vargeekaran.json)")
    parser.add_argument("--output", required=True, help="Output transformed JSON path")
    parser.add_argument("--text-out", default=None, help="Intermediate Unicode text output")
    parser.add_argument("--qa-out", default=None, help="QA report output path")
    parser.add_argument("--supersection", default=None, help="Only this supersection id (e.g. supersection_1)")
    parser.add_argument("--section", default=None, help="Only this section id (e.g. section_1)")
    args = parser.parse_args()

    input_path = Path(args.input)
    data = json.loads(input_path.read_text(encoding="utf-8"))

    if args.supersection:
        keep = {args.supersection: _supersections(data)[args.supersection]}
        data = {"supersection": keep}
    if args.section:
        for ss in _supersections(data).values():
            keep = {args.section: ss["sections"][args.section]}
            ss["sections"] = keep

    out_data, warnings, stats = transform_ast(data)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(out_data, ensure_ascii=False, indent=2), encoding="utf-8")

    if args.text_out:
        text_path = Path(args.text_out)
        text_path.parent.mkdir(parents=True, exist_ok=True)
        text_path.write_text(render_intermediate_text(out_data), encoding="utf-8")

    print(f"Wrote {output_path}")
    if args.text_out:
        print(f"Wrote {args.text_out}")
    n_subs = sum(
        len(s.get("subsections", {}))
        for ss in _supersections(out_data).values()
        for s in ss.get("sections", {}).values()
        if isinstance(s, dict)
    )
    print(f"Subsections processed: {n_subs}")
    print(f"Marked words: {stats['marked_words']}")
    print(f"Marker sources: {dict(stats['marker_sources'])}")
    print(f"Syllable mismatches: {stats['syllable_mismatches']}")
    print(f"Warnings: {len(warnings)}")
    for w in warnings[:30]:
        print(f"  WARN {w}")

    if args.qa_out:
        qa_path = Path(args.qa_out)
        qa_path.write_text("\n".join(warnings) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()