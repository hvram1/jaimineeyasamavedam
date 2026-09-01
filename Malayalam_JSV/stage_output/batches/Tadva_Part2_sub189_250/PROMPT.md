# Visual Swara Extraction Prompt — Batch: Tadva_Part2_sub189_250

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
page_0073.png, page_0074.png, page_0075.png, page_0076.png, page_0077.png, page_0078.png, page_0079.png, page_0080.png, page_0081.png, page_0082.png, page_0083.png, page_0084.png, page_0085.png, page_0086.png, page_0087.png, page_0088.png, page_0089.png, page_0090.png, page_0091.png, page_0092.png, page_0093.png, page_0094.png, page_0095.png, page_0096.png, page_0097.png, page_0098.png

---

## MASTER TEXT TO ANNOTATE:

```text
#Start of Mantra Sets -- subsection_189 ## DO NOT EDIT
അഭ്യേആഭീ(𑌤𑍀)   ।  പ്രാഗോ(𑌕𑌾)  പാതീ(𑌥𑌾)  ങ്ഗീരാഃ(𑌟𑌾)   ।  ഇന്ദ്രമ൪ച്ചായാഥാ(𑌯𑍂)  വിദാ(𑌪𑌾)  ഇസൂനൂം(𑌤𑌿) । ഓഇസത്യോ(𑌪𑍀) ഹാ(𑌣)  ഇ(𑌶) । സ്യാ(𑌟)  സാ(𑌖)  ഔഹോവാ(𑌶𑌿)  । പാ(𑌚) തീ(𑌟) മേ(𑌖) ॥11॥ അഭ്യേആഭീ(𑌤𑍀)   ।  പ്രഗോപതീ(𑌕𑍀)  ങ്ഗിരാഃ(𑌟𑌾)   ।  ഇന്ദ്രമ൪ച്ചാ(𑌟𑍀) യാ(𑌖)  ഥാ(𑌣)  । ഹിം(𑌟)  ഹിം(𑌤)  ഓ(𑌪)  ഈ(𑌣)  വീദാ(𑌣𑌾)  ഇസനും(𑌫𑌿) സാത്യാ(𑌫𑌾) സ്യാസാ(𑌤𑌾)    ।  ഹിം(𑌟)  ഹിം(𑌤)  ഓ(𑌪)  ബാ(𑌪𑍍𑌲)  പാതാ(𑌪𑍍𑌲𑌾)  ഇം(𑌶) । ഹാഇ(𑌶𑌾)॥12॥
#End of Mantra Sets -- subsection_189 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_190 ## DO NOT EDIT
ആഭീ(𑌫𑌾)  പ്രഗോ(𑌖𑌾)  പതീ(𑌖𑌾)  ങ്ഗിരാഃ(𑌶𑌾)   ।  ഇന്ദ്രമ൪ച്ച(𑌷𑍀) യഥാവിദാഏ(𑌟𑍁)   ।  സൂനുംസാത്യാ(𑌕𑍀)  ഓ(𑌪)  സ്യാ(𑌶)  സാ(𑌫) ത്പാതാഇം(𑌶𑌿)   ।  സൂനുംസാത്യാ(𑌕𑍀)  ഓ(𑌪)  സ്യാസോ(𑌪𑍍𑌲𑌾)  ബാ(𑌪𑍍𑌲) ത്പാതാ(𑌪𑍍𑌲𑌾)  ഇം(𑌶) ।  ഹാഇ(𑌶𑌾) ॥13॥
#End of Mantra Sets -- subsection_190 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_191 ## DO NOT EDIT
കയാനശ്ചീ(𑌤𑍀)  । ത്രാ(𑌤)  യാഭൂ(𑌪𑌾) വാ(𑌶) ത്। ഊ(𑌕)  താഇസദാവാ(𑌕𑍁)  ൪ധസ്സാ(𑌖𑌾) ഖാ(𑌣)   ।  കയാശാ(𑌟𑌿)  ചാ(𑌤)  ഇ(𑌶)   । ഷ്ഠാ(𑌪)  യാ(𑌶)  വാ(𑌖)  ൪തോ(𑌪𑍍𑌲) । ഹാഇ(𑌶𑌾)॥14॥ ഹോവാഇഹോവാഇ(𑌷𑍂) കയാനശ്ചീ(𑌤𑍀)  । ത്രാ(𑌤)  യാഭൂ(𑌪𑌾)  വാ(𑌶) ത്। ഹോവാഇഹോവാഇ(𑌷𑍂) ഊതീ(𑌚𑌾)  സ്സാദാ(𑌕𑌾𑌚𑍍)  വൃധാ(𑌕𑌾)  സ്സാ(𑌪)  ഖാ(𑌶) । ഹോവാഇഹോവാഇ(𑌷𑍂)  കയാ(𑌤𑌾)  ശചാ(𑌤𑌾) ഇ(𑌶)   ।  ഷ്ഠായാവാ(𑌟𑌿𑌟𑍍) ൪താ(𑌖) ഔഹോവാ(𑌶𑌿)   ।  ഊ(𑌖)  പാ(𑌶) ॥15॥
#End of Mantra Sets -- subsection_191 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_192 ## DO NOT EDIT
കാ(𑌣)  യാ(𑌫)  നശ്ചാ(𑌫𑌾)  ഇത്രാ(𑌖𑌾)  യാഭുവാ(𑌶𑌿) ത്।  ഊതീ(𑌕𑌾) സ്സാദാ(𑌕𑌾)  വൃധസ്സഖാഔ(𑌕𑍁)  ഹോഹാ(𑌤𑌾)  ഇകയാ(𑌟𑌿)  ശചാ(𑌤𑌾)  ഇ(𑌶) । ഷ്ഠയൗഹോ(𑌤𑌿)  ഹിമ്മാ(𑌟𑌾)  വാ(𑌟)  ൪തോ(𑌖) । ഹാ(𑌤𑍍𑌰)  ഇ(𑌶) ॥16॥ കാ(𑌣)  സ്ത്വാ(𑌫)  സത്യോ(𑌫𑌾)  മാ(𑌖)  ദാനാം(𑌶𑌾) ।  മംഹിഷ്ഠോ(𑌕𑌿) മത്സദ(𑌕𑍀)  ന്ധസാഔ(𑌕𑌿)  ഹോഹാ(𑌤𑌾)  ഇദൃഢാ(𑌟𑌿)  ചിദാ(𑌤𑌾) । രൂജൗഹോ(𑌤𑌿)  ഹിമ്മാ(𑌟𑌾)   ।  വാ(𑌟)  സോ(𑌖)  । ഹാ(𑌤𑍍𑌰)  ഇ(𑌶) ॥17॥ ആ(𑌣)  ഭീ(𑌫)  ഷൂണാ(𑌫𑌾)  സ്സാ(𑌖)  ഖീനാം(𑌶𑌾) । അവിതാ(𑌕𑌿) ജരാഇതൃ(𑌕𑍀)  ണാമാഔ(𑌕𑌿) ഹോഹാ(𑌤𑌾)  ഈശാതാം(𑌟𑌿)  ഭവാ(𑌤𑌾)   ।  സിയൗഹോ(𑌤𑌿)  ഹിമ്മാ(𑌟𑌾)   ।  താ(𑌟) യോ(𑌖)  ।ഹാ(𑌤𑍍𑌰)  ഇ(𑌶) ॥18॥
#End of Mantra Sets -- subsection_192 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_193 ## DO NOT EDIT
ത്യമൂവാഃ(𑌤𑌿)   ।  സത്രാ(𑌥𑌾) സാഹാം(𑌟𑌾) ।  വിശ്വാസുഗീരിഷൂ(𑌟𑍂) ആയാതാം(𑌟𑌿) । ആച്യാവാ(𑌟𑌿𑌟𑍍) യാ(𑌖)  ഔഹോവാ(𑌶𑌿) । സ്യൂ(𑌕) തയേ(𑌟𑌾𑌖𑍍)॥19॥ ത്യാ(𑌖)  മൂവസ്സത്രാസാഹമ്മോവാ(𑌶𑍃)   ।  വിശ്വാസു(𑌷𑌿) ഗീരിഷ്വായാ(𑌟𑍀) താം(𑌚) । ആച്യാവാ(𑌟𑌿)  യാ(𑌤) । സിയൗ(𑌟𑌾)  ഹോവാ(𑌖𑌾) ഹാ(𑌣) ഇ(𑌶) । താ(𑌖) യോ(𑌪𑍍𑌲) ।ഹാഇ(𑌶𑌾) ॥20॥
#End of Mantra Sets -- subsection_193 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_194 ## DO NOT EDIT
സാദാ(𑌤𑌾)   ।  സസ്പതാ(𑌚𑌿)  ഈമാ(𑌯𑌾)  ത്ഭൂതാ(𑌟𑌾)  ഉവോ(𑌖𑌾)  വാ(𑌶)   । പ്രായാ(𑌟𑌾)  ഉവോ(𑌖𑌾) വാ(𑌶)   ।  ആഇന്ദ്രാസ്യാകാ(𑌕𑍂)  മാ(𑌖)  യാം(𑌤𑍍𑌰) । സാനിമ്മേ(𑌚𑌿)  ധാമയാ(𑌟𑌿)  സിഷാം(𑌖𑌾) ॥21॥
#End of Mantra Sets -- subsection_194 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_195 ## DO NOT EDIT
ഹാവാപ്സൂദാ(𑌖𑍀) ക്ഷാ(𑌶)  ആപ്സൂദാ(𑌖𑌿)  ക്ഷാഃ(𑌣) । ഏതേ(𑌕𑌾)  പന്ഥാ(𑌥𑌾𑌚𑍍)  ആഥോദീവാഃ(𑌟𑍀)  । ഹാവാപ്സൂദാ(𑌖𑍀) ക്ഷാ(𑌶) ആപ്സൂദാ(𑌖𑌿)  ക്ഷാഃ(𑌣) ।  ഏഭി(𑌕𑌾) ൪വ്യാ(𑌥𑌚𑍍) ശ്വാമാഇരായാ(𑌟𑍁) ഹാഉതാശ്രോ(𑌖𑍀)  ഷാ(𑌣) ന്। തൂനോഭൂ(𑌟𑌿𑌟𑍍)  വാ(𑌖)  ഔഹോവാ(𑌶𑌿)  । ഈ(𑌖)  തി(𑌶)  ॥22॥
#End of Mantra Sets -- subsection_195 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_196 ## DO NOT EDIT
ഭദ്രംഭാ(𑌤𑌿) ദ്രാം(𑌤) ।  നാ(𑌕)  ആഭാ(𑌟𑌾)  രാ(𑌖)  ഇഷാമൂ൪ജം(𑌶𑍀) । ശാതാക്രാ(𑌟𑌿)  താ(𑌖)  ബൂയാദിന്ദ്രാമൃ(𑌶𑍁) । ഡാ(𑌟)  യാ(𑌖) ഔഹോവാ(𑌶𑌿)   ।  സീ(𑌖)  നഃ(𑌶) ॥23॥
#End of Mantra Sets -- subsection_196 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_197 ## DO NOT EDIT
അസ്തിസോമോഅയം(𑌷𑍂)  സുതോഅസ്തേആസ്തീ(𑌤𑍂)   । സോമോഅയംസുതഃ(𑌷𑍂) പിബന്ത്യസ്യാമാ(𑌫𑍁)  രുതോ(𑌖)  ഹാ(𑌣)  ഇ(𑌶)   । ഉതസ്വരാജോ(𑌪𑍁)  അശ്വാഇനോ(𑌪𑍍𑌲𑍀)।  ഹാഇ(𑌶𑌾) ॥24॥
#End of Mantra Sets -- subsection_197 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_198 ## DO NOT EDIT
ഈംഖ്യയന്തീഃ(𑌤𑍀)   ।  അപാ(𑌟𑌾)  സ്യൂവാഃ(𑌟𑌾)   ।  ആഇന്ദ്രൻജാ(𑌕𑍀𑌚𑍍) താമൂ(𑌚𑌾)  പാ(𑌯)  സാതാ(𑌟𑌾)  ഇ(𑌶)   ।  വ(𑌕) ന്വാനാ(𑌟𑌾) സാഃ(𑌤)   । സൂവീ൪യാ(𑌕𑌿)  ആഉവാ(𑌶𑌿)   ।  വൃധേ(𑌤𑌾𑌚𑍍) ॥1॥
#End of Mantra Sets -- subsection_198 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_199 ## DO NOT EDIT
നകിദേവാഃ(𑌤𑍀)   ।  ഈനാഇനീമാസാ(𑌟𑍂)   ഇ(𑌶)   മാസീ(𑌕𑌾)   യാ(𑌖) നക്യായോ(𑌶𑌿)     ।   പായാപയാമാസാ(𑌟𑍂)   ഇ(𑌶)        മാസീ(𑌕𑌾) യാ(𑌖)  മന്ദ്രശ്രുത്യം(𑌶𑍀) ।  ചാരാചരാമാസാ(𑌟𑍂)   ഇ(𑌶)      മാസീ(𑌖𑌾) യാ(𑌣)॥2॥
#End of Mantra Sets -- subsection_199 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_200 ## DO NOT EDIT
ദോഷോആഗാ(𑌤𑍀) ത്।  ബൃഹദ്ഗായ(𑌷𑍀) ദ്യുമത്ഗാ(𑌟𑌿) മാ(𑌤)   । അഥ(𑌚𑌾) ൪വണസ്തുഹീയൗ(𑌟𑍁)  ഹോ(𑌖)  ഇദേവാം(𑌤𑌿) । സാ(𑌕)  വോ(𑌪)  ബാ(𑌪𑍍𑌲)  താരാം(𑌪𑍍𑌲𑌾)  ।ഹാഇ(𑌶𑌾)॥3॥
#End of Mantra Sets -- subsection_200 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_201 ## DO NOT EDIT
ഏഷോഊഷാഃ(𑌤𑍀)     ।   ആപൂ(𑌕𑌾)   ൪വ്യുവ്യൂച്ഛതീ(𑌕𑍀)   ഹോവാ(𑌟𑌾)  ഹാ(𑌤)  ഇ(𑌶)     ।   പ്രീയാദാ(𑌟𑌿)   ഇവാ(𑌖𑌾)   സ്തുഷാ(𑌖𑌾)   ഇവാമാ(𑌤𑌿)     । ശ്വീ(𑌕)   നോ(𑌪)   ബാ(𑌪𑍍𑌲)   ബൃഹാ(𑌪𑍍𑌲𑌾) ത്। ഹാഇ(𑌶𑌾) ॥4॥
#End of Mantra Sets -- subsection_201 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_202 ## DO NOT EDIT
ഇന്ദ്രോദധീചോ(𑌷𑍁) അസ്ഥഭിരീയാ(𑌟𑍁) ഈ(𑌟)  യാ(𑌤)  । വൃത്രാണ്യ(𑌷𑌿) പ്രതിഷ്കൃതഇയാ(𑌟𑍂) ഈ(𑌟) യാ(𑌤)। ജഘാനന(𑌷𑍀) വതീ൪നവഇയാ(𑌟𑍂) ഈ(𑌟) യാ(𑌖) ഔഹോവാ(𑌶𑌿)। ഊ(𑌖) പാ(𑌶)॥5॥ ഇന്ദ്രോദധാ(𑌤𑍀)  ഇചോഅസ്ഥാ(𑌖𑍀) ഭീഃ(𑌣) । വൃത്രാണ്യപ്രാ(𑌕𑍀) തിഷ്കൃതാഃ(𑌚𑌿)  । ജഘാനാ(𑌟𑌿) നാ(𑌤) । വതീ(𑌕𑌾𑌚𑍍)  ൪ന്നാ(𑌕)  വാഔ(𑌟𑌾) ഹോ(𑌖) ബാ(𑌪𑍍𑌲) । ഹോ(𑌪𑍍𑌲) ഇഴാ(𑌶𑌾)॥6॥
#End of Mantra Sets -- subsection_202 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_203 ## DO NOT EDIT
ഇന്ദ്രേഹിമാ(𑌤𑍀)  ഹാ(𑌤)  ബു(𑌶)   ।  സ്തീയാന്ധാ(𑌪𑌿)  സാഃ(𑌶)   । വാഇശ്വേ(𑌚𑌿)  ഭിസ്സോ(𑌥𑌾)  ഹാ(𑌤) മാ(𑌕)  പ൪വാ(𑌖𑌾) ഭീഃ(𑌣)   । മഹം(𑌟𑌾)  ആ(𑌟)  ഭാ(𑌖)  ഔഹോവാ(𑌶𑌿)   । ഷ്ടിരോജാ(𑌟𑌿)  സാ(𑌖) ॥7॥
#End of Mantra Sets -- subsection_203 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_204 ## DO NOT EDIT
ആതൂ(𑌖𑌾)  ഔഹോ(𑌪𑍍𑌲𑌾)  ആതൂ(𑌖𑌾)  ഔഹോ(𑌪𑍍𑌲𑌾)   ।  നാഇന്ദ്രവൃത്രാ(𑌟𑍁)  ഹാ(𑌕𑌥𑍍)  ന്നസ്മാകാമാ(𑌕𑍀)  ൪ദ്ധാമാഗാ(𑌟𑌿)  ഹീ(𑌤)   ।  മാഹാ(𑌟𑌾) ന്മാഹീ(𑌟𑌾𑌚𑍍)  ഭീ(𑌕)  രോ(𑌪)  ബാ(𑌪𑍍𑌲)  താഇഭോ(𑌪𑍍𑌲𑌿)  ഹാഇ(𑌶𑌾)॥8॥
#End of Mantra Sets -- subsection_204 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_205 ## DO NOT EDIT
ഹാ(𑌫)  ഹാഉവാ(𑌤𑌿) ।  ഓജസ്തദ(𑌷𑍀) സ്യതിദ്വിഷേ(𑌕𑍀𑌖𑍍)।   ഹാ(𑌫) ഹാഉവാ(𑌤𑌿)  ।  ഊഭേയത്സാമ(𑌷𑍁) വ൪ക്തയാ(𑌕𑌿𑌖𑍍) ത്। ഹാ(𑌫)  ഹാഉവാ(𑌤𑌿) । ഇന്ദ്രാശ്ച൪മേ(𑌕𑍀𑌚𑍍) വാ(𑌕)  രോദാ(𑌟𑌾)  സീ(𑌖) ॥ 9॥ ഓജസ്തദാ(𑌫𑍀)  സ്യതിദ്വിഷാ(𑌕𑍀)  ഇ(𑌶)   ।  ഊഭേയത്സമവ(𑌷𑍂) ൪ക്തയാദാഇന്ദ്രാശ്ചാ(𑌟𑍂𑌟𑍍) ൪മ്മാ(𑌖)  ഔഹോവാ(𑌶𑌿)   ।  ഏ(𑌤𑌚𑍍)  വാരോദാ(𑌟𑍀)  സീ(𑌖) ॥10॥
#End of Mantra Sets -- subsection_205 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_206 ## DO NOT EDIT
ആയാ(𑌣𑌾)  മൂതാ(𑌣𑌾𑌫𑍍)  ഇസാ(𑌖𑌾)  മാതസാഇ(𑌶𑍀)   ।  കാപോതാഇവാ(𑌕𑍁)  ഗാ(𑌚)  ൪ഭാ(𑌯)  ധീം(𑌟) ।  വാചാ(𑌟𑌾)  സ്താചീ(𑌟𑌾𑌚𑍍)  ന്നാ(𑌕) ഓ(𑌪)  ബാ(𑌪𑍍𑌲)  ഹാസോ(𑌪𑍍𑌲𑌾) । ഹാഇ(𑌶𑌾) ॥11॥
#End of Mantra Sets -- subsection_206 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_207 ## DO NOT EDIT
വാതആവാതുഭാ(𑌤𑍂)  ഇഷജാം(𑌤𑌿) ।  ശം(𑌕)  ഭൂമയോ(𑌕𑌿𑌚𑍍) ഭൂനോ(𑌕𑌾)  ഹൃദാ(𑌪𑌾)  ഇഹാ(𑌪𑍍𑌲𑌾)  ഹാ(𑌙)  ഇ(𑌶)   ।  പ്രാനആയൂംഷി(𑌪𑍁)  താ(𑌶)  രിഷാദൗ(𑌪𑌿)  ഹോബാ(𑌪𑍍𑌲𑌾) । ഹോ(𑌪𑍍𑌲)  ഇഴാ(𑌶𑌾)  ॥ 12॥
#End of Mantra Sets -- subsection_207 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_208 ## DO NOT EDIT
യംരക്ഷന്തി(𑌷𑍀) പ്രചേതസാഃ(𑌤𑍀)   ।  വാരൂണോമിത്രോ(𑌷𑍁) അ൪യാ(𑌟𑌾)  മാ(𑌤)   ।  നാകാഇസ്സാ(𑌟𑍀)  ദാ(𑌤)   ।  ഹിമ്മാഇഭ്യാ(𑌟𑍀𑌟𑍍) താ(𑌖) ഔഹോവാ(𑌶𑌿)   ।  ജാ(𑌖)  നാഃ(𑌪𑍍𑌲) ॥1॥
#End of Mantra Sets -- subsection_208 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_209 ## DO NOT EDIT
ഗവ്യോഷുണോ(𑌷𑍀) യഥാപുരാ(𑌤𑍀)   ।  അശ്വയോ(𑌕𑌿) തരഥായാ(𑌕𑍀)  വാരീ(𑌕𑌾)  വസ്യാമഹോമാ(𑌟𑍁) ഹോനാ(𑌖𑌾) ഔഹോവാ(𑌶𑌿)   ।  ഊ(𑌖) പാ(𑌶) ॥2॥ ഗവ്യോഷുണോ(𑌷𑍀) യഥാപുരാ(𑌤𑍀) ഏ(𑌤)   ।  അശ്വയോ(𑌕𑌿) തരഥാ(𑌟𑌿) യാ(𑌕𑌥𑍍)  വാരീ(𑌟𑌾)  വാസ്യാമഹോമാഹോ(𑌟𑍂𑌟) നാ(𑌖)  ഔഹോവാ(𑌶𑌿)   । ഈ(𑌖)  ॥3॥
#End of Mantra Sets -- subsection_209 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_210 ## DO NOT EDIT
ഇമാസ്തയാ(𑌤𑍀)  । ന്ദ്രാപൃശ്നയോ(𑌕𑍀)  ഘൃതന്തൂ(𑌟𑌿)  ഹാ(𑌤)  ബുഹോ(𑌟𑌾)  ഹാ(𑌤)  ഹാ(𑌤)  ഇതയാ(𑌟𑌿)  ശാ(𑌖)  ഇരം(𑌣𑌾) ।  ഏനാ(𑌖𑌾)  മൃതാ(𑌤𑌾) । സ്യാ(𑌕)  പോ(𑌪)  ബാ(𑌪𑍍𑌲)  പ്യൂഷാ(𑌪𑍍𑌲𑌾) ഇ(𑌶)  ।ഹാഇ(𑌶𑌾) ॥4॥
#End of Mantra Sets -- subsection_210 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_211 ## DO NOT EDIT
അയാധിയാച(𑌷𑍁) ഗവ്യയാ(𑌤𑌿) ഏ(𑌤)   ।  പുരൂനാ(𑌕𑌿)  മൻപൂ(𑌖𑌾) രൂ(𑌣)  ।  ഷ്ടൂതൗ(𑌕𑌾)  വാ(𑌤𑌤𑍍)  । യത്സോമേസോമയാ(𑌤𑍂)   ।  യത്സോമേ(𑌟𑌿) സോമയോ(𑌪𑌿)  ബാ(𑌪𑍍𑌲) ഭൂവോ(𑌪𑍍𑌲𑌾) । ഹാഇ(𑌶𑌾)  ॥5॥
#End of Mantra Sets -- subsection_211 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_212 ## DO NOT EDIT
പാവകാനഈയാ(𑌤𑍂)   ।  സാരാ(𑌚𑌾)  സ്വാ(𑌯) തീ(𑌟)   ।  വാജേ(𑌚𑌾)  ഭി൪വാ(𑌥𑌾𑌚𑍍)  ജീനാ(𑌕𑌾)  ഇവാ(𑌯𑌾) തീ(𑌟)  ।  യജ്ഞാംവാ(𑌟𑌿𑌟𑍍)  ഷ്ടൂ(𑌖) ഔഹോവാ(𑌶𑌿)   ।  ധിയാ(𑌤𑌾)  വാ(𑌟) സൂഃ(𑌖)  ॥6॥
#End of Mantra Sets -- subsection_212 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_213 ## DO NOT EDIT
കഇമ്മുഹുവാ(𑌤𑍁)  ഹാ(𑌤) ഇ(𑌶) ।  നാ(𑌤𑌚𑍍)  ഹൂഷാ(𑌕𑌾)  ഇഷൂ(𑌯𑌾) വാ(𑌟)  । ആഇന്ദ്രം(𑌕𑌿)  സോമാ(𑌕𑌾)  സ്യാതാ൪പാ(𑌯𑌿)  യാ(𑌟)     ത്സനോ(𑌟𑌾) വസൂ(𑌟𑌾𑌚𑍍)  നീയാ(𑌕𑌾)  ഭാ(𑌯)  രാ(𑌟) ത്സനോ(𑌟𑌾)  വസൂ(𑌕𑌾)  നിയാ(𑌟𑌾) ഭരാ(𑌕𑌾)  ഉവാ(𑌤𑌾)   ।  ആഗഹ്യേഹീ(𑌷𑍀) തഇമേ(𑌟𑌿𑌖𑍍) ॥7॥
#End of Mantra Sets -- subsection_213 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_214 ## DO NOT EDIT
ആയാഹിസൂ(𑌤𑍀)   ।  ഷൂമാ(𑌚𑌾)  ഹാ(𑌯)  ഇതേ(𑌟𑌾𑌚𑍍)  ഷൂമാ(𑌕𑌾) ഹാ(𑌯)  ഇതേ(𑌟𑌾)   । ആഇന്ദ്രാ(𑌚𑌿) സോമം(𑌥𑌾) പിബാ(𑌕𑌾)  ആ(𑌯) ഇമാം(𑌟𑌾𑌚𑍍) പിബാ(𑌕𑌾)  ആ(𑌯) ഇമാം(𑌟𑌾)   । ഏദംബ(𑌕𑌿)  ൪ഹാഇസ്സാ(𑌕𑌿)  ദോമാ(𑌟𑌾)  മാ(𑌖𑌣𑍍)  ।  ഓ(𑌪)  ഇഴാ(𑌪𑍍𑌲𑌾) ॥8॥
#End of Mantra Sets -- subsection_214 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_215 ## DO NOT EDIT
മഹാഇത്രാ(𑌖𑍀) ഇണം(𑌣𑌾) ।  ആവാ(𑌟𑌾) രസ്തുദ്യുക്ഷാ(𑌕𑍀)  ൪മാ(𑌖) ഇത്രാ(𑌣𑌾)   । സ്യാ(𑌟)  ൪യമ്നാ(𑌟𑌾)   ദുരാ(𑌕𑌾) ധാ(𑌖) ൪ഷം(𑌣) । വാ(𑌕) രോ(𑌪) ബാ(𑌪𑍍𑌲) ണാസ്യോ(𑌪𑍍𑌲𑌾) । ഹാഇ(𑌶𑌾)॥9॥ മഹിത്രീണാ(𑌷𑍀) മവരസ്തു(𑌤𑍀)  ഏ(𑌤)   ।  ദ്യുക്ഷ൪മ്മിത്ര(𑌷𑍀) സ്യാ൪യമ്ണാ(𑌕𑌿) ദുരാധാ(𑌟𑌿)  ൪ഷാം(𑌤) ।  വാരൗഹോവാ(𑌕𑍀)  ഹിമ്മാ(𑌟𑌾)  ണാസ്യോ(𑌟𑌾𑌟𑍍) യാ(𑌖) ഔഹോവാ(𑌶𑌿)  । ഹാ(𑌤)  ഓവാ(𑌟𑌾)  ഓവാ(𑌟𑌾𑌖𑍍) ॥10॥
#End of Mantra Sets -- subsection_215 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_216 ## DO NOT EDIT
ത്വാവാതോ(𑌕𑌿)  ഹാബുഹോ(𑌕𑌿)  ഓ(𑌚)  ഇ(𑌶)   ।  പുരോവസോ(𑌕𑍀) ഹാബുഹോ(𑌕𑌿)  ഓ(𑌚) ഇ(𑌶)   ।  വായമിന്ദ്രാ(𑌕𑍀) ഹാബുഹോ(𑌕𑌿) ഓ(𑌚) ഇ(𑌶)   । പ്രണേതൠ(𑌕𑍀)  ഹാബുഹോ(𑌕𑌿)  ഓ(𑌚)  ഇ(𑌶)  । സ്മസിസ്ഥാതൠ(𑌕𑍁)  ഹാബുഹോ(𑌕𑌿)  ഓ(𑌚) ഇ(𑌶)   ।  ഹാരീണാം(𑌕𑌿)  ഹാബുഹോ(𑌕𑌿) । ഓ(𑌪)  ഇഴാ(𑌶𑌾) ॥11॥
#End of Mantra Sets -- subsection_216 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_217 ## DO NOT EDIT
ഉത്വാമന്ദന്തുസോ(𑌤𑍂)  ഹോ(𑌤)  മാഃ(𑌤)   ।  കൃണൗഹോ(𑌕𑌿) ഷ്വാരൗഹോധോ(𑌕𑍀)  അദ്രിവാഃ(𑌚𑌿)   ।  ആ(𑌕𑌥𑍍)  വബ്രാ(𑌟𑌾) ഹ്മാ(𑌤)   । ദ്വിഷാ(𑌟𑌾)  ഹോ(𑌕)  വാ(𑌥)  ഔ(𑌟)  ഹോ(𑌯)  ഇജാ(𑌟𑌾𑌟𑍍)  ഹാ(𑌖)  ഔഹോവാ(𑌶𑌿)   ।  ഏ(𑌤)  യയൂഃ(𑌟𑌾𑌖𑍍) ॥1॥
#End of Mantra Sets -- subsection_217 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_218 ## DO NOT EDIT
ഗി൪വണഃപഹിന(𑌷𑍂) സ്സുതംഗി൪വണഃപാ(𑌤𑍂)  । ഹീനാസ്സുതാ(𑌟𑍀𑌚𑍍) മ്മാധോ(𑌕𑌾) ൪ധാരാ(𑌕𑌾)  ഭീരാഹോവാ(𑌕𑍀) ജ്യാസേ(𑌟𑌾)  ഹാഉവാ(𑌤𑌿) । ഇന്ദ്രത്വാ(𑌟𑌿) ദാ(𑌤) । താമാഇദ്യാ(𑌟𑍀𑌟𑍍)  ശാ(𑌖)  ഔഹോവാ(𑌶𑌿) । ഹാ(𑌚)  രിശ്രീഃ(𑌟𑌾𑌖𑍍) ॥2॥
#End of Mantra Sets -- subsection_218 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_219 ## DO NOT EDIT
സാദാ(𑌤𑌾)   ।  വഇന്ദ്രശ്ചകൃഷാ(𑌖𑍂)  താ(𑌶)   ।  ഉപോനുസാ(𑌤𑍀) സാപ൪യന്നദേ(𑌕𑍁)  വാഃ(𑌚) । ൠതാ(𑌣𑌾)  ശ്ശൂ(𑌫) രാ(𑌖)  ഇ(𑌶) ।ന്ദ്രാഃ(𑌤𑍍𑌰)॥3॥
#End of Mantra Sets -- subsection_219 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_220 ## DO NOT EDIT
ആത്വാവിശത്വിന്ദാ(𑌤𑍂) വാഃ(𑌤)   । സാമുദ്രമീ(𑌕𑍀)  വാസിന്ധാവാഃ(𑌕𑍀) സാമൂദ്രമീ(𑌕𑍀) വാ(𑌕)  സിന്ധാ(𑌟𑌾)  വാഃ(𑌤)  । നത്വാമിന്ദ്രാ(𑌷𑍀) തിരിച്യതേ(𑌕𑍀)   നത്വാ(𑌕𑌾) മാ(𑌟)  ഇന്ദ്രാ(𑌤𑌾) । തിരിച്യാ(𑌟𑌿)  താ(𑌖𑌣𑍍)   ഇ(𑌶)  ।ഓ(𑌪)  ഇഴാ(𑌶𑌾) ॥4॥
#End of Mantra Sets -- subsection_220 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_221 ## DO NOT EDIT
ഇന്ദ്രമിത്ഗാ(𑌤𑍀)   ।  ഥീനോബൃഹാ(𑌷𑍀) ദിന്ദ്രമാ(𑌟𑌿)  ൪കേ(𑌤𑌚𑍍)   ഭീ(𑌕) ര൪കീണാഃ(𑌚𑌿)   ।  ഇ(𑌕) ന്ദ്രംവാ(𑌟𑌾) ണീ(𑌤)     രാനൂ(𑌕𑌾)  ഷതാഇഴാ(𑌟𑍀) ഭാ(𑌖𑌣𑍍)  । ഓ(𑌪) ഇഴാ(𑌪𑍍𑌲𑌾) ॥5॥ ഇന്ദ്രാ(𑌫𑌾)   മിത്ഗാഥിനോ(𑌖𑍀)  ബൃഹാ(𑌶𑌾) ത്। ഇ(𑌕)  ന്ദ്രാമ൪കാഇഭീ(𑌕𑍁)  ര൪കീണാഃ(𑌟𑌿)   ।  ആഇന്ദ്രംവാണീ(𑌟𑍁) ൪ഹാ(𑌤)  ഹാ(𑌤)   । ആനൂ(𑌫𑌾)  ഷതാ(𑌪𑍍𑌲𑌾) ।ഹോ(𑌪𑍍𑌲) ഇഴാ(𑌶𑌾)  ॥6॥
#End of Mantra Sets -- subsection_221 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_222 ## DO NOT EDIT
ഇന്ദ്രഇഷേ(𑌷𑍀) ദദാതുനാ(𑌤𑍀) ഏ(𑌤)  । ൠഭുക്ഷാണാ(𑌕𑍀) മൃഭൂം(𑌖𑌾𑌣𑌫𑌪𑍍𑌲) രാ(𑌟)  യിം(𑌤) । വാ(𑌚)  ജീ(𑌥)  ദദാതൂ(𑌕𑌿)  വോ(𑌪)  ബാജാ(𑌪𑍍𑌲𑌾) ഇനാം(𑌪𑍍𑌲𑌾) । ഹാഇ(𑌶𑌾) ॥7॥ ഇന്ദ്രഇഷേ(𑌷𑍀) ദദാതുനഓ(𑌤𑍂)  ഹാ(𑌤)  ഇ(𑌶) ।  ൠ(𑌚)  ഭുക്ഷണാ(𑌟𑌿) മൃഭുംരാ(𑌖𑌿) യീം(𑌣) ।  വാജീദദാതുവാ(𑌤𑍂)   ।  വാ(𑌕)  ജീദദാ(𑌟𑌿)  തുവോ(𑌪𑌾) വാ(𑌪𑍍𑌲)  ജാഇനാം(𑌪𑍍𑌲𑌿) ।ഹാഇ(𑌶𑌾)॥8॥
#End of Mantra Sets -- subsection_222 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_223 ## DO NOT EDIT
ഇന്ദ്രോഅംഗാ(𑌤𑍀) । മാഹാത്ഭാ(𑌟𑌿)  യാം(𑌤) ।  ആഭീ(𑌕𑌾)  ഷാദ(𑌚𑌾) പാച്യുച്യാ(𑌟𑌿)  വാ(𑌖) ത്സഹാ(𑌖𑌾)  ഇസ്ഥിരാഃ(𑌤𑌿)   ।  വീ(𑌕)  ചോ(𑌪) ബാ൪ഷാണാ(𑌪𑍍𑌲𑌿)  ഇ(𑌶) । ൪ഹാഇ(𑌶𑌾)॥9॥
#End of Mantra Sets -- subsection_223 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_224 ## DO NOT EDIT
ഇമാഉത്വാ(𑌤𑍀)   ।  സൂതാ(𑌤𑌾)  ഇസൂതാഇ(𑌷𑍀) നക്ഷന്താ(𑌟𑌿)  ഇഗീ(𑌖𑌾)  ൪വാണോ(𑌪𑍍𑌲)  ഗാ(𑌖)  ഇരാഃ(𑌣𑌾)  ।  ഗാവോവാ(𑌭𑌿)  ത്സാ(𑌤𑌚𑍍) ന്നാ(𑌕)  ധോ(𑌪)  ബാനാ(𑌪𑍍𑌲𑌾)  വോ(𑌪𑍍𑌲)  ।ഹാഇ(𑌶𑌾)॥10॥ ഇന്ദ്രാനൂപൂ(𑌤𑍀)   ।  ഷാണാവാ(𑌟𑌿) യാം(𑌤) ।  സാഖ്യാ(𑌕𑌾) യസൂവസ്താ(𑌟𑍀)  യാ(𑌤)  ഇ(𑌶)   ।  ഹുവേ(𑌕𑌾)  മാവാ(𑌟𑌾𑌚𑍍)  ജാ(𑌕) സോ(𑌪)  ബാ(𑌪𑍍𑌲)  തായോ(𑌪𑍍𑌲𑌾)  । ഹാഇ(𑌶𑌾) ॥11॥
#End of Mantra Sets -- subsection_224 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_225 ## DO NOT EDIT
നക്യേനാകീ(𑌤𑍀) । ആ(𑌚) ഇന്ദ്രത്വദുത്വരാ(𑌚𑍂)  ന്നാ(𑌕) ജ്യായോ(𑌥𑌾)  അസ്താ(𑌪𑌾)  ഇവൃ(𑌶𑌾)  । ഹിം(𑌟)  ഹിന്ത്രാ(𑌖𑌾)  ഹ(𑌣) ന്। നക്യേ(𑌟𑌾)  വയ്യാ(𑌪𑌾) ഥാ। ഹിം(𑌪) ഹിം(𑌶) തൂ(𑌖) വാം(𑌪𑍍𑌲) । ഹാഇ(𑌶𑌾) ॥12॥
#End of Mantra Sets -- subsection_225 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_226 ## DO NOT EDIT
തരണിംവാഃ(𑌤𑍀)   ।  ജനാ(𑌟𑌾)  നാമം(𑌤) ।  ത്രാദംവാജാ(𑌟𑍀)  ഹാ(𑌤) സ്യാഗോ(𑌕𑌾)  മാ(𑌖)  താഃ(𑌣)   ।  സമാനാ(𑌟𑌿)  മൂ(𑌤) । പ്രശാംസിഷാഃ(𑌪𑍍𑌲𑍀) । ഹോ(𑌪𑍍𑌲) ഇഴാ(𑌶𑌾)  ॥1॥
#End of Mantra Sets -- subsection_226 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_227 ## DO NOT EDIT
അസൃഗ്രമാഇന്ദ്രാ(𑌤𑍂)  തേഗിരാഃ(𑌤𑌿)   ।  പ്രാതീ(𑌟𑌾)  ത്വാമൂ(𑌟𑌾) ദഹാ(𑌕𑌾)  സതാ(𑌶𑌾)   ।  സാജോ(𑌟𑌾)  ഷാവൃ(𑌟𑌾)  ഷഭാം(𑌕𑌾𑌚𑍍) പാതിമോ(𑌪𑌿)  ഇഴാ(𑌪𑍍𑌲𑌾) ॥2॥
#End of Mantra Sets -- subsection_227 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_228 ## DO NOT EDIT
സുനീഥോഘാ(𑌫𑍀) സമാ(𑌶𑌾)  ൪ക്ത്യാഃ(𑌕)   ।  യമ്മരൂതോ(𑌟𑍀𑌚𑍍) യമ(𑌚𑌾)  ൪യാമാ(𑌚𑌾)  മിത്രാഃപാ(𑌚𑌿)  ന്ത്യദ്രുഹാ(𑌟𑌿)  ഉഉവാ(𑌟𑌿𑌚𑍍) ഹാ(𑌯)  ഉവാ(𑌟𑌾)   ।  ആ(𑌥)  തിദ്വീഷാഃ(𑌟𑌿𑌖𑍍)॥3॥
#End of Mantra Sets -- subsection_228 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_229 ## DO NOT EDIT
ഔഹോവാഔഹോ(𑌖𑍁) വാ(𑌶)  ഓഹാ(𑌪𑍍𑌲𑌾)  ഇ(𑌶)  । യദ്വിഴാവീ(𑌖𑍀) ന്ദ്രായാ(𑌕𑌿)  സ്ഥീരാ(𑌫𑌾) ഇ(𑌶) । ഔഹോവാഔഹോ(𑌖𑍁) വാ(𑌶)  ഓഹാ(𑌪𑍍𑌲𑌾) ഇ(𑌶) । യത്പ൪ശാനേ(𑌖𑍁)  പാരാ(𑌕𑌾) ഭൃതം(𑌫𑌾) । ഔഹോവാഔഹോ(𑌖𑍁) വാ(𑌶) ഓഹാ(𑌪𑍍𑌲𑌾) ഇ(𑌶)  വസുസ്പാ൪ഹാ(𑌖𑍀)  ന്താദാ(𑌕𑌾) ഭാരാ(𑌫)  । ഔഹോവാഔഹോ(𑌖𑍁) വാ(𑌶)  ഓഹാ(𑌪𑍍𑌲𑌾) ഇ(𑌶)   । ഹോ(𑌪𑍍𑌲)  ഇഴാ(𑌶𑌾) ॥4॥
#End of Mantra Sets -- subsection_229 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_230 ## DO NOT EDIT
ശ്രൂതാം(𑌤𑌾) । വോവൃത്രഹന്തമം(𑌷𑍂) പ്രശദ്ധഞ്ചഋ(𑌕𑍁)  ഷാണാ(𑌟𑌾) ഇനാം(𑌤𑌾) ।  ആശാ(𑌕𑌾)  ഇഷാ(𑌟𑌾)  ഇരാ(𑌤𑌾)   ।  ധസേ(𑌕𑌾𑌚𑍍)  മാ(𑌕) ഹാഔ(𑌟𑌾)  ഹോ(𑌖)  ബാ(𑌪𑍍𑌲)   ।  ഹോ(𑌪𑍍𑌲)  ഇഴാ(𑌶𑌾)  ॥5॥
#End of Mantra Sets -- subsection_230 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_231 ## DO NOT EDIT
അരന്തഇന്ദ്ര(𑌷𑍂) ശ്രവസേ(𑌤𑌿) ഏ(𑌤)   ।  ഗമാ(𑌚𑌾) ഇ(𑌶) മാ(𑌥) ശൂരത്വാ(𑌕𑌿)  വതോ(𑌟𑌾)  ഹോവാ(𑌟𑌾)  ഹാ(𑌤)  ഇ(𑌶)   ।  ആരാം(𑌚𑌾)  ശാ(𑌯) ക്രാ(𑌟)  ഹോവാ(𑌟𑌾)  ഹാ(𑌤)  ഇ(𑌶)  । പാരേമാ(𑌟𑌿)  ണാ(𑌖𑌣𑍍)  ഇ(𑌶)   ।  ഓ(𑌪)  ഇഴാ(𑌪𑍍𑌲𑌾)  ॥6॥
#End of Mantra Sets -- subsection_231 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_232 ## DO NOT EDIT
ധാനാ(𑌫𑌾)  വന്തങ്കരാ(𑌖𑍀) മ്ഭിണം(𑌶𑌾) ।  ആപൂപവന്തമൂ(𑌯𑍂) ത്ഥീ(𑌪) നാം(𑌶) ।  ഇന്ദ്രാപ്രാ(𑌖𑌿) താ(ശ𑌪𑍍𑌲𑍍)   ഓ(𑌖)  ഹാ(𑌣) ഇ(𑌶)। ജുഷോബാ(𑌪𑍍𑌲𑌿)   സ്വാനോ(𑌪𑍍𑌲𑌾)  ।ഹാഇ(𑌶𑌾)॥7॥
#End of Mantra Sets -- subsection_232 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_233 ## DO NOT EDIT
അപാംഫേനേ(𑌷𑍀) നനമുചേഃ(𑌤𑍀)   ।  ശീരഇ(𑌚𑌿)  ന്ദ്രോദവാ(𑌟𑌿) ൪ക്താ(𑌖) യാഃ(𑌣)   ।  വാഇശ്വായാ(𑌟𑍀𑌟𑍍)  ദാ(𑌖)  ഔഹോവാ(𑌶𑌿)   । ജയാ(𑌤𑌾)  സ്പാ(𑌟) ൪ധാഃ(𑌖)॥8॥
#End of Mantra Sets -- subsection_233 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_234 ## DO NOT EDIT
ഇമേതയാ(𑌤𑍀)   ।  ന്ദ്രാസോമോ(𑌟𑌿)  ഹോവാ(𑌕𑌾)  ഹോ(𑌚)  ഇ(𑌶)    । സൂ(𑌕)  താസോയേ(𑌟𑌿)     ചാസോ(𑌕𑌾)  തൂ(𑌖)  വാഃ(𑌣)   ।  തേ(𑌖)  ഷാം(𑌪𑍍𑌲) ഹാ(𑌤)  ഹാ(𑌤)  ഇ(𑌶)  । മാത്സ്വപ്രഭൂ(𑌕𑍀)  ഓ(𑌪)  ബാ(𑌪𑍍𑌲)  വാസോ(𑌪𑍍𑌲𑌾) । ഹാഇ(𑌶𑌾)  ॥9॥ തുഭ്യാം(𑌤𑌾)  ഹാ(𑌤)  ബു(𑌶)   ।  സൂതാസസ്സോമാ(𑌷𑍁) സ്തീ൪ണാംബാ(𑌟𑌿) ൪ഹീ(𑌤)  വീഭാ(𑌟𑌾𑌚𑍍)  ഹോ(𑌯)   ഇവാ(𑌟𑌾)  സോ(𑌤)  ।  സ്തോതൃ(𑌪𑌾) ആ(𑌶)  ഭ്യാ(𑌟)  ഇന്ദ്രമൃ(𑌖𑌿)  ഔഹോവാ(𑌶𑌿)  । ഡാ(𑌖) യാ(𑌶) ॥10॥
#End of Mantra Sets -- subsection_234 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_235 ## DO NOT EDIT
ആവഇന്ദ്രാം(𑌤𑍀) ।  കൃവീംയഥാ(𑌷𑍀) വാജയാ(𑌟𑌿) ന്താ(𑌤𑌚𑍍)  ശ്ശാതാ(𑌚𑌾) ക്രാതും(𑌶𑌾) । മംഹിഷ്ഠാം(𑌟𑌿) സീ(𑌤)  । ഞ്ചായാ(𑌟𑌾)  ഉവാ(𑌤𑌾)  । ദൂ(𑌖)  ഭിഃ(𑌪𑍍𑌲)॥1॥
#End of Mantra Sets -- subsection_235 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_236 ## DO NOT EDIT
അതശ്ചിദിന്ദ്രന(𑌷𑍂) ഉപാ(𑌤𑌾)  ഏ(𑌤)   ।  ആയാ(𑌚𑌾)  ഹി(𑌶)  ശാതാവാജാ(𑌟𑍀)  യാ(𑌖) ഈഷാ(𑌖𑌾)  സഹാ(𑌤𑌾)   ।  സ്രാ(𑌕)  വോ(𑌪)  ബാ(𑌪𑍍𑌲)  ജായോ(𑌪𑍍𑌲𑌾) । ഹാഇ(𑌶𑌾) ॥2॥
#End of Mantra Sets -- subsection_236 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_237 ## DO NOT EDIT
ആബുന്ദംവൃ(𑌤𑍀)   ।  ത്രാ(𑌚) ഹാദദാഇജാതാഃ(𑌕𑍂)    പാ(𑌕) ച്ഛ൪ദ്വിമാ(𑌟𑌿) താ(𑌖) രം(𑌣) ।  കാഉഗ്രാ(𑌟𑌿)  കേ(𑌤)  ।  ഹാശ്രു(𑌚𑌾)   ണ്വിരാഇഴാ(𑌟𑍀) ഭാ(𑌖𑌣𑍍)   । ഓ(𑌪)  ഇഴാ(𑌶𑌾)  ॥3॥
#End of Mantra Sets -- subsection_237 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_238 ## DO NOT EDIT
ബ്രബദുക്ഥംഹാ(𑌤𑍁)  വാമഹാ(𑌤𑌿)  ഇ(𑌶)   ।  സപ്രാ(𑌟𑌾)  കാരാ(𑌟𑌾)  സ്നാമൂ(𑌕𑌾) തായാ(𑌚𑌾)  ഇ(𑌶)   ।  സാധാഃ(𑌟𑌾)  കാ൪ണ്വാ(𑌟𑌾𑌚𑍍)  ന്താ(𑌕) മോ(𑌪)  ബാ(𑌪𑍍𑌲) വാസോ(𑌪𑍍𑌲𑌾) । ഹാഇ(𑌶𑌾)॥4॥
#End of Mantra Sets -- subsection_238 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_239 ## DO NOT EDIT
ഋജുനീതീനോ(𑌷𑍁) വരൂണഇഹാ(𑌤𑍁)   ।  മിത്രോ(𑌚𑌾)  നായാ(𑌚𑌾) തീവിദ്വാം(𑌟𑌿)  സാഇഹാ(𑌤𑌿)   ।  അ൪യാ(𑌥𑌾)  മാദാ(𑌟𑌾)  ഇവാഇഹാ(𑌤𑍀)   । സാജോഷാ(𑌟𑌿)  ഉവാ(𑌤𑌾)   ।  ഈ(𑌖) ഹാ(𑌶) ॥5॥
#End of Mantra Sets -- subsection_239 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_240 ## DO NOT EDIT
ദൂരാ(𑌕𑌾)  ദീ(𑌪)  ഹേവയത്സാതാഃ(𑌶𑍁)   ।  ആരൂ(𑌚𑌾)  ണാ(𑌚)  പ്സൂരാശിശ്വാ(𑌟𑍀)  ഇതാ(𑌤𑌾) ത്।  വീഭാനൂം(𑌟𑌿)  വീ(𑌤)   ।  ശ്വാഥാ(𑌚𑌾) തനാദിഴാ(𑌟𑍀) ഭാ(𑌖𑌣𑍍)   ।  ഓ(𑌪)  ഇഴാ(𑌪𑍍𑌲𑌾)  ॥6॥
#End of Mantra Sets -- subsection_240 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_241 ## DO NOT EDIT
ആനോമിത്രാവരു(𑌕𑍂)  ണാഔ(𑌥𑌾)  ഹോവാ(𑌟𑌾)   ।  ഘൃതൈ(𑌤𑌾) ൪ഗവ്യൂതിമുക്ഷാ(𑌕𑍁)  താമൗ(𑌥𑌾)  ഹോവാ(𑌟𑌾)   ।  മാധ്വാ(𑌥𑌾)  രാജാം(𑌟𑌾) സീ(𑌕)  സുഔ(𑌥𑌾) ഹോവാ(𑌟𑌾)  ।  കൃതൂ(𑌕𑌾)  ഇഴാ(𑌟𑌾)  ഭാ(𑌖𑌣𑍍)   ।  ഓ(𑌪) ഇഴാ(𑌪𑍍𑌲𑌾) ॥7॥
#End of Mantra Sets -- subsection_241 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_242 ## DO NOT EDIT
ഉദുത്യേസൂനാ(𑌤𑍁)  വോഗിരാഃ(𑌤𑌿)   ।  കാഷ്ഠാ(𑌥𑌾𑌚𑍍)  യജ്ഞാ(𑌕𑌾) ഇഷുവാ(𑌟𑌿)  ത്നാ(𑌖)  താ(𑌣)   ।  വാ(𑌕)  ശ്രാആ(𑌟𑌾)  ഭീ(𑌤)   ।  ജ്ഞൂ(𑌪) യാ(𑌶) താ(𑌖)  വോ(𑌪𑍍𑌲)  ।ഹാഇ(𑌶𑌾)॥8॥
#End of Mantra Sets -- subsection_242 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_243 ## DO NOT EDIT
ഇദാമേ(𑌤𑌿)   ।  വിഷ്ണൂ(𑌟𑌾)  ൪വിചാക്രാ(𑌖𑌿)  മാ(𑌣) ഇ(𑌶)। ത്രാഇധാ(𑌚𑌿)  നിദ(𑌕𑌾)  ധാ(𑌚)  ഇപാ(𑌯𑌾)  ദാം(𑌟)   സമൂ(𑌟𑌾)  ഹോ(𑌯) ഢാ(𑌟)  മാ(𑌤)   ।  സ്യാ(𑌟)  പാ(𑌖)  ഔഹോവാ(𑌶𑌿)   ।  ഏം(𑌤)  സൂലേ(𑌤𑌾𑌚𑍍) ॥9॥
#End of Mantra Sets -- subsection_243 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_244 ## DO NOT EDIT
അതീഹിമാ(𑌤𑍀)   ।  ന്യൂഷാ(𑌟𑌾)  വാഇണാം(𑌟𑌿)   ।  സൂഷൂവാം(𑌚𑌿) സാ(𑌟𑌚)  ഹോ(𑌕)  ഉപൈ(𑌯𑌾)  രായാ(𑌟𑌾)   ।  ആസ്യരാ(𑌕𑌿)  താബുസൂ(𑌟𑌿)  താ(𑌖)  ഔഹോവാ(𑌶𑌿)   ।  പീ(𑌖)  ബാ(𑌶) ॥1॥
#End of Mantra Sets -- subsection_244 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_245 ## DO NOT EDIT
കദൂപ്രാചേ(𑌚𑌿)  താ(𑌕)  സേ(𑌫)    മഹാ(𑌤𑌾)  ഇവാ(𑌪𑌾) ചോ(𑌶) ദേവാഹാബുവചോദേവാ(𑌶𑍃)  । യാശസ്യാ(𑌟𑌿)  താ(𑌖)  ഇതദാ(𑌖𑌿)  ഇധിയാ(𑌤𑌿) । സ്യാ(𑌕) വോ(𑌪)  വാ(𑌪𑍍𑌲)  ൪ധാനാം(𑌪𑍍𑌲𑌾)   ।  ഹാഇ(𑌶𑌾)॥2॥
#End of Mantra Sets -- subsection_245 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_246 ## DO NOT EDIT
ഉക്ഥഞ്ചനോ(𑌤𑍀)  ഹാ(𑌤)  ഇ(𑌶)   ।  ശസ്യമാനാ(𑌷𑍀) ന്നാഗോരാ(𑌟𑌿𑌚𑍍)  ഇരാ(𑌚𑌾) ചികേ(𑌖𑌾)  താ(𑌶)   । നാഗായാ(𑌟𑌿) ത്രാം(𑌤) । ഗീ(𑌕) യാമാ(𑌟𑌾) നാ(𑌖)  ഔഹോവാ(𑌶𑌿)  ।  ഊ(𑌖)  പാ(𑌶) ॥3॥ ഇന്ദ്രഉക്ഥാ(𑌤𑍀) ഇ(𑌶𑍁)   ।  ഭ്യ(𑌕)  ൪മന്ദാഇഷ്ഠോ(𑌟𑍀)  വാജാനാ(𑌖𑌿) ഞ്ചാ(𑌣)   । വാ(𑌚)  ജപാ(𑌚𑌾)  തി൪ഹരാ(𑌟𑌿)  ഈവാ(𑌖𑌾)  ന്സൂ(𑌣)   । താനാം(𑌕𑌾𑌚𑍍) സാ(𑌕)  ഖാഔ(𑌟𑌾)  ഹോ(𑌖)  ബാ(𑌪𑍍𑌲)  ।ഹോ(𑌪𑍍𑌲)  ഇഴാ(𑌶𑌾) ॥4॥
#End of Mantra Sets -- subsection_246 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_247 ## DO NOT EDIT
ബ്രാഹ്മണാദീ(𑌤𑍀)  । ന്ദ്രരാ(𑌕𑌾) ധസാഃപിബാ(𑌕𑍀)  സോമാ(𑌟𑌾)  മൃതൂം(𑌕𑌾) രനൂ(𑌚𑌾)  । താവേ(𑌕𑌾)  ദൂസാ(𑌟𑌾)  ഖ്യാ(𑌪)  മാ(𑌶)   സ്താ(𑌖) ൪ത്താ(𑌪𑍍𑌲)   ।ഹാഇ(𑌶𑌾) ॥5॥ വയംഘാതേ(𑌫𑍀)  അപീ(𑌶𑌾)  സ്മസാ(𑌕𑌾)  ഇ(𑌶)   ।  സ്തോ(𑌕) താരഇന്ദ്രഗി൪വണാ(𑌷𑍃) ഉവഉവാ(𑌟𑍀)  ഹോ(𑌚) ഇ(𑌶)   ।  തൂ(𑌚)  വാ(𑌯)  ന്നോജീ(𑌟𑌾)  ഉവഉവാ(𑌟𑍀)  ഹോ(𑌕𑌥𑍍) ന്വാ(𑌶)  സോമാ(𑌟𑌾𑌟𑍍)  പാ(𑌖) ഔഹോവാ(𑌶𑌿)   ।  ഏ(𑌤) ഊപാ(𑌟𑌾𑌖𑍍) ॥6॥
#End of Mantra Sets -- subsection_247 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_248 ## DO NOT EDIT
ആയാഹീ(𑌤𑌿)   ।  ഊ(𑌚)  പാനാ(𑌚𑌾)  സ്സൂതം(𑌶𑌾)  ഹോവാ(𑌟𑌾)  ഹാ(𑌤)  ഇ(𑌶) । വാജേഭി(𑌕𑌿) മാഹൃണീ(𑌕𑌿)  യഥാ(𑌤𑌾) ഹോവാ(𑌟𑌾)  ഹാ(𑌤)  ഇ(𑌶)  । മാഹം(𑌚𑌾)  ഈവായുവാ(𑌟𑍀)   ഹോവാ(𑌟𑌾)  ഹാ(𑌤)  ഇ(𑌶) । ജാ(𑌟𑌟𑍍)  നാ(𑌖)  ഔഹോവാ(𑌶𑌿)   ।  ഉഊ(𑌖𑌾)  പാ(𑌶) ॥7॥ ഓ(𑌟𑌚𑍍)  ഹോ(𑌚)  ഇ(𑌶)    കാദാ(𑌕𑌾)  വസോ(𑌫𑌾)  സ്തോത്രാം(𑌟𑌾) ഹ൪യതാ(𑌖𑌿) യാ(𑌶)   । ഓ(𑌟𑌚𑍍)  ഹോ(𑌚)  ഇ(𑌶)     യാവാ(𑌕𑌾)  ശ്മാശാ(𑌫𑌾)  രൂധാദൂ(𑌖𑌿)  വാഃ(𑌣)   ।  ഓ(𑌟𑌚𑍍)  ഹോ(𑌚)  ഇ(𑌶) ദീ൪ഘം(𑌕𑌾)  സൂതം(𑌫𑌾)  വാതാ(𑌪𑌾)  പീയാ(𑌖𑌾)  യാ(𑌤𑍍𑌰)   ।  ഈ(𑌖) ॥8॥ കാദാ(𑌖𑌾)  ഔ(𑌕)  ഹോവാ(𑌥𑌾)  വാസോസ്തോത്രാം(𑌟𑍀) ഹ൪യതാ(𑌖𑌿) യാ(𑌶)  । അവാ(𑌖𑌾)  ഔ(𑌕)  ഹോവാ(𑌥𑌾)। ।  ശ്മശാ(𑌕𑌾)  രൂധാദൂ(𑌖𑌿)  വാഃ(𑌣)   । ദീ൪ഘാ(𑌖𑌾)   ഔ(𑌕)  ഹോവാ(𑌥𑌾) । സൂതാം(𑌟𑌾)   ।  വാതാ(𑌖𑌾)  പീയാ(𑌖𑌾)  ।യാ(𑌤𑍍𑌰) ॥9॥ ഔ(𑌚) ഹോവാഇ(𑌶𑌿) കാദാവാ(𑌕𑌿)  സോ(𑌫)  സ്തോത്രാം(𑌟𑌾) ഹ൪യാതാ(𑌖𑌿) യാ(𑌶) । ഔ(𑌚)  ഹോവാഇ(𑌶𑌿)  യാവാ(𑌕𑌾)  ശ്മാശാ(𑌫𑌾)  രൂധാദൂ(𑌖𑌿)  വാഃ(𑌣) । ഔ(𑌚)  ഹോവാഇ(𑌶𑌿)  ദീ൪ഘം(𑌕𑌾)  സൂതം(𑌫𑌾)  വാതാ(𑌪𑌾)  പീയാ(𑌖𑌾)  യാ(𑌤𑍍𑌰)   ।  ഏ(𑌤𑌚𑍍)  ॥10॥
#End of Mantra Sets -- subsection_248 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_249 ## DO NOT EDIT
ഏന്ദ്രപൃക്ഷു(𑌷𑍀) കാസുചീ(𑌤𑌿)  ദേ(𑌤)   ।  നൃമ്ണാ(𑌚𑌾)  തനൂ(𑌕𑌾𑌚𑍍) ഷൂധാ(𑌕𑌾) ഹാ(𑌯)  ഇനാഃ(𑌟𑌾)   ।  സാ(𑌚) ത്രാ(𑌶) ജിദൂ(𑌚𑌾) ഗ്രാപാ(𑌟𑌾) പുംസിയാ(𑌕𑌿)  ഉവാ(𑌤𑌾)   ।  ഊ(𑌖)  പാ(𑌶) ॥11॥
#End of Mantra Sets -- subsection_249 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_250 ## DO NOT EDIT
അയമേനം(𑌷𑍀) സചതാം(𑌤𑌿)  ഹാ(𑌤)  ബു(𑌶)   ।  ഓഇസൂ(𑌟𑌿)  തോ(𑌤)  മന്ദിമി(𑌕𑌿) ന്ദ്രായമാ(𑌟𑌿)  ന്ദാ(𑌖)  ഇനാ(𑌣𑌾)  ഇ(𑌶)   ।  ചക്രാഇംവാ(𑌟𑍀𑌟𑍍)  ഇശ്വാ(𑌖𑌾) ഔഹോവാ(𑌶𑌿)   ।  നീചാക്രാ(𑌟𑌿) യേ(𑌖) ॥12॥
#End of Mantra Sets -- subsection_250 ## DO NOT EDIT
```

---

## OUTPUT FORMAT:
Return **ONLY** the fully annotated text preserving the `#Start of Mantra Sets` and `#End of Mantra Sets` tags. Do not wrap in conversational fluff or additional markdown tags.
