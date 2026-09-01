"""Jaimineeya Samaveda Devanagari -> Malayalam transliteration pipeline (Phase 1).

Modules:
    ml_map          frozen swara-marker -> Grantha lookup (reads the reviewed
                    Malayalam_JSV/swara_lookup_frozen.json)
    ml_transliterate aksharamukha wrapper + Malayalam edge-case cleanup
    ml_text         Samam text -> Malayalam intermediate text transformer
"""

__version__ = "0.1.0"