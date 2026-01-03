import math
from collections import defaultdict
from typing import Dict, List
from ..models.document import Document
from ..models.posting import Posting
from ..preprocessing.normalizer import normalize
from ..preprocessing.stemmer import simple_stem


class InvertedIndex:
    def __init__(self):
        self.index: Dict[str, List[Posting]] = {}
        self.vocabulary: set[str] = set()
        self.num_docs: int = 0
        self._df: Dict[str, int] = {}

    def build(self, documents: List[Document]) -> None:
        postings = defaultdict(lambda: defaultdict(int))
        self.num_docs = len(documents)

        for doc in documents:
            # normalize + stem each document
            tokens = [simple_stem(t) for t in normalize(doc.content)]
            seen_terms = set()  # track unique terms in the document
            for term in tokens:
                # increment term frequency, increment occurrence by 1
                postings[term][doc.doc_id] += 1
                if term not in seen_terms:  # if term seen first time in this doc
                    # increment document frequency
                    self._df[term] = self._df.get(term, 0) + 1
                    seen_terms.add(term)

        self.index = {}
        self.vocabulary = set(postings.keys())
        for term, doc_tf_map in postings.items():
            self.index[term] = [
                Posting(doc_id=doc_id, tf=float(tf))
                for doc_id, tf in doc_tf_map.items()  # convert to Posting
            ]

    def idf(self, term: str) -> float:
        df = self._df.get(term, 0)
        if df == 0 or self.num_docs == 0:  # avoid division by zero
            return 0.0
        return math.log((1 + self.num_docs) / (1 + df)) + 1.0  # smoothed IDF
