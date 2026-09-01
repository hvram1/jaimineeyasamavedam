# LaTeX Workflow & Studio Guide

This guide explains how to effectively manage the Samaveda LaTeX project using **Antigravity** and your local **LaTeX Studio/Workshop** plugin.

## 1. The Power of Pair Programming
While your LaTeX Studio/Workshop plugin provides the visual environment, Antigravity acts as the specialized "typesetting engine" for the Jaimineeya Samavedam.

| Feature | Role of LaTeX Plugin | Role of Antigravity |
| :--- | :--- | :--- |
| **Viewing** | Provides syntax highlighting and PDF preview. | Explains complex Vedic macros (e.g., `\stackleft`). |
| **Editing** | Allows manual one-off tweaks to text. | Performs global, safe, AI-powered structural edits. |
| **Compilation** | Provides "Build" buttons and shortcuts. | Orchestrates the `lualatex` build process via CLI. |
| **Debugging** | Highlights errors in the code. | Analyzes `.log` files to find and fix root causes. |

## 2. Key Project Macros
The project uses custom commands to handle the unique requirements of Vedic typesetting:

### Devanagari Macros
*   **`\stackcenter{Mantrah}{Swarah}`**: Stacks a Swara mark centrally beneath a mantra syllable.
*   **`\stackleft{Mantrah}{Swarah}`**: Used for multi-character Swara marks (aligns based on the project's traditional layout).
*   **`\accentmark{Size}{Char}`**: Dynamically sizes and bolds Devanagari numerals or symbols.
*   **`\accentadj`**: Provides fine-tuned kerning (spacing adjustment) between colliding accents.

### Malayalam Macros & Stacking
*   **`\swarastack{Syllable}{Swara}`**: Dynamic width-aware stacking engine that places red swara notations **above** the base Malayalam akshara without collision.
*   **`\stackcenter{Syllable}{Swara}`** & **`\stackleft{Syllable}{Swara}`**: Overhead stacking commands mapped to `\swarastack`.
*   **`\accentmark{Size}{Char}`**: Sizes Vedic combining marks (`\devafont`) over/under Malayalam aksharas.
*   **`\makeindex` & `\apptocmd{\theindex}{\malayalamfont}{}{}`**: Compiles full two-column alphabetical indices in Malayalam (`അനുക്രമണിക`).

## 3. Recommended Workflow

### Step A: Generation
*   **Devanagari:**
    ```bash
    python src/render_pdf.py data/output/Vargeekaran.json --type samhita
    ```
*   **Malayalam:**
    ```bash
    python src/render_pdf.py data/output/malayalam/Samhita_Malayalam.json --script malayalam
    ```

### Step B: AI-Driven Refinement
Instead of hunting through 20,000+ lines of LaTeX, ask Antigravity to perform targeted shifts:
*   *"Make the Rishi/Devata metadata line purple in the PDF."*
*   *"Increase the vertical gap between the mantra lines by 10%."*

### Step C: Compilation & Preview
Use your plugin's **PDF Preview** to see the changes. If the build breaks, simply tell Antigravity:
> *"The build failed with an error about 'Undefined control sequence'. Please fix it."*

## 4. Environment & Font Requirements
*   **Devanagari**: Compiled with LuaLaTeX/XeLaTeX, `fontspec`, and `AdishilaVedic`.
*   **Malayalam**: Compiled with XeLaTeX (2-pass + `makeindex`) using:
    - Base Text: `NotoSerifMalayalam-Regular.ttf`
    - Superscript Swaras & Modifiers: `JaimineeyaSwara.ttf`
    - Vedic Accents: `NotoSerifDevanagari-Regular.ttf`
    - English Numerals & Footnotes: `Nimbus Roman.ttf`

---
*Created by Antigravity for the Jaimineeya Samavedam Digitalization Project.*

