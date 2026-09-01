# Visual Swara Extraction Prompt — Batch: Asaavi_K6_sub402_411

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
page_0157.png, page_0158.png, page_0159.png, page_0160.png

---

## MASTER TEXT TO ANNOTATE:

```text
#Start of Mantra Sets -- subsection_402 ## DO NOT EDIT
പ്രപ്രവസ്ത്രഷ്ടുഭ(𑌷𑍁) മിഷമോഹാഓഹാ(𑌤𑍂) ഏ(𑌤) । വന്ദ(𑌕𑌾) ദ്വീരാ(𑌥𑌾𑌚𑍍) യാആ(𑌕𑌾) ഇന്ദവാ(𑌟𑌿) ഓ(𑌟) ഹാ(𑌤) ഓ(𑌟) ഹാ(𑌤) ഏ(𑌤) । ധീയാവോമേധസാ(𑌯𑍂) താ(𑌪) യേ(𑌶) ഓ(𑌟) ഹാ(𑌤) ഓ(𑌟) ഹാ(𑌤) ഏ(𑌤) । പുരാന്ധീ(𑌭𑌿) യാ(𑌤) । വീ(𑌕) വോ(𑌪) ബാ(𑌪𑍍𑌲) സാതോ(𑌪𑍍𑌲𑌾) । ഹാഇ(𑌶𑌾) । ॥1॥
#End of Mantra Sets -- subsection_402 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_403 ## DO NOT EDIT
കശ്യപസ്യ(𑌷𑍀) സ്വ൪വിദാ(𑌤𑌿) ഏ(𑌤) । യാആഹുസ്സാ(𑌚𑍀) യൂജാ(𑌕𑌾) വാ(𑌯) ഇതീ(𑌪𑌾) യായോ(𑌫𑌾) ൪വീശ്വാ(𑌫𑌾) മാപീ(𑌫𑌾) വ്രതാ(𑌤𑌾) ഇ(𑌶) । യജ്ഞാന്ധീ(𑌭𑌿) രോ(𑌤) । നീചായാ(𑌟𑌿𑌟𑍍) യാ(𑌖) ഔഹോവാ(𑌶𑌿) ।ഊ(𑌖) പാ(𑌶) ॥2॥
#End of Mantra Sets -- subsection_403 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_404 ## DO NOT EDIT
വിശ്വാനരാ(𑌤𑍀) । സ്യവാ(𑌟𑌾) സ്പാതീം(𑌟𑌾) । ആനാനതസ്യാ(𑌕𑍁) ശാ(𑌚) വാ(𑌯) സാഃ(𑌟) । ഏ(𑌕) വൈ(𑌚) ശ്ചച൪ഷണാ(𑌟𑍀𑌚𑍍) ഈനാം(𑌚𑌾) । ഊതീ(𑌕𑌾) ഹൂവാ(𑌕𑌾) ഇരഥാ(𑌪𑌿) നാം(𑌪𑍍𑌲) । ഹാഇ(𑌶𑌾) ॥3॥ വിശ്വാ(𑌖𑌾) നരസ്യവൗഹോ(𑌪𑍍𑌲𑍂) സ്പാ(𑌙) തിം(𑌶) । ആനാനതാ(𑌟𑍀) ഹാ(𑌤) സ്യാശാ(𑌕𑌾) വാ(𑌖) സാഃ(𑌣) । ഏ(𑌕) വൈ(𑌚) ശ്ചച൪ഷണാ(𑌪𑍀) ഇനാം(𑌤𑍍𑌰𑌾) । ഊതീ(𑌕𑌾) ഹൂവാ(𑌕𑌾) ഇരഥാ(𑌪𑌿) നാം(𑌪𑍍𑌲) । ഹാഇ(𑌶𑌾) ॥4॥
#End of Mantra Sets -- subsection_404 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_405 ## DO NOT EDIT
സാഘായാസ്താ(𑌟𑍀) ഏ(𑌤) । ദിവോനാരാ(𑌟𑍀) ഏ(𑌤) । ധിയാമാ൪ക്താ(𑌟𑍀) ഏ(𑌤) । സ്യാശാ൪മ്മാതാ(𑌟𑍀) ഏ(𑌤) । ഊതാഇസാബൃ(𑌟𑍁) ഏ(𑌤) । ഹാതോദീവാ(𑌟𑍀) ഏ(𑌤) । ദ്വിഷോആംഹാ(𑌟𑍀) ഏ(𑌤) । നാതാരാ(𑌚𑌿) തിഇഴാ(𑌟𑌿) ഭാ(𑌖𑌣𑍍) । ഓ(𑌪) ഇഴാ(𑌪𑍍𑌲𑌾) ॥5॥ സഘായസ്താ(𑌤𑍀) ഇ(𑌶) । ദീവോ(𑌕𑌾) നരോധിയോ(𑌕𑍀) മാ൪ക്താ(𑌟𑌾) സ്യാശ(𑌕𑌾) ൪മ്മാതാഃ(𑌚𑌾) । ഊതീ(𑌥𑌾) സാബൃ(𑌟𑌾) ഹാതോ(𑌕𑌾) ദിവാഃ(𑌚𑌾) । ദ്വിഷോ(𑌕𑌾) ആംഹോ(𑌟𑌾) । നാതാരാ(𑌚𑌿) തിഇഴാ(𑌟𑌿) ഭാ(𑌖𑌣𑍍) । ഓ(𑌪) ഇഴാ(𑌪𑍍𑌲𑌾) ॥6॥
#End of Mantra Sets -- subsection_405 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_406 ## DO NOT EDIT
അ൪ചതപ്രാ൪ചതാ(𑌷𑍂) നാ(𑌖) രാഃ(𑌪𑍍𑌲) । പ്രിയമേധാ(𑌖𑍀) സോആ(𑌚𑌾) ൪ചാതാ(𑌫𑌾) । അ൪ചന്തുപൂ(𑌖𑍀) ത്രാകാ(𑌚𑌾) ഊ(𑌕) താ(𑌫) । പൂ(𑌕) രമിദ്ധാ(𑌟𑌿) ഷ്ണുവാ൪ചാ(𑌖𑌿) । താ(𑌤𑍍𑌰) ॥7॥
#End of Mantra Sets -- subsection_406 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_407 ## DO NOT EDIT
ഉക്ഥമിന്ദ്രാ(𑌤𑍀) । യാശംസാ(𑌟𑌿) യാം(𑌤) । വാ൪ധാനം(𑌕𑌿) പുരൂനിഷ്ഷാ(𑌟𑍀) ഇധാ(𑌤𑌾) ഇ(𑌶) । ശക്രോയാ(𑌭𑌿) ഥാ(𑌤) സൂതേ(𑌕𑌾) ഷൂ(𑌖) നാഃ(𑌣) । രാ(𑌕) രണാ(𑌟𑌾) ത്സാ(𑌤) । ഖീയാ(𑌕𑌾) ഇഷൂ(𑌟𑌾) ചാ(𑌖𑌣𑍍) । ഓ(𑌪) ഇഴാ(𑌶𑌾) ॥8॥
#End of Mantra Sets -- subsection_407 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_408 ## DO NOT EDIT
വിഭോഷ്ടഇ(𑌷𑌿) ന്ദ്രരാധാ(𑌤𑌿) സാഃ(𑌤) । വിഭവീരാ(𑌟𑍀) തിശ്ശതോകൃതോ(𑌕𑍁) ശതാ(𑌟𑌾) ക്രതാ(𑌚𑌾) ബു(𑌶) । ആഥാ(𑌕𑌾) നോവിശ്വച൪ഷണേ(𑌚𑍂) ശ്വചാ(𑌟𑌾) ൪ഷാണാ(𑌚𑌾) ഇ(𑌶) । ദ്യുമ്നംസൂദത്രമം(𑌕𑍂) ഹയത്രമാംഹാ(𑌖𑍁) । യാ(𑌤𑍍𑌰) ॥9॥
#End of Mantra Sets -- subsection_408 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_409 ## DO NOT EDIT
വയശ്ചാ(𑌖𑌿) ഇക്തേപതത്രിണാഃ(𑌶𑍂) । ദ്ബിപാശ്ചതൂ(𑌷𑍀) ഷ്പദ൪ജൂ(𑌕𑌿) നായേ(𑌪𑌾) ഉഷഃപ്രാരാ(𑌶𑍀) ൻ। ൠതൂം(𑌕𑌾) രനൂദിവോ(𑌕𑍀) ആന്തേ(𑌟𑌾) । ഭാ(𑌪) യാ(𑌶) സ്പാ(𑌖) രോ(𑌪𑍍𑌲) । ഹാഇ(𑌶𑌾) ॥10॥
#End of Mantra Sets -- subsection_409 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_410 ## DO NOT EDIT
ആമിയേ(𑌷𑌿) ദേവാസ്ഥനാ(𑌤𑍀) । മധ്യേയേരോ(𑌷𑍀) ചനേദിവാഃകാ(𑌚𑍁) ദ്വാഋതാങ്കാ(𑌕𑍀) ദമാ൪ക്താം(𑌟𑌿) । കാപ്രത്നാ(𑌕𑌿) വാആഹൂ(𑌟𑌿) തീഃ(𑌖𑌣𑍍) । ഓ(𑌪) ഇഴാ(𑌶𑌾) ॥11॥
#End of Mantra Sets -- subsection_410 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_411 ## DO NOT EDIT
ൠചംസാമയജാ(𑌤𑍂) । മഹാഇയാഭ്യാ(𑌷𑍁) ങ്ക൪മാ(𑌕𑌿) ണീകൃണ്വാ(𑌟𑌿) താ(𑌤) ഇ(𑌶) । വീതേസദ(𑌕𑍀) സിരാജാ(𑌟𑌿) താഃ(𑌤) । യജ്ഞാന്ദാ(𑌟𑌿) ഇവേ(𑌤𑌾) । ഷൂവാ(𑌕𑌾) ക്ഷതാ(𑌕𑌾) ഇഴാ(𑌟𑌾) ഭാ(𑌖𑌣𑍍) । ഓ(𑌪) ഇഴാ(𑌪𑍍𑌲𑌾) ॥12॥ ൠചംസാമാ(𑌖𑍀) യാജാമഹാ(𑌪𑍍𑌲𑍀) ഇ(𑌶) । യാഭ്യാം(𑌚𑌾) ക൪മാ(𑌥𑌾𑌚𑍍) ണീകാ(𑌕𑌾) ണ്വാ(𑌯) താ(𑌟) ഇണ്വതാ(𑌟𑌿) ഇ(𑌶) । വാഇതേസദ(𑌕𑍁𑌚𑍍) സീരാ(𑌕𑌾) ജാ(𑌯) തോ(𑌟) ജാതാഃ(𑌟𑌾) । യജ്ഞാ(𑌕𑌾) ന്ദാ(𑌯) ഇവേ(𑌟𑌾) । ഷൂവാ(𑌕𑌾) ക്ഷതാ(𑌕𑌾) ഇഴാ(𑌟𑌾) ഭാ(𑌖𑌣𑍍) । ഓ(𑌪) ഇഴാ(𑌶𑌾) ॥13॥
#End of Mantra Sets -- subsection_411 ## DO NOT EDIT
```

---

## OUTPUT FORMAT:
Return **ONLY** the fully annotated text preserving the `#Start of Mantra Sets` and `#End of Mantra Sets` tags. Do not wrap in conversational fluff or additional markdown tags.
