---
name: manage_prayoga_procedures
description: Guidelines on constructing and embedding structural Prayoga instructions (Markdown) into both the dynamic Vedic Website and compiled LaTeX/PDF Appendices.
---

# Manage Prayoga Procedures Skill

This skill explains how **Procedural Descriptions (Prayoga)** are mapped from explicit Markdown definitions into both our website architecture and the compiled TeX/PDF pipelines.

## 1. Directory Structure & Markdown
All procedural content should be written using standard Markdown to maintain platform independence, and stored within:
`data/input/prayoga/*.md`

The pipeline expects simple Markdown structuring (Headers `#`, `##`, `###`, bold `**`, italic `*`, and list items `- `) internally.

## 2. Prayoga Index Mapping (YAML)
We explicitly map procedures to hierarchy blocks using the configuration map inside `data/input/prayoga/prayoga_index.yaml`.
*   **Scopes**: Can be attached at `supersection`, `section`, or `subsection` levels.
*   **Resolution Logic**: Both Web and PDF logic search for matches by ascending the nested structures. If a particular `subsection` does not possess a specific procedure, the pipeline inherits its parent `section` procedure, and so on.
*   **CLI Integration**: To inject procedure references into JSON, use the `--procedures` flag:
    ```bash
    python src/generate_json.py <input.txt> --procedures data/input/prayoga/prayoga_index.yaml --output output.json
    ```
    If `--procedures` is omitted, no procedure links are added (default: no procedure).

*Example YAML Entry:*
```yaml
procedures:
  - scope: section
    id: section_1
    file: aupasanam.md
    title: औपासनम् - विधिः
```

## 3. Web Implementation (HTML)
*   **Generation Step**: The script `src/generate_website.py` aggregates `prayoga_index.yaml`.
*   **Class Addition**: Inside the `.Sama` dataclasses, the attribute `procedure_ref` is dynamically tied to the matched subset hierarchy.
*   **Dedicated Webpages**: The generator outputs entirely dedicated HTML web pages for each matched Prayoga definition inside directories comparable to (e.g., `docs/aranam/prayoga/udakashanti.html`).
*   **Linking**: The Jinja2 logic appends a navigation hyperlink right alongside the Vedic text header allowing instant browser redirection.

## 4. LaTeX / PDF Integration (Appendix)
*   **In-Memory Injection**: Unlike the website export, `src/render_pdf.py` must load the original JSON configuration (ex: `Prayogamala-Purvabhagam_out.json`) and run the `prayoga_index.yaml` mapping **in real-time** internally directly over the structure blocks.
*   **Conversion (No Dependencies)**: `render_pdf.py` uses bespoke regex loops to quickly compile Prayoga Markdown down to functional TeX logic (generating `.tex` `\vspace`, `\section*`, `\textbf`, and `\bullet`).
*   **Jinja Document Template (`Devanagari_main.template`)**:
    1.  **Appendix Aggregation Block**: All matched procedures are automatically printed entirely under `\chapter*{ ॥ परिशिष्टम् (Appendix) ॥ }` immediately preceding `\printindex` at the end of the document.
    2.  **Referencing Hooks**: The parsed blocks have injected hooks generated (`\phantomsection \label{app:slug}`).
    3.  **Footnote Jumps**: `render_pdf.py` automatically injects matching `.aux`-compilable footnotes straight onto the relevant Samam text (`\footnote{{Title} - \hyperref[app:{slug}]{परिशिष्टम् पश्यतु (See Appendix)}}`).

## 5. Critical Troubleshooting
If the footnotes inside generating PDFs refuse to successfully jump over click interaction:
*   Ensure the host `templates/pdf/Devanagari_main.template` loads the `\usepackage[perpage]{footmisc}` package **PRIOR** to `\usepackage{hyperref}` to prevent `footmisc` from wiping internal anchor dependencies entirely.
*   Ensure that the final LuaLaTeX compilation runs **at least two times** recursively over the `.tex` output, otherwise `.aux` markers will fail internally. Using `latexmk` resolves this.
