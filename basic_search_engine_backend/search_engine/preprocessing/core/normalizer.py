import re


"""
Module: normalizer.py
Description: Implements the second stage of the text preprocessing pipeline. 
This module focuses on standardizing the raw text through case folding and 
precise token extraction using word boundaries.
"""


def normalize(text: str) -> list[str]:
    """
    Standardizes the input text and extracts a clean list of tokens.

    The normalization process involves two key steps:
    1. Case Folding: Converting the entire text to lowercase to ensure 
       case-insensitivity during the search phase.
    2. Strict Tokenization: Using regular expressions with word boundaries (\b) 
       to isolate whole alphanumeric sequences, effectively stripping 
       punctuation and special characters.

    Args:
        text (str): The raw input string to be normalized.

    Returns:
        list[str]: A collection of isolated, lowercase alphanumeric tokens.

    Complexity:
        O(L), where L is the number of characters in the text, as it requires 
        a single pass for lowercasing and one for regex extraction.
    """

    # 1: Convert to lowercase for uniformity across the index
    text = text.lower()

    # 2: Strict tokenization for whole words.
    # We use \b (word boundary) to ensure we isolate words from surrounding punctuation.
    # re.findall(r'\b\w+\b', ...) extracts only complete alphanumeric sequences.
    tokens = re.findall(r'\b\w+\b', text)

    return tokens
