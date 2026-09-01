"""Sanskrit98 → Devanagari decoder v12 (syllable-aware)."""
import sys, re

sys.stdout.reconfigure(encoding='utf-8')

CHAR = {
    0x01: ('॥', 'D'),
    0x02: (' ', 'SP'),
    0x03: ('म', 'C'),
    0x04: ('ह', 'C'),
    0x05: ('ा', 'm'),
    0x06: ('न्', 'Hc'),
    0x07: ('य', 'C'),
    0x08: ('स', 'C'),
    0x09: ('ः', 'H'),
    0x0A: ('अ', 'V'),
    0x0B: ('थ', 'C'),
    0x0C: ('प', 'C'),
    0x0D: ('ं', 'M'),
    0x0E: ('च', 'C'),
    0x0F: ('ग', 'C'),
    0x10: ('रु', 'NM'),
    0x11: ('द्र', 'NM'),
    0x12: ('ण', 'C'),
    0x13: ('ऊ', 'V'),
    0x14: ('व', 'C'),
    0x15: ('र्', 'R'),
    0x16: ('क', 'C'),
    0x17: ('ज', 'C'),
    0x18: ('े', 'm'),
    0x19: ('न', 'C'),
    0x1A: ('ि', 'mi'),
    0x1B: ('भ', 'C'),
    0x1C: ('ष', 'C'),
    0x1D: ('ध', 'C'),
    0x1E: ('\u1CDA', 'A'),
    0x1F: ('र', 'C'),
    0x20: ('व्', 'Hc'),
    0x21: ('स्', 'Hc'),
    0x22: ('', 'SEP'),
    0x23: ('', 'PRT'),
    0x24: ('त', 'C'),
    0x25: ('उ', 'V'),
    0x26: ('इ', 'V'),
    0x27: ('।', 'D'),
    0x28: ('ु', 'm'),
    0x29: ('ब', 'C'),
    0x2A: ('हु', 'NM'),
    0x2B: ('भ्', 'Hc'),
    0x2C: ('श', 'C'),
    0x2D: ('भ', '!'),
    0x2E: ('ृ', 'm'),
    0x2F: ('ड', 'C'),
    0x30: ('ख', 'C'),
    0x31: ('घ', 'C'),
    0x32: ('ल', 'C'),
    0x33: ('ॐ', 'OM'),
    0x34: ('ै', 'm'),
    0x35: ('त्', 'Hc'),
    0x36: ('श्', 'Hc'),
    0x37: ('ी', 'm'),
    0x38: ('ꣳ', 'M'),
    0x39: ('छ', 'C'),
    0x3A: ('झ', 'C'),
    0x3B: ('ञ', 'C'),
    0x3C: ('द', 'C'),
    0x3D: ('क्ष', 'NM'),
    0x3E: ('ऊ', 'V'),
    0x3F: ('ध्', 'Hc'),
    0x40: ('ङ्ग', 'NM'),
    0x41: ('ण्', 'Hc'),
    0x42: ('ज्', 'Hc'),
    0x43: ('ए', 'V'),
    0x44: ('ग्', 'Hc'),
    0x45: ('त्र', 'NM'),
    0x46: ('ट', 'C'),
    0x47: ('ठ', 'C'),
    0x48: ('ढ', 'C'),
    0x49: ('श्च', 'NM'),
    0x4A: ('ग्न', 'NM'),
    0x4B: ('प्', 'Hc'),
    0x4C: ('श्व', 'NM'),
    0x4D: ('ऽ', 'V'),
    0x4E: ('त्त', 'NM'),
    0x4F: ('प्र', 'NM'),
    0x50: ('ग्र', 'NM'),
    0x51: ('न्न', 'NM'),
    0x52: ('ष्', 'Hc'),
    0x53: ('फ', 'C'),
    0x54: ('म्', 'Hc'),
    0x55: ('्र', 'm'),
    0x56: ('द्य', 'NM'),
    0x57: ('द्ध', 'NM'),
    0x58: ('रू', 'NM'),
    0x59: ('द्भ', 'NM'),
    0x5A: ('क्त', 'NM'),
    0x5B: ('ब्र', 'NM'),
    0x5C: ('ह्म', 'NM'),
    0x5D: ('ऋ', 'V'),
    0x5E: ('श्र', 'NM'),
    0x5F: ('भ्र', 'NM'),
    0x60: ('क्', 'Hc'),
    0x61: ('ई', 'V'),
    0x62: ('क्ष्', 'Hc'),
    0x63: ('स्त्र', 'NM'),
    0x64: ('दृ', 'NM'),
    0x65: ('य्', 'Hc'),
    0x66: ('ब्', 'Hc'),
    0x67: ('त्र्', 'Hc'),
    0x68: ('ष्ट', 'NM'),
    0x69: ('थ्', 'Hc'),
    0x6A: ('ल्', 'Hc'),
    0x6B: ('ु', 'm'),
    0x6C: ('दु', 'NM'),
    0x6D: ('्', 'H'),
    0x6E: ('हृ', 'NM'),
    0x6F: ('ृ', 'm'),
    0x70: ('ञ्ज', 'NM'),
    0x71: ('ह्य', 'NM'),
    0x72: ('ञ्च', 'NM'),
    0x73: ('त्न', 'NM'),
    0x74: ('ह्र', 'NM'),
    0x75: ('ज्ञ', 'NM'),
    0x76: ('क्र', 'NM'),
    0x77: ('द्व', 'NM'),
    0x78: ('ह्न', 'NM'),
    0x79: ('च्', 'Hc'),
    0x7A: ('म्र', 'NM'),
    0x7B: ('ह्व', 'NM'),
    0x7C: ('य्', 'Hc'),
    0x7D: ('ँ', 'M'),
    0x7E: ('द्द', 'NM'),
    0x7F: ('ु', 'm'),
    0x80: ('ू', 'm'),
    0x81: ('च्च', 'NM'),
    0x82: ('दू', 'NM'),
    0x83: ('ङ', 'C'),
    0x84: ('प्त', 'NM'),
    0x85: ('ध्न', 'NM'),
    0x86: ('ज्ज', 'NM'),
    0x87: ('हू', 'NM'),
    0x88: ('ज्र', 'NM'),
    0x89: ('ष्ठ', 'NM'),
    0x8A: ('घ्', 'Hc'),
    0x8B: ('न्त्र', 'NM'),
}

SVARITA = '\u0951'
ANUDATTA = '\u0952'

V_TO_MATRA = {
    'अ': 'ा', 'इ': 'ि', 'ई': 'ी', 'उ': 'ु', 'ऊ': 'ू',
    'ऋ': 'ृ', 'ए': 'े', 'ऐ': 'ै', 'ओ': 'ो', 'औ': 'ौ', 'ॐ': '',
}

LONG_VOWEL = {
    'अ': 'आ', 'इ': 'ई', 'उ': 'ऊ', 'ऋ': 'ॠ', 'ॠ': 'ॡ',
    'ए': 'ॆ', 'ऐ': 'ॖ', 'ओ': 'ॊ', 'औ': 'ॐ',
}

MATRA_COMBINE = {
    ('ा', 'े'): 'ो',
    ('ा', 'ै'): 'ौ',
}


def decode_bytes(raw):
    bs = [b for b in raw if b != 0]
    if not bs:
        return ''

    # First pass: build syllables
    # A syllable = [Hc/NM]* + C + [matras]* + [visarga]?
    # PRT/SEP apply to the PREVIOUS syllable

    syllables = []  # each = {'parts': [], 'svarita': False, 'anudatta': False}
    current_syll = {'parts': [], 'svarita': False, 'anudatta': False}
    in_conjunct = False  # currently in Hc chain
    pending_i = None
    i = 0

    def flush_syllable():
        nonlocal current_syll, syllables
        if current_syll['parts']:
            syllables.append(current_syll)
            current_syll = {'parts': [], 'svarita': False, 'anudatta': False}

    while i < len(bs):
        b = bs[i]
        info = CHAR.get(b)
        if info is None:
            i += 1
            continue
        dev, typ = info

        if typ == 'PRT':
            # Svarita: mark current syllable, DON'T flush yet (matras may follow)
            if current_syll['parts']:
                current_syll['svarita'] = True
            elif syllables:
                syllables[-1]['svarita'] = True
            i += 1
            continue

        if typ == 'SEP':
            # Anudatta: mark current syllable, DON'T flush yet
            if current_syll['parts']:
                current_syll['anudatta'] = True
            elif syllables:
                syllables[-1]['anudatta'] = True
            i += 1
            continue

        if typ == '!':  # 0x2D - context-dependent भ
            # Word start: after space/danda or at beginning
            if (not syllables and not current_syll['parts']) or \
               (syllables and ''.join(syllables[-1]['parts']) in (' ', '।', '॥')):
                current_syll['parts'].append('भ')
            elif current_syll['parts'] and current_syll['parts'][-1].endswith('म') and \
                 i + 1 < len(bs) and bs[i + 1] != 0x09:
                current_syll['parts'][-1] = current_syll['parts'][-1][:-1] + 'ं'
            i += 1
            continue

        if typ == 'mi':  # i-matra / I-matra (deferred)
            pending_i = dev
            i += 1
            continue

        if typ == 'R':  # Repha (superscript r)
            if current_syll['parts']:
                current_syll['parts'].insert(0, 'र्')
            else:
                current_syll['parts'].append('र्')
            i += 1
            continue

        # Vowel (V-type): matra after consonant in same syllable, else new syllable
        if typ == 'V':
            if pending_i is not None:
                current_syll['parts'].append(dev + pending_i)
                pending_i = None
            elif current_syll['parts'] and not in_conjunct:
                matra = V_TO_MATRA.get(dev, '')
                if matra:
                    current_syll['parts'].append(matra)
                else:
                    current_syll['parts'].append(dev)
            else:
                # New syllable: check if next byte is matching matra
                expected_matra = V_TO_MATRA.get(dev)
                if expected_matra and i + 1 < len(bs):
                    nxt = bs[i + 1]
                    nxt_info = CHAR.get(nxt)
                    if nxt_info and nxt_info[1] == 'm' and nxt_info[0] == expected_matra:
                        # Next is matching matra → use long vowel, skip matra
                        current_syll['parts'].append(LONG_VOWEL.get(dev, dev))
                        i += 2  # skip both vowel and matra
                        in_conjunct = False
                        continue
                current_syll['parts'].append(dev)
            in_conjunct = False
            i += 1
            continue

        # Consonant-like
        if typ in ('C', 'Hc', 'NM', 'OM', 'GO'):
            if typ == 'Hc':
                # Half-form: if current syllable has a complete consonant (not in conjunct),
                # start new syllable for conjunct onset
                if current_syll['parts'] and not in_conjunct:
                    flush_syllable()
                current_syll['parts'].append(dev)
                in_conjunct = True
            elif typ == 'NM':
                # Ligature: complete unit, new syllable
                if current_syll['parts']:
                    flush_syllable()
                if pending_i is not None:
                    current_syll['parts'].append(dev + pending_i)
                    pending_i = None
                else:
                    current_syll['parts'].append(dev)
                in_conjunct = False
            else:  # C, OM, GO
                # Full consonant: if in conjunct, completes it; else new syllable
                if not in_conjunct and current_syll['parts']:
                    flush_syllable()
                if pending_i is not None:
                    current_syll['parts'].append(dev + pending_i)
                    pending_i = None
                else:
                    current_syll['parts'].append(dev)
                in_conjunct = False
            i += 1
            continue

        # Matra (m-type): attach to current syllable
        if typ == 'm':
            if current_syll['parts']:
                last = current_syll['parts'][-1]
                # Special: repha (र्) + u-matra (ु) → रु ligature
                if last == 'र्' and dev == 'ु':
                    current_syll['parts'][-1] = 'रु'
                elif last == 'अ':
                    if dev == 'ा': current_syll['parts'][-1] = 'आ'
                    elif dev == 'े': current_syll['parts'][-1] = 'ए'
                    elif dev == 'ै': current_syll['parts'][-1] = 'ऐ'
                    elif dev == 'ु': current_syll['parts'][-1] = 'उ'
                    elif dev == 'ू': current_syll['parts'][-1] = 'ऊ'
                    else: current_syll['parts'][-1] = last + dev
                elif last == 'आ':
                    if dev == 'े': current_syll['parts'][-1] = 'ओ'
                    elif dev == 'ै': current_syll['parts'][-1] = 'औ'
                    else: current_syll['parts'][-1] = last + dev
                else:
                    combined = MATRA_COMBINE.get((last[-1], dev))
                    if combined:
                        current_syll['parts'][-1] = last[:-1] + combined
                    else:
                        current_syll['parts'][-1] = last + dev
            else:
                current_syll['parts'].append(dev)
            in_conjunct = False
            i += 1
            continue

        # Space, Danda, Visarga, Anusvara
        if typ == 'H':
            # Visarga attaches to current syllable, then ends it
            if current_syll['parts']:
                current_syll['parts'].append(dev)
            else:
                current_syll['parts'].append(dev)
            flush_syllable()
            in_conjunct = False
            i += 1
            continue
        if typ in ('SP', 'D', 'M', 'A'):
            flush_syllable()
            syllables.append({'parts': [dev], 'svarita': False, 'anudatta': False})
            in_conjunct = False
            i += 1
            continue

        i += 1

    flush_syllable()
    if pending_i is not None:
        syllables.append({'parts': [pending_i], 'svarita': False, 'anudatta': False})

    # Build output
    out = []
    for syl in syllables:
        s = ''.join(syl['parts'])
        if syl['svarita']:
            # Svarita before visarga if visarga is the last char
            if s.endswith('\u0903'):  # visarga
                s = s[:-1] + SVARITA + '\u0903'
            else:
                s += SVARITA
        if syl['anudatta']:
            # Anudatta similarly before visarga
            if s.endswith('\u0903'):
                s = s[:-1] + ANUDATTA + '\u0903'
            else:
                s += ANUDATTA
        out.append(s)

    return clean_repetitions(''.join(out).strip())


def clean_repetitions(text):
    if not text:
        return text

    # 1. Clean duplicated whole-phrases like '॥ महान्यासः॥॥ महान्यासः॥' -> '॥ महान्यासः॥'
    prev = None
    while prev != text:
        prev = text
        text = re.sub(r'(॥\s*[^॥]+?॥)\s*\1', r'\1', text)
        text = re.sub(r'([^\s॥।]+[॥।])\s*\1', r'\1', text)

    # 2. Known repeated direction/body section labels in Mahanyasa
    label_replacements = [
        (r'पूर्वागं\s*पूर्वागं|पूर्वांग\s*पूर्वांग', 'पूर्वांग'),
        (r'दक्षिणांग\s*दक्षिणांग', 'दक्षिणांग'),
        (r'पश्चिमांग\s*पश्चिमांग', 'पश्चिमांग'),
        (r'उत्तराा?ुत्तराा?ंगं?ग?|उत्तरांग\s*उत्तरांग|उत्तरांगुत्तरांग', 'उत्तरांग'),
        (r'ऊर्ध्वांग\s*ऊर्ध्वांग|ऊर्ध्वांगूर्ध्वांग', 'ऊर्ध्वांग'),
        (r'पूर्वंपूर्वं', 'पूर्वं'),
        (r'दक्षिणदक्षिण', 'दक्षिण'),
        (r'पश्चिमंपश्चिमं?', 'पश्चिमं'),
        (r'ध्यानं।\s*ध्यानं।', 'ध्यानं।'),
    ]

    for pattern, repl in label_replacements:
        text = re.sub(pattern, repl, text)

    # 3. Clean adjacent word-half repetitions for any general word
    def dedup_word(m):
        w = m.group(0)
        n = len(w)
        for half_len in range(3, n // 2 + 1):
            if n % half_len == 0 or n == 2 * half_len:
                h1 = w[:half_len]
                h2 = w[half_len:2*half_len]
                c1 = re.sub(r'[\u0951\u0952]', '', h1)
                c2 = re.sub(r'[\u0951\u0952]', '', h2)
                if c1 == c2 and len(w) == 2 * half_len:
                    return h1
        return w

    tokens = text.split(' ')
    new_tokens = []
    for tok in tokens:
        new_tok = re.sub(r'[\u0900-\u097F\u1CD0-\u1CFF\uA8E0-\uA8FF]+', dedup_word, tok)
        new_tokens.append(new_tok)
    text = ' '.join(new_tokens)

    # 4. Clean trailing label after final danda/double-danda: e.g. "॥ पूर्वागम्" or "॥ पूर्वागंपूर्वागं"
    m = re.match(r'^(.*[॥।])\s*([\u0900-\u097F\u1CD0-\u1CFF\uA8E0-\uA8FF\s]+)$', text)
    if m:
        body, tail = m.group(1), m.group(2).strip()
        if tail:
            tail_clean = re.sub(r'[\u0951\u0952\s]', '', tail)
            body_clean = re.sub(r'[\u0951\u0952\s]', '', body)
            if tail_clean in body_clean or any(k in tail_clean for k in ['पूर्वा', 'दक्षि', 'पश्छि', 'पश्चि', 'उत्तरा', 'ऊर्ध्वा', 'पूर्व', 'दक्षिण', 'पश्चिम']):
                text = body

    return text.strip()


def run_tests():
    tests = [
        (bytes([0x19, 0x03, 0x23, 0x21, 0x24, 0x18, 0x02, 0x10, 0x11, 0x02,
                0x03, 0x22, 0x06, 0x07, 0x14, 0x23, 0x02, 0x25, 0x22, 0x24, 0x05,
                0x18, 0x24, 0x22, 0x02, 0x26, 0x1c, 0x23, 0x14, 0x18, 0x22, 0x02,
                0x19, 0x03, 0x23, 0x09, 0x27]),
         'नम॑स्ते रुद्र म॒न्यव॑ उ॒तोत॒ इष॑वे॒ नम॑ः।'),
        (bytes([0x19, 0x03, 0x23, 0x21, 0x24, 0x18, 0x02, 0x0a, 0x21, 0x24, 0x28, 0x22, 0x02,
                0x1d, 0x06, 0x14, 0x23, 0x19, 0x18, 0x02, 0x29, 0x05, 0x22, 0x2a, 0x2b, 0x07, 0x05, 0x23,
                0x03, 0x28, 0x22, 0x24, 0x02, 0x24, 0x18, 0x22, 0x02, 0x19, 0x03, 0x23, 0x09, 0x01, 0x02]),
         'नम॑स्ते अस्तु॒ धन्व॑ने बा॒हुभ्या॑मु॒त ते॒ नम॑ः॥'),
        (bytes([0x07, 0x05, 0x02, 0x24, 0x22, 0x02, 0x26, 0x1c, 0x28, 0x23, 0x09, 0x02,
                0x1a, 0x2c, 0x22, 0x14, 0x24, 0x23, 0x03, 0x05, 0x02, 0x1a, 0x2c, 0x22, 0x14, 0x03, 0x2d,
                0x02, 0x29, 0x22, 0x1b, 0x13, 0x14, 0x23, 0x02, 0x24, 0x18, 0x22, 0x02, 0x1d, 0x19, 0x28, 0x23, 0x09, 0x27]),
         'या त॒ इषु॑ः शि॒वत॑मा शि॒वं ब॒भूव॑ ते॒ धनु॑ः।'),
        (bytes([0x1a, 0x2c, 0x22, 0x14, 0x05, 0x02, 0x2c, 0x23, 0x1f, 0x22, 0x20, 0x07, 0x05, 0x23, 0x02,
                0x07, 0x05, 0x02, 0x24, 0x14, 0x22, 0x02, 0x24, 0x07, 0x05, 0x23, 0x02, 0x19, 0x05, 0x18, 0x02, 0x10, 0x11, 0x02, 0x03, 0x2e, 0x2f, 0x07, 0x01, 0x02]),
         'शि॒वा श॑र॒व्या॑ या तव॒ तया॑ नो रुद्र मृडय॥'),
    ]

    ok = True
    for raw, exp in tests:
        got = decode_bytes(raw)
        status = 'OK' if got == exp else 'FAIL'
        if got != exp:
            ok = False
        print(f'{status}  {raw.hex()}')
        print(f'  Got:  {got}')
        print(f'  Exp:  {exp}')
    print(f'\nAll pass: {ok}')
    return ok


if __name__ == '__main__':
    run_tests()