# pdfconverter — Technical Reference

> This document is the authoritative technical reference for the Vedic PDF/DOCX → Devanagari → Malayalam conversion pipeline.  
> It covers: end-to-end conversion steps, the complete Sanskrit98 font byte map (with glyph identification notes), algorithmic internals, and tricky edge cases.

---

## Table of Contents
1. [Conversion Pipelines — End-to-End Steps](#1-conversion-pipelines--end-to-end-steps)
2. [Sanskrit98 Font Byte Map](#2-sanskrit98-font-byte-map)
3. [Glyph Identification Notes — Where Draft Differs from Decoder](#3-glyph-identification-notes--where-draft-differs-from-decoder)
4. [Baraha Encoding Reference](#4-baraha-encoding-reference)
5. [Decoder Internals — Algorithm Detail](#5-decoder-internals--algorithm-detail)
6. [Transliteration and Document Generation](#6-transliteration-and-document-generation)

---

## 1. Conversion Pipelines — End-to-End Steps

### Pipeline A — Sanskrit98 Font-Encoded PDF (e.g. `maha_s.pdf`, Sringeri Paddhati)

```
INPUT: legacy Sanskrit98 PDF
       |
       v Step 1 — Font stream extraction
       |  Tool: PyPDF2 / pypdf  ContentStream walker
       |  Reads raw binary bytes from each Tf/Tj/TJ operator
       |  in the PDF content stream. These bytes are NOT Unicode —
       |  they are private glyph codes for the Sanskrit98 font.
       |  Output: list of byte arrays, one per text chunk, with
       |  y/x position, font tag, and font size metadata.
       |
       v Step 2 — Font byte -> Devanagari Unicode decoding
       |  Tool: src/sanskrit98_decoder_v5.py  decode_bytes()
       |  Maps each byte via the CHAR table (139 entries, 0x01-0x8B)
       |  Assembles syllables, handles deferred i-matra and Repha,
       |  attaches Svarita/Anudatta accent marks.
       |  Runs clean_repetitions() to strip font duplication artifacts.
       |  Output: Unicode Devanagari string per text line.
       |
       v Step 3 — [Human] Review and edit Devanagari text
       |  mahanyasam_devanagari.txt (or data/output/*_devanagari.txt)
       |  Optional manual corrections to accent placement, spacing.
       |
       v Step 4 — Devanagari -> Malayalam transliteration
       |  Tool: src/convert_devanagari_to_malayalam.py
       |  Uses aksharamukha library (Devanagari -> Malayalam script).
       |  Vedic accent marks (ANUDATTA UDATTA DIRGHA SVARITA GOMUKHA
       |  CANDRABINDU AVAGRAHA) are protected with placeholders before
       |  transliteration and restored after.
       |  Post-processing: accent reordering, dotted-circle cleanup,
       |  word-final halant-m -> anusvara, doubled matra collapse.
       |
       v Step 5 — Smart layout classification
       |  Each line is classified by pattern matching:
       |  * double-danda...double-danda  -> Main Title (24pt, bold, centered)
       |  * atha...  -> Section Subtitle (19pt, bold, centered)
       |  * (EAST) etc -> Direction marker (italic, centered)
       |  * ...rudraya namah double-danda -> Section header (bold, left)
       |  * Everything else -> Mantra body (16pt)
       |
       v Step 6 — HTML generation
       |  Self-contained HTML with Noto Serif Malayalam/Devanagari fonts,
       |  A4 @page CSS, Anudatta lowering span, Malayalam/Devanagari toggle.
       |
       v Step 7 — PDF generation
          Headless MS Edge / Chrome prints HTML -> A4 PDF.

OUTPUT: *_devanagari.txt, *_malayalam.txt, *_malayalam.html, *_malayalam.pdf
```

**CLI for Step 2+:**
```bash
# From text file (after manual edit):
python src/convert_devanagari_to_malayalam.py \
  --input mahanyasam_devanagari.txt \
  --output data/output/mahanyasam_malayalam.txt \
  --html data/output/mahanyasam_malayalam.html \
  --pdf data/output/mahanyasam_malayalam.pdf

# Directly from PDF (steps 1+2 happen automatically):
python src/convert_devanagari_to_malayalam.py \
  --input maha_s.pdf \
  --output data/output/mahanyasam_malayalam_pdfin.txt \
  --html data/output/mahanyasam_malayalam_pdfin.html \
  --pdf data/output/mahanyasam_malayalam_pdfin.pdf
```

---

### Pipeline B — Baraha-Encoded DOCX (Primary Path Going Forward)

```
INPUT: Baraha DOCX (e.g. SivaStuti_baraha_vedavms.docx)
       |
       v Step 1 — DOCX text extraction
       |  Tool: mammoth.extract_raw_text()
       |  Extracts plain text preserving <lang=eng> / <lang=def> tags
       |  that Baraha software embeds to mark English vs Sanskrit sections.
       |  Output: raw text string with embedded mode-switch tags.
       |
       v Step 2 — Baraha ASCII -> Devanagari Unicode
       |  Tool: src/baraha_to_devanagari.py  parse_baraha_document()
       |  Processes line by line. Inside <lang=def> sections:
       |    * Identifies consonant clusters (longest-match first)
       |    * Attaches vowel matras or halant as appropriate
       |    * Maps accent markers: q=ANUDATTA  #=UDATTA  $=DIRGHA SVARITA
       |    * (gm)=GOMUKHA  (gg)=double-g form
       |    * Handles vocalic-R: Ru -> vocalic-R by default;
       |      Rudra family -> ra+u
       |    * Passes Vedic citation refs (RV/TB/TS/TA) verbatim
       |  Inside <lang=eng> sections: text passes through unchanged.
       |  Output: Unicode Devanagari string.
       |
       v Step 3 — Devanagari -> Malayalam (same as Pipeline A Step 4-7)
       |  Tool: src/convert_devanagari_to_malayalam.py  VedicTransliterate
       |
       v Step 4 — HTML generation (parallel view)
       |  Two panels: Malayalam (default) | Devanagari (toggle button)
       |
       v Step 5 — PDF generation
          Headless browser -> A4 PDF.

OUTPUT: *_devanagari.txt, *_malayalam.txt, *_malayalam.html, *_malayalam.pdf
```

**CLI:**
```bash
python src/convert_baraha_docx.py SivaStuti_baraha_vedavms.docx \
  --output data/output/s_baraha_output
```

---

### Pipeline C — BRH / Vedavms Font-Encoded PDF (Legacy)

```
INPUT: BRH-encoded PDF (e.g. Siva_stuti_vedavams.pdf)
       |
       v Step 1 — PDF text extraction (standard)
       |  pypdf visitor_text() extracts text using the PDF's own
       |  character map (but the PDF uses Latin-1 extended chars
       |  as glyph codes, not real text).
       |
       v Step 2 — BRH glyph -> Devanagari Unicode
       |  Tool: BRHDevanagariDecoder.decode() inside
       |         src/convert_devanagari_to_malayalam.py
       |  250+ string replacement rules applied longest-first.
       |  Regex-based repha reordering applied after substitutions.
       |
       v Step 3+ — Same as Pipeline A Step 4-7

OUTPUT: *_devanagari.txt, *_malayalam.txt, *_malayalam.html, *_malayalam.pdf
```

---

## 2. Sanskrit98 Font Byte Map

The `Sanskrit98` / `HMHDPN_Sanskrit98` TrueType font encodes Devanagari using private single-byte codes (0x01-0x8B). None of these correspond to standard Unicode. The mapping was reverse-engineered by:

1. Rendering all 139 glyphs from the embedded font into a visual grid (`_glyph_grid_big.png`)
2. Identifying each glyph shape from the grid (documented in `_CHARMAP_DRAFT.md`)
3. Testing candidate mappings against known mantra text to verify correctness

The final decoder table is in `src/sanskrit98_decoder_v5.py` (`CHAR` dict).

### Type Codes

| Code | Meaning |
|------|---------|
| `C` | Full consonant (ka ha sa...) |
| `V` | Independent vowel (a i u e...) |
| `m` | Vowel matra / sign (aa-matra, i-matra, u-matra, vocalic-r-matra...) |
| `mi` | Short-i matra — **deferred** (appears BEFORE consonant in stream) |
| `Hc` | Half-consonant — starts a conjunct cluster (half-n, half-v, half-t...) |
| `NM` | Pre-built ligature / conjunct (dra, tra, ksha...) |
| `R` | Repha — appears **after** consonant in stream, moved **before** in output |
| `H` | Visarga or Halant (ends syllable) |
| `M` | Anusvara / Gomukha / Chandrabindu (nasals) |
| `A` | Vedic diacritic accent mark |
| `PRT` | Svarita accent trigger — invisible, marks current syllable |
| `SEP` | Anudatta accent trigger — invisible, marks current syllable |
| `D` | Danda or Double-danda |
| `SP` | Space |
| `OM` | Omkara |
| `!` | Context-sensitive: consonant at word-start, converts preceding nasal at word-end |

### Note Column Legend

- **EXACT** — Draft and decoder agree on the Devanagari output character
- **DESC** — Draft had human-readable description text; decoder has the actual Unicode character. Semantically identical, no discrepancy.
- **REFINED** — Decoder differs from draft. Genuine correction made during testing (see Section 3 for full explanation).

---

### Full Byte Map (0x01-0x8B)

| Byte | Latin glyph name | Draft identification | Decoder output | Type | Status |
|------|-----------------|---------------------|----------------|------|--------|
| 0x01 | period | danda | double-danda (DOUBLE DANDA) | D | REFINED |
| 0x02 | space | space | space | SP | DESC |
| 0x03 | m | ma | ma | C | EXACT |
| 0x04 | h | ha | ha | C | EXACT |
| 0x05 | a | aa-matra | aa-matra | m | DESC |
| 0x06 | N | half-na | half-na (na+halant) | Hc | DESC |
| 0x07 | y | ya | ya | C | EXACT |
| 0x08 | s | sa | sa | C | EXACT |
| 0x09 | greater | visarga | visarga | H | DESC |
| 0x0A | A | a (short vowel) | a (short vowel) | V | EXACT |
| 0x0B | w | tha | tha | C | EXACT |
| 0x0C | p | pa | pa | C | EXACT |
| 0x0D | less | anusvara | anusvara | M | DESC |
| 0x0E | c | ca | ca | C | EXACT |
| 0x0F | g | ga | ga | C | EXACT |
| 0x10 | eacute | ru ligature | ru ligature (ra+u) | NM | DESC |
| 0x11 | Ocircumflex | dra ligature | dra ligature (da+ra) | NM | DESC |
| 0x12 | bracketleft | retroflex Na | retroflex Na | C | DESC |
| 0x13 | U | long-U vowel | long-U vowel | V | EXACT |
| 0x14 | v | va | va | C | EXACT |
| 0x15 | R | Repha (ra+halant, pre-consonant) | ra+halant | R | DESC — positioned AFTER consonant in stream; prepended BEFORE in Unicode output |
| 0x16 | k | ka | ka | C | EXACT |
| 0x17 | j | ja | ja | C | EXACT |
| 0x18 | e | e-matra | e-matra | m | DESC |
| 0x19 | n | na | na | C | EXACT |
| 0x1A | i | i-matra | i-matra | mi | DESC — appears BEFORE consonant in stream; deferred as pending_i in decoder |
| 0x1B | hyphen | bha | bha | C | EXACT |
| 0x1C | semicolon | retroflex sha | retroflex sha | C | EXACT |
| 0x1D | x | dha | dha | C | EXACT |
| 0x1E | scaron | Dirgha Svarita accent | Dirgha Svarita (U+1CDA) | A | DESC |
| 0x1F | r | ra | ra | C | EXACT |
| 0x20 | V | conjunct-va | half-va (va+halant) | Hc | REFINED — draft saw full va; actually half-form |
| 0x21 | S | half-sa | half-sa (sa+halant) | Hc | DESC |
| 0x22 | slash | invisible separator | (empty string) | SEP | DESC — Anudatta accent trigger |
| 0x23 | question | invisible prot marker | (empty string) | PRT | DESC — Svarita accent trigger |
| 0x24 | t | ta | ta | C | EXACT |
| 0x25 | percent | short-u vowel | short-u vowel | V | EXACT |
| 0x26 | numbersign | short-i vowel | short-i vowel | V | EXACT |
| 0x27 | comma | single danda | single danda | D | DESC |
| 0x28 | u | u-matra | u-matra | m | DESC |
| 0x29 | b | ba | ba | C | EXACT |
| 0x2A | divide | u-matra | ha+u ligature (hu) | NM | REFINED — glyph is a pre-built ha+u ligature, not plain u-matra |
| 0x2B | underscore | half-bha | half-bha (bha+halant) | Hc | DESC |
| 0x2C | z | sha (palatal) | sha (palatal) | C | EXACT |
| 0x2D | exclam | bha (context-sensitive) | bha | ! | DESC — at word-start = bha; after ma = converts ma to anusvara |
| 0x2E | ampersand | vocalic-r matra | vocalic-r matra (U+0943) | m | DESC |
| 0x2F | f | retroflex Da | retroflex Da | C | EXACT |
| 0x30 | o | kha | kha | C | EXACT |
| 0x31 | quotedbl | gha | gha | C | EXACT |
| 0x32 | l | la | la | C | EXACT |
| 0x33 | grave | Omkara | Omkara | OM | EXACT |
| 0x34 | E | ai-matra | ai-matra | m | DESC |
| 0x35 | T | half-ta | half-ta (ta+halant) | Hc | DESC |
| 0x36 | Z | half-sha | half-sha (sha+halant) | Hc | DESC |
| 0x37 | I | long-ii-matra (ki etc.) | long-ii-matra | m | DESC |
| 0x38 | daggerdbl | Gomukha | Gomukha (U+A8F3) | M | DESC |
| 0x39 | D | cha (aspirated ca) | cha | C | EXACT |
| 0x3A | H | jha (aspirated ja) | jha | C | EXACT |
| 0x3B | bar | (ambiguous — bar glyph) | palatal-na (nya) | C | REFINED — draft said bar; confirmed as nya from context |
| 0x3C | d | da | da | C | EXACT |
| 0x3D | bracketright | ksha ligature | ksha ligature | NM | EXACT |
| 0x3E | bracketright | long-U vowel (alternate) | long-U vowel | V | EXACT |
| 0x3F | X | half-dha | half-dha (dha+halant) | Hc | DESC |
| 0x40 | onequarter | nga+ga ligature | nga+ga ligature | NM | EXACT |
| 0x41 | braceleft | half-Na (retroflex) | half-Na (Na+halant) | Hc | DESC |
| 0x42 | J | half-ja | half-ja (ja+halant) | Hc | DESC |
| 0x43 | at | long-e vowel | long-e vowel | V | EXACT |
| 0x44 | G | half-ga | half-ga (ga+halant) | Hc | DESC |
| 0x45 | Ccedilla | tra ligature | tra ligature | NM | EXACT |
| 0x46 | q | retroflex Ta | retroflex Ta | C | EXACT |
| 0x47 | Q | retroflex Tha | retroflex Tha | C | EXACT |
| 0x48 | F | retroflex Dha | retroflex Dha | C | EXACT |
| 0x49 | iacute | shca ligature | shca ligature | NM | EXACT |
| 0x4A | paragraph | gna ligature | gna ligature | NM | EXACT |
| 0x4B | P | half-pa | half-pa (pa+halant) | Hc | DESC |
| 0x4C | ntilde | shva ligature | shva ligature | NM | EXACT |
| 0x4D | equal | avagraha | avagraha | V | EXACT |
| 0x4E | Adieresis | tta ligature | tta ligature | NM | EXACT |
| 0x4F | agrave | pra ligature | pra ligature | NM | EXACT |
| 0x50 | cent | gra ligature | gra ligature | NM | EXACT |
| 0x51 | Uacute | nna ligature | nna ligature | NM | EXACT |
| 0x52 | colon | half-sha (retroflex) | half-sha (sha+halant) | Hc | DESC |
| 0x53 | parenright | pha | pha | C | EXACT |
| 0x54 | M | half-ma | half-ma (ma+halant) | Hc | DESC |
| 0x55 | plus | (ra-phala subscript) | virama+ra (ra-phala) | m | REFINED — draft said vocalic-r; actually subscript ra-phala fixing damshhtrankuram, taamradharam etc. |
| 0x56 | asterisk | dya ligature | dya ligature | NM | EXACT |
| 0x57 | Idieresis | ddha ligature | ddha ligature | NM | EXACT |
| 0x58 | ecircumflex | ruu ligature | ruu ligature | NM | EXACT |
| 0x59 | Ntilde | dbha ligature | dbha ligature | NM | EXACT |
| 0x5A | minus | kta ligature | kta ligature | NM | EXACT |
| 0x5B | adieresis | bra ligature | bra ligature | NM | EXACT |
| 0x5C | udieresis | hma ligature | hma ligature | NM | EXACT |
| 0x5D | backslash | vocalic-R vowel | vocalic-R (U+090B) | V | DESC |
| 0x5E | idieresis | shra ligature | shra ligature | NM | EXACT |
| 0x5F | ae | bhra ligature | bhra ligature | NM | EXACT |
| 0x60 | K | half-ka | half-ka (ka+halant) | Hc | DESC |
| 0x61 | dollar | long-ii vowel | long-ii vowel | V | EXACT |
| 0x62 | uacute | half-ksha | half-ksha (ksha+halant) | Hc | DESC |
| 0x63 | odieresis | stra ligature | stra ligature | NM | EXACT |
| 0x64 | dagger | dru ligature | dru ligature | NM | EXACT |
| 0x65 | parenleft | half-ya | half-ya (ya+halant) | Hc | DESC |
| 0x66 | B | half-ba | half-ba (ba+halant) | Hc | DESC |
| 0x67 | Egrave | half-tra | half-tra (tra+halant) | Hc | DESC |
| 0x68 | ograve | shTa ligature | shTa ligature | NM | EXACT |
| 0x69 | W | half-tha | half-tha (tha+halant) | Hc | DESC |
| 0x6A | L | half-la | half-la (la+halant) | Hc | DESC |
| 0x6B | ellipsis | u-matra (alternate) | u-matra | m | DESC |
| 0x6C | Ecircumflex | du ligature | du ligature | NM | EXACT |
| 0x6D | oe | halant (virama) | halant (U+094D) | H | DESC |
| 0x6E | ugrave | hru ligature | hru ligature | NM | EXACT |
| 0x6F | guillemotleft | vocalic-r matra | vocalic-r matra (U+0943) | m | DESC |
| 0x70 | Atilde | nyaja ligature | nyaja ligature | NM | EXACT |
| 0x71 | yacute | hya ligature | hya ligature | NM | EXACT |
| 0x72 | Acircumflex | nyaca ligature | nyaca ligature | NM | EXACT |
| 0x73 | AE | tna ligature | tna ligature | NM | EXACT |
| 0x74 | ydieresis | hra ligature | hra ligature | NM | EXACT |
| 0x75 | braceright | jnya ligature | jnya ligature | NM | EXACT |
| 0x76 | threesuperior | kra ligature | kra ligature | NM | EXACT |
| 0x77 | Odieresis | dva ligature | dva ligature | NM | EXACT |
| 0x78 | ucircumflex | hna ligature | hna ligature | NM | EXACT |
| 0x79 | C | half-ca | half-ca (ca+halant) | Hc | DESC |
| 0x7A | egrave | mra ligature | mra ligature | NM | EXACT |
| 0x7B | thorn | hva ligature | hva ligature | NM | EXACT |
| 0x7C | Y | half-ya (alternate) | half-ya (ya+halant) | Hc | DESC |
| 0x7D | exclamdown | chandrabindu | chandrabindu (U+0901) | M | DESC |
| 0x7E | Icircumflex | dda ligature | dda ligature | NM | EXACT |
| 0x7F | quotesinglbase | u-matra (alternate 2) | u-matra | m | DESC |
| 0x80 | florin | long-uu-matra | long-uu-matra | m | DESC |
| 0x81 | onehalf | cca ligature | cca ligature | NM | EXACT |
| 0x82 | Edieresis | duu ligature | duu ligature | NM | EXACT |
| 0x83 | quotesingle | nga (velar nasal) | nga | C | EXACT |
| 0x84 | Yacute | pta ligature | pta ligature | NM | EXACT |
| 0x85 | multiply | dhna ligature | dhna ligature | NM | EXACT |
| 0x86 | threequarters | jja ligature | jja ligature | NM | EXACT |
| 0x87 | oslash | huu ligature | huu ligature | NM | EXACT |
| 0x88 | questiondown | jra ligature | jra ligature | NM | EXACT |
| 0x89 | oacute | shTha ligature | shTha ligature | NM | EXACT |
| 0x8A | cedilla | half-gha | half-gha (gha+halant) | Hc | DESC |
| 0x8B | Ugrave | ntra ligature | ntra ligature | NM | EXACT |

**Summary: 139 bytes mapped. 58 EXACT, 78 DESC (description-only difference, semantically identical), 3 REFINED (genuine corrections made during testing).**

---

## 3. Glyph Identification Notes — Where Draft Differs from Decoder

The `_CHARMAP_DRAFT.md` was the visual research notebook. All 139 glyphs were identified from the rendered glyph grid. The decoder has the same 139 entries — no bytes are missing from either side. The "DIFF" flags in the comparison are mostly because the draft used human-readable English descriptions while the decoder stores the actual Unicode character.

Three entries represent genuine corrections discovered during testing:

### 0x01 — Single danda corrected to Double danda
- Draft said: single danda (U+0964)
- Decoder has: double danda (U+0965)
- Reason: Byte 0x01 appears exclusively at chapter and section breaks in Mahanyasam, never as a mid-verse pause. Every occurrence corresponds to a double danda. Single dandas are encoded at 0x27.

### 0x2A — u-matra corrected to hu ligature
- Draft said: u-matra (vowel sign for short-u)
- Decoder has: hu ligature (ha+u pre-built, type NM)
- Reason: A matra can only follow a consonant, but 0x2A appeared at syllable-initial positions. Testing showed byte sequence 0x04+0x2A decoded as a single hu unit (e.g. in huvema, huta), confirming it is a pre-built ha+u ligature, not a standalone matra.

### 0x55 — Vocalic-r matra corrected to ra-phala subscript
- Draft said: vocalic-r matra (U+0943, the combining sign for syllabic-r)
- Decoder has: virama+ra (ra-phala subscript, type m)
- Reason: Context disambiguation. The byte appeared after consonants that already had a vowel, making a second vowel sign structurally impossible. Decoding as subscript ra-phala correctly produced: damshtrankuram, taamradharam, kaalabhra, vajrahastaya. Note that 0x2E is the correct vocalic-r matra entry.

---

## 4. Baraha Encoding Reference

The Baraha software encodes Sanskrit in phonetic Latin ASCII. The following tables document the conventions used in this corpus.

### Accent Markers

| Baraha | Vedic accent | Unicode codepoint | Vedic name |
|--------|-------------|-------------------|-----------|
| q | Anudatta bar | U+0952 | Anudatta |
| # | Udatta stroke | U+0951 | Udatta / Svarita |
| $ | Double Svarita | U+1CDA | Dirgha Svarita |
| (gm) | Gomukha symbol | U+A8F3 | Vedic Sign Candrabindu Two |
| (gg) | Doubled gomukha | ga+halant+ga+halant | Alternate nasalization form |
| ~M | Chandrabindu | U+0901 | Anunasika |
| M | Anusvara | U+0902 | Anusvara |
| H | Visarga | U+0903 | Visarga |
| & | Avagraha | U+093D | Avagraha |

### Consonants

| Baraha | Devanagari | Notes |
|--------|-----------|-------|
| k K g G | ka kha ga gha | ka-varga |
| c C j J | ca cha ja jha | ca-varga |
| T Th D Dh N | Ta Tha Da Dha Na | retroflex ta-varga |
| t th d dh n | ta tha da dha na | dental ta-varga |
| p P b B m | pa pha ba bha ma | pa-varga |
| y r l v (or w) | ya ra la va | semi-vowels |
| ~g ~j | nga nya | varga nasals |
| s | sa | dental sibilant |
| S | sha (palatal) | only when NOT followed by h |
| Sh | sha (retroflex) | S+h as a 2-character unit |
| h | ha | |
| L | retroflex La | |

### Vowels

| Baraha | Independent vowel | Matra form | Notes |
|--------|------------------|-----------|-------|
| a | short-a | (inherent, no matra) | |
| A | long-aa | aa-matra | |
| i | short-i | i-matra | |
| I | long-ii | ii-matra | |
| u | short-u | u-matra | |
| U | long-uu | uu-matra | |
| Ru | vocalic-R (default) | vocalic-r-matra | Word-initial default; see Rudra exception below |
| e or E | long-e | e-matra | Both treated as long-e per corpus convention |
| o or O | long-o | o-matra | Both treated as long-o per corpus convention |
| ai | diphthong-ai | ai-matra | 2-char, matched before single-char vowels |
| au | diphthong-au | au-matra | 2-char, matched before single-char vowels |

### Vocalic-R Exception (Rudra Family)

Word-initial Ru defaults to vocalic-R. The following prefixes are exceptions where Ru means normal ra+u:

- rudra -> ra+u+dra (Rudra — capitalized for emphasis in the corpus)
- rudraikA -> ra+u+draikA

All other word-initial Ru tokens (Ruddhi, Ruca, RugVeda, RuShi, Rutvik, etc.) decode as vocalic-R.

### Dandas

| Baraha | Output |
|--------|--------|
| \| | single danda |
| \|\| | double danda |

---

## 5. Decoder Internals — Algorithm Detail

### Sanskrit98 decode_bytes() — Syllable Assembly

The decoder works in two passes.

#### Pass 1 — Syllable building

Each byte is classified by its type code and handled as follows:

```
Hc (half-consonant):
  If current syllable has content AND not already in conjunct:
    flush current syllable to list, start new
  Append half-form to current syllable
  Set in_conjunct = True

C (full consonant):
  If NOT in conjunct and current syllable has content: flush
  If pending_i exists: append consonant + i-matra together
  Else: append consonant
  Set in_conjunct = False

NM (pre-built ligature):
  Always flush current syllable first
  If pending_i: append ligature + i-matra
  Else: append ligature
  Set in_conjunct = False

mi (short-i matra, 0x1A):
  Set pending_i = i-matra  (DEFERRED — byte appears before its consonant)
  Do not flush

R (Repha, 0x15):
  Insert ra+halant at the START of current syllable's parts list
  (Font stream has Repha AFTER the consonant; Unicode needs it BEFORE)

V (independent vowel):
  If pending_i: append vowel + i-matra
  Elif current syllable has content and not in conjunct:
    Convert to matra form (vowel sign after consonant)
  Else: check if next byte is the matching matra -> emit long vowel, skip matra
  Set in_conjunct = False

m (matra):
  Attach to current syllable's last part
  Special: ra+halant + u-matra -> ru ligature
  Special: short-a + aa-matra -> long-aa
  Special: short-a + e-matra -> long-e
  Special: long-aa + e-matra -> long-o
  Special: long-aa + ai-matra -> au diphthong
  Set in_conjunct = False

PRT (0x23, svarita trigger):
  Mark current syllable (or last syllable if current empty) svarita = True

SEP (0x22, anudatta trigger):
  Mark current syllable (or last syllable) anudatta = True

H (visarga or halant):
  Append to current syllable, then flush

SP / D / M / A:
  Flush current syllable
  Emit the character as its own standalone syllable unit
```

#### Pass 2 — Accent insertion

For each completed syllable:
- If svarita=True: append Udatta mark (U+0951) — inserted before visarga if syllable ends in visarga
- If anudatta=True: append Anudatta mark (U+0952) — inserted before visarga if syllable ends in visarga

#### Post-processing — clean_repetitions()

The Sanskrit98 font renderer sometimes outputs text twice as a rendering artifact. Four cleaning steps are applied:

1. Regex dedup of double-danda...double-danda phrase repetitions
2. Named label dedup: puurvaanga puurvaanga -> puurvaanga (and similar direction labels)
3. Token-level word halving: any word where the second half equals the first half (ignoring accents) is collapsed
4. Trailing label after final danda cleanup: label appended after double-danda that is already present in the body is stripped

---

### Baraha parse_baraha_document() — Phonetic Assembly

Processes a full document text with embedded lang-mode tags:

```
For each line:
  Find all <lang=eng> and <lang=def> tag positions
  Split into segments: each segment has (mode=eng|def, text)
  For each segment:
    If mode = def (Baraha Sanskrit):
      Split on whitespace, dandas
      For each token: call parse_baraha_token()
    If mode = eng:
      Pass through verbatim

parse_baraha_token(token):
  1. Check word-initial Ru override (Rudra prefix -> ra+u not vocalic-R)
  2. Check for (gm) bracketed gomukha -> Gomukha symbol
  3. Check for (gg) bracketed gomukha -> doubled-ga form
  4. Check single-char markers: q # $ M H ~M & . -
  5. Match consonant (longest-match first: Sh Th Dh th dh ~g ~j, then single chars)
     Peek for following vowel:
       If vowel follows -> emit consonant + matra (empty string for inherent-a)
       If no vowel -> emit consonant + halant (ardhakshara / conjunct onset)
     Attach trailing accent / anusvara / visarga immediately after syllable
  6. Match independent vowel (if no consonant preceded in this unit)
  7. Fallthrough: emit character verbatim (digits, stray ASCII, citation refs)
```

Citation references like (RV.5.25.5) or (TB 1.2.1.26) are detected by pattern and passed through verbatim without syllabification.

---

## 6. Transliteration and Document Generation

### VedicTransliterate.devanagari_to_malayalam()

**Step 1 — Nasal mode preprocessing** (if --nasal flag is not symbol):
- gg mode: Gomukha -> ga+halant+ga+halant
- gm mode: Gomukha -> ga+halant+ma+halant
- latin_gm mode: Gomukha -> literal "gm"
- Default symbol: preserve Gomukha as-is (U+A8F3)

**Step 2 — Danda protection:** double-danda and single danda are replaced with private-use placeholders before transliteration (aksharamukha does not handle dandas correctly).

**Step 3 — Per-token transliteration:** Text is split on Devanagari / Vedic Unicode ranges. Each Devanagari segment is passed to `aksharamukha.transliterate.process('Devanagari', 'Malayalam', token)`. Non-Devanagari tokens pass verbatim.

**Step 4 — Danda restoration:** placeholders restored to double-danda / single danda.

**Step 5 — clean_accent_spaces():**
- Removes space artifacts between Indic chars and accent marks (BRH font offset artifact)
- Calls reorder_accents_before_ardhakshara(): moves accent marks that landed after a halant consonant to before it. (Vedic accents attach to vowel-bearing syllables, never to halant-only consonants.)
- Calls normalize_combining_marks():
  - Drops spurious virama before matras (prevents dotted-circle rendering)
  - Drops single space between a char and an orphaned combining mark
  - NFC-normalizes to recompose decomposed matra pairs (aa-matra + e-matra -> o-matra)

**Step 6 — Word-final halant-ma to anusvara:** Malayalam uses anusvara (ring) at word end rather than halant-ma. Converted by regex.

**Step 7 — Malayalam cleanup:** Small table of known aksharamukha output mismatches for specific words corrected by string replacement.

---

### Anudatta Lowering in HTML

Malayalam glyphs have deep bottom descenders (e.g. ka+u, virama+ra). The Devanagari combining Anudatta (U+0952) collides visually with these descenders when placed inline. The HTML renderer applies a lowering trick:

```css
.anudatta-bar {
    display: inline-block;
    width: 0;
    overflow: visible;
    position: relative;
    left: -0.35em;
    vertical-align: -0.52em;
    font-weight: 700;
    white-space: nowrap;
}
```

Each Anudatta mark in the Malayalam output is wrapped:
```html
<span class="anudatta-bar">॒</span>
```

**Important:** This wrapping is applied ONLY in the Malayalam panel. In the Devanagari panel, U+0952 is left as a native combining mark — wrapping it in an inline-block breaks the combining behavior and causes visual drift onto adjacent consonants.

---

### PDF Generation

The script searches for a headless browser in this order:
1. MS Edge (x86 Program Files)
2. MS Edge (64-bit Program Files)
3. Google Chrome (64-bit)
4. Google Chrome (x86)

Command used:
```
msedge.exe --headless --disable-gpu --no-pdf-header-footer
           --print-to-pdf=<output.pdf> <file:///path/to/input.html>
```

Timeout is 120 seconds. If no browser is found, the script prints a warning and skips PDF generation (HTML output is still saved).
