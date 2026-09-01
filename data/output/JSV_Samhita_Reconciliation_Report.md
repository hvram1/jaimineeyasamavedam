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
