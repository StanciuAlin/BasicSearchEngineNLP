from .strategies.custom_strategy import CustomPreprocessor
from .strategies.nltk_strategy import NLTKPreprocessor
from .strategies.spacy_strategy import SpacyPreprocessor
from .strategies.sklearn_strategy import SklearnPreprocessor


"""
Module: factory.py
Description: Implements the Factory Design Pattern to manage and provide different 
NLP preprocessing strategies. This decoupling allows the search engine to switch 
between various linguistic normalization techniques seamlessly.
"""


class PreprocessorFactory:
    """
    A factory class for managing NLP preprocessing instances.

    This class utilizes an internal cache to store singleton-like instances of 
    different preprocessors. This ensures efficiency by avoiding the overhead 
    of re-initializing heavy libraries (like NLTK or SpaCy) for every search query.
    """

    def __init__(self):
        """
        Initializes the factory and pre-loads the available preprocessing strategies.

        The internal cache (_instances) maps mode identifiers to their 
        respective strategy implementation objects.
        """

        # Instance cache for performance: ensures heavy models are loaded only once
        self._instances = {
            "custom": CustomPreprocessor(),
            "nltk": NLTKPreprocessor(),
            "spacy": SpacyPreprocessor(),
            "sklearn": SklearnPreprocessor(["initialization content"]),
        }

    def get_preprocessor(self, mode: str):
        """
        Retrieves the requested preprocessor instance based on the mode.

        Args:
            mode (str): The identifier for the NLP strategy (custom, nltk, spacy, sklearn).

        Returns:
            BasePreprocessor: The requested strategy instance, or the 'custom' 
                             strategy as a default fallback.
        """

        return self._instances.get(mode, self._instances["custom"])

    def get_strategy(self, mode: str):
        """
        Alias for get_preprocessor to maintain compatibility with the engine orchestration.

        Args:
            mode (str): The identifier for the NLP strategy.

        Returns:
            BasePreprocessor: The corresponding strategy instance.
        """

        return self.get_preprocessor(mode)


# Global singleton instance to be imported across the application (app.py, engine.py)
factory = PreprocessorFactory()


def get_preprocessor(mode: str):
    """
    Utility function to access the global factory instance.

    Args:
        mode (str): The requested preprocessing mode.

    Returns:
        BasePreprocessor: The strategy instance from the global factory.
    """

    return factory.get_preprocessor(mode)
