from sklearn.feature_extraction.text import TfidfVectorizer
from ..base import Preprocessor


class SklearnPreprocessor(Preprocessor):
    def __init__(self, corpus_texts: list[str]):
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.is_fitted = False

        # Daca primim texte la init (ex: textul de siguranta), facem fit
        if corpus_texts:
            self.fit(corpus_texts)

        self.vectorizer.fit(corpus_texts)
        self.feature_names = self.vectorizer.get_feature_names_out()

    def fit(self, corpus_texts: list[str]):
        """Train the Vectorizer with the input data"""
        if corpus_texts and len(corpus_texts) > 0:
            self.vectorizer.fit(corpus_texts)
            self.feature_names = self.vectorizer.get_feature_names_out()
            self.is_fitted = True

    def process(self, text: str) -> list[str]:
        # Daca nu este antrenat (ex: baza de date e inca goala), returnam o tokenizare simpla
        if not self.is_fitted:
            return text.lower().split()

        # Folosim analyzer-ul intern de la Sklearn
        analyze = self.vectorizer.build_analyzer()
        return analyze(text)
