# Aaranam Structural Audit Report (LATEST)

**Target File**: `data/input/Aaranam_latest.txt`
**Configuration**: `reset_per_super: false` (Global IDs)
**Audit Date**: 2026-04-19
**Total Structural Blocks Found**: 1,248

---

## 1. ID Collisions (Duplicate Sections)
> [!NOTE]
> Section numbering is now globally unique. No duplicates found. **[FIXED]**

- **Status**: PASS

---

## 2. Data Integrity (Missing Mantra Sets)
> [!CAUTION]
> While numbers are unique, the renumbering script has **lost the connection to the Samam text** for nearly the entire file.

- **subsection_9–147**: Nearly all subsections in this range are **missing their Mantra Set blocks**.
- **Observation**: The chanting text was not renumbered or associated with the new Subsection IDs, meaning they will be invisible to the JSON pipeline.

---

## 3. Parity Errors (Mismatched Start/End Tags)
> [!IMPORTANT]
> The following IDs have mismatched opening/closing markers, which will break the JSON parser.

- **subsection_21**: 3 Start tags vs 4 End tags
- **subsection_92**: 1 Start tags vs 0 End tags
- **subsection_148**: 1 Start tags vs 2 End tags
- **subsection_151**: 2 Start tags vs 1 End tags

---

## 4. Logical Mapping Issue
- **Rik-Before-Title**: In many sections (e.g., subsection_2 onward), the Rik Metadata correctly precedes the SubSection Title. However, the renumbering script did not always apply the same increment to both, leading to the data being split across different IDs.
