import math
from typing import Dict
from .inverted_index import InvertedIndex
from ..models.document import Document

# TODO: Add Jaccard or Okapi BM25 weighting schemes later.

class TfIdfWeighter:
    def __init__(self, index: InvertedIndex):
        self.index = index
        self.doc_vectors: Dict[int, Dict[str, float]] = {}

    def build_doc_vectors(self, documents: list[Document]) -> None:
        self.doc_vectors = {}
        for term, postings in self.index.index.items():
            idf = self.index.idf(term)
            for p in postings:
                self.doc_vectors.setdefault(p.doc_id, {})
                self.doc_vectors[p.doc_id][term] = (1 + math.log(p.tf)) * idf

    def cosine_similarity(self, q_vec: Dict[str, float], doc_vec: Dict[str, float]) -> float:
        if not q_vec or not doc_vec:
            return 0.0
        dot = 0.0
        for term, q_w in q_vec.items():
            d_w = doc_vec.get(term)
            if d_w is not None:
                dot += q_w * d_w

        def norm(vec: Dict[str, float]) -> float:
            return math.sqrt(sum(w * w for w in vec.values()))
        qn = norm(q_vec)
        dn = norm(doc_vec)
        if qn == 0 or dn == 0:
            return 0.0
        return dot / (qn * dn)

    def make_query_vector(self, terms: list[str]) -> Dict[str, float]:
        tf_map: Dict[str, int] = {}
        for t in terms:
            tf_map[t] = tf_map.get(t, 0) + 1
        q_vec: Dict[str, float] = {}
        for t, tf in tf_map.items():
            idf = self.index.idf(t)
            if idf == 0:
                continue
            q_vec[t] = (1 + math.log(tf)) * idf
        return q_vec
