# search_engine/indexing/sklearn_tfidf.py
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os
import numpy as np

"""
Module: sklearn_tfidf.py
Description: Provides a baseline Information Retrieval implementation using the 
Scikit-Learn framework. This module handles the creation, persistence, and 
querying of a standard TF-IDF vector space model.
"""


class SklearnTfIdf:
    """
    A validation baseline using Scikit-Learn's TF-IDF implementation.

    This class serves as a "gold standard" to verify the accuracy of the custom 
    inverted index. It uses a sparse matrix representation to store document 
    vectors and computes relevance using the optimized Cosine Similarity 
    functions provided by sklearn.
    """

    def __init__(self, model_path="data/tfidf_model.pkl"):
        """
        Initializes the Sklearn engine with standard English NLP settings.

        Args:
            model_path (str): The file path used to persist the trained model 
                              and the TF-IDF matrix.
        """

        # Utilize standard English stop-word removal and limit vocabulary size
        # to ensure memory efficiency on large corpora.
        self.model_path = model_path
        self.vectorizer = TfidfVectorizer(
            stop_words='english', max_features=50000)
        self.tfidf_matrix = None
        self.doc_ids = []

    def build_index(self, documents):
        """
        Trains the vectorizer and builds the TF-IDF matrix for the entire corpus.

        This method transforms the raw text of Document objects into a sparse 
        feature matrix. The resulting model is serialized to disk using joblib 
        for efficient reloading.

        Args:
            documents (List[Document]): A list of Document model instances.

        Complexity:
            O(N * M), where N is the number of documents and M is the unique 
            term count, limited by max_features.
        """

        self.doc_ids = [d.doc_id for d in documents]

        # Use a generator expression to minimize memory usage during text extraction
        texts = (d.content for d in documents)

        # Transform the raw texts into a Sparse TF-IDF Matrix
        self.tfidf_matrix = self.vectorizer.fit_transform(texts)

        # Persist the state (vectorizer, matrix, and ID mapping) to disk
        joblib.dump((self.vectorizer, self.tfidf_matrix,
                    self.doc_ids), self.model_path)

    def load_index(self):
        """
        Attempts to load a previously serialized index from the disk.

        Returns:
            bool: True if the model was successfully loaded; otherwise, False.
        """

        if os.path.exists(self.model_path):
            self.vectorizer, self.tfidf_matrix, self.doc_ids = joblib.load(
                self.model_path)
            return True
        return False

    def search(self, query: str):
        """
        Executes a similarity search for a given query string.

        The query is transformed into the same vector space as the documents, 
        and Cosine Similarity is calculated across the entire matrix.

        Args:
            query (str): The raw search keywords.

        Returns:
            List[Tuple[int, float]]: A ranked list of (document_id, score) pairs 
                                     for documents with a non-zero similarity.
        """

        if self.tfidf_matrix is None or self.vectorizer is None:
            return []

        # Transform the input query into the trained TF-IDF vector space
        query_vec = self.vectorizer.transform([query])

        # Compute Cosine Similarity between the query and all indexed documents
        similarities = cosine_similarity(
            query_vec, self.tfidf_matrix).flatten()

        # Sort document indices in descending order based on similarity scores
        related_docs_indices = similarities.argsort()[::-1]

        results = []
        for i in related_docs_indices:
            score = similarities[i]
            # Exclude documents with zero similarity to maintain result quality
            if score > 0:
                results.append((self.doc_ids[i], score))

        return results
