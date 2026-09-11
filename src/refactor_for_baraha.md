The user wants a clean two-step pipeline:

Step 1: vedavms html/transliterate.py (or src/baraha_reader.py) converts Baraha .docx → JSON (with proper title, content_lines, etc.)
Step 2: src/render_pdf.py takes that JSON → PDF, HTML, TXT (just like it does for JSV)
This is architecturally cleaner because:

render_pdf.py stays focused on rendering from JSON
No special .docx code path inside render_pdf.py
The JSON becomes the canonical intermediate format
The Baraha conversion logic lives in its own script
I need to figure out which script should be the entry point. transliterate.py currently only has the baraha_to_devanagari() function, while baraha_reader.py already handles the full DOCX-to-JSON pipeline including extraction and AST generation. So baraha_reader.py seems like the better fit as the actual entry point, since transliterate.py would need significant additions to match that functionality.

I'm leaning toward making baraha_reader.py a standalone CLI that generates JSON from .docx, removing the special .docx/--baraha handling from render_pdf.py, and fixing the title resolution logic there so Devanagari titles work correctly. But since the user specifically mentioned running transliterate.py to generate the JSON, I should reconsider whether they want that file enhanced instead, even though the pipeline logic already exists elsewhere.

I also need render_pdf.py's title resolution to correctly pick up Devanagari meta.title from the generated JSON, and I should simplify or remove the --baraha special-case path. Given the architectural nature of these changes, I want to confirm the plan with the user before implementing.

Yes, that's the right architectural approach — it mirrors the standard JSV pipeline:

generate_json.py  →  JSON  →  render_pdf.py  →  PDF/HTML/TXT   (JSV path)
baraha_reader.py  →  JSON  →  render_pdf.py  →  PDF/HTML/TXT   (Baraha path)

Here's what needs to happen:

Make baraha_reader.py a standalone CLI (like generate_json.py) — it already has the DOCX→JSON logic; just needs a __main__ block. It imports transliterate.py for the actual Baraha→Devanagari conversion.

Fix render_pdf.py title resolution — when the JSON has a Devanagari meta.title (like "तैत्तिरीयोपनिषत्"), use it directly instead of defaulting to "जैमिनीय साम संहिता".

Remove the --baraha / .docx special path from render_pdf.py — render_pdf.py should only accept JSON, keeping it clean.

The workflow would be:

# Step 1: Generate JSON from Baraha DOCX
python src/baraha_reader.py "vedavms html/tu_baraha.docx" -o "vedavms html/tu_baraha.json"

# Step 2: Render PDF/HTML/TXT from JSON (standard path)
python src/render_pdf.py "vedavms html/tu_baraha.json" 