"""Build JaimineeyaSwara.ttf using fontTools.

This script creates the dedicated OpenType font for Jaimineeya Samaveda
superscript swara notations and swara modifiers:
1. Imports all 19 Ayugma swara bases:
   - Grantha bases from NotoSerifGrantha-Regular.ttf
   - Malayalam Sha (U+0D36) from NotoSerifMalayalam-Regular.ttf
   - Authentic Vedic manuscript Pla (custom vector glyph)
   - Grantha Tra and Kra conjuncts
2. Builds Grantha matra combinations for all bases (eliminating dotted circles):
   - Sha + Grantha matras (ശா, ശി, ശീ, ശു, ശൂ, ശെ, ശൈ, ശൊ, ശൌ, ശ്, etc.)
   - Pla + Grantha matras (പ്ലാ, പ്ലി, പ്ലീ, etc.)
   - All standard Grantha bases + matras
3. Adds full Vedic Swara Modifier set:
   - High / Mid-Dot (Mod 10 / H)
   - Phrasing Danda (Mod 6 / L: starts near bottom and extends downward below baseline)
   - Descending Tone Slash (Mod 21/22/23: falling slash below baseline)
   - Syllable Spanning Arc / Tie (Mod 2/3: smooth bridge)
   - Caret / Peak Arrowhead (Mod 13/15: ^)
   - Roof / Inverted Angle (Mod 14: /\\)
   - Low Underbar (Mod 4: _)
   - Full Danda (virama / text danda)
4. Configures cmap, GSUB ligatures, and font metadata.
"""

from pathlib import Path
import copy
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._g_l_y_f import Glyph, GlyphCoordinates, ttProgram
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString

ROOT = Path(__file__).resolve().parents[1]
GRANTHA_FONT_PATH = ROOT / "fonts" / "NotoSerifGrantha-Regular.ttf"
MALAYALAM_FONT_PATH = ROOT / "fonts" / "NotoSerifMalayalam-Regular.ttf"
OUT_FONT_PATH = ROOT / "fonts" / "JaimineeyaVedicSwara.ttf"


def init_glyph() -> Glyph:
    glyph = Glyph()
    glyph.program = ttProgram.Program()
    return glyph


def draw_pla_glyph() -> Glyph:
    """Construct the authentic Vedic manuscript Pla glyph with bezier curves."""
    glyph = init_glyph()
    glyph.numberOfContours = 2

    # Outer outline of Pla
    coords_outer = [
        # Left eyelet loop (top-left)
        (120, 480, 1),
        (160, 520, 0),
        (210, 520, 0),
        (250, 470, 1),
        (250, 410, 0),
        (200, 360, 0),
        (150, 360, 1),
        # Crossbar connecting to subjoined loop
        (270, 360, 1),
        # Subjoined loop going down
        (270, 240, 1),
        (220, 190, 0),
        (170, 140, 0),
        (170, 80, 1),
        (170, 20, 0),
        (220, -20, 0),
        (270, -20, 1),
        (330, -20, 0),
        (380, 30, 0),
        (400, 90, 1),
        # Diagonal return rising to right vertex
        (560, 280, 1),
        # Right stem & upward arc
        (600, 340, 0),
        (650, 450, 0),
        (670, 580, 1),
        (630, 590, 1),
        (610, 480, 0),
        (560, 370, 0),
        (520, 310, 1),
        # Return along crossbar to inner eyelet
        (290, 310, 1),
        (270, 330, 0),
        (220, 390, 0),
        (160, 390, 1),
        (130, 420, 0),
        (120, 450, 1),
    ]

    # Inner counter of subjoined loop
    coords_inner = [
        (220, 80, 1),
        (220, 120, 0),
        (250, 140, 0),
        (280, 120, 1),
        (310, 80, 0),
        (310, 30, 0),
        (270, 20, 1),
        (230, 20, 0),
        (220, 50, 1),
    ]

    all_coords = [(x, y) for x, y, _ in coords_outer] + [(x, y) for x, y, _ in coords_inner]
    all_flags = [f for _, _, f in coords_outer] + [f for _, _, f in coords_inner]

    glyph.coordinates = GlyphCoordinates(all_coords)
    glyph.flags = bytearray(all_flags)
    glyph.endPtsOfContours = [len(coords_outer) - 1, len(all_coords) - 1]
    glyph.recalcBounds({})
    return glyph


def draw_circle_glyph(cx: int, cy: int, r: int) -> Glyph:
    """Draw a circular dot glyph (e.g. for High/Mid-Dot)."""
    glyph = init_glyph()
    glyph.numberOfContours = 1
    coords = [
        (cx - r, cy, 1),
        (cx - r, cy + int(r * 0.55), 0),
        (cx - int(r * 0.55), cy + r, 0),
        (cx, cy + r, 1),
        (cx + int(r * 0.55), cy + r, 0),
        (cx + r, cy + int(r * 0.55), 0),
        (cx + r, cy, 1),
        (cx + r, cy - int(r * 0.55), 0),
        (cx + int(r * 0.55), cy - r, 0),
        (cx, cy - r, 1),
        (cx - int(r * 0.55), cy - r, 0),
        (cx - r, cy - int(r * 0.55), 0),
    ]
    glyph.coordinates = GlyphCoordinates([(x, y) for x, y, _ in coords])
    glyph.flags = bytearray([f for _, _, f in coords])
    glyph.endPtsOfContours = [len(coords) - 1]
    glyph.recalcBounds({})
    return glyph


def draw_phrasing_danda() -> Glyph:
    """Swara Modifier F: Phrasing Danda with distinct overhead circular dot (╷)."""
    glyph = init_glyph()
    
    # Contour 1: Vertical bar extending longer downwards (x=85..165, y=-200..480)
    coords_bar = [
        (85, 480, 1),
        (165, 480, 1),
        (165, -200, 1),
        (85, -200, 1),
    ]
    
    # Contour 2: Distinct overhead circular dot (r=60, cy=630, cx=125)
    cx, cy, r = 125, 630, 60
    coords_dot = [
        (cx - r, cy, 1),
        (cx - r, cy + int(r * 0.55), 0),
        (cx - int(r * 0.55), cy + r, 0),
        (cx, cy + r, 1),
        (cx + int(r * 0.55), cy + r, 0),
        (cx + r, cy + int(r * 0.55), 0),
        (cx + r, cy, 1),
        (cx + r, cy - int(r * 0.55), 0),
        (cx + int(r * 0.55), cy - r, 0),
        (cx, cy - r, 1),
        (cx - int(r * 0.55), cy - r, 0),
        (cx - r, cy - int(r * 0.55), 0),
    ]
    
    all_coords = [(x, y) for x, y, _ in coords_bar] + [(x, y) for x, y, _ in coords_dot]
    all_flags = [f for _, _, f in coords_bar] + [f for _, _, f in coords_dot]
    
    glyph.coordinates = GlyphCoordinates(all_coords)
    glyph.flags = bytearray(all_flags)
    glyph.endPtsOfContours = [len(coords_bar) - 1, len(all_coords) - 1]
    glyph.numberOfContours = 2
    glyph.recalcBounds({})
    return glyph


def draw_bold_tone_column() -> Glyph:
    """Swara Modifier E: Bold solid vertical tone column extending downwards (┃)."""
    glyph = init_glyph()
    glyph.numberOfContours = 1
    coords = [
        (85, 580, 1),
        (175, 580, 1),
        (175, -200, 1),
        (85, -200, 1),
    ]
    glyph.coordinates = GlyphCoordinates([(x, y) for x, y, _ in coords])
    glyph.flags = bytearray([f for _, _, f in coords])
    glyph.endPtsOfContours = [len(coords) - 1]
    glyph.recalcBounds({})
    return glyph


def draw_descending_tone_slash() -> Glyph:
    """Swara Modifier G: Bold, highly visible downward diagonal stroke starting from middle bottom of preceding syllable."""
    glyph = init_glyph()
    glyph.numberOfContours = 1
    # Bold diagonal falling stroke starting from middle bottom (x=0, y=-10) to (380, -480)
    w = 130
    coords = [
        (0, -10, 1),
        (0 + w, -10, 1),
        (380 + w, -480, 1),
        (380, -480, 1),
    ]
    glyph.coordinates = GlyphCoordinates([(x, y) for x, y, _ in coords])
    glyph.flags = bytearray([f for _, _, f in coords])
    glyph.endPtsOfContours = [len(coords) - 1]
    glyph.recalcBounds({})
    return glyph


def get_bezier_arc_coords(width: int, y_base: int = 480, thickness: int = 125, height_factor: float = 0.88) -> list:
    import numpy as np
    mid_x = width / 2.0
    r_out_x = (width - 320) / 2.0
    r_out_y = r_out_x * height_factor
    r_in_x = r_out_x - thickness
    r_in_y = r_out_y - thickness
    
    angles = np.radians([180, 150, 120, 90, 60, 30, 0])
    ctrl_angles = np.radians([165, 135, 105, 75, 45, 15])
    r_scale = 1.035
    
    outer_coords = []
    outer_coords.append((int(mid_x + r_out_x * np.cos(angles[0])), int(y_base + r_out_y * np.sin(angles[0])), 1))
    for i in range(len(ctrl_angles)):
        cx = int(mid_x + r_out_x * r_scale * np.cos(ctrl_angles[i]))
        cy = int(y_base + r_out_y * r_scale * np.sin(ctrl_angles[i]))
        outer_coords.append((cx, cy, 0))
        ex = int(mid_x + r_out_x * np.cos(angles[i+1]))
        ey = int(y_base + r_out_y * np.sin(angles[i+1]))
        outer_coords.append((ex, ey, 1))
        
    inner_angles = np.radians([0, 30, 60, 90, 120, 150, 180])
    inner_ctrl_angles = np.radians([15, 45, 75, 105, 135, 165])
    
    inner_coords = []
    inner_coords.append((int(mid_x + r_in_x * np.cos(inner_angles[0])), int(y_base + r_in_y * np.sin(inner_angles[0])), 1))
    for i in range(len(inner_ctrl_angles)):
        cx = int(mid_x + r_in_x * r_scale * np.cos(inner_ctrl_angles[i]))
        cy = int(y_base + r_in_y * r_scale * np.sin(inner_ctrl_angles[i]))
        inner_coords.append((cx, cy, 0))
        ex = int(mid_x + r_in_x * np.cos(inner_angles[i+1]))
        ey = int(y_base + r_in_y * np.sin(inner_angles[i+1]))
        inner_coords.append((ex, ey, 1))
        
    return outer_coords + inner_coords


def draw_syllable_arc(width: int = 1600) -> Glyph:
    """Swara Modifier A: Overhead smooth semi-circular curved bridge spanning across 2 syllables (spec_image1..5)."""
    glyph = init_glyph()
    glyph.numberOfContours = 1
    coords = get_bezier_arc_coords(width, y_base=480, thickness=125, height_factor=0.88)
    glyph.coordinates = GlyphCoordinates([(x, y) for x, y, _ in coords])
    glyph.flags = bytearray([f for _, _, f in coords])
    glyph.endPtsOfContours = [len(coords) - 1]
    glyph.recalcBounds({})
    return glyph


def draw_syllable_arc_danda(width: int = 2250) -> Glyph:
    """Swara Modifier A1 (MOD-A_1): Overhead smooth semi-circular curved arch spanning across 2 syllables with a danda separator (spec_image6..8)."""
    glyph = init_glyph()
    glyph.numberOfContours = 1
    coords = get_bezier_arc_coords(width, y_base=480, thickness=95, height_factor=0.78)
    glyph.coordinates = GlyphCoordinates([(x, y) for x, y, _ in coords])
    glyph.flags = bytearray([f for _, _, f in coords])
    glyph.endPtsOfContours = [len(coords) - 1]
    glyph.recalcBounds({})
    return glyph


def draw_caret(width: int = 1500) -> Glyph:
    """Swara Modifier B: Crisp, bold peak elevation caret (/ \\) spanning across 2 syllables."""
    glyph = init_glyph()
    glyph.numberOfContours = 2
    # Left arm: clean perpendicular rectangular stroke rising to apex
    # Centerline from (220, 450) to (710, 940), thickness 130
    coords_left = [
        (174, 496, 1),
        (664, 986, 1),
        (756, 894, 1),
        (266, 404, 1),
    ]
    # Right arm: clean perpendicular rectangular stroke descending from apex
    # Centerline from (790, 940) to (1280, 450), thickness 130
    coords_right = [
        (836, 986, 1),
        (1326, 496, 1),
        (1234, 404, 1),
        (744, 894, 1),
    ]
    all_coords = coords_left + coords_right
    glyph.coordinates = GlyphCoordinates([(x, y) for x, y, _ in all_coords])
    glyph.flags = bytearray([f for _, _, f in all_coords])
    glyph.endPtsOfContours = [len(coords_left) - 1, len(all_coords) - 1]
    glyph.recalcBounds({})
    return glyph


def draw_roof(width: int = 1500) -> Glyph:
    """Swara Modifier D: Stylized Caret with steep left leg + apex turn, break gap, and detached right leg."""
    glyph = init_glyph()
    glyph.numberOfContours = 2
    # Unbroken left part + sharp apex + downward turn
    coords_left = [
        (240, 480, 1),
        (750, 1200, 1),
        (900, 960, 1),
        (815, 910, 1),
        (725, 1060, 1),
        (325, 480, 1),
    ]
    # Lower right detached stroke
    coords_right = [
        (970, 840, 1),
        (1200, 480, 1),
        (1115, 480, 1),
        (885, 790, 1),
    ]
    all_coords = coords_left + coords_right
    glyph.coordinates = GlyphCoordinates([(x, y) for x, y, _ in all_coords])
    glyph.flags = bytearray([f for _, _, f in all_coords])
    glyph.endPtsOfContours = [len(coords_left) - 1, len(all_coords) - 1]
    glyph.recalcBounds({})
    return glyph


def draw_swarita() -> Glyph:
    """Swara Modifier H: Centered vertical stroke (|) on top of mantrakshara."""
    glyph = init_glyph()
    glyph.numberOfContours = 1
    # Vertical bar from y=540 to y=880 centered at x=0, stroke width 70
    w2 = 35
    coords = [
        (-w2, 880, 1),
        (w2, 880, 1),
        (w2, 540, 1),
        (-w2, 540, 1),
    ]
    glyph.coordinates = GlyphCoordinates([(x, y) for x, y, _ in coords])
    glyph.flags = bytearray([f for _, _, f in coords])
    glyph.endPtsOfContours = [len(coords) - 1]
    glyph.recalcBounds({})
    return glyph


def draw_underbar(width: int = 500) -> Glyph:
    """Horizontal low line under baseline."""
    glyph = init_glyph()
    glyph.numberOfContours = 1
    coords = [
        (30, -120, 1),
        (width - 30, -120, 1),
        (width - 30, -165, 1),
        (30, -165, 1),
    ]
    glyph.coordinates = GlyphCoordinates([(x, y) for x, y, _ in coords])
    glyph.flags = bytearray([f for _, _, f in coords])
    glyph.endPtsOfContours = [len(coords) - 1]
    glyph.recalcBounds({})
    return glyph


def draw_ascending_tone_slash() -> Glyph:
    """Upward diagonal stroke (rising slash /) situated below baseline."""
    glyph = init_glyph()
    glyph.numberOfContours = 1
    # Diagonal rising stroke below baseline from (80, -330) to (280, -30)
    w = 50
    coords = [
        (80, -330, 1),
        (80 + w, -330, 1),
        (280 + w, -30, 1),
        (280, -30, 1),
    ]
    glyph.coordinates = GlyphCoordinates([(x, y) for x, y, _ in coords])
    glyph.flags = bytearray([f for _, _, f in coords])
    glyph.endPtsOfContours = [len(coords) - 1]
    glyph.recalcBounds({})
    return glyph


def draw_ring_above() -> Glyph:
    """Overhead small ring/circle (ͦ / ˚) above akshara."""
    glyph = init_glyph()
    glyph.numberOfContours = 2
    # Outer circle (cx=250, cy=740, r=70)
    cx, cy, r_out, r_in = 250, 740, 70, 35
    coords_outer = [
        (cx - r_out, cy, 1),
        (cx - r_out, cy + int(r_out * 0.55), 0),
        (cx - int(r_out * 0.55), cy + r_out, 0),
        (cx, cy + r_out, 1),
        (cx + int(r_out * 0.55), cy + r_out, 0),
        (cx + r_out, cy + int(r_out * 0.55), 0),
        (cx + r_out, cy, 1),
        (cx + r_out, cy - int(r_out * 0.55), 0),
        (cx + int(r_out * 0.55), cy - r_out, 0),
        (cx, cy - r_out, 1),
        (cx - int(r_out * 0.55), cy - r_out, 0),
        (cx - r_out, cy - int(r_out * 0.55), 0),
    ]
    coords_inner = [
        (cx - r_in, cy, 1),
        (cx - r_in, cy - int(r_in * 0.55), 0),
        (cx - int(r_in * 0.55), cy - r_in, 0),
        (cx, cy - r_in, 1),
        (cx + int(r_in * 0.55), cy - r_in, 0),
        (cx + r_in, cy - int(r_in * 0.55), 0),
        (cx + r_in, cy, 1),
        (cx + r_in, cy + int(r_in * 0.55), 0),
        (cx + int(r_in * 0.55), cy + r_in, 0),
        (cx, cy + r_in, 1),
        (cx - int(r_in * 0.55), cy + r_in, 0),
        (cx - r_in, cy + int(r_in * 0.55), 0),
    ]
    all_coords = [(x, y) for x, y, _ in coords_outer] + [(x, y) for x, y, _ in coords_inner]
    all_flags = [f for _, _, f in coords_outer] + [f for _, _, f in coords_inner]
    glyph.coordinates = GlyphCoordinates(all_coords)
    glyph.flags = bytearray(all_flags)
    glyph.endPtsOfContours = [len(coords_outer) - 1, len(all_coords) - 1]
    glyph.recalcBounds({})
    return glyph


def draw_low_comma() -> Glyph:
    """Low comma / pause hook (,) below baseline."""
    glyph = init_glyph()
    glyph.numberOfContours = 1
    # Comma below baseline from y=-40 to y=-240
    coords = [
        (120, -40, 1),
        (180, -40, 1),
        (180, -100, 1),
        (140, -220, 1),
        (110, -210, 1),
        (135, -120, 1),
        (120, -120, 1),
    ]
    glyph.coordinates = GlyphCoordinates([(x, y) for x, y, _ in coords])
    glyph.flags = bytearray([f for _, _, f in coords])
    glyph.endPtsOfContours = [len(coords) - 1]
    glyph.recalcBounds({})
    return glyph


def draw_double_danda() -> Glyph:
    """Double phrasing danda (||)."""
    glyph = init_glyph()
    glyph.numberOfContours = 2
    # Two vertical bars
    c1 = [(80, 550, 1), (135, 550, 1), (135, -250, 1), (80, -250, 1)]
    c2 = [(220, 550, 1), (275, 550, 1), (275, -250, 1), (220, -250, 1)]
    coords = c1 + c2
    glyph.coordinates = GlyphCoordinates([(x, y) for x, y, _ in coords])
    glyph.flags = bytearray([f for _, _, f in coords])
    glyph.endPtsOfContours = [len(c1) - 1, len(coords) - 1]
    glyph.recalcBounds({})
    return glyph


def draw_rising_stroke_d1() -> Glyph:
    """Swara Modifier D1 (MOD-D1): Asymmetrical inverted-V / rising diagonal with downward right hook (Larger/Bolder)."""
    glyph = init_glyph()
    glyph.numberOfContours = 1
    # Long rising left leg from syllable boundary to apex, then short downward right slope
    coords = [
        (80, 480, 1),
        (360, 1140, 1),
        (540, 840, 1),
        (480, 780, 1),
        (350, 1000, 1),
        (140, 430, 1),
    ]
    glyph.coordinates = GlyphCoordinates([(x, y) for x, y, _ in coords])
    glyph.flags = bytearray([f for _, _, f in coords])
    glyph.endPtsOfContours = [len(coords) - 1]
    glyph.recalcBounds({})
    return glyph


def draw_check_tick_d2() -> Glyph:
    """Swara Modifier D2 (MOD-D2): Bold check-mark tick stroke (✓) on upper-right shoulder."""
    glyph = init_glyph()
    glyph.numberOfContours = 1
    coords = [
        (80, 680, 1),
        (140, 710, 1),
        (220, 540, 1),
        (440, 1020, 1),
        (375, 1050, 1),
        (180, 460, 1),
    ]
    glyph.coordinates = GlyphCoordinates([(x, y) for x, y, _ in coords])
    glyph.flags = bytearray([f for _, _, f in coords])
    glyph.endPtsOfContours = [len(coords) - 1]
    glyph.recalcBounds({})
    return glyph


def draw_double_shoulder_dash_i() -> Glyph:
    """Swara Modifier I (MOD-I): Two stacked parallel gently-rising dashes on upper right shoulder (Larger/Bolder)."""
    glyph = init_glyph()
    glyph.numberOfContours = 2
    # Upper parallel dash (wider and thicker)
    coords1 = [
        (100, 720, 1),
        (370, 800, 1),
        (355, 880, 1),
        (85, 800, 1),
    ]
    # Lower parallel dash
    coords2 = [
        (100, 530, 1),
        (370, 610, 1),
        (355, 690, 1),
        (85, 610, 1),
    ]
    all_coords = coords1 + coords2
    glyph.coordinates = GlyphCoordinates([(x, y) for x, y, _ in all_coords])
    glyph.flags = bytearray([f for _, _, f in all_coords])
    glyph.endPtsOfContours = [len(coords1) - 1, len(all_coords) - 1]
    glyph.recalcBounds({})
    return glyph


def draw_overhead_bar_j(width: int = 340) -> Glyph:
    """Swara Modifier J (MOD-J): Horizontal shoulder bar (—) on upper-right shoulder (Elevated)."""
    glyph = init_glyph()
    glyph.numberOfContours = 1
    # Elevated horizontal shoulder bar from y=800 to y=880, width=340
    coords = [
        (100, 880, 1),
        (100 + width, 880, 1),
        (100 + width, 800, 1),
        (100, 800, 1),
    ]
    glyph.coordinates = GlyphCoordinates([(x, y) for x, y, _ in coords])
    glyph.flags = bytearray([f for _, _, f in coords])
    glyph.endPtsOfContours = [len(coords) - 1]
    glyph.recalcBounds({})
    return glyph


def draw_bridging_slash_b1() -> Glyph:
    """Swara Modifier B1 (MOD-B1): Diagonal bridging stroke (/ / ↗) spanning between syllables."""
    glyph = init_glyph()
    glyph.numberOfContours = 1
    coords = [
        (120, 480, 1),
        (180, 460, 1),
        (440, 980, 1),
        (380, 1000, 1),
    ]
    glyph.coordinates = GlyphCoordinates([(x, y) for x, y, _ in coords])
    glyph.flags = bytearray([f for _, _, f in coords])
    glyph.endPtsOfContours = [len(coords) - 1]
    glyph.recalcBounds({})
    return glyph


def draw_shoulder_cross_k() -> Glyph:
    """Swara Modifier K (MOD-K): Bold cross / X mark on upper-right shoulder (Larger/Bolder)."""
    glyph = init_glyph()
    glyph.numberOfContours = 2
    # Slash / (wider span 80 to 360, thicker stroke)
    c1 = [
        (80, 560, 1),
        (130, 500, 1),
        (360, 720, 1),
        (310, 780, 1),
    ]
    # Backslash \
    c2 = [
        (80, 720, 1),
        (310, 500, 1),
        (360, 560, 1),
        (130, 780, 1),
    ]
    coords = c1 + c2
    glyph.coordinates = GlyphCoordinates([(x, y) for x, y, _ in coords])
    glyph.flags = bytearray([f for _, _, f in coords])
    glyph.endPtsOfContours = [len(c1) - 1, len(coords) - 1]
    glyph.recalcBounds({})
    return glyph


def compose_glyphs(base_glyph: Glyph, mark_glyph: Glyph, dx: int, dy: int) -> Glyph:
    """Create a composite glyph by combining base and mark glyph outlines."""
    new_glyph = init_glyph()
    base_contours = base_glyph.numberOfContours
    mark_contours = mark_glyph.numberOfContours
    if base_contours <= 0 or mark_contours <= 0:
        return copy.deepcopy(base_glyph)

    new_glyph.numberOfContours = base_contours + mark_contours
    base_coords = list(base_glyph.coordinates)
    mark_coords = [(x + dx, y + dy) for x, y in mark_glyph.coordinates]
    new_glyph.coordinates = GlyphCoordinates(base_coords + mark_coords)

    new_glyph.flags = bytearray(base_glyph.flags) + bytearray(mark_glyph.flags)

    base_endpoints = list(base_glyph.endPtsOfContours)
    mark_endpoints = [ep + len(base_coords) for ep in mark_glyph.endPtsOfContours]
    new_glyph.endPtsOfContours = base_endpoints + mark_endpoints
    new_glyph.recalcBounds({})
    return new_glyph


def draw_shi_hook_contour() -> tuple[list, list]:
    """Grantha I-hook canopy starting from inner junction/trough of Sha, overarching, and dropping on the right."""
    coords = [
        (490, 470, 1),
        (420, 680, 0),
        (380, 750, 1),
        (400, 810, 0),
        (520, 860, 1),
        (720, 860, 1),
        (820, 860, 0),
        (880, 760, 0),
        (920, 200, 1),
        (865, 200, 1),
        (835, 720, 0),
        (760, 805, 1),
        (520, 805, 1),
        (440, 770, 0),
        (460, 700, 0),
        (540, 480, 1),
    ]
    flags = [f for _, _, f in coords]
    xy = [(x, y) for x, y, _ in coords]
    return xy, flags


def draw_shii_loop_contours() -> tuple[list, list, list]:
    """Grantha II-loop loop rising from right lobe of Sha into a high upper-right eyelet."""
    outer = [
        (620, 520, 1),
        (560, 640, 0),
        (500, 720, 1),
        (540, 810, 0),
        (620, 860, 1),
        (780, 860, 0),
        (860, 840, 1),
        (860, 730, 1),
        (820, 730, 0),
        (680, 730, 1),
        (580, 660, 0),
        (670, 520, 1),
    ]
    inner = [
        (620, 780, 1),
        (680, 780, 0),
        (800, 780, 1),
        (800, 810, 1),
        (720, 810, 0),
        (620, 810, 1),
        (570, 810, 0),
        (570, 780, 1),
    ]
    all_xy = [(x, y) for x, y, _ in outer] + [(x, y) for x, y, _ in inner]
    all_flags = [f for _, _, f in outer] + [f for _, _, f in inner]
    endpts = [len(outer) - 1, len(all_xy) - 1]
    return all_xy, all_flags, endpts


def build_font() -> None:
    print(f"Loading Grantha base font: {GRANTHA_FONT_PATH}")
    gfont = TTFont(GRANTHA_FONT_PATH)
    print(f"Loading Malayalam base font: {MALAYALAM_FONT_PATH}")
    mfont = TTFont(MALAYALAM_FONT_PATH)

    glyf_table = gfont["glyf"]
    hmtx_table = gfont["hmtx"]
    cmap_table = gfont["cmap"]

    # 1. Fully extract Malayalam 'shamlym' (U+0D36) resolving all sub-components
    from fontTools.pens.ttGlyphPen import TTGlyphPen
    m_glyph_set = mfont.getGlyphSet()
    pen = TTGlyphPen(m_glyph_set)
    m_glyph_set["shamlym"].draw(pen)
    sha_glyph = pen.glyph()
    sha_glyph.recalcBounds({})
    sha_width, sha_lsb = mfont["hmtx"]["shamlym"]
    glyf_table["sha_mal"] = sha_glyph
    hmtx_table["sha_mal"] = (sha_width, sha_lsb)

    def scale_and_shift_glyph(glyph, scale, dx, dy):
        from fontTools.ttLib.tables._g_l_y_f import Glyph, GlyphCoordinates
        new_glyph = Glyph()
        new_glyph.numberOfContours = glyph.numberOfContours
        new_glyph.coordinates = GlyphCoordinates([(int(x * scale + dx), int(y * scale + dy)) for x, y in glyph.coordinates])
        new_glyph.flags = bytearray(glyph.flags)
        new_glyph.endPtsOfContours = list(glyph.endPtsOfContours)
        new_glyph.program = copy.deepcopy(glyph.program)
        new_glyph.recalcBounds({})
        return new_glyph

    # 2. Custom Vedic Pla: Grantha Pa (pa_gran) + Malayalam subjoined La (lasubscriptmlym)
    g_glyph_set = gfont.getGlyphSet()
    m_glyph_set = mfont.getGlyphSet()

    pen_pa = TTGlyphPen(g_glyph_set)
    g_glyph_set["pa_gran"].draw(pen_pa)
    pa_glyph = pen_pa.glyph()
    pa_glyph.recalcBounds({})
    pa_width, pa_lsb = gfont["hmtx"]["pa_gran"]

    pen_la = TTGlyphPen(m_glyph_set)
    m_glyph_set["lasubscriptmlym"].draw(pen_la)
    la_sub = pen_la.glyph()

    # Compose Pla: Grantha Pa with Malayalam subjoined La attached at bottom-right
    pla_glyph = compose_glyphs(pa_glyph, la_sub, 1380, 0)
    glyf_table["pla_jsv"] = pla_glyph
    hmtx_table["pla_jsv"] = (pa_width, pa_lsb)

    # Kra (A19): Grantha Ka + subjoined Ra (ra_vattu_gran)
    pen_ka = TTGlyphPen(g_glyph_set)
    g_glyph_set["ka_gran"].draw(pen_ka)
    ka_glyph = pen_ka.glyph()
    ka_width, ka_lsb = gfont["hmtx"]["ka_gran"]

    pen_ra = TTGlyphPen(g_glyph_set)
    g_glyph_set["ra_vattu_gran"].draw(pen_ra)
    ra_vattu = pen_ra.glyph()

    k_ra_glyph = compose_glyphs(ka_glyph, ra_vattu, 980, 0)
    glyf_table["k_ra_jsv"] = k_ra_glyph
    hmtx_table["k_ra_jsv"] = (ka_width + 100, ka_lsb)

    # Kra + Virama (A19 + virama): 𑌕𑍍𑌰𑍍
    pen_virama = TTGlyphPen(m_glyph_set)
    m_glyph_set["viramamlym"].draw(pen_virama)
    virama_mlym = pen_virama.glyph()
    virama_mlym_width, virama_mlym_lsb = mfont["hmtx"]["viramamlym"]

    # Replace Grantha virama combining marks with Malayalam virama (Chandrakala)
    glyf_table["virama_gran"] = virama_mlym
    glyf_table["virama_gran.alt"] = virama_mlym
    glyf_table["virama_gran.s1"] = virama_mlym
    hmtx_table["virama_gran"] = (virama_mlym_width, virama_mlym_lsb)
    hmtx_table["virama_gran.alt"] = (virama_mlym_width, virama_mlym_lsb)
    hmtx_table["virama_gran.s1"] = (virama_mlym_width, virama_mlym_lsb)

    # Recompose all existing Grantha virama ligatures with Malayalam virama
    for gname in list(glyf_table.keys()):
        if "virama" in gname and gname not in ("virama_gran", "virama_gran.alt", "virama_gran.s1", "rephviramamlym"):
            base_cand = gname.split("_virama")[0] + "_gran"
            if base_cand in gfont["glyf"]:
                pen_b = TTGlyphPen(g_glyph_set)
                g_glyph_set[base_cand].draw(pen_b)
                base_gl = pen_b.glyph()
                base_gl.recalcBounds({})
                comp = compose_glyphs(base_gl, virama_mlym, base_gl.xMax + 50, 0)
                glyf_table[gname] = comp
                b_w, b_lsb = gfont["hmtx"][base_cand]
                hmtx_table[gname] = (max(b_w, comp.xMax + 80), b_lsb)

    # Kra + Virama
    k_ra_virama_glyph = compose_glyphs(k_ra_glyph, virama_mlym, k_ra_glyph.xMax + 50, 0)
    glyf_table["k_ra_virama_jsv"] = k_ra_virama_glyph
    hmtx_table["k_ra_virama_jsv"] = (k_ra_glyph.xMax + 120, ka_lsb)

    # 3. Create Sha + Grantha matra composites
    def get_gran_glyph(name):
        pen = TTGlyphPen(g_glyph_set)
        g_glyph_set[name].draw(pen)
        gl = pen.glyph()
        gl.recalcBounds(gfont["glyf"])
        return gl

    def shift_glyph(glyph, dx, dy):
        from fontTools.ttLib.tables._g_l_y_f import Glyph, GlyphCoordinates
        new_glyph = Glyph()
        new_glyph.numberOfContours = glyph.numberOfContours
        new_glyph.coordinates = GlyphCoordinates([(x + dx, y + dy) for x, y in glyph.coordinates])
        new_glyph.flags = bytearray(glyph.flags)
        new_glyph.endPtsOfContours = list(glyph.endPtsOfContours)
        new_glyph.program = copy.deepcopy(glyph.program)
        new_glyph.recalcBounds({})
        return new_glyph

    aa_matra = get_gran_glyph("aaMatra_gran")
    aa_width, _ = gfont["hmtx"]["aaMatra_gran"]
    i_matra = get_gran_glyph("iMatra_gran")
    ii_matra = get_gran_glyph("iiMatra_gran")
    # Shift u and uu down by -380 to align to consonant baseline level
    u_matra = shift_glyph(get_gran_glyph("uMatra_gran"), 0, -380)
    uu_matra = shift_glyph(get_gran_glyph("uuMatra_gran"), 0, -380)
    glyf_table["uMatra_gran"] = u_matra
    glyf_table["uuMatra_gran"] = uu_matra
    r_matra = get_gran_glyph("rVocalicMatra_gran")
    rr_matra = get_gran_glyph("rrVocalicMatra_gran")
    ee_matra = get_gran_glyph("eeMatra_gran")
    ee_width, _ = gfont["hmtx"]["eeMatra_gran"]
    ai_matra = get_gran_glyph("aiMatra_gran")
    ai_width, _ = gfont["hmtx"]["aiMatra_gran"]
    au_matra = get_gran_glyph("auMatra_gran")
    au_len = get_gran_glyph("auLengthMark_gran")

    # Sha + AA (Grantha separate right arm)
    sha_aa = compose_glyphs(sha_glyph, aa_matra, sha_width + 40, 0)
    glyf_table["sha_aa_jsv"] = sha_aa
    hmtx_table["sha_aa_jsv"] = (sha_width + 780, sha_lsb)

    # Sha + I (Grantha authentic iMatra attached to right lobe)
    sha_i = compose_glyphs(sha_glyph, i_matra, 960, 0)
    glyf_table["sha_i_jsv"] = sha_i
    hmtx_table["sha_i_jsv"] = (sha_width + 150, sha_lsb)

    # Sha + II (Grantha authentic iiMatra attached to right lobe)
    sha_ii = compose_glyphs(sha_glyph, ii_matra, 1000, 0)
    glyf_table["sha_ii_jsv"] = sha_ii
    hmtx_table["sha_ii_jsv"] = (sha_width + 50, sha_lsb)

    # Sha + Virama (Malayalam virama)
    sha_virama = compose_glyphs(sha_glyph, virama_mlym, sha_glyph.xMax + 50, 0)
    glyf_table["sha_virama_jsv"] = sha_virama
    hmtx_table["sha_virama_jsv"] = (sha_glyph.xMax + 120, sha_lsb)

    # Sha + U / UU / R / RR / E / AI / O / AU
    glyf_table["sha_u_jsv"] = compose_glyphs(sha_glyph, u_matra, 980, 0)
    hmtx_table["sha_u_jsv"] = (1380, sha_lsb)
    glyf_table["sha_uu_jsv"] = compose_glyphs(sha_glyph, uu_matra, 980, 0)
    hmtx_table["sha_uu_jsv"] = (1380, sha_lsb)
    glyf_table["sha_r_jsv"] = compose_glyphs(sha_glyph, r_matra, 980, 0)
    hmtx_table["sha_r_jsv"] = (1380, sha_lsb)
    glyf_table["sha_rr_jsv"] = compose_glyphs(sha_glyph, rr_matra, 1150, 0)
    hmtx_table["sha_rr_jsv"] = (1550, sha_lsb)
    glyf_table["sha_e_jsv"] = compose_glyphs(ee_matra, sha_glyph, ee_width + 40, 0)
    hmtx_table["sha_e_jsv"] = (sha_width + ee_width + 60, sha_lsb)
    glyf_table["sha_ai_jsv"] = compose_glyphs(ai_matra, sha_glyph, ai_width + 40, 0)
    hmtx_table["sha_ai_jsv"] = (sha_width + ai_width + 60, sha_lsb)
    glyf_table["sha_o_jsv"] = compose_glyphs(ee_matra, sha_aa, ee_width + 40, 0)
    hmtx_table["sha_o_jsv"] = (sha_width + 780 + ee_width + 60, sha_lsb)
    # Sha + AU (eeMatra on left + sha in middle + auLengthMark on right)
    au_len = glyf_table["auLengthMark_gran"]
    sha_au = compose_glyphs(ee_matra, sha_glyph, 820, 0)
    sha_au = compose_glyphs(sha_au, au_len, 820 + sha_width + 20, 0)
    glyf_table["sha_au_jsv"] = sha_au
    hmtx_table["sha_au_jsv"] = (820 + sha_width + 1300, sha_lsb)

    # Shruu (श्रू) and Shrr (श्रृ) without dotted circles
    sh_ra = compose_glyphs(sha_glyph, ra_vattu, 980, 0)
    glyf_table["sh_ruu_jsv"] = compose_glyphs(sh_ra, uu_matra, 1380, 0)
    hmtx_table["sh_ruu_jsv"] = (2430, sha_lsb)
    glyf_table["sh_r_r_jsv"] = compose_glyphs(sh_ra, r_matra, 1380, 0)
    hmtx_table["sh_r_r_jsv"] = (1800, sha_lsb)

    # Nna + U (णु): attached to right side of Nna without collision
    pen_nna = TTGlyphPen(g_glyph_set)
    g_glyph_set["nna_gran"].draw(pen_nna)
    nna_glyph = pen_nna.glyph()
    nna_width, nna_lsb = gfont["hmtx"]["nna_gran"]
    glyf_table["nna_u_jsv"] = compose_glyphs(nna_glyph, u_matra, 1750, 0)
    hmtx_table["nna_u_jsv"] = (2580, nna_lsb)

    # 4. Create Pla + Grantha matra composites
    pen_pi = TTGlyphPen(g_glyph_set)
    g_glyph_set["pi_gran"].draw(pen_pi)
    pi_glyph = pen_pi.glyph()
    pi_width, pi_lsb = gfont["hmtx"]["pi_gran"]

    pen_pii = TTGlyphPen(g_glyph_set)
    g_glyph_set["pii_gran"].draw(pen_pii)
    pii_glyph = pen_pii.glyph()
    pii_width, pii_lsb = gfont["hmtx"]["pii_gran"]

    pla_aa = compose_glyphs(pla_glyph, aa_matra, pa_width - 80, 0)
    glyf_table["pla_aa_jsv"] = pla_aa
    hmtx_table["pla_aa_jsv"] = (pa_width + aa_width - 60, pa_lsb)

    # Pli: pi_gran + subjoined Malayalam La
    pla_i = compose_glyphs(pi_glyph, la_sub, 1380, 0)
    glyf_table["pla_i_jsv"] = pla_i
    hmtx_table["pla_i_jsv"] = (pi_width, pi_lsb)

    # Plii: pii_gran + subjoined Malayalam La
    pla_ii = compose_glyphs(pii_glyph, la_sub, 1380, 0)
    glyf_table["pla_ii_jsv"] = pla_ii
    hmtx_table["pla_ii_jsv"] = (pii_width, pii_lsb)

    # Plu / Pluu / Pla-virama
    glyf_table["pla_u_jsv"] = compose_glyphs(pla_glyph, u_matra, pa_width - 150, 0)
    hmtx_table["pla_u_jsv"] = (pa_width, pa_lsb)
    glyf_table["pla_uu_jsv"] = compose_glyphs(pla_glyph, uu_matra, pa_width - 150, 0)
    hmtx_table["pla_uu_jsv"] = (pa_width + 400, pa_lsb)
    glyf_table["pla_virama_jsv"] = compose_glyphs(pla_glyph, virama_mlym, pla_glyph.xMax + 50, 0)
    hmtx_table["pla_virama_jsv"] = (pla_glyph.xMax + 120, pa_lsb)

    # 5. Modifiers (All 11 Canonical Vedic Swara Modifiers)
    # Mod 1: High / Mid-Dot (U+E001, U+0971, U+00B7) - Swara Modifier C: larger bold dot aligned to swara baseline
    dot_glyph = draw_circle_glyph(200, 560, 95)
    glyf_table["high_dot_jsv"] = dot_glyph
    hmtx_table["high_dot_jsv"] = (400, 105)

    # Mod 2: Phrasing Danda with Overhead Dot (MOD-F) (U+2577, U+20D3)
    phrasing_danda = draw_phrasing_danda()
    glyf_table["phrasing_danda_jsv"] = phrasing_danda
    hmtx_table["phrasing_danda_jsv"] = (360, 80)

    # Mod 2b: Bold Tone Column (MOD-E) (U+E002, U+2503)
    bold_tone_column = draw_bold_tone_column()
    glyf_table["bold_tone_column_jsv"] = bold_tone_column
    hmtx_table["bold_tone_column_jsv"] = (360, 80)

    # Mod 3: Descending Tone slash (\) (U+E003, U+005C, U+2572, U+27CD) - Swara Modifier G
    descending_tone = draw_descending_tone_slash()
    glyf_table["descending_tone_jsv"] = descending_tone
    hmtx_table["descending_tone_jsv"] = (0, 0)

    # Mod 4: Syllable Spanning Arc (Tie) (U+E004, U+2040, U+0361, U+256D, U+256E) - Swara Modifier A
    syllable_arc = draw_syllable_arc()
    glyf_table["syllable_arc_jsv"] = syllable_arc
    hmtx_table["syllable_arc_jsv"] = (1650, 120)

    # Mod 4b: Syllable Spanning Arc over Danda (U+E00D) - Swara Modifier A1
    syllable_arc_danda = draw_syllable_arc_danda()
    glyf_table["syllable_arc_danda_jsv"] = syllable_arc_danda
    hmtx_table["syllable_arc_danda_jsv"] = (2300, 120)

    # Mod 5: Caret (^) (U+E005, U+005E, U+02C4) - Swara Modifier B (spans 2 syllables)
    caret_glyph = draw_caret()
    glyf_table["caret_jsv"] = caret_glyph
    hmtx_table["caret_jsv"] = (1550, 150)

    # Mod 6: Roof (/\) (U+E006, U+0245, U+2227) - Swara Modifier D (stylized caret spans 2 syllables)
    roof_glyph = draw_roof()
    glyf_table["roof_jsv"] = roof_glyph
    hmtx_table["roof_jsv"] = (1550, 160)

    # Mod 7: Underbar (_) (U+E007, U+005F)
    underbar_glyph = draw_underbar()
    glyf_table["underbar_jsv"] = underbar_glyph
    hmtx_table["underbar_jsv"] = (500, 30)

    # Mod 8: Ascending Tone slash (/) (U+E008, U+002F)
    ascending_tone = draw_ascending_tone_slash()
    glyf_table["ascending_tone_jsv"] = ascending_tone
    hmtx_table["ascending_tone_jsv"] = (360, 80)

    # Mod 9: Combining Small Ring / Circle (ͦ / ˚) (U+E009, U+0366, U+02DA)
    ring_above = draw_ring_above()
    glyf_table["ring_above_jsv"] = ring_above
    hmtx_table["ring_above_jsv"] = (500, 180)

    # Mod 10: Low Comma / Pause Hook (,) (U+E00A, U+002C, U+0326)
    low_comma = draw_low_comma()
    glyf_table["low_comma_jsv"] = low_comma
    hmtx_table["low_comma_jsv"] = (300, 110)

    # Mod 11: Phrasing Double Danda (||) (U+E00B, U+0965)
    double_danda = draw_double_danda()
    glyf_table["double_danda_jsv"] = double_danda
    hmtx_table["double_danda_jsv"] = (400, 80)

    # Mod 12: Overhead Swarita stroke (॑) (U+E00C, U+0951)
    swarita_glyph = draw_swarita()
    glyf_table["swarita_jsv"] = swarita_glyph
    hmtx_table["swarita_jsv"] = (0, -35)

    # Mod 13: Rising Stroke (MOD-D1) (U+E00E, U+2197)
    rising_stroke_d1 = draw_rising_stroke_d1()
    glyf_table["rising_stroke_d1_jsv"] = rising_stroke_d1
    hmtx_table["rising_stroke_d1_jsv"] = (450, 100)

    # Mod 14: Check Tick (MOD-D2) (U+E00F, U+2713)
    check_tick_d2 = draw_check_tick_d2()
    glyf_table["check_tick_d2_jsv"] = check_tick_d2
    hmtx_table["check_tick_d2_jsv"] = (450, 60)

    # Mod 15: Double Shoulder Dash (MOD-I) (U+E02A, U+2AF5)
    double_dash_i = draw_double_shoulder_dash_i()
    glyf_table["double_shoulder_dash_i_jsv"] = double_dash_i
    hmtx_table["double_shoulder_dash_i_jsv"] = (400, 110)

    # Mod 16: Overhead Horizontal Macron/Bar (MOD-J) (U+E02B, U+0304, U+00AF, U+203E)
    overhead_bar_j = draw_overhead_bar_j()
    glyf_table["overhead_bar_j_jsv"] = overhead_bar_j
    hmtx_table["overhead_bar_j_jsv"] = (400, 40)

    # Mod 17: Diagonal Bridging Slash (MOD-B1) (U+E02C)
    bridging_slash_b1 = draw_bridging_slash_b1()
    glyf_table["bridging_slash_b1_jsv"] = bridging_slash_b1
    hmtx_table["bridging_slash_b1_jsv"] = (450, 120)

    # Mod 18: Shoulder Cross Mark (MOD-K) (U+E02D, U+2A2F, U+00D7)
    shoulder_cross_k = draw_shoulder_cross_k()
    glyf_table["shoulder_cross_k_jsv"] = shoulder_cross_k
    hmtx_table["shoulder_cross_k_jsv"] = (400, 120)

    # 6. Update Cmap
    # Add custom mappings to Unicode and PUA codepoints
    custom_cmap = {
        # Malayalam Sha (and redirect Grantha Sha 0x11336 to Malayalam Sha sha_mal)
        0x0D36: "sha_mal",
        0x11336: "sha_mal",
        0x0D4D: "virama_gran",
        0x1134D: "virama_gran",
        # PUA Direct codepoints for Vedic Modifiers
        0xE001: "high_dot_jsv",
        0xE002: "bold_tone_column_jsv",
        0xE003: "descending_tone_jsv",
        0xE004: "syllable_arc_jsv",
        0x2040: "syllable_arc_jsv",
        0x256D: "syllable_arc_jsv",
        0x256E: "syllable_arc_jsv",
        0x203F: "syllable_arc_jsv",
        0xE005: "caret_jsv",
        0xE006: "roof_jsv",
        0xE007: "underbar_jsv",
        0xE008: "phrasing_danda_jsv",
        0xE009: "ring_above_jsv",
        0xE00A: "low_comma_jsv",
        0xE00B: "double_danda_jsv",
        0xE00C: "swarita_jsv",
        0x0951: "swarita_jsv",
        0xE00D: "syllable_arc_danda_jsv",
        0xE00E: "rising_stroke_d1_jsv",
        0x2197: "rising_stroke_d1_jsv",
        0xE00F: "check_tick_d2_jsv",
        0x2713: "check_tick_d2_jsv",
        0xE02A: "double_shoulder_dash_i_jsv",
        0x2AF5: "double_shoulder_dash_i_jsv",
        0xE02B: "overhead_bar_j_jsv",
        0x0304: "overhead_bar_j_jsv",
        0x00AF: "overhead_bar_j_jsv",
        0x203E: "overhead_bar_j_jsv",
        0x02C9: "overhead_bar_j_jsv",
        0xE02C: "bridging_slash_b1_jsv",
        0xE02D: "shoulder_cross_k_jsv",
        0x2A2F: "shoulder_cross_k_jsv",
        0x00D7: "shoulder_cross_k_jsv",
        # Sha family
        0xE010: "sha_aa_jsv",
        0xE011: "sha_i_jsv",
        0xE012: "sha_ii_jsv",
        0xE013: "sha_virama_jsv",
        0xE015: "sha_u_jsv",
        0xE016: "sha_uu_jsv",
        0xE017: "sha_r_jsv",
        0xE018: "sha_rr_jsv",
        0xE019: "sha_e_jsv",
        0xE01A: "sha_ai_jsv",
        0xE01B: "sha_o_jsv",
        0xE01C: "sha_au_jsv",
        # Tra & Kra family
        0xE01D: "t_ra_gran",
        0xE01E: "k_ra_jsv",
        0xE01F: "k_ra_virama_jsv",
        # Pla family
        0xE020: "pla_jsv",
        0xE021: "pla_aa_jsv",
        0xE022: "pla_i_jsv",
        0xE023: "pla_ii_jsv",
        0xE024: "pla_u_jsv",
        0xE025: "pla_uu_jsv",
        0xE026: "pla_virama_jsv",
        # Special clean composites
        0xE027: "sh_ruu_jsv",
        0xE028: "sh_r_r_jsv",
        0xE029: "nna_u_jsv",
        # Standard candidate Unicode characters for modifiers
        0x0971: "high_dot_jsv",       # Devanagari High Spacing Dot
        0x00B7: "high_dot_jsv",       # Middle Dot
        0x2040: "syllable_arc_jsv",    # Character Tie
        0x0361: "syllable_arc_jsv",    # Combining Double Inverted Breve
        0x005E: "caret_jsv",           # Caret
        0x02C4: "caret_jsv",           # Modifier Letter Up Arrowhead
        0x0245: "roof_jsv",            # Latin Letter Turned V / Roof
        0x2227: "roof_jsv",            # Logical AND / Roof
        0x005F: "underbar_jsv",        # Low line
        0x2577: "phrasing_danda_jsv",   # Box drawings light down (L)
        0x20D3: "phrasing_danda_jsv",   # Combining short vertical line overlay
        0x2572: "descending_tone_jsv", # Falling diagonal
        0x27CD: "descending_tone_jsv", # Mathematical falling diagonal
        0x005C: "descending_tone_jsv", # Backslash
        0x002F: "ascending_tone_jsv",  # Solidus / Slash
        0x0366: "ring_above_jsv",      # Combining Latin small letter o
        0x02DA: "ring_above_jsv",      # Ring above
        0x007C: "danda_deva",          # Vertical bar | (Swarita stroke at swara baseline)
        0x2502: "danda_deva",          # Box drawings light vertical
        0x256D: "syllable_arc_jsv",    # Syllable Arc Left ╭
        0x256E: "syllable_arc_jsv",    # Syllable Arc Right ╮
        0x0965: "double_danda_jsv",    # Devanagari Double Danda
        0x1CDA: "high_dot_jsv",        # Vedic tone double-stroke fallback to dot
    }

    # Inject into all cmap sub-tables respecting subtable format limits (format 4: <= 0xFFFF, format 12: full unicode)
    for subtable in cmap_table.tables:
        if subtable.isUnicode():
            for cp, gname in custom_cmap.items():
                if cp <= 0xFFFF or subtable.format == 12:
                    subtable.cmap[cp] = gname

    # 7. Add OpenType Layout Features (GSUB) while preserving ALL 107 native Grantha lookups
    print("Appending custom ligatures to native Grantha GSUB layout table...")
    from fontTools.ttLib.tables import otTables as ot
    gsub = gfont["GSUB"].table

    lig_subst = ot.LigatureSubst()
    lig_subst.ligatures = {}

    def add_ligature(target: str, components: list[str]) -> None:
        first = components[0]
        rest = components[1:]
        lig = ot.Ligature()
        lig.LigGlyph = target
        lig.Component = rest
        if first not in lig_subst.ligatures:
            lig_subst.ligatures[first] = []
        lig_subst.ligatures[first].append(lig)

    # Custom Sha and Pla ligatures
    add_ligature("sha_aa_jsv", ["sha_gran", "aaMatra_gran"])
    add_ligature("sha_i_jsv", ["sha_gran", "iMatra_gran"])
    add_ligature("sha_ii_jsv", ["sha_gran", "iiMatra_gran"])
    add_ligature("sha_virama_jsv", ["sha_gran", "virama_gran"])

    add_ligature("sha_aa_jsv", ["sha_mal", "aaMatra_gran"])
    add_ligature("sha_i_jsv", ["sha_mal", "iMatra_gran"])
    add_ligature("sha_ii_jsv", ["sha_mal", "iiMatra_gran"])
    add_ligature("sha_virama_jsv", ["sha_mal", "virama_gran"])

    add_ligature("pla_jsv", ["pa_gran", "virama_gran", "la_gran"])
    add_ligature("pla_aa_jsv", ["pla_jsv", "aaMatra_gran"])
    add_ligature("pla_i_jsv", ["pla_jsv", "iMatra_gran"])
    add_ligature("pla_ii_jsv", ["pla_jsv", "iiMatra_gran"])

    add_ligature("k_ra_jsv", ["ka_gran", "virama_gran", "ra_gran"])

    # Create new lookup and append to LookupList
    custom_lookup = ot.Lookup()
    custom_lookup.LookupType = 4
    custom_lookup.LookupFlag = 0
    custom_lookup.SubTable = [lig_subst]
    custom_lookup.SubTableCount = 1

    lookup_idx = len(gsub.LookupList.Lookup)
    gsub.LookupList.Lookup.append(custom_lookup)
    gsub.LookupList.LookupCount = len(gsub.LookupList.Lookup)

    # Attach lookup index to active features (ccmp, liga, blwf, psts)
    for feat_rec in gsub.FeatureList.FeatureRecord:
        if feat_rec.FeatureTag in ("ccmp", "liga", "blwf", "psts", "haln"):
            feat_rec.Feature.LookupListIndex.append(lookup_idx)
            feat_rec.Feature.LookupCount = len(feat_rec.Feature.LookupListIndex)

    # 8. Update font names in 'name' table
    name_table = gfont["name"]
    for record in name_table.names:
        if record.nameID in (1, 4):  # Family name & Full name
            record.string = "JaimineeyaVedicSwara"
        elif record.nameID == 6:     # PostScript name
            record.string = "JaimineeyaVedicSwara-Regular"

    OUT_FONT_PATH.parent.mkdir(parents=True, exist_ok=True)
    gfont.save(OUT_FONT_PATH)
    legacy_path = ROOT / "fonts" / "JaimineeyaSwara.ttf"
    gfont.save(legacy_path)
    
    # Also sync to Malayalam_JSV and docs font locations
    m_jsv_font = ROOT / "Malayalam_JSV" / "fonts" / "JaimineeyaSwara.ttf"
    if m_jsv_font.parent.exists():
        gfont.save(m_jsv_font)
    docs_font = ROOT / "docs" / "malayalam" / "fonts" / "JaimineeyaSwara.ttf"
    if docs_font.parent.exists():
        gfont.save(docs_font)

    print(f"Successfully generated custom Vedic Swara font across all locations.")


if __name__ == "__main__":
    build_font()
