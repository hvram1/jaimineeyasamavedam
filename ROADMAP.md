# Jaimineeya Samavedam Roadmap: Pipeline Evolution

This document captures the strategic vision for the next generation of the Vedic text processing pipeline, as discussed in [Conversation 480ce470].

## Phase 1: Tactical Safety (Stabilized)
- [ ] **Validation Layer**: Implement a pre-flight validator in `renumber_sooktam.py` to catch orphan or mismatched `# Start` and `# End` tags before processing.
- [x] **Danda Normalization & Search Stability**: Strengthened regex logic to handle corrupted heavy bars and standard dandas without losing verse alignment. Fully implemented permissive, danda-agnostic search matching and highlighting for the website.

## Phase 2: Structural Alignment (Next)
- **Shared Pattern Registry**: Move all structural tag definitions (SuperSection, Section, SubSection, Rik, Mantra Set) into a shared `src/patterns.py`.
- **Pre-Parsing Validation**: Refactor both `renumber_sooktam.py` and `generate_json.py` to use a shared structural validator to ensure "Zero-Corruption" during ingestion.

## Phase 3: The Unified Vedic Engine (Long Term)
- **Block-Based AST Parser**: Move from regex "line patching" to a true hierarchical parser (Abstract Syntax Tree).
  - **Tree Ingestion**: Read the raw `.txt` file into a list of semantic Node objects.
  - **In-Memory Transformation**: Perform renumbering, ID generation, and metadata injection on the Tree nodes.
- **Unified Export**: Export both the cleaned `.txt` file (for version control) and the structured `.json` file (for the website) from the exact same in-memory object.
  - **Strategic Benefit**: Completely eliminates "drift" between the source text and the website display.
