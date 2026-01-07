from abc import ABC, abstractmethod
from typing import List

"""
Module: base.py
Description: Defines the abstract interface for all preprocessing strategies 
within the NLP pipeline. This ensures a consistent contract for different 
linguistic normalization techniques. [cite: 50, 69]
"""


class Preprocessor(ABC):
    """
    Abstract Base Class for text preprocessing strategies.

    This class serves as the foundation for the Strategy Design Pattern 
    implemented in the Preprocessor Factory. Any new NLP pipeline (e.g., NLTK, 
    SpaCy, or Transformer-based) must inherit from this class and implement 
    the 'process' method. [cite: 108, 109]
    """

    @abstractmethod
    def process(self, text: str) -> List[str]:
        """
        Abstract method to transform raw text into a normalized list of tokens.

        Implementations of this method should handle tasks such as tokenization, 
        case folding, stop-word removal, and stemming/lemmatization based on 
        the specific strategy's requirements. [cite: 110]

        Args:
            text (str): The raw input string to be processed.

        Returns:
            List[str]: A list of cleaned and normalized terms (tokens).
        """

        pass
