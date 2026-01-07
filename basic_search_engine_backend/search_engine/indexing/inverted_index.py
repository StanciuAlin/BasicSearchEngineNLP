import math
from collections import defaultdict
from typing import Dict, List
from ..models.document import Document
from ..models.posting import Posting
from ..preprocessing.core.normalizer import normalize
from ..preprocessing.core.stemmer import simple_stem

"""
Module: inverted_index.py
Description: Implements the primary data structure for the search engine. 
The Inverted Index maps unique terms to their occurrences across the corpus, 
enabling sub-linear retrieval and providing the foundation for ranking algorithms.
"""


class InvertedIndex:
    """
    A manually engineered Inverted Index for efficient text retrieval.

    This class manages the mapping between terms and documents, calculates 
    global statistics such as Document Frequency (DF) and Inverse Document 
    Frequency (IDF), and tracks document lengths required for advanced 
    ranking models like BM25.
    """

    def __init__(self):
        """
        Initializes an empty Inverted Index and its associated metadata stores.
        """

        # Dictionary mapping each unique term to a list of Posting objects
        self.index: Dict[str, List[Posting]] = {}
        # Set containing all unique terms present in the indexed corpus
        self.vocabulary: set[str] = set()
        # Total count of documents successfully indexed
        self.num_docs: int = 0
        # Internal dictionary tracking the document frequency (DF) for each term
        self._df: Dict[str, int] = {}
        # Stores the total token count for each document by its ID
        self.doc_lengths: Dict[int, int] = {}
        # The average length of all documents in the corpus, used for BM25 normalization
        self.avg_doc_length: float = 0.0

    def build(self, documents: List[Document]) -> None:
        """
        Constructs the Inverted Index from a collection of Document objects.

        This process involves:
        1. Normalizing and stemming the content of each document.
        2. Updating the global term-document frequency mapping.
        3. Calculating individual and average document lengths.
        4. Converting temporary frequency maps into optimized Posting lists.

        Args:
            documents (List[Document]): The collection of documents to be indexed.

        Complexity:
            O(T), where T is the total number of tokens across all documents.
        """

        # Temporary nested dictionary to accumulate frequencies: {term: {doc_id: tf}}
        postings = defaultdict(lambda: defaultdict(int))
        self.num_docs = len(documents)
        total_length = 0

        for doc in documents:
            # Normalize and apply custom stemming to each document's content
            tokens = [simple_stem(t) for t in normalize(doc.content)]
            doc_len = len(tokens)
            self.doc_lengths[doc.doc_id] = doc_len
            total_length += doc_len

            # Track unique terms within the current document for DF calculation
            seen_terms = set()
            for term in tokens:
                # Increment raw term frequency (TF) for this document
                postings[term][doc.doc_id] += 1
                if term not in seen_terms:
                    # Increment the global document frequency (DF) for the term
                    self._df[term] = self._df.get(term, 0) + 1
                    seen_terms.add(term)

        # Finalize the index by converting maps to Posting objects
        self.index = {}
        self.vocabulary = set(postings.keys())
        for term, doc_tf_map in postings.items():
            self.index[term] = [
                Posting(doc_id=doc_id, tf=float(tf))
                for doc_id, tf in doc_tf_map.items()  # convert to Posting
            ]

        # Calculate the average document length required for BM25 probabilistic ranking
        if self.num_docs > 0:
            self.avg_doc_length = total_length / self.num_docs

    def idf(self, term: str) -> float:
        """
        Calculates the Smoothed Inverse Document Frequency (IDF) for a term.

        IDF evaluates the global importance of a term. Terms that appear in 
        many documents (e.g., "and", "the") receive a lower score, while 
        rarer terms receive a boost.

        Args:
            term (str): The term for which to calculate the weight.

        Returns:
            float: The calculated IDF weight. Returns 0.0 if the term is not indexed.
        """

        df = self._df.get(term, 0)
        # Avoid division by zero if the term or corpus is missing
        if df == 0 or self.num_docs == 0:
            return 0.0

        # Standard smoothed IDF formula: log((1 + N) / (1 + df)) + 1.0
        return math.log((1 + self.num_docs) / (1 + df)) + 1.0
