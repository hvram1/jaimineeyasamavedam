"""
Devanagari to Malayalam Vedic Notation Converter

Converts Devanagari input files (PDF, TXT, DOCX, etc.) with Vedic accent notations
(such as Yajurveda/Samaveda/Rigveda accents: udatta, anudatta, svarita, dirgha svarita, kampa, gomukha/candrabindu)
into Malayalam script with exact Vedic notations.

Preserves full document page properties:
- Page headers and footers (footers retained as original English without transliteration)
- Page numbers
- Font sizes (headings, subheadings, body text, captions)
- Exact bold and normal font weights matching original Devanagari PDF
- Lowered Anudatta accent symbol (॒) via inline vertical-align (-0.32em) for clean clearance below descenders
- Elimination of extra blank lines/spacers between mantras and paragraphs
- Hrasva (short) vs Deergha (long) vowel integrity: prevents artificial deergha matras (ാ) on hrasva syllables
- Page boundaries and printable A4 layout

Supports legacy BRH Devanagari font encoded PDFs (e.g. vedavms.in) as well as standard Unicode text/PDFs.
Converts word-final halant ma (മ്) to Anusvara (ം), e.g. സൂക്തമ് -> സൂക്തം.
Fixed repha positioning for Pratar (പ്രാതർ) vs Prartha.
Aardhashchidyam (ആദ്ധ്രശ്ചിദ്യം), Dadannah (ദദന്നഃ), Vidvamsam (വിദ്വാംസം), Dviteeyam (ദ്വിതീയം), Maghavanth (മഘവന്ഥ്), Poorvanga Pooja (പൂർവ്വാംഗ പൂജ), and Ijjo (ഇജ്ജോ) font glyph decoding.
Preserves authentic Vedic symbols directly in Malayalam text output:
- ꣳ (U+A8F3 Vedic Sign Candrabindu Two / Gomukha)
- ँ (U+0901 Devanagari Anunasika / Candrabindu)
- ऽ (U+093D Avagraha)
- ᳺ (U+1CF6 Vedic Sign Ardhavisarga)
- ᳩ (U+1CE9 Vedic Sign Anusvara Ring)
- ॑ (U+0951 Udatta), ॒ (U+0952 Anudatta), ᳚ (U+1CF2 Dirgha Svarita)
"""

import sys
import os
import argparse
import re
import subprocess
import unicodedata
from pathlib import Path

try:
    from src.sanskrit98_decoder_v5 import decode_bytes as s98_decode_bytes, clean_repetitions as s98_clean_repetitions
except ImportError:
    try:
        from sanskrit98_decoder_v5 import decode_bytes as s98_decode_bytes, clean_repetitions as s98_clean_repetitions
    except ImportError:
        s98_decode_bytes = None
        s98_clean_repetitions = None

# Ensure UTF-8 stdout on Windows
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Fallback PDF extractors
PDF_ENGINE = None
pypdf_module = None

try:
    import pypdf
    pypdf_module = pypdf
    PDF_ENGINE = 'pypdf'
except ImportError:
    try:
        import PyPDF2 as pypdf
        pypdf_module = pypdf
        PDF_ENGINE = 'PyPDF2'
    except ImportError:
        try:
            import pypdfium2 as pdfium
            PDF_ENGINE = 'pypdfium2'
        except ImportError:
            PDF_ENGINE = None

try:
    from PyPDF2.generic import IndirectObject, ContentStream, TextStringObject, ByteStringObject
except ImportError:
    try:
        from pypdf.generic import IndirectObject, ContentStream, TextStringObject, ByteStringObject
    except ImportError:
        IndirectObject, ContentStream, TextStringObject, ByteStringObject = None, None, None, None

try:
    from aksharamukha import transliterate
except ImportError:
    transliterate = None


class BRHDevanagariDecoder:
    """Decodes BRH Devanagari / Vedavms legacy font encoded PDF text streams into Unicode Devanagari."""

    _MAPPING = [
        # Headers/Footers & Generic English Markers
        ('www.vedavms.in', 'www.vedavms.in'),
        ('vedavms@gmail.com', 'vedavms@gmail.com'),
        
        # Vedic Accents & Signs
        ('þ', '॑'), ('–', '॒'), ('ÿ', '᳚'), ('ý', '॒'),
        # óè / ò  = ꣳ (U+A8F3 Vedic gomukha, Candrabindu Two — Samavedic nasalization)
        # Æ       = ँ (U+0901 Devanagari Chandrabindu — general Vedic anunasika)
        # Diagnostic evidence: Æ always precedes a following consonant/vowel in word-final
        # anunasika position (e.g. lÉÇ ÆuÉ = naṃ ँva), while óè follows Vedic accent marks.
        ('óè', 'ꣳ'), ('ò', 'ꣳ'), ('Æ', 'ँ'), ('Å', 'ऽ'),
        ('Ç', 'ं'), ('È', 'ः'),
        ('ã', 'े'), ('Á', 'ॐ'), ('Ã', 'ू'), ('T', 'फ'), ('V', 'ल'), ('ª', 'ग'), ('…', 'ंग'), ('½', 'ह'),
        ('F', 'ऊ'), ('¡', 'ं'), ('X', 'ङ'), ('ɳ', 'ि'), ('§', 'ष्ठ'),
        
        # Title Decoding Fixes (Poorvanga Pooja -> पूर्वाङ्ग पूजा -> പൂർവ്വാംഗ പൂജ)
        ('mÉÔuÉÉïÇaÉ', 'पूर्वाङ्ग'), ('mÉÔuÉÉïauÉ', 'पूर्वाङ्ग'), ('mÉÔuÉÉï', 'पूर्वा'),
        ('mÉÔeÉ É', 'पूजा'), ('mÉÔeÉÉ', 'पूजा'),
        
        # BRH Conjunct fixes (Sringeri D-Bha, T-Ta, N-Ga, N-Ka, N-Ku, Shtra, Mani)
        ('MühÉÉãï°É', 'कर्णोद्भा'),
        ('mÉëÉãÎ°³', 'प्रोद्भिन्न'),
        ('Î°³', 'िद्भिन्न'),
        ('Î°', 'िद्भि'),
        ('°É', 'द्भा'),
        ('°', 'द्भ'),
        ('uÉ×¨É', 'वृत्त'),
        ('¨É', 'त्त'),
        ('¨', 'त्त'),
        ('…¡ãû', 'ङ्गे'),
        ('…¡ã', 'ङ्गे'),
        ('…¡û', 'ङ्ग'),
        ('…¡', 'ङ्ग'),
        ('ƒ¡Óû', 'ङ्कु'),
        ('ƒ¡Ó', 'ङ्कु'),
        ('ƒ¡', 'ङ्क'),
        ('íा', 'ङ्क'),
        ('¹íा', 'ष्ट्रा'),
        ('¹í', 'ष्ट्र'),
        ('¹É', 'ष्ट्रा'),
        ('¹', 'ष्ट्र'),
        ('qÉÍhÉ', 'मणि'),
        ('bne', 'घ्ने'),
        ('bn', 'घ्न'),

        # Page 2 Matra Fixes (ध्यायन्ति, नमो नमः, नमः, हिरण्याय, हिरण्यलिङ्गाय, ऊर्ध्वलिङ्गाय)
        ('krÉÉrÉliÉ', 'ध्यायन्ति'),
        ('liÉ', 'न्ति'),
        ('li', 'न्ति'),
        ('lÉqÉÉã', 'नमो'),
        ('lÉqÉÉः', 'नमः'),
        ('lÉqÉÉ', 'नम'),
        ('nmlाः', 'नमः'),
        ('नम्ाः', 'नमः'),
        ('नम्ा', 'नम'),
        ('ÌWûUhrÉÍsÉ…¡ûÉrÉý', 'हिरण्यलिङ्गाय॒'),
        ('ÌWûUhrÉÍsÉ…¡ûÉrÉ', 'हिरण्यलिङ्गाय'),
        ('हिरण्यलिङ्गाय्ा॒', 'हिरण्यलिङ्गाय॒'),
        ('हिरण्यलिङ्गाय्ा', 'हिरण्यलिङ्गाय'),
        ('लिङ्गाय्ा॒', 'लिङ्गाय॒'),
        ('लिङ्गाय्ा', 'लिङ्गाय'),
        ('ÌWûUhrÉÉrÉý', 'हिरण्याय॒'),
        ('ÌWûUhrÉÉrÉ', 'हिरण्याय'),
        ('ÌWûUhrÉ', 'हिरण्य'),
        ('ÌWû', 'हि'),
        ('ÍsÉ…¡ûÉrÉý', 'लिङ्गाय॒'),
        ('ÍsÉ…¡ûÉrÉ', 'लिङ्गाय'),
        ('ÍsÉ…¡û', 'लिङ्ग'),
        ('ÍsÉ…¡', 'लिङ्ग'),
        ('rÉÎssÉ…¡Çû', 'यल्लिङ्गं'),
        ('ÍsÉ', 'लि'),
        ('Ís', 'लि'),
        ('rÉý', 'य॒'),

        # Leaked BRH font glyph fixes (Ó -> ु, Ö -> ू, Ù -> ृ, ì -> द्रि, œ -> ठ्य, Š -> च्च, š -> ठ, † -> घ, • -> ळ्, © -> द्म, ´ -> श्र, ¦ -> द्व)
        ('अङ्गÓष्ठाभ्यां', 'अङ्गुष्ठाभ्याम्'),
        ('अङ्गÓ', 'अङ्गु'),
        ('अंगÓ', 'अङ्गु'),
        ('कदृÓ', 'कदुरु'),
        ('कद्रÓ', 'कदुरु'),
        ('शामÓ', 'शामगुल'),
        ('Ó', 'ु'),
        ('चिद्रÖ', 'चिद्रू'),
        ('ष•Ö॑तो', 'षळ्ढोतो'),
        ('ष•Ö', 'षळ्ढो'),
        ('द्रÖ', 'द्रू'),
        ('Ö', 'ू'),
        ('कालङ्कÙत', 'कालङ्कृत'),
        ('कÙ', 'कृत'),
        ('Ù', 'ृ'),
        ('अ॑दिì॒जा', 'अ॑द्रि॒जा'),
        ('रुदिì', 'रुद्रिया'),
        ('दिì', 'द्रि'),
        ('ì', 'द्रि'),
        ('प॒œते', 'प॒ठ्यते'),
        ('œ', 'ठ्य'),
        ('परा᳚Šैव', 'पराच्चैव'),
        ('रसा᳚Š', 'रसाच्च'),
        ('सू॒दय॑Š', 'सूदयच्च'),
        ('Š', 'च्च'),
        ('दृष्šा', 'दृष्ट्वा'),
        ('का॒šा॑य', 'का॒ठ्याय॑'),
        ('कšै', 'कष्ठाय'),
        ('š', 'ठ'),
        ('ज†ंाभ्यां', 'जङ्घाभ्याम्'),
        ('ज†', 'जङ्घ'),
        ('अ†', 'अङ्घ'),
        ('†', 'घ'),
        ('•', 'ळ्'),
        ('वि॒©हे', 'वि॒द्महे'),
        ('©', 'द्म'),
        ('´', 'श्र'),
        ('¦', 'द्व'),
        ('À', ''),
        ('¬', '-'),
        ('¾', '-'),
        ('ð', 'ँ'),
        ('kÉÉÌrÉþ', 'धायि॑'),
        ('kÉÉÌrÉ', 'धायि'),
        ('ÌrÉ', 'यि'),
        ('Ø', 'ृ'),
        ('uÉØýkÉã', 'वृ॒धे'),
        ('uÉØkÉã', 'वृधे'),
        ('uÉØ', 'वृ'),
        ('rÉÎxqÉý³É¤Éþ§Éã rÉýqÉ LãÌiÉý UÉeÉÉÿ', 'यस्मि॒न्नक्ष॑त्रे य॒म ऐति॒ राजा᳚'),
        ('rÉÎxqÉý ³É¤Éþ§Éã rÉýqÉ LÌiÉý UÉeÉÉÿ', 'यस्मि॒न्नक्ष॑त्रे य॒म ऐति॒ राजा᳚'),
        ('Lã', 'ऐ'),
        ('ÎxqÉ', 'स्मि'),
        ('Îxq', 'स्मि'),
        ('lÉ×ýwÉ²þUýxÉSØþiÉýxÉSèurÉÉãþqÉýxÉSýoeÉÉ a ÉÉãýeÉÉ GþiÉýeÉÉ', 'नृ॒षद्व॑र॒सदृ॑त॒सद्व्यो॑म॒सद॒ब्जामद॒ब्जा गो॒जाऋ॑त॒जा'),
        ('AÉãwÉþkÉÏwÉÑý', 'ओष॑धीषु॒'),
        ('AÉãwÉ', 'ओष'),
        ('AýbÉÉãUãÿprÉÉãÅjÉý', 'अ॒घोरे᳚भ्योऽथ॒'),
        ('jÉý', 'थ॒'),
        ('jÉ', 'थ'),
        ('zÉÔÍsÉlÉÈ', 'शूलिनः'),
        ('zÉÔ', 'शू'),
        ('fÉÇ', 'झं'),
        ('fÉ', 'झ'),
        ('gÉÇ', 'ञं'),
        ('gÉ', 'ञ'),
        ('DÇ', 'ईं'),
        ('D', 'ई'),
        
        # Jyeshthaya & Shreshthaya fixes (ज्येष्ठाय, श्रेष्ठाय)
        ('erÉãý¸ÉrÉý', 'ज्ये॒ष्ठाय॒'),
        ('erÉãý¸ÉrÉ', 'ज्ये॒ष्ठाय'),
        ('erÉã¸ÉrÉ', 'ज्येष्ठाय'),
        ('´Éãý¸ ÉrÉý', 'श्रे॒ष्ठाय॒'),
        ('´Éãý¸ÉrÉý', 'श्रे॒ष्ठाय॒'),
        ('´Éãý¸ÉrÉ', 'श्रे॒ष्ठाय'),
        ('´Éã¸ÉrÉ', 'श्रेष्ठाय'),
        ('´Éã', 'श्रे'),
        ('¸ ÉrÉ', 'ष्ठाय'),
        ('¸É', 'ष्ठा'),
        
        # Ijjo (C‹Éå -> इज्जो / ഇജ്ജോ)
        ('C‹Éå', 'इज्जो'), ('‹Éå', 'ज्जो'), ('‹É', 'ज्जा'), ('‹', 'ज्ज'),
        
        # Maghavanth & Hrasva fixes
        ('qÉbÉuÉ', 'मघव'), ('bÉÉ', 'घा'), ('bÉ', 'घ'),
        ('ljÉç', 'न्थ्'), ('lj', 'न्थ'),
        
        # Aadhrashchidyam & Turashchidyam
        ('SèkÉë', 'द्ध्र'), ('kÉë', 'ध्र'),
        ('±Ç', 'द्यं'), ('±', 'द्य'),
        ('Í¶É', 'श्चि'),
        
        # Dadannah
        ('³ÉÈ', 'न्नः'), ('³ÉÉÈ', 'न्नाः'), ('³ÉÉ', 'न्ना'), ('³É', 'न्न'), ('³', 'न्न'),
        
        # Systematic BRH prose & mantra conjuncts (long form BEFORE base form)
        ('²É', 'द्वा'), ('²', 'द्व'),
        ('²॒॒तीयं', 'द्वि॒॒तीयं'), ('²तीयं', 'द्वितीयं'),
        ('hÉÏïÇ', 'णीं'), ('hÉÏï', 'णी'),
        ('mÉïÌiÉÉÇ', 'र्पितां'), ('mÉïÌiÉ', 'र्पित'), ('mÉï', 'र्प'),
        ('eÉ¤ÉhÉÉÇ', 'दक्षिणां'), ('eÉ¤É', 'दक्षिण'),
        ('MüçrÉÉïi', 'कुर्यात्'), ('MüçrÉÉï', 'कुर्या'),
        ('MüçrÉ', 'कुर्य'), ('Müç', 'कु'),
        
        # Words & Repha fixes
        ('oÉÔuÉÉïauÉ', 'पूर्वाङ्ग'), ('oÉÔuÉÉï', 'पूर्वा'),
        ('xÉÔrÉïxÉrÉ', 'सूर्यस्य'), ('xÉÔrÉïxrÉ', 'सूर्यस्य'), ('xÉÔrÉï', 'सूर्य'),
        ('xÉuÉï', 'सर्व'), ('AuÉÉï', 'अर्वा'),
        ('mÉëÉ–iÉÍqÉï', 'प्रा॒तर्मि'), ('iÉÍqÉï', 'तर्मि'), ('ÍqÉï', 'र्मि'),
        ('iÉpÉï', 'तर्भ'), ('iÉ–pÉï', 'तर्भ'),
        ('iÉå–rÉÉåï', 'ते॒र्यो'), ('rÉÉåï', 'र्यो'),
        ('kÉ–iÉÉï', 'ध॒र्ता'), ('iÉÉï', 'र्ता'),
        ('ËUlSì', 'रिन्द्र'), ('ËUl', 'रिन्'), ('ËU', 'रि'),
        ('ÍµÉlÉÉ', 'श्विना'), ('ÍµÉ', 'श्वि'), ('Íµ', 'श्वि'),
        ('ÎeÉïiÉÇ', 'र्जितं'), ('ÍeÉïiÉÇ', 'र्जितं'), ('ÎeÉï', 'जिर्'), ('ÍeÉï', 'जिर्'), ('ÎeÉ', 'जि'), ('ÍeÉ', 'जि'), ('Íe', 'जि'),
        ('ÌuÉ', 'वि'), ('ÌS', 'दि'), ('ÌlÉ', 'नि'), ('ÌaÉ', 'गि'), ('Ì§É', 'त्रि'), ('ÌmÉ', 'पि'), ('Ìw', 'षि'), ('ÌiÉ', 'ति'), ('ÌqÉ', 'मि'),
        ('ÍqÉ', 'मि'), ('ÍpÉ', 'भि'), ('ÍzÉ', 'शि'), ('ÍxÉ', 'सि'), ('Í´É', 'श्रि'), ('Íd', 'दि'), ('Íध', 'धि'), ('ÍcÉ', 'चि'), ('ÍkÉ', 'धि'), ('ÍS', 'दि'), ('Ík', 'धि'), ('Íc', 'चि'), ('Íz', 'शि'),
        
        # Short u vs long u (huvema -> हुवेम)
        ('WÒûÉå', 'हो'), ('WÒûæ', 'है'), ('WÒûå', 'हे'), ('WÒûÉ', 'हा'),
        ('WÒûþuÉåqÉ', 'हु॑वेम'), ('WÒûuÉåqÉ', 'हुवेम'),
        ('WÒû', 'हु'), ('WÒ', 'हु'),
        ('WÕû', 'हू'), ('WÕ', 'हू'),
        ('WûÉå', 'हो'), ('Wûæ', 'है'), ('Wûå', 'हे'), ('WûÉ', 'हा'), ('Wû', 'ह'),
        ('WÉû', 'हा'), ('Wåû', 'हे'), ('Wæû', 'है'), ('WÉåû', 'हो'),
        
        # Conjuncts (long form BEFORE base form)
        ('§ÉÉ', 'त्रा'), ('§É', 'त्र'), ('§', 'त्र्'),
        ('¤ÉÉ', 'क्षा'), ('¤É', 'क्ष'), ('¤', 'क्ष्'),
        ('¥ÉÉ', 'ज्ञा'), ('¥É', 'ज्ञ'), ('¥', 'ज्ञ्'),
        ('¶ÉÉ', 'श्चा'), ('¶É', 'श्च'), ('¶', 'श्च्'),
        ('¸ÉÉ', 'ष्ठा'), ('¸É', 'ष्ठ'), ('¸', 'ष्ठ्'),
        ('µÉÉ', 'श्वा'), ('µÉ', 'श्व'), ('µ', 'श्व्'),
        ('mÉëÉ', 'प्रा'), ('mÉë', 'प्र'),
        ('bÉ', 'घ'), ('b×', 'घृ'),
        
        # Base Consonants: Long deergha form (ÉÉ) BEFORE base hrasva form (É)
        ('xÉÉ', 'सा'), ('xÉ', 'स'), ('x', 'स्'),
        ('iÉÉ', 'ता'), ('iÉ', 'त'), ('i', 'त्'),
        ('hÉÉ', 'णा'), ('hÉ', 'ण'), ('h', 'ण्'),
        ('wÉÉ', 'षा'), ('wÉ', 'ष'), ('w', 'ष्'),
        ('zÉÉ', 'शा'), ('zÉ', 'श'), ('z', 'श्'),
        ('kÉÉ', 'धा'), ('kÉ', 'ध'), ('k', 'ध्'),
        ('lÉÉ', 'ना'), ('lÉ', 'न'), ('l', 'न्'),
        ('mÉÉ', 'पा'), ('mÉ', 'प'), ('m', 'प्'),
        ('pÉÉ', 'भा'), ('pÉ', 'भ'), ('p', 'भ्'),
        ('qÉÉ', 'मा'), ('qÉ', 'म'), ('q', 'म्'),
        ('rÉÉ', 'या'), ('rÉ', 'य'), ('r', 'य्'),
        ('uÉÉ', 'वा'), ('uÉ', 'व'), ('u', 'व्'),
        ('aÉÉ', 'गा'), ('aÉ', 'ग'), ('a', 'ग्'),
        ('cÉÉ', 'चा'), ('cÉ', 'च'), ('c', 'च्'),
        ('eÉÉ', 'जा'), ('eÉ', 'ज'), ('e', 'ज्'),
        ('sÉÉ', 'ला'), ('sÉ', 'ल'), ('s', 'ल्'),
        ('oÉÉ', 'बा'), ('oÉ', 'ब'), ('o', 'ब्'),
        ('UÉ', 'रा'), ('U', 'र'), ('WÉ', 'हा'), ('W', 'ह्'),
        ('MüÉ', 'का'), ('Mü', 'क'), ('M', 'क्'),
        ('JüÉ', 'खा'), ('Jü', 'ख'), ('J', 'ख्'),
        # Z-series: alternative kha glyph (ZÉÉ/ZÉ/Z like Mü/M for ka)
        ('ZÉÉ', 'खा'), ('ZÉ', 'ख'), ('Z', 'ख्'),
        ('O', 'ट्'), ('P', 'ठ्'), ('Q', 'ड्'), ('R', 'ढ्'), ('N', 'छ्'),
        ('G', 'ऋ'),  # Vocalic R letter (ṛ standalone)
        ('E', 'उ'), ('C', 'इ'), ('I', 'ई'), ('AÉ', 'आ'), ('A', 'अ'), ('L', 'ए'),
        ('™', 'हृ'), ('Õ', 'ू'), ('Â', 'रु'), ('³', 'न्न्'), ('n', 'प्'),

        # Glyph combinations
        ('Oû', 'ट'), ('Pû', 'ठ'), ('Qû', 'ड'), ('Rû', 'ढ'), ('Nû', 'छ'),
        ('»û', 'ह्न'), ('»', 'ह्न'),
        ('ƒ¡û', 'ङ्क'), ('sÉƒ¡û', 'लङ्क'),
        ('cÉ¤ÉÑï', 'चक्षुर्'),
        ('®', 'द्ध'), ('n', 'प्'), ('g', 'ञ्च'), ('t', 'ल'),
        ('ÎalÉÇ', 'ग्निं'), ('ÎalÉ', 'ग्नि'), ('Îal', 'ग्नि'), ('ÎglÉ', 'ग्नि'), ('Îgl', 'ग्नि'),
        ('Sì', 'द्र'), ('S', 'द'), ('j', 'थ'), ('£', 'क्त'), ('¼', 'ह्म'),
        ('¨', 'र्त'), ('¹', 'ष्ट्र'),
        # kīr syllable glyph: 'Ð' already encodes कीर् (with repha र्);
        # 'Mü' is just its ka carrier glyph (must NOT add a second क),
        # and a trailing 'þUç' re-encodes the udatta + redundant repha.
        ('MüÐþUç', 'कीर्॑'), ('MüÐ', 'कीर्'),
        ('Ð', 'कीर्'), ('±', 'श्च'),
        ('Ë', 'र'), ('Ò', 'ू'), ('¢', 'क्र'),

        # Halants & Conjuncts
        ('ç', '्'), ('è', '्'), ('ë', '्र'),

        # Matras (Long 2-character matras BEFORE single character matras)
        ('Éå', 'ो'), ('Éæ', 'ौ'), ('É', 'ा'),
        ('Ï', 'ी'), ('Ñ', 'ु'), ('Ô', 'ू'), ('×', 'ृ'),
        ('å', 'े'), ('æ', 'ै'),
        
        # ï (U+00EF): BRH repha/coda-r fallback — must come AFTER all longer ï-containing patterns


        # Cleanup remaining trailing font control chars
        ('û', ''), ('Î', ''), ('Í', ''), ('Ì', ''), ('ü', '')
    ]

    @classmethod
    def is_brh_encoded(cls, text: str) -> bool:
        """Returns True if text contains BRH legacy font indicators."""
        indicators = ['þ', '–', 'óè', 'qÉWûÉ', 'mÉë', 'oÉë', 'Sì', 'jÉ', '£', 'Wû', 'Wåû', 'WÒû']
        return any(ind in text for ind in indicators)

    @classmethod
    def decode(cls, text: str) -> str:
        """Decodes BRH Devanagari text into Unicode Devanagari, preserving English text."""
        lines = text.splitlines()
        sorted_map = sorted(cls._MAPPING, key=lambda x: len(x[0]), reverse=True)
        out_lines = []
        for line in lines:
            s_line = line.strip()
            # Skip metadata/footer lines matching standard patterns
            if re.match(r'^(Version\s+\d|August|See\s+Item|Bodhayana|Based\s+on|Page\s+\d+|www\.vedavms|With\s+Poorvanga|EkadaSa|Rudra|http|TS\s+\d)', s_line, re.IGNORECASE):
                out_lines.append(line)
            else:
                res = line
                # Pre-clean split spaces inside raw font glyph streams
                res = res.replace('lÉq ÉÈ', 'lÉqÉÈ').replace('lÉq É', 'lÉqÉ')
                res = res.replace('Ér Éý', 'ÉrÉý').replace('Ér É', 'ÉrÉ').replace('q É', 'qÉ')
                res = res.replace('sÉ…¡ûÉr Éý', 'sÉ…¡ûÉrÉý').replace('ÍsÉ…¡ûÉr Éý', 'ÍsÉ…¡ûÉrÉý')

                for k, v in sorted_map:
                    res = res.replace(k, v)
                
                # Reorder the repha (ï) character: move it before the consonant cluster it modifies
                res = re.sub(
                    r'([क-ह](?:[्][क-ह])*(?:[ा-ौॢॣ]|[॒॑]|[᳐-᳹])*)ï',
                    r'र्\1',
                    res
                )
                
                # Replace any remaining isolated ï with standard repha (र्)
                res = res.replace('ï', 'र्')
                
                # Clean up any leftover unmapped font artifacts
                res = res.replace('û', '').replace('Í', '').replace('Ì', '').replace('Î', '').replace('ü', '').replace('Ø', 'ृ').replace('ð', 'ँ')
                res = res.replace('Ó', 'ु').replace('Ö', 'ू').replace('Ù', 'ृ').replace('ì', 'द्रि').replace('œ', 'ठ्य').replace('Š', 'च्च').replace('š', 'ठ').replace('†', 'घ').replace('•', 'ळ्').replace('©', 'द्म').replace('´', 'श्र').replace('¦', 'द्व').replace('À', '').replace('¬', '-').replace('¾', '-')
                
                # Fix BRH artifact: consonant + virama + ṛ-matra → consonant + ṛ-matra
                # (BRH sometimes inserts a spurious halant before the ृ vowel sign)
                res = res.replace('्ृ', 'ृ')

                # Fix Sringeri Paddhati matra & word artifacts
                res = res.replace('धाय॑', 'धायि॑')
                res = res.replace('यस्म॒न्नक्ष॑त्रे', 'यस्मि॒न्नक्ष॑त्रे').replace('यस्म॒ न्नक्ष॑त्रे', 'यस्मि॒न्नक्ष॑त्रे')
                res = res.replace('एेति॒', 'ऐति॒').replace('एेति', 'ऐति').replace('एति॒ राजा', 'ऐति॒ राजा')
                res = res.replace('एे', 'ऐ')
                res = res.replace('नृ॒षद्व॑र॒सदØ॑त॒सद्व्यो॑म॒सद॒ब्जा ग्ो॒जा ऋ॑त॒जा', 'नृ॒षद्व॑र॒सदृ॑त॒सद्व्यो॑म॒सद॒ब्जामद॒ब्जा गो॒जाऋ॑त॒जा')
                res = res.replace('nृ॒षद्व॑र॒सदØ॑त॒सद्व्यो॑म॒सद॒ब्जा ग्ो॒जा ऋ॑त॒जा', 'नृ॒षद्व॑र॒सदृ॑त॒सद्व्यो॑म॒सद॒ब्जामद॒ब्जा गो॒जाऋ॑त॒जा')
                res = res.replace('सदØ॑त॒सद्', 'सदृ॑त॒सद्')
                res = res.replace('आेष॑धीषु', 'ओष॑धीषु').replace('आेषधीषु', 'ओषधीषु')
                res = res.replace('भ्योऽथा॒', 'भ्योऽथ॒').replace('भ्योऽथा', 'भ्योऽथ')
                res = res.replace('श्ाूलिनः', 'शूलिनः').replace('श्ाूलि', 'शूलि').replace('श्ाू', 'शू')
                res = res.replace('न्ामः', 'नमः').replace('न्ाम', 'नम')
                res = res.replace('नम्ाः', 'नमः').replace('नम्ा', 'नम')
                res = res.replace('हिरण्यलिङ्गाय्ा', 'हिरण्यलिङ्गाय').replace('लिङ्गाय्ा', 'लिङ्गाय')
                res = res.replace('हरण्याय', 'हिरण्याय')
                res = res.replace('ऊर्ध्वलंगंाय', 'ऊर्ध्वलिङ्गाय').replace('ऊर्ध्वलंगाय', 'ऊर्ध्वलिङ्गाय')
                res = res.replace('ध्यायन्तिि', 'ध्यायन्ति').replace('ध्यायन्त', 'ध्यायन्ति')
                res = res.replace('िि', 'ि')

                # Fix common typos/legacy font errors in Devanagari
                res = res.replace('कमर्कर्ताुर्ं', 'कर्मकर्तुं')
                res = res.replace('कमर्कर्तुं', 'कर्मकर्तुं')
                res = res.replace('कमर्गतिभिः', 'कर्मगतिभिः')
                res = res.replace('पुण्यकमर्', 'पुण्यकर्म')
                res = res.replace('कमർ', 'कर्म')  # in case any Malayalam chars leaked
                res = res.replace('कमर्सु', 'कर्मसु')
                res = res.replace('कमर्णः', 'कर्मणः')
                res = res.replace('निविर्bнеन', 'निर्विघ्नेन')
                res = res.replace('निविर्bनेन', 'निर्विघ्नेന') # in case of mixed chars
                res = res.replace('परिसमाप्त്യഥാർം', 'परिसमाप्त्यर्थं')
                res = res.replace('परिसमाप्त्यथार्ं', 'परिसमाप्त्यर्थं')
                res = res.replace('सिद्ध्यथार्ं', 'सिद्ध्यर्थं')
                res = res.replace('सिद्धं अनुग्रहाण', 'सिद्धिं अनुग्रहाण')
                res = res.replace('सिद्धരസ്തു', 'सिद्धिरस्तु')
                res = res.replace('सिद्धरस्तु', 'सिद्धिरस्तु')
                res = res.replace('सिद्धिരസ്തു', 'सिद्धिरस्तु')

                # Fix common typos/legacy font errors in Devanagari
                res = res.replace('कमर्कर्ता ुर्ं', 'कर्मकर्तुं')
                res = res.replace('कमर्कर्ताुर्ं', 'कर्मकर्तुं')
                res = res.replace('कमर्कर्तुं', 'कर्मकर्तुं')
                res = res.replace('कमर्कतुर्ं', 'कर्मकर्तुं')
                res = res.replace('कमर्कुर्तुं', 'कर्मकर्तुं')
                res = res.replace('कमर्कर्त्ताुर्ं', 'कर्मकर्तुं')
                res = res.replace('कमर्गतिभिः', 'कर्मगतिभिः')
                res = res.replace('पुण्यकमर्', 'पुण्यकर्म')
                res = res.replace('कमർ', 'कर्म')  # in case any Malayalam chars leaked
                res = res.replace('कमर्सु', 'कर्मसु')
                res = res.replace('कमर्णः', 'कर्मणः')
                res = res.replace('निविर्bнеन', 'निर्विघ्नेन')
                res = res.replace('निविर्bनेन', 'निर्विघ्नेന') # in case of mixed chars
                res = res.replace('परिसमाप्त്യഥാർം', 'परिसमाप्त्यर्थं')
                res = res.replace('परिसमाप्त्यथार्ं', 'परिसमाप्त्यर्थं')
                res = res.replace('सिद्ध्यथार्ं', 'सिद्ध्यर्थं')
                res = res.replace('सिद्धं अनुग्रहाण', 'सिद्धिं अनुग्रहाण')
                res = res.replace('सिद्धരസ്തു', 'सिद्धिरस्तु')
                res = res.replace('सिद्धरस्तु', 'सिद्धिरस्तु')
                res = res.replace('सिद्धिരസ്തു', 'सिद्धिरस्तु')

                # Fix common typos/legacy font errors in Devanagari
                res = res.replace('कमर्कर्ता ुर्ं', 'कर्मकर्तुं')
                res = res.replace('कमर्कर्ताुर्ं', 'कर्मकर्तुं')
                res = res.replace('कमर्कर्तुं', 'कर्मकर्तुं')
                res = res.replace('कमर्कतुर्ं', 'कर्मकर्तुं')
                res = res.replace('कमर्कुर्तुं', 'कर्मकर्तुं')
                res = res.replace('कमर्कर्त्ताुर्ं', 'कर्मकर्तुं')
                res = res.replace('कमर्', 'कर्म')
                res = res.replace('कमर्गतिभिः', 'कर्मगतिभिः')
                res = res.replace('पुण्यकमर्', 'पुण्यकर्म')
                res = res.replace('कमർ', 'कर्म')  # in case any Malayalam chars leaked
                res = res.replace('कमर्सु', 'कर्मसु')
                res = res.replace('कमर्णः', 'कर्मणः')
                res = res.replace('निविर्bнеन', 'निर्विघ्नेन')
                res = res.replace('निविर्bनेन', 'निर्विघ्नेന') # in case of mixed chars
                res = res.replace('परिसमाप्त്യഥാർം', 'परिसमाप्त्यर्थं')
                res = res.replace('परिसमाप्त्यथार्ं', 'परिसमाप्त्यर्थं')
                res = res.replace('सिद्ध्यथार्ं', 'सिद्ध्यर्थं')
                res = res.replace('सिद्धं अनुग्रहाण', 'सिद्धिं अनुग्रहाण')
                res = res.replace('सिद्धരസ്തു', 'सिद्धिरस्तु')
                res = res.replace('सिद्धरस्तु', 'सिद्धिरस्तु')
                res = res.replace('सिद्धिരസ്തു', 'सिद्धिरस्तु')

                # Collapse any accidental double AA matras (ाा -> ा)
                res = re.sub(r'ा+', 'ा', res)
                out_lines.append(res)
        return '\n'.join(out_lines)


def reorder_accents_before_ardhakshara(text: str) -> str:
    """Move Vedic accent marks (॒॑᳚) that follow an ardhakshara (halant consonant) to BEFORE it,
    so the accent attaches to the preceding vowel-bearing syllable it actually marks.

    Vedic accents fall on svaras (vowels), never on halant-only (ardha) consonants. When the
    stream is `<syllable>(<C>virama)+<accent>...`, the accent should attach to <syllable>,
    not to the trailing ardhakshara.

    Covers:
    - Devanagari: chains of <consonant + U+094D (virama)>
    - Malayalam:  chains of <consonant + U+0D4D (virama)>; plus chillu forms (U+0D7A-U+0D7F)
    """
    # Devanagari: one or more (consonant + virama) followed by an accent → move accent left
    text = re.sub(r'((?:[\u0915-\u0939]\u094D)+)([॒॑᳚])', r'\2\1', text)
    # Malayalam: one or more (consonant + virama) followed by an accent → move accent left
    text = re.sub(r'((?:[\u0D15-\u0D39]\u0D4D)+)([॒॑᳚])', r'\2\1', text)
    # Malayalam chillus (ൺൻർൽൾൿ) followed by an accent → move accent before the chillu
    text = re.sub(r'([\u0D7A-\u0D7F])([॒॑᳚])', r'\2\1', text)
    return text


# Devanagari & Malayalam vowel-sign (matra) ranges, used by the dotted-circle cleanup below.
_DEV_MATRA = r'\u093E-\u094C\u093A\u093B\u094E\u094F\u1CD0-\u1CFF'   # Devanagari matras + Vedic signs
_MAL_MATRA = r'\u0D3E-\u0D57\u0D66-\u0D6F'                            # Malayalam matras + vowel signs

def normalize_combining_marks(text: str) -> str:
    """Eliminate the dotted-circle rendering artifacts that come from combining marks (matras,
    anusvara/visarga, Vedic accents) lacking a proper consonant base.

    Sources of orphans in BRH-decoded / aksharamukha-transliterated text:
      1. Spurious virama inserted before a matra:   <C> + virama + <matra>  (renders as <C>्<matra>)
         → the matra cannot attach to a halant-only consonant, so the renderer inserts a dotted circle.
         Fix: drop the virama, so the matra attaches to <C>.  e.g. क्ुरु → कुरु.
      2. Spurious whitespace inserted between a consonant and its following matra/accent:
         <C> + ' ' + <combining-mark> → dotted circle on the orphaned mark.
         Fix: drop the space, re-attaching the mark to its syllable.  e.g. द ेवानां → देवानां.
      3. NFD-decomposed two-matra sequences produced by aksharamukha / Python regex normalisation,
         e.g. `ा` (U+093E) + `े` (U+0947) instead of `ो` (U+094B). The second matra is orphaned
         because one consonant cannot hold two vowel signs → dotted circle.
         Fix: NFC-normalise so that canonical equivalent sequences recompose into their single
         code-point form (U+094B / U+094C / Malayalam analogues).

    Works uniformly on Devanagari and Malayalam, since the matra ranges cover both blocks.
    """
    # 1. Drop spurious virama (U+094D / U+0D4D) that sits between a consonant and a matra/accent.
    #    <consonant>+virama+<matra-or-accent>  →  <consonant>+<matra-or-accent>
    text = re.sub(r'([\u0915-\u0939])\u094D([' + _DEV_MATRA + r'\u0900-\u0902\u0903\u0951\u0952])', r'\1\2', text)
    text = re.sub(r'([\u0D15-\u0D39])\u0D4D([' + _MAL_MATRA + r'\u0D02\u0D03\u0D01\u0951\u0952])', r'\1\2', text)

    # 2. Drop single space between an Indic char and a following orphaned combining mark (BRH font
    #    offset artifact). A standalone matra/accent after a space is never legitimate — it was
    #    detached from its consonant. Dropping the space re-attaches it (then NFC recomposes
    #    decomposed matra pairs such as ा+े → ो).
    #    <any-Indic-char>+space+<combining-mark>  →  <any-Indic-char>+<combining-mark>
    text = re.sub(r'([\u0900-\u097F\u0D00-\u0D7F])\s+([' + _DEV_MATRA + _MAL_MATRA + r'\u0900-\u0903\u0D00-\u0D03\u0951\u0952\u1CD0-\u1CFF])',
                  r'\1\2', text)

    # 3. NFC-normalise so decomposed matra pairs (ा+े etc.) recompose into single code points.
    text = unicodedata.normalize('NFC', text)

    # Devanagari/Malayalam O (ो/ോ) and AU (ौ/ൌ) vowel signs have a canonical decomposition
    # into AA + E pairs (ा+े / ാ+െ, ാ+േ) that NFC will NOT recompose because the composition
    # is consonant-context dependent. The BRH font / aksharamukha pipeline occasionally emits
    # the decomposed pair after we drop the intervening space, so we collapse them explicitly.
    text = text.replace('\u093E\u0947', '\u094B')  # ाे → ो   (Devanagari O)
    text = text.replace('\u093E\u094C', '\u094C')  # ाौ → ौ   (Devanagari AU, defensive)
    text = text.replace('\u0D3E\u0D46', '\u0D4B')  # ാെ → ോ   (Malayalam O)
    text = text.replace('\u0D3E\u0D47', '\u0D4C')  # ാേ → ൌ   (Malayalam AU)

    return text


def clean_accent_spaces(text: str) -> str:
    """Removes font offset space artifacts attached to Vedic accent marks inside words,
    reorders accents that landed after an ardhakshara, and eliminates dotted-circle
    orphan-mark artifacts (spurious virama/space before matras, NFD-decomposed matras)."""
    text = re.sub(r'([\u0900-\u097F\u0D00-\u0D7F])\s+([॒॑᳚])([\u0900-\u097F\u0D00-\u0D7F])', r'\1\2\3', text)
    text = re.sub(r'([\u0900-\u097F\u0D00-\u0D7F])\s+([॒॑᳚])', r'\1\2', text)
    text = reorder_accents_before_ardhakshara(text)
    text = normalize_combining_marks(text)
    text = re.sub(r'्+', '्', text)
    text = re.sub(r'്+', '്', text)
    text = text.replace('ശാൂലിനഃ', 'ശൂലിനഃ').replace('ശാൂലി', 'ശൂലി').replace('ശാൂ', 'ശൂ')
    return text


def format_accents_html(text: str, wrap_anudatta: bool = True) -> str:
    """Wraps Anudatta accents in inline vertical-align spans to lower the accent mark below baseline.

    For Devanagari we do NOT wrap: U+0952 is a native combining mark that attaches to the
    preceding matra/consonant. Wrapping it in an inline-block orphan breaks the combining
    behavior so the accent visually drifts onto the following consonant ('half consonant')
    instead of the syllable it belongs to. Wrapping is only meaningful for Malayalam, where
    the Devanagari code point does not combine naturally.
    """
    if not wrap_anudatta:
        return text
    return text.replace('॒', '<span class="anudatta-bar">॒</span>')


def is_indic_or_brh_line(text: str) -> bool:
    """False for lines that are essentially English/Latin and contain no Indic or BRH-encoded
    glyphs. Such lines (introductions, footnotes, chapter titles in English, "see Chapter X",
    "based on ..." notes) should be passed through verbatim without BRH decoding or
    transliteration, which would otherwise corrupt them.

    Heuristic — line is considered English-only when it has:
      - No Devanagari / Malayalam / Vedic-extension code points (U+0900-U+097F, U+0D00-U+0D7F,
        U+1CD0-U+1CFF, U+A8E0-U+A8FF);
      - No Latin-1 supplement letters in the high range used as BRH font glyphs
        (U+00C0-U+017F) — these are what the BRH encoder uses for देवनागरी consonants/matras.
      - No Devanagari danda (। ॥).
    Pure ASCII / basic Latin / digits / standard punctuation → False.
    """
    if not text or not text.strip():
        return False
    for ch in text:
        cp = ord(ch)
        if 0x0900 <= cp <= 0x097F:       # Devanagari
            return True
        if 0x0D00 <= cp <= 0x0D7F:       # Malayalam
            return True
        if 0x1CD0 <= cp <= 0x1CFF:       # Vedic extensions
            return True
        if 0xA8E0 <= cp <= 0xA8FF:       # Vedic / Devanagari extended
            return True
        if ch in '।॥':                  # Devanagari dandas
            return True
        if 0x00C0 <= cp <= 0x017F:       # Latin-1 supplement / Latin Extended-A used by BRH
            return True
    return False


class VedicTransliterate:
    """Handles transliteration of Devanagari text with Vedic notation to Malayalam."""

    _MALAYALAM_CLEANUP = [
        ('Íശവ', 'ശിവ'),
        ('oാുÎധ്നയ', 'ഓജിഷ്ഠായ'),
        ('Gച॒ഃ', 'ഋച॒ഃ'),
        ('´ാീര', 'ക്ഷീര'),
        ('³ാാ-ത്മ॒Í³ാത്യാ', 'ത്മാനമാത്മന്നഭ്യാ'),
        ('തÇ', 'തം'), ('L॒തം', 'ഏ॒തം'),
        ('mാgcാ॑', 'പഞ്ച॑'), ('WÕûത॒', 'ഹൂത॒'),
        ('സlത᳚Ç', 'സന്തം᳚'), ('Wûാå॒തേiയാ', 'ഹോ॒തേത്യാ'),
        ('cാ॑¤ാതേ', 'ച॑ക്ഷതേ'), ('mാ॒Uാå¤ാå॑ഹാ', 'പ॒രോക്ഷേ॑ണ'),
        ('mാ॒Uാå¤ാ॑Ìmാëയാ', 'പ॒രോക്ഷ॑പ്രിയാ'), ('ÌWû', 'ഹി'),
        ('പൂർവാംഗ', 'പൂർവ്വാംഗ'), ('പൂർവാങ്ഗം', 'പൂർവ്വാങ്ഗം'),
        ('സൂക്തമ്', 'സൂക്തം'),
        ('പൂവാർംഗ', 'പൂർവ്വാംഗ'), ('സൂയർസ്യ', 'സൂര്യസ്യ'),
        ('û', ''), ('Í', ''), ('Ì', '')
    ]

    @staticmethod
    def devanagari_to_malayalam(dev_text: str, nasal_mode: str = 'symbol') -> str:
        """
        Transliterates Unicode Devanagari text to Malayalam using Aksharamukha while preserving Vedic accents and symbols.
        Preserves ꣳ (U+A8F3), ँ (U+0901), ऽ (U+093D), ᳺ (U+1CF6), ᳩ (U+1CE9), etc. directly in Malayalam.
        Converts word-final halant ma (മ്) to Anusvara (ം), e.g. സൂക്തമ് -> സൂക്തം.
        Enforces hrasva vs deergha vowel integrity (collapses extra ാ matras).
        """
        if not transliterate:
            raise RuntimeError("aksharamukha library is not installed. Please install via 'pip install aksharamukha'.")
        
        # Apply Vedic Nasal transformation if user requested phonetic replacement (gg/gm)
        target_dev_text = dev_text
        if nasal_mode in ('gg', 'malayalam_gg'):
            target_dev_text = target_dev_text.replace('ꣳ', 'ग्ग्').replace('ँ', 'ग्ग्')
        elif nasal_mode in ('gm', 'malayalam_gm'):
            target_dev_text = target_dev_text.replace('ꣳ', 'ग्म्').replace('ँ', 'ग्म्')
        elif nasal_mode == 'latin_gm':
            target_dev_text = target_dev_text.replace('ꣳ', 'gm').replace('ँ', 'gm')
        # Otherwise (nasal_mode == 'symbol' / default): preserve ꣳ, ँ, ऽ, ᳺ, ᳩ as-is!
        # ँ (U+0901) will be transliterated by aksharamukha to Malayalam chandrabindu (ഁ) — that is correct.

        lines = target_dev_text.splitlines()
        result_lines = []
        DANDA_PLACEHOLDER = '\u00A6\u00A6\u00A6'  # unlikely triple broken bar
        DANDA2_PLACEHOLDER = '\u00A6\u00A6\u00A6\u00A6'
        for line in lines:
            # Preserve danda/double-danda (not in Malayalam script)
            line = line.replace('॥', DANDA2_PLACEHOLDER).replace('।', DANDA_PLACEHOLDER)
            if re.search(r'[\u0900-\u097F\u1CD0-\u1CF9\uA8E0-\uA8FF]', line):
                tokens = re.split(r'([\u0900-\u097F\u1CD0-\u1CF9\uA8E0-\uA8FF]+)', line)
                line_res = []
                for token in tokens:
                    if not token:
                        continue
                    if re.search(r'[\u0900-\u097F\u1CD0-\u1CF9\uA8E0-\uA8FF]', token):
                        line_res.append(transliterate.process('Devanagari', 'Malayalam', token))
                    else:
                        line_res.append(token)
                res_str = ''.join(line_res)
                res_str = res_str.replace(DANDA2_PLACEHOLDER, '॥').replace(DANDA_PLACEHOLDER, '।')
                
                # Clean up font offset spaces attached to Vedic accents
                res_str = clean_accent_spaces(res_str)
                
                # Convert word-final halant ma (മ്) to Anusvara (ം)
                res_str = re.sub(r'മ്(?=[\s\|\|।\?!\.,;\)]|$)', 'ം', res_str)
                
                # Collapse any extra Malayalam AA matras (ാാ -> ാ)
                res_str = re.sub(r'ാ+', 'ാ', res_str)

                # Fix BRH artifact surviving transliteration: virama before ൃ (ക്ൃ -> കൃ)
                res_str = res_str.replace('്ൃ', 'ൃ')

                # Fix BRH artifact: virama before ൄ (ക്ൄ -> കൄ, long vocalic R)
                res_str = res_str.replace('്ൄ', 'ൄ')
                
                # Cleanup spaces between halant nasal and accents if gg/gm mode was chosen
                if nasal_mode in ('gg', 'gm', 'malayalam_gg', 'malayalam_gm'):
                    res_str = res_str.replace('ഗ്ഗ് ॑', 'ഗ്ഗ്॑').replace('ഗ്മ് ॑', 'ഗ്മ്॑')
                    res_str = res_str.replace('ഗ്ഗ് ॒', 'ഗ്ഗ്॒').replace('ഗ്മ് ॒', 'ഗ്മ്॒')
                    res_str = res_str.replace('ഗ്ഗ്  ', 'ഗ്ഗ് ').replace('ഗ്മ്  ', 'ഗ്മ് ')

                for k, v in VedicTransliterate._MALAYALAM_CLEANUP:
                    res_str = res_str.replace(k, v)
                
                # Apply repha to ൪ conversion before consonant
                res_str = re.sub(r'[\u0d7b\u0d7c]([\u0d15-\u0d39])', r'൪\1', res_str)
                
                # Fix dotted circle before visarga U+0D03 and anusvara U+0D02:
                # Swap Vedic accent (U+0951, U+0952, U+1CF2) and visarga/anusvara
                res_str = re.sub(r'([\u0d00-\u0d7f])([॒॑᳚])([ംഃ])', r'\1\3\2', res_str)

                # Swap space and combining chandrabindu U+0D01 so it attaches to the preceding word
                # (preventing dotted circle while keeping its position before the consonant)
                res_str = re.sub(r'([\s\u00a0]+)\u0d01', '\u0d01\\1', res_str)

                # Move accents that landed after an ardhakshara (halant consonant or chillu)
                # so they attach to the preceding vowel-bearing syllable, not the ardhakshara.
                res_str = reorder_accents_before_ardhakshara(res_str)

                # Eliminate dotted-circle orphan combining-mark artifacts in Malayalam
                # (spurious virama before matras / inter-mark spaces / NFD-decomposed matra pairs).
                res_str = normalize_combining_marks(res_str)

                result_lines.append(res_str)
            else:
                result_lines.append(line)
                
        return '\n'.join(result_lines)


def parse_page_range(pages_arg: str, total_pages: int):
    """Parses page range strings like '1-10', '5', '1,3,5-8', or 'all' into a list of 0-based page indices."""
    if not pages_arg or pages_arg.lower() == 'all':
        return list(range(total_pages))
        
    indices = set()
    parts = pages_arg.split(',')
    for part in parts:
        part = part.strip()
        if '-' in part:
            sub = part.split('-')
            start = int(sub[0]) - 1
            end = int(sub[1])
            indices.update(range(max(0, start), min(total_pages, end)))
        else:
            p_num = int(part) - 1
            if 0 <= p_num < total_pages:
                indices.add(p_num)
                
    return sorted(list(indices))


def extract_structured_pdf_pages(input_file: str, pages_filter: list = None, nasal_mode: str = 'symbol') -> list:
    """
    Extracts structured page elements (headers, footers, body text lines, font sizes, bold weight, alignment)
    using PyPDF2 / pypdf. Supports both Sanskrit98 font streams and standard Unicode/BRH font PDFs.
    """
    if not PDF_ENGINE or PDF_ENGINE not in ('pypdf', 'PyPDF2'):
        return None

    reader = pypdf_module.PdfReader(input_file)
    total_pages = len(reader.pages)
    indices = pages_filter if pages_filter is not None else list(range(total_pages))
    
    pages_data = []

    def mat_mul(m1, m2):
        a1, b1, c1, d1, e1, f1 = m1
        a2, b2, c2, d2, e2, f2 = m2
        return [
            a1 * a2 + c1 * b2,
            b1 * a2 + d1 * b2,
            a1 * c2 + c1 * d2,
            b1 * c2 + d1 * d2,
            a1 * e2 + c1 * f2 + e1,
            b1 * e2 + d1 * f2 + f1,
        ]

    def raw_bytes(s):
        if hasattr(s, 'original_bytes'):
            return list(s.original_bytes)
        return list(bytes(s, 'latin-1'))

    FONT_KEY = 'Sanskrit98'
    
    for i, page_idx in enumerate(indices):
        if (i + 1) % 10 == 0 or i + 1 == len(indices):
            print(f"Extracting structured PDF page properties {i + 1}/{len(indices)}...")
            
        page = reader.pages[page_idx]
        media_box = page.mediabox
        page_height = float(media_box.height)
        page_width = float(media_box.width)
        
        res = page.get('/Resources')
        fonts = res.get('/Font') if res else None
        if isinstance(fonts, IndirectObject):
            fonts = fonts.get_object()
            
        finfo = {}
        has_sanskrit98 = False
        for tag, fref in (fonts or {}).items():
            fobj = fref.get_object()
            fname = str(fobj.get('/BaseFont', ''))
            is98 = FONT_KEY in fname
            if is98:
                has_sanskrit98 = True
            is_bold = 'bold' in fname.lower() or 'heavy' in fname.lower() or 'black' in fname.lower()
            is_italic = 'italic' in fname.lower() or 'oblique' in fname.lower()
            finfo[str(tag)] = {'is98': is98, 'font_name': fname, 'is_bold': is_bold, 'is_italic': is_italic}

        if has_sanskrit98 and s98_decode_bytes is not None:
            # Sanskrit98 stream extraction
            cs = ContentStream(page['/Contents'].get_object(), reader)
            ctm = [1, 0, 0, 1, 0, 0]
            gstack = []
            tlm = [1, 0, 0, 1, 0, 0]
            cur_font, cur_size, leading = None, 12.0, 0.0
            chunks = []

            for operands, op in cs.operations:
                if op == b'q':
                    gstack.append(ctm[:])
                elif op == b'Q':
                    ctm = gstack.pop() if gstack else ctm
                elif op == b'cm':
                    m = [float(v) for v in operands]
                    ctm = mat_mul(ctm, m)
                elif op == b'Tf':
                    cur_font = str(operands[0])
                    cur_size = float(operands[1])
                elif op == b'TL':
                    leading = float(operands[0])
                elif op in (b'Td', b'TD'):
                    tlm = mat_mul([1, 0, 0, 1, float(operands[0]), float(operands[1])], tlm)
                    if op == b'TD':
                        leading = -float(operands[1])
                elif op == b'Tm':
                    tlm = [float(v) for v in operands]
                elif op == b'T*':
                    tlm = mat_mul([1, 0, 0, 1, 0, -leading], tlm)
                elif op in (b'Tj', b"'", b'"', b'TJ'):
                    pos = mat_mul(ctm, tlm)
                    px, py = pos[4], pos[5]
                    strs = []
                    if op in (b'Tj', b"'"):
                        strs = [operands[0]]
                    elif op == b'"':
                        strs = [operands[2]]
                    else:
                        strs = [it for it in operands[0]
                                if isinstance(it, (TextStringObject, ByteStringObject))]
                    for s in strs:
                        rb = raw_bytes(s)
                        chunks.append({'y': py, 'x': px, 'font': cur_font, 'size': cur_size, 'bytes': rb})

            chunks.sort(key=lambda c: (-c['y'], c['x']))
            lines_dict = {}
            for c in chunks:
                y_val = round(c['y'] / 3.0) * 3.0
                if y_val not in lines_dict:
                    lines_dict[y_val] = []
                lines_dict[y_val].append(c)

            sorted_y = sorted(lines_dict.keys(), reverse=True)
            headers, footers, body_lines = [], [], []

            for y_val in sorted_y:
                line_chunks = sorted(lines_dict[y_val], key=lambda c: c['x'])
                byts, sizes, fonts = [], [], []
                is_s98_line = False
                for lc in line_chunks:
                    byts.extend(lc['bytes'])
                    sizes.append(lc['size'])
                    fonts.append(lc['font'])
                    if lc['font'] and finfo.get(lc['font'], {}).get('is98'):
                        is_s98_line = True

                max_size = max(sizes) if sizes else 12.0
                has_bold = any(finfo.get(f, {}).get('is_bold') for f in fonts)
                has_italic = any(finfo.get(f, {}).get('is_italic') for f in fonts)
                min_x = min(lc['x'] for lc in line_chunks)
                max_x = max(lc['x'] for lc in line_chunks)

                is_header = y_val > (page_height - 55)
                is_footer = y_val < 65

                center_x = (min_x + max_x) / 2.0
                if abs(center_x - (page_width / 2.0)) < 50:
                    align = 'center'
                elif min_x > (page_width * 0.55):
                    align = 'right'
                else:
                    align = 'left'

                if is_s98_line:
                    dev_text = s98_decode_bytes(byts)
                    if s98_clean_repetitions is not None:
                        dev_text = s98_clean_repetitions(dev_text)
                else:
                    dev_text = "".join(chr(b) for b in byts if b > 0)

                dev_text = clean_accent_spaces(dev_text.strip())

                if not dev_text:
                    continue

                if not is_indic_or_brh_line(dev_text) or is_footer or 'created by' in dev_text.lower() or 'page ' in dev_text.lower():
                    mal_text = dev_text
                else:
                    mal_text = VedicTransliterate.devanagari_to_malayalam(dev_text, nasal_mode=nasal_mode)

                line_obj = {
                    'raw_text': dev_text,
                    'dev_text': dev_text,
                    'mal_text': mal_text,
                    'size': max_size,
                    'is_bold': has_bold,
                    'is_italic': has_italic,
                    'align': align,
                    'is_header': is_header,
                    'is_footer': is_footer,
                    'y': y_val
                }

                if is_header:
                    headers.append(line_obj)
                elif is_footer:
                    footers.append(line_obj)
                else:
                    body_lines.append(line_obj)

            pages_data.append({
                'page_number': page_idx + 1,
                'headers': headers,
                'body_lines': body_lines,
                'footers': footers
            })

        else:
            # Standard visitor_text extraction
            spans = []
            def visitor(text, cm, tm, font_dict, font_size):
                if text:
                    font_name = font_dict.get('/BaseFont', '') if font_dict else ''
                    is_bold = 'bold' in font_name.lower() or 'heavy' in font_name.lower() or 'black' in font_name.lower()
                    is_italic = 'italic' in font_name.lower() or 'oblique' in font_name.lower()
                    x = tm[4]
                    y = tm[5]
                    spans.append({
                        'text': text,
                        'font': font_name,
                        'size': font_size,
                        'is_bold': is_bold,
                        'is_italic': is_italic,
                        'x': x,
                        'y': y
                    })
                    
            page.extract_text(visitor_text=visitor)
            
            lines_dict = {}
            for s in spans:
                y_cluster = round(s['y'] / 3.5) * 3.5
                if y_cluster not in lines_dict:
                    lines_dict[y_cluster] = []
                lines_dict[y_cluster].append(s)
                
            sorted_y = sorted(lines_dict.keys(), reverse=True)
            
            headers = []
            footers = []
            body_lines = []
            
            for y_val in sorted_y:
                line_spans = sorted(lines_dict[y_val], key=lambda item: item['x'])
                full_line_text = "".join(item['text'] for item in line_spans)
                if not full_line_text.strip():
                    continue
                    
                max_size = max(item['size'] for item in line_spans)
                has_italic = any(item['is_italic'] for item in line_spans)
                min_x = min(item['x'] for item in line_spans)
                max_x = max(item['x'] + len(item['text']) * (item['size'] * 0.38) for item in line_spans)
                
                bold_chars = sum(len(item['text'].strip()) for item in line_spans if item['is_bold'])
                total_chars = sum(len(item['text'].strip()) for item in line_spans)
                has_bold = (total_chars > 0) and ((bold_chars / total_chars) > 0.50)
                
                is_header = y_val > (page_height - 55)
                is_footer = y_val < 75
                
                center_x = (min_x + max_x) / 2.0
                if abs(center_x - (page_width / 2.0)) < 40 and len(full_line_text.strip()) < 40:
                    align = 'center'
                elif min_x > (page_width * 0.55):
                    align = 'right'
                else:
                    align = 'left'
                    
                if not is_indic_or_brh_line(full_line_text):
                    dev_text = full_line_text
                    mal_text = full_line_text
                else:
                    dev_text = BRHDevanagariDecoder.decode(full_line_text)
                    dev_text = clean_accent_spaces(dev_text)

                    if is_footer or 'vedavms' in full_line_text.lower() or 'page ' in full_line_text.lower():
                        mal_text = full_line_text
                    else:
                        mal_text = VedicTransliterate.devanagari_to_malayalam(dev_text, nasal_mode=nasal_mode)
                
                line_obj = {
                    'raw_text': full_line_text,
                    'dev_text': dev_text,
                    'mal_text': mal_text,
                    'size': max_size,
                    'is_bold': has_bold,
                    'is_italic': has_italic,
                    'align': align,
                    'is_header': is_header,
                    'is_footer': is_footer,
                    'y': y_val
                }
                
                if is_header:
                    headers.append(line_obj)
                elif is_footer:
                    footers.append(line_obj)
                else:
                    body_lines.append(line_obj)
                    
            pages_data.append({
                'page_number': page_idx + 1,
                'headers': headers,
                'body_lines': body_lines,
                'footers': footers
            })
            
    return pages_data


def extract_fallback_pages(input_file: str, pages_arg: str = None, nasal_mode: str = 'symbol') -> tuple:
    """Fallback text extraction with smart semantic font size, boldness, and alignment layout rules."""
    ext = os.path.splitext(input_file)[1].lower()
    
    if ext == '.pdf':
        if not PDF_ENGINE:
            raise RuntimeError("A PDF processing library is required.")
        reader = pypdf_module.PdfReader(input_file)
        total_pages = len(reader.pages)
        pages_filter = parse_page_range(pages_arg, total_pages)
        
        pages_data = []
        for idx in pages_filter:
            p_text = reader.pages[idx].extract_text() or ""
            dev_text = BRHDevanagariDecoder.decode(p_text)
            dev_text = clean_accent_spaces(dev_text)
            mal_text = VedicTransliterate.devanagari_to_malayalam(dev_text, nasal_mode=nasal_mode)
            
            lines = p_text.splitlines()
            body_lines = []
            footers = []
            headers = []
            
            for line in lines:
                if not line.strip():
                    continue
                if not is_indic_or_brh_line(line):
                    l_dev = line
                    l_mal = line
                    is_foot = 'page ' in line.lower() or 'vedavms' in line.lower()
                else:
                    l_dev = BRHDevanagariDecoder.decode(line)
                    l_dev = clean_accent_spaces(l_dev)
                    is_foot = 'page ' in line.lower() or 'vedavms' in line.lower()
                    l_mal = line if is_foot else VedicTransliterate.devanagari_to_malayalam(l_dev, nasal_mode=nasal_mode)
                l_obj = {
                    'raw_text': line,
                    'dev_text': l_dev,
                    'mal_text': l_mal,
                    'size': 18.0,
                    'is_bold': False,
                    'is_italic': False,
                    'align': 'left',
                    'is_header': False,
                    'is_footer': is_foot,
                    'y': 0
                }
                if is_foot:
                    footers.append(l_obj)
                else:
                    body_lines.append(l_obj)
                    
            pages_data.append({
                'page_number': idx + 1,
                'headers': headers,
                'body_lines': body_lines,
                'footers': footers
            })
            
        return pages_data, len(pages_filter), total_pages
    else:
        with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Check if file has [PAGE X] section dividers
        page_blocks = re.split(r'={5,}\s*\n\[PAGE\s+(\d+)\]\s*\n={5,}', content)
        pages_raw = []
        if len(page_blocks) > 1:
            if page_blocks[0].strip():
                pages_raw.append((1, page_blocks[0]))
            for i in range(1, len(page_blocks), 2):
                pno = int(page_blocks[i])
                ptext = page_blocks[i+1] if i+1 < len(page_blocks) else ""
                pages_raw.append((pno, ptext))
        else:
            pages_raw.append((1, content))
            
        pages_data = []
        for pno, ptext in pages_raw:
            body_lines = []
            headers = []
            footers = []
            lines = ptext.splitlines()
            for line in lines:
                if not line.strip():
                    continue
                sline = line.strip()
                if not is_indic_or_brh_line(sline):
                    l_dev = sline
                    l_mal = sline
                else:
                    l_dev = clean_accent_spaces(sline)
                    l_mal = VedicTransliterate.devanagari_to_malayalam(l_dev, nasal_mode=nasal_mode)

                # Smart typography detection for text files
                if sline.startswith('॥') and sline.endswith('॥') and len(sline) < 30:
                    size = 24.0
                    is_bold = True
                    is_italic = False
                    align = 'center'
                elif sline.startswith('अथ ') or sline.startswith('ഓം ') or sline.startswith('അഥ '):
                    size = 19.0
                    is_bold = True
                    is_italic = False
                    align = 'center'
                elif sline.startswith('(') and sline.endswith(')') and len(sline) < 25:
                    size = 13.0
                    is_bold = True
                    is_italic = True
                    align = 'center'
                elif 'रुद्राय नमः' in sline or 'മുഖായ നമഃ' in sline or 'मुखाय नमः' in sline or 'ध्यानं' in sline:
                    size = 17.0
                    is_bold = True
                    is_italic = False
                    align = 'left'
                else:
                    size = 16.0
                    is_bold = False
                    is_italic = False
                    align = 'left'

                body_lines.append({
                    'raw_text': line,
                    'dev_text': l_dev,
                    'mal_text': l_mal,
                    'size': size,
                    'is_bold': is_bold,
                    'is_italic': is_italic,
                    'align': align,
                    'is_header': False,
                    'is_footer': False,
                    'y': 0
                })
                
            pages_data.append({
                'page_number': pno,
                'headers': headers,
                'body_lines': body_lines,
                'footers': footers
            })
            
        return pages_data, len(pages_data), len(pages_data)


def generate_structured_txt(pages_data: list) -> str:
    """Generates plain text output preserving page numbers, headers, and footers."""
    out_lines = []
    for p in pages_data:
        if p['headers']:
            out_lines.append("================================================================================")
            for h in p['headers']:
                out_lines.append(f"[HEADER] {h['mal_text']}")
            out_lines.append("================================================================================")
            
        for b in p['body_lines']:
            if b['mal_text'].strip():
                out_lines.append(b['mal_text'])
            
        if p['footers']:
            out_lines.append("--------------------------------------------------------------------------------")
            for f in p['footers']:
                out_lines.append(f"[FOOTER] {f['mal_text']}")
            out_lines.append("================================================================================")
        out_lines.append("\n")
        
    return "\n".join(out_lines)


def generate_structured_html_view(pages_data: list, title: str = "Vedic Document") -> str:
    """Generates an elegant HTML viewer preserving font sizes, bold styles, alignments, headers & footers."""
    
    def render_lines_html(lines: list, text_key: str, script_class: str):
        html_snippets = []
        for l in lines:
            raw_t = l[text_key]
            if not raw_t.strip():
                continue
                
            # Escape HTML characters
            t = raw_t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            # Only wrap anudatta in the lowering span for Malayalam; for Devanagari
            # U+0952 must remain a native combining mark so it attaches to the
            # preceding consonant/swara instead of drifting onto the next consonant.
            t = format_accents_html(t, wrap_anudatta=(script_class == 'malayalam-text'))
            
            size_pt = l['size']
            rem_size = round(max(0.65, min(1.75, size_pt / 19.0)), 2)
            
            # Styles
            styles = []
            styles.append(f"font-size: {rem_size}rem;")
            styles.append(f"text-align: {l['align']};")
            if l['is_bold']:
                styles.append("font-weight: 700;")
            else:
                styles.append("font-weight: 400;")
            if l['is_italic']:
                styles.append("font-style: italic;")
                
            style_attr = " ".join(styles)
            html_snippets.append(f'<div class="line {script_class}" style="{style_attr}">{t}</div>')
        return "\n".join(html_snippets)

    mal_pages_html = []
    dev_pages_html = []
    
    for p in pages_data:
        # Malayalam Page
        m_head = render_lines_html(p['headers'], 'mal_text', 'malayalam-text')
        m_body = render_lines_html(p['body_lines'], 'mal_text', 'malayalam-text')
        m_foot = render_lines_html(p['footers'], 'mal_text', 'malayalam-text')
        
        mal_pages_html.append(f"""
        <div class="document-page">
            <div class="page-header">{m_head}</div>
            <div class="page-body">{m_body}</div>
            <div class="page-footer">{m_foot}</div>
        </div>
        <div class="page-break"></div>
        """)
        
        # Devanagari Page
        d_head = render_lines_html(p['headers'], 'dev_text', 'devanagari-text')
        d_body = render_lines_html(p['body_lines'], 'dev_text', 'devanagari-text')
        d_foot = render_lines_html(p['footers'], 'dev_text', 'devanagari-text')
        
        dev_pages_html.append(f"""
        <div class="document-page">
            <div class="page-header">{d_head}</div>
            <div class="page-body">{d_body}</div>
            <div class="page-footer">{d_foot}</div>
        </div>
        <div class="page-break"></div>
        """)

    mal_content = "\n".join(mal_pages_html)
    dev_content = "\n".join(dev_pages_html)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Serif+Devanagari:wght@400;600;700&family=Noto+Serif+Malayalam:wght@400;600;700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        @page {{
            size: A4;
            margin: 3mm 5mm;
        }}
        
        body {{
            background-color: #f3f4f6;
            color: #111827;
            font-family: 'Inter', sans-serif;
            margin: 0;
            padding: 1.5rem;
            display: flex;
            flex-direction: column;
            align-items: center;
        }}
        
        .no-print {{
            display: flex;
            gap: 0.75rem;
            margin-bottom: 1.5rem;
            background: #ffffff;
            padding: 0.75rem 1.25rem;
            border-radius: 9999px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.06);
            border: 1px solid #e5e7eb;
        }}
        
        .btn {{
            background: #f9fafb;
            color: #374151;
            border: 1px solid #d1d5db;
            padding: 0.5rem 1.2rem;
            border-radius: 9999px;
            cursor: pointer;
            font-size: 0.9rem;
            font-weight: 500;
            transition: all 0.15s ease;
        }}
        
        .btn:hover, .btn.active {{
            background: #1d4ed8;
            color: #ffffff;
            border-color: #1d4ed8;
        }}
        
        .document-page {{
            background: #ffffff;
            width: 100%;
            max-width: 900px;
            min-height: 1100px;
            padding: 2.2rem 2.8rem;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
            border-radius: 4px;
            box-sizing: border-box;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            margin-bottom: 2rem;
        }}
        
        .page-header {{
            border-bottom: 1px solid #e5e7eb;
            padding-bottom: 0.5rem;
            margin-bottom: 1.5rem;
            color: #4b5563;
        }}
        
        .page-body {{
            flex-grow: 1;
        }}
        
        .page-footer {{
            border-top: 1px solid #e5e7eb;
            padding-top: 0.5rem;
            margin-top: 1.5rem;
            color: #4b5563;
        }}
        
        .line {{
            line-height: 2.0;
            white-space: pre-wrap;
            margin-bottom: 0.2rem;
        }}
        
        .devanagari-text {{
            font-family: 'Noto Serif Devanagari', serif;
            color: #0f172a;
        }}
        
        .malayalam-text {{
            font-family: 'Noto Serif Malayalam', 'Noto Serif Devanagari', serif;
            color: #0f172a;
        }}

        .anudatta-bar {{
            display: inline-block;
            width: 0;
            overflow: visible;
            position: relative;
            left: -0.35em;
            vertical-align: -0.52em;
            font-weight: 700;
            white-space: nowrap;
        }}
        
        .page-break {{
            page-break-after: always;
        }}
        
        @media print {{
            html, body {{
                background: #ffffff;
                padding: 0;
                margin: 0;
            }}
            .no-print {{
                display: none !important;
            }}
            .document-page-container[style*="display: none"] {{
                display: none !important;
            }}
            .document-page {{
                box-shadow: none;
                padding: 1mm 2mm !important;
                width: 100% !important;
                max-width: 100% !important;
                height: 270mm !important;
                max-height: 270mm !important;
                overflow: hidden !important;
                margin-bottom: 0 !important;
                page-break-after: always !important;
                page-break-inside: avoid !important;
                box-sizing: border-box !important;
                display: flex !important;
                flex-direction: column !important;
                justify-content: space-between !important;
            }}
            .line {{
                line-height: 1.15 !important;
                margin-bottom: 0.01rem !important;
                font-size: 0.82rem !important;
            }}
            .page-header {{
                margin-bottom: 0.2rem !important;
                padding-bottom: 0.1rem !important;
            }}
            .page-footer {{
                margin-top: 0.2rem !important;
                padding-top: 0.1rem !important;
            }}
            .page-break {{
                display: none !important;
            }}
        }}
    </style>
</head>
<body>
    <div class="no-print">
        <button class="btn active" id="btn-mal" onclick="showDoc('mal')">Malayalam Document View</button>
        <button class="btn" id="btn-dev" onclick="showDoc('dev')">Devanagari Document View</button>
    </div>

    <div class="document-page-container" id="doc-mal" style="width: 100%; max-width: 900px;">
        {mal_content}
    </div>

    <div class="document-page-container" id="doc-dev" style="width: 100%; max-width: 900px; display: none;">
        {dev_content}
    </div>

    <script>
        function showDoc(mode) {{
            document.getElementById('doc-mal').style.display = mode === 'mal' ? 'block' : 'none';
            document.getElementById('doc-dev').style.display = mode === 'dev' ? 'block' : 'none';
            document.getElementById('btn-mal').classList.toggle('active', mode === 'mal');
            document.getElementById('btn-dev').classList.toggle('active', mode === 'dev');
        }}
    </script>
</body>
</html>
"""
    return html


def convert_html_to_pdf(html_file_path: str, pdf_file_path: str) -> bool:
    """Converts HTML file to a formatted PDF using headless browser."""
    browser_executables = [
        r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
        r'C:\Program Files\Microsoft\Edge\Application\msedge.exe',
        r'C:\Program Files\Google\Chrome\Application\chrome.exe',
        r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe'
    ]
    
    browser_bin = None
    for b_path in browser_executables:
        if os.path.exists(b_path):
            browser_bin = b_path
            break
            
    if not browser_bin:
        print("Warning: Neither MS Edge nor Google Chrome found for PDF rendering.", file=sys.stderr)
        return False
        
    html_uri = Path(html_file_path).resolve().as_uri()
    pdf_abs_path = Path(pdf_file_path).resolve()
    
    cmd = [
        browser_bin,
        '--headless',
        '--disable-gpu',
        '--no-pdf-header-footer',
        f'--print-to-pdf={pdf_abs_path}',
        html_uri
    ]
    
    try:
        res = subprocess.run(cmd, capture_output=True, timeout=120)
        if res.returncode == 0 and pdf_abs_path.exists():
            print(f"Saved PDF output: {pdf_file_path}")
            return True
        else:
            print(f"Warning: PDF conversion failed: {res.stderr.decode('utf-8', errors='ignore')}", file=sys.stderr)
            return False
    except subprocess.TimeoutExpired:
        print("Warning: PDF generation timed out after 120s.", file=sys.stderr)
        return False


def convert_file(input_path: str, output_txt_path: str = None, output_html_path: str = None, 
                 output_pdf_path: str = None, pages: str = None, generate_html: bool = True, 
                 generate_pdf: bool = True, nasal_mode: str = 'symbol'):
    """Performs end-to-end file conversion with full page properties preservation."""
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")
        
    print(f"Reading input file: {input_path} (Engine: {PDF_ENGINE or 'Text'}, Nasal Mode: {nasal_mode})...")
    
    ext = os.path.splitext(input_path)[1].lower()
    if ext == '.pdf' and PDF_ENGINE in ('pypdf', 'PyPDF2'):
        total_pages = len(pypdf_module.PdfReader(input_path).pages)
        pages_filter = parse_page_range(pages, total_pages)
        pages_data = extract_structured_pdf_pages(input_path, pages_filter, nasal_mode=nasal_mode)
        num_proc_pages = len(pages_filter)
    else:
        pages_data, num_proc_pages, total_pages = extract_fallback_pages(input_path, pages, nasal_mode=nasal_mode)
        
    print(f"Extracted structured page properties for {num_proc_pages} of {total_pages} page(s).")
    
    # Generate default output paths if not specified
    input_stem = Path(input_path).stem
    out_dir = Path(input_path).parent if not output_txt_path else Path(output_txt_path).parent
    os.makedirs(out_dir, exist_ok=True)
    
    if not output_txt_path:
        output_txt_path = os.path.join(out_dir, f"{input_stem}_malayalam.txt")
        
    if not output_html_path:
        output_html_path = os.path.join(out_dir, f"{input_stem}_malayalam.html")

    if not output_pdf_path:
        output_pdf_path = os.path.join(out_dir, f"{input_stem}_malayalam.pdf")
        
    # Write plain text Malayalam output with headers & footers
    txt_content = generate_structured_txt(pages_data)
    with open(output_txt_path, 'w', encoding='utf-8') as f:
        f.write(txt_content)
    print(f"Saved Malayalam text output: {output_txt_path}")
    
    # Write HTML visual output
    if generate_html:
        html_content = generate_structured_html_view(pages_data, title=f"Vedic Conversion: {input_stem}")
        with open(output_html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"Saved HTML viewer: {output_html_path}")
        
        # Generate PDF output
        if generate_pdf:
            print("Generating PDF output via browser...")
            convert_html_to_pdf(output_html_path, output_pdf_path)
            
    return pages_data, output_txt_path, output_html_path, output_pdf_path


def main():
    parser = argparse.ArgumentParser(description="Convert Devanagari input file with Vedic notation to Malayalam with page properties.")
    parser.add_argument("--input", "-i", required=True, help="Path to input Devanagari file (PDF, TXT, etc.)")
    parser.add_argument("--output", "-o", help="Path to output Malayalam text file (.txt)")
    parser.add_argument("--html", help="Path to output HTML viewer file (.html)")
    parser.add_argument("--pdf", "-p", help="Path to output PDF file (.pdf)")
    parser.add_argument("--pages", help="Page range to process (e.g. '1-5', '10,12', or 'all')")
    parser.add_argument("--nasal", choices=['symbol', 'gg', 'gm', 'latin_gm'], default='symbol', help="Vedic Anunasika/Gomukha symbol preservation mode (symbol, gg, gm, or latin_gm). Default: symbol")
    parser.add_argument("--no-html", action="store_true", help="Skip HTML viewer generation")
    parser.add_argument("--no-pdf", action="store_true", help="Skip PDF document generation")
    
    args = parser.parse_args()
    
    try:
        convert_file(
            input_path=args.input, 
            output_txt_path=args.output, 
            output_html_path=args.html, 
            output_pdf_path=args.pdf,
            pages=args.pages,
            generate_html=not args.no_html,
            generate_pdf=not args.no_pdf,
            nasal_mode=args.nasal
        )
        print("Conversion completed successfully!")
    except Exception as e:
        print(f"Error during conversion: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

