# Jaimineeya Samavedam Pipeline Architecture

This document provides a diagrammatic overview of the various workflow pipelines used to process, curate, and publish the Jaimineeya Samavedam text and metadata.

## 1. Core Data Processing Pipeline

This is the primary flow for transforming raw manuscript corrections into the final "Vargeekaran" JSON and the main website.

```mermaid
graph TD
    subgraph "Phase 1: Normalization"
        A1["Raw Corrections (data/input/Samhita_corrected.txt)"] --> B1("renumber_sooktam.py")
        B1 --> C1["Normalized Text (data/output/txt/...)"]
    end

    subgraph "Phase 2: Metadata Integration"
        C1 --> D1("generate_json.py")
        D2["Rishi/Devata Metadata (.txt)"] --> D1
        D3["Saman Metadata (.txt)"] --> D1
        D1 --> E1["Structured JSON (data/output/json/...)"]
    end

    subgraph "Phase 3: Classification & Curation"
        E1["Structured JSON (data/output/json/...)"] --> F1("generate_rik_table.py")
        F2["Reconciliation Excel (.xlsx)"] --> F1
        F1 --> G1["Vargeekaran.json (Primary Source)"]
        F1 --> G2["Rik Table (.csv & .xlsx)"]
    end

    subgraph "Phase 4: Publication"
        G1 --> H1("generate_website.py")
        G1 --> H2("render_pdf.py")
        H1 --> I1["Static Website (docs/)"]
        H2 --> I2["PDF & HTML Reports"]
    end
```

---

## 2. Collection & Curation Workflow

This secondary pipeline is used to create specific subsets or thematic collections (like Sooktamala or Ashirvachana Samani).

```mermaid
graph LR
    G1["Vargeekaran.json"] --> J1("curate_jsv.py")
    K1["Selection Filter (.txt)"] --> J1
    J1 --> L1["Subset JSON (data/output/..._out.json)"]
    L1 --> M1("generate_website.py")
    M1 --> N1["Collection Site (docs/collection/...)"]
```

---

## 3. Custom Sooktamala Pipeline

For independent collections using the P.K.S (Parva.Kandah.Samam) identifier system.

```mermaid
graph TD
    O1["Structural Index (YAML)"] --> P1("build_curated_collection")
    G1["Vargeekaran.json"] --> P1
    P1 --> Q1["Sooktamala.json"]
    Q1 --> R1("generate_website.py")
    R1 --> S1["Sooktamala Site (docs/collection/sooktamala)"]
```

---

## 4. Prayoga & Procedure Integration

How ritual instructions are embedded into the Samam display.

```mermaid
graph TD
    T1["Prayoga Markdown (.md)"] --> U1("manage_prayoga_procedures")
    V1["Procedure Index (YAML)"] --> W1("generate_json.py")
    W1 --> G1
    G1 -- "Procedure Ref" --> H1
    H1 -- "Embedded Link" --> I1
```

---

## Key Maintenance Commands

| Pipeline | Command Example |
| :--- | :--- |
| **Core JSON** | `python src/generate_json.py --type samhita` |
| **Rik Table** | `python src/generate_rik_table.py --type samhita` |
| **Website** | `python src/generate_website.py --samhita` |
| **Curation** | `python src/curate_jsv.py` |
| **PDF** | `python src/render_pdf.py data/output/Vargeekaran.json` |
