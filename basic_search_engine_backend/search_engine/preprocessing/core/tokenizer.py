import re
from typing import List


"""
Module: tokenizer.py
Description: Provides a fundamental tokenization implementation for the NLP pipeline. 
This serves as the initial stage in transforming raw text into a discrete 
collection of searchable terms.
"""

# Educational simple regex-based tokenizer pattern.
# This pattern identifies sequences starting with a letter followed by
# alphanumeric characters or hyphens.
TOKEN_PATTERN = re.compile(r"[A-Za-z][A-Za-z0-9\-]*")


def tokenize(text: str) -> List[str]:
    """
    Extracts word-like tokens from a raw string using a regular expression.

    This function performs initial case folding (lowercasing) and utilizes 
    the '\w+' pattern to isolate alphanumeric character groups (whole words). 
    It effectively strips away punctuation that might otherwise be attached 
    to the terms.

    Args:
        text (str): The raw input string to be tokenized.

    Returns:
        List[str]: A collection of lowercase alphanumeric tokens.

    Complexity:
        O(L), where L is the number of characters in the input text, as the 
        regex engine performs a single pass over the string.
    """

    # The \w+ pattern extracts groups of alphanumeric characters (whole words)
    # while ignoring punctuation that might otherwise adjoin them.
    return re.findall(r'\w+', text.lower())
