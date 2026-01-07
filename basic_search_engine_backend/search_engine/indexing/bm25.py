import math
from typing import List, Dict
from .inverted_index import InvertedIndex

"""
Module: bm25.py
Description: Implements the Okapi BM25 (Best Matching 25) ranking function. 
BM25 is a state-of-the-art probabilistic retrieval model used to estimate 
the relevance of documents to a given search query.
"""


class BM25Weighter:
    """
    A probabilistic weighting engine based on the BM25 algorithm.

    BM25 improves upon standard TF-IDF by introducing non-linear term frequency 
    saturation and document length normalization. This ensures that long 
    documents are not unfairly advantaged simply by having more words.
    """

    def __init__(self, index: InvertedIndex, k1: float = 1.5, b: float = 0.75):
        """
        Initializes the BM25 weighter with the index and tuning parameters.

        Args:
            index (InvertedIndex): Reference to the index providing corpus statistics.
            k1 (float): Term frequency saturation parameter. Controls how quickly 
                       an additional occurrence of a term increases the score.
            b (float): Length normalization parameter (0 to 1). 1.0 provides full 
                      normalization based on document length.
        """

        self.index = index
        self.k1 = k1
        self.b = b

    def calculate_score(self, query_terms: List[str], doc_id: int) -> float:
        """
        Computes the BM25 relevance score for a specific document.

        The formula incorporates:
        1. IDF: To weight rare terms higher than common ones.
        2. TF Saturation: Using k1 to limit the influence of term repetition.
        3. Length Normalization: Using b and the average document length to 
           adjust for variations in content volume.

        Args:
            query_terms (List[str]): Processed tokens from the user query.
            doc_id (int): The unique identifier of the document to be scored.

        Returns:
            float: The final probabilistic relevance score.

        Complexity:
            O(Q * P), where Q is the number of query terms and P is the 
            average length of a posting list for a term.
        """

        score = 0.0
        doc_len = self.index.doc_lengths.get(doc_id, 0)

        # Base case: avoid processing documents with no content
        if doc_len == 0:
            return 0.0

        for term in query_terms:
            if term not in self.index.index:
                continue

            # Retrieve the term frequency (tf) for this specific document from the index
            term_postings = self.index.index[term]
            tf = next((p.tf for p in term_postings if p.doc_id == doc_id), 0.0)

            if tf > 0:
                # Retrieve the smoothed IDF for the term
                idf = self.index.idf(term)

                # BM25 Core Formula Implementation:
                # Score = IDF * [(TF * (k1 + 1)) / (TF + k1 * (1 - b + b * (doc_len / avg_len)))]
                numerator = tf * (self.k1 + 1)
                denominator = tf + self.k1 * \
                    (1 - self.b + self.b * (doc_len / self.index.avg_doc_length))

                score += idf * (numerator / denominator)

        return score
