# JSV Visual Curation Tool

Interactive browser-based workspace for curating Malayalam Vedic Samavedam text against high-resolution manuscript scans.

## Quick Launch
```bash
python server.py
```
Open **[http://localhost:8080/](http://localhost:8080/)** in your browser.

## Features
- **Split & Stacked Views**: View handwritten palm-leaf/paper scans side-by-side with live Unicode editing.
- **Deep Zoom & Contrast**: Zoom 10%–500% with mouse wheel and toggle high-contrast inversion (`🌓`).
- **Direct Subsection Jump**: Quickly navigate across all 6 Parvas by typing subsection numbers.
- **1-Click Modifier Palette**: Insert Vedic Swarita (`(H)`), Under-Slash (`(G)`), Dot (`(C)`), Slur Arc (`(A)`), Peak Caret (`(B)`), Hooked Rise (`(D)`), etc.
- **Live Stacking Preview**: Visual real-time rendering of blue accents over Malayalam aksharas.
- **Keyboard Shortcuts**: `Ctrl+S` (Save), `Ctrl+[`/`Ctrl+]` (Navigate Samams), `Alt+H`/`Alt+G`/`Alt+C` (Insert modifiers).

For the complete architectural guide and active-learning protocol, see:
- [Visual Curation Tool Guide](../../.agent/documentation/VISUAL_CURATION_TOOL.md)
