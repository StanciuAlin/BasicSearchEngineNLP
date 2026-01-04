import math
from typing import List, Dict
from .inverted_index import InvertedIndex


class BM25Weighter:
    def __init__(self, index: InvertedIndex, k1: float = 1.5, b: float = 0.75):
        self.index = index
        self.k1 = k1
        self.b = b

    def calculate_score(self, query_terms: List[str], doc_id: int) -> float:
        score = 0.0
        doc_len = self.index.doc_lengths.get(doc_id, 0)

        if doc_len == 0:
            return 0.0

        for term in query_terms:
            if term not in self.index.index:
                continue

            # Căutăm frecvența termenului (tf) în documentul specific
            term_postings = self.index.index[term]
            tf = next((p.tf for p in term_postings if p.doc_id == doc_id), 0.0)

            if tf > 0:
                idf = self.index.idf(term)
                # Formula BM25
                numerator = tf * (self.k1 + 1)
                denominator = tf + self.k1 * \
                    (1 - self.b + self.b * (doc_len / self.index.avg_doc_length))
                score += idf * (numerator / denominator)

        return score
