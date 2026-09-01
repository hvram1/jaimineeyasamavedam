# Visual Swara Extraction Prompt — Batch: Pavamanam_K2_sub562_569

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
page_0230.png, page_0231.png, page_0232.png, page_0233.png, page_0234.png, page_0235.png

---

## MASTER TEXT TO ANNOTATE:

```text
#Start of Mantra Sets -- subsection_562 ## DO NOT EDIT
പ്രസോമാ(𑌖𑌿) സാഃ(𑌣)। മദച്യൂ(𑌚𑌿) താഔ(𑌟𑌾) ഹോ(𑌤) വാ(𑌤) ഇശ്രവാ(𑌟𑌿) സാ(𑌖) ഇനാഃ(𑌣𑌾)। ഓഇമഘോനാം(𑌟𑍁) । സൂതാവാ(𑌟𑌿𑌟𑍍) ഇദാ(𑌖𑌾) ഔഹോവാ(𑌶𑌿) । ഥേഅക്രമൂഃ(𑌖𑍀) ॥ 1॥ പ്രസോമാസാഃ(𑌤𑍀)। വാഇപാശ്ചീ(𑌕𑍀) താ(𑌶) ആ(𑌚) പോ(𑌯) നായാ(𑌟𑌾) ന്താഊ൪മയോ(𑌕𑍀) വാ(𑌚) നാ(𑌯) നിമാ(𑌟𑌾) ഓഔ(𑌕𑌾) ഹോ(𑌤)। ഹിഷാഈ(𑌚𑌿) വാഇഴാ(𑌟𑌿) ഭാ(𑌖𑌣𑍍) । ഓ(𑌪) ഇഴാ(𑌶𑌾) ॥2॥
#End of Mantra Sets -- subsection_562 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_563 ## DO NOT EDIT
പവസ്വേന്ദോ(𑌫𑍀) വൃഷാ(𑌶𑌾) സുതാഃ(𑌕𑌾)। കൃധീനോയശസോ(𑌷𑍁) ജനാഏ(𑌪𑌿) വാഇശ്വായാപാ(𑌶𑍁)। ദ്വാ(𑌟) ഇഷാ(𑌖𑌾) ഔഹോവാ(𑌶𑌿)। ജാ(𑌖) ഹി(𑌶) ॥3॥ വൃഷാഹിയാ(𑌤𑍀)। സിഭാനൂ(𑌭𑌿) നാ(𑌤)।ദ്യുമന്തത്വാഹവാ(𑌯𑍂) മാഹാ(𑌪𑌾) ഇപാവാ(𑌤𑌿)। മാനാസുവോ(𑌟𑍀) ഓ(𑌪) ബാ(𑌶)। ദൃ(𑌖) ശം(𑌶) ॥ 4॥ വൃഷാഹിയാ(𑌫𑍀) സിഭാനുനാ(𑌕𑍀)। ദ്യുമന്തന്ത്വാ(𑌟𑍀) ഹവാമഹേ(𑌕𑍀) ഹോവാ(𑌕𑌾) ഔ(𑌟) ഹോവാ(𑌕𑌾)। പാവമാ(𑌟𑌿) നാ(𑌚) സുവദൃശം(𑌟𑍀) ഹോവാ(𑌕𑌾) ഔ(𑌟) ഹോവാ(𑌕𑌾)। ഹൂവോ(𑌖𑌾) ഇഴാ(𑌪𑍍𑌲𑌾) ॥ 5॥
#End of Mantra Sets -- subsection_563 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_564 ## DO NOT EDIT
ഇന്ദൂ(𑌖𑌾) രൗഹോവാഹാഇപാവീ(𑌶𑍃)। ഷ്ടചാ(𑌟𑌾) ഈതനോ(𑌖𑌿) ഹാ(𑌣) ഇ(𑌶)। ഹാ(𑌕) ഹോഏ(𑌟𑌾) ഹോ(𑌟) വാ(𑌤)। പ്രീയാഃകവീ(𑌕𑍀) നാമ്മതിരോ(𑌪𑍀) ഹാ(𑌣) ഇ(𑌶)। ഹാ(𑌕) ഹോഏ(𑌟𑌾) ഹോ(𑌟) വാ(𑌤)। സൃജാ(𑌟𑌾) ദശ്വാം(𑌖𑌾) ഹാ(𑌣) ഇ(𑌶)।ഹാ(𑌕) ഹോഏ(𑌟𑌾) ഹോ(𑌟) വാ(𑌤)। രാ(𑌟) ഥാ(𑌖) ഔഹോവാ(𑌶𑌿)। ഈ(𑌖) വാ(𑌶)॥ 6॥ ഇന്ദുഃപവിഷ്ടചേ(𑌷𑍂) തനഃപ്രിയഃകവാ(𑌤𑍂) ഇ(𑌶)। ഹിം(𑌟) ഹിന്നാമ്മാ(𑌖𑌿) തീഃ(𑌣)। സൃജദാ(𑌪𑌿) ശ്വാം(𑌶) ।ഹിം(𑌟) ഹിം(𑌤) രാ(𑌟𑌟𑍍) ഥാ(𑌖) ഔഹോവാ(𑌶𑌿)।ഈ(𑌖) വാ(𑌶)॥ 7॥ ഇന്ദുഃപവിഷ്ടചേതനഃപ്രിയഃകവി(𑌷𑍋) നാമ്മതിംസൃജാ(𑌤𑍁) ദശ്വാം(𑌤𑌾)। ഓവാ(𑌕𑌾) ഓവാ(𑌕𑌾) രാ(𑌟𑌟𑍍) ഥാ(𑌖) ഔഹോവാ(𑌶𑌿) ।ഈ(𑌖) വാ(𑌶)॥ 8॥
#End of Mantra Sets -- subsection_564 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_565 ## DO NOT EDIT
അസൃക്ഷാതാ(𑌖𑍀) പ്രാ(𑌶) വാജീനാഃ(𑌪𑍍𑌲𑌿)। ഗവ്യാ(𑌟𑌾) സോമാ(𑌟𑌾) സോ(𑌤) ആശ്വയാ(𑌚𑌿)।ശുക്രാ(𑌟𑌾) സോവീ(𑌟𑌾) രയാ(𑌕𑌾𑌚𑍍) ശാ(𑌕) വഓ(𑌪𑌾) ഇഴാ(𑌶𑌾) ॥ 9॥ അസൃക്ഷതാപ്രാ(𑌤𑍁) വാജീനാഃ(𑌤𑌿)। ഗവ്യാസോമാസോ(𑌷𑍁) ആശ്വയാ(𑌟𑌿) ഹോ(𑌚) ഇ(𑌶)। ശുക്രാ(𑌤𑌾) സോവാ(𑌟𑌾) ഹോ(𑌚) ഇ(𑌶)।രാ(𑌕) യാശാ(𑌟𑌾𑌟𑍍) വാ(𑌖) ഔഹോവാ(𑌶𑌿)। ഗ്വാ(𑌖) ഭീഃ(𑌶) ॥ 10॥ അസൃക്ഷത(𑌷𑍀) പ്രവാജിനഏ(𑌖𑍁) ഗവ്യാസോമാ(𑌶𑍀)। സോ(𑌤) ആശ്വാ(𑌪𑌾) യാ(𑌶)। ശുക്രാ(𑌟𑌾) സോ(𑌖) വീ(𑌣)।രാ(𑌕) യോ(𑌪) ബാ(𑌪𑍍𑌲) ശാവോ(𑌪𑍍𑌲𑌾)। ഹാഇ(𑌶𑌾) ॥ 11॥
#End of Mantra Sets -- subsection_565 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_566 ## DO NOT EDIT
പാവാസ്വാദേ(𑌤𑍀)। വയാ(𑌤𑌾) വാ(𑌟) യാ(𑌖) ഔഹോവാ(𑌶𑌿)। യൂ(𑌖) ഷാഗാഇന്ദ്രംഗച്ഛാ(𑌶𑍂)। തുതാ(𑌤𑌾) ഇതു(𑌟𑌾) താ(𑌖) ഔഹോവാ(𑌶𑌿)। മാ(𑌖) ദാഃ(𑌪𑍍𑌲)। വായൂം(𑌟𑌾𑌚𑍍) ഹോ(𑌯) ആ(𑌟) രോ(𑌤)। ഹധാ(𑌤𑌾) ഹാ(𑌟) ധാ(𑌖) ഔഹോവാ(𑌶𑌿)। ൪മ്മാ(𑌖) ണാ(𑌶) ॥ 12॥ പവസ്വദേവാ(𑌫𑍁) ഐഹിഐഹീ(𑌖𑍀) യാ(𑌶)। ആയുഷാഗൈ(𑌟𑍀) ഹീഐ(𑌟𑌾) ഹീ(𑌟) യാ(𑌤)।ഇന്ദ്രംഗച്ഛ(𑌷𑍀) ന്തുതേമദാഐ(𑌟𑍁) ഹീഐ(𑌟𑌾) ഹീ(𑌟) യാ(𑌤)। വായൂമാരോ(𑌕𑍀) ഓഹാ(𑌕𑌾) ധോ(𑌪) ബാ(𑌪𑍍𑌲) ൪മ്മാണോ(𑌪𑍍𑌲𑌾) ।ഹാഇ(𑌶𑌾) ॥ 13॥
#End of Mantra Sets -- subsection_566 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_567 ## DO NOT EDIT
പാവാ(𑌤𑌾)। മാനോഅജീ(𑌕𑍀) ജാ(𑌖) നാ(𑌣) ത്। ദീവാ(𑌚𑌾) ശ്ചിത്രാ(𑌚𑌾) ന്ന്യതാന്യതൂം(𑌶𑍀) । ജ്യോതീ൪വൈ(𑌕𑌿) ശ്വാനാ(𑌟𑌾) രാ(𑌖) ഔഹോവാ(𑌶𑌿)। ബൃ(𑌖) ഹാ(𑌶) ത്॥14॥ പവമാനാഃ(𑌤𑍀)। അജാഇജാ(𑌪𑍀) നാ(𑌶) ത്। ദീവാ(𑌚𑌾) ശ്ചിത്രാം(𑌟𑌾) ഹാ(𑌤) ഹാ(𑌤) ഇ(𑌶) നാത(𑌕𑌾) ന്യാ(𑌖) തൂം(𑌣) । ജ്യോ(𑌖) തീ(𑌶) ൪വാ(𑌖) ഇശ്വാ(𑌣𑌾)। നരോ(𑌪𑍍𑌲𑌾) ബാബൃഹാ(𑌪𑍍𑌲𑌿) ത്। ഹാഇ(𑌶𑌾) ॥ 15॥
#End of Mantra Sets -- subsection_567 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_568 ## DO NOT EDIT
പാരീ(𑌤𑌾) । സ്വാനാസഇന്ദവോ(𑌷𑍂) മദായാ(𑌚𑌿) ബ൪ഹണാ(𑌟𑌿) ഗിരാ(𑌖𑌾) മധോ(𑌖𑌾) അ൪ഷാം(𑌤𑌾) । തീ(𑌕) ധോ(𑌪) ബാ(𑌪𑍍𑌲) രായോ(𑌪𑍍𑌲𑌾)। ഹാഇ(𑌶𑌾) ॥ 16॥ പ൪യേപാരീ(𑌤𑍀)। സ്വാനാസഇന്ദവാ(𑌷𑍂) ഉവാ(𑌟𑌾) ഹാഉവാ(𑌟𑌿) ഹോ(𑌕) വാ(𑌥) ഇയാ(𑌚𑌾)। മദായബ൪ഹണാ(𑌷𑍂) ഗിരാഉവാ(𑌟𑍀) ഹാഉവാ(𑌟𑌿) ഹോ(𑌕) വാ(𑌥) ഇയാ(𑌚𑌾)। മാധോഅ൪ഷന്തി(𑌷𑍁) ധാരയാഉവാ(𑌟𑍁) ഹാഉവാ(𑌟𑌿) ഹോ(𑌕) വാ(𑌥) ഇയോ(𑌟𑌾𑌟𑍍) യാ(𑌖) ഔഹോവാ(𑌶𑌿)। ഊ(𑌖)പാ(𑌶) ॥ 17॥ പാരീ(𑌫𑌾) സ്വാനാ(𑌣𑌾𑌫𑍍) സാ(𑌖) ഇന്ദവാഃ(𑌶𑌿)। മദാ(𑌟𑌾) യാ(𑌚) ബ൪ഹണാ(𑌚𑌿) ഗീ(𑌕) രാമധോആ(𑌟𑍀)൪ഷാ(𑌤) ൻ। ഊ൪മ്മിരിവാ(𑌟𑍀) ഈ(𑌟) യാ(𑌤)। തിധാ(𑌕𑌾𑌚𑍍) രാ(𑌕) യാഔ(𑌟𑌾) ഹോ(𑌖) ബാ(𑌪𑍍𑌲)। ഹോ(𑌪𑍍𑌲) ഇഴാ(𑌶𑌾) ॥ 18॥
#End of Mantra Sets -- subsection_568 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_569 ## DO NOT EDIT
പരിപ്രാസീ(𑌤𑍀)। ഷ്യാദത്കാ(𑌚𑌿) വീഃ(𑌟) । സിന്ധോരൂ൪മ്മാവാധീ(𑌯𑍂) ശ്രീതാഃ(𑌟𑌾)। കാരൂംബാ(𑌟𑌿𑌟𑍍) ഇഭ്രാ(𑌖𑌾) ഔഹോവാ(𑌶𑌿)। പൂരൂ(𑌤𑌾) സ്പൃഹാം(𑌟𑌾𑌖𑍍) ॥19॥
#End of Mantra Sets -- subsection_569 ## DO NOT EDIT
```

---

## OUTPUT FORMAT:
Return **ONLY** the fully annotated text preserving the `#Start of Mantra Sets` and `#End of Mantra Sets` tags. Do not wrap in conversational fluff or additional markdown tags.
