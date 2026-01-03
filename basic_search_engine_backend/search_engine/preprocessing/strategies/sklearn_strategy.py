from sklearn.feature_extraction.text import TfidfVectorizer
from ..base import Preprocessor
import pandas as pd


class SklearnPreprocessor(Preprocessor):
    def __init__(self, corpus_texts: list[str]):
        # Sklearn învață vocabularul din întreg corpusul la inițializare
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.vectorizer.fit(corpus_texts)
        self.feature_names = self.vectorizer.get_feature_names_out()

    def process(self, text: str) -> list[str]:
        # Sklearn are propriul tokenizer intern
        analyze = self.vectorizer.build_analyzer()
        return analyze(text)
