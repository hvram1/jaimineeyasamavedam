---
name: curate_visual_jsv
description: Protocol for interactive visual curation of Malayalam Jaimineeya Samavedam and synchronization of swara modifier geometry with the custom Vedic font.
---

# Visual JSV Curation & Swara Font Synchronization Skill

This skill defines the operational protocol for using the split-screen **JSV Visual Curation Tool** (`Malayalam_JSV/curation_tool/server.py`) and maintaining strict visual synchronization between CSS live preview styling and the OpenType/TrueType font binaries (`JaimineeyaSwara.ttf` / `JaimineeyaVedicSwara.ttf`).

---

## 1. Golden Rule of Swara Modifier Alignment

> [!IMPORTANT]
> **Font Synchronization Requirement**:
> The positioning of the swara modifiers in the JSV Curation tool should be reflected to the font file as well.
> Whenever a modifier's vertical or horizontal offset is adjusted in `Malayalam_JSV/curation_tool/static/style.css` (e.g. `MOD-J`, `MOD-B1`, `MOD-H`, `MOD-D1`, `MOD-D2`), the exact equivalent contour coordinates must be updated in `scripts/build_swara_font.py` and all font binaries regenerated.

---

## 2. Font Rebuilding Procedure

When modifier geometry is refined in CSS:
1. **Update Python Glyph Draw Function**:
   - Edit the respective contour drawing function in `scripts/build_swara_font.py` (e.g. `draw_overhead_bar_j()`, `draw_bridging_slash_b1()`, `draw_double_shoulder_dash_i()`).
2. **Rebuild Font Binaries**:
   ```bash
   python scripts/build_swara_font.py
   ```
   This automatically updates:
   - `fonts/JaimineeyaVedicSwara.ttf`
   - `fonts/JaimineeyaSwara.ttf`
   - `Malayalam_JSV/fonts/JaimineeyaSwara.ttf`
   - `docs/malayalam/fonts/JaimineeyaSwara.ttf`
3. **Bump Font Cache Version**:
   - In `Malayalam_JSV/curation_tool/static/style.css`, bump the `@font-face` query string (e.g. `src: url('/fonts/JaimineeyaSwara.ttf?v=3.5')`).
   - In `Malayalam_JSV/curation_tool/static/index.html`, bump the stylesheet query string (e.g. `style.css?v=3.1`).

---

## 3. Visual Curation Server Operation

- **Start Tool**:
  ```bash
  python Malayalam_JSV/curation_tool/server.py
  ```
- **Access**: Open `http://localhost:8080/` in browser.
- **Workflow**:
  1. Inspect manuscript crop on left pane.
  2. Edit Malayalam text and swara tokens `(𑌪𑍍𑌲𑍁)`, `(C)`, `(G)`, `(H)`, `(D1)`, `(B1)`, `(J)`, `_`, `.`, `,` on right pane.
  3. Verify live accent-rendered preview.
  4. Save changes with `Ctrl + S`.
  5. Run active-learning benchmark tracker:
     ```bash
     python Malayalam_JSV/extraction/track_accuracy_benchmark.py
     ```
