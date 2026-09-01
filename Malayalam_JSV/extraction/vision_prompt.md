# Vision Extraction Prompt — JSV Samhita Malayalam Swara Modifiers

Canonical session preamble for every## 3. Mandatory 2-Pass Visual Extraction Protocol

To achieve 100% accuracy and eliminate false negatives, execute the extraction in two sequential passes:

### Pass 1: Phrasing & Pause Sweep
1. **Connector Underbars `_`**: Detect every baseline horizontal connector bar between closely sung words/syllables (e.g. `ഹവ്യാ_ദാ`, `സത്സീ_ബ൪ഹാ`, `ക്രായാ_ഹു`).
2. **Pause Dots `.`**: Detect every baseline period marking intermediate pauses (e.g. `തായാഇ.`, `ഇഷീ.`, `ജ്ഞാ.`).
3. **Cadence Commas `,`**: Detect every baseline comma marking cadence breaks (e.g. `ആയാ,`, `യജ്ഞാനാ,`, `വിശ്വെ,`, `ഹോ,`).

### Pass 2: Diacritic & Swara Modifier Sweep
1. **Shoulder Dots `(C)`**: Detect raised dots at the upper-right shoulder of characters (e.g. `ഓ(C)`, `താ(C)`, `ഷാം(C)`, `ജം(C)`). Note: Distinguish raised shoulder `(C)` from baseline pause period `.`.
2. **Under-Slashes `(G)`**: Detect downward diagonal strokes below baseline consonants (e.g. `വീ(G)`, `ബാ(G)`, `ഭോ(G)`). Do NOT confuse with standard Malayalam descenders (റ്റ, ല്ല).
3. **Melodic Arcs `(A)` & `(A1)`**: Detect bridging curves over syllables `(A)` or extending over dandas `(A1)`.
4. **Overhead Roofs & Carets `(D)` & `(B)`**: Detect inverted-V roofs `(D)` (`∧`) and peak carets `(B)` (`^`).
5. **High Accents `(H)` & `(E)`**: Detect vertical swarita bars `(H)` and heavy tone columns `(E)`.
6. **Shoulder Extended Marks `(D2)` (tick `✓`), `(I)` (dash `═`), `(J)` (bar `—`), `(K)` (cross `⨯`)**.

---

## 4. Ground-Truth Few-Shot Gold Standard Examples

Use these exact verified examples from the scanned manuscript to calibrate detection across both Agneyam Kandah 1 and Kandah 2:

### Example 1: `subsection_1` (Agneyam K1, Page 3)
```text
#Start of Mantra Sets -- subsection_1 ## DO NOT EDIT
ഓ(𑌤)(C) ഗ്നാ(𑌤) ഇ(𑌶) । ആയാ(𑌥𑌾𑌚𑍍) ഹീവാ(𑌚𑌾) ഇ(𑌶) । 
താ(C)യാ(𑌟𑌾)_ഇ(𑌶). താ(C)യാ(𑌟𑌿)_ഇ(𑌶) । 
ഗൃണാ(𑌚𑌾) നോ(𑌶)_ ഹവ്യാ_ദാ(𑌚𑌿)(H) ।
താ(C)യാ_(𑌟𑌾)ഇ(𑌶).താ(C)യാ(𑌟𑌿) ഇ(𑌶) । 
നാഇഹോ_(𑌕𑌿) താ(𑌚)(H) । സാ(𑌟)_ത്സാ(𑌟).ഇബാ(𑌖𑌾) ഔഹോവാ(𑌶𑌿)।ഹീ(𑌖)ഷി(𑌶)॥1॥
#End of Mantra Sets -- subsection_1 ## DO NOT EDIT
```

### Example 2: `subsection_15` (Agneyam K2, Page 6) — Demonstrating `(D1)`, `(C)`, `(G)`, `(A)`
```text
#Start of Mantra Sets -- subsection_15 ## DO NOT EDIT
ദൂ(𑌣) താം(𑌫)(D1). വോ(𑌖) വിശ്വവേദസാം(𑌶𑍁) ।ഹാ(𑌥) വ്യാവാ(𑌚), ഹാ(𑌟) മമാ(𑌟𑍁). ൪ത്താ(𑌖) യം(𑌣) ।യാ(𑌚)_ ജിഷ്ഠ(𑌚), മൃഞ്ജസേ(𑌟𑍁)(C) ഹാ(𑌤) ഇ(𑌶) ।ഗീ(𑌚) രാ(C)ഔ(𑌟𑌾). ഹോ(𑌖)(A) ബാ(𑌪𑍍𑌲)(G) ।ഹോ(𑌪𑍍𑌲)(D1) ഇഴാ(𑌶𑌾)॥2॥
#End of Mantra Sets -- subsection_15 ## DO NOT EDIT
```

### Example 3: `subsection_16` (Agneyam K2, Page 6) — Demonstrating Heavy Tone Column `(E)` & Inline Punctuation
```text
#Start of Mantra Sets -- subsection_16 ## DO NOT EDIT
ഉപത്വാ(E)ജാ(𑌤𑍀)।മ,യോ(𑌟𑌾). ഗീരാഃ(𑌟𑌾) ।ഓഇയായൂ_൪ദാ(𑌷𑍁) ഇ.ദിശതീ_൪ഹാ(𑌤𑍂). വിഷ്കൃതാഃ(𑌟𑌿) ।ഓ(𑌕) ഇയായൂ(𑌟𑌿𑌚𑍍)_ ൪വാ(𑌕). യോ(C)രാ(𑌟𑌾)(C) നീ(𑌤) ।കയാസ്ഥാ(𑌖𑌿) ഇരാ(𑌤𑍍𑌰𑌾) ന്।അശ്വാ(𑌥𑌾). ഗാ(𑌟)(C) വാഃ(𑌖)॥3॥ ഉപത്വാജാമാ(𑌤𑍁). യോഗീരാഃ(𑌤𑌿) ।ദാ(𑌚), ഇ(𑌶) ദിശാ(𑌕𑌾). താ,ഇ൪ഹാവി(𑌟𑍀). ഷ്കാ(𑌖) ൪താഃ(𑌣) ।വായോ(E)രനാ(𑌤𑍀). ഹാഇകാ(E)യാ(𑌤𑍀) ।സ്ഥാഇരാ(𑌟𑌿). ഔഹോ(𑌖𑌾) വാ,ഇ,ഴാ(𑌶𑌿)(G) ॥4॥
#End of Mantra Sets -- subsection_16 ## DO NOT EDIT
```

### Example 4: `subsection_20` (Agneyam K2, Page 7) — Demonstrating Light Tick `(F)` & Stacking `(G)(C)`
```text
#Start of Mantra Sets -- subsection_20 ## DO NOT EDIT
ആ(C)ശ്വാ(𑌟𑌾). ഔഹോ(𑌖𑌾) വാ(𑌶) ।നാ(C)ത്വാ(𑌟𑌾). ഔഹോ(𑌖𑌾) വാ(𑌶) । വാരവന്തം(𑌷𑍀) വന്ദ(F)ദ്ധ്യൈ(𑌤𑌿) ।ആ(C)ഗ്നാ(𑌟𑌾). ഔഹോ(𑌖𑌾) വാ(𑌶) । നമോഭി(𑌷𑌿) സ്സമ്മ്രാജ(F)ന്താം(𑌤𑍁) ।ആദ്ധ്വരാ(𑌕𑌿). ണാ(G)(C)മൌ(C)(𑌪𑌾)ഹോ(A)_ബാ(𑌪𑍍𑌲𑌾)(G) ।ഹോ(𑌪𑍍𑌲𑌾) ഇഴാ(𑌶)॥9॥ അശ്വന്നത്വാ(𑌷𑍀) വാരവ(F)ന്താം(𑌤𑍀) ।വ(𑌕)ന്ദദ്ധ്യാ(𑌷𑌿) അഗ്നിന്നമോഭാ_(𑌚𑍁) ഇഃ(𑌶) ।സം(𑌕)(G)_ മ്രാജം(𑌥𑌾).ന്താമാ(𑌚𑌾). ദ്ധ്വരാ(𑌖𑌾) ഔഹോവാഇഹോ(𑌖𑍁)ഹാ(𑌣) ഇ(𑌶) ।ഔ(𑌕)(C) ഹോ(𑌟), യാ(𑌖) ഔഹോവാ(𑌶𑌿) ।ണാം(𑌖) ॥10॥
#End of Mantra Sets -- subsection_20 ## DO NOT EDIT
```

### Example 5: `subsection_24` (Agneyam K2, Page 8) — Demonstrating Bridging Slash `(B1)` & Swarita Bar `(H)`
```text
#Start of Mantra Sets -- subsection_24 ## DO NOT EDIT
ആദിപ്രത്നാ(B1)(𑌫𑍀). സ്യരേ(𑌶𑌾) തസാഃ(𑌕𑌾) । ജ്യോതിഃപശ്യ(𑌷𑍀) ന്തിവാ_സാ(𑌟𑌿)_ രാം(H)(𑌚) । പാരോ_ യാ(𑌟𑌿). തിധ്യതാ(𑌚𑌿) ഇ(𑌶) । ദിവിഹോഇഹോ(𑌕𑍂)_ ഔ. ഹോ ഔ. ഹോ(G)വാ(𑌪𑌾)(C)(A) ഹാ_(𑌪𑍍𑌲) ബു(𑌶)(G) । ബാ(𑌖)॥15॥
#End of Mantra Sets -- subsection_24 ## DO NOT EDIT
```

### Example 6: `subsection_28` (Agneyam K3, Page 11) — Demonstrating Apex Carets `(B)`, Chevron Roofs `(D)` & `(G)(C)` Stacking
```text
#Start of Mantra Sets -- subsection_28 ## DO NOT EDIT
അഗ്നാ(𑌟𑌾), ഇമൃഴാ(𑌟𑍁). മഹം(𑌖𑌿)_ യാസീ(𑌣). । ആയആ_ദാ(𑌟𑍀). ഇവയൂ(𑌖𑍀)_ ഞ്ജാനം(𑌣) । ഈയേഥാ(𑌟𑍀) ബ൪ഹിരാ(𑌖𑌿)(G)(C) സാദാം(𑌤𑍍𑌰) ॥7॥ ആ(B)(𑌣) ഗ്നേ(𑌫). മൃഴാ(D)മാ(𑌫𑌿). ഹംയാ(D)സി(𑌫𑌿). ഓഹാ(𑌖𑌾). ഓ(𑌖) ഹാ(𑌶) । ആ(B)(𑌣)യാ(𑌫). ആദേ(D)വാ(𑌫𑌿). യുൻജ(D)നാ(𑌫𑌿). മോ(𑌖) ഹാ(𑌶). ഓ(𑌖𑌾) ഹാ(𑌶) । ഇയാഈഥാ(𑌟𑍀). ബ൪ഹിരാ(𑌖𑌾)(G)(C) സാദാം(𑌤𑍍𑌰) ॥8॥
#End of Mantra Sets -- subsection_28 ## DO NOT EDIT
```

### Example 7: `subsection_32` (Agneyam K3, Page 12) — Demonstrating Isolated `(G)`, `(F)` & Accurate Punctuation
```text
#Start of Mantra Sets -- subsection_32 ## DO NOT EDIT
ഇമമൂ(𑌤𑍀)(F) ഷൂ(𑌤𑍀) । ത്വാമാ_സ്മാ(𑌟𑌿)(C) കാം(𑌤) । സാ(C)നിം(𑌟𑌾). ഹോഇഗാ(𑌟𑍀)_ യാ(𑌟𑍀). ഹോ(G)(𑌕)_ തൃ(𑌥)ന്ന_,വ്യാം(𑌟𑌾)(C), സാം(𑌤𑌾) । ആ(C)ഗ്നേ(𑌟𑌾). ഹോഇദേ(𑌟𑍀)_ വാ(𑌟𑍀). ഹോ(𑌕𑌥𑍍). ഷുപ്രാ(C)വോ(𑌟𑌿). ചാഃ(𑌖𑌣𑍍) । ഓ(𑌪) ഇഴാ(𑌪𑍍𑌲𑌾) ॥13॥
#End of Mantra Sets -- subsection_32 ## DO NOT EDIT
```

### Example 8: `subsection_33` (Agneyam K3, Page 12) — Demonstrating Light Tick `(F)`, Shoulder Dot `(C)`, Chevron `(D)`
```text
#Start of Mantra Sets -- subsection_33 ## DO NOT EDIT
തന്ത്വാ(𑌤𑍀) ഗോ(F)പാ(𑌤𑍀) । വാ(C)നോ(𑌟𑌾). ഗാ(𑌖) ഇരാഃ(𑌣𑌾) । ജനാ(𑌚𑌾) ഇഷ്ഠാ(𑌚𑌾), ദഗ്നായാ(𑌟𑍂). ങ്ഗാ(𑌖) ഇരാഃ(𑌣𑌾) । സപൗ(𑌖𑍁) വാ(𑌶)_ ഉവോ(𑌖𑍁) വാ(𑌶). കൗ(𑌖𑌿) വാ(𑌣)_ ഉവോ(𑌖𑌿) വാ(𑌣) । ശ്രുധീ(𑌪𑍍𑌲𑍀)(D) ഹവാം(𑌪𑍍𑌲𑍀)(G) । ഹോ(𑌪) ഇഴാ(𑌶𑌾) ॥14॥
#End of Mantra Sets -- subsection_33 ## DO NOT EDIT
```

### Example 9: `subsection_34` (Agneyam K3, Pages 12 & 13) — Demonstrating Compound `(C)(G)` & Slur Arc `(A)`
```text
#Start of Mantra Sets -- subsection_34 ## DO NOT EDIT
പരിയൗ(𑌷𑍀) ഹോ(𑌷𑍀) ഇവാ(𑌤𑌿)(F)ജാ(𑌤𑌿) । പാതാ(𑌚𑌾)_ ഇഃ(𑌚𑌾) കാ(𑌯𑌾)_ വീഃ(𑌟) । അ_ഗ്നീ(𑌚𑌾), ൪ഹവ്യാ(𑌥𑌾)_ ന്നാ(𑌟). യഃ(𑌟𑌿)ക്രമീ(𑌟𑌿) ത് । ദധാ(𑌟𑌿𑌟𑍍)(C) ദ്രാ(𑌟𑌿𑌟𑍍). ത്നാ(𑌶𑌿) ഔഹോവാ(𑌶𑌿) । നിദാ(𑌤𑌾). ശൂ(C)ഷേ(𑌟𑌾𑌖𑍍) ॥15॥ ഉദുത്യമോ(𑌤𑍀)(C) ഹാ(𑌤) ഇ(𑌶) । ജാതാവേ(𑌕𑌿). ദാ(𑌖) സം(𑌣) । ദേ(𑌕)_വം(𑌕) വഹന്തീകേ(𑌕𑍁). താ(𑌖) വാഃ(𑌣) । ദാ൪ശേ(𑌪𑌾) ഹാ(𑌣) ഇ(𑌶) । വാഇശ്വാ(𑌕𑌿𑌚𑍍) യാ(𑌕). സൂ൪യാ(C)(G)മൗ(𑌪𑌿)(C) ഹോ(𑌪𑍍𑌲)(A)_ ബാ(𑌪𑍍𑌲𑌾)(G) । ഹോ(𑌪𑍍𑌲) ഇഴാ(𑌶𑌾) ॥16॥
#End of Mantra Sets -- subsection_34 ## DO NOT EDIT
```

### Example 10: `subsection_35` (Agneyam K3, Page 13) — Demonstrating Overhead Swarita `(H)` & Shoulder Dots `(C)`
```text
#Start of Mantra Sets -- subsection_35 ## DO NOT EDIT
കവിമഗ്നീം(𑌤𑍀) । ഉപാ(𑌟𑌿𑌚𑍍)(C) സ്തു(𑌖), ഹാ(𑌶) ഔഹോവാ(𑌶) । സത്യധ(𑌕𑍀)_ ൪മ്മാണം(𑌚𑌾) അ_ദ്ധ്വ(𑌚𑌾), രേ(H) । ദേവാ(𑌤𑍀), മമീ(𑌤𑍀). വാചാ(𑌣𑌾)(C) താ(𑌪). നാം । ഓ(𑌪𑍍𑌲) ഇഴാ(𑌶𑌾) ॥17॥
#End of Mantra Sets -- subsection_35 ## DO NOT EDIT
```

### Example 11: `subsection_36` (Agneyam K3, Page 13) — Demonstrating Compound `(B1)(D2)` & `(F)` / `(C)`
```text
#Start of Mantra Sets -- subsection_36 ## DO NOT EDIT
ശന്നോദേ(𑌤𑍀)(F) വീഃ । ആഭീ(𑌟𑌿)(C) ഷ്ടാ(𑌟𑌿). യാ(𑌖) ഇശന്നോഭുവാം(𑌶𑍁) । തൂപീ(𑌟𑌿)(C) താ(𑌟𑌿). യാ(𑌖) ഇശയ്യോരഭീഃ(𑌶𑍁) । സ്രാവ(C)ന്തൂ(𑌟𑌿𑌟𑍍). നാ(𑌖) ഔഹോവാ(𑌶𑌿) । ഊ(𑌖) പാ(𑌶) ॥18॥ ഹുവാ(𑌤𑌾)(A), ഹോ(𑌪) ഇശന്നോദേവീ(𑌪𑍍𑌲𑍁)(B1)(D2) രഭിഷ്ടയാ(𑌙𑌿) ഇ(𑌶) । ഹുവാ(𑌤𑌾)(G). ഹോ(𑌪) ഇശന്നോഭുവാ(𑌪𑍍𑌲𑍁)(B1)(D2) ന്തൂപീതായാ(𑌙𑍀) ഇ(𑌶) । ഹുവാ(𑌤𑌾)(G). ഹോ(𑌪) ഇശയ്യോരഭീ(𑌪𑍍𑌲𑍁)(B1)(D2) സ്രവന്തു(𑌙𑌿) നാഃ(𑌶) । ഹുവാ(𑌤𑌾)_ ഹോ(𑌟). യാ(𑌖) ഔഹോവാ(𑌶𑌿) । ഊ(𑌖) പാ(𑌶) ॥19॥
#End of Mantra Sets -- subsection_36 ## DO NOT EDIT
```

### Example 12: `subsection_37` (Agneyam K3, Pages 13 & 14) — Demonstrating `(B1)`, `(D)`, Compound `(G)(C)`
```text
#Start of Mantra Sets -- subsection_37 ## DO NOT EDIT
കസ്യാനൂ(𑌟𑍀)_ നാം(𑌟𑍀). പരീ_ണാ(𑌖𑌿) സീ(𑌣) । ധീയോജിന്വാ(𑌟𑍀). സീസാ(𑌖𑌿)_ ത്പാതാ(𑌣) ഇ(𑌶) । ഗോ(𑌚)(G)_ ഷാതാ(𑌚𑌾)_ യാസ്യാ(𑌟𑌾𑌟𑍍). താ(𑌖) ഔഹോവാ(𑌶𑌿) । ഉബ്ഗ്ഗീ(𑌖𑌾)(B1) രാഃ(𑌶) ॥20॥ ഓ(𑌕)_(G) ഹൊ(𑌥𑌾)വാ(𑌥𑌾)_ ഇഹുവാ(𑌟𑌿) ഇഹു(𑌚𑌿)_ വാ(𑌚𑌿)(C)ഏ(𑌤) । കസ്യനൂ(𑌖𑍀)(G)(C) നാം(𑌖𑍀). പാരീ(𑌚𑌾). ണാ(D)സീ(𑌫𑌾) । ഓ(𑌕)(G)_ ഹൊ(𑌥𑌾) വാ(𑌥𑌾)_ ഇഹുവാ(𑌟𑌿). ഇഹു(𑌚𑌿)_ വാ(C)(𑌚𑌿) ഏ(𑌤) । ധീയൊജിന്വാ(𑌖𑍀). സീസാ(𑌚𑌾). ത്പാ(D)തീം(𑌫𑌾) ഇ । ഓ(𑌕)_ ഹൊ(𑌥𑌾) വാ(𑌥𑌾)_ ഇഹു_വാ(𑌟𑌿). ഇഹു(𑌚𑌿)_വാ(𑌚𑌿)(C)ഏ(𑌤) । ഗോഷാതായസ്യതാ(𑌖𑍂)(G)(C) ഗാ(𑌖𑍂) ഇ(𑌶) । രാഃ(𑌤𑍍𑌰) ॥21॥
#End of Mantra Sets -- subsection_37 ## DO NOT EDIT
```

### Example 13: `subsection_38` (Agneyam K4, Page 14) — Demonstrating Compound `(D1)(C)`, `(G)_`, `(C)`
```text
#Start of Mantra Sets -- subsection_38 ## DO NOT EDIT
യജ്ഞായജ്ഞാ(𑌤𑍀) । വോ(𑌤). ഗ്നയാ(𑌤𑌾). ഇഗിരാ(𑌟𑌿). ഗിരാ(𑌖𑌾)(C) ഹാ(𑌪𑍍𑌲)(C) ഹാ(𑌤). ഇചാ(𑌚𑌾)(C) ദക്ഷാ(𑌖𑌾) സാ(𑌣) ഇ(𑌶) । പ്രപ്രാ(𑌟𑌾𑌚𑍍). വയമമൃത(𑌷𑍀) ജാതാവേ(𑌯𑌿). ദാസാം(𑌟𑌾) । പ്രിയം(𑌚𑌾) മിത്രാ(𑌕𑌿)_ ന്നാ(𑌕𑌿). ശംസിഷാ_മേ(𑌕𑍀). ഹിയാ ഔഹോ ഔഹോ(𑌖𑍂)(C) ഇഴാ(𑌪𑍍𑌲𑌾)(D1)(C) ॥१॥ യജ്ഞായജ്ഞാ(𑌤𑍀) । ഹോ(𑌤), ഇവോ(𑌤𑌾), ഗ്നായാ(𑌕𑌾). ഏ(𑌖) ഹിയാ(𑌣𑌾) । ഗിരാ(𑌕𑌾𑌚𑍍)(G)_ ഗീ(𑌚)രാ(𑌟𑌾)ചാ(𑌚). ദാ(𑌚)_ ക്ഷസാ(𑌚𑌾) ഇ(𑌶) । പ്രപ്രാ(𑌥𑌾𑌚𑍍). വായാ(𑌚𑌾) മാ(𑌕) മൃതൻ,ജാതാവേ(𑌟𑍁). ദാ(𑌖) സം(𑌣) । പ്രീയ(𑌚𑌾)മ്മിത്രാ(𑌕𑌿)_ ന്നാ(𑌕𑌿). ശംസിഷാ_മേ(𑌕𑍀). ഹിയാ.ഔഹോ(𑌖𑌾)(C) ഇഴാ(𑌪𑍍𑌲𑌾)(D1) ॥2॥
#End of Mantra Sets -- subsection_38 ## DO NOT EDIT
```

### Example 14: `subsection_39` (Agneyam K4, Pages 14 & 15) — Demonstrating Phrasing Underbars
```text
#Start of Mantra Sets -- subsection_39 ## DO NOT EDIT
യാജ്ഞായാ(𑌟𑍀)_ ജ്ഞാ(𑌟𑍀). വോഅഗ്നായാ(𑌟𑍀) ഇ(𑌶) । ഗാഇരാഗാ_ഇ(𑌟𑍂)രാ(𑌟𑍂). ചാദക്ഷാസാ(𑌟𑍀) ഇ(𑌶) । പ്രപ്രാ(𑌟𑍀𑌚𑍍)വാ_യാ(𑌟𑍀𑌚𑍍). മാ(𑌕) മൃതൻ,ജാ(𑌕𑌿) താവേ(𑌟𑌾). ദാ(𑌖) സം(𑌣) । പ്രാ(𑌚)_ യാ(𑌯)_ മ്മാഇ(𑌚𑍀)ത്രാ_ന്നാ(𑌚𑍀)_ ശാം(𑌯)_ സാ(𑌟). ഇഷാം(𑌖𑌾𑌣𑍍) । ഓ(𑌪) ഇഴാ(𑌪𑍍𑌲𑌾) ॥3॥
#End of Mantra Sets -- subsection_39 ## DO NOT EDIT
```

### Example 15: `subsection_40` (Agneyam K4, Page 15) — Demonstrating `(D)`, Compound `(G)(C)`
```text
#Start of Mantra Sets -- subsection_40 ## DO NOT EDIT
യജ്ഞാ(𑌣𑌾)(G). യജ്ഞാ(𑌣𑌾)(D) വോ(𑌫). അഗ്നാ(𑌖𑌾) യാ(𑌣) ഇ(𑌶) । ഗാഇരാ(𑌟𑍂), ഗിരാ(𑌟𑍂)_ ചാ(𑌟𑍂). ദാ(𑌪𑌾)(G)(C) ക്ഷാസാഇ(𑌶𑌾) । പ്രപ്രാ(𑌟𑌾𑌚𑍍). വയമമൃതൻജാതാ(𑌪𑍂). വാ(𑌶) ഹിമ്മാ(𑌚𑌾) ഇ(𑌶) । ദാ(𑌤)(C) സാം(𑌤) । പ്രായമ്മിത്രാന്നാശാം(𑌕𑍂). സിഷാ(𑌕𑌾) ബു(𑌶) । ബാ(𑌖) ॥4॥
#End of Mantra Sets -- subsection_40 ## DO NOT EDIT
```

### Example 16: `subsection_41` (Agneyam K4, Page 15) — Demonstrating Compound `(G)(C)`, `(A)`
```text
#Start of Mantra Sets -- subsection_41 ## DO NOT EDIT
പാഹിനൊ(𑌖𑍀)(G)(C) ആ(𑌖𑍀)(A)ഗ്നാ(𑌖𑍀)_ ഏകയാ(𑌪𑍍𑌲𑍀)(G) । പാ(𑌚)_ ഹ്യുതദ്വിതാ (𑌚𑍀)_ ഇയാ(𑌯𑌾)_ യാ(𑌟) । പാഹീ(𑌟𑌿)_ ഗീ(𑌟𑌿). ൪ഭിസ്തിസൃഭീരൂ(𑌚𑍁)_ ൪ജാം(𑌕)_ പാ(𑌯)_ താ(𑌟) ഇ(𑌶) । പാഹീ(𑌕𑌾)(G)(C) ചാതൗ(𑌕𑌾). ഹോ(𑌤)(C) വാ(𑌤)।സ്രഭി൪വാ(𑌟𑌿). സാ(𑌖𑌣𑍍) ബു(𑌶) । ഓ(𑌪) ഇഴാ(𑌪𑍍𑌲𑌾) ॥5॥
#End of Mantra Sets -- subsection_41 ## DO NOT EDIT
```

### Example 17: `subsection_42` (Agneyam K4, Pages 15 & 16) — Demonstrating Compound `(C)(G)`, `(A)`
```text
#Start of Mantra Sets -- subsection_42 ## DO NOT EDIT
പാഹീനൊ(𑌷𑌿) അഗ്നഏകയാ(𑌤𑍁)(C) ഏ(𑌤) । പാ(𑌕)(G)_ ഹാഉതാ(𑌟𑌿). ദ്വിതാ(𑌪𑍀)(C)(G) ഇയാ(𑌪𑍀) യാ(𑌶) । പാ(C)ഹാ(𑌟𑌾). ഇഗാ(𑌖𑌾) ഇ൪ഭീഃ(𑌣𑌾) । താഇസൃഭീരൂ(𑌕𑍁). ൪ജാമ്പാ(𑌟𑌿)_ താ(𑌟𑌿). ഔഹോഔഹോ(𑌖𑍀) വാ(𑌣) । പാ(𑌪). ഹീഹാ(𑌚𑌾) ഇ(𑌶) । ചാ(𑌕)(G)_ താസൃഭാ(𑌟𑌿). ഔഹോഔഹോ(𑌖𑍀) വാ(𑌣) । വാ(𑌪)(C) സാ(𑌪), വെഹി(A)യാ(𑌪𑍍𑌲𑍁)_ ഹാ(𑌪𑍍𑌲𑍁)(G) । ഹോ(𑌪𑍍𑌲) ഇഴാ(𑌶𑌾) ॥6॥
#End of Mantra Sets -- subsection_42 ## DO NOT EDIT
```

### Example 18: `subsection_43` (Agneyam K4, Page 16) — Demonstrating Compound `(A)(B1)`, `(H)`, `(F)`
```text
#Start of Mantra Sets -- subsection_43 ## DO NOT EDIT
പാഹിനൊ(𑌫𑍂)അഗ്നഏ(𑌫𑍂).(H) കയാ(𑌤𑌾)(G). പാ(𑌪). ഹ്യൂതദ്വീതീ(𑌪𑍍𑌲𑍀)(A)(B1) യാ(𑌙) യാ(𑌶) । പാഹിഗീ൪ഭീ(𑌷𑍀)സ്തിസൃഭിരൂ൪ജ്ജാം(𑌖𑍂)(F) പാ(𑌖𑍂) താ(𑌣) ഇ(𑌶) । പാ(G)ഹാ(𑌚𑌾) ഇ(𑌶) । ചാ(𑌖) താഹാഓവാ(𑌶𑍀) । സൃഭി൪വസോ(𑌤𑍀)(G). । ഊ(𑌟)(C) പാ(𑌖) ॥7॥
#End of Mantra Sets -- subsection_43 ## DO NOT EDIT
```

---

## 2. THE COLOR RULE (critical — this is the K2 pilot fix)

The manuscript is printed/written in **two inks**:

| Ink | What it is | Action |
|---|---|---|
| **RED** | Grantha swara *letters* and their handwritten flourishes (e.g. തി, ത്ത്, ഖ, ടു, and the hook/"4"-shaped ligatures). These are the swara markers **already transliterated from Devanagari** and already present in the master body as parenthesized Grantha tokens. | **IGNORE unconditionally.** Never emit a modifier token for anything red. Never transcribe a red mark into the body. |
| **BLACK** | Base Malayalam aksharas, dandas, numerals — **and the swara modifiers** (arcs, slashes, dots, bars, carets, checkmarks, crosses, underbars, commas, periods). | Extract the **non-base black marks** as modifier/inline tokens. |

> The previous (v1) pilot failed because it hunted *red* marks for modifiers.
> In the real manuscript, modifiers are written in the **same black pen as the
> base text**. Red ink is reserved for Grantha swara letters which are already
> captured downstream. **If you look at red ink for modifiers, you are doing it
> wrong.**

Spot-check before annotating: confirm you can see black period-dots after
words, black commas, black underbar connectors, and (for Kandah 2) many
black under-slashes. If you cannot see any black non-base marks on a line,
re-scan that line at higher zoom before concluding there are none.

---

## 3. Canonical Token Lexicon

From `Malayalam_JSV/glyph_table.html` (18 modifiers & marks).
Write tokens exactly as shown in the "Token" column.

| Token | Name | Ink | Shape & Position | Stacking / Footprint |
|---|---|---|---|---|
| `(A)` | Syllable-spanning arc | black | Flat/slur arch **above** the line, bridging two adjacent syllables/words | 2 syllables, above |
| `(A1)` | Arc over danda | black | Same arch centered **over a danda `।`** between phrases | over `।` |
| `(B)` | Peak caret roof | black | `^`-shaped roof **above** a syllable; carries a swara glyph on its apex | above, 1–2 syl |
| `(B1)` | Bridging slash | black | Diagonal bridging stroke (`/` / `↗`) **above/between** syllables with swara above | above/between syl |
| `(C)` | Shoulder dot | black | Small round dot at the **upper-right shoulder** of a syllable (`·`) | upper-right shoulder |
| `(D)` | Chevron roof | black | Wide `Ʌ`-shaped symmetrical roof **above** the line, spanning **2+ syllables across a word boundary** | above, 2+ syl |
| `(D1)` | Hooked rise / Inverted-V | black | Asymmetrical inverted-V (`⋀`) with long rising left leg and short downward right hook **above/between** syllables | above/between syl |
| `(D2)` | Shoulder check-mark tick | black | Check-mark tick (`✓`) on the **upper-right shoulder** of an akshara | upper-right shoulder |
| `(I)` | Double shoulder dash | black | Two stacked parallel gently-rising bars (`═`) on the **upper-right shoulder** | upper-right shoulder |
| `(J)` | Horizontal shoulder bar | black | Horizontal straight bar (`—`) on the **upper-right shoulder** | upper-right shoulder |
| `(K)` | Shoulder cross mark | black | Bold cross / X mark (`⨯` / `x`) on the **upper-right shoulder** | upper-right shoulder |
| `(E)` | Heavy tone column | black | Bold vertical stroke **inline** at baseline height (heavier than a danda) | inline |
| `(F)` | Light tick | black | Thin short vertical tick **inline** | inline |
| `(G)` | **Descending slash** | black | Short straight/curved diagonal stroke attached **below** the baseline at the **bottom-right** of a single akshara; looks like a small `\`, `L`, or `4`-hook hanging beneath the character | **below, 1 syllable** |
| `(H)` | Swarita bar | black | Vertical stroke **above** and centered on a syllable (Vedic swarita) | above, 1 syl |
| `(L)` | Lower danda | black | Downward stem/inline bar (deep cadence) | inline |
| `_` | Sustain underbar | black | Horizontal low-line **connecting words at the baseline** (joins two adjacent mantra units) | inline, between words |
| `.` | Pause dot | black | Dot **inline at the baseline** after a word (stobha/breath pause) | inline |
| `,` | Low comma | black | Comma **inline** at baseline (minor cadence pause) | inline |

Notes:
- Dandas `।` (single) and `॥` (double) are **base punctuation**, already
  present in the master body. Never wrap them as a modifier.
- Numerals inside `॥ N ॥` samam-end markers are base text. Leave them.
- Grantha swara parenthesized tokens like `(𑌤𑌿)` already exist in the
  master body. Leave them untouched; only insert modifier tokens around them.

---

## 4. Density Priors & Corpus Insights

From the curated Ground Truth across Agneyam Kandahs 1, 2, and 3 (`sub_1`–`sub_37`):

| Modifier | Typical Share | Key Behavioral Notes |
|---|---|---|
| `(C)` | ~45% | Most frequent shoulder mark overall. Always attached at upper-right shoulder. |
| `(G)` | ~18% | Independent downward diagonal stroke beneath baseline (e.g. `ഹോ(G)`, `ബാ(𑌪𑍍𑌲)(G)`). **NEVER emit in chains across normal words or syllables.** |
| `(H)` | ~12% | Overhead vertical Vedic swarita bar. |
| `(A)` / `(A1)` | ~8% | Syllable-spanning slur `(A)` or centered over danda `(A1)`. |
| `(D1)` / `(D)` | ~6% | Hooked rise `(D1)` (asymmetrical inverted-V) vs wide chevron roof `(D)` (spanning across word boundaries). |
| `(B)` / `(B1)` | ~3% | Peak caret `(B)` (apex-seated swara) vs diagonal bridging slash `(B1)`. |
| `(E)`, `(F)` | ~3% | Heavy inline column `(E)` vs light vertical tick `(F)`. |
| `(D2)`, `(I)`, `(J)`, `(K)` | ~2% | Shoulder extended marks in special sections and Bruhati. |

**Compound Stacking Rules (Observed in Kandah 2, 3 & 4)**:
- `(G)(C)` / `(C)(G)`: Akshara carries both an under-slash `(G)` and a shoulder dot `(C)` (e.g., `ബ൪ഹിരാ(𑌖𑌿)(G)(C)`, `സൂ൪യാ(C)(G)`, `പാഹിനൊ(𑌖𑍀)(G)(C)`).
- `(G)(D1)`: Akshara carries an under-slash `(G)` and a hooked rise `(D1)` (e.g., `ഇഴാ(𑌪𑍍𑌲𑌾)(G)(D1)`).
- `(D1)(C)`: Akshara carries a hooked rise `(D1)` and a shoulder dot `(C)` (e.g., `ഇഴാ(𑌪𑍍𑌲𑌾)(D1)(C)`).
- `(B)(H)`: Akshara carries a peak caret `(B)` with a vertical swarita bar `(H)` directly on its apex (e.g., `ശ്രുധീ(𑌪𑍍𑌲𑍀)(B)(H)`).
- `(B1)(D2)`: Grantha swara carries a diagonal bridging slash `(B1)` and a check tick `(D2)` (e.g., `ദേവീ(𑌪𑍍𑌲𑍁)(B1)(D2)` in K3 `sub_36`).
- `(A)(B1)`: Grantha swara carries a melodic slur arc `(A)` and a diagonal bridging slash `(B1)` (e.g., `ഹ്യൂതദ്വീതീ(𑌪𑍍𑌲𑍀)(A)(B1)` in K4 `sub_43`).

---

## 5. Multi-Pass Protocol (mandatory per crop)

### Pass 1 — Transcription & all-mark scan
For each mantra line on the crop:
1. Locate the corresponding master body (the anchor). Copy it verbatim.
2. Walking left→right over the manuscript line, insert every **black** mark
   you can identify at the correct akshara, using the lexicon above.
3. If a samam continues across a crop boundary (e.g. samam 6 split as
   `k2_samam_5_6a.png` / `k2_samam_6b_7.png`), read **both** crops before
   annotating that samam, so the split is not double-counted or missed.

### Pass 2 — Dedicated `(G)` Under-Slash Verification (Anti-False-Positive Filter)
When inspecting the area **below the baseline at the bottom-right of an akshara**:
- **Positive `(G)` Criteria**: An **independent, intentional black diagonal slash / under-tick** (e.g. `\`, `L`, or `4`-hook) attached distinctly beneath the consonant stem (e.g., `ബാ(𑌪𑍍𑌲)(G)`, `വീശേ(𑌕𑌾)(G)`, `സം(𑌕)(G)_`).
- **CRITICAL False-Positive Exclusions (Do NOT emit `(G)`)**:
  - **Intrinsic Malayalam Glyphs & Conjunct Descenders**: Do **NOT** mistake standard Malayalam letter anatomy for `(G)`:
    - Subscript tails in `ഷ്ഠ`, `ല്ല`, `റ്റ`, `ശ്ച`, `ന്ധ`, `ജ്ഞ`, `ത്ഥ`.
    - Right-tail vowel/consonant loops in `യാ`, `പോ`, `വോ`, `രാ`.
    - Standard vowel signs `ു` (u), `ൂ` (oo), `ൃ` (ri).
  - **Ruled Notebook Lines & Ink Bleeds**: Do not count ink contact with the horizontal blue/red notebook ruled line as `(G)`.
  - Only emit `(G)` when there is a **separate, clearly drawn diagonal stroke** beneath the character.

### Pass 3 — Shoulder Marks Sweep (`(C)`, `(D2)`, `(I)`, `(J)`, `(K)`)
Scan the **upper-right shoulder** of every akshara for raised black marks:
- **Round dot** $\rightarrow$ `(C)` (distinguish from baseline `.` pause dots — see §6).
- **Check-mark tick `✓`** $\rightarrow$ `(D2)`.
- **Double parallel horizontal/gently-slanted bars `═`** $\rightarrow$ `(I)`.
- **Single horizontal bar `—`** $\rightarrow$ `(J)`.
- **Cross / X mark `⨯`** $\rightarrow$ `(K)`.

### Pass 4 — Overhead & Syllable-Spanning Sweep (`(A)`, `(A1)`, `(B)`, `(B1)`, `(D)`, `(D1)`, `(H)`)
Inspect the area **above the header line** between and above syllables:
- **Smooth curved arch** $\rightarrow$ `(A)` (or `(A1)` if centered over `।`).
- **Inverted-V with long rising stroke & short hook** $\rightarrow$ `(D1)`.
- **Wide symmetrical chevron** $\rightarrow$ `(D)`.
- **Rising diagonal slash with swara above** $\rightarrow$ `(B1)`.
- **Peak caret roof with swara on apex** $\rightarrow$ `(B)`.
- **Vertical overhead swarita line** $\rightarrow$ `(H)`.

Only after all four passes, emit the annotated line.

### Samam boundary rule (critical)

A modifier mark belongs to the **samam in which it was detected**. It must
**not** carry over into the next samam. Concretely:

- The `॥ N ॥` numeral marker terminates a samam. Any modifier on an akshara
  **before** the marker belongs to samam N; any modifier on an akshara
  **after** the marker belongs to samam N+1.
- When a modifier visually sits at the boundary (e.g., an arc or underbar
  near the danda), assign it to the samam whose text it physically annotates
  — never push it forward.
- Each samam line in the candidate is annotated independently. Do not let
  a modifier detected in one samam "leak" into the next line.

---

## 6. Disambiguation Rules

| Confusion | Rule |
|---|---|
| `(G)` vs `(D)` | `(G)`: **narrow, below** the baseline, attached to **one** akshara, looks like `\`/`L`/`4`. `(D)`: **wide chevron above** the line, spanning **2+ syllables across a word boundary**. When a below-baseline single-akshara mark is ambiguous between G and D → **choose `(G)`**. |
| `(D1)` vs `(D)` vs `(A)` | `(A)` is a **smooth flat arch** (slur). `(D)` is a **wide symmetrical chevron roof `Ʌ`**. `(D1)` is an **asymmetrical inverted-V `⋀`** with a long rising left diagonal stroke and a short downward right hook. |
| `(B1)` vs `(D1)` | `(B1)` is a straight **diagonal bridging slash `/`** that carries a swara letter directly above it. `(D1)` is an **inverted-V / bent peak stroke `⋀`** without an apex-seated letter. |
| `(D2)` vs `(C)` | `(D2)` is a **check-mark tick `✓`** (left dip + right rise) at the upper-right shoulder. `(C)` is a **round dot `·`** at the shoulder. |
| `(I)` vs `(J)` vs `(K)` | All sit on the **upper-right shoulder**: `(I)` = **two stacked parallel bars `═`**; `(J)` = **single horizontal bar `—`**; `(K)` = **cross / `X` mark `⨯`**. |
| `(J)` vs `_` | `(J)` sits **raised at the upper-right shoulder** of an akshara. `_` sits **inline at the baseline** connecting two adjacent words. |
| baseline `.` vs `(C)` | `.` sits **inline at the baseline** after a word (stobha pause). `(C)` sits **raised at the upper-right shoulder** of a syllable (Bindu-Svara). Both are black dots; position decides. |
| `_` vs decorative flourish | `_` is a **baseline low-line that connects two adjacent words/units**. A long ornamental underline beneath a samam's opening word (often wavy, spanning the whole word) is **decoration — skip it**, do not emit `_`. |
| danda `।`/`॥` vs `(E)`/`(L)` | Dandas are base punctuation (already in the master body). `(E)` is a **bold inline column heavier than a danda**; `(L)` is a downward stem. Only emit `(E)`/`(L)`/`(F)` for marks clearly heavier/lighter than the surrounding dandas. |
| red hook/"4"-shape | Red ink = swara-letter flourish → **ignore**. A black `4`/`L`-hook **below** an akshara is `(G)`. |

---

## 7. Anchor & Output Contract

For each subsection you are given:
1. The master mantra body (one line per samam), verbatim, e.g.:
   ```text
   ദൂ(𑌣) താം(𑌫)(D1). വോ(𑌖) വിശ്വവേദസാം(𑌶𑍁) ।ഹാ(𑌥) വ്യാവാ(𑌚), ഹാ(𑌟) മമാ(𑌟𑍁). ൪ത്താ(𑌖) യം(𑌣) ।യാ(𑌚)_ ജിഷ്ഠ(𑌚), മൃഞ്ജസേ(𑌟𑍁)(C) ഹാ(𑌤) ഇ(𑌶) ।ഗീ(𑌚) രാ(C)ഔ(𑌟𑌾). ഹോ(𑌖)(A) ബാ(𑌪𑍍𑌲)(G) ।ഹോ(𑌪𑍍𑌲)(D1) ഇഴാ(𑌶𑌾)॥2॥
   ```
2. The matching manuscript crop(s).

Your output for that subsection is the same body with modifier tokens
**inserted** at the correct positions. Do not:
- reorder, delete, or add base aksharas
- change any `(𑌶𑌾)`-style Grantha parenthesized token
- change dandas, numerals, or whitespace runs
- introduce tokens outside the canonical lexicon in §3

Emit the candidate in the exact structural skeleton the merge tool expects
(see `Malayalam_JSV/extraction/merge_candidates.py` `SUBSECTION_RE`):

```
# Start of SubSection Title -- subsection_NN ## DO NOT EDIT
<title verbatim>
# End of SubSection Title -- subsection_NN ## DO NOT EDIT
#Start of Mantra Sets -- subsection_NN ## DO NOT EDIT
<annotated mantra line 1>
<annotated mantra line 2>
...
#End of Mantra Sets -- subsection_NN ## DO NOT EDIT
```

One body line per samam, matching the master's line layout exactly.

---

## 8. Uncertainty

Do **not** pollute the candidate file with annotations like `(?)`. If a mark
is genuinely unreadable, make your best-guess call inside the candidate
(per the disambiguation rules) and record the uncertain position in a separate
notes file `<candidate_basename>_notes.txt` in the same directory, e.g.:

```
subsection_18 samam_6 akshara "ഹാ(𑌟)" : unclear mark below baseline, guessed (G)
```

The merge tool only reads the candidate `.txt`; the notes file is for the
human curation pass in the interactive tool.

---

## 9. Pre-Emit Self-Checklist

Before writing a candidate file, verify:
- [ ] **Zero** red marks were transcribed as modifiers.
- [ ] `(G)` count is not suspiciously low (K2: expect several per samam).
- [ ] Every akshara's bottom-right was inspected for `(G)`.
- [ ] Baseline `.` vs raised `(C)` distinction held.
- [ ] Connecting `_` (between words) vs decorative flourish (single word)
      distinction held.
- [ ] Base text, Grantha parens, dandas, numerals are byte-identical to the
      master anchor (run `validate_modifiers.py` mentally; the merge tool
      will reject on any mismatch).
- [ ] No tokens outside the §3 lexicon.
- [ ] Split samams were annotated using both adjacent crops.
- [ ] Uncertain positions logged to `_notes.txt`, not into the candidate.

After emitting, the candidate will be validated by
`Malayalam_JSV/extraction/validate_modifiers.py` (zero base-text regressions
required) and scored by `Malayalam_JSV/extraction/eval_modifiers.py`
(token-level precision/recall vs ground truth).
