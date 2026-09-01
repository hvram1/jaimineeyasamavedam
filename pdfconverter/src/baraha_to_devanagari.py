"""
Baraha → Devanagari Vedic Parser

Translates Baraha-encoded Sanskrit text (phonetic Latin script produced by Baraha
software, with Vedic accent annotations) into Unicode Devanagari, preserving:
  - Vedic accents: q=anudatta(॒), #=svarita(॑), $=dirgha svarita(᳚)
  - Vedic nasal symbols: (gm)=gomukha/candrabindu-two(ꣳ), (gg)=ग्ग् doubled form,
    ~M=candrabindu(ँ), M=anusvara(ं)
  - Visarga (H=ः), avagraha (&=ऽ)
  - Virala hint "." — kept as a literal period (pronunciation marker, not virama)
  - Compound hyphen "-" — kept as literal hyphen
  - Dandas: | = ।, || = ॥

Vowel conventions per the s.docx header:
  e/E = long E (ए/े); the author uses capital E uniformly for Sanskrit.
  o/O = long O (ओ/ो); the author uses capital O uniformly for Sanskrit.

Vocalic R rule (the sequence `Ru`):
  - Mid-word (after a consonant in the same unit): `Ru` → ृ matra. Unambiguous
    (e.g., `kRuShNa` → कृष्ण, `pRuthiqvI` → पृथिवी, `mRutasya` → मृतस्य).
  - Word-initial: `Ru` is ambiguous. The DEFAULT is vocalic R (ऋ): most genuine
    word-initial `Ru` tokens in this corpus are vocalic-R words
    (`Ruddhi`=ऋद्धि, `Rucaq`=ऋच॒, `RugvEda`=ऋग्वेद, `RuShi`=ऋषि, `Rutvik`=ऋत्विक्).
    A small whitelist of word-initial `Ru` tokens instead represent normal r+u
    (रु) — chiefly Rudra-family words capitalized for emphasis — and is listed in
    `_WORD_INITIAL_RU_AS_RU` below as prefix patterns.

Sibilant convention per the s.docx header:
  s   = स (dental sibilant)
  S   = श (palatal sibilant) — when NOT followed by 'h'
  Sh  = ष (retroflex sibilant) — 'S' followed by 'h' as a 2-char unit
  (e.g., kSh = क्ष because k gets halant and Sh is ष)

Nasal conventions:
  ~g  = ङ (nasal of ka varga)
  ~j  = ञ (nasal of cha varga)
  M   = ं (anusvara)
  ~M  = ँ (candrabindu / anunasika)

Aspirates (this doc uses lowercase 'th'/'dh' for dentals, capital 'Th'/'Dh' for
retroflexes; ka/cha/ta/pa-varga aspirates use single capital letters K/G/C/J/P/B):
  th  = थ,     dh = ध
  Th  = ठ,     Dh = ढ
  Sh  = ष      (special — see sibilant note above)
  K   = ख, G = घ, C = छ, J = झ, P = फ, B = भ   (single capitals)

The parser is phonetic: each consonant letter → Devanagari consonant + halant (्)
when followed by another consonant or word-end, OR + matra when followed by a
vowel. Accent markers attach post-hoc to the previously-emitted syllable.
"""

import re
import unicodedata

# Ensure UTF-8 stdout on Windows
import sys
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass


# --- Consonant inventory (longest-first for unambiguous matching) -------------

# Multi-char consonant units. Sorted by length desc so 'Sh' wins over plain 'S'.
_MULTI_CONS = [
    ('Sh', '\u0937'),   # ष  (retroflex sibilant)
    ('Th', '\u0920'),   # ठ  (retroflex aspirated)
    ('Dh', '\u0922'),   # ढ  (retroflex aspirated voiced)
    ('th', '\u0925'),   # थ  (dental aspirated)
    ('dh', '\u0927'),   # ध  (dental aspirated voiced)
    ('~g', '\u0919'),   # ङ  (nasal of ka varga)
    ('~j', '\u091E'),   # ञ  (nasal of cha varga)
]

# Single-char consonants. Note: 'S' alone = श (palatal), since 'Sh' is matched first.
_SINGLE_CONS = {
    'k': '\u0915',  # क
    'K': '\u0916',  # ख
    'g': '\u0917',  # ग
    'G': '\u0918',  # घ
    'c': '\u091A',  # च
    'C': '\u091B',  # छ
    'j': '\u091C',  # ज
    'J': '\u091D',  # झ
    'T': '\u091F',  # ट
    'D': '\u0921',  # ड
    'N': '\u0923',  # ण
    't': '\u0924',  # त
    'd': '\u0926',  # द
    'n': '\u0928',  # न
    'p': '\u092A',  # प
    'P': '\u092B',  # फ
    'b': '\u092C',  # ब
    'B': '\u092D',  # भ
    'm': '\u092E',  # म
    'y': '\u092F',  # य
    'r': '\u0930',  # र
    'l': '\u0932',  # ल
    'L': '\u0933',  # ळ  (retroflex l — not the rare ऌ)
    'v': '\u0935',  # व
    'V': '\u0935',  # व  (capitalized form, e.g., "VaikuNTha")
    'w': '\u0935',  # व  (alternative)
    'S': '\u0936',  # श  (palatal sibilant — only reached when 'Sh' didn't match)
    's': '\u0938',  # स  (dental sibilant)
    'h': '\u0939',  # ह
}

# All consonant keys we recognize (for lookahead checks).
_CONS_KEYS = sorted(list(_SINGLE_CONS.keys()) + [k for k, _ in _MULTI_CONS],
                    key=len, reverse=True)


# --- Vowel inventory ----------------------------------------------------------

# Independent vowels at word start (no preceding consonant in current unit).
# 2-char diphthongs (ai/au) MUST be matched before single-char vowels; _peek_vowel
# checks the 2-char forms first.
_INDEP_VOWEL = {
    'a':  '\u0905',  # अ
    'A':  '\u0906',  # आ
    'i':  '\u0907',  # इ
    'I':  '\u0908',  # ई
    'u':  '\u0909',  # उ
    'U':  '\u090A',  # ऊ
    'e':  '\u090F',  # ए  (lowercase e rare, per author note; treat as long)
    'E':  '\u090F',  # ए
    'o':  '\u0913',  # ओ
    'O':  '\u0913',  # ओ
    'ai': '\u0910',  # ऐ
    'au': '\u0914',  # औ
}
_INDEP_VOWEL_2CHAR = ('ai', 'au')   # checked first by _peek_vowel

# Matra (vowel-sign) forms, applied to a previously emitted consonant.
_MATRA = {
    'a':  '',          # inherent vowel — no matra needed
    'A':  '\u093E',    # ा
    'i':  '\u093F',    # ि
    'I':  '\u0940',    # ी
    'u':  '\u0941',    # ु
    'U':  '\u0942',    # ू
    'e':  '\u0947',    # े
    'E':  '\u0947',    # े
    'o':  '\u094B',    # ो
    'O':  '\u094B',    # ो
    'ai': '\u0948',    # ै
    'au': '\u094C',    # ौ
}
_MATRA_2CHAR = ('ai', 'au')   # checked first by _peek_vowel

_VOWEL_KEYS = list(_INDEP_VOWEL.keys())


# Word-initial `Ru` overrides: tokens whose initial `Ru` is normal r+u (रु), NOT
# vocalic R (ऋ). Listed as lowercase prefixes; matched case-insensitively against
# the current token's first chars. The default for unlisted word-initial `Ru` is
# vocalic R (ऋ) — see the "Vocalic R rule" note in the module docstring.
#
# Catalog evidence (s.docx): the only word-initial Ru tokens that decode as रु are
# the Rudra family and a couple of RNa-family words. Everything else (Ruddhi, Ruca,
# Rug/Ṛg, RuShi, Rutvik, Ruqta, Ruta, Rutau, RuqtiM, RuShicCandO, etc.) is ऋ.
_WORD_INITIAL_RU_AS_RU_PREFIXES = (
    'rudra',     # रुद्र    (e.g., RudrAya = रुद्राय) — Rudra capitalized for emphasis
    'rudraikA',  # रुद्रैका (e.g., rudraikAdaSini)
)


def _word_initial_ru_is_normal_ru(token: str) -> bool:
    """True if a word-initial `Ru` should decode as normal r+u (रु) rather than vocalic R (ऋ)."""
    head = token[:8].lower()
    return head.startswith(_WORD_INITIAL_RU_AS_RU_PREFIXES)

VIRAMA  = '\u094D'  # ्
ANUSVARA  = '\u0902'  # ं
VISARGA  = '\u0903'  # ः
AVAGRAHA = '\u093D'  # ऽ
CANDRABINDU = '\u0901'  # ँ
VOCALIC_R_INDEP = '\u090B'  # ऋ
VOCALIC_R_MATRA = '\u0943'  # ृ
GOMUKHA  = '\uA8F3'  # ꣳ  (Vedic Sign Candrabindu Two)
UDATTA   = '\u0951'  # ॑
ANUDATTA = '\u0952'  # ॒
DIRGHA_SVARITA = '\u1CDA'  # ᳚  (Vedic Tone Double Svarita)

DANDA        = '\u0964'  # ।
DOUBLE_DANDA = '\u0965'  # ॥


def _match_consonant(token, i):
    """Try to match a consonant at token position i. Returns (char, new_i) or None."""
    # multi-char first (longest-first)
    for k, v in _MULTI_CONS:
        if token.startswith(k, i):
            return v, i + len(k)
    # single-char
    ch = token[i]
    if ch in _SINGLE_CONS:
        return _SINGLE_CONS[ch], i + 1
    return None


def _peek_vowel(token, i):
    """
    Returns (matra_or_indep_char, is_independent, new_i, is_vocalic_R) if a vowel
    starts at position i, or None.
    Vocalic R is special: 'Ru' (R followed by u) forms a single vowel unit.
      - If preceded by a consonant in the current syllable: returns matra ृ, consumes 'Ru'.
      - If at word start (no consonant yet): returns independent ऋ, consumes 'Ru'.
    """
    n = len(token)
    if i >= n:
        return None
    # Vocalic R: 'R' followed by 'u' (or 'U' for long form, though it's not used here)
    if token[i] == 'R' and i + 1 < n and token[i + 1] in ('u', 'U'):
        is_long = token[i + 1] == 'U'
        matra = '\u0944' if is_long else VOCALIC_R_MATRA   # ॄ for long, ृ for short
        indep = '\u0960' if is_long else VOCALIC_R_INDEP  # ॠ for long, ऋ for short
        return (matra, indep, i + 2, True)
    # 2-char diphthongs (ai/au) — checked before single-char vowels so 'a' doesn't
    # steal the 'a' from 'ai'/'au' as inherent-a and leave 'i'/'u' dangling.
    for k in _INDEP_VOWEL_2CHAR:
        if token.startswith(k, i):
            return (_MATRA[k], _INDEP_VOWEL[k], i + len(k), False)
    # Ordinary vowels
    ch = token[i]
    if ch in _VOWEL_KEYS:
        return (_MATRA[ch], _INDEP_VOWEL[ch], i + 1, False)
    return None


def _syllabify_token(token):
    """
    Convert one Baraha word (whitespace-free token-with-no-tag) to Unicode Devanagari.
    The token may contain q/#/$ accents, M/H/~M end marks, & avagraha, (gm)/(gg)
    bracketed gomukha markers, '.' virala hints, '-' compound hyphens, and any
    other ASCII punctuation. Non-Baraha chars (digits, stray Latin etc.) are
    passed through verbatim.
    """
    out = []
    i = 0
    n = len(token)
    while i < n:
        ch = token[i]

        # --- Word-initial Ru override (रु not ऋ) -----------------------------------------
        # When this segment begins with `Ru` AND the token is in the override list,
        # decode the initial `Ru` as normal r+u (रु) — emit it as a normal
        # consonant (र) + short-u matra (ु) and continue from position 2.
        # Everything afterwards is handled by the regular path.
        if i == 0 and token.startswith('Ru') and _word_initial_ru_is_normal_ru(token):
            out.append('\u0930' + '\u0941')   # र + ु = रु
            i = 2
            # Trailing accent / anusvara / visarga attaches to this r+u syllable.
            if i < n and token[i] in ('q', '#', '$'):
                out.append({ 'q': ANUDATTA, '#': UDATTA, '$': DIRGHA_SVARITA }[token[i]]); i += 1
            if i < n and token[i] in ('M', 'H'):
                out.append(ANUSVARA if token[i] == 'M' else VISARGA); i += 1
            continue

        # --- Bracketed special forms -------------------------------------------------
        if token.startswith('(gm)', i):
            out.append(GOMUKHA)
            i += 4
            # An immediately-following accent (# or $) attaches to the gomukha itself.
            if i < n and token[i] in ('#', '$'):
                out.append(UDATTA if token[i] == '#' else DIRGHA_SVARITA)
                i += 1
            continue
        if token.startswith('(gg)', i):
            # Doubled gomukha / nRuShTi form: emit ग्ग् (g + halant + g + halant).
            out.append('\u0917' + VIRAMA + '\u0917' + VIRAMA)
            i += 4
            if i < n and token[i] in ('#', '$'):
                out.append(UDATTA if token[i] == '#' else DIRGHA_SVARITA)
                i += 1
            continue

        # --- Single-char accents / marks / punctuation -------------------------------
        if ch == 'q':
            out.append(ANUDATTA);        i += 1; continue
        if ch == '#':
            out.append(UDATTA);          i += 1; continue
        if ch == '$':
            out.append(DIRGHA_SVARITA);  i += 1; continue
        if ch == 'M':
            out.append(ANUSVARA);        i += 1; continue
        if ch == 'H':
            out.append(VISARGA);         i += 1; continue
        if ch == '~' and token.startswith('~M', i):
            out.append(CANDRABINDU);     i += 2; continue
        if ch == '&':
            out.append(AVAGRAHA);        i += 1; continue
        if ch == '.':
            out.append('.');             i += 1; continue   # virala hint — kept literal
        if ch == '-':
            out.append('-');             i += 1; continue   # compound hyphen — kept literal

        # --- Consonant + optional vowel ---------------------------------------------
        cons = _match_consonant(token, i)
        if cons is not None:
            cons_char, next_i = cons
            # Peek next: vowel? accent (q)? end-of-token?
            vowel = _peek_vowel(token, next_i)
            if vowel is not None:
                _matra, _indep, vi, _is_R = vowel
                out.append(cons_char + _matra)   # matra may be '' for inherent a
                i = vi
                # Immediately trailing accent attaches to this syllable.
                if i < n and token[i] in ('q', '#', '$'):
                    out.append({ 'q': ANUDATTA, '#': UDATTA, '$': DIRGHA_SVARITA }[token[i]])
                    i += 1
                # Immediately trailing anusvara / visarga / candrabindu / avagraha too.
                if i < n and token[i] in ('M', 'H'):
                    out.append(ANUSVARA if token[i] == 'M' else VISARGA)
                    i += 1
                elif i < n and token[i] == '~' and token.startswith('~M', i):
                    out.append(CANDRABINDU); i += 2
                continue
            # No vowel follows → consonant with halant (ardhakshara / conjunct).
            out.append(cons_char + VIRAMA)
            i = next_i
            # Accent right after a halant-only consonant? Vedic accent cannot fall on a
            # halant syllable, so reorder it: move accent BEFORE the ardhakshara so it
            # attaches to the previous vowel-bearing syllable.
            if i < n and token[i] in ('q', '#', '$'):
                mark = { 'q': ANUDATTA, '#': UDATTA, '$': DIRGHA_SVARITA }[token[i]]
                # Insert mark before the consonant+halant we just emitted.
                out.insert(len(out) - 2 + 1, mark)  # before cons_char+halant
                # Simpler: pop the last two (cons+virama), push mark, push cons+virama
                last = out.pop()              # virama
                prev = out.pop()              # cons_char
                out.append(mark)
                out.append(prev + last)
                i += 1
            continue

        # --- Independent vowel at syllable start ------------------------------------
        # (reached only when we are at the very start of the token — a lone vowel with
        #  no consonant before it in this unit)
        vowel = _peek_vowel(token, i)
        if vowel is not None and (not out or out[-1].endswith(VIRAMA) is False):
            # Word-initial independent vowel. Note: 'a'/etc. attach to previous syllable
            # only if the previous emitted char has an inherent-a; but in Baraha phonetic
            # spelling a vowel letter at the start of a token always means an independent
            # vowel — Baraha never reuses a final matra of the previous token.
            _matra, _indep, vi, _is_R = vowel
            out.append(_indep)
            i = vi
            # Trailing accent attaches to this independent vowel.
            if i < n and token[i] in ('q', '#', '$'):
                out.append({ 'q': ANUDATTA, '#': UDATTA, '$': DIRGHA_SVARITA }[token[i]])
                i += 1
            if i < n and token[i] in ('M', 'H'):
                out.append(ANUSVARA if token[i] == 'M' else VISARGA)
                i += 1
            continue

        # --- Fallback: passthrough (digits, punctuation, stray ASCII) ----------------
        out.append(ch)
        i += 1

    return ''.join(out)


def _split_unit_aware(token):
    """
    Baraha tokens occasionally contain '-' (compound hyphen) which segments
    boundaries. We keep these but still treat each segment as its own syllabify
    pass (so the vowel at start of a segment is independent). Similarly for the
    virala '.' — it pauses the consonant chain.

    Returns list of (run_type, text) where run_type is 'baraha' or 'literal'.
    The 'baraha' sub-runs are syllabified independently; 'literal' segments
    (hyphens, dots) are kept verbatim between them.
    """
    # The hyphen and dot are literal passthroughs in syllabify_token already,
    # but to reset the "word-start" state for independent vowels we explicitly
    # split on these markers so each segment is independently syllabified.
    # Single char splitters that always reset the syllable context.
    parts = re.split(r'(-|\.)', token)
    return parts


# Patterns indicating a parenthesized (or free-standing) Vedic citation reference
# embedded inside <lang=def> runs. These are English (RV/TB/TS/TA abbreviations)
# and should be passed through verbatim rather than syllabified as Baraha Sanskrit.
_CITATION_PATTERN = re.compile(
    r'^[\(]?'                         # optional opening paren
    r'(?:RV|TB|TS|TA|T\.[ABS]|Rig)'   # citation source prefix
    r'[\s\.]'                          # separator (. or space)
    r'[\d\.\s\w]+'                     # numbers/dots/spaces
    r'\)?$'                            # optional closing paren
)


def _is_citation_token(token: str) -> bool:
    """True if the token is/contains a Vedic citation reference like '(RV.5.25.5)' or
    '(TB 1.2.1.26)' which must NOT be syllabified as Baraha Sanskrit."""
    if not token:
        return False
    # The whole token is a citation: '(RV.5.25.5)', '(TB 1.2.1.26)', 'RV.10.173.5)', etc.
    if _CITATION_PATTERN.match(token):
        return True
    # The token is a paren-group enclosing Sanskrit + citation: rare. Treat as
    # citation only if it begins with `(` immediately followed by a known prefix.
    if token.startswith('(') and re.match(r'\((RV|TB|TS|TA|T\.[ABS]|Rig)[\s\.]', token):
        return True
    return False


def parse_baraha_token(token: str) -> str:
    """
    Public entry: convert one Baraha word (no surrounding whitespace) to Devanagari.

    Handles compound-segment splits on '.' and '-' so each sub-tract gets a fresh
    "word-initial" state for independent vowels. Passes through citation-reference
    tokens (RV/TB/TS/TA refs like '(RV.5.25.5)') verbatim — these are English even
    inside <lang=def> sections.
    """
    if not token:
        return token
    # Fast path: pure ASCII digits/punctuation (no Baraha letters) → passthrough
    if not re.search(r'[A-Za-z~]', token):
        return token
    # Citation reference → pass through verbatim
    if _is_citation_token(token):
        return token
    # If this token is clearly English (starts with a lowercase ASCII word and has
    # no Baraha markers), the caller (segmenter) already routed it to a non-Sanskrit
    # path. We don't second-guess here.

    # Split on '.' and '-' so each segment is syllabified independently — this
    # makes vowel-at-segment-start behave as an independent vowel (correct for
    # compounds like "harA-rOgya" → हरा-रोग्य).
    pieces = _split_unit_aware(token)
    return ''.join(_syllabify_token(p) for p in pieces)


def parse_baraha_line(line: str) -> str:
    """
    Convert one Baraha line to Devanagari. Whitespace and intra-line punctuation
    ('|', '||', parentheses, commas, digits, etc.) are preserved. Each whitespace-
    separated token is syllabified independently.

    Note: '(RV 1.27.13)' and similar English citation refs inside <lang=def>
    sections will still be passed to syllabify per-token; ASCII-only tokens fall
    through unchanged. See parse_baraha_document for proper handling.
    """
    out_parts = []
    # Split on whitespace + the dandas while keeping them.
    # We use re.split with capturing so the delimiters are preserved in the result.
    pieces = re.split(r'(\s+|\|\||\|)', line)
    for p in pieces:
        if not p:
            continue
        if p.startswith('||'):
            out_parts.append(DOUBLE_DANDA)
        elif p.startswith('|'):
            out_parts.append(DANDA)
        elif re.match(r'^\s+$', p):
            out_parts.append(p)   # preserve original whitespace
        else:
            out_parts.append(parse_baraha_token(p))
    return ''.join(out_parts)


def parse_baraha_document(text: str, on_progress=None) -> str:
    """
    Convert a full Baraha document to Devanagari.

    The document uses <lang=eng> ... <lang=def> markers (case-sensitive tags
    embedded in the text) to switch between English explanation and Baraha
    Sanskrit. Inside <lang=def> runs we syllabify; inside <lang=eng> runs we
    pass through verbatim. The tags themselves are consumed (not emitted in
    the output).

    The algorithm tracks the current language mode line-by-line, switching
    whenever a <lang=xxx> tag is encountered. A <lang=eng> tag also retroactively
    marks any text on the same line BEFORE the tag as still being <lang=def>
    (so a normal Sanskrit line ending with an English citation is handled
    correctly — the Sanskrit is decoded, the citation is preserved).
    """
    lines = text.split('\n')
    out_lines = []
    in_def = False   # default is English (the preamble is English)
    for idx, raw in enumerate(lines):
        if on_progress and (idx + 1) % 500 == 0:
            on_progress(idx + 1, len(lines))

        # Strip the lang tag(s) from the raw line; they don't appear in output.
        # <lang=eng> acts as a mode switch: text BEFORE it on the same line
        # inherits the previous mode; text AFTER it is English.
        # <lang=def> similarly switches to Baraha Sanskrit.
        def_segments = []   # list of (mode, text)
        pos = 0
        mode = in_def
        for m in re.finditer(r'<lang=(eng|def)>', raw):
            chunk = raw[pos:m.start()]
            if chunk:
                def_segments.append((mode, chunk))
            mode = (m.group(1) == 'def')
            pos = m.end()
            in_def = mode   # persist mode into the next line
        final = raw[pos:]
        if final:
            def_segments.append((mode, final))

        # Render each segment
        rendered_parts = []
        for seg_mode, seg_text in def_segments:
            if seg_mode:
                # Baraha Sanskrit — syllabify per token
                rendered_parts.append(parse_baraha_line(seg_text))
            else:
                # English — pass through verbatim
                rendered_parts.append(seg_text)
        out_lines.append(''.join(rendered_parts))

    if on_progress:
        on_progress(len(lines), len(lines))
    return '\n'.join(out_lines)


# --- Keyboard / self-test -----------------------------------------------------

def _self_test():
    cases = [
        # (baraha, expected_devanagari)
        ('ku#ruq',        'कु॑रु॒'),
        ('cikI#r.Shati',  'चिकी॑र्.षति'),
        ('yatki~jcat',    'यत्किञ्चत्'),
        ('dakShiNAM',     'दक्षिणां'),
        ('prAqtaraqgniM', 'प्रा॒तर॒ग्निं'),
        ('ruqdra(gm)',    'रु॒द्रꣳ'),
        ('havAmahE',      'हवामहे'),
        ('OM',            'ओं'),  # O+M -> ओ+ं = ओं
        ('hari#H',        'हरि॑ः'),
        ('&gnE',          'ऽग्ने'),
        ('sarvaq',        'सर्व॒'),
        ('Bagaq',         'भग॒'),
        ('mRutasya',      'मृतस्य'),
        ('amRutasya',     'अमृतस्य'),
        ('rudra',         'रुद्र'),
        ('RudrAya',       'रुद्राय'),
        ('SivaM',         'शिवं'),
        ('Sa~gkaraM',     'शङ्करं'),
        ('kShiNA',        'क्षिणा'),
        ('namO#',         'नमो॑'),
        ('nama#H',        'नम॑ः'),
        ('VaikuNTha',     'वैकुण्ठ'),
        ('kaurava',       'कौरव'),       # au diphthong
        ('dainandinI',    'दैनन्दिनी'),  # ai diphthong
        ('gaurI',         'गौरी'),       # au in mid-word matra position
    ]
    fails = 0
    for src, expected in cases:
        got = parse_baraha_token(src)
        ok = '✓' if got == expected else '✗'
        if got != expected:
            fails += 1
            print(f"  {ok} {src!r:20s} → got {got!r:30s} expected {expected!r}")
        else:
            print(f"  {ok} {src!r:20s} → {got!r}")
    print(f"\n{'FAIL' if fails else 'PASS'}: {fails}/{len(cases)} failed")
    return fails == 0


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser(description="Baraha→Devanagari Vedic parser")
    p.add_argument('--test', action='store_true', help='run built-in self-test')
    p.add_argument('--input', '-i', help='input .txt file with Baraha text')
    p.add_argument('--output', '-o', help='output .txt file (Devanagari)')
    args = p.parse_args()
    if args.test:
        ok = _self_test()
        sys.exit(0 if ok else 1)
    if args.input:
        with open(args.input, 'r', encoding='utf-8') as f:
            text = f.read()
        out = parse_baraha_document(text)
        with open(args.output or args.input + '.dev.txt', 'w', encoding='utf-8') as f:
            f.write(out)
        print(f"Saved Devanagari to {args.output or args.input + '.dev.txt'}")