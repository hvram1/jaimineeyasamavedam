# Jaimineeya Samavedam Typography Guide

This document outlines the font mapping and typography rules applied across the website. Use this as a reference for fine-tuning the visual appearance.

## 🏛️ Core Fonts

| Font Family | Visual Style | Usage |
| :--- | :--- | :--- |
| **Adishila Vedic** | Traditional Serif | Sanskrit text, Mantra metadata, Traditional labels |
| **Adishila San Vedic** | Modern Sans-serif | Numerals, Counts, Navigation links, Table data |

---

## 📊 Master Typography Table

This table provides a comprehensive summary of UI elements, their fonts, and current sizes.

| Page Type | UI Element | Font Family | Size | Color | Example String | CSS Selector |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **🌍 Global** | Sidebar Logo Title | Adishila Vedic (Serif) | 1.8rem | Saffron (#FF6B35) | **जैमिनीय साम संहिता** | `.logo-text` |
| | Sidebar Logo Subtitle| Adishila Vedic (Serif) | 1rem | Muted Gray (#6B6B6B) | **Jaimineeya Sama...** | `.logo-subtitle` |
| | Sidebar Labels | Adishila Vedic (Serif) | 1.15rem | Charcoal (#2C2C2C) | **पर्व:, खण्ड:, साम:** | `.nav-section h3` |
| | Sidebar Pills | Adishila San (Sans) | 0.7rem | Dark Gray (#4A4A4A) | **1, 10, 20** | `.nav-links a` |
| | Jump to Input | Adishila San (Sans) | 0.9rem | Charcoal (#2C2C2C) | **e.g. 1.1.1** | `.jump-input` |
| | Search Button | Adishila Vedic (Serif) | 1.0rem | Brown (#8B4513) | **अन्वेषणम् (Search)** | `.search-btn` |
| | Footer Nav Buttons| Adishila Vedic (Serif) | 1.0rem | Saffron (#FF6B35) | **ऋषयः, देवताः** | `.footer-btn` |
| | Jump Nav Labels | Adishila Vedic (Serif) | 0.85rem | Muted Gray (#6B6B6B) | **साम: (19)** | `.sidebar-right h3` |
| | Jump Nav Icons | Adishila San (Sans) | 0.7rem | Dark Gray (#4A4A4A) | **1, 10, 20** | `.jump-links a` |
| **🏠 Home** | Hero Page Title | Adishila Vedic (Serif) | 3.0rem | Charcoal (#2C2C2C) | **जैमिनीयसामवेद: (Jaimineeya Samavedam)** | `.home-hero h1` |
| | Stats Values | Adishila San (Sans) | 2.2rem | Saffron (#FF6B35) | **6, 125, 1222** | `.stat-value` |
| | Stats Labels | Adishila Vedic (Serif) | 1.3rem | Muted Gray (#6B6B6B) | **पर्व: (Parva)** | `.stat-label` |
| | Indices Section Title| Adishila Vedic (Serif) | 2.2rem | Charcoal (#2C2C2C) | **अन्य वर्गीकरणम् (Indices)** | `.anya-vargeekaran-card h2` |
| | Index Pill Title | Adishila Vedic (Serif) | 1.5rem | Saffron (#FF6B35) | **ऋषयः (Rishi)** | `.index-link-item .title` |
| | Index Pill Count| Adishila San (Sans) | 0.8rem | Gray (#888) | **(172)** | `.index-link-item .stats` |
| **📖 Kandah** | Page Title | Adishila Vedic (Serif) | 1.8rem | Charcoal (#2C2C2C) | **अर्चिकपर्व - प्रथमः खण्डः** | `h1` |
| | Header Metadata | Adishila Vedic (Serif) | 1.1rem | Dark Gray (#4A4A4A) | **पर्व: १, खण्ड: १ | साम: १९** | `.page-subtitle` |
| | Metadata Numerals | Adishila San (Sans) | 0.8rem | Dark Gray (#4A4A4A) | **1, 12, 19** | `.page-meta .number` |
| | TOC Header | Adishila Vedic (Serif) | 1.2rem | Charcoal (#2C2C2C) | **खण्ड: 1 - सम्पूर्णम्** | `.toc h4` |
| | TOC Pills | Adishila San (Sans) | 0.9rem | Dark Gray (#4A4A4A) | **१.१.१, १.१.२** | `.toc-list li a` |
| **🕉️ Mantra** | Sama ID Badge | Adishila San (Sans) | 0.9rem | Saffron (#FF6B35) | **1.1.1** | `.sama-id` |
| | Metadata Line | Adishila Vedic (Serif) | 1.6rem | Purple (#7B1FA2) | **॥ भरद्वाजो बार्हस्पत्यः ... ॥** | `.rik-metadata` |
| | Class. Table Head | Adishila Vedic (Serif) | 1.1rem | White (#FFFFFF) | **Global #, ऋषिः, देवता** | `.classification-table th` |
| | Class. Table Values| Adishila Vedic (Serif) | 1.3rem | Charcoal (#2C2C2C) | **अग्निः, त्रिष्टुप्** | `.class-value` |
| | Table Numerals | Adishila San (Sans) | 0.9rem | Dark Gray (#4A4A4A) | **1, 10, 20** | `.sama-entry .number` |
| | Rik Text (Blue) | Adishila Vedic (Serif) | 1.6rem | Blue (#1565C0) | **इ॒षे त्वो॒र्जे त्वा॑...** | `.rik-text` |
| | Mantra Text | Adishila Vedic (Serif) | 1.6rem | Charcoal (#2C2C2C) | **इ॒षे त्वो॒र्जे त्वा॑...** | `.mantra-container` |
| | Mantra Numbering | Adishila Vedic (Serif) | 1.1rem | Charcoal (#2C2C2C) | **॥ १ ॥** | `.mantra-number` |
| **🗂️ Index** | Letter Heading | Adishila Vedic (Serif) | 1.2rem | Red (#B03A2E) | **अ, आ, इ** | `.alpha-char` |
| | Item Name | Adishila Vedic (Serif) | 1.3rem | Charcoal (#2C2C2C) | **वसिष्ठः, अग्निः** | `.item-name` |
| | Item Count Badge | Adishila San (Sans) | 0.75rem | Dark Gray (#777) | **(172), (5)** | `.item-count-badge` |
| | Location Refs | Adishila San (Sans) | 0.8rem | Saffron (#FF6B35) | **1.1.1, 1.1.2** | `.item-refs a` |
| | Top 20 Ranking | Adishila San (Sans) | 0.85rem | White (#FFFFFF) | **1, 2, 3** | `.rishi-rank` |

---

## 🎨 Element Specific Mappings

### 1. Traditional Elements (Serif Look)
These elements use the traditional **Adishila Vedic** font for a classical appearance.

| Element | CSS Selector | Description |
| :--- | :--- | :--- |
| **Homepage Stats Labels** | `.stat-label` | "पर्व: (Parva)", "खण्ड: (Kandah)", etc. |
| **Mantra Metadata** | `.rik-metadata` | Purple line: "॥ वसिष्ठो मैत्रावरुणिः ... ॥" |
| **Sama Headers** | `.sama-header-text` | Green line above mantra text |
| **Mantra Numbering** | `.mantra-number` | The "॥ १ ॥" marker inside/below mantra boxes |
| **Navigation Headers** | `.classification-table th` | Headers in the Mantra classification table |
| **Traditional Values** | `.class-value` | Values inside classification tables |
| **Kandah Metadata** | `.page-subtitle`, `.sama-count` | Labels on the Kandah page: "पर्व: ... खण्ड: ...", "साम: ..." |
| **Sidebar Headers** | `.nav-section h3`, `.sidebar-right h3` | Labels in the navigation: "पर्व:", "खण्ड:", "साम:" |

**Code Location:** `src/generate_website.py` around lines 921-923.
```css
.nav-section h3, .sidebar-right h3 {
    font-size: 1.15rem;
    text-transform: none; /* Allows "Jump to" instead of forced caps */
    letter-spacing: normal; /* Important: keeps Devanagari characters connected */
    font-family: 'AdishilaVedic', 'Noto Serif Devanagari', serif !important;
}

.nav-section h3 .number, .sidebar-right h3 .number {
    font-size: 0.85rem; /* Smaller size for bracketed counts */
}
```

---

### 2. Numerical & Dynamic Data (Sans Look)
These elements use the modern **Adishila San Vedic** font for maximum clarity and a scholarly index feel.

| Element | CSS Selector | Description |
| :--- | :--- | :--- |
| **Large Stats Values** | `.stat-value` | Large numbers on the homepage (e.g., "6", "125") |
| **Rank Indices** | `.rishi-rank` | The orange circles with numbers in Top 20 lists |
| **ToC / Nav Links** | `.toc-list li a`, `.nav-links a` | All numeric references in menus |
| **Summary Counts** | `.stats-summary` | Page header stats: "23 देवताः • 719 आर्षेयम्" (AdishilaVedic + English Numerals) |
| **Alphabetical Counts** | `.alpha-count` | Small numbers in alphabet navigation buttons |
| **Pill Counts** | `.index-link-item .stats` | Numbers in indices pills: "(172)", "(23)" |
| **Sama ID (Badge)** | `.sama-id` | Top-left badge on mantra entries: "1.1.1" |
| **Table Numerals** | `.number` (inside tables) | The "Global #" column values in classification tables |

**Code Location:** `src/generate_website.py` around lines 917-919.
```css
.stat-value, .rishi-rank, .number, .nav-links a, .toc-list li a, .jump-links a, 
.footnote-ref, .stats-summary, .stats-summary strong, .count, 
.rishi-count, .stats, .alpha-count, .item-count, .item-refs a, .item-count-badge, .sama-id, .sama-id a {
    font-family: 'AdishilaSanVedic', 'Noto Sans Devanagari', 'Inter', sans-serif !important;
}
```

---

### Sidebar Logo & Title
To adjust the size of the branding section in the sidebar:
**Location:** `src/generate_website.py` around lines 983-996.

```css
.logo-text {
    font-size: 1.8rem; /* Increased from 1.5rem */
}

.logo-subtitle {
    font-size: 1rem; /* Increased from 0.85rem */
}
```

```css
.index-link-item .title {
    font-size: 1.5rem; /* Change the Devanagari label size */
}

.index-link-item .stats {
    font-size: 0.8rem; /* Change the count (numeral) size */
    color: #888;
}
```

### Top 20 Classification Cards
To adjust the font weight or size of the names in the Top 20 lists (e.g., Rishi page):
**Location:** `src/generate_website.py` around lines 2397-2415.

```css
.rishi-name {
    font-weight: 400; /* Regular (400) or Bold (600) */
    font-size: 1.15rem;
}

.rishi-count {
    font-size: 0.8rem;
    font-weight: 400;
}
```

### Mantra Numbering (॥ १ ॥)
To adjust the size of the mantra index:
**Location:** `src/generate_website.py` around lines 1745-1750.

```css
.mantra-number {
    font-size: 1.6rem; /* Adjust this value */
    font-weight: 500;
}
```

### Kandah Page Sub-header (Metadata)
To adjust the second line of text on Kandah pages (labels and numbers):
**Location:** `src/generate_website.py` around lines 1133-1158.

```css
.page-subtitle, .sama-count {
    font-size: 1.1rem; /* Adjust labels and numbers together */
}

.page-meta .number {
    font-size: 0.8rem; /* Fine-tune only the numerals here */
    font-weight: 400;
}
```

### Mantra Classification & ID
To unify sizes for the Sama ID badge and the classification table:
**Location:** `src/generate_website.py` around lines 1261-1270 and 1977-1986.

```css
.sama-id, .sama-entry .number {
    font-size: 0.9rem; /* Compact metadata badges */
}

.classification-table {
    font-size: 1.1rem; /* Clearer table structure */
}
```

### Alphabetical Index (Anukramanika) References
To adjust the density of the location numerals in the index:
**Location:** `src/generate_website.py` around line 2286.

```css
.item-refs a {
    font-size: 0.8rem; /* Smaller size for dense linking */
}
```

---

> [!TIP]
> **Important**: All these styles are injected into the HTML during generation. After editing the fragments in `src/generate_website.py`, you **must** run the generator script to see the changes:
> `python src/generate_website.py --source-file data/output/Vargeekaran.json -o docs`

---

## 🌴 Malayalam & Grantha Swara Typography System

### Font Hierarchy

| Role | Font File | Visual Description | Usage |
| :--- | :--- | :--- | :--- |
| **Base Text** | `NotoSerifMalayalam-Regular.ttf` | Traditional Malayalam Serif | Mantra words, Titles, Headings, Footnote body |
| **Swara Notations** | `JaimineeyaSwara.ttf` | Red bold superscript (`#c62828`) | Stacks directly **above** Malayalam aksharas |
| **Vedic Accents** | `NotoSerifDevanagari-Regular.ttf` | Vedic Unicode Extensions | Swarita (`U+0951`), Anudatta (`U+1CD2`), Kampa |
| **Numerals & Latin** | `Nimbus Roman.ttf` | Classic Latin Serif | English numerals, page numbers, title metadata |

### Stacking Geometry
*   **Swara Elevation**: `\setstackgap{L}{0.7\baselineskip}` elevates swaras cleanly above Malayalam ascenders.
*   **Auto-Kerning**: `\swarastack` automatically computes the width of base syllables vs multi-glyph swaras (`\stackleft` / `\stackcenter`) to eliminate visual collisions.

### 11 Vedic Swara Modifiers Layout

| Modifier | Symbol | Stacking Position | Hex / PUA |
| :--- | :---: | :---: | :--- |
| **Syllable Arc (Tie)** | `⁀` / `͡` | **Stacked Above** | `U+E004` / `U+2040` |
| **Caret** | `^` / `˄` | **Stacked Above** | `U+E005` / `U+005E` |
| **Roof** | `/\` / `Ʌ` | **Stacked Above** | `U+E006` / `U+0245` |
| **Ring Above** | `˚` / `ͦ` | **Stacked Above** | `U+E009` / `U+0366` |
| **High/Mid-Dot** | `ॱ` / `·` | **Stacked Above** | `U+E001` / `U+0971` |
| **Underbar** | `_` | **Stacked Below** | `U+E007` / `U+005F` |
| **Phrasing Danda** | `╷` / `L` | **Stacked Below** | `U+E002` / `U+2577` |
| **Descending Tone** | `\` / `╲` | **Stacked Below** | `U+E003` / `U+005C` |
| **Ascending Tone** | `/` | **Stacked Below** | `U+E008` / `U+002F` |
| **Low Comma** | `,` / `ˏ` | **Stacked Below** | `U+E00A` / `U+002C` |
| **Double Danda** | `\|\|` / `॥` | **Inline** | `U+E00B` / `U+0965` |

