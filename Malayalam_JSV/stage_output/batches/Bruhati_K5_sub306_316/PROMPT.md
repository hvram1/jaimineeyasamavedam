# Visual Swara Extraction Prompt — Batch: Bruhati_K5_sub306_316

You are an expert Vedic epigraphist and Sanskrit/Malayalam manuscript transcriber specializing in Jaimineeya Samavedam (JSV) musical notations.

## TASK
Inspect the attached scanned manuscript page(s) and insert the visual swara modifiers into the provided Malayalam master text block.

## STRICT RULES
1. **COLOR RULE (CRITICAL)**: **IGNORE RED INK completely.**
   - Red ink marks are Grantha swara letters (e.g. തി, ത്ത്, ഖ, ടു) which are **already present** as Unicode Grantha tokens (like `(𑌤𑌿)`) in the text.
   - Look **ONLY for non-base BLACK INK marks** (slashes, dots, vertical bars, arcs, roofs, underbars, commas).
2. **ZERO-REGRESSION ON BASE TEXT**:
   - Do **NOT** alter base Malayalam letters, Grantha tokens, punctuation (`।`, `॥`), verse numbers, or spacing.
   - You **ONLY** insert visual modifier tokens into the text.
3. **TOKEN LEXICON**:
   - `(G)` : Descending slash attached below bottom-right of an akshara (e.g., `അ(G)ഗ്നേ`)
   - `(C)` : Raised shoulder dot at top-right of an akshara (e.g., `ദേ(C)വാ`)
   - `(H)` : Vertical swarita bar centered directly above an akshara (e.g., `മാ(H)നോ`)
   - `(A)` : Syllable-spanning arc above the line
   - `(A1)`: Arc over danda `।`
   - `(B)` : Peak caret roof `^` above syllable
   - `(D)` : Wide chevron roof `Ʌ` above line spanning 2+ syllables
   - `_`   : Sustain underbar connector between words at baseline
   - `.`   : Pause dot inline at baseline
   - `,`   : Low comma inline at baseline

## ATTACHED MANUSCRIPT IMAGES
page_0111.png, page_0112.png, page_0113.png, page_0114.png, page_0115.png, page_0116.png

---

## MASTER TEXT TO ANNOTATE:

```text
#Start of Mantra Sets -- subsection_306 ## DO NOT EDIT
യോരാജാ(H)ചാ(𑌖𑍀) ൪ഷാണാഇനാം(𑌪𑍍𑌲𑍀) । യാതാരഥേ(𑌕𑍀𑌚𑍍)_ ഭീരാ(𑌕𑌾)_ ധ്രാ(𑌯)_ ഇഗൂഃ(𑌟𑌾)_ ധ്രാഇഗൂഃ(𑌟𑌿) । വാഇശ്വാസാ(𑌟𑍀)_ ന്താരൂതാ(𑌟𑌿)_ താരൂതാ(𑌟𑌿)_ പാ൪താ(𑌕𑌾) നാ(𑌖) നാം(𑌣) । ജ്യാഇഷ്ഠായോ(𑌟𑍀) വാത്രാഹാ(𑌕𑌿) ഗാ(𑌖) ൪ണാ(𑌣) ഇ(𑌶) । ത്രഹാഗൃണാ(𑌪𑍍𑌲𑍀)_ ഇ(𑌶) ।ഹോ(𑌪𑍍𑌲) ഇഴാ(𑌶𑌾) ॥1॥
#End of Mantra Sets -- subsection_306 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_307 ## DO NOT EDIT
യോരാജാ(H)ചഋ(𑌤𑍁) ഷാണാ(𑌖𑌾) ഇനാം(𑌶𑌾) । യാതാരഥേ(𑌕𑍀) ഭീരാ(A)ധ്രാ(𑌟𑌿)(A) ഇഗൂഃ(𑌤𑌾) । വിശ്വാസാന്തരുതാ(𑌷𑍂) പൃതനാ(𑌟𑌿) നാം(𑌤) । ജ്യാ(𑌟) ഇഷ്ഠാ(𑌤𑌾) യ്യോ(A)വൃ(𑌕𑌾)(A) ത്രാഹാഉവാ(𑌕𑍀) । ഓ(𑌪) ബാഗാ(H)൪ണോ(𑌪𑍍𑌲𑌿) । ഹാഇ(𑌶𑌾) । ॥2॥
#End of Mantra Sets -- subsection_307 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_308 ## DO NOT EDIT
യത(A)ആന്ദ്രാ(𑌖𑍀)(A) ഭായാമഹാ(𑌪𑍍𑌲𑍀) ഇ(𑌶) । താതോനോ(𑌕𑌿) അഭായങ്കാ(𑌟𑌿) ൪ദ്ധീ(𑌤) । മാഘവൻശഗ്ധി(𑌷𑍁) തവത(𑌕𑌿) ന്നാഊതാ(𑌟𑌿) യാ(𑌤) ഇ(𑌶) । വിദ്വാ(A)ഇഷോ(𑌟𑍀)(A) വീ(𑌤) മാ൪ധോ(𑌕𑌾)_ ജഹിഇഴാ(𑌟𑍀) ഭാ(𑌖𑌣𑍍) । ഓ(𑌪) ഇഴാ(𑌶𑌾) ॥3॥
#End of Mantra Sets -- subsection_308 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_309 ## DO NOT EDIT
വാസ്തോഷ്പതാ(𑌤𑍀) ഇ(𑌶) । ധ്രൂവാ(A)സ്ഥൂണാ(𑌟𑍀)(A) ഉവോ(𑌖𑌾) വാ(𑌶) । അം(H)സത്രം(𑌕𑌿𑌚𑍍)_ സോ(𑌕)_ മ്യാനാം(𑌟𑌾) । ദ്രപ്സഃപുരാം(H)ഭേക്താ(𑌷𑍂) ശശ്വതാ(𑌟𑌿) ഇനാമാ(𑌖𑌿) ഇന്ദ്രാഃ(𑌣𑌾) । മൂനീനാം(𑌕𑌿) ആഉവാ(𑌟𑌿) । സാ(𑌖) ഖാ(𑌶) ॥4॥ വാസ്തോഷ്പതേ(H)ധ്രൂവാ(𑌫𑍂) സ്ഥൂ(𑌤) ണാം(𑌪) സത്രം(H)സോ(𑌪𑍍𑌲𑌿) മ്യാ(𑌙) നാം(𑌶) । ദ്രപ്സഃപുരാം(H)ഭേക്താ(𑌷𑍂) ശശ്വതാ(𑌟𑌿) ഇനാം(𑌤𑌾) । ആ(𑌟) ഇന്ദ്രാഃ(𑌤𑌾) । മൂനീ(𑌟𑌾) നാം(𑌖𑌣𑌫𑌪𑍍𑌲𑍍) । സാ(𑌖) ഖാ(𑌶) ॥5॥
#End of Mantra Sets -- subsection_309 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_310 ## DO NOT EDIT
ബണ്മഹം(𑌖𑌿) അസിസൂ൪യാ(𑌶𑍀) । ബാഴാദിത്യാ(𑌕𑍀𑌚𑍍) മാഹം(𑌕𑌾) ആ(𑌯) സാ(𑌪) ഈ(𑌣) മാഹസ്തേ(𑌣𑌿) സാതോ(𑌫𑌾) മാഹി(𑌫𑌾) മാപാ(𑌪𑍍𑌲𑌾) നീ(𑌪) ഷ്ടാ(𑌤) മാ(𑌤) । മൻഹാ(H)ദാ(𑌟𑌿) ഇവാ(𑌤𑌾) । മാ(𑌕) ഹോ(𑌪) ബാ(𑌪𑍍𑌲) ആസോ(𑌪𑍍𑌲) । ഹാഇ(𑌶𑌾) ॥6॥
#End of Mantra Sets -- subsection_310 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_311 ## DO NOT EDIT
യദിന്ദ്രപ്രാഗപാ(𑌤𑍂) ത്।  ഊദാ(𑌕𑌾)  ന്യാഗ്വാഹൂയാസേ(𑌕𑍁)  നൃഭാ(𑌟𑌾)  ഇഃ(𑌶) । സിമാ(𑌟𑌾𑌚𑍍)  പൂരൂ(𑌚𑌾)  നൃഷൂതോ(𑌥𑌿)  അസ്യാനവേ(𑌟𑍀)   । ആസീ(𑌟𑌾) പ്രാശാ(𑌟𑌾𑌚𑍍)  ദ്ധാ(𑌕)  തോ(𑌪)  ബാ(𑌪𑍍𑌲)  ൪വാശോ(𑌪𑍍𑌲𑌾) । ഹാഇ(𑌶𑌾) ॥7॥ യ(A)ദിന്ദ്ര(A)പ്രാ(𑌷𑍀) ഗപാഗുദാ(𑌤𑍀)  ഗേ(𑌤)   ।  നായഗ്വാഹൂ(𑌕𑍀𑌚𑍍) യാ(𑌕) സാഇനൃഭി(𑌟𑍀) ൪ഹാബുഹോ(𑌖𑌿) ഹാ(𑌣) ഇ(𑌶)  ।  സിമാ(𑌟𑌾𑌚𑍍)  പൂ(𑌕)  രൂ(𑌚) നൃഷൂതോ(𑌥𑌿) അസ്യാനവേ(𑌟𑍀) ൪ഹാബുഹോ(𑌖𑌿)  ഹാ(𑌣) ഇ(𑌶)  ।ആസാഇപ്രാശാ(𑌟𑍁𑌚𑍍)  ൪ഹാബുഹോ(𑌖𑌿) ഹാ(𑌣) ഇ(𑌶) । ദ്ധാ(𑌟𑌟𑍍) തൂ(𑌖)  ഔഹോവാ(𑌶𑌿)   । ൪വാ(𑌖) ശേ(𑌶) ॥8॥
#End of Mantra Sets -- subsection_311 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_312 ## DO NOT EDIT
കസ്ത(A)മിന്ദ്രാ(𑌤𑍀)(A)  ।  തുവാ(𑌟𑌾)   വാസാ(𑌟𑌾)  ബു(𑌶)  ।ആമ൪ക്ത്യോ(𑌷𑍀) ദധ൪(A)ഷതാ(𑌚𑍀)(A) ഇ(𑌶)   ശ്രദ്ധാ(𑌥𑌾)  ഹാഇതേ(𑌟𑌿)।  മാഘവ(𑌕𑌿) ന്പാ൪യാഇദാ(𑌯𑍀)  ഇവീ(𑌟𑌾)   ।  വാജീ(𑌟𑌾)  വാജാം(𑌟𑌾)  സീ(𑌕)  ഷാസാ(𑌟𑌾𑌟𑍍) താ(𑌖)  ഔഹോവാ(𑌶𑌿)    ।  ഉഊ(𑌖𑌾)  പാ(𑌶) ॥9॥ കസ്ത(A)മിന്ദ്രാത്വാ(𑌫𑍁)(A)  വസാ(𑌤𑌾)  ബൂആ(𑌪𑌾)  മ൪ക്ത്യോദധ൪ഷതാഇ(𑌶𑍃)   । ശ്രദ്ധാ(𑌥𑌾)  ഹാഇതേ(𑌟𑌿) । മാഘവ(𑌕𑌿) ന്പാ൪യാഇദാഇവാ(𑌟𑍂)  ഉവോ(𑌖𑌾)  വാ(𑌶) । വാജീ(𑌥𑌾)  വാജാം(𑌟𑌾𑌚𑍍)  സീ(𑌕)  ഷാസാ(𑌟𑌾𑌟𑍍) താ(𑌖)  ഔഹോവാ(𑌶𑌿)  । ഉഊ(𑌖𑌾) പാ(𑌶)॥10॥
#End of Mantra Sets -- subsection_312 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_313 ## DO NOT EDIT
അശ്വീ(A)അശ്വീ(𑌤𑍀)(A) । രഥീ(𑌕𑌾𑌚𑍍) സൂരൂ(𑌕𑌾) പാ(𑌯) യൂഃ(𑌟)  । ഗോ(𑌕) മയ്യദി(𑌕𑌿) ന്ദ്രാതേ(𑌯𑌾)  സാഖാ(𑌟𑌾) । ശ്വാത്രാ(𑌟𑌾)  ഭാജാ(𑌟𑌾)  വയസാ(𑌚𑌿) സചാതേസാ(𑌟𑌿) ദാ(𑌤)  । ചന്ദ്രാഇ൪യാ(𑌭𑍀)  തീ(𑌤) । സാ(𑌪)  ഭാ(𑌶)  ഊ(𑌖) പോ(𑌪𑍍𑌲)  । ഹാഇ(𑌶𑌾) ॥11॥ അശ്വീ(A)രഥീ(A)സുരൂപാ(𑌤𑍂)  യൂഃ(𑌤)   ।  ഗോ(𑌕𑌿)_  മയ്യദി(𑌕𑌿)  ന്ദ്രാതേസഖാ(𑌕𑍀) ഉവാ(𑌟𑌾)  ഹാഉവാ(𑌟𑌿)  ഹോ(𑌕)_  വാ(𑌥)_ ഇയാ(𑌚𑌾) । ശ്വാത്രാഭാജാ(𑌷𑍀) വയസാ(𑌕𑌿)  സചാതേസദാ(𑌕𑍁)  ഉവാ(𑌟𑌾)  ഹാഉവാ(𑌟𑌿)  ഹോ(𑌕)_ വാ(𑌥)_ ഇയാ(𑌚𑌾)  ।  ചന്ദ്രാ(𑌚𑌾)_ ഇ൪യാ(𑌯𑌾)_  തീ(𑌤)   । സാഭാ(𑌕𑌾)_ ഊപാഇഴാ(𑌟𑍀) ഭാ(𑌖𑌣𑍍)  । ഓ(𑌪) ഇഴാ(𑌪𑍍𑌲𑌾)  ॥12॥
#End of Mantra Sets -- subsection_313 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_314 ## DO NOT EDIT
യദ്യാവാ(𑌪𑌿)_  ഇന്ദ്രതേശതാം(𑌶𑍁) ।  ശാതംഭൂമീ(𑌕𑍀)_  രൂതാസ്യൂഃ(𑌟𑌿)   । നത്വാ(A)വജ്രി(𑌷𑍀)(A) ന്സാഹസ്രംസൂ൪യാ(𑌕𑍁)  ആനൂ(𑌟𑌾)   ।  നാജാ(𑌟𑌾)  താമാ(𑌟𑌾𑌚𑍍) ഷ്ടാ(𑌕)  രോ(𑌪)  ബാ(𑌪𑍍𑌲)  ദാസോ(𑌪𑍍𑌲𑌾)  ।ഹാഇ(𑌶𑌾)  ॥13॥
#End of Mantra Sets -- subsection_314 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_315 ## DO NOT EDIT
ഇന്ദ്രാഗ്നീ(𑌷𑍀) യപാദിയാ(𑌤𑍀) മേ(𑌤)   ।  പൂ൪വാ(A)ഗാ(𑌟𑌿)(A)  ത്പദ്വാദാ(𑌚𑌿)  ഇഭാ(𑌯𑌾) യാഃ(𑌟)   ।  ഹിത്വാശിരോ(𑌟𑍀)  ജിഹ്വായാരാരാപാ(𑌯𑍂) ശ്ചാരാ(𑌟𑌾) ത്। ത്രിം(𑌕)_ ശത്പദാന്യാക്രാ(𑌟𑍁𑌟𑍍) മാ(𑌖)  ഔഹോവാ(𑌶𑌿)    ।  ഉഊ(𑌖𑌾)  പാ(𑌶)  ॥14॥
#End of Mantra Sets -- subsection_315 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_316 ## DO NOT EDIT
ഇന്ദ്രനേദീ(𑌷) യഏദിഹാ(𑌤𑍀)  ഇമിതമേധാ(𑌤𑍁)   ।  ഭിരൂതിഭിരാ(𑌷𑍀) ശന്താ(𑌟𑌾) മാ(𑌤)    ശന്തമാഭീരാ(𑌕𑍁)_  ഭിഷ്ടിഭിരാസ്വാ(𑌟𑍁) പേ(𑌤)  । സ്വാഔ(𑌪𑌾)  ഹോ(𑌶)  ।പിഭിരോ(𑌖𑌿)  ഇഴാ(𑌶𑌾)॥15॥  । ഇന്ദ്രനേദീ(𑌷𑍀) യഏദിഹാ(𑌤𑍃)  ഇമിതമേധാ(𑌷𑍀) ഭിരൂതിഭാ(𑌤𑍀) ഇഃ(𑌶)   । ആ(𑌕)  ശന്തമശന്തമാ(𑌟𑍂)  ഭാഇരാഭീ(𑌯𑍀)  ഷ്ടീഭീരാസ്വാപാ(𑌚𑍁)  ഇ(𑌶)   । സ്വാ(𑌪) ഹാ(𑌶)   ।  പിഭിരോ(𑌖𑌿)  ഇഴാ(𑌪𑍍𑌲𑌾)  ॥16॥
#End of Mantra Sets -- subsection_316 ## DO NOT EDIT
```

---

## OUTPUT FORMAT:
Return **ONLY** the fully annotated text preserving the `#Start of Mantra Sets` and `#End of Mantra Sets` tags. Do not wrap in conversational fluff or additional markdown tags.
