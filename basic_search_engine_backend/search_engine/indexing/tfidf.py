import math
from typing import Dict, List
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity as sklearn_cosine
from .inverted_index import InvertedIndex
from ..models.document import Document

"""
Module: tfidf.py
Description: Implements the Vector Space Model (VSM) using TF-IDF weighting. 
This module provides the mathematical framework for calculating document 
vectors and computing geometric (Cosine) and set-theoretic (Jaccard) similarities.
"""


class TfIdfWeighter:
    """
    A weighting engine for the Vector Space Model.

    This class is responsible for transforming documents and queries into 
    weighted vectors. It utilizes the log-frequency weighting scheme for 
    Term Frequency (TF) and Inverse Document Frequency (IDF) to evaluate 
    the statistical importance of terms.
    """

    def __init__(self, index: InvertedIndex):
        """
        Initializes the weighter with a reference to the Inverted Index.

        Args:
            index (InvertedIndex): The index used to retrieve term statistics.
        """
        self.index = index
        self.doc_vectors: Dict[int, Dict[str, float]] = {}

    def build_doc_vectors(self, documents: list[Document]) -> None:
        """
        Constructs weighted vectors for all documents in the corpus.

        The weight for a term in a document is calculated using the formula:
        W = (1 + log(tf)) * idf. This reduces the impact of highly frequent 
        terms within a single document while boosting rare, descriptive terms.

        Args:
            documents (list[Document]): The collection of documents to vectorize.

        Complexity:
            O(V), where V is the number of unique term-document pairs in the index.
        """

        self.doc_vectors = {}
        for term, postings in self.index.index.items():
            idf = self.index.idf(term)
            for p in postings:
                self.doc_vectors.setdefault(p.doc_id, {})
                # Log-frequency weighting to dampen the effect of high TF
                self.doc_vectors[p.doc_id][term] = (1 + math.log(p.tf)) * idf

    def cosine_similarity(self, q_vec: Dict[str, float], doc_vec: Dict[str, float]) -> float:
        """
        Calculates the Cosine Similarity between a query vector and a document vector.

        Cosine Similarity measures the cosine of the angle between two vectors 
        in an n-dimensional space. This metric is length-invariant, meaning 
        topical similarity is determined by the term distribution rather than 
        the document volume.

        Args:
            q_vec (Dict[str, float]): The weighted query vector.
            doc_vec (Dict[str, float]): The weighted document vector.

        Returns:
            float: A similarity score between 0.0 and 1.0.
        """

        if not q_vec or not doc_vec:
            return 0.0
        dot = 0.0

        # Calculate the Dot Product
        for term, q_w in q_vec.items():
            d_w = doc_vec.get(term)
            if d_w is not None:
                dot += q_w * d_w

       # Helper function to calculate the Euclidean Norm (magnitude)
        def norm(vec: Dict[str, float]) -> float:
            return math.sqrt(sum(w * w for w in vec.values()))

        qn = norm(q_vec)
        dn = norm(doc_vec)
        if qn == 0 or dn == 0:
            return 0.0

        # Cosine similarity formula: (A . B) / (||A|| * ||B||)
        return dot / (qn * dn)

    def jaccard_similarity(self, query_terms, doc_id):
        """
        Calculates Jaccard Similarity as a set-theoretic baseline.

        Jaccard Similarity measures the ratio of the size of the intersection 
        to the size of the union of the query and document term sets. 
        Unlike Cosine, it ignores term importance (IDF) and weights.

        Args:
            query_terms (List[str]): The processed terms from the query.
            doc_id (int): The identifier of the document to compare.

        Returns:
            float: The Jaccard coefficient.
        """

        # Retrieve document terms from the inverted index efficiently
        doc_terms = set()
        for term, postings in self.index.index.items():
            if any(p.doc_id == doc_id for p in postings):
                doc_terms.add(term)

        query_terms_set = set(query_terms)

        # Intersection over Union
        intersection = query_terms_set.intersection(doc_terms)
        union = query_terms_set.union(doc_terms)

        if not union:
            return 0.0

        return len(intersection) / len(union)

    def make_query_vector(self, terms: List[str]) -> Dict[str, float]:
        """
        Transforms a list of query terms into a weighted TF-IDF vector.

        Args:
            terms (List[str]): Processed query tokens.

        Returns:
            Dict[str, float]: A dictionary mapping terms to their TF-IDF weights.
        """

        # Count raw term frequency within the query
        tf_map: Dict[str, int] = {}
        for t in terms:
            tf_map[t] = tf_map.get(t, 0) + 1

        q_vec: Dict[str, float] = {}
        for t, tf in tf_map.items():
            idf = self.index.idf(t)
            # Only include terms that exist in the corpus (IDF > 0)
            if idf > 0:
                q_vec[t] = (1 + math.log(tf)) * idf
        return q_vec
