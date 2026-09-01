# Visual Swara Extraction Prompt — Batch: Agneyam_K1_benchmark_eval

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
page_0003.png, page_0004.png, page_0005.png, page_0006.png

---

## MASTER TEXT TO ANNOTATE:

```text
#Start of Mantra Sets -- subsection_1 ## DO NOT EDIT
ഓ(𑌤)(C) ഗ്നാ(𑌤) ഇ(𑌶) ।ആയാ(𑌥𑌾𑌚𑍍) ഹീവാ(𑌚𑌾) ഇ(𑌶) । 
താ(C)യാ(𑌟𑌾)_ഇ(𑌶). താ(C)യാ(𑌟𑌿)_ഇ(𑌶) । 
ഗൃണാ(𑌚𑌾) നോ(𑌶)_ ഹവ്യാ_ദാ(𑌚𑌿)(H) ।
താ(C)യാ_(𑌟𑌾)ഇ(𑌶).താ(C)യാ(𑌟𑌿) ഇ(𑌶) । 
നാഇഹോ_(𑌕𑌿) താ(𑌚)(H) । സാ(𑌟)_ത്സാ(𑌟).ഇബാ(𑌖𑌾) ഔഹോവാ(𑌶𑌿)।ഹീ(𑌖)ഷി(𑌶)॥1॥
#End of Mantra Sets -- subsection_1 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_2 ## DO NOT EDIT
അഗ്നആയാ(E)ഹീവീ(𑌤𑍂) ।തായാഇഗൃണാനോ(𑌷𑍂) ഹവ്യദാ_താ(C)(𑌟𑍀) യാ(𑌤) ഇ(𑌶)। 
നീഹോതാ(𑌚𑌿) സത്സീ_ബ൪ഹാ(𑌟𑍀). ഇഷീ(𑌤𑌾)। ബ,൪ഹാ(𑌟𑌾). ഇഷാ(𑌖𑌾) ഔഹോവാ(𑌶𑌿) ।
ബ(𑌚).൪ഹീ(C)ഷീ(𑌖𑌾)॥2॥
#End of Mantra Sets -- subsection_2 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_3 ## DO NOT EDIT
അഗ്നആയാഹീവാ(𑌤𑍂),  ഇതായാ(𑌤𑌿) ഇ(𑌶) । ഗൃണാനോഹവ്യദാ(𑌯𑍂). താ(𑌪) യേ(𑌶)  । 
നിഹോതാ(𑌖𑌿) സാ(𑌣) ത്। സാ(𑌟). ഇബാ(𑌤𑌾).  ൠഹാ(𑌪𑌾)(A) ആഇഷോ(𑌪𑍍𑌲𑌿)(G)  । ഹാഇ(𑌶𑌾)  ॥3॥
#End of Mantra Sets -- subsection_3 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_4 ## DO NOT EDIT
ത്വമഗ്നേയജ്ഞാനാം(𑌷𑍂), ത്വമഗ്നാ(𑌤𑌿) ഇ(𑌶)। യജ്ഞാനാംഹോതാവിശ്വേ(𑌷𑍃), ഷാം(C)ഹാ(𑌟𑌾). 
ഇതാഃ(𑌤𑌾) । ദേ(𑌕)(G)_വാഇഭാ(𑌟𑌿), ഇ൪മാ(𑌤𑌾) । നുഷേ(𑌤𑌾𑌚𑍍). ജ(𑌕) നാ(C)ഔ(𑌟𑌾). ഹോ(𑌖)(A) ബാ(𑌪𑍍𑌲)(G)। ഹോ(𑌪𑍍𑌲)(D) ഇഴാ(𑌶𑌾) ॥4॥
#End of Mantra Sets -- subsection_4 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_5 ## DO NOT EDIT
അഗ്നിന്ദൂ(𑌟𑌿), താം(𑌤) ।വൃണീമഹാഇ(𑌷𑍂) ഹോ,താ(C)രാം(𑌟𑌿)_ വീ(𑌤)(G) ശ്വാവേ(𑌚𑌾)_ ദസാം(𑌚𑌾) ।അസ്യയാ(𑌟𑌿)(C) 
ജ്ഞാ(𑌤). ഓഔ(𑌕𑌾). ഹോ(𑌤)(C) വാ(𑌤) । സ്യാസൂ(𑌚𑌾)_ ക്ര,തൂമിഴാ(𑌟𑍀). ഭാ(𑌖𑌣) ।ഓ(𑌪) ഇഴാ(𑌪𑍍𑌲𑌾)॥5॥
#End of Mantra Sets -- subsection_5 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_6 ## DO NOT EDIT
അഗ്നി൪വൃത്രാ(𑌤𑍀) ।ണാ(𑌟). ഇജാ(𑌖𑌾) ഔഹോവാ(𑌶𑌿) ।ഘാ(𑌖) നാ(𑌶) ത്। 
ദ്ര(𑌚) വി(𑌶) ണാ(𑌕) സ്യു൪വീപ(𑌕𑌿)_ ന്യാ,യാ(𑌟𑌾). ഓഇ,സമിദ്ധാ(𑌟𑍁)(C) ശ്ശൂ(𑌤) ।
ക്രായാ(𑌚𑌾)_ ഹു,താഇഴാ(𑌟𑍀). ഭാ(𑌖𑌣𑍍)। ഓ(𑌪) ഇഴാ(𑌪𑍍𑌲𑌾) ॥6॥ അഗ്നീ(𑌖𑌾) രൗഹോവാ(𑌶𑌿) ഹാഇവൃത്രാണീ(𑌶𑍁) ।ജം(C)ഘാ(𑌟𑌾)(C) നാ(𑌤). 
ദൗ(C)ഹോ(𑌟𑌾)(C) വാ(𑌤) ഇ(𑌶) ।
ദ്രവിണാ(𑌪𑌿) സ്യൂഃ(𑌣) ।ഓഇവാഇ(𑌷𑍀),പന്യായാ(𑌟𑌿), 
സാമാഇദ്ധാ(𑌟𑍀𑌟𑍍). ശ്ശൂ(𑌖) ഔഹോവാ(𑌶𑌿) । ക്രായാ_ഹൂ(𑌟𑌿).താഃ(𑌖)॥7॥ ഓ(𑌤)(C) ഗ്നീഃ(𑌤)। വൃത്രാണീ(𑌕𑌿)   ജംഘനാ_ദൗ(𑌕𑍀)_ ഹോഔഹോ(𑌖𑌿) വാ(𑌶) । ദ്രവീ(𑌚𑌾) ണാ(𑌕) സ്യു൪വീപ(𑌕𑌿)_ ന്യയാ(𑌚𑌾) ഔ(𑌕)_ ഹോഔഹോ(𑌖𑌿) വാ(𑌶) । സമിദ്ധാ(𑌚𑌿)ശ്ശുക്രയാ(𑌚𑌿)_ഔ(𑌕)_ഹോഔഹോ(𑌖𑌿).ബാ(𑌪𑍍𑌲)ഹൂ(D)തോ(𑌪𑍍𑌲𑌾)(A1)।ഹാഇ(𑌶𑌾)॥8॥
#End of Mantra Sets -- subsection_6 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_7 ## DO NOT EDIT
പ്രേഷ്ഠം(E)വാഃ(𑌤𑌿) ।അ,താ(𑌟𑌾). ഇഥീം(𑌤𑌾) ।സ്തുഷേ(𑌚𑌾) മിത്ര,മിവപ്രാ(𑌟𑍁)(C) യാം(𑌤) ।
അഗ്നാ_ഇരാ(𑌭𑍀)(C) ഥാ(𑌤). ന്നാ(C)വാ(𑌟𑌾). ഹാ(𑌖𑌣) ഇ(𑌶) । ദാ(𑌪)ആ(A)യാം(𑌪𑍍𑌲𑌾) । ഹാഇ(𑌶𑌾) ॥9॥
#End of Mantra Sets -- subsection_7 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_8 ## DO NOT EDIT
പ്രേഷ്ഠംവയോ(𑌤𑍀)(C) ഹാ(𑌤) ഇ(𑌶) ।അ,താ(𑌟𑌾).ഇഥീം(𑌤𑌾) ।സ്തൂഷാ(𑌤𑌾) ഇ(𑌶). മീത്രാ(𑌤𑌾)(G), 
മീ,വാ(𑌟𑌾). പ്രാ(𑌖) യാം(𑌣) । ഔ(𑌥) ഹോ(𑌚) ഇ(𑌶) । അഗ്നേ(𑌥𑌾). രാ(C)ഥാ(𑌟𑌾). ന്നാ(𑌪) 
വേ(𑌶) ।ദാ(𑌖)(A) യാം(𑌶)(G) ।ഹാഇ(𑌶𑌾)॥10॥ 

പ്രേഷ്ഠംവോ(𑌤𑌿)(C) ഹാ(𑌤) ബു(𑌶) ।
ആതിഥാഇംസ്തൂ(𑌷𑍁) ഷേമിത്രാ,മീവപ്രാ(𑌟𑍂)(C) യാം(𑌤) ।
അഗ്നാഇരാ(𑌟𑍀𑌟𑍍). ഥാ(𑌖)(C) ഔഹോവാ(𑌶𑌿)। നാവേ_ദീ(𑌟𑌿) യാം(𑌖) ॥11॥
#End of Mantra Sets -- subsection_8 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_9 ## DO NOT EDIT
ത്വന്നോ(E)യാ(𑌤𑌿) ।ഗ്നേ(𑌚) മാ_ഹോ(𑌥𑌾) ഭിഃപാ,ഹാഇവീ(𑌟𑍁)(C) ശ്വാ(𑌤) । സ്യാ(𑌚) ആ_രാതേ(𑌥𑌿𑌚𑍍)_ രൂതാ(𑌚𑌾)_ ദ്വാ(𑌯)_ 
ഇഷാഃ(𑌟𑌾) ।മാ(𑌕)(G)_ ൪ത്യാ(𑌥) സ്യാഇഴാ(𑌟𑌿). ഭാ(𑌖𑌣𑍍) ।ഓ(𑌪) ഇഴാ(𑌶𑌾) ॥12॥ 
ത്വാന്ത്വന്നോ(𑌷𑌿) അഗ്നേമഹോ(𑌤𑍀)(C) ഭാ(𑌤) ഇഃ(𑌶) । പാ(𑌕)(G)_ ഹിവിശ്വാ_ഔ(𑌟𑍀)(C) 
ഹോ(𑌤) സ്യാ(C)_ഔ(𑌟𑌾)(C) ഹോ(𑌤) ।ആരാതേ(𑌕𑌿𑌚𑍍)_രൂതാ(𑌚𑌾)_ദ്വാ(𑌯)_ഇഷാഃ(𑌟𑌾) ।മ,൪തോ(𑌟𑌾𑌟𑍍). 
യാ(𑌖).ഔഹോവാ(𑌶𑌿) ।സ്യാ(𑌖) ॥13॥
#End of Mantra Sets -- subsection_9 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_10 ## DO NOT EDIT
ഏ(B)ഹ്യൂ(𑌫𑌾) ഷുബ്രാവാ(𑌖𑌿) ണാഇതാഇ(𑌶𑍀) । അഗ്നഇത്ഥേ(𑌷𑍀) തരാ_ഗാ(𑌟𑌿). ഇരാഃ(𑌚𑌾) ।
ഏ(C)ഭാ(𑌟𑌾). ഇ൪വാധാ(𑌚𑌿) ।സ,യാ(𑌟𑌾). ഹാ(𑌖𑌣𑍍) ഇ(𑌶) । ദോ(𑌪) (A)ഭോ(𑌪𑍍𑌲)(G) ।ഹാഇ(𑌶𑌾) ॥14॥ 
ഏഹ്യൂഷൂ(𑌷𑌿) ബ്രവൗഹോണാ(𑌤𑍀)(E) ഇതാ(𑌤𑌾) ഇ(𑌶) ।അഗ്നഇത്ഥേതരാ(𑌯𑍂). ഗീ(𑌪) രാഃ(𑌶) ।
ഏഭി൪വാ(𑌖𑌿) ൪ദ്ധാ(𑌣) ।സ,യാ(𑌟𑌾). ഹാ(𑌖𑌣𑍍) ഇ(𑌶) ।ദോ(𑌪) (A)ഭോ(𑌪𑍍𑌲)(G) ।ഹാഇ(𑌶𑌾)॥15॥
#End of Mantra Sets -- subsection_10 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_11 ## DO NOT EDIT
ആതേവത്സാഃ(𑌤𑍀) ।മാ(𑌚) നോ(𑌶)_ യമത്പാരാ(𑌚𑍀)_ മാ(𑌥)_ ച്ചിത്സാധാ(𑌟𑌿)(C) സ്ഥാ(𑌤) ത്। 
അഗ്നാ_ഇത്വാ(𑌭𑍀)(C) ങ്കാ(𑌤)। മയോ(𑌪𑌾).(D) ബാ(𑌪𑍍𑌲) ഗാ(D)ഇരോ(𑌪𑍍𑌲𑌿)(A1)। ഹാഇ(𑌶𑌾)॥16॥ 
ആതേവത്സോ(𑌷𑍀) മനോയമദയ്യാ(𑌤𑍂)(C) ഹാ(𑌤) ഇ(𑌶) ।
പാരാമാ(𑌷𑌿) ച്ചിത്സധസ്ഥാ,ദ്ം(C)യ്യാ(𑌟𑍂).ഹോ(𑌕𑌚𑍍)_ ഇയാ(𑌶𑌾) ।
അഗ്നേത്വാങ്കാ(𑌷𑍀) മാ,യാഅയ്യാ(𑌟𑍂𑌚𑍍). ഹോ(𑌕𑌚)_ ഇയാ(𑌶𑌾) ।
ഗീരാ(𑌕𑌾) ഇഴാ(𑌟𑌾). ഭാ(𑌖𑌣𑍍)। ഓ(𑌪) ഇഴാ(𑌶𑌾) ॥17॥
#End of Mantra Sets -- subsection_11 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_12 ## DO NOT EDIT
ത്വാമഗ്നേപുഷ്കാ(𑌤𑍁), രാദധീ(𑌤𑌿) ।ആ(𑌚) ഥ൪വാ(𑌚𑌾)_ നാ_ഇരാമാ(𑌟𑍀). ന്ധാ(𑌖) താ(𑌣) ।
മൂ(𑌖)(C) ൪ധ്നോ(𑌪𑍍𑌲)(C) വാ(𑌖) ഇശ്വാ(𑌣𑌾) ।സ്യാവോ(𑌪𑌾)(D) ബാ(𑌪𑍍𑌲) ഘാ(D)തോ(𑌪𑍍𑌲𑌾) (A1)।ഹാഇ(𑌶𑌾)॥18॥
#End of Mantra Sets -- subsection_12 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_13 ## DO NOT EDIT
അഗ്നേവിവ(𑌷𑍀) സ്വദാഭരോവാ(𑌤𑍂)(C) ഹാ(𑌤) ഇ(𑌶) ।അസ്മാ(𑌚𑌾) ഭ്യാമൂ(𑌕𑌾𑌚𑍍). തായാ(𑌚𑌾) ഇമ,
ഹാ(𑌟𑌿) ഓവാ(𑌟𑌾)(C) ഹാ(𑌤). ഓ,വാ(𑌟𑌾)(C) ഹാ(𑌤) ഇ(𑌶) ।ദാ(𑌚)_ ഇവോ(𑌯𑌾)_ ഹി,യാ(𑌟𑌾)_ 
ഓ,വാ(𑌟𑌾)(C)_ ഹാ(𑌤)_ ഓ,വാ(𑌟𑌾)(C) ഹാ(𑌤)ഇ(𑌶) ।സാ(𑌟), ഇനാ(𑌖𑌾)_ ഔഹോവാ(𑌶𑌿) ।
ദൃശേ(𑌤𑌾𑌚𑍍)(G)॥19॥
#End of Mantra Sets -- subsection_13 ## DO NOT EDIT
```

---

## OUTPUT FORMAT:
Return **ONLY** the fully annotated text preserving the `#Start of Mantra Sets` and `#End of Mantra Sets` tags. Do not wrap in conversational fluff or additional markdown tags.
