# Automated Vision Extraction — Full Samhita Drafting Layer

## Goal

Insert swara modifier annotations `(A)`, `(B)`, `(C)`, `(D)`, `(E)`, `(G)`, `(H)` and phrasing marks (`_`, `.`, `,`) into all **677 uncurated subsections** of [`Samam_Malayalam_Unicode.txt`](file:///c:/Users/sekha/OneDrive/Documents/GitHub/jaimineeyasamavedam/data/input/Malayalam/Samam_Malayalam_Unicode.txt) by reading the manuscript scan.

> [!IMPORTANT]
> **Single file contract**: `data/input/Malayalam/Samam_Malayalam_Unicode.txt` is the **only** input and output. No other Malayalam text file is read or written.

**Manuscript source:** `G:\My Drive\Jaimineeya Sama Veda Archive\Archives\JSV Samhita Malayalam.pdf`  
- 324 pages, ~43 MB, image-based (no text layer — pure scan)
- Swara modifiers are **small red diacritics** printed above/below/beside Malayalam aksharas
- Average density: **~2.2 subsections per page**

---

## Revised Current State

| Item | Status |
|---|---|
| Total subsections | 722 |
| Modifier-annotated (done) | 45 (sub_1 – sub_48) |
| Remaining to extract | **677** (sub_49 – sub_727 + Indra sub_1413–1517) |
| Source PDF | `JSV Samhita Malayalam.pdf` (324 pages, Google Drive) |
| PDF text layer | **None** — pure image scan |
| Existing page scans | pages 3–25 already in `Malayalam_JSV/scans/page_003.png` – `page_025.png` |
| Pages still to render | **26–324** (299 pages) |
| Already done scans cover | Agneyam K1–K6 (sub_1 through ~sub_80) |

> [!IMPORTANT]
> The PDF is **image-only** — no text layer is extractable. All modifier extraction **must be done via visual inspection** of the rendered PNG pages.

---

## Page Range Estimates

Based on 722 subs across ~319 content pages (pages 5–324):

| SuperSection | Name | Sub Range | Sub Count | Est. Pages |
|---|---|---|---|---|
| supersection_1 | Agneyam | sub_1 – sub_125 | 125 | pages 5 – 60 |
| supersection_2 | Tadva | sub_127 – sub_250 | 124 | pages 60 – 115 |
| supersection_3 | Bruhati | sub_252 – sub_346 | 95 | pages 115 – 157 |
| supersection_4 | Asaavi | sub_348 – sub_411 | 64 | pages 157 – 185 |
| supersection_5 | Aindra | sub_1413 – sub_1517 | 105 | pages 185 – 231 |
| supersection_6 | Pavamana | sub_519 – sub_727 | 209 | pages 231 – 323 |

**Sub_49 starts at approximately page 21** (mid Agneyam Kandah 4, section_4).  
Existing `page_025.png` reaches approximately subsection 80 (mid Agneyam K6).  
**All pages from 26 onward need rendering.**

---

## Workflow: 3-Layer Pipeline

```
JSV Samhita Malayalam.pdf (Google Drive, pages 26-324)
    |
    v
[STEP 1] Batch Slice -> PNG images (page_026.png ... page_324.png)
    |  Script: Malayalam_JSV/extraction/slice_pages.py
    |  Output dir: Malayalam_JSV/scans/  (continuing page_NNN.png naming)
    |  ~10 min to render all 299 pages at 300 DPI
    |
    v
[STEP 2] Page-to-Subsection Map -> page_map.json
    |  Script: NEW Malayalam_JSV/extraction/build_page_map.py
    |  Reads PNG images via vision model, identifies Kandah/Samam numbers
    |  Output: stage_output/page_map.json
    |
    v
[STEP 3] Vision Extraction -> Modifier Draft (per-Kandah candidate .txt)
    |  Tool: Vision model (Claude/Gemini) reading each PNG
    |  For each subsection, reads red modifier marks and inserts annotations
    |  Output: stage_output/candidates/SS<n>_K<m>_candidate.txt
    |
    v
[STEP 4] Validate + Merge -> Samam_Malayalam_Unicode.txt
    |  Script: NEW merge_candidates.py + existing validate_modifiers.py
    |  Guardrails: zero base-text or Grantha regressions
    |  Output: Updated Samam_Malayalam_Unicode.txt
    |
    v
[STEP 5] Interactive Curation
       Tool: http://localhost:8080
       Human review of ~10% edge cases, ambiguous marks
```

---

## Proposed Changes

### Phase A — Batch PDF Rendering

#### [MODIFY] [`slice_pages.py`](file:///c:/Users/sekha/OneDrive/Documents/GitHub/jaimineeyasamavedam/Malayalam_JSV/extraction/slice_pages.py)
- Add `--start-page` / `--end-page` / `--dpi` CLI args (300 DPI default)
- Point at `G:/My Drive/Jaimineeya Sama Veda Archive/Archives/JSV Samhita Malayalam.pdf`
- Output to `Malayalam_JSV/scans/page_NNN.png` (4-digit zero-padded)

**Run once to produce all remaining pages:**
```powershell
python -X utf8 Malayalam_JSV/extraction/slice_pages.py `
    --pdf "G:/My Drive/Jaimineeya Sama Veda Archive/Archives/JSV Samhita Malayalam.pdf" `
    --out Malayalam_JSV/scans --dpi 300 --start-page 26
```

---

### Phase B — Page-to-Subsection Map

#### [NEW] `Malayalam_JSV/extraction/build_page_map.py`
- Reads each PNG via lightweight OCR (looking for page headers like `ആഗ്നേയം ഖണ്ഡം 4`, `ഖണ്ഡം 5` etc. and Samam numbers `1`, `2`, ... in the left margin)
- Cross-references against the known subsection list in `Samam_Malayalam_Unicode.txt`
- Outputs `stage_output/page_map.json` — `{ "page_026": ["subsection_80", "subsection_81"], ... }`

---

### Phase C — Vision Extraction (Core Task)

#### Strategy: Supersection-by-supersection, Kandah-by-Kandah batches

For each batch of 3–5 pages (~6–10 subsections):
1. Read the PNG scans
2. For each subsection visible on the page, identify **black-ink** modifier marks
   (red ink = Grantha swara letters already transliterated — IGNORE all red;
   see `vision_prompt.md` §2 for the full color rule):
   - Black **subscript slash** below an akshara → `(G)`
   - Black **vertical bar / swarita** above akshara → `(H)`
   - Black **overhead arc** bridging syllables → `(A)` or `(A1)` over danda
   - Black **caret/roof** above → `(B)` with swara on peak
   - Black **chevron** spanning syllables → `(D)`
   - Black **dot** at shoulder (raised) → `(C)`; black dot at baseline → `.`
   - Black **bold vertical stroke** inline → `(E)`
   - Black **underbar** connecting words → `_`
   - Black **comma** pause mark → `,`
3. Insert annotations at correct akshara positions in the existing text
4. Save to candidate file

#### Per-Supersection extraction scripts:

#### [NEW] `Malayalam_JSV/extraction/extract_agneyam_rest.py`
- sub_49 – sub_125, pages ~21–60

#### [NEW] `Malayalam_JSV/extraction/extract_tadva.py`
- sub_127 – sub_250, pages ~60–115

#### [NEW] `Malayalam_JSV/extraction/extract_bruhati.py`
- sub_252 – sub_346, pages ~115–157

#### [NEW] `Malayalam_JSV/extraction/extract_asaavi.py`
- sub_348 – sub_411, pages ~157–185

#### [NEW] `Malayalam_JSV/extraction/extract_aindra.py`
- sub_1413 – sub_1517, pages ~185–231

#### [NEW] `Malayalam_JSV/extraction/extract_pavamana.py`
- sub_519 – sub_727, pages ~231–323

---

### Phase D — Merge Utility

#### [NEW] `Malayalam_JSV/extraction/merge_candidates.py`
- Reads candidate `.txt` files from `stage_output/candidates/`
- Patches `Samam_Malayalam_Unicode.txt` subsection by subsection
- Strict guardrails:
  - Malayalam base text: bit-exact match
  - Grantha swara parentheses: unchanged
  - Only modifier tokens from canonical lexicon allowed
- Produces `stage_output/merge_report.txt`

---

### Phase E — Benchmark

#### [NEW] `Malayalam_JSV/extraction/benchmark_full_samhita.py`
- Reports per-subsection modifier coverage across all 722 subs
- Shows which supersections are complete vs pending

---

## Open Questions

> [!IMPORTANT]
> **Q1 — Vision extraction granularity**: Should each vision extraction session process:
> - **(a) Page-by-page** — one PNG at a time (~2–3 subsections each), simpler, more API calls
> - **(b) Kandah-by-Kandah** — pass 3–5 pages at once with the full Kandah Malayalam text as context, giving the model more anchor points for accurate modifier placement
> Option (b) is recommended as the existing text in `Samam_Malayalam_Unicode.txt` can serve as the exact Malayalam syllable anchor for each position.

> [!NOTE]
> **Q2 — Parallelism**: The 299 pages can be processed in parallel subagents (one per supersection, 6 concurrent). Estimated time: ~2–4 hours parallel vs ~14–20 hours serial. Approve parallel processing?

---

## Verification Plan

### Automated Tests
```powershell
python -X utf8 Malayalam_JSV/extraction/validate_modifiers.py
python -X utf8 Malayalam_JSV/extraction/benchmark_full_samhita.py
```

### Success Criteria
- Zero base-text regressions (Malayalam syllables bit-exact)
- Zero Grantha swara code regressions
- >= 90% of 677 subsections have at least one modifier annotation
- All inserted tokens pass canonical modifier lexicon check

### Manual Verification
- Spot-check 10 random subsections per supersection in curation tool at `http://localhost:8080`
