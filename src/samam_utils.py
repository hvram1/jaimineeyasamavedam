"""
Shared utilities for counting Samams in the Jaimineeya Samaveda project.
This module provides a unified counting method used by both the website generator
and summary table scripts.
"""
import re

# Unified pattern for Samam number markers
# Matches both: ॥N॥ (Devanagari danda) and ||N|| (ASCII pipes)
# With both Devanagari numerals (०-९) and Arabic numerals (0-9)
SAMAM_PATTERN = re.compile(r'(?:॥|\|\|)\s*[\d०-९]+\s*(?:॥|\|\|)')


def count_samam_markers(text: str) -> int:
    """
    Count the number of Samam markers in a text.
    
    Args:
        text: The mantra text to search
        
    Returns:
        Number of Samam markers found (e.g., ॥१॥, ||2||)
    """
    if not text:
        return 0
    return len(SAMAM_PATTERN.findall(text))


def count_samams_with_fallback(text: str, min_count: int = 1) -> int:
    """
    Count Samam markers with a minimum fallback.
    If no markers are found, returns the fallback value.
    
    Args:
        text: The mantra text to search
        min_count: Minimum count to return if no markers found
        
    Returns:
        Number of Samam markers, or min_count if none found
    """
    count = count_samam_markers(text)
    return count if count > 0 else min_count
