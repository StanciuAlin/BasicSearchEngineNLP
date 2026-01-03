# search_engine/indexing/sklearn_tfidf.py
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os
import numpy as np


class SklearnTfIdf:
    def __init__(self, model_path="data/tfidf_model.pkl"):
        # Folosim setările standard care includ eliminarea stop-words în engleză
        self.model_path = model_path
        self.vectorizer = TfidfVectorizer(
            stop_words='english', max_features=50000)
        self.tfidf_matrix = None
        self.doc_ids = []

    def build_index(self, documents):
        """
        Antrenează vectorizatorul pe tot corpusul de documente.
        documents: o listă de obiecte Document (cele din models/document.py)
        """
        self.doc_ids = [d.doc_id for d in documents]
        # Folosim generator pentru memorie
        texts = (d.content for d in documents)
        # Transformă textele într-o matrice TF-IDF (Sparse Matrix)
        self.tfidf_matrix = self.vectorizer.fit_transform(texts)
        # Salvăm pe disc
        joblib.dump((self.vectorizer, self.tfidf_matrix,
                    self.doc_ids), self.model_path)

    def load_index(self):
        if os.path.exists(self.model_path):
            self.vectorizer, self.tfidf_matrix, self.doc_ids = joblib.load(
                self.model_path)
            return True
        return False

    def search(self, query: str):
        if self.tfidf_matrix is None or self.vectorizer is None:
            return []

        # Transformă query-ul
        query_vec = self.vectorizer.transform([query])

        # Calculăm similaritatea
        similarities = cosine_similarity(
            query_vec, self.tfidf_matrix).flatten()

        # Sortăm descrescător după scor
        related_docs_indices = similarities.argsort()[::-1]

        results = []
        for i in related_docs_indices:
            score = similarities[i]
            if score > 0:
                results.append((self.doc_ids[i], score))

        return results
