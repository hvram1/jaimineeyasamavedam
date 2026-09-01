#!/usr/bin/env python3
"""
Generate a comprehensive visual Glyph Grid PNG and interactive HTML table
showcasing the full set of Jaimineeya Vedic Swara glyphs, composite ligatures,
manuscript overrides (Pla/Sha), and all Canonical Vedic Swara Modifiers (A..H) with their
"Stacked above/below" positions, dotted-circle syllable representations, and typing shortcuts.
"""

from pathlib import Path
import csv
import shutil
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
FONT_PATH = ROOT / "fonts" / "JaimineeyaSwara.ttf"
OUT_DIR = ROOT / "Malayalam_JSV" / "malayalam"
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_IMG = OUT_DIR / "glyph_grid_JaimineeyaSwara.png"
OUT_HTML = OUT_DIR / "glyph_table.html"

ARTIFACT_DIR = Path(r"C:\Users\sekha\.gemini\antigravity-ide\brain\33a78242-ade0-47ff-b909-95b423204936")

# Featured highlights for the high-res visual chart
FEATURED_GLYPHS = [
    # Row 1: The Canonical Vedic Swara Modifiers & Inline Marks
    ("Modifier (A) Arc", "\uE004", "syllable_arc_jsv", "U+E004 / ╭╮", "Modifier (A)", "Above", "Syllable Spanning Arc"),
    ("Modifier (A1) Arc/|", "\uE00D", "syllable_arc_danda_jsv", "U+E00D / (A1)", "Modifier (A1)", "Above", "Syllable Spanning Arc over Danda"),
    ("Modifier (B) Caret", "\uE005", "caret_jsv", "U+E005 / /\\", "Modifier (B)", "Above", "Peak Elevation Caret"),
    ("Modifier (B1) Slash", "\uE02C", "bridging_slash_b1_jsv", "U+E02C / (B1)", "Modifier (B1)", "Above", "Diagonal Bridging Slash"),
    ("Modifier (C) Dot", "\uE001", "high_dot_jsv", "U+E001 / ॱ", "Modifier (C)", "Shoulder", "Shoulder Pause Dot"),
    ("Modifier (D) Chevron", "\uE006", "roof_jsv", "U+E006 / Ʌ", "Modifier (D)", "Above", "Chevron Roof"),
    ("Modifier (D1) Rise", "\uE00E", "rising_stroke_d1_jsv", "U+E00E / (D1)", "Modifier (D1)", "Above", "Rising Stroke (↗)"),
    ("Modifier (D2) Tick", "\uE00F", "check_tick_d2_jsv", "U+E00F / (D2)", "Modifier (D2)", "Shoulder", "Shoulder Check-Mark Tick (✓)"),
    ("Modifier (E) Danda", "\uE002", "bold_tone_column_jsv", "U+E002 / ┃", "Modifier (E)", "Inline", "Phrasing Heavy Danda"),
    ("Modifier (F) Danda+Dot", "\u2577", "phrasing_danda_jsv", "U+2577 / ╷", "Modifier (F)", "Inline", "Danda with Overhead Dot"),
    ("Modifier (G) Slash", "\uE003", "descending_tone_jsv", "U+E003 / \\", "Modifier (G)", "Below", "Descending Tone Slash"),
    ("Modifier (H) Swarita", "\uE00C", "swarita_jsv", "U+E00C / ॑", "Modifier (H)", "Above", "Overhead Swarita Stroke"),
    ("Modifier (I) Dash", "\uE02A", "double_shoulder_dash_i_jsv", "U+E02A / (I)", "Modifier (I)", "Shoulder", "Double Shoulder Dash (⫽)"),
    ("Modifier (J) Bar", "\uE02B", "overhead_bar_j_jsv", "U+E02B / (J)", "Modifier (J)", "Shoulder", "Horizontal Shoulder Bar (—)"),
    ("Modifier (K) Cross", "\uE02D", "shoulder_cross_k_jsv", "U+E02D / (K)", "Modifier (K)", "Shoulder", "Shoulder Cross Mark (⨯)"),
    ("Inline ( . ) Dot", ".", "dot_inline_jsv", "U+002E / .", "Inline Mark", "Inline", "Inline Staccato Dot"),
    ("Inline ( _ ) Underbar", "_", "underbar_inline_jsv", "U+005F / _", "Inline Mark", "Inline", "Inline Prolongation Bar"),
    ("Inline ( , ) Comma", ",", "comma_inline_jsv", "U+002C / ,", "Inline Mark", "Inline", "Inline Pause Comma"),

    # Row 2: Ayugma pure Grantha bases (A01..A08) from Google Sheet
    ("A01 Ka (അവരോഹം)", "\U00011315", "ka_gran", "U+11315", "Ayugma Swara", "Above", "Ka (Avaroham)"),
    ("A02 Kha (അന്വംഗുല്യം)", "\U00011316", "kha_gran", "U+11316", "Ayugma Swara", "Above", "Kha (Anvangulyam)"),
    ("A03 Ca (ഉദ്ഗമം)", "\U0001131A", "ca_gran", "U+1131A", "Ayugma Swara", "Above", "Ca (Udgamam)"),
    ("A04 Ta (യാനം)", "\U0001131F", "tta_gran", "U+1131F", "Ayugma Swara", "Above", "Ta (Yanam)"),
    ("A05 Nna (ണ-സ്വരം)", "\U00011323", "nna_gran", "U+11323", "Ayugma Swara", "Above", "Nna (\"Na\" Swaram)"),
    ("A06 Ta (ആവർത്തം)", "\U00011324", "ta_gran", "U+11324", "Ayugma Swara", "Above", "Ta (Aavarttam)"),
    ("A07 Tha (ഉത്ഥാനം)", "\U00011325", "tha_gran", "U+11325", "Ayugma Swara", "Above", "Tha (Utthanam)"),
    ("A08 Pa (ക്ഷേപണം)", "\U0001132A", "pa_gran", "U+1132A", "Ayugma Swara", "Above", "Pa (Kshepanam)"),

    # Row 3: Ayugma pure Grantha bases (A09..A16) from Google Sheet
    ("A09 Pha (ഫ-സ്വരം)", "\U0001132B", "pha_gran", "U+1132B", "Ayugma Swara", "Above", "Pha (\"Pha\" Swaram)"),
    ("A10 Bha (മർദ്ദനം)", "\U0001132D", "bha_gran", "U+1132D", "Ayugma Swara", "Above", "Bha (Mardanam)"),
    ("A11 Ya (മർശനം)", "\U0001132F", "ya_gran", "U+1132F", "Ayugma Swara", "Above", "Ya (Marsanam)"),
    ("A12 Sa (അനാമികാമർശനം)", "\U00011338", "sa_gran", "U+11338", "Ayugma Swara", "Above", "Sa (Anamika Marsanam)"),
    ("A13 Sha (Base)", "\u0D36", "sha_mal", "U+0D36 (ശ)", "Manuscript Base", "Above", "Sha (Anuvarnna Suchakah)"),
    ("A14 Ssa (ആദ്യവർണ്ണ)", "\U00011337", "ssa_gran", "U+11337", "Ayugma Swara", "Above", "Ssa (Aadyavarnna Dyotakah)"),
    ("A15 Pla (Vedic Base)", "\uE020", "pla_jsv", "U+E020 / Pla", "Manuscript Base", "Above", "Pla (Plutam)"),
    ("A16 Nga (ങ-സ്വരം)", "\U00011319", "nga_gran", "U+11319", "Ayugma Swara", "Above", "Nga (Ng-Swaram)"),

    # Row 4: Custom bases & Sha-family
    ("A17 Tra (ത്രസ്വരാഖ്യഃ)", "\uE01D", "t_ra_gran", "U+11324+11330", "Ayugma Conjunct", "Above", "Tra (Tra Swarakhyaha)"),
    ("A18 Ra (ദ്രുതസ്ഥാനം)", "\U00011330", "ra_gran", "U+11330", "Ayugma Swara", "Above", "Ra (Druta Swara Indicator)"),
    ("A19 Kra (കൃഷ്ടാഖ്യ)", "\uE01E", "k_ra_jsv", "U+11315+11330", "Ayugma Conjunct", "Above", "Kra (Krishtakhya Bhedah)"),
    ("A13 Sha (Base)", "\u0D36", "sha_mal", "U+0D36 (ശ)", "Malayalam Base", "Above", "Sha Base (Mal)"),
    ("Shaa (Sha+AA)", "\uE010", "sha_aa_jsv", "U+E010 / ശ+ാ", "Manuscript Ligature", "Above", "Shaa Ligature"),
    ("Shi (Sha+I)", "\uE011", "sha_i_jsv", "U+E011 / ശ+ി", "Manuscript Ligature", "Above", "Shi Ligature"),
    ("Shii (Sha+II)", "\uE012", "sha_ii_jsv", "U+E012 / ശ+ീ", "Manuscript Ligature", "Above", "Shii Ligature"),
    ("Sha+Virama", "\uE013", "sha_virama_jsv", "U+E013 / ശ്", "Manuscript Ligature", "Above", "Sha Virama"),
    ("A15 Pla (Vedic Base)", "\uE020", "pla_jsv", "U+E020 / Pla", "Manuscript Base", "Above", "Authentic Vedic Pla"),

    # Row 5: Pla-family & Complex Ligatures
    ("Plaa (Pla+AA)", "\uE021", "pla_aa_jsv", "U+E021 / Pla+ാ", "Manuscript Ligature", "Above", "Plaa Ligature"),
    ("Pli (Pla+I)", "\uE022", "pla_i_jsv", "U+E022 / Pla+ി", "Manuscript Ligature", "Above", "Pli Ligature"),
    ("Plii (Pla+II)", "\uE023", "pla_ii_jsv", "U+E023 / Pla+ീ", "Manuscript Ligature", "Above", "Plii Ligature"),
    ("Shruu (ശ്രൂ)", "\uE027", "sh_ruu_jsv", "U+E027", "Manuscript Ligature", "Above", "Clean Shruu"),
    ("Shrr (ശ്രൃ)", "\uE028", "sh_r_r_jsv", "U+E028", "Manuscript Ligature", "Above", "Clean Shrr"),
    ("Nna+U (ണു)", "\uE029", "nna_u_jsv", "U+E029", "Manuscript Ligature", "Above", "Clean Nna+U"),
    ("Rik Swarita", "\u0951", "swarita_accent_jsv", "U+0951 / (1)", "Rik Accent", "Above", "Udaatta Accent"),
    ("Rik Anudatta", "\u1CD2", "anudatta_accent_jsv", "U+1CD2 / (2)", "Rik Accent", "Above", "Anudatta Bar"),
]


def render_image_grid() -> None:
    cols = 4
    rows = (len(FEATURED_GLYPHS) + cols - 1) // cols
    cell_w, cell_h = 440, 250
    pad_x, pad_y = 60, 110
    w = cols * cell_w + pad_x * 2
    h = rows * cell_h + pad_y * 2 + 100

    img = Image.new("RGB", (w, h), color=(248, 250, 253))
    draw = ImageDraw.Draw(img)

    kartika_path = Path("C:/Windows/Fonts/kartika.ttf")
    kartika_bold = Path("C:/Windows/Fonts/kartikab.ttf")
    try:
        title_font = ImageFont.truetype("arial.ttf", 36)
        label_font = ImageFont.truetype(str(kartika_bold) if kartika_bold.exists() else "arial.ttf", 19)
        sub_font = ImageFont.truetype(str(kartika_path) if kartika_path.exists() else "arial.ttf", 14)
        swara_font = ImageFont.truetype(str(FONT_PATH), 60)
        dotted_font = ImageFont.truetype("seguisym.ttf", 46) if Path("C:/Windows/Fonts/seguisym.ttf").exists() else ImageFont.truetype("arial.ttf", 46)
    except Exception:
        title_font = ImageFont.load_default()
        label_font = ImageFont.load_default()
        sub_font = ImageFont.load_default()
        swara_font = ImageFont.load_default()
        dotted_font = ImageFont.load_default()

    # Header
    draw.text((pad_x, 35), "Jaimineeya Samavedam — Vedic Swara & Modifier Glyph Inventory", fill=(15, 23, 42), font=title_font)
    draw.text((pad_x, 82), "JaimineeyaSwara.ttf — Swara Pitch Markers (Bold Red) & Mantrakshara Modifiers (Dark Blue)", fill=(71, 85, 105), font=label_font)

    # Grid Cells
    for i, (label, char_str, gname, cp_str, category, stack_pos, desc) in enumerate(FEATURED_GLYPHS):
        r = i // cols
        c = i % cols
        x0 = pad_x + c * cell_w
        y0 = pad_y + 30 + r * cell_h
        x1 = x0 + cell_w - 20
        y1 = y0 + cell_h - 20

        # Background card
        is_mod = "Modifier" in category
        bg_fill = (255, 255, 255)
        border_col = (0, 33, 113) if is_mod else (226, 232, 240)
        border_w = 2 if is_mod else 1
        draw.rounded_rectangle([x0, y0, x1, y1], radius=12, fill=bg_fill, outline=border_col, width=border_w)

        # Header tag
        tag_color = (0, 33, 113) if is_mod else (198, 40, 40) if "Ayugma" in category else (21, 101, 192) if "Ligature" in category else (46, 125, 50)
        draw.rounded_rectangle([x0 + 12, y0 + 12, x0 + 125, y0 + 34], radius=6, fill=tag_color)
        draw.text((x0 + 18, y0 + 15), category[:14], fill=(255, 255, 255), font=sub_font)

        # Stacking position tag
        pos_color = (15, 118, 110) if stack_pos == "Shoulder" else (30, 64, 175) if stack_pos == "Above" else (147, 51, 234) if stack_pos == "Below" else (100, 116, 139)
        draw.rounded_rectangle([x0 + 135, y0 + 12, x0 + 245, y0 + 34], radius=6, fill=pos_color)
        draw.text((x0 + 143, y0 + 15), f"Pos: {stack_pos}", fill=(255, 255, 255), font=sub_font)

        # Glyph Box
        draw.rounded_rectangle([x0 + 12, y0 + 46, x0 + 140, y0 + 185], radius=8, fill=(248, 250, 252), outline=(226, 232, 240), width=1)
        bx_cx = x0 + 76
        bx_cy = y0 + 115

        if is_mod:
            # Modifiers rendered in Sky Blue (#0284c7) with Dotted Circle (◌)
            mod_blue = (2, 132, 199)
            dot_gray = (148, 163, 184)
            if "Modifier (A)" in category and "Modifier (A1)" not in category:
                # 2-syllable spanning arc (A)
                draw.text((bx_cx - 22 - 19, bx_cy + 12 - 33), "◌", fill=dot_gray, font=dotted_font)
                draw.text((bx_cx + 22 - 19, bx_cy + 12 - 33), "◌", fill=dot_gray, font=dotted_font)
                draw.text((bx_cx - 41.5, bx_cy - 22 - 33.5), char_str, fill=mod_blue, font=swara_font)
            elif "Modifier (A1)" in category:
                # 2-syllable spanning arc over danda (A1)
                draw.text((bx_cx - 28 - 19, bx_cy + 12 - 33), "◌", fill=dot_gray, font=dotted_font)
                draw.text((bx_cx - 4, bx_cy + 12 - 33), "।", fill=dot_gray, font=dotted_font)
                draw.text((bx_cx + 20 - 19, bx_cy + 12 - 33), "◌", fill=dot_gray, font=dotted_font)
                draw.text((bx_cx - 48, bx_cy - 26 - 33.5), char_str, fill=mod_blue, font=swara_font)
            elif "Modifier (B)" in category:
                # 2-syllable spanning peak caret (B) with Swara marker sitting well above apex (zero collision)
                draw.text((bx_cx - 24 - 19, bx_cy + 25 - 33), "◌", fill=dot_gray, font=dotted_font)
                draw.text((bx_cx + 24 - 19, bx_cy + 25 - 33), "◌", fill=dot_gray, font=dotted_font)
                draw.text((bx_cx - 36, bx_cy - 8 - 17), char_str, fill=mod_blue, font=swara_font)
                # Grantha Kha (\U00011316) sitting cleanly above apex in SwaraRed
                kha_str = chr(0x11316)
                kha_bbox = swara_font.getbbox(kha_str)
                kha_w = kha_bbox[2] - kha_bbox[0]
                draw.text((bx_cx - kha_w / 2, bx_cy - 82), kha_str, fill=(198, 40, 40), font=swara_font)
            elif "Modifier (D)" in category:
                # 2-syllable spanning chevron roof (D)
                draw.text((bx_cx - 22 - 19, bx_cy + 12 - 33), "◌", fill=dot_gray, font=dotted_font)
                draw.text((bx_cx + 22 - 19, bx_cy + 12 - 33), "◌", fill=dot_gray, font=dotted_font)
                draw.text((bx_cx - 39, bx_cy - 22 - 33.5), char_str, fill=mod_blue, font=swara_font)
            elif "Modifier (C)" in category:
                # Shoulder dot (C)
                draw.text((bx_cx - 8 - 19, bx_cy - 33), "◌", fill=dot_gray, font=dotted_font)
                draw.text((bx_cx + 12, bx_cy - 50), char_str, fill=mod_blue, font=swara_font)
            elif "Modifier (E)" in category or "Modifier (F)" in category:
                # Inline danda (E, F)
                draw.text((bx_cx - 12 - 19, bx_cy - 33), "◌", fill=dot_gray, font=dotted_font)
                draw.text((bx_cx + 12, bx_cy - 42), char_str, fill=mod_blue, font=swara_font)
            elif "Modifier (G)" in category:
                # Descending tone slash aligned directly to bottom-center of ◌ (G)
                c_cy = bx_cy - 14
                draw.text((bx_cx - 19, c_cy - 33), "◌", fill=dot_gray, font=dotted_font)
                draw.text((bx_cx - 13, (c_cy + 16) - 65), char_str, fill=mod_blue, font=swara_font)
            elif "Modifier (H)" in category:
                # Overhead swarita tick centered above ◌ (H)
                c_cy = bx_cy + 14
                draw.text((bx_cx - 19, c_cy - 33), "◌", fill=dot_gray, font=dotted_font)
                draw.text((bx_cx, (c_cy - 22) - 65), char_str, fill=mod_blue, font=swara_font)
            elif "Inline Mark" in category:
                draw.text((bx_cx - 19, bx_cy - 33), "◌", fill=dot_gray, font=dotted_font)
                draw.text((bx_cx + 12, bx_cy - 33), char_str, fill=mod_blue, font=label_font)
            else:
                draw.text((bx_cx - 19, bx_cy - 33), "◌", fill=dot_gray, font=dotted_font)
                draw.text((bx_cx + 12, bx_cy - 33), char_str, fill=mod_blue, font=swara_font)
        else:
            # Swara pitch glyphs rendered in Bold SwaraRed (#c62828)
            draw.text((x0 + 45, y0 + 75), char_str, fill=(198, 40, 40), font=swara_font)

        # Labels & metadata
        draw.text((x0 + 155, y0 + 52), label, fill=(15, 23, 42), font=label_font)
        draw.text((x0 + 155, y0 + 82), f"Desc: {desc}", fill=(51, 65, 85), font=sub_font)
        draw.text((x0 + 155, y0 + 108), f"Glyph: {gname}", fill=(71, 85, 105), font=sub_font)
        draw.text((x0 + 155, y0 + 134), f"Code: {cp_str}", fill=(100, 116, 139), font=sub_font)

        # Color note badge
        color_badge_text = "Sky Blue (Mantrakshara Mod)" if is_mod else "Bold Red (Swara Pitch)"
        color_badge_bg = (240, 249, 255) if is_mod else (254, 242, 242)
        color_badge_fg = (2, 132, 199) if is_mod else (198, 40, 40)
        draw.rounded_rectangle([x0 + 12, y0 + 195, x0 + cell_w - 32, y0 + 220], radius=4, fill=color_badge_bg)
        draw.text((x0 + 20, y0 + 200), color_badge_text, fill=color_badge_fg, font=sub_font)

    OUT_IMG.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT_IMG, "PNG")
    print(f"Saved Glyph Grid Image: {OUT_IMG}")
    
    # Copy to artifact directory for UI display
    art_img = ARTIFACT_DIR / "glyph_grid_JaimineeyaSwara.png"
    shutil.copy(OUT_IMG, art_img)
    print(f"Copied to artifact directory: {art_img}")


def render_html_table() -> None:
    csv_path = ROOT / "data" / "output" / "malayalam" / "samhita_marker_review.csv"
    if not csv_path.exists():
        csv_path = ROOT / "Malayalam_JSV" / "samhita_marker_review.csv"

    rows = []
    if csv_path.exists():
        with open(csv_path, encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))

    import base64
    jaimineeya_swara_b64 = ""
    if FONT_PATH.exists():
        with open(FONT_PATH, "rb") as f_font:
            jaimineeya_swara_b64 = base64.b64encode(f_font.read()).decode("ascii")

    # All Canonical Vedic Swara Modifiers (A..H + Inline . _ ,)
    modifiers = [
        {
            "id": "MOD-A",
            "shortcut": "(A)",
            "name": "Syllable Spanning Melodic Arc (⁀)",
            "glyph": "\uE004",
            "codepoint": "U+E004 / ╭╮ / ⁀",
            "input_methods": "<code>(A)</code> / <code>(a)</code> / <code>(╭╮)</code> / <code>(⁀)</code>",
            "stack_pos": "Stacked Above",
            "dotted_rep": "<span class='dotted-sample'><span class='base-circle-box'>◌&nbsp;&nbsp;◌<span class='swara-mod-dotted mod-a-dotted'>&#xE004;</span></span></span>",
            "example_text": "ഹോ(𑌖)(A) ബാ(𑌪𑍍𑌲)",
            "example_preview": "<div class='mantra-preview-flex'><span class='mantra-word'><span class='swara-text'>𑌖</span><span class='mantra-text'>ഹോ<span class='swara-mod mod-a'>&#xE004;</span></span></span><span class='word-space'>&nbsp;</span><span class='mantra-word'><span class='swara-text'>&#xE020;</span><span class='mantra-text'>ബാ</span></span></div>",
            "meaning": "Smooth flatter melodic slur bridging two adjacent syllables.",
            "color_note": "Sky Blue (#0284c7) on Mantrakshara"
        },
        {
            "id": "MOD-A1",
            "shortcut": "(A1)",
            "name": "Syllable Spanning Arc over Danda (MOD-A1)",
            "glyph": "\uE00D",
            "codepoint": "U+E00D / (A1) / (A_1)",
            "input_methods": "<code>(A1)</code> / <code>(a1)</code> / <code>(A_1)</code> / <code>(a_1)</code>",
            "stack_pos": "Stacked Above (Over Danda)",
            "dotted_rep": "<span class='dotted-sample'><span class='base-circle-box'>◌&nbsp;।&nbsp;◌<span class='swara-mod-dotted mod-a1-dotted'>&#xE00D;</span></span></span>",
            "example_text": "തൊ(𑌤)(A1) । ഹാ(𑌟𑌾)",
            "example_preview": "<div class='mantra-preview-flex'><span class='mantra-word'><span class='swara-text'>𑌤</span><span class='mantra-text'>തൊ<span class='swara-mod mod-a1'>&#xE00D;</span></span></span><span class='mantra-text'><span class='danda'>।</span></span><span class='word-space'>&nbsp;</span><span class='mantra-word'><span class='swara-text'>𑌟𑌾</span><span class='mantra-text'>ഹാ</span></span></div>",
            "meaning": "Overhead melodic slur bridging two adjacent syllables across a danda separator.",
            "color_note": "Sky Blue (#0284c7) on Mantrakshara"
        },
        {
            "id": "MOD-B",
            "shortcut": "(B)",
            "name": "Peak Caret Roof (/\\ / ^)",
            "glyph": "\uE005",
            "codepoint": "U+E005 / ^ / /\\",
            "input_methods": "<code>(B)</code> / <code>(b)</code> / <code>(^)</code> / <code>(/\\)</code>",
            "stack_pos": "Stacked Above",
            "dotted_rep": "<span class='dotted-sample'><span class='base-circle-box'>◌&nbsp;&nbsp;◌<span class='swara-mod-dotted mod-b-dotted'>&#xE005;</span><span class='swara-on-caret-dotted'>𑌖</span></span></span>",
            "example_text": "ഹോ(𑌖)(B) ബാ",
            "example_preview": "<div class='mantra-preview-flex'><span class='mantra-word'><span class='swara-text'>&nbsp;</span><span class='mantra-text'>ഹോ<span class='swara-mod mod-b'><span class='caret-glyph'>&#xE005;</span><span class='swara-on-caret'>𑌖</span></span></span></span><span class='word-space'>&nbsp;</span><span class='mantra-word'><span class='swara-text'>&nbsp;</span><span class='mantra-text'>ബാ</span></span></div>",
            "meaning": "Peak pitch crest over consonant with embedded swara glyph above apex.",
            "color_note": "Sky Blue (#0284c7) on Mantrakshara + SwaraRed (#c62828) Marker above Apex"
        },
        {
            "id": "MOD-B1",
            "shortcut": "(B1)",
            "name": "Diagonal Bridging Slash (/ / ↗)",
            "glyph": "\uE02C",
            "codepoint": "U+E02C / (B1)",
            "input_methods": "<code>(B1)</code> / <code>(b1)</code>",
            "stack_pos": "Stacked Above",
            "dotted_rep": "<span class='dotted-sample'><span class='base-circle-box'>◌&nbsp;&nbsp;◌<span class='swara-mod-dotted mod-b1-dotted'>&#xE02C;</span></span></span>",
            "example_text": "സ്രൗ(𑌵)(B1) ധാഃ",
            "example_preview": "<div class='mantra-preview-flex'><span class='mantra-word'><span class='swara-text'>𑌵</span><span class='mantra-text'>സ്രൗ<span class='swara-mod mod-b1'>&#xE02C;</span></span></span><span class='word-space'>&nbsp;</span><span class='mantra-word'><span class='swara-text'>&nbsp;</span><span class='mantra-text'>ധാഃ</span></span></div>",
            "meaning": "Diagonal bridging slash rising between syllables with swara above.",
            "color_note": "Sky Blue (#0284c7) on Mantrakshara"
        },
        {
            "id": "MOD-C",
            "shortcut": "(C)",
            "name": "Upper Shoulder Dot (· / ॱ)",
            "glyph": "\uE001",
            "codepoint": "U+E001 / U+00B7 / ·",
            "input_methods": "<code>(C)</code> / <code>(c)</code> / <code>(ॱ)</code> / <code>(·)</code>",
            "stack_pos": "Shoulder",
            "dotted_rep": "<span class='dotted-sample'><span class='base-circle-box'>◌<span class='swara-mod-dotted mod-c-dotted'>&#xE001;</span></span></span>",
            "example_text": "ഓ(𑌤)(C) ഗ്നാ(𑌤)",
            "example_preview": "<div class='mantra-preview-flex'><span class='mantra-word'><span class='swara-text'>𑌤</span><span class='mantra-text'>ഓ<span class='swara-mod mod-c'>&#xE001;</span></span></span><span class='word-space'>&nbsp;</span><span class='mantra-word'><span class='swara-text'>𑌤</span><span class='mantra-text'>ഗ്നാ</span></span></div>",
            "meaning": "Staccato stress pulse attached to syllable curve (Bindu-Svara).",
            "color_note": "Sky Blue (#0284c7) on Mantrakshara"
        },
        {
            "id": "MOD-D",
            "shortcut": "(D)",
            "name": "Chevron Roof (∧ / Ʌ)",
            "glyph": "\uE006",
            "codepoint": "U+E006 / U+0245 / Ʌ",
            "input_methods": "<code>(D)</code> / <code>(d)</code> / <code>(∧)</code> / <code>(Ʌ)</code>",
            "stack_pos": "Stacked Above",
            "dotted_rep": "<span class='dotted-sample'><span class='base-circle-box'>◌&nbsp;&nbsp;◌<span class='swara-mod-dotted mod-d-dotted'>&#xE006;</span></span></span>",
            "example_text": "ഹോ(𑌪𑍍𑌲)(D) ഇഴാ(𑌶𑌾)",
            "example_preview": "<div class='mantra-preview-flex'><span class='mantra-word'><span class='swara-text'>&#xE020;</span><span class='mantra-text'>ഹോ<span class='swara-mod mod-d'>&#xE006;</span></span></span><span class='word-space'>&nbsp;</span><span class='mantra-word'><span class='swara-text'>&nbsp;</span><span class='mantra-text'>ഇ</span></span><span class='mantra-word'><span class='swara-text'>&#xE010;</span><span class='mantra-text'>ഴാ</span></span></div>",
            "meaning": "Span-roof inflection indicator across word boundaries.",
            "color_note": "Sky Blue (#0284c7) on Mantrakshara"
        },
        {
            "id": "MOD-D1",
            "shortcut": "(D1)",
            "name": "Asymmetrical Inverted-V / Hooked Rise (⋀)",
            "glyph": "\uE00E",
            "codepoint": "U+E00E / (D1) / ↗",
            "input_methods": "<code>(D1)</code> / <code>(d1)</code> / <code>↗</code>",
            "stack_pos": "Stacked Above",
            "dotted_rep": "<span class='dotted-sample'><span class='base-circle-box'>◌&nbsp;&nbsp;◌<span class='swara-mod-dotted mod-d1-dotted'>&#xE00E;</span></span></span>",
            "example_text": "യാ(𑌯)(D1) വാ",
            "example_preview": "<div class='mantra-preview-flex'><span class='mantra-word'><span class='swara-text'>𑌯</span><span class='mantra-text'>യാ<span class='swara-mod mod-d1'>&#xE00E;</span></span></span><span class='word-space'>&nbsp;</span><span class='mantra-word'><span class='swara-text'>&nbsp;</span><span class='mantra-text'>വാ</span></span></div>",
            "meaning": "Asymmetrical inverted-V with a long rising left leg and a shorter downward-sloping right hook.",
            "color_note": "Sky Blue (#0284c7) on Mantrakshara"
        },
        {
            "id": "MOD-D2",
            "shortcut": "(D2)",
            "name": "Shoulder Check-Mark Tick (✓)",
            "glyph": "\uE00F",
            "codepoint": "U+E00F / (D2) / ✓",
            "input_methods": "<code>(D2)</code> / <code>(d2)</code> / <code>✓</code>",
            "stack_pos": "Shoulder",
            "dotted_rep": "<span class='dotted-sample'><span class='base-circle-box'>◌<span class='swara-mod-dotted mod-d2-dotted'>&#xE00F;</span></span></span>",
            "example_text": "ണോ(𑌣)(D2)",
            "example_preview": "<div class='mantra-preview-flex'><span class='mantra-word'><span class='swara-text'>𑌣</span><span class='mantra-text'>ണോ<span class='swara-mod mod-d2'>&#xE00F;</span></span></span></div>",
            "meaning": "Check-mark tick stroke placed directly on the upper-right shoulder.",
            "color_note": "Sky Blue (#0284c7) on Mantrakshara"
        },
        {
            "id": "MOD-E",
            "shortcut": "(E)",
            "name": "Bold Tone Column (┃)",
            "glyph": "\uE002",
            "codepoint": "U+E002 / U+2503 / ┃",
            "input_methods": "<code>(E)</code> / <code>(e)</code> / <code>(┃)</code>",
            "stack_pos": "Inline",
            "dotted_rep": "<span class='dotted-sample'><span class='base-circle-box'>◌<span class='swara-mod-dotted mod-e-dotted'>&#xE002;</span></span></span>",
            "example_text": "വാ(𑌚)(E)",
            "example_preview": "<div class='mantra-preview-flex'><span class='mantra-word'><span class='swara-text'>𑌚</span><span class='mantra-text'>വാ<span class='swara-mod mod-e'>&#xE002;</span></span></span></div>",
            "meaning": "Heavy vertical phrase partition and caesura pause.",
            "color_note": "Sky Blue (#0284c7) on Mantrakshara"
        },
        {
            "id": "MOD-F",
            "shortcut": "(F)",
            "name": "Danda with Overhead Dot (╷ with Dot Above)",
            "glyph": "\u2577",
            "codepoint": "U+2577 / (F)",
            "input_methods": "<code>(F)</code> / <code>(f)</code> / <code>(╷)</code>",
            "stack_pos": "Inline",
            "dotted_rep": "<span class='dotted-sample'><span class='base-circle-box'>◌<span class='swara-mod-dotted mod-f-dotted'>&#x2577;</span></span></span>",
            "example_text": "ഇ(𑌚)(F)",
            "example_preview": "<div class='mantra-preview-flex'><span class='mantra-word'><span class='swara-text'>𑌚</span><span class='mantra-text'>ഇ<span class='swara-mod mod-f'>&#x2577;</span></span></span></div>",
            "meaning": "Inline vertical stroke with a distinct dot positioned directly above it.",
            "color_note": "Sky Blue (#0284c7) on Mantrakshara"
        },
        {
            "id": "MOD-G",
            "shortcut": "(G)",
            "name": "Lower Under-Slash (\\ / ⟍)",
            "glyph": "\uE003",
            "codepoint": "U+E003 / U+005C / \\",
            "input_methods": "<code>(G)</code> / <code>(g)</code> / <code>(\\)</code> / <code>(⟍)</code>",
            "stack_pos": "Stacked Below",
            "dotted_rep": "<span class='dotted-sample'><span class='base-circle-box'>◌<span class='swara-mod-dotted mod-g-dotted'>&#xE003;</span></span></span>",
            "example_text": "ബാ(𑌪𑍍𑌲)(G)",
            "example_preview": "<div class='mantra-preview-flex'><span class='mantra-word'><span class='swara-text'>&#xE020;</span><span class='mantra-text'>ബാ<span class='swara-mod mod-g'>&#xE003;</span></span></span></div>",
            "meaning": "Subscript downward sliding glide attached beneath the mantrakshara baseline.",
            "color_note": "Sky Blue (#0284c7) on Mantrakshara"
        },
        {
            "id": "MOD-H",
            "shortcut": "(H)",
            "name": "High Pitch Swarita (॑ / |)",
            "glyph": "\uE00C",
            "codepoint": "U+E00C / U+007C / |",
            "input_methods": "<code>(H)</code> / <code>(h)</code> / <code>(L)</code> / <code>(|)</code> / <code>(॑)</code>",
            "stack_pos": "Stacked Above",
            "dotted_rep": "<span class='dotted-sample'><span class='base-circle-box'>◌<span class='swara-mod-dotted mod-h-dotted'>&#xE00C;</span></span></span>",
            "example_text": "ദാ(𑌚𑌿)(H)",
            "example_preview": "<div class='mantra-preview-flex'><span class='mantra-word'><span class='swara-text'>𑌚𑌿</span><span class='mantra-text'>ദാ<span class='swara-mod mod-h'>&#xE00C;</span></span></span></div>",
            "meaning": "Vedic high pitch tone marker placed directly above the mantrakshara.",
            "color_note": "Sky Blue (#0284c7) on Mantrakshara"
        },
        {
            "id": "MOD-I",
            "shortcut": "(I)",
            "name": "Two Stacked Parallel Shoulder Dashes (═)",
            "glyph": "\uE02A",
            "codepoint": "U+E02A / (I) / ═",
            "input_methods": "<code>(I)</code> / <code>(i)</code> / <code>═</code>",
            "stack_pos": "Shoulder",
            "dotted_rep": "<span class='dotted-sample'><span class='base-circle-box'>◌<span class='swara-mod-dotted mod-i-dotted'>&#xE02A;</span></span></span>",
            "example_text": "ഗ്നാ(𑌤)(I)",
            "example_preview": "<div class='mantra-preview-flex'><span class='mantra-word'><span class='swara-text'>𑌤</span><span class='mantra-text'>ഗ്നാ<span class='swara-mod mod-i'>&#xE02A;</span></span></span></div>",
            "meaning": "Two stacked parallel gently-rising bars attached directly to the upper-right shoulder.",
            "color_note": "Sky Blue (#0284c7) on Mantrakshara"
        },
        {
            "id": "MOD-J",
            "shortcut": "(J)",
            "name": "Horizontal Shoulder Bar (—)",
            "glyph": "\uE02B",
            "codepoint": "U+E02B / (J) / —",
            "input_methods": "<code>(J)</code> / <code>(j)</code> / <code>—</code>",
            "stack_pos": "Shoulder",
            "dotted_rep": "<span class='dotted-sample'><span class='base-circle-box'>◌<span class='swara-mod-dotted mod-j-dotted'>&#xE02B;</span></span></span>",
            "example_text": "ഹോ(𑌖)(J)",
            "example_preview": "<div class='mantra-preview-flex'><span class='mantra-word'><span class='swara-text'>𑌖</span><span class='mantra-text'>ഹോ<span class='swara-mod mod-j'>&#xE02B;</span></span></span></div>",
            "meaning": "Horizontal straight bar attached directly on the upper-right shoulder.",
            "color_note": "Sky Blue (#0284c7) on Mantrakshara"
        },
        {
            "id": "MOD-K",
            "shortcut": "(K)",
            "name": "Shoulder Cross Mark (⨯ / x)",
            "glyph": "\uE02D",
            "codepoint": "U+E02D / (K) / ⨯",
            "input_methods": "<code>(K)</code> / <code>(k)</code> / <code>⨯</code> / <code>x</code>",
            "stack_pos": "Shoulder",
            "dotted_rep": "<span class='dotted-sample'><span class='base-circle-box'>◌<span class='swara-mod-dotted mod-k-dotted'>&#xE02D;</span></span></span>",
            "example_text": "വാ(𑌵)(K)",
            "example_preview": "<div class='mantra-preview-flex'><span class='mantra-word'><span class='swara-text'>𑌵</span><span class='mantra-text'>വാ<span class='swara-mod mod-k'>&#xE02D;</span></span></span></div>",
            "meaning": "Small cross / X mark on upper-right shoulder.",
            "color_note": "Sky Blue (#0284c7) on Mantrakshara"
        },
        {
            "id": "MOD-DOT",
            "shortcut": "( . )",
            "name": "Inline Staccato Dot ( . )",
            "glyph": ".",
            "codepoint": "U+002E / .",
            "input_methods": "<code>.</code> / <code>(.)</code> / <code>(·)</code>",
            "stack_pos": "Inline",
            "dotted_rep": "<span class='dotted-sample'><span class='base-circle-box'>◌<span class='swara-mod-dotted' style='font-size:1.4em; font-weight:bold; color:var(--mod-blue); margin-left:0.1em; line-height:1;'>.</span></span></span>",
            "example_text": "വാ(𑌚).",
            "example_preview": "<div class='mantra-preview-flex'><span class='mantra-word'><span class='swara-text'>𑌚</span><span class='mantra-text'>വാ</span></span><span class='mantra-punct'>.</span></div>",
            "meaning": "Inline staccato pulse mark placed directly in the text flow.",
            "color_note": "Sky Blue (#0284c7) on Mantrakshara"
        },
        {
            "id": "MOD-UNDERBAR",
            "shortcut": "( _ )",
            "name": "Inline Sustain Underbar ( _ )",
            "glyph": "_",
            "codepoint": "U+005F / _",
            "input_methods": "<code>_</code> / <code>(_)</code>",
            "stack_pos": "Inline",
            "dotted_rep": "<span class='dotted-sample'><span class='base-circle-box'>◌<span class='swara-mod-dotted' style='font-size:1.3em; font-weight:bold; color:var(--mod-blue); margin-left:0.1em;'>_</span></span></span>",
            "example_text": "ഇ(𑌚)_",
            "example_preview": "<div class='mantra-preview-flex'><span class='mantra-word'><span class='swara-text'>𑌚</span><span class='mantra-text'>ഇ</span></span><span class='mantra-punct'>_</span></div>",
            "meaning": "Inline sustain prolongation bar connecting adjacent words or chanting units.",
            "color_note": "Sky Blue (#0284c7) on Mantrakshara"
        },
        {
            "id": "MOD-COMMA",
            "shortcut": "( , )",
            "name": "Inline Short Pause Comma ( , )",
            "glyph": ",",
            "codepoint": "U+002C / ,",
            "input_methods": "<code>,</code> / <code>(,)</code>",
            "stack_pos": "Inline",
            "dotted_rep": "<span class='dotted-sample'><span class='base-circle-box'>◌<span class='swara-mod-dotted' style='font-size:1.3em; font-weight:bold; color:var(--mod-blue); margin-left:0.1em;'>,</span></span></span>",
            "example_text": "ദാ(𑌚),",
            "example_preview": "<div class='mantra-preview-flex'><span class='mantra-word'><span class='swara-text'>𑌚</span><span class='mantra-text'>ദാ</span></span><span class='mantra-punct'>,</span></div>",
            "meaning": "Inline short rhythmic pause marker within the chant.",
            "color_note": "Sky Blue (#0284c7) on Mantrakshara"
        },
    ]

    # Modifier HTML Rows
    modifier_rows_html = []
    for m in modifiers:
        stack_badge = "badge-above" if m['stack_pos'] == "Stacked Above" else "badge-below" if m['stack_pos'] == "Stacked Below" else "badge-shoulder" if m['stack_pos'] == "Shoulder" else "badge-inline"
        modifier_rows_html.append(f"""
        <tr data-type="modifier">
            <td class="idx-col"><strong>{m['id']}</strong></td>
            <td><strong class="shortcut-tag">{m['shortcut']}</strong></td>
            <td><strong>{m['name']}</strong><div class="mod-desc">{m['meaning']}</div></td>
            <td>{m['input_methods']}</td>
            <td class="glyph-cell"><span class="swara-glyph mod-glyph">{m['glyph']}</span></td>
            <td class="dotted-cell">{m['dotted_rep']}</td>
            <td class="preview-cell">{m['example_preview']}</td>
            <td><code>{m['codepoint']}</code></td>
            <td><span class="badge {stack_badge}">{m['stack_pos']}</span></td>
        </tr>
        """)

    # Ayugma Bases table from Google Sheet (A01..A19)
    ayugma_bases = [
        ("A01", "Ka", "ക", "𑌕", "U+11315", "Avaroham (അവരോഹം)", "Odd swara"),
        ("A02", "Kha", "ഖ", "𑌖", "U+11316", "Anvangulyam (അന്വംഗുല്യം)", "Odd swara"),
        ("A03", "Ca", "ച", "𑌚", "U+1131A", "Udgamam (ഉദ്ഗമം)", "Odd swara"),
        ("A04", "Ta", "ട", "𑌟", "U+1131F", "Yanam (യാനം)", "Odd swara"),
        ("A05", "Ṇa", "ണ", "𑌣", "U+11323", "\"Na\" Swaram (\"ണ\" സ്വരം)", "Odd swara"),
        ("A06", "Ta", "ത", "𑌤", "U+11324", "Aavarttam (ആവർത്തം)", "Odd swara"),
        ("A07", "Tha", "ഥ", "𑌥", "U+11325", "Utthanam (ഉത്ഥാനം)", "Odd swara"),
        ("A08", "Pa", "പ", "𑌪", "U+1132A", "Kshepanam (ക്ഷേപണം)", "Odd swara"),
        ("A09", "Pha", "ഫ", "𑌫", "U+1132B", "\"Pha\" Swaram (ഫ-സ്വരം)", "Odd swara"),
        ("A10", "Bha", "ഭ", "𑌭", "U+1132D", "Mardanam (മർദ്ദനം)", "Odd swara"),
        ("A11", "Ya", "യ", "𑌯", "U+1132F", "Marsanam (മർശനം)", "Odd swara"),
        ("A12", "Sa", "സ", "𑌸", "U+11338", "Anamika Marsanam (അനാമികാമർശനം)", "Odd swara"),
        ("A13", "Sha (Mal)", "ശ", "ശ", "U+0D36", "Anuvarnna Swara Rahitya Suchakah", "Manuscript Base"),
        ("A14", "Ssa", "ഷ", "𑌷", "U+11337", "Aadyavarnna Swaraa Bhava Dyotakah", "Odd swara"),
        ("A15", "Pla (Vedic)", "പ്ല", "\uE020", "U+E020", "\"Pla\" Swara Ityucyamanaha (\"പ്ല\" സ്വര ഇത്യുച്യമാനഃ)", "Manuscript Base"),
        ("A16", "Nga", "ങ", "𑌙", "U+11319", "Ng-Swaram (\"ങ\" സ്വര ഇത്യുച്യമാനഃ)", "Odd swara"),
        ("A17", "Tra", "ത്ര", "\uE01D", "U+E01D", "Tra Swarakhyaha (ത്രസ്വരാഖ്യഃ)", "Conjunct"),
        ("A18", "Ra", "ര", "𑌰", "U+11330", "Druta Swara Position Indicator", "Odd swara"),
        ("A19", "Kra", "ക്ര", "\uE01E", "U+E01E", "Krishtakhya Swara Bhedah (കൃഷ്ടാഖ്യ സ്വര ഭേദഃ)", "Conjunct"),
    ]

    ayugma_rows_html = []
    for aid, m_name, m_char, g_char, hex_code, meaning, notes in ayugma_bases:
        ayugma_rows_html.append(f"""
        <tr data-type="ayugma">
            <td class="idx-col"><strong>{aid}</strong></td>
            <td><strong>{m_name}</strong></td>
            <td style="font-family:'Noto Serif Malayalam'; font-size:22px; font-weight:bold;">{m_char}</td>
            <td class="glyph-cell"><span class="swara-glyph swara-red">{g_char}</span></td>
            <td><code>{hex_code}</code></td>
            <td>{meaning}</td>
            <td><span class="badge badge-base">{notes}</span></td>
        </tr>
        """)

    # Manuscript Ligatures table
    ligatures = [
        ("LIG-01", "Shaa (Sha+AA)", "\uE010", "U+E010 / 0D36+1133E", "ശ + 𑌾 (Grantha separate right arm)", "Stacked Above"),
        ("LIG-02", "Shi (Sha+I)", "\uE011", "U+E011 / 0D36+1133F", "ശ + 𑌿 (Grantha authentic iMatra attached to right lobe)", "Stacked Above"),
        ("LIG-03", "Shii (Sha+II)", "\uE012", "U+E012 / 0D36+11340", "ശ + 𑍀 (Grantha iiMatra attached to right lobe)", "Stacked Above"),
        ("LIG-04", "Sha+Virama", "\uE013", "U+E013 / 0D36+1134D", "ശ + ് (Malayalam virama)", "Stacked Above"),
        ("LIG-05", "Plaa (Pla+AA)", "\uE021", "U+E021 / Pla+1133E", "Vedic Pla + Grantha separate right arm", "Stacked Above"),
        ("LIG-06", "Pli (Pla+I)", "\uE022", "U+E022 / Pla+1133F", "pi_gran + subjoined Malayalam La", "Stacked Above"),
        ("LIG-07", "Plii (Pla+II)", "\uE023", "U+E023 / Pla+11340", "pii_gran + subjoined Malayalam La", "Stacked Above"),
        ("LIG-08", "Shruu (ശ്രൂ)", "\uE027", "U+E027", "Clean composite without dotted circles", "Stacked Above"),
        ("LIG-09", "Shrr (ശ്രൃ)", "\uE028", "U+E028", "Clean composite without dotted circles", "Stacked Above"),
        ("LIG-10", "Nna+U (ണു)", "\uE029", "U+E029", "Nna with right-attached uMatra without collision", "Stacked Above"),
    ]

    liga_rows_html = []
    for lid, lname, lglyph, lcode, ldesc, lpos in ligatures:
        liga_rows_html.append(f"""
        <tr data-type="ligature">
            <td class="idx-col"><strong>{lid}</strong></td>
            <td><strong>{lname}</strong></td>
            <td class="glyph-cell"><span class="swara-glyph swara-red">{lglyph}</span></td>
            <td><code>{lcode}</code></td>
            <td>{ldesc}</td>
            <td><span class="badge badge-above">{lpos}</span></td>
        </tr>
        """)

    # Swara Markers Rows
    swara_rows_html = []
    for idx, r in enumerate(rows, 1):
        marker = r.get("marker", "")
        count = r.get("count", "")
        hex_str = r.get("grantha_hex", "")
        text_str = r.get("grantha_text", "")
        match_id = r.get("sheet_entry_match", "")

        if any(c in marker for c in ["प्ल", "प्लि", "प्ली", "प्ला"]):
            cat = "Pla Hybrid Base"
            badge_cls = "badge-pla"
        elif "श" in marker:
            cat = "Sha Malayalam Base"
            badge_cls = "badge-sha"
        elif match_id:
            cat = f"Ayugma Base ({match_id})"
            badge_cls = "badge-base"
        elif len(hex_str.split()) > 1:
            cat = "Compound / Ligature"
            badge_cls = "badge-liga"
        else:
            cat = "Grantha Swara"
            badge_cls = "badge-base"

        swara_rows_html.append(f"""
        <tr data-type="corpus">
            <td class="idx-col">{idx}</td>
            <td><strong>({marker})</strong></td>
            <td class="glyph-cell"><span class="swara-glyph swara-red">{text_str}</span></td>
            <td><code>{hex_str}</code></td>
            <td><span class="badge {badge_cls}">{cat}</span></td>
            <td class="count-cell">{count}</td>
        </tr>
        """)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Jaimineeya Swara Font — Complete Glyph Inventory & Modifiers Review</title>
<style>
    @font-face {{
        font-family: 'JaimineeyaSwara';
        src: url('../fonts/JaimineeyaSwara.ttf') format('truetype'),
             url('./fonts/JaimineeyaSwara.ttf') format('truetype'),
             url('/fonts/JaimineeyaSwara.ttf') format('truetype'),
             url('data:font/truetype;charset=utf-8;base64,{jaimineeya_swara_b64}') format('truetype');
    }}
    @font-face {{
        font-family: 'Noto Serif Malayalam';
        src: url('https://fonts.gstatic.com/s/notoserifmalayalam/v28/0FlZVP2yodst28XFviZkH8UfGvjFmsF4Yw.woff2') format('woff2');
    }}

    :root {{
        --bg-main: #f8fafc;
        --card-bg: #ffffff;
        --text-main: #0f172a;
        --text-muted: #64748b;
        --primary-blue: #002171;
        --mod-blue: #0284c7;
        --swara-red: #c62828;
        --border-color: #e2e8f0;
    }}

    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        background: var(--bg-main);
        color: var(--text-main);
        padding: 30px 20px;
        line-height: 1.5;
    }}
    .container {{
        max-width: 1300px;
        margin: 0 auto;
    }}
    header {{
        background: linear-gradient(135deg, #002171 0%, #1e3a8a 100%);
        color: white;
        padding: 36px 32px;
        border-radius: 16px;
        margin-bottom: 30px;
        box-shadow: 0 10px 25px -5px rgba(0, 33, 113, 0.2);
    }}
    h1 {{
        font-size: 28px;
        font-weight: 800;
        letter-spacing: -0.5px;
        margin-bottom: 8px;
    }}
    .subtitle {{
        font-size: 15px;
        color: #bfdbfe;
        max-width: 900px;
        line-height: 1.6;
    }}
    .color-legend {{
        display: flex;
        gap: 20px;
        margin-top: 18px;
        flex-wrap: wrap;
    }}
    .legend-item {{
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 13px;
        font-weight: 600;
        background: rgba(255, 255, 255, 0.12);
        padding: 6px 14px;
        border-radius: 20px;
        backdrop-filter: blur(4px);
    }}
    .legend-dot {{
        width: 12px;
        height: 12px;
        border-radius: 50%;
    }}
    .dot-red {{ background: #ef4444; border: 2px solid white; }}
    .dot-blue {{ background: #0284c7; border: 2px solid white; }}

    .nav-tabs {{
        display: flex;
        gap: 10px;
        margin-bottom: 24px;
        border-bottom: 2px solid var(--border-color);
        padding-bottom: 8px;
        overflow-x: auto;
    }}
    .tab-btn {{
        background: transparent;
        border: none;
        padding: 10px 18px;
        font-size: 15px;
        font-weight: 700;
        color: var(--text-muted);
        cursor: pointer;
        border-radius: 8px;
        transition: all 0.2s ease;
    }}
    .tab-btn:hover {{
        background: #e2e8f0;
        color: var(--text-main);
    }}
    .tab-btn.active {{
        background: var(--primary-blue);
        color: white;
    }}

    .section-card {{
        background: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: 14px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
        margin-bottom: 30px;
        overflow: hidden;
    }}
    .section-header {{
        background: #f8fafc;
        border-bottom: 1px solid var(--border-color);
        padding: 16px 24px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }}
    .section-title {{
        font-size: 18px;
        font-weight: 700;
        color: var(--text-main);
        display: flex;
        align-items: center;
        gap: 10px;
    }}
    .section-tag {{
        font-size: 12px;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 700;
        text-transform: uppercase;
    }}
    .tag-modifiers {{ background: #e0e7ff; color: #3730a3; }}
    .tag-ayugma {{ background: #fee2e2; color: #991b1b; }}
    .tag-liga {{ background: #dbeafe; color: #1e40af; }}
    .tag-all {{ background: #dcfce7; color: #166534; }}

    /* DOTTED CIRCLE REPRESENTATION CELL */
    .dotted-cell {{
        width: 140px;
        text-align: center;
    }}
    .dotted-sample {{
        display: inline-flex;
        align-items: center;
        justify-content: center;
        background: #ffffff;
        border: 1px solid var(--border-color);
        padding: 8px 14px;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }}
    .base-circle-box {{
        position: relative;
        display: inline-block;
        font-family: 'Segoe UI Symbol', 'Noto Sans Malayalam', sans-serif;
        font-size: 1.4rem;
        color: var(--text-muted);
        line-height: 1.2;
        letter-spacing: 2px;
        user-select: none;
    }}
    .swara-mod-dotted {{
        font-family: 'JaimineeyaSwara', serif;
        font-weight: bold;
        line-height: 1;
        pointer-events: none;
    }}
    .swara-mod-dotted.mod-a-dotted {{
        position: absolute;
        top: -0.22em;
        left: 50%;
        transform: translateX(-50%);
        font-size: 1.15em;
        color: var(--mod-blue);
    }}
    .swara-mod-dotted.mod-a1-dotted {{
        position: absolute;
        top: -0.22em;
        left: 50%;
        transform: translateX(-50%);
        font-size: 1.25em;
        color: var(--mod-blue);
    }}
    .swara-mod-dotted.mod-b-dotted {{
        position: absolute;
        top: -0.22em;
        left: 50%;
        transform: translateX(-50%);
        font-size: 1.15em;
        color: var(--mod-blue);
    }}
    .swara-on-caret-dotted {{
        position: absolute;
        top: -1.70em;
        left: 50%;
        transform: translateX(-50%);
        color: #c62828;
        font-family: 'JaimineeyaSwara', serif;
        font-size: 1.05em;
        font-weight: bold;
        line-height: 1;
        pointer-events: none;
    }}
    .swara-mod-dotted.mod-c-dotted {{
        position: absolute;
        top: -0.15em;
        right: -0.35em;
        font-size: 1.05em;
        color: var(--mod-blue);
    }}
    .swara-mod-dotted.mod-d-dotted {{
        position: absolute;
        top: -0.24em;
        left: 50%;
        transform: translateX(-50%);
        font-size: 1.15em;
        color: var(--mod-blue);
    }}
    .swara-mod-dotted.mod-b1-dotted {{
        position: absolute;
        top: -0.22em;
        left: 50%;
        transform: translateX(-50%);
        font-size: 1.15em;
        color: var(--mod-blue);
    }}
    .swara-mod-dotted.mod-d1-dotted {{
        position: absolute;
        top: -0.28em;
        left: 50%;
        transform: translateX(-50%);
        font-size: 1.45em;
        color: var(--mod-blue);
    }}
    .swara-mod-dotted.mod-d2-dotted {{
        position: absolute;
        top: -0.22em;
        right: -0.38em;
        font-size: 1.45em;
        color: var(--mod-blue);
    }}
    .swara-mod-dotted.mod-i-dotted {{
        position: absolute;
        top: -0.22em;
        right: -0.38em;
        font-size: 1.45em;
        color: var(--mod-blue);
    }}
    .swara-mod-dotted.mod-j-dotted {{
        position: absolute;
        top: -0.22em;
        right: -0.38em;
        font-size: 1.45em;
        color: var(--mod-blue);
    }}
    .swara-mod-dotted.mod-k-dotted {{
        position: absolute;
        top: -0.22em;
        right: -0.38em;
        font-size: 1.45em;
        color: var(--mod-blue);
    }}
    .swara-mod-dotted.mod-e-dotted {{
        position: relative;
        margin-left: 0.15em;
        font-size: 1.25em;
        vertical-align: -0.05em;
        color: var(--mod-blue);
    }}
    .swara-mod-dotted.mod-f-dotted {{
        position: relative;
        margin-left: 0.15em;
        font-size: 1.25em;
        vertical-align: -0.05em;
        color: var(--mod-blue);
    }}
    .swara-mod-dotted.mod-g-dotted {{
        position: absolute;
        bottom: -0.40em;
        left: 50%;
        transform: translateX(-65%);
        font-size: 1.25em;
        color: var(--mod-blue);
    }}
    .swara-mod-dotted.mod-h-dotted {{
        position: absolute;
        top: -0.35em;
        left: 50%;
        transform: translateX(-50%);
        font-size: 1.15em;
        color: var(--mod-blue);
    }}

    /* MANTRAS STACKING PREVIEW CELL */
    .preview-cell {{
        width: 220px;
    }}
    .mantra-preview-flex {{
        display: inline-flex;
        align-items: flex-end;
        background: #ffffff;
        border: 1px solid var(--border-color);
        padding: 8px 16px;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }}
    .mantra-preview-flex .mantra-word {{
        display: inline-flex;
        flex-direction: column;
        align-items: center;
        justify-content: flex-end;
        vertical-align: bottom;
        position: relative;
        font-size: 1.35rem;
    }}
    .mantra-preview-flex .swara-text {{
        font-family: 'JaimineeyaSwara', serif;
        font-size: 0.90rem;
        color: var(--swara-red);
        line-height: 1;
        margin-bottom: 4px;
        padding-bottom: 2px;
        min-height: 1.1em;
        user-select: none;
        display: block;
        text-align: center;
    }}
    .mantra-preview-flex .mantra-text {{
        font-family: 'Noto Serif Malayalam', serif;
        font-size: 1.35rem;
        font-weight: 500;
        line-height: 1.1;
        color: var(--text-main);
        position: relative;
        display: inline-block;
    }}
    .mantra-preview-flex .word-space {{
        width: 0.40em;
        display: inline-block;
    }}
    .mantra-preview-flex .swara-mod {{
        color: var(--mod-blue);
        font-family: 'JaimineeyaSwara', serif;
        font-weight: bold;
        line-height: 1;
    }}
    .mantra-preview-flex .swara-mod.mod-a {{
        position: absolute;
        top: -0.28em;
        left: 100%;
        transform: translateX(-40%);
        font-size: 0.95rem;
        pointer-events: none;
    }}
    .mantra-preview-flex .swara-mod.mod-a1 {{
        position: absolute;
        top: -0.28em;
        left: 100%;
        transform: translateX(-40%);
        font-size: 1.15rem;
        pointer-events: none;
    }}
    .mantra-preview-flex .swara-mod.mod-b {{
        position: absolute;
        top: -0.22em;
        left: 100%;
        transform: translateX(-50%);
        pointer-events: none;
        display: inline-flex;
        flex-direction: column;
        align-items: center;
    }}
    .mantra-preview-flex .swara-mod.mod-b .caret-glyph {{
        display: block;
        color: var(--mod-blue);
        font-size: 0.95rem;
        line-height: 1;
    }}
    .mantra-preview-flex .swara-mod.mod-b .swara-on-caret {{
        position: absolute;
        top: -1.70em;
        left: 50%;
        transform: translateX(-50%);
        color: var(--swara-red);
        font-size: 0.90rem;
        font-weight: bold;
        font-family: 'JaimineeyaSwara', serif;
        line-height: 1;
        white-space: nowrap;
    }}
    .mantra-preview-flex .swara-mod.mod-b1 {{
        position: absolute;
        top: -0.22em;
        left: 100%;
        transform: translateX(-40%);
        font-size: 0.95rem;
        pointer-events: none;
    }}
    .mantra-preview-flex .swara-mod.mod-c {{
        position: absolute;
        top: -0.15em;
        right: -0.35em;
        font-size: 0.85rem;
    }}
    .mantra-preview-flex .swara-mod.mod-d {{
        position: absolute;
        top: -0.30em;
        left: 100%;
        transform: translateX(-40%);
        font-size: 0.95rem;
        pointer-events: none;
    }}
    .mantra-preview-flex .swara-mod.mod-d1 {{
        position: absolute;
        top: -0.28em;
        left: 100%;
        transform: translateX(-40%);
        font-size: 1.25rem;
        pointer-events: none;
    }}
    .mantra-preview-flex .swara-mod.mod-d2 {{
        position: absolute;
        top: -0.22em;
        right: -0.35em;
        font-size: 1.25rem;
    }}
    .mantra-preview-flex .swara-mod.mod-e {{
        position: relative;
        margin-left: 0.15em;
        font-size: 1.15rem;
        vertical-align: -0.05em;
    }}
    .mantra-preview-flex .swara-mod.mod-f {{
        position: relative;
        margin-left: 0.15em;
        font-size: 1.15rem;
        vertical-align: -0.05em;
    }}
    .mantra-preview-flex .swara-mod.mod-g {{
        position: absolute;
        bottom: -0.38em;
        left: 28%;
        transform: translateX(-50%);
        font-size: 1.05rem;
    }}
    .mantra-preview-flex .swara-mod.mod-h {{
        position: absolute;
        top: -0.35em;
        left: 50%;
        transform: translateX(-50%);
        font-size: 0.95rem;
    }}
    .mantra-preview-flex .swara-mod.mod-i {{
        position: absolute;
        top: -0.22em;
        right: -0.35em;
        font-size: 1.25rem;
    }}
    .mantra-preview-flex .swara-mod.mod-j {{
        position: absolute;
        top: -0.22em;
        right: -0.35em;
        font-size: 1.25rem;
    }}
    .mantra-preview-flex .swara-mod.mod-k {{
        position: absolute;
        top: -0.22em;
        right: -0.35em;
        font-size: 1.25rem;
    }}mod.mod-d2 {{
        position: absolute;
        top: -0.24em;
        left: 100%;
        transform: translateX(-40%);
        font-size: 0.95rem;
        pointer-events: none;
    }}
    .mantra-preview-flex .swara-mod.mod-e {{
        position: relative;
        margin-left: 0.15em;
        font-size: 1.15rem;
        vertical-align: -0.05em;
    }}
    .mantra-preview-flex .swara-mod.mod-f {{
        position: relative;
        margin-left: 0.15em;
        font-size: 1.15rem;
        vertical-align: -0.05em;
    }}
    .mantra-preview-flex .swara-mod.mod-g {{
        position: absolute;
        bottom: -0.38em;
        left: 28%;
        transform: translateX(-50%);
        font-size: 1.05rem;
    }}
    .mantra-preview-flex .swara-mod.mod-h {{
        position: absolute;
        top: -0.35em;
        left: 50%;
        transform: translateX(-50%);
        font-size: 0.95rem;
    }}
    .mantra-preview-flex .swara-mod.mod-i {{
        position: absolute;
        top: -0.15em;
        right: -0.35em;
        font-size: 0.85rem;
    }}
    .mantra-preview-flex .swara-mod.mod-j {{
        position: absolute;
        top: -0.15em;
        right: -0.25em;
        font-size: 0.85rem;
    }}
    .mantra-preview-flex .swara-mod.mod-k {{
        position: absolute;
        top: -0.15em;
        right: -0.25em;
        font-size: 0.85rem;
    }}
    .mantra-preview-flex .mantra-punct {{
        font-family: 'Noto Serif Malayalam', serif;
        font-size: 1.35rem;
        font-weight: 500;
        line-height: 1.1;
        color: var(--mod-blue);
        display: inline-block;
        margin-left: 0.05em;
    }}

    table {{
        width: 100%;
        border-collapse: collapse;
        text-align: left;
    }}
    th {{
        background: #f1f5f9;
        color: #475569;
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        padding: 14px 18px;
        border-bottom: 1px solid var(--border-color);
    }}
    td {{
        padding: 14px 18px;
        border-bottom: 1px solid #f1f5f9;
        font-size: 14px;
        vertical-align: middle;
    }}
    tr:hover {{
        background: #f8fafc;
    }}
    .idx-col {{
        color: #94a3b8;
        font-size: 13px;
        font-weight: 600;
        width: 75px;
    }}
    .glyph-cell {{
        font-size: 34px;
        line-height: 1;
        width: 100px;
        text-align: center;
    }}
    .swara-glyph {{
        font-family: 'JaimineeyaSwara', serif;
    }}
    .swara-red {{
        color: var(--swara-red);
        font-weight: bold;
    }}
    .mod-glyph {{
        color: var(--primary-blue);
    }}

    .shortcut-tag {{
        font-family: ui-monospace, monospace;
        font-size: 15px;
        color: #3730a3;
        background: #e0e7ff;
        padding: 4px 10px;
        border-radius: 6px;
        border: 1px solid #c7d2fe;
    }}
    .mod-desc {{
        font-size: 12px;
        color: var(--text-muted);
        font-weight: normal;
        margin-top: 4px;
        line-height: 1.4;
    }}
    code {{
        font-family: ui-monospace, monospace;
        background: #f1f5f9;
        color: #0f172a;
        padding: 3px 6px;
        border-radius: 4px;
        font-size: 12px;
    }}
    .badge {{
        display: inline-block;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    .badge-above {{ background: #e0e7ff; color: #3730a3; }}
    .badge-below {{ background: #fef3c7; color: #92400e; }}
    .badge-shoulder {{ background: #f3e8ff; color: #6b21a8; }}
    .badge-inline {{ background: #f1f5f9; color: #334155; }}
    .badge-base {{ background: #fee2e2; color: #991b1b; }}
    .badge-sha {{ background: #ecfdf5; color: #065f46; }}
    .badge-pla {{ background: #fff7ed; color: #9a3412; }}
    .badge-liga {{ background: #eff6ff; color: #1e40af; }}

    .count-cell {{
        font-weight: 700;
        color: var(--text-muted);
        text-align: right;
        width: 80px;
    }}

    footer {{
        text-align: center;
        padding: 24px;
        color: var(--text-muted);
        font-size: 13px;
        border-top: 1px solid var(--border-color);
        margin-top: 40px;
    }}
</style>
</head>
<body>
<div class="container">

    <header>
        <h1>Jaimineeya Swara Font — Complete Glyph Inventory & Modifiers</h1>
        <div class="subtitle">
            Authoritative typographic catalog of <strong>JaimineeyaSwara.ttf</strong> showing all Canonical Vedic Swara Modifiers (A..H) and inline marks (. _ ,) with dotted-circle positions and live Mantrakshara stacking previews, 19 Ayugma Grantha bases, custom manuscript ligatures (Pla/Sha), and the full Samhita marker inventory.
        </div>
        <div class="color-legend">
            <div class="legend-item">
                <span class="legend-dot dot-red"></span>
                <span>Swara Marker = Red (<code>#c62828</code>)</span>
            </div>
            <div class="legend-item">
                <span class="legend-dot dot-blue"></span>
                <span>Swara Modifier = DarkBlue (<code>#002171</code>)</span>
            </div>
        </div>
    </header>

    <div class="nav-tabs">
        <button class="tab-btn active" onclick="filterTab('all')">All Tables</button>
        <button class="tab-btn" onclick="filterTab('modifiers')">Vedic Modifiers & Marks</button>
        <button class="tab-btn" onclick="filterTab('ayugma')">Ayugma Bases (A01..A19)</button>
        <button class="tab-btn" onclick="filterTab('ligatures')">Manuscript Ligatures (Pla/Sha)</button>
        <button class="tab-btn" onclick="filterTab('corpus')">Full Samhita Markers (229)</button>
    </div>

    <!-- Section 1: Modifiers (A..H + Inline Marks) -->
    <div class="section-card" id="sec-modifiers">
        <div class="section-header">
            <div class="section-title">
                <span>1. Canonical Vedic Swara Modifiers & Inline Marks</span>
            </div>
            <span class="section-tag tag-modifiers">{len(modifiers)} Modifiers & Marks</span>
        </div>
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Shortcut</th>
                    <th>Modifier Name & Function</th>
                    <th>Typing Shortcuts</th>
                    <th style="text-align:center;">Direct Glyph</th>
                    <th style="text-align:center;">Dotted Base</th>
                    <th>Mantrakshara Preview</th>
                    <th>Unicode / Hex</th>
                    <th>Position</th>
                </tr>
            </thead>
            <tbody>
                {"".join(modifier_rows_html)}
            </tbody>
        </table>
    </div>

    <!-- Section 2: Ayugma Bases (A01..A19) -->
    <div class="section-card" id="sec-ayugma">
        <div class="section-header">
            <div class="section-title">
                <span>2. Ayugma Pure Grantha Bases (A01..A19)</span>
            </div>
            <span class="section-tag tag-ayugma">19 Bases</span>
        </div>
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Swara Name</th>
                    <th>Malayalam Equiv</th>
                    <th style="text-align:center;">Grantha Glyph</th>
                    <th>Unicode Codepoint</th>
                    <th>Phonetic / Traditional Name</th>
                    <th>Classification</th>
                </tr>
            </thead>
            <tbody>
                {"".join(ayugma_rows_html)}
            </tbody>
        </table>
    </div>

    <!-- Section 3: Manuscript Ligatures (Pla/Sha) -->
    <div class="section-card" id="sec-ligatures">
        <div class="section-header">
            <div class="section-title">
                <span>3. Manuscript Overrides & Ligatures (Pla / Sha)</span>
            </div>
            <span class="section-tag tag-liga">10 Ligatures</span>
        </div>
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Ligature Name</th>
                    <th style="text-align:center;">Glyph</th>
                    <th>PUA / Mapping</th>
                    <th>Description & Shaping Rules</th>
                    <th>Stacking</th>
                </tr>
            </thead>
            <tbody>
                {"".join(liga_rows_html)}
            </tbody>
        </table>
    </div>

    <!-- Section 4: Full Corpus Markers -->
    <div class="section-card" id="sec-corpus">
        <div class="section-header">
            <div class="section-title">
                <span>4. Full Samhita Swara Marker Inventory</span>
            </div>
            <span class="section-tag tag-all">{len(rows)} Markers in Corpus</span>
        </div>
        <table>
            <thead>
                <tr>
                    <th>#</th>
                    <th>Devanagari Marker</th>
                    <th style="text-align:center;">Grantha Glyph</th>
                    <th>Grantha Hex Codepoints</th>
                    <th>Classification</th>
                    <th style="text-align:right;">Corpus Frequency</th>
                </tr>
            </thead>
            <tbody>
                {"".join(swara_rows_html)}
            </tbody>
        </table>
    </div>

    <footer>
        Jaimineeya Samaveda Digitization Project &bull; Generated from authoritative Grantha & Manuscript Review Tables &bull; Font: JaimineeyaSwara.ttf
    </footer>

</div>

<script>
function filterTab(tabName) {{
    var secs = document.querySelectorAll('.section-card');
    var btns = document.querySelectorAll('.tab-btn');
    for (var j = 0; j < btns.length; j++) {{
        btns[j].classList.remove('active');
    }}
    if (event && event.currentTarget) {{
        event.currentTarget.classList.add('active');
    }}
    if (tabName === 'all') {{
        for (var i = 0; i < secs.length; i++) {{
            secs[i].style.display = 'block';
        }}
    }} else {{
        for (var i = 0; i < secs.length; i++) {{
            secs[i].style.display = 'none';
        }}
        var target = document.getElementById('sec-' + tabName);
        if (target) {{
            target.style.display = 'block';
        }}
    }}
}}
</script>
</body>
</html>
"""

    OUT_HTML.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_HTML, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Saved HTML Glyph Table: {OUT_HTML}")

    # Copy to Malayalam_JSV root and data/output/malayalam
    for dst in [
        ROOT / "Malayalam_JSV" / "glyph_table.html",
        ROOT / "data" / "output" / "malayalam" / "glyph_table.html",
        ARTIFACT_DIR / "glyph_table.html"
    ]:
        try:
            dst.parent.mkdir(parents=True, exist_ok=True)
            with open(dst, "w", encoding="utf-8") as f:
                f.write(html_content)
            print(f"Copied to: {dst}")
        except Exception as e:
            print(f"Warning: could not copy to {dst}: {e}")


if __name__ == "__main__":
    render_image_grid()
    render_html_table()
