# Visual Swara Extraction Prompt — Batch: Asaavi_K5_sub393_401

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
page_0153.png, page_0154.png, page_0155.png, page_0156.png

---

## MASTER TEXT TO ANNOTATE:

```text
#Start of Mantra Sets -- subsection_393 ## DO NOT EDIT
പ്രത്യസ്മൈപീബാ(𑌤𑍁) ഹാ(𑌤) ബു(𑌶) । ഓഇഷാ(𑌤𑌿) താ(𑌤) ഇ(𑌶) ഇ। വാഇശ്വാ(𑌕𑌿) നീ(𑌚𑌕𑍍) വാഇദൂഷേ(𑌟𑍀) ഹാ(𑌤) ഇഭാ(𑌤𑌾) രാ(𑌤) ആരാ(𑌟𑌾𑌚𑍍) ങ്ഗമാ(𑌕𑌾) യാജാ(𑌟𑌾) ഹാ(𑌤) ഗ്മായാ(𑌥𑌾) യപാശ്ചാ(𑌟𑌿𑌟𑍍) ദ്ദാ(𑌖) ഔഹോവാ(𑌶𑌿) । ഘ്വനേ(𑌟𑌾) നരാഃ(𑌖𑌾) ॥1॥ പ്രത്യസ്മൈപീ(𑌤𑍀) പീഷതാ(𑌤𑌿) ഇ(𑌶) । വാഇശ്വാ(𑌕𑌿𑌚𑍍) നീ(𑌕) വാഇദൂഷേ(𑌟𑌿) ഭാരാ(𑌟𑌾) ആരാ(𑌟𑌾𑌚𑍍) ങ്ഗാ(𑌕) മായജഗ്മായാ(𑌷𑍂) യപശ്ചാദ്ദഘ്വനാ(𑌟𑍂) ഹോ(𑌚) ഇ(𑌶) । നാരാഔ(𑌟𑌿) ഹോ(𑌖) ബാ(𑌪𑍍𑌲) । ഹോ(𑌪𑍍𑌲) ഇഴാ(𑌶𑌾)॥2॥
#End of Mantra Sets -- subsection_393 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_394 ## DO NOT EDIT
പ്രത്യസ്മൈപീപീ(𑌫𑍁) ഷതാ(𑌤𑌾) ഇവാ(𑌪𑌾) ഇശ്വാനിവിദുഷേ(𑌪𑍍𑌲𑍂) ഭാ(𑌙) രാ(𑌶) । അരംഗമായാജ(𑌫𑍂) ഗ്മയോ(𑌖𑌾) ഹായാപാശ്ചാദ്ദാഃ(𑌟𑍁) । ഘ്വാ(𑌕) നോ(𑌪) ബാ(𑌪𑍍𑌲) നാരോ(𑌪𑍍𑌲𑌾) ।ഹാഇ(𑌶𑌾) ॥3॥
#End of Mantra Sets -- subsection_394 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_395 ## DO NOT EDIT
ആനോവയോ(𑌷𑍀) വയശ്ശാ(𑌤𑌿) യാം(𑌤) । മാഹാന്തംഗഹ്വരാ(𑌖𑍂) ഇഷ്ഠാം(𑌶𑌾) । മാഹാന്തമ്പൂ൪വീനാ(𑌖𑍂) ഇഷ്ഠാം(𑌣𑌾) । ഉഗ്രംവാ(𑌟𑌿) ചോഅപാവാ(𑌖𑍀) ।ധീഃ(𑌤𑍍𑌰) ॥4॥
#End of Mantra Sets -- subsection_395 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_396 ## DO NOT EDIT
ആത്വാരഥം(𑌷𑍀) യഥൗഹോ(𑌤𑌿) വാ(𑌤) । തായാ(𑌕𑌾) ഇസൂ(𑌖𑌾) മ്നാ(𑌣) । യാവ൪ക്തയാമസീ(𑌷𑍂) തുവികൂ(𑌟𑍁) ൪മീ(𑌟𑌚𑍍) മാ(𑌖) ൪ക്തീ(𑌣) । ഷഹാം(𑌕𑌾) മാഇന്ദ്രം(𑌕𑌿) ശാ(𑌖) വീ(𑌣) । ഷ്ഠാസാത്പാ(𑌟𑌿) തീം(𑌖𑌣𑍍) ।ഓ(𑌪) ഇഴാ(𑌶𑌾) ॥5॥ ആത്വാരഥംയഥോ(𑌫𑍂) തായാ(𑌖𑌾) ആത്വാരഥാം(𑌶𑍀) । യാഥോതായാ(𑌟𑍀) ഔഹോ(𑌖𑌾) വാ(𑌶) । ഈ(𑌖) ഹാ(𑌶) । സുമ്നായാ(𑌚𑌿) വാ(𑌕) ൪ക്തായാമസീയൗ(𑌕𑍁𑌚𑍍) ഹോ(𑌯) യൗ(𑌟) ഹോ(𑌖) വാ(𑌶) । ഈ(𑌖) ഹാ(𑌶) । തുവികു൪മീ(𑌚𑍀) മൃ(𑌕) താഇഷഹമൗ(𑌕𑍁𑌚𑍍) ഹോ(𑌯) യൗ(𑌟) ഹോ(𑌖) വാ(𑌶) ।ഈ(𑌖) ഹാ(𑌶) । ഇന്ദ്രംശവീ(𑌚𑍀) ഷ്ഠാസാത്പതിമൗ(𑌕𑍁𑌚𑍍) ഹോ(𑌯) യൗ(𑌟) ഹോ(𑌖) വാ(𑌶) । ഈ(𑌖) ഹാ(𑌶) ॥6॥
#End of Mantra Sets -- subsection_396 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_397 ## DO NOT EDIT
സപൂ൪വ്യോമഹോനാ(𑌤𑍂) മേ(𑌤) । വേനാഃക്രാ(𑌚𑌿) തൂ(𑌕) ഭാഇരാനാജേ(𑌟𑍁) ഹാ(𑌤) ഹാഔ(𑌟𑌾) ഹോ(𑌤) വാആ(𑌟𑌾) ഇഹീ(𑌤𑌾) । യസ്യാ(𑌕𑌾) ദ്വാരാ(𑌥𑌾) മാനൂഃപീതാ(𑌟𑍀) ഹാ(𑌤) ഹാഔ(𑌟𑌾) ഹോ(𑌤) വാആ(𑌟𑌾) ഇഹീ(𑌤𑌾) । ദാഇവാഇഷൂ(𑌟𑍁) ഹാ(𑌤) ഹാഔ(𑌟𑌾) ഹോ(𑌤) വാആ(𑌟𑌾) ഇഹീ(𑌤𑌾) । ധീയാ(𑌕𑌾) ആനാ(𑌟𑌾𑌟𑍍) ജാ(𑌖) ഔഹോവാ(𑌶𑌿) । മധൂ(𑌤𑌾) ശ്ച്യൂതാഃ(𑌟𑌾𑌖𑍍) ॥7॥
#End of Mantra Sets -- subsection_397 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_398 ## DO NOT EDIT
യദീവഹന്ത്യാശ(𑌷𑍂) വോയദ്യേയാദീ(𑌤𑍁) । ഓഇവഹന്തായാ(𑌯𑍂) ശാവാഃ(𑌟𑌾) । ഓഇഭ്രാജമാനാ(𑌷𑍂) രഥാഇഷൂ(𑌯𑍇) വാ(𑌟) । ഓഇപിബന്തോ(𑌷𑍁) മദീരാമ്മാ(𑌯𑍀) ധൂ(𑌟) ।ഓഇതത്രശ്രാവാം(𑌷𑍂) സിക്രാഉവാ(𑌕𑍀) ഓ(𑌪) ബാ(𑌪𑍍𑌲) ണ്വാതോ(𑌪𑍍𑌲𑌾) ।ഹാഇ(𑌶𑌾) ॥8॥
#End of Mantra Sets -- subsection_398 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_399 ## DO NOT EDIT
ത്യമുവോ(𑌷𑌿) അപ്രാഹാ(𑌖𑍀) ണം(𑌣) । ഗൃണീ(𑌕𑌾) ഷേശവാ(𑌕𑌿) സസ്പാതാഇമിന്ദ്രാ(𑌟𑍂) വാ(𑌖) ഇശ്വാ(𑌣𑌾) । സാഹം(𑌕𑌾) ഹോയേ(𑌪𑌾) നാരമോ(𑌤𑌿) ഇ(𑌶) । ശചാഇഷ്ഠാം(𑌪𑍀) വീ(𑌣) । ശ്വാവാ(𑌟𑌾) ഹോ(𑌖) ബാ(𑌪𑍍𑌲) ദാസാം(𑌪𑍍𑌲𑌾) ।ഹാഇ(𑌶𑌾)॥9॥
#End of Mantra Sets -- subsection_399 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_400 ## DO NOT EDIT
ഓ(𑌤) ഹാഇദധിക്രാ(𑌷𑍂) വിണ്ണോഅകാ൪ഷാമോ(𑌤𑍂) ഹാ(𑌤) ഇ(𑌶) । ഓ(𑌤) ഹാഇജിഷ്ണോ(𑌷𑍀) രശ്വസ്യവാജിനാ(𑌟𑍂) ഓഹാ(𑌚𑌾) ഇ(𑌶) । സുരാ(𑌕𑌾) ഭീനോ(𑌕𑌾) മുഖാകാ(𑌟𑌿) രാ(𑌤) ത്। പ്രണാ(𑌟𑌾𑌚𑍍) ഹോ(𑌯) ആയൂം(𑌟𑌾) ഹോ(𑌯) ഷീതാരാ(𑌟𑌿) ഇഷാ(𑌖𑌾𑌣𑍍) ത്। ഓ(𑌪) ഇഴാ(𑌶𑌾) ॥10॥
#End of Mantra Sets -- subsection_400 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_401 ## DO NOT EDIT
പൂരാം(𑌫𑌾) ഭിന്ദു൪യുവാ(𑌖𑍀) കവിഃ(𑌶𑌾) । ആമീതൗജാ(𑌕𑍀) ആജായാ(𑌟𑌿) താ(𑌤) । ആഇന്ദ്രോവിശ്വാ(𑌟𑍁) സ്യാക(𑌕𑌾) ൪മാ(𑌖) ണാഃ(𑌣) । ധ൪ക്താവാജ്രൗ(𑌕𑍀) വാഉവോ(𑌖𑌿) വാ(𑌶) । പുരൂഷ്ടു(𑌪𑍍𑌲𑌿) താഃ(𑌶) । ഹോ(𑌪𑍍𑌲) ഇഴാ(𑌶𑌾) ॥11॥
#End of Mantra Sets -- subsection_401 ## DO NOT EDIT
```

---

## OUTPUT FORMAT:
Return **ONLY** the fully annotated text preserving the `#Start of Mantra Sets` and `#End of Mantra Sets` tags. Do not wrap in conversational fluff or additional markdown tags.
