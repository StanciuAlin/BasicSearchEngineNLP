from ..base import Preprocessor
from ..core.normalizer import normalize
from ..core.stemmer import simple_stem


"""
Module: custom_strategy.py
Description: Implements a high-speed, rule-based preprocessing strategy. 
This approach utilizes custom normalization and stemming logic designed 
for efficiency on large-scale textual datasets.
"""


class CustomPreprocessor(Preprocessor):
    """
    A lightweight and efficient text preprocessor.

    This strategy follows a rule-based approach to text normalization. It is 
    designed to provide maximum performance by using optimized regex-based 
    normalization and a simple suffix-stripping stemmer. It serves as the 
    default strategy for real-time search scenarios.
    """

    def process(self, text: str) -> list[str]:
        """
        Transforms raw text into a list of stemmed tokens using custom logic.

        The processing pipeline consists of:
        1. Normalization: Isolating whole words using regex patterns and 
           performing initial cleaning.
        2. Stemming: Applying a simplified stemming algorithm to each token 
           to reduce them to a common base form.

        Note on Indexing:
        The inverted index relies on these processed keys. The custom logic 
        ensures that distinct semantic roots (e.g., "car" vs. "carpet") are 
        mapped to different keys in the dictionary to maintain precision.

        Args:
            text (str): The raw input string to be processed.

        Returns:
            list[str]: A collection of normalized and stemmed tokens.

        Complexity:
            O(L), where L is the number of characters in the input text. 
            This is the most computationally efficient strategy in the factory.
        """

        # Obtain a list of whole words isolated via regex-based normalization
        tokens = normalize(text)

        # Apply the custom stemmer to each isolated token.
        # This reduces words to their base form while preserving semantic
        # distinctions required by the inverted index keys.
        return [simple_stem(t) for t in tokens if t]
