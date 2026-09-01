# Jaimineeya Samaveda Samhita - Data Reconciliation Report

**Generated:** 2026-02-05 18:05:53

---

## Executive Summary

This report summarizes the data reconciliation analysis performed on the Jaimineeya Samaveda Samhita source text and its various processed outputs.

### Overall Structure

| Metric | Value |
|--------|-------|
| **Pathas (SuperSections)** | 6 |
| **Khandas (Sections)** | 59 |
| **Samams** | 1,226 |

**Numbering Continuity:** ✅ **PASS**

---

## Section 1: Patha-wise Breakdown

| Patha | Samams |
|-------|--------|
| आग्नेयपाठः | 182 |
| तद्वपाठः | 200 |
| बृहतिपाठः | 152 |
| असाविपाठः | 106 |
| ऐन्द्रपाठः | 186 |
| पवमानपाठः | 400 |
| **TOTAL** | **1,226** |

---

## Detailed Structure Breakdown
Derived from `JSV_Structure_Summary.txt`.

### PATHA 1: आग्नेयपाठः

| Khanda | Samas |
| :--- | :--- |
| प्रथम खण्डः | 19 |
| द्वितीय खण्डः | 15 |
| तृतीय खण्डः | 21 |
| चतुर्थ खण्डः | 22 |
| पञ्चम खण्डः | 16 |
| षष्ठ खण्डः | 10 |
| सप्तम खण्डः | 16 |
| अष्टम खण्डः | 9 |
| नवम खण्डः | 13 |
| दशम खण्डः | 7 |
| एकादश खण्डः | 18 |
| द्वादश खण्डः | 16 |
| **TOTAL** | **182** |


### PATHA 2: तद्वपाठः

| Khanda | Samas |
| :--- | :--- |
| प्रथम खण्डः | 23 |
| द्वितीय खण्डः | 22 |
| तृतीय खण्डः | 20 |
| चतुर्थ खण्डः | 15 |
| पञ्चम खण्डः | 30 |
| षष्ठ खण्डः | 24 |
| सप्तम खण्डः | 12 |
| अष्टम खण्डः | 11 |
| नवम खण्डः | 12 |
| दशम खण्डः | 10 |
| एकादश खण्डः | 9 |
| द्वादश खण्डः | 12 |
| **TOTAL** | **200** |


### PATHA 3: बृहतिपाठः

| Khanda | Samas |
| :--- | :--- |
| प्रथम खण्डः | 31 |
| द्वितीय खण्डः | 25 |
| तृतीय खण्डः | 25 |
| चतुर्थ खण्डः | 17 |
| पञ्चम खण्डः | 16 |
| षष्ठ खण्डः | 17 |
| सप्तम खण्डः | 10 |
| अष्टम खण्डः | 11 |
| **TOTAL** | **152** |


### PATHA 4: असाविपाठः

| Khanda | Samas |
| :--- | :--- |
| प्रथम खण्डः | 19 |
| द्वितीय खण्डः | 17 |
| तृतीय खण्डः | 18 |
| चतुर्थ खण्डः | 28 |
| पञ्चम खण्डः | 11 |
| षष्ठ खण्डः | 13 |
| **TOTAL** | **106** |


### PATHA 5: ऐन्द्रपाठः

| Khanda | Samas |
| :--- | :--- |
| प्रथम खण्डः | 24 |
| द्वितीय खण्डः | 21 |
| तृतीय खण्डः | 10 |
| चतुर्थ खण्डः | 21 |
| पञ्चम खण्डः | 28 |
| षष्ठ खण्डः | 15 |
| सप्तम खण्डः | 18 |
| अष्टम खण्डः | 16 |
| नवम खण्डः | 17 |
| दशम खण्डः | 16 |
| **TOTAL** | **186** |


### PATHA 6: पवमानपाठः

| Khanda | Samas |
| :--- | :--- |
| प्रथम खण्डः | 69 |
| द्वितीय खण्डः | 19 |
| तृतीय खण्डः | 16 |
| चतुर्थ खण्डः | 20 |
| पञ्चम खण्डः | 76 |
| षष्ठ खण्डः | 36 |
| सप्तम खण्डः | 21 |
| अष्टम खण्डः | 33 |
| नवम खण्डः | 35 |
| दशम खण्डः | 39 |
| एकादश खण्डः | 36 |
| **TOTAL** | **400** |

---

## Section 2: Continuity & Integrity Checks

Derived from `JSON_Samam_Continuity_Report.txt`.

### ✅ No Issues Found
All Khandas have contiguous Samam numbering starting from 1.

---

## Section 3: Output Files Generated

| File | Description | Status |
|------|-------------|--------|
| `JSV_Structure_Summary.csv` | Aggregated counts | Updated |
| `JSV_Samam_Granular_Table.csv` | Full Samam list (1226 rows) | Updated |
| `JSON_Samam_Continuity_Report.txt` | Detailed checks | Updated |

---

## Conclusion

| Check | Status | Note |
|-------|--------|------|
| **Total Count** | 1226 | Based on '॥N॥' markers |
| **Continuity** | ✅ **PASS** | See Section 2 |

*Report generated automatically by `src/generate_reconciliation_report.py`*
