# Visual Swara Extraction Prompt — Batch: Aindram_K6_sub1466_1475

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
page_0185.png, page_0186.png, page_0187.png, page_0188.png, page_0189.png

---

## MASTER TEXT TO ANNOTATE:

```text
#Start of Mantra Sets -- subsection_1466 ## DO NOT EDIT
ഏന്ദ്നനാഃ(𑌤𑌿) ।ഗ(𑌕) ധിപ്രാ(𑌟𑌾) യാ(𑌖) ।സാത്രാജിതാ(𑌕𑍀) ഗോഹാ(𑌟𑌾) യാ(𑌖𑌾) ഗിരാഇ൪ന്നവാ(𑌤𑌿) ഇ(𑌶) ।ശ്വാതാഃപാ(𑌤𑌿) ൪ത്ഥൂഃപാ(𑌟𑌾𑌟𑍍) ൪താ(𑌖) ഔഹോവാ(𑌶𑌿) ।൪ദീ(𑌖) വാഃ(𑌪𑍍𑌲) ॥1॥ ഏന്ദ്നനോ(𑌫𑌿) ഗധിപ്രാ(𑌣𑌿) യാ(𑌶) ।സാത്രാജിതാ(𑌕𑍀) ഗോഹാ(𑌯𑌾) യൗ(𑌟) ഹോവാ(𑌤𑌾) ഹാ(𑌤) ഇ(𑌶)। ഗിരാഇ൪ന്നവൗ(𑌟𑍀) ഹോവാ(𑌤𑌾) ഹാ(𑌤)  ഇ(𑌶)। ശ്വാതാഃപാ(𑌟𑌿) ൪ത്ഥൂഃ(𑌖)  ഔഹോവാ(𑌶𑌿) ।പാതീ൪ദീവാഃ(𑌤𑍀) ॥2॥
#End of Mantra Sets -- subsection_1466 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_1467 ## DO NOT EDIT
യസ്യാ(𑌤𑌾) ഓ(𑌪) ത്യാച്ഛാ(𑌤𑌾) ഓം(𑌪)  ബര(𑌪𑍍𑌲𑌾) മ്മാ(𑌤) ദാ(𑌤) ഇ(𑌶)  । ദിവോ(𑌤𑌾)  ഓ(𑌕)  ദാസാ(𑌤𑌾) ഓ(𑌪) യര(𑌪𑍍𑌲𑌾) ന്ധാ(𑌤) യാ(𑌤) യാ(𑌶) ൻ। അയാ(𑌤𑌾) ഓം(𑌕) സസോ(𑌤𑌾) ഓ(𑌪) മ(𑌪𑍍𑌲)  ഇന്ദ്രാ(𑌤𑌾) താ(𑌤) ഇ(𑌶) । സുതാഃ(𑌤𑌾) ഓഃ(𑌕) പിബാ(𑌤𑌾) ഓ(𑌪)  ബാ(𑌪𑍍𑌲) ।ഊ(𑌖) പാ(𑌶)  ॥3॥ യസ്യാത്യച്ഛാം(𑌫𑍀) ബരമ്മാദാ(𑌕𑍀) ഇ(𑌶) ।ദീവോദാസാ(𑌷𑍀) യരന്ധായന്നായാം(𑌕𑍂𑌚𑍍) സാ(𑌕) സോ(𑌖) മഇന്ദ്രാ(𑌤𑌿)  താ(𑌤) ഇ(𑌶) ।സൂ(𑌟) താ(𑌖) ഔഹോവാ(𑌶𑌿) । പീ(𑌖) ബാ(𑌶)  ॥4॥ യസ്യാത്യാച്ഛാം(𑌖𑍀)  ബരമ്മാദാ(𑌪𑍍𑌲𑍀) ഇ(𑌶)। ദീവോ(𑌟𑌾𑌚𑍍) ദാ(𑌕)  സായര(𑌷𑌿) ന്ധയന്നയാം(𑌕𑍀𑌚𑍍) സാ(𑌕)  സോ(𑌖) മഇന്ദ്രാ(𑌤𑌿) താ(𑌤) ഇ(𑌶) ।സുതാ(𑌕𑌾)  ഓഃപാ(𑌟𑌾𑌟𑍍) ഇബാ(𑌖𑌾) ഔഹോവാ(𑌶𑌿) । ഈ(𑌖) തി(𑌶) ॥5॥ യാ(𑌫)  സ്യാത്യാ(𑌪𑍍𑌲𑌾) ച്ഛദ്ധോഇശംബരാ(𑌖𑍂)  മ്മദാഏ(𑌪𑍍𑌲𑌿) । ദീവോദാസാ(𑌷𑍀) യരന്ധയ(𑌚𑍀)  ന്നയാംസാ(𑌭𑌿) സോ(𑌖) മഇന്ദ്രാതാ(𑌖𑍀)  ഔഹോവാ(𑌶𑌿) ।സൂ(𑌖) താഃ(𑌪𑍍𑌲) പിബോ(𑌖𑌾) ഇഴാ(𑌶𑌾)॥6॥
#End of Mantra Sets -- subsection_1467 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_1468 ## DO NOT EDIT
ഹാബുഗൃണാ(𑌤𑍀) ഇ(𑌶)  । തദാഇന്ദ്രോ(𑌖𑍀)  താ(𑌣) ഇ(𑌶) ।ശവാ(𑌟𑌾) ഓവാ(𑌕𑌾) ഉപാമാ(𑌖𑌿) ന്ദേ(𑌣)  । വാതാതയാഇ(𑌷𑍁) യദ്ധംസാ(𑌟𑌿) ഇവാ(𑌖𑌾)  ത്രമോജസാശാചീ(𑌶𑍂) ।പാതാ(𑌟𑌾) ഔ(𑌟)  ഹോവാഹാ(𑌖𑌿) ഔഹോവാ(𑌶𑌿) ।ദ്യൂ(𑌖) ഭീഃ(𑌪𑍍𑌲)  ॥7॥
#End of Mantra Sets -- subsection_1468 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_1469 ## DO NOT EDIT
ഗൃണേതദാ(𑌖𑍀) ।ഔഹോ(𑌖𑌾)  ഇന്ദ്രതേ(𑌚𑌿)  ശവാഃ(𑌣𑌾) ।ഉപാ(𑌚𑌾) മാന്ദേ(𑌥𑌾) വാതാ(𑌕𑌾)  താ(𑌟) യാ(𑌖) ഇയദ്ധാം(𑌚𑌿) സിവാ(𑌤𑌾) ത്രമോ(𑌕𑌾)  ജസാ(𑌚𑌾) ശാചീ(𑌚𑌾) പാ(𑌫) । താ(𑌖) ഇ(𑌶) ॥8॥
#End of Mantra Sets -- subsection_1469 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_1470 ## DO NOT EDIT
ഗൃണേതദൗഹോ(𑌫𑍁)  ഇന്ദ്രതേ(𑌶𑌿) ശവാഃ(𑌕𑌾)  । ഉപാ(𑌚𑌾) മാന്ദേ(𑌟𑌾𑌚𑍍) വാതാ(𑌕𑌾)  തായഉപാ(𑌚𑍀) മാ(𑌟) ന്ദേ(𑌥𑌚𑍍) വാതാ(𑌕𑌾)  താ(𑌟) യാ(𑌤) ഇ(𑌶) ।യദ്ധംസീ(𑌕𑌿) വൃത്രമോ(𑌟𑌿)  ജസാ(𑌕𑌾) ഉവാ(𑌤𑌾) ।ശാ(𑌖)  ചീ(𑌪𑍍𑌲) പാ(𑌖) താഇഹോ(𑌖𑌿) ഇഴാ(𑌶𑌾) ॥9॥
#End of Mantra Sets -- subsection_1470 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_1471 ## DO NOT EDIT
യാഇന്ദ്രസോ(𑌤𑍀) ।മാപാ(𑌟𑌾) താ(𑌖) മാഃ(𑌣) ।മാദശ്ശവാ(𑌷𑍀) ഇഷ്ഠചേ(𑌕𑌿) തതാ(𑌚𑌾) ഇ(𑌶)  । യാഇനാ(𑌟𑌿) ഹാം(𑌖) സീ(𑌣) ।നീയത്രിണാ(𑌕𑍀)  ന്താ(𑌚) മീ(𑌕) മാ(𑌫) ।ഹാ(𑌖) ഇ(𑌶)  ॥10॥
#End of Mantra Sets -- subsection_1471 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_1472 ## DO NOT EDIT
തുചേതുനാ(𑌷𑍀) യതാത്സൂ(𑌖𑌿) നാഃ(𑌣)  । ദ്രാഘീ(𑌕𑌾) യആ(𑌖𑌾) യൂഃ(𑌣) ।ജീവാ(𑌚𑌾) സാആദി(𑌟𑌿) ത്യാസാ(𑌟𑌾) സ്സമ്മഹസാഃ(𑌟𑍀)  । കൃണോതാ(𑌖𑌿) । നാ(𑌤𑍍𑌰)  ॥11॥
#End of Mantra Sets -- subsection_1472 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_1473 ## DO NOT EDIT
വേത്ഥാഹി(𑌷𑌿) നിൠതീനാം(𑌤𑍀)  । വാജ്രഹാസ്താ(𑌕𑍀) പാരീ(𑌕𑌾) വ്രജാമാ(𑌕𑌿) ഹാരാ(𑌕𑌾) ഹാശു(𑌕𑌾) ന്ധ്യുഃപാരീ(𑌕𑌿) പദാ(𑌟𑌾) മാ(𑌖) । ഇവാ(𑌤𑍍𑌰𑌾)  ॥12॥
#End of Mantra Sets -- subsection_1473 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_1474 ## DO NOT EDIT
അപാമീവാമപാ(𑌤𑍂) ।സ്രീധാമപസേ(𑌷𑍁) ധതാ(𑌕𑌾) ദു൪മ്മാ(𑌟𑌾) തീം(𑌤) । ആദീ(𑌟𑌾)  ത്യാസോ(𑌟𑌾𑌚𑍍) യൂ(𑌕) യോതനാനാ(𑌷𑍀) ആഉവാ(𑌕𑌿) ഓ(𑌪) ബാം(𑌪𑍍𑌲) ഹാസോ(𑌪𑍍𑌲𑌾) । ഹാ(𑌪𑍍𑌲) ഇ(𑌶𑌾) ॥13॥
#End of Mantra Sets -- subsection_1474 ## DO NOT EDIT
#Start of Mantra Sets -- subsection_1475 ## DO NOT EDIT
പീബാ(𑌤𑌾) ।സോമമിന്ദ്രമ(𑌷𑍁) ന്ദതുത്വാ(𑌟𑌿) യ(𑌕) ന്തേസുഷാവഹ൪യാ(𑌕𑍂) ശ്വാ(𑌟) ദ്രീഃ(𑌤) । സോ(𑌟) (𑌤) ൪ബാഹുഭീ(𑌟𑌿) യാം(𑌤) സൂയാ(𑌟𑌾𑌟𑍍)  താ(𑌖) ഔഹോവാ(𑌶𑌿) ।ഏ(𑌤𑌚𑍍) നാ൪വാ(𑌟𑌾𑌖𑍍)॥14॥ ഹാബുപിബാ(𑌤𑍀)  । സോമാമിന്ദ്രമ(𑌷𑍁) ന്ദതുത്വാ(𑌕𑌿) ദതുത്വാ(𑌚𑌿) യ(𑌕) ന്തേസുഷാവഹ൪യാ(𑌯𑍂) ശ്വാദ്രീ(𑌟𑌾) ശ്വാദ്രീഃ(𑌟𑌾) । സോ(𑌕) തു൪ബാഹുഭ്യാം(𑌕𑍀) സൂയതാ(𑌕𑌿) സ്സൂയതോ(𑌕𑌿) നാ(𑌟𑌟𑍍) ൪വാ(𑌖) ഔഹോവാ(𑌶𑌿)  । ഈ(𑌖)॥15॥
#End of Mantra Sets -- subsection_1475 ## DO NOT EDIT
```

---

## OUTPUT FORMAT:
Return **ONLY** the fully annotated text preserving the `#Start of Mantra Sets` and `#End of Mantra Sets` tags. Do not wrap in conversational fluff or additional markdown tags.
