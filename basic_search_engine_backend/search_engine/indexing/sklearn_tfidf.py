# search_engine/indexing/sklearn_tfidf.py
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


class SklearnTfIdf:
    def __init__(self):
        # Folosim setările standard care includ eliminarea stop-words în engleză
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.tfidf_matrix = None
        self.doc_ids = []

    def build_index(self, documents):
        """
        Antrenează vectorizatorul pe tot corpusul de documente.
        documents: o listă de obiecte Document (cele din models/document.py)
        """
        self.doc_ids = [doc.doc_id for doc in documents]
        texts = [doc.content for doc in documents]

        # Transformă textele într-o matrice TF-IDF (Sparse Matrix)
        self.tfidf_matrix = self.vectorizer.fit_transform(texts)

    def search(self, query: str):
        """
        Calculează similaritatea cosinus între query și toate documentele.
        """
        if self.tfidf_matrix is None:
            return []

        # Transformă query-ul folosind același vocabular ca documentele
        query_vec = self.vectorizer.transform([query])

        # Calculează similaritatea (rezultatul este un array de scoruri)
        similarities = cosine_similarity(
            query_vec, self.tfidf_matrix).flatten()

        # Returnează o listă de (doc_id, score)
        results = []
        for idx, score in enumerate(similarities):
            if score > 0:
                results.append((self.doc_ids[idx], score))

        return results
