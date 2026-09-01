# Visual Swara Extraction Prompt — Batch: Pavamanam_K4_sub580_593

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
page_0243.png, page_0244.png, page_0245.png, page_0246.png, page_0247.png, page_0248.png, page_0249.png, page_0250.png, page_0251.png, page_0252.png

---

## MASTER TEXT TO ANNOTATE:

```text
#Start of Mantra Sets -- subsection_580 ## DO NOT EDIT
അചിക്രദാ(𑌤𑍀) ദാചീ(𑌕𑌾𑌚𑍍) ക്രാ(𑌕) ദാ(𑌖) ദചിക്രദാദേ(𑌪𑍍𑌲𑍁)। വൃഷാഹരാ(𑌤𑍀) ഇ(𑌶) വാ൪ഷാ(𑌕𑌾𑌚𑍍) ഹാ(𑌕) രാ(𑌖) ഇവൃഷാഹരാഏ(𑌪𑍍𑌲𑍂)। മഹാന്മിത്രോ(𑌤𑍀) മാഹാ(𑌕𑌾) ന്മി(𑌕) ത്രോ(𑌖𑌾) മഹാന്മിത്രാഏ(𑌪𑍍𑌲𑍁)। നദ൪ശതാ(𑌤𑍀) നാദ(𑌕𑌾) ൪ശാ(𑌕) താ(𑌖) നദ൪ശതാഏ(𑌪𑍍𑌲𑍁)। സംസൂ൪യാ(𑌤𑌿) ഇ(𑌶) സംസൂ(𑌕𑌾𑌚𑍍) രീ(𑌕) യാ(𑌖) ഇസംസൂ൪യാഏ(𑌪𑍍𑌲)। ണദിദ്യുതാ(𑌤𑍀) ഇ(𑌶) ണാദീ(𑌕𑌾𑌚𑍍) ദ്യൂ(𑌕) താ(𑌖) ഇണാദാ(𑌶𑌿) ഇദ്യുതാബൂ(𑌪𑍍𑌲𑍀)। ബാ(𑌶) ॥ 1॥
#End of Mantra Sets -- subsection_580 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_581 ## DO NOT EDIT
ആതേദക്ഷാം(𑌤𑍀) । മയോഭൂ(𑌭𑌿) വാം(𑌤) । വൻഹിമദ്യാവൃണീ(𑌟𑍂) മാ(𑌖) ഹാ(𑌣) ഇ(𑌶)। പാന്താ(𑌕𑌾) മാഈ(𑌟𑌾) യാ(𑌤)। പൂരൂസ്പൃ(𑌟𑌿𑌟𑍍) ഹാ(𑌖) ഔഹോവാ(𑌶𑌿)। ഉഊ(𑌖𑌾)പാ(𑌶) ॥ 2॥ ആതേദാ(𑌖𑌿) ക്ഷാം(𑌶) മായോഭൂ(𑌖𑌿) വം(𑌣) । വൻഹിമദ്യാവൃണി(𑌫𑍂) മഹോ(𑌖𑌾) ഹാഇ(𑌶𑌾)। പാന്താ(𑌟𑌾) മാ(𑌤) ഈ(𑌟) യാ(𑌤) പൂ(𑌟𑌟𑍍) രൂ(𑌖) ഔഹോവാ(𑌶𑌿)। സ്പൃ(𑌖) ഹം(𑌶) ॥ 3॥ ആതേദക്ഷമ്മയോ(𑌫𑍂) ഭുവാം(𑌖𑌾) ഹാഇ(𑌶𑌾)।വൻഹിമദ്യാവൃണീ(𑌫𑍂) മഹോ(𑌖𑌾) ഹാഇ(𑌶𑌾)। പാന്താ(𑌯𑌾) മാ(𑌟) പൂരൂ(𑌕𑌾) സ്പൃഹാമീഴാ(𑌟𑍀) ഭാ(𑌖𑌣𑍍) ।ഓ(𑌪) ഇഴാ(𑌶𑌾) ॥ 4॥
#End of Mantra Sets -- subsection_581 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_582 ## DO NOT EDIT
അധ്വ൪യോ(𑌪𑌿) ആ(𑌣)। ദ്രിഭാഇസ്സൂ(𑌭𑍀) താം(𑌤) സോമം(𑌕𑌾) പാ(𑌖) വീ(𑌣)।ത്രാആ(𑌯𑌾) നായാ(𑌟𑌾)। പുനാ(𑌟𑌾) ഹീന്ദ്രാ(𑌖𑌾) ഔഹോവാ(𑌶𑌿)।യാപാതാ(𑌟𑌿) വേ(𑌖) ॥ 5॥ അധ്വ൪യോ(𑌷𑌿) ഔഹോഅദ്രീഭീഃ(𑌤𑍁)। സൂ(𑌚) തമൗ(𑌟𑌾) ഹോ(𑌤) വാ(𑌤) ഇ(𑌶) സോമം(𑌕𑌾) പാ(𑌖) വീ(𑌣)।ഓഇത്രായാ(𑌯𑍀) നായാ(𑌟𑌾)। പുനാഹാ(𑌟𑌿𑌟𑍍) ഇന്ദ്രാ(𑌖𑌾) ഔഹോവാ(𑌶𑌿)। ഏ(𑌤𑌚𑍍) യാ(𑌕) പാതാ(𑌟𑌾) വേ(𑌖) ॥ 6॥
#End of Mantra Sets -- subsection_582 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_583 ## DO NOT EDIT
തരത്സമാ(𑌤𑍀) ന്ദീ(𑌤) ധാവാ(𑌯𑌾) താ(𑌟) ഇ(𑌶)। ധാരാ(𑌟𑌾) സൂ(𑌖) താ(𑌣)। സ്യാന്ധാ(𑌟𑌾𑌟𑍍) സാ(𑌖) ഔഹോവാ(𑌶𑌿)। താരത്സമന്ദീധാ(𑌕𑍁) വതീ(𑌖𑍀) ॥ 7॥
#End of Mantra Sets -- subsection_583 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_584 ## DO NOT EDIT
ആപവസ്വാ(𑌤𑍀)। സാ(𑌚) ഹസ്രിണാം(𑌟𑌿) ഹുവാ(𑌟𑌾) ഇഹുവാ(𑌟𑌿) ഹോ(𑌚) ഇ(𑌶)। രയിം(𑌕𑌾) സോമാ(𑌕𑌾) സുവീ൪യാം(𑌟𑌿) ഹുവാ(𑌟𑌾) ഇഹുവാ(𑌟𑌿) ഹോ(𑌚) ഇ(𑌶)। അസ്മൈ(𑌥𑌾) ശ്രവാംസിധാ(𑌕𑍀) രായാ(𑌟𑌾) ഹുവാ(𑌟𑌾) ഇഹുവാ(𑌟𑌿) ഹോ(𑌟𑌟𑍍) യാ(𑌖) ഔഹോവാ(𑌶𑌿)। ഊ(𑌖) പാ(𑌶) ॥ 8॥
#End of Mantra Sets -- subsection_584 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_585 ## DO NOT EDIT
ആനുപ്രത്നാ(𑌷𑍀) സആയാ(𑌤𑌿) വാഃ(𑌤)। പാദന്നവീ(𑌷𑍀) യോഅക്രമൂഃ(𑌚𑍀)। രൂചേജനാന്താ(𑌪𑍁) സൂ(𑌶) ഹിമ്മാഏ(𑌭𑌿)। രീ(𑌖) യം(𑌶) ॥ 9॥
#End of Mantra Sets -- subsection_585 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_586 ## DO NOT EDIT
ആ൪ഷാ(𑌚𑌾) ഇഹാ(𑌶𑌾)।സോമാദ്യുമാ(𑌟𑍀) ക്താമാ(𑌚𑌾) ഇഹാ(𑌶𑌾)। ആഭാ(𑌚𑌾) ഇ(𑌶) ഇഹാ(𑌚𑌾)। ദ്രോണാനിരോ(𑌟𑍀𑌚𑍍) രൂ(𑌕) വാ(𑌚) ദിഹാ(𑌶𑌾)। സീ(𑌕) ദാ(𑌚) നിഹാ(𑌶𑌾)। യോനൗവനാ(𑌟𑍀𑌚𑍍) ഇ(𑌶) ഷൂവാ(𑌚𑌾) ഇഹാ(𑌶𑌾) ॥ 10॥ ആ൪ഷാ(𑌕𑌾) ഹാ(𑌤) ബു(𑌶) । സോമദ്യുമക്തമോ(𑌷𑍂) അഭിദ്രോ(𑌟𑌿) ണാ(𑌤) നിരോഔ(𑌭𑌿) ഹോ(𑌤) രൂവാ(𑌟𑌾) ത്സീദാഉവാ(𑌤𑍀) ।യോനൗവാ(𑌪𑌿) നേ(𑌶) ഹിമ്മാഏ(𑌭𑌿)। ഷൂ(𑌖) വാ(𑌶) ॥ 11॥ അ൪ഷാസോമാദ്യുമാ(𑌫𑍂) ക്തമോ(𑌖𑌾) അ൪ഷാസോമാ(𑌶𑍀) । ദ്യുമക്തമോ(𑌕𑍀) അഭിദ്രോ(𑌕𑌿) ണാ(𑌟) ഹാ(𑌤) ഹാ(𑌤) ഇ(𑌶)। നീരോ(𑌚𑌾) രൂവത്സാ(𑌕𑌿) ഇദന്യോനൗ(𑌟𑍀) ഹാ(𑌤) ഹാ(𑌤) ഇ(𑌶)। വാനാഇഷു(𑌟𑍀) വാ(𑌖𑌣𑍍)। ഓ(𑌪) ഇഴാ(𑌶𑌾)॥12॥
#End of Mantra Sets -- subsection_586 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_587 ## DO NOT EDIT
വൃഷാസോമാ(𑌤𑍀)। ദ്യൂമം(𑌚𑌾) ആ(𑌯) സാ(𑌟) ഇ(𑌶) । വൃഷാദാഇവോ(𑌟𑍁) ഹാ(𑌤) ഇ(𑌶)  വാ൪ഷാ(𑌕𑌾) വ്രാ(𑌖) താഃ(𑌣) ।വൃഷാധ൪മാ(𑌕𑍀) ഇ(𑌟) യാ(𑌤)। ണാഇദ(𑌕𑌿) ദ്രിഷാഇഴാ(𑌟𑍀) ഭാ(𑌖𑌣𑍍)। ഓ(𑌪) ഇഴാ(𑌶𑌾)॥ 13॥
#End of Mantra Sets -- subsection_587 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_588 ## DO NOT EDIT
ഇഷേപവാ(𑌤𑍀) ।സ്വധാരയൗ(𑌕𑍀) ഹോവാഹാ(𑌖𑌿) ഔഹോവാ(𑌶𑌿)। മൃജ്യമാനോ(𑌕𑍀) മനീഷീഭീഃ(𑌟𑍀𑌖𑍍) । ഇന്ദോ(𑌚𑌾) രൂ(𑌕) ചാ(𑌫) ഭിഗാഔ(𑌶𑌿) ഹോവാഹാ(𑌖𑌿) ഔഹോവാ(𑌶𑌿। 𑌉𑌪𑌈(𑌕𑌿) ഹീ(𑌖) ॥ 14॥
#End of Mantra Sets -- subsection_588 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_589 ## DO NOT EDIT
മന്ദ്രയാസോ(𑌤𑍀) । മാധാരയാ(𑌷𑍀) വൃഷപാ(𑌟𑌿) വാ(𑌤𑌚𑍍)। സ്വാ(𑌕) ദാഇവാ(𑌟𑌿) യൂഃ(𑌤) । അവ്യാവാ(𑌟𑌿𑌟𑍍) രാ(𑌖) ഔഹോവാ(𑌶𑌿) । ഭിരസ്മയൂഃ(𑌤𑍀𑌚𑍍)॥ 15॥
#End of Mantra Sets -- subsection_589 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_590 ## DO NOT EDIT
ആയാ(𑌣𑌾𑌫𑍍) സോ(𑌖) മസൂകൃത്യയാ(𑌶𑍁) । മാഹാൻസന്നാഭ്യവാ(𑌟𑍂) ൪ദ്ധാ(𑌖) ഥാഃ(𑌣)। മാ(𑌯) ന്ദാ(𑌟) നാ(𑌯) ഈ(𑌟) ദ്വൃഷായാ(𑌖𑌿) ।സാ(𑌤𑍍𑌰) ഇ(𑌶) ॥ 16॥
#End of Mantra Sets -- subsection_590 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_591 ## DO NOT EDIT
ആ(𑌖) ബുഹൗഹോവാഹാ(𑌷𑍁) അയാവിചാ(𑌶𑍀)। ൪ഷണാഇ൪ഹാ(𑌟𑍀) ഇതാഃ(𑌖𑌾)। ആ(𑌖) ബുഹൗഹോവാഹാ(𑌷𑍁) ഇപവമാനാഃ(𑌶𑍁)। സാചാഇതാ(𑌟𑍀) താ(𑌖) ഇ(𑌶)। ആ(𑌖) ബുഹൗഹോവാഹാ(𑌷𑍁) ഇഹിന്വാനയാ(𑌶𑍁) । പിയൗ(𑌟𑌾) ഹൗഹാഹോ(𑌖𑌿) ബാ(𑌪𑍍𑌲) ബൃഹാ(𑌪𑍍𑌲𑌾) ത്। ഹാഇ(𑌶𑌾) ॥ 17॥
#End of Mantra Sets -- subsection_591 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_592 ## DO NOT EDIT
പ്രണഇന്ദോ(𑌫𑍀) ഐഹീഐഹീ(𑌖𑍀) യാ(𑌶) । മാഹേതുനഐ(𑌟𑍁) ഹീഐ(𑌟) ഹീ(𑌟) യാ(𑌤)। ഊ(𑌕) ൪മ്മിന്നബിഭ്ര(𑌷𑍀) ദ൪ഷസീഐ(𑌟𑍂) ഐഹീഐഹീ(𑌖𑍀) യാ(𑌶)। ആഭാഇദാ(𑌟𑍀𑌟𑍍) ഇവം(𑌖𑌾) ഔഹോവാ(𑌶𑌿)। ആയാ(𑌟𑌾) സ്യാഃ(𑌖)॥ 18॥ പ്രണഇന്ദോ(𑌫𑍀) ഇയാ(𑌖𑌾) ഈ(𑌖) യാ(𑌶)। മാഹേതുനഇയാ(𑌟𑍂) ഈ(𑌟) യാ(𑌤)। ഊ(𑌕) ൪മ്മിന്നബിഭ്ര(𑌷𑍀) ദ൪ഷസീയാ(𑌟𑍀) ഈ(𑌟) യാ(𑌤) । ആഭാഇദാ(𑌟𑍀) ഇവം(𑌖𑌾) ഔഹോവാ(𑌶𑌿) । ഏ(𑌤𑌚𑍍) ആ(𑌕) യാ(𑌟) സ്യാഃ(𑌖) ॥ 19॥
#End of Mantra Sets -- subsection_592 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_593 ## DO NOT EDIT
ഹോഈ(𑌖𑌾) യാ(𑌪𑍍𑌲) ഹോഈ(𑌖𑌾) യാഈയാഹാഇ(𑌶𑍁)। അപഘ്നാ(𑌟𑌿) ന്പാ(𑌖) ഹോഈ(𑌖𑌾) യാ(𑌪𑍍𑌲) ഹോഈ(𑌖𑌾) യാഈയാഹാഇ(𑌶𑍁)। വാതാഇമാ(𑌟𑍀𑌟𑍍) ൪ദ്ധാ(𑌖) ഔഹോവാ(𑌶𑌿) । അപസോ(𑌕𑌿) മോഅരാ(𑌟𑌿) വിണ്ണാഃ(𑌖𑌾) ഹോഈ(𑌖𑌾) യാ(𑌪𑍍𑌲) ഹോഈ(𑌖𑌾) യാഈയാഹാഇ(𑌶𑍁)। ഗച്ഛന്നാ(𑌟𑌿) ഇന്ദ്രാ(𑌖𑌾) ഹോഈ(𑌖𑌾) യാ(𑌪𑍍𑌲) ഹോഈ(𑌖𑌾) യാഈയാഹാഇ(𑌶𑍁)। സ്യാനാഇഷ്കാ(𑌟𑍀𑌟𑍍) ൪ക്താ(𑌖) ഔഹോവാ(𑌶𑌿) । ഈ(𑌖) ॥ 20॥
#End of Mantra Sets -- subsection_593 ## DO NOT EDIT
```

---

## OUTPUT FORMAT:
Return **ONLY** the fully annotated text preserving the `#Start of Mantra Sets` and `#End of Mantra Sets` tags. Do not wrap in conversational fluff or additional markdown tags.
