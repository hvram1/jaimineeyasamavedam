# Instruction Manual: Multi-LLM Visual Swara Extraction for Jaimineeya Samavedam

This guide explains how to use an external Vision-capable Large Language Model (e.g., Claude 3.5 Sonnet, GPT-4o, Gemini 1.5 Pro) to perform high-fidelity visual swara modifier extraction from the handwritten Malayalam JSV manuscript scans.

---

## 1. High-Level Mission

Our objective is to annotate the master Malayalam Unicode text file with **visual swara modifiers** (`(G)`, `(C)`, `(H)`, `(A)`, `(D)`, `(B)`, `_`, `.`, `,`) by inspecting the high-resolution scanned manuscript pages (`Malayalam_JSV/scans/page_XXXX.png`).

### The Golden Rule: Zero-Regression on Base Text
**You ONLY insert modifier tokens and inline phrasing marks.**
- **NEVER** alter Malayalam letters, vowel signs (matras), or conjuncts.
- **NEVER** delete, modify, or add Grantha swara tokens (e.g. `(𑌤𑌿)`, `(𑌪𑍍𑌲)`, `(𑌫𑌾)`).
- **NEVER** modify verse numbers (`॥1॥`, `॥2॥`, etc.) or base dandas (`।`, `॥`).
- **NEVER** remove or alter whitespace between words.

If you strip all modifiers from your generated candidate text, it **MUST IDENTICALLY MATCH** the master input text character-by-character:
$$\text{strip\_modifiers}(\text{Candidate}) == \text{strip\_modifiers}(\text{Master})$$

---

## 2. The Color Rule (Crucial)

The manuscript is written using **two distinct inks**:

| Ink Color | Meaning | What to do |
| :--- | :--- | :--- |
| **RED INK** | Grantha swara letters written above/below words (e.g., തി, ത്ത്, ഖ, ടു, and letter-like ligatures). These swaras are **already captured** as Unicode Grantha tokens (like `(𑌤𑌿)`) in the master file. | **IGNORE UNCONDITIONALLY.** Never transcribe red characters or emit modifiers for red marks. |
| **BLACK INK** | Base Malayalam aksharas AND non-base swara modifiers/strokes (slashes, dots, vertical bars, arcs, roofs, underbars, commas). | **EXTRACT THESE.** Non-base black strokes attached to or hovering over/under black Malayalam aksharas are the swara modifiers. |

> **Summary:** Look ONLY for non-base **black ink marks**. Red ink marks are already converted to Grantha tokens in the master text.

---

## 3. Visual Modifier Token Lexicon

| Token | Name | Visual Appearance & Position | Scope / Placement |
| :---: | :--- | :--- | :--- |
| `(G)` | **Descending Slash** | Short diagonal slash or small hook attached **below** the bottom-right of a Malayalam akshara. Looks like a tiny `\`, `L`, or hook. *(Most frequent mark ~70%)* | Immediately after the modified akshara (e.g., `അ(G)ഗ്നേ`) |
| `(C)` | **Shoulder Dot** | Small raised dot at the **top-right shoulder** of an akshara (distinct from baseline punctuation). | Immediately after the akshara (e.g., `ദേ(C)വാ`) |
| `(H)` | **Swarita Bar** | Small vertical stroke **centered directly above** an akshara (standard Vedic Swarita). | Immediately after the akshara (e.g., `മാ(H)നോ`) |
| `(A)` | **Syllable Arc** | Smooth curved arc/slur **above** two adjacent syllables or across a word boundary. | Encloses/marks the syllable or phrase |
| `(A1)` | **Danda Arc** | Curved arc centered **directly over a danda `।`**. | Placed over/after the danda |
| `(B)` | **Peak Caret** | `^`-shaped chevron roof centered **above** a single syllable. | Immediately after the syllable |
| `(D)` | **Chevron Roof** | Wide `Ʌ`-shaped roof **above the line spanning 2+ syllables** across word boundaries. | Placed after the first/spanning unit |
| `(E)` | **Heavy Column** | Heavy vertical bar inline at baseline height. | Inline |
| `_` | **Sustain Underbar** | Low horizontal connecting bar **joining two words at baseline**. | Inline between words (e.g., `മാ(G)തോ_ വാ(𑌶)`) |
| `.` | **Pause Dot** | Dot at **baseline level** after a word (breath/cadence pause). | Inline after word (e.g., `ഹോതാ(𑌚𑌾).`) |
| `,` | **Low Comma** | Comma at **baseline level** after a word (minor pause). | Inline after word (e.g., `ഹോ(𑌕),`) |

---

## 4. Master Text Subsection Structure

The master text is organized into bounded subsections:

```text
#Start of Mantra Sets -- subsection_127 ## DO NOT EDIT
തദ്വോ(𑌫𑍀) ഗായാ(𑌚𑌾) സുതേ(𑌕𑌿) ശുചാ(𑌚𑌾) ...
#End of Mantra Sets -- subsection_127 ## DO NOT EDIT
```

When annotating, you must preserve the exact `#Start of Mantra Sets` and `#End of Mantra Sets` delimiter lines.

---

## 5. Concrete Annotation Example

### Master (Unannotated Base):
```text
#Start of Mantra Sets -- subsection_117 ## DO NOT EDIT
പ്രാസോ(𑌟𑌾),  ഹാ(𑌤).  ആഗ്നേ(𑌟𑌾)  ഹാ(𑌤). ഇ(𑌶)    ।  തവാ(𑌤𑌾)_ ആഉവാ(𑌟𑌿) । തീ(𑌖). ഭീഃ(𑌪𑍍𑌲).  ।  സൂവീ(𑌚𑌾)_ രാ(𑌶),  ഭിസ്താരാ(𑌚𑌿), തീവാ(𑌚𑌾). ജക(𑌕𑌾)_ ൪മാഭി൪യാ(𑌚𑌿) സ്യാ(𑌟) ഹാ(𑌤). ഇ(𑌶)  ।  ത്വംസാ(𑌪𑌾)  ഖ്യമോബാ(𑌪𑍍𑌲𑌿).  വാഇഥോ(𑌪𑍍𑌲𑌿)  ।ഹാഇ(𑌶𑌾) ॥5॥
#End of Mantra Sets -- subsection_117 ## DO NOT EDIT
```

### Visual Observation on Manuscript Scan:
- `പ്രാ` has a vertical swarita bar on top $\rightarrow$ `പ്രാ(H)`
- `ആഗ്നേ` has a bottom-right slash on `ആ` $\rightarrow$ `ആ(G)ഗ്നേ`
- `സൂവീ` has a bottom-right slash on `സൂ` $\rightarrow$ `സൂ(G)വീ`
- `ഭിസ്താരാ` has a bottom-right slash on `ഭി` $\rightarrow$ `ഭി(G)സ്താരാ`
- `ജക` has a bottom-right slash on `ജ` $\rightarrow$ `ജ(G)ക`
- `ത്വംസാ` has a bottom-right slash on `ത്വം` $\rightarrow$ `ത്വം(G)സാ`

### Output Candidate (Annotated):
```text
#Start of Mantra Sets -- subsection_117 ## DO NOT EDIT
പ്രാ(H)സോ(𑌟𑌾),  ഹാ(𑌤).  ആ(G)ഗ്നേ(𑌟𑌾)  ഹാ(𑌤). ഇ(𑌶)    ।  തവാ(𑌤𑌾)_ ആഉവാ(𑌟𑌿) । തീ(𑌖). ഭീഃ(𑌪𑍍𑌲).  ।  സൂ(G)വീ(𑌚𑌾)_ രാ(𑌶),  ഭി(G)സ്താരാ(𑌚𑌿), തീവാ(𑌚𑌾). ജ(G)ക(𑌕𑌾)_ ൪മാഭി൪യാ(𑌚𑌿) സ്യാ(𑌟) ഹാ(𑌤). ഇ(𑌶)  ।  ത്വം(G)സാ(𑌪𑌾)  ഖ്യമോബാ(𑌪𑍍𑌲𑌿).  വാഇഥോ(𑌪𑍍𑌲𑌿)  ।ഹാഇ(𑌶𑌾) ॥5॥
#End of Mantra Sets -- subsection_117 ## DO NOT EDIT
```

---

## 6. Prompt Template to Send to Any External LLM

When delegating a batch to an external LLM (Claude, ChatGPT, Gemini), copy and paste the prompt below along with the relevant scanned manuscript image(s):

````markdown
You are an expert Vedic epigraphist and Sanskrit/Malayalam manuscript transcriber specializing in Jaimineeya Samavedam (JSV) musical notations.

TASK:
Inspect the attached high-resolution manuscript image(s) and insert the visual swara modifiers into the provided Malayalam master text block.

STRICT RULES:
1. COLOR RULE: IGNORE RED INK completely. Red characters are Grantha swara letters already present as Unicode Grantha tokens in the text. Look ONLY for non-base BLACK INK marks.
2. ZERO-REGRESSION: Do NOT alter base Malayalam letters, Grantha tokens, punctuation (।, ॥), numerals, or spacing. ONLY insert visual modifier tokens.
3. TOKEN LEXICON:
   - `(G)` : Descending slash attached below bottom-right of an akshara (e.g., `അ(G)ഗ്നേ`)
   - `(C)` : Raised shoulder dot at top-right of an akshara (e.g., `ദേ(C)വാ`)
   - `(H)` : Vertical swarita bar centered above an akshara (e.g., `മാ(H)നോ`)
   - `(A)` : Syllable-spanning arc above the line
   - `(A1)`: Arc over danda `।`
   - `(B)` : Peak caret roof `^` above syllable
   - `(D)` : Wide chevron roof `Ʌ` above line spanning 2+ syllables
   - `_`   : Underbar connector between words at baseline
   - `.`   : Pause dot inline at baseline
   - `,`   : Low comma inline at baseline

MASTER TEXT TO ANNOTATE:
```text
[PASTE MASTER TEXT SUBSECTIONS HERE]
```

OUTPUT FORMAT:
Return ONLY the completed text with `#Start of Mantra Sets` and `#End of Mantra Sets` tags. Do NOT wrap in markdown formatting or add explanatory conversation.
````

---

## 7. Automated Ingestion & Verification Workflow

Once the external LLM responds:

1. **Save Output to Candidates Directory**:
   Save the returned text into:
   `Malayalam_JSV/stage_output/candidates/<Batch_Name>_candidate.txt`

2. **Automated Validation & Merge**:
   Run the merge tool:
   ```bash
   python Malayalam_JSV/extraction/merge_candidates.py
   ```
   - If the candidate passes zero-regression (`strip_modifiers(candidate) == strip_modifiers(master)`), it will automatically merge into master `Samam_Malayalam_Unicode.txt`.
   - If any character mismatch exists, it will report the exact line and error with 0 risk of repository corruption.

3. **Check Benchmark Progress**:
   ```bash
   python Malayalam_JSV/extraction/benchmark_full_samhita.py
   ```
