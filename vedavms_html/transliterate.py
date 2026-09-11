"""Baraha transliteration to Devanagari Unicode converter with full Vedic accent support.

Supports:
- Consonants and conjuncts (including ~g, ~G, ~j, ~J, kSh, GY)
- Vowels and matras
- Vedic accents:
    q -> U+0952 (Anudatta: bottom horizontal line ॒)
    # -> U+0951 (Svarita: top vertical stroke ॑)
    $ -> U+1CDA (Deergha Svarita: double vertical stroke ᳚)
- Vedic nasal glyphs:
    (gm), (gM), (gm~) -> U+A8F3 (ꣳ DEVANAGARI SIGN CANDRABINDU VIRAMA)
    (gg)              -> U+1CFA (ᳺ VEDIC SIGN DOUBLE ANUSVARA ANTARGOMUKHA)
    ~M                -> U+00A0 U+0901 (NBSP + Candrabindu ँ)
- Symbols & Punctuation:
    & -> ऽ (Avagraha)
    | -> । (Danda)
    || -> ॥ (Double Danda)
    ^ -> ZWNJ (Zero Width Non-Joiner)
- Canonical normalization: ensures zero dotted circles around Visarga (ः) and Anusvara (ं).
"""

import re
import unicodedata

CONSONANTS = {
    'k': 'क्', 'kh': 'ख्', 'K': 'ख्', 'g': 'ग्', 'gh': 'घ्', 'G': 'घ्', '~g': 'ङ्', '~G': 'ङ्',
    'c': 'च्', 'ch': 'च्', 'Ch': 'छ्', 'C': 'छ्', 'j': 'ज्', 'jh': 'झ्', 'J': 'झ्', '~j': 'ञ्', '~J': 'ञ्',
    'T': 'ट्', 'Th': 'ठ्', 'TH': 'ठ्', 'D': 'ड्', 'Dh': 'ढ्', 'DH': 'ढ्', 'N': 'ण्',
    't': 'त्', 'th': 'थ्', 'd': 'द्', 'dh': 'ध्', 'n': 'न्',
    'p': 'प्', 'ph': 'फ्', 'P': 'फ्', 'b': 'ब्', 'bh': 'भ्', 'B': 'भ्', 'm': 'म्',
    'y': 'य्', 'r': 'र्', 'l': 'ल्', 'v': 'व्', 'w': 'व्',
    'S': 'श्', 'sh': 'श्', 'Sh': 'ष्', 'shh': 'ष्', 's': 'स्', 'h': 'ह्', 'L': 'ळ्',
    'x': 'क्ष्', 'kSh': 'क्ष्', 'j~j': 'ज्ञ्', 'GY': 'ज्ञ्',
}

VOWEL_SIGNS = {
    'a': '',
    'A': 'ा', 'aa': 'ा',
    'i': 'ि',
    'I': 'ी', 'ee': 'ी',
    'u': 'ु',
    'U': 'ू', 'oo': 'ू',
    'Ru': 'ृ', 'ru': 'ृ',
    'RU': 'ॄ',
    'e': 'े', 'E': 'े',
    'ai': 'ै',
    'o': 'ो', 'O': 'ो',
    'au': 'ौ',
}

INDEPENDENT_VOWELS = {
    'a': 'अ',
    'A': 'आ', 'aa': 'आ',
    'i': 'इ',
    'I': 'ई', 'ee': 'ई',
    'u': 'उ',
    'U': 'ऊ', 'oo': 'ऊ',
    'Ru': 'ऋ', 'ru': 'ऋ',
    'RU': 'ॠ',
    'e': 'ए', 'E': 'ए',
    'ai': 'ऐ',
    'o': 'ओ', 'O': 'ओ',
    'au': 'औ',
}

CONSONANT_KEYS = sorted(CONSONANTS.keys(), key=len, reverse=True)
VOWEL_KEYS = sorted(VOWEL_SIGNS.keys(), key=len, reverse=True)


def baraha_to_devanagari(text: str) -> str:
    """Convert Baraha ASCII transliteration text into Devanagari Unicode with Vedic svara notation."""
    if not text:
        return ""

    # Protect English tokens, tags, and phrases
    placeholders = []

    def repl_eng(m):
        placeholders.append(m.group(0))
        return f'\uE000{len(placeholders)-1}\uE001'

    # Entirely English phrases (Korvai, notes, etc.)
    if re.search(r'\b(Korvai|Padam|Prapaataka|Series|Dasinis|Special|First and Last|Notes for Users)\b', text, re.I):
        return text

    # Parenthesized English tags e.g. (A1), (A7), (A67), (A14)
    text = re.sub(r'\([A-Za-z]+\d+[a-z]?\)', repl_eng, text)
    # Standalone letter+digit codes e.g. A1, A7, T.A.1.2.3, T.B.3.11.7.1
    text = re.sub(r'\b[A-Za-z]\d+\b', repl_eng, text)
    text = re.sub(r'\b[A-Z]\.[A-Z0-9\.]+\b', repl_eng, text)

    # 1. Clean whitespace before combining tokens in Baraha source
    text = re.sub(r'\s+([q#$HM]+)', r'\1', text)

    # 2. Normalize compound symbols
    text = text.replace('~g', 'ङ्')
    text = text.replace('~G', 'ङ्')
    text = text.replace('~j', 'ञ्')
    text = text.replace('~J', 'ञ्')

    # Vedic Nasal glyphs:
    # (gm), (gM), (gm~) -> ꣳ (U+A8F3 DEVANAGARI SIGN CANDRABINDU VIRAMA / GUM with dot)
    # (gg)              -> ᳺ (U+1CFA VEDIC SIGN DOUBLE ANUSVARA ANTARGOMUKHA)
    # ~M                -> \u00A0ँ (NBSP + Chandrabindu)
    text = re.sub(r'\(gm~?\)', '\uA8F3', text, flags=re.I)
    text = re.sub(r'\(gg\)', '\u1CFA', text, flags=re.I)
    text = text.replace('~M', '\u00A0\u0901')
    text = text.replace('&', 'ऽ')
    text = text.replace('||', '॥')
    text = text.replace('|', '।')

    # Normalize ^^ and ^ to single ZWNJ token
    text = re.sub(r'\^+', '\u200C', text)

    # 3. Fix ordering of accents with Visarga (H) and Anusvara (M)
    # In Baraha: #H -> H#, qH -> Hq, $H -> H$
    # In Baraha: #M -> M#, qM -> Mq, $M -> M$
    text = re.sub(r'([q#$]+)H', r'H\1', text)
    text = re.sub(r'([q#$]+)M', r'M\1', text)

    out = []
    i = 0
    n = len(text)
    while i < n:
        if text[i] == '\uE000':
            end_p = text.find('\uE001', i)
            if end_p != -1:
                idx = int(text[i + 1:end_p])
                out.append(placeholders[idx])
                i = end_p + 1
                continue

        if text[i] == 'q':
            out.append('॒')  # U+0952 Anudatta
            i += 1
            continue
        elif text[i] == '#':
            out.append('॑')  # U+0951 Svarita
            i += 1
            continue
        elif text[i] == '$':
            out.append('᳚')  # U+1CDA Deergha Svarita
            i += 1
            continue
        elif text[i] == 'H':
            out.append('ः')  # U+0903 Visarga
            i += 1
            continue
        elif text[i] == 'M':
            out.append('ं')  # U+0902 Anusvara
            i += 1
            continue
        elif text[i] == '\u200C':
            out.append('\u200C')
            i += 1
            continue
        elif text[i] in ' \t\n\r।,॥():-0123456789.[]{}~/\\+*\uA8F3\uA8F2\uA8F4\u1CFA\u00A0\u0901':
            out.append(text[i])
            i += 1
            continue

        # Match consonant
        matched_c = None
        for c in CONSONANT_KEYS:
            if text.startswith(c, i):
                matched_c = c
                break

        if matched_c:
            i += len(matched_c)
            matched_v = None
            for v in VOWEL_KEYS:
                if text.startswith(v, i):
                    matched_v = v
                    break

            if matched_v:
                i += len(matched_v)
                cons_char = CONSONANTS[matched_c][:-1]
                v_sign = VOWEL_SIGNS[matched_v]
                out.append(cons_char + v_sign)
            else:
                out.append(CONSONANTS[matched_c])
            continue

        # Match independent vowel
        matched_v = None
        for v in VOWEL_KEYS:
            if text.startswith(v, i):
                matched_v = v
                break

        if matched_v:
            i += len(matched_v)
            out.append(INDEPENDENT_VOWELS[matched_v])
            continue

        out.append(text[i])
        i += 1

    res = ''.join(out)

    # 4. Canonical Normalization to ensure ZERO dotted circles:
    # 4a. Deduplicate consecutive viramas:
    res = re.sub(r'\u094D+', '्', res)
    # 4b. Visarga (ः) must precede any combining Vedic accent:
    res = re.sub(r'([\u0951\u0952\u1CDA])(ः)', r'\2\1', res)
    # 4c. Anusvara (ं) must precede any combining Vedic accent:
    res = re.sub(r'([\u0951\u0952\u1CDA])(ं)', r'\2\1', res)
    # 4d. Candrabindu (ँ) directly after whitespace -> convert space to non-breaking space
    res = re.sub(r'\s+ँ', '\u00A0ँ', res)
    # 4e. Accents should not follow punctuation or whitespace without a base:
    res = re.sub(r'([ \t\n।,॥\(\)\[\]\{\}\-])([\u0951\u0952\u1CDA]+)', r'\1', res)

    return res


if __name__ == '__main__':
    tests = [
        "SannO# miqtraH SaM ~Mvaru#NaH | SannO# BavatvaryaqmA |",
        "Sannaq indrOq bRuhaqspati#H | SannOq viShNu#rurukraqmaH |",
        "namOq brahma#NE | nama#stE vAyO | tvamEqva praqtyakShaqM brahmA#si |",
        "tvamEqva praqtyakShaqM brahma# vadiShyAmi | RuqtaM ~Mva#diShyAmi | saqtyaM ~Mva#diShyAmi |",
        "SIkShAM ~MvyA$KyAsyAqmaH | varNaqH svaraH | mAtrAq balaM | sAma# santAqnaH |",
        "pA~NktA(gg)# sOmaH |",
        "OM SAntiqH SAntiqH SAnti#H ||",
    ]
    for t in tests:
        print(f"Baraha: {t}")
        print(f"Deva:   {baraha_to_devanagari(t)}\n")
