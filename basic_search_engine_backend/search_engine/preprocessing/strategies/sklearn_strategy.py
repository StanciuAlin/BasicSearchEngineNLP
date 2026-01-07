from sklearn.feature_extraction.text import TfidfVectorizer
from ..base import Preprocessor

"""
Module: sklearn_strategy.py
Description: Implements a preprocessing strategy using Scikit-Learn's internal 
text processing engine. This serves as a standardized baseline for the 
Search Engine's modular NLP factory.
"""


class SklearnPreprocessor(Preprocessor):
    """
    A preprocessing strategy powered by the Scikit-Learn TfidfVectorizer.

    This class leverages the industrial-grade tokenization and stop-word 
    filtering capabilities of the Scikit-Learn library. It is designed to 
    provide a consistent "analyzer" that matches the baseline TF-IDF 
    implementation used for model validation.
    """

    def __init__(self, corpus_texts: list[str]):
        """
        Initializes the Sklearn preprocessor and attempts an initial training phase.

        Args:
            corpus_texts (list[str]): A collection of strings used to build the 
                                      initial vocabulary and fit the vectorizer.
        """

        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.is_fitted = False

        # If initialization texts are provided, perform the initial fit operation
        if corpus_texts:
            self.fit(corpus_texts)

        # Ensure the vectorizer is fitted to allow access to feature names
        self.vectorizer.fit(corpus_texts)
        self.feature_names = self.vectorizer.get_feature_names_out()

    def fit(self, corpus_texts: list[str]):
        """
        Trains the internal vectorizer with the input dataset.

        This step is crucial as it defines the vocabulary and the 'analyzer' 
        logic used during the search phase.

        Args:
            corpus_texts (list[str]): The input data used for training.

        Complexity:
            O(T), where T is the total number of terms in the input corpus.
        """

        if corpus_texts and len(corpus_texts) > 0:
            self.vectorizer.fit(corpus_texts)
            self.feature_names = self.vectorizer.get_feature_names_out()
            self.is_fitted = True

    def process(self, text: str) -> list[str]:
        """
        Transforms raw text into a list of tokens using Sklearn's internal analyzer.

        If the vectorizer has not been fitted (e.g., the database is empty), 
        it falls back to a basic whitespace tokenization. Once fitted, it 
        applies Sklearn's standard pipeline: lowercasing, stop-word removal, 
        and N-gram generation (if configured).

        Args:
            text (str): The raw input text to be processed.

        Returns:
            list[str]: A collection of tokens derived from the text.
        """

        # Fallback mechanism: return simple tokenization if training is incomplete
        if not self.is_fitted:
            return text.lower().split()

        # Retrieve and utilize the internal analyzer built during the fitting process
        analyze = self.vectorizer.build_analyzer()
        return analyze(text)
