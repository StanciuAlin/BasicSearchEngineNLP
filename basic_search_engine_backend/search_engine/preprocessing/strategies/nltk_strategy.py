import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import string
from ..base import Preprocessor


"""
Module: nltk_strategy.py
Description: Implements a high-precision NLP preprocessing strategy using the 
Natural Language Toolkit (NLTK). This strategy focuses on standard linguistic 
normalization techniques including lemmatization and stop-word removal.
"""


class NLTKPreprocessor(Preprocessor):
    """
    A robust NLP preprocessor powered by NLTK.

    This strategy utilizes the WordNet Lemmatizer to perform morphological 
    analysis of words, reducing them to their base dictionary form. It is 
    ideal for improving search recall by ensuring different grammatical forms 
    of a word (e.g., "running", "ran") match the same root ("run").
    """

    def __init__(self):
        """
        Initializes the NLTK components and ensures necessary corpora are downloaded.

        This constructor checks for the presence of required NLTK data packages 
        (punkt, stopwords, wordnet) and downloads them silently if they are missing.
        """

        # Ensure resource availability once during initialization
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            nltk.download('wordnet', quiet=True)

        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        self.punctuation = set(string.punctuation)

    def process(self, text: str) -> list[str]:
        """
        Normalizes raw text into a list of lemmatized tokens using the NLTK pipeline.

        The processing pipeline involves:
        1. Lowercasing and professional tokenization using Punkt.
        2. Filtering out common English stop-words and punctuation marks.
        3. Lemmatization using the WordNet corpus to extract semantic roots.

        Args:
            text (str): The raw input string to be normalized.

        Returns:
            list[str]: A collection of cleaned and lemmatized tokens.

        Complexity:
            O(L * log W), where L is the number of characters and W is the 
            complexity of the WordNet lookup for lemmatization.
        """

        # Professional tokenization and case folding (lowercasing)
        tokens = word_tokenize(text.lower())
        # Filter out stop-words and punctuation to retain high-information terms
        filtered = [
            t for t in tokens if t not in self.stop_words and t not in self.punctuation]
        # Apply lemmatization (e.g., transforming "better" -> "good") and return
        return [self.lemmatizer.lemmatize(t) for t in filtered]
