import sys, re
sys.stdout.reconfigure(encoding='utf-8')
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate

"""
Sanskrit98 -> ITRANS -> Devanagari decoder v4.

Encoding rules (derived empirically from PDF font analysis):
- Lowercase char  = full consonant (inherent vowel 'a' unless a matra follows)
- Uppercase char  = half consonant (halant built into glyph; joins next consonant)
- '?' = protection marker: the consonant it follows keeps its inherent vowel
        and never joins a conjunct. Invisible in output.
- '/' = invisible boundary. Two effects:
    * a bare consonant cluster (2+ matra-less, unprotected full consonants)
      immediately before '/' forms a conjunct (tv/ -> tva)
    * matras after '/' attach back to the consonant before '/' (ba/÷ -> bahu)
- 'a' immediately before '/' = consonant ha (ह); otherwise = aa matra (ा)
- 'V'/'W' = conjunct-forming va: suppresses the inherent vowel of the
            preceding consonant (even across '/'), then acts as व (r/V -> rva)
- After a '/'-terminated conjunct-cluster word, if the next word repeats the
  cluster's first consonant, that duplicate is dropped (tv/ tya -> tvayA)
- Ligatures: é = रु, Ô = द्र, _ = भ् (half)
- 'm!' at word end = anusvara; '!' at word start = भ; '!' at word end = silent
- 'f' = ड, but ङ after ka-varga chars (k, o, g, ")
- '÷' = u matra, '&' = vocalic-r matra
"""

CONS = {
    'k': 'k', 'o': 'kh', 'g': 'g', '"': 'gh',
    'c': 'ch', 'D': 'Ch', 'j': 'j', 'H': 'jh', '|': '~n',
    'q': 'T', 'Q': 'Th', 'F': 'Dh', '[': 'N',
    't': 't', 'w': 'th', 'd': 'd', 'x': 'dh', 'n': 'n',
    'p': 'p', ')': 'ph', 'b': 'b', 'm': 'm',
    'y': 'y', 'r': 'r', 'l': 'l', 'v': 'v', 'L': 'L',
    'z': 'sh', ';': 'Sh', 's': 's', 'h': 'h',
}

HALF = {
    'N': 'n', 'S': 's', 'T': 't', 'R': 'r', 'M': 'm',
    'Y': 'y', 'K': 'k', 'G': 'g',
}

VOW = {'A': 'a', '@': 'A', '#': 'i', '$': 'I', '%': 'u', '^': 'U', ']': 'RRi'}

MATRA = {'i': 'i', 'I': 'I', 'u': 'u', 'U': 'U', 'e': 'e', 'E': 'ai',
         '&': 'RRi', '÷': 'u', 'a': 'A'}


def tokenize(text):
    """Turn Sanskrit98 text into tokens: [type, value, protected].

    Types: C (full consonant), Hc (half consonant), VW (conjunct va),
           m (matra), V (independent vowel), M (anusvara), H (visarga),
           D (danda), SEP ('/'), SP (space).
    '?' is folded into the preceding consonant's protected flag.
    """
    tokens = []
    i, n = 0, len(text)
    prev_raw = ''
    while i < n:
        ch = text[i]
        if ch in '/\n\r':
            tokens.append(['SEP', None, False])
        elif ch == ' ':
            tokens.append(['SP', None, False])
        elif ch == '?':
            # protect most recent consonant (may look past matras/seps)
            for j in range(len(tokens) - 1, -1, -1):
                t = tokens[j][0]
                if t in ('C', 'Hc', 'VW'):
                    tokens[j][2] = True
                    break
                if t in ('m', 'SEP'):
                    continue
                break
        elif ch == 'm' and i + 1 < n and text[i + 1] == '!':
            tokens.append(['M', None, False])      # m! at word end = anusvara
            i += 1
        elif ch == '<':
            tokens.append(['M', None, False])
        elif ch == '>':
            tokens.append(['H', None, False])
        elif ch in '.,':
            tokens.append(['D', None, False])
        elif ch == '\u00e9':                        # é = रु
            tokens.append(['C', 'r', False])
            tokens.append(['m', 'u', False])
        elif ch == '\u00d4':                        # Ô = द्र
            tokens.append(['Hc', 'd', False])
            tokens.append(['C', 'r', False])
        elif ch == '_':                             # _ = भ्
            tokens.append(['Hc', 'bh', False])
        elif ch in 'VW':                            # conjunct-forming va
            tokens.append(['VW', 'v', False])
        elif ch == 'f':
            tokens.append(['C', '~n' if prev_raw in 'kog"' else 'D', False])
        elif ch == '!':
            if prev_raw == '' or prev_raw in '/ \n\r':
                tokens.append(['C', 'bh', False])   # ! at word start = भ
            # else: silent word ender
        elif ch == 'a':
            if i + 1 < n and text[i + 1] == '/':
                tokens.append(['C', 'h', False])    # a/ = ह (h + inherent a)
            else:
                tokens.append(['m', 'A', False])    # ा matra
        elif ch in CONS:
            tokens.append(['C', CONS[ch], False])
        elif ch in HALF:
            tokens.append(['Hc', HALF[ch], False])
        elif ch in VOW:
            tokens.append(['V', VOW[ch], False])
        elif ch in MATRA:
            tokens.append(['m', MATRA[ch], False])
        # else: unknown char, skip
        prev_raw = ch
        i += 1
    return tokens


def _collect_matras(tokens, i):
    """Collect matras following position i, skipping invisible SEPs.
    Returns (matras, next_index_after_consumed)."""
    matras = []
    j = i
    while j < len(tokens):
        t = tokens[j][0]
        if t == 'SEP':
            j += 1
        elif t == 'm':
            matras.append(tokens[j][1])
            j += 1
        else:
            break
    # aa + e sandhi -> o
    merged, k = [], 0
    while k < len(matras):
        if matras[k] == 'A' and k + 1 < len(matras) and matras[k + 1] == 'e':
            merged.append('o')
            k += 2
        else:
            merged.append(matras[k])
            k += 1
    return merged, j


def to_itrans(tokens):
    out = []
    pending = []            # matras seen before their consonant (e.g. i-matra)
    drop_first = None       # consonant to drop at start of next word
    pending_space = False   # space deferred while a duplicate-drop is armed
    i, n = 0, len(tokens)
    while i < n:
        typ, val, prot = tokens[i]

        if typ == 'SEP':
            i += 1
            continue
        if typ == 'SP':
            if drop_first is not None:
                pending_space = True    # defer: join words if drop fires
            else:
                out.append(' ')
            i += 1
            continue

        # any meaningful token: resolve a pending duplicate-drop first
        if drop_first is not None:
            if typ == 'C' and val == drop_first:
                drop_first = None
                pending_space = False   # words join (tv/ tya -> tvaya)
                i += 1
                continue
            drop_first = None
            if pending_space:
                out.append(' ')
                pending_space = False
        elif pending_space:
            out.append(' ')
            pending_space = False

        if typ == 'M':
            out.append('M'); i += 1; continue
        if typ == 'H':
            out.append('H'); i += 1; continue
        if typ == 'D':
            out.append('|'); i += 1; continue
        if typ == 'V':
            out.append(val); i += 1; continue
        if typ == 'm':
            pending.append(val)     # matra before its consonant (i-matra)
            i += 1
            continue

        matras, j = _collect_matras(tokens, i + 1)
        matras = pending + matras
        pending = []

        if matras:
            out.append(val + ''.join(matras))
            i = j
            continue

        if typ == 'Hc':             # half consonant: never has inherent vowel
            out.append(val)
            i += 1
            continue

        # next meaningful token (j already skipped SEPs)
        nt = tokens[j][0] if j < n else None

        if nt == 'VW':              # conjunct va: this consonant goes bare
            out.append(val)
            i += 1
            continue

        if prot:                    # protected by '?': keeps inherent vowel
            out.append(val + 'a')
            i += 1
            continue

        if typ == 'C' and nt == 'C' and not tokens[j][2]:
            # possible '/'-terminated conjunct cluster:
            # consecutive adjacent, unprotected, matra-less C tokens,
            # last one immediately followed by SEP
            cluster = [i]
            k = i
            ok = True
            while True:
                mts, _ = _collect_matras(tokens, k + 1)
                nxt = k + 1
                if mts:                     # member has matra -> no cluster
                    ok = False
                    break
                if nxt < n and tokens[nxt][0] == 'C' and not tokens[nxt][2]:
                    cluster.append(nxt)
                    k = nxt
                    continue
                break
            if ok and len(cluster) >= 2 and k + 1 < n and tokens[k + 1][0] == 'SEP':
                # emit conjunct: all but last bare, last with inherent 'a'
                for ci in cluster[:-1]:
                    out.append(tokens[ci][1])
                out.append(tokens[cluster[-1]][1] + 'a')
                drop_first = tokens[cluster[0]][1]
                i = cluster[-1] + 1
                continue

        out.append(val + 'a')       # default: inherent vowel
        i += 1

    itrans = ''.join(out)
    itrans = re.sub(r' +', ' ', itrans).strip()
    return itrans


def decode(text, debug=False):
    tokens = tokenize(text)
    itrans = to_itrans(tokens)
    dev = transliterate(itrans, sanscript.ITRANS, sanscript.DEVANAGARI)
    if debug:
        return dev, itrans, tokens
    return dev


if __name__ == '__main__':
    tests = [
        ('nm?Ste éÔ m/Nyv? %/taet/ #;?ve/ nm?>,',
         'नमस्ते रुद्र मन्यव उतोत इषवे नमः।'),
        ('nm?Ste AStu/ xNv?ne ba/÷_ya?mu/t te/ nm?>.',
         'नमस्ते अस्तु धन्वने बहुभ्यामुत ते नमः।'),
        ('ya t/ #;u?> iz/vt?ma iz/vm! b/!Uv? te/ xnu?>,',
         'या त इषुः शिवतमा शिवं बभूव ते धनुः।'),
        ('iz/va z?r/Vya? ya tv/ tya? nae éÔ m&fy.',
         'शिवा शर्वया या त्वया नो रुद्र मृडय।'),
    ]

    print("=== Sanskrit98 decoder tests ===")
    all_pass = True
    for raw, exp in tests:
        dev, itrans, _ = decode(raw, debug=True)
        ok = dev == exp
        all_pass &= ok
        print(f"{'PASS' if ok else 'FAIL'}  {raw}")
        print(f"  ITRANS: {itrans}")
        print(f"  Got: {dev}")
        if not ok:
            print(f"  Exp: {exp}")
    print(f"\nAll pass: {all_pass}")
