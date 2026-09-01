from fontTools.ttLib import TTFont

font_path = "/System/Library/Fonts/Apple Color Emoji.ttc"  # Replace with the actual path
font = TTFont(font_path)
cmap = font['cmap'].getcmap(3, 1).cmap
# cmap is a dictionary mapping character codes to glyph names

for char_code, glyph_name in cmap.items():
    try:
        unicode_value = chr(char_code)
        print(f"Character: {unicode_value}, Code Point: U+{char_code:04X}, Glyph Name: {glyph_name}")
    except ValueError:
        # Handle non-BMP characters (outside the basic multilingual plane)
        print(f"Character: (Non-BMP), Code Point: U+{char_code:04X}, Glyph Name: {glyph_name}")

font.close()