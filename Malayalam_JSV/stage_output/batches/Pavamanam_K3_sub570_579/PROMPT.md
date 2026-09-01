# Visual Swara Extraction Prompt — Batch: Pavamanam_K3_sub570_579

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
page_0236.png, page_0237.png, page_0238.png, page_0239.png, page_0240.png, page_0241.png, page_0242.png

---

## MASTER TEXT TO ANNOTATE:

```text
#Start of Mantra Sets -- subsection_570 ## DO NOT EDIT
ഇഹാ(𑌟𑌾𑌚𑍍) ഇ(𑌕) ഹാ(𑌶) ഉപോഷുജാതമാ(𑌟𑍂𑌚𑍍) പ്തൂ(𑌕) രാ(𑌚) മിഹാ(𑌶𑌾)। ഇഹാ(𑌟𑌾𑌚𑍍) ഇ(𑌕) ഹാ(𑌶) ഗോഭി൪ഭംഗമ്പരാ(𑌟𑍂𑌚𑍍) ഇഷ്കൃ(𑌕𑌾) താ(𑌚) മിഹാ(𑌶𑌾)। ഇഹാ(𑌟𑌾𑌚𑍍) ഇ(𑌕) ഹാ(𑌶) ഇന്ദുന്ദേവാഅയാ(𑌟𑍂𑌚𑍍) സീ(𑌕) ഷൂഃ(𑌚) ഇ(𑌕) ഹാ(𑌶)॥ 1॥ ആ(𑌷) ഉപോഷുജാതമാ(𑌟𑍂𑌚𑍍) പ്തു(𑌕) രാ(𑌚) മുപാ(𑌶𑌾)। ഗോഭാ(𑌟𑌾) ഇ൪ഹോ(𑌕𑌾𑌚𑍍) ഇ(𑌶) । ഭംഗമ്പരാ(𑌟𑍀) ഇഷ്കൃതാ(𑌚𑌿) മുപാ(𑌶𑌾)। ഇന്ദും(𑌟𑌾𑌚𑍍) ഹോ(𑌕) ഇ(𑌶)। ദേവാഅയാ(𑌟𑍀) സിഷുരാ(𑌤𑌿) ആഉവാ(𑌟𑌿)। ഉഊ(𑌖𑌾) പാ(𑌶)॥ 2॥ ഉപോഷ്വൗഹോഇ(𑌷𑍁) ജാതാം(𑌤𑌾) ।ആപ്തൂ(𑌟𑌾) രാ(𑌤) മൗഹോ(𑌟𑌾) വാ(𑌤) ഇഗോ(𑌚𑌾) ഭി൪ഭാ(𑌖𑌾) ഗം(𑌣) । ഓഇപാരീ(𑌯𑍀) ഷ്കൃതാം(𑌟𑌾) । ഇന്ദൂ(𑌟𑌾) ന്ദേവാ(𑌖𑌾) ഔഹോവാ(𑌶𑌿)। അയാസിഷൂഃ(𑌖𑍀) ॥ 3॥
#End of Mantra Sets -- subsection_570 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_571 ## DO NOT EDIT
പുനാനോയാ(𑌤𑍀)। ക്രാമീദാ(𑌖𑌿) ഭീഃ(𑌣)। വിശ്വാ(𑌟𑌾) മാ(𑌖) ൪ദ്ധോ(𑌶) വീച൪ഷാ(𑌖𑌿) ണാ(𑌣) ഇഃ(𑌶)।ശുംഭാ(𑌟𑌾) ന്താ(𑌖) വീ(𑌣)। പ്രാ(𑌟𑌟𑍍) ന്ധാ(𑌖) ഔഹോവാ(𑌶𑌿)। തീ(𑌖) ഭീഃ(𑌪𑍍𑌲)॥ 4॥
#End of Mantra Sets -- subsection_571 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_572 ## DO NOT EDIT
ആവിശൻകാലാ(𑌤𑍁) ശംസുതാഃ(𑌤𑌿)। വാഇശ്വാ(𑌕𑌿)  അ(𑌕) ൪ഷ(𑌥) ന്നാ(𑌕) ഭാഇശ്രായാ(𑌟𑍀) ഓ(𑌟) ഹാ(𑌤) ഓവാ(𑌟𑌾) ഓ(𑌖) ഹാ(𑌣)। ഇന്ദൂരാ(𑌟𑌿𑌟𑍍) ഇന്ദ്രാ(𑌖𑌾)  ഔഹോവാ(𑌶𑌿) യധീയതേ(𑌖𑍀) ॥ 5॥ ആവീ(𑌫𑌾) ശങ്കാ(𑌫𑌾) ലശം(𑌫𑌾𑌪𑍍𑌲𑍍) സുതോവാ(𑌖𑌿) ഇശ്വാ(𑌣𑌾)। അ൪ഷ(𑌥𑌾𑌚𑍍) ന്നാ(𑌕) ഭാഇശ്രായാ(𑌟𑍀) ഔഹോഔഹോ(𑌖𑍀) വാ(𑌶)।ഔ(𑌟) ഹോഔഹോ(𑌤𑌿𑌚𑍍) ഇന്ദൂ(𑌕𑌾) രാ(𑌯) ഇന്ദ്രാ(𑌟𑌾)। യാധീയാ(𑌟𑌿𑌟𑍍) താ(𑌖) ഔഹോവാ(𑌶𑌿)। ഊ(𑌖) പാ(𑌶) ॥ 6॥
#End of Mantra Sets -- subsection_572 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_573 ## DO NOT EDIT
അസ൪ജിരാ(𑌤𑍀)। ഥിയോയാ(𑌪𑌿) ഥാ(𑌶)। പാവിത്രേ(𑌚𑌿) ചാമുവോ(𑌟𑌿) സ്സൂ(𑌖) താഃ(𑌣)। കാ(𑌕) ൪ഷ്മന്ന്വാ(𑌟𑌾) ജീ(𑌤)। നിയാ(𑌚𑌾) ക്രാ(𑌕) മാഇദൗ(𑌪𑌿) ഹോബാ(𑌪𑍍𑌲𑌾)। ഹോ(𑌪𑍍𑌲) ഇഴാ(𑌶𑌾) ॥ 7॥
#End of Mantra Sets -- subsection_573 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_574 ## DO NOT EDIT
പ്രയദ്ധാ(𑌤𑌿) ബു(𑌶)। ഗാവോ(𑌥𑌾𑌚𑍍) നാഭൂ(𑌕𑌾) ൪ണാ(𑌯) യാ(𑌪) സ്ത്വേഷാ(𑌤𑌾)। അയാസോഅക്രാ(𑌕𑍁) മുഘ്നാ(𑌚𑌾) ന്താഃകാ(𑌟𑌾) ൪ഷ്ണാം(𑌤) । ആപാത്വചമൗ(𑌕𑍁) ഹോ(𑌟𑌟𑍍) ഹാ(𑌖) ഔഹോവാ(𑌶𑌿)। ഉഊ(𑌖𑌾) പാ(𑌶)॥ 8॥ പ്രയത്ഗാ(𑌕𑌿) വോ(𑌖) നഭൂ൪ണായാഃ(𑌶𑍀)। ത്വാഇഷാ(𑌚𑌿) അയാ(𑌕𑌾) സോ(𑌟) അക്രമൂ(𑌕𑌿) ഘ്നാ(𑌪) തോഹാ(𑌣𑌾) ഇ(𑌶)। കാ(𑌟𑌟𑍍) ൪ഷ്ണാ(𑌖) ഔഹോവാ(𑌶𑌿)। ആ(𑌥) പത്വാ(𑌟𑌾) ചാം(𑌖) ॥ 9॥
#End of Mantra Sets -- subsection_574 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_575 ## DO NOT EDIT
അപഘ്നൻഹോഇ(𑌷𑍁) പാവാ(𑌤𑌾)। സാ(𑌚) ഇമാ(𑌯𑌾) ൪ധാഃ(𑌟)। ക്രതൂവിത്സോ(𑌕𑍀𑌚𑍍) മാമാ(𑌕𑌾) ത്സാ(𑌯) രാഃ(𑌟)। നുദസ്വാ(𑌟𑌿𑌟𑍍) ദാ(𑌖) ഔഹോവാ(𑌶𑌿)। വയു(𑌕𑌾) ന്ജനാം(𑌟𑌾𑌖𑍍) ॥ 10॥
#End of Mantra Sets -- subsection_575 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_576 ## DO NOT EDIT
ഏആയാപവാ(𑌤𑍁)। സ്വധാ(𑌕𑌾) രായാ(𑌟𑌾𑌚𑍍) ഹാ(𑌯) ഉവാ(𑌟𑌾𑌚𑍍) ഊ(𑌖) പാ(𑌶)। യായാസൂ(𑌕𑌿) ൪യമരോ(𑌕𑌿) ചായാ(𑌟𑌾𑌚𑍍) ഹാ(𑌯) ഉവാ(𑌟𑌾𑌚𑍍)। ഊ(𑌖) പാ(𑌶)। ഹിന്വാനോമാനുഷാ(𑌟𑍂) ഇ൪ഹോ(𑌕𑌾𑌚𑍍) യാ(𑌕) പയാ(𑌤𑌾) ആഉവാ(𑌟𑌿)। ഉഊ(𑌖𑌾) പാ(𑌶) ॥ 11॥
#End of Mantra Sets -- subsection_576 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_577 ## DO NOT EDIT
സഹോ(𑌤𑌾) ഇപവസ്വാ(𑌶𑍀)। യായാ(𑌟𑌾) വീ(𑌕) ഥാഇ(𑌥𑌾) ന്ദ്രവൃത്രാ(𑌟𑌿) യാഹ(𑌕𑌾) ന്താ(𑌖) വാ(𑌣) ഇ(𑌶)।ഓവാ(𑌟𑌾) ഓ(𑌖) വാ(𑌣)। വബ്രീവാം(𑌟𑌿) സാം(𑌤)। മാഹീ(𑌕𑌾) രാ(𑌕) പാഔ(𑌟𑌾) ഹോ(𑌖) ബാ(𑌪𑍍𑌲)।ഹോ(𑌪𑍍𑌲) ഇഴാ(𑌶𑌾)॥12॥
#End of Mantra Sets -- subsection_577 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_578 ## DO NOT EDIT
അയാവീതീ(𑌤𑍀)। പാ(𑌕) രിസ്രവായസ്താ(𑌕𑍁) ഇന്ദോമാദാ(𑌕𑍀) ഇഷുവാ(𑌟𑌿) അവാഹാ(𑌭𑌿) ന്നാ(𑌤)। വാ(𑌤) തോ(𑌪) ബാ(𑌪𑍍𑌲)നാവോ(𑌪𑍍𑌲𑌾)। ഹാഇ(𑌶𑌾) ॥ 13॥ അയാവീ(𑌕𑌿) താഔ(𑌥𑌾) ഹോവാ(𑌟𑌾)। ഔഹോ(𑌥𑌾𑌚𑍍) ഔ(𑌕) ഹോ(𑌟𑌟𑍍) വാ(𑌖) ഔഹോവാ(𑌶𑌿)। പരി(𑌕𑌾) സ്രാവാ(𑌕𑌾) യസ്തഇന്ദോ(𑌕𑍀𑌚𑍍) ഔ(𑌕) ഹോവാ(𑌟𑌾) ।ഔഹോ(𑌥𑌾𑌚𑍍) ഔ(𑌕) ഹോ(𑌟𑌟𑍍) വാ(𑌖) ഔഹോവാ(𑌶𑌿)। മദേ(𑌟𑌾𑌚𑍍) ഷുവാ(𑌕𑌾) അവാ(𑌕𑌾) ഹാന്നാ(𑌕𑌾𑌚𑍍) ഔ(𑌕) ഹോവാ(𑌟𑌾)। ഔഹോ(𑌥𑌾𑌚𑍍) ഔ(𑌕) ഹോ(𑌟𑌟𑍍) വാ(𑌖) ഔഹോവാ(𑌶𑌿)। വതീ൪നവാ(𑌟𑍀𑌖𑍍) ॥ 14॥ ആയാ(𑌣𑌾) വീതാ(𑌣𑌾𑌫𑍍) ഇപാ(𑌖𑌾) രിസ്രവാ(𑌶𑌿)। യാസ്താ(𑌚𑌾) ഇന്ദോ(𑌥𑌾𑌚𑍍) മാദാ(𑌕𑌾) ഇഷൂ(𑌯𑌾) വാ(𑌟)। അവാഹാ(𑌭𑌿) ന്നാ(𑌤)।വതീ(𑌕𑌾) ൪ന്നാ(𑌕) വാഔ(𑌟𑌾) ഹോ(𑌖) ബാ(𑌪𑍍𑌲)।ഹോ(𑌪𑍍𑌲) ഇഴാ(𑌶𑌾) ॥15॥
#End of Mantra Sets -- subsection_578 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_579 ## DO NOT EDIT
പരിദ്യുക്ഷാം(𑌤𑍀) । ഓഇസനദ്രായീം(𑌟𑍂) । ഓഇഭരദ്വാജാം(𑌟𑍂) । ഓഇനോഅന്ധസാ(𑌪𑍂) സ്വാനോ(𑌖𑌾) അ൪ഷാ(𑌤𑌾)। വാ(𑌕) വോ(𑌪) ബാ(𑌪𑍍𑌲) ത്രായോ(𑌪𑍍𑌲𑌾)। ഹാഇ(𑌶𑌾) ॥16॥
#End of Mantra Sets -- subsection_579 ## DO NOT EDIT
```

---

## OUTPUT FORMAT:
Return **ONLY** the fully annotated text preserving the `#Start of Mantra Sets` and `#End of Mantra Sets` tags. Do not wrap in conversational fluff or additional markdown tags.
