"""
Module: stemmer.py
Description: Implements a fundamental stemming component for the NLP pipeline. 
Stemming is used to reduce words to their base or root form, enhancing the 
recall of the search engine by mapping different word variations to a single term.
"""


def simple_stem(token: str) -> str:
    """
    Reduces a token to its base form using a simple suffix-stripping algorithm.

    This function targets common English suffixes such as "ing", "ed", and "s". 
    It includes a length constraint to prevent over-stemming of short words, 
    ensuring that the resulting stem maintains a minimum level of semantic meaning.

    Args:
        token (str): The normalized word token to be stemmed.

    Returns:
        str: The stemmed version of the word if a suffix was removed; 
             otherwise, the original token.

    Complexity:
        O(S * K), where S is the number of defined suffixes and K is the 
        average length of a suffix, as it performs string comparison operations.
    """

    # Suffix-stripping logic for basic linguistic normalization
    for suffix in ("ing", "ed", "s"):
        # Apply stripping only if the remaining stem length is greater than 2 characters
        if token.endswith(suffix) and len(token) > len(suffix) + 2:
            return token[: -len(suffix)]
    return token

# Note: More advanced stemmer implementations (such as Porter or Lancaster)
# can be integrated here to further refine the indexing process.
