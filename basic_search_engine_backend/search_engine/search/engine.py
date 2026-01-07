import os
from typing import List, Dict, Any
from ..models.search_result import SearchResult
from ..utils.text_loader import load_documents_from_folder
from ..indexing.document_store import DocumentStore
from ..indexing.sklearn_tfidf import SklearnTfIdf
from ..indexing.inverted_index import InvertedIndex
from ..indexing.tfidf import TfIdfWeighter
from ..indexing.bm25 import BM25Weighter
from ..preprocessing.factory import factory
from .cache_manager import SearchCache


"""
Module: engine.py
Description: Acts as the central orchestration layer of the Information Retrieval system. 
It integrates the document store, indexing engines, weighting models, and caching 
mechanisms to provide a unified search interface.
"""


class SearchEngine:
    """
    The core coordinator of the search system.

    This class manages the lifecycle of document indexing and query execution. 
    It supports multiple ranking algorithms (TF-IDF, BM25, Jaccard, Sklearn) 
    and handles results pagination, snippet generation, and persistence.
    """

    def __init__(self):
        """
        Initializes the search engine components and dependencies.
        """
        self.doc_store = DocumentStore()
        self.sklearn_engine = SklearnTfIdf()
        self.index = InvertedIndex()
        self.weighter = TfIdfWeighter(self.index)
        self.bm25_weighter = BM25Weighter(self.index)
        self.preprocessor = factory.get_preprocessor("custom")
        self.cache = SearchCache("data/library.db")

    def index_corpus(self, folder: str = "data/docs") -> None:
        """
        Synchronizes the document store with files from the disk and builds the in-memory index.

        This method avoids duplicates by checking existing document IDs in the SQLite 
        database and allows for incremental updates to the index without re-processing 
        the entire corpus.

        Args:
            folder (str): Path to the directory containing text documents (.txt).

        Complexity:
            O(N * M) for loading, plus O(T) for index construction, where T is the 
            total number of terms in the corpus.
        """

        # 1. Sincronise: Add documents from folder that are not already in DB
        if folder and os.path.exists(folder):

            # Load the documents from disk
            docs_from_disk = load_documents_from_folder(folder)

            # Verify what is already in the database to avoid duplicates
            existing_metadata = self.doc_store.get_metadata_list()
            existing_ids = {m[0] for m in existing_metadata}

            # Filter only new documents
            new_docs = [
                d for d in docs_from_disk if d.doc_id not in existing_ids]

            if new_docs:
                print(
                    f"There are found {len(new_docs)} new documents in '{folder}'. Adding to SQLite...")
                self.doc_store.add_documents(new_docs)
            else:
                print(
                    f"The datebase is up to date with files from '{folder}'.")

        # 2. Load: We fetch ALL documents from SQLite for in-memory indexing
        metadata = self.doc_store.get_metadata_list()
        all_docs = []

        if not metadata:
            print(
                "Attention: No documents found in the database nor in folder to index.")

            return

        print(f"Indexing {len(metadata)} documents from the database...")
        for row in metadata:
            try:
                all_docs.append(self.doc_store.get(row[0]))
            except KeyError:
                continue

        # 3. Building search structures (In-Memory)
        # Rebuild the inverted index manually (Custom)
        self.index.build(all_docs)
        self.weighter.build_doc_vectors(all_docs)

        # Extract text from all documents to fit with Sklearn vectorizer
        corpus_texts = [d.content for d in all_docs]
        sklearn_proc = factory.get_preprocessor("sklearn")

        # Check if the preprocessor has 'fit' method for Sklearn strategy
        if hasattr(sklearn_proc, 'fit'):
            print("Fitting Sklearn Preprocessor with current corpus...")
            sklearn_proc.fit(corpus_texts)

        # Rebuild/Load Sklearn index
        if not self.sklearn_engine.load_index():
            self.sklearn_engine.build_index(all_docs)

        print("Indexing complete with success!")

    def search(self, query: str,
               page: int = 1,
               page_size: int = 10,
               mode: str = "custom",
               ranking_method: str = "cosine",
               k1: float = 1.5,
               b: float = 0.75,
               sort_order: str = "desc",
               search_logic: str = "OR") -> dict:
        """
        Executes a ranked search query based on the specified IR model and parameters.

        This method checks the cache before performing calculations. It supports 
        different ranking methods and applies boolean logic (AND/OR/Hybrid) to 
        filter and score results.

        Args:
            query (str): The search input.
            page (int): Current results page.
            page_size (int): results per page.
            mode (str): NLP strategy (custom, nltk, spacy).
            algorithm (str): Ranking model (tfidf, bm25, jaccard, sklearn).
            k1 (float): BM25 saturation parameter.
            b (float): BM25 length normalization parameter.
            logic (str): Boolean logic for term matching.
            sort_order (str): Result ordering (asc/desc).

        Returns:
            Dict[str, Any]: A dictionary containing total matches, paginated 
                            results as dictionaries, and metadata.
        """

        # Generate a unique key for caching based on all input parameters
        cache_key = f"{query}|{mode}|{ranking_method}|{k1}|{b}|{search_logic}|{sort_order}|{page}|{page_size}"

        cached_res = self.cache.get(cache_key)
        if cached_res:
            print(f"DEBUG: Cache Hit for: {query}")
            return cached_res

        # Configure the NLP strategy and BM25 parameters for the current session
        self.set_mode(mode)
        self.bm25_weighter.k1 = k1
        self.bm25_weighter.b = b

        # 1. Calculate the token count from the original (raw) query for metadata purposes
        raw_query_tokens = query.split()
        total_q_raw = len(raw_query_tokens)

        # 2. Obtain processed terms (after stop-word removal, lemmatization, etc.)
        q_terms = self.preprocessor.process(query)
        total_q_processed = len(q_terms)

        if not q_terms:
            return {"total": 0, "results": []}

        if mode == "sklearn":
            # Baseline search using the Scikit-Learn TF-IDF implementation
            hits_raw = self.sklearn_engine.search(query)

            # Retrieve document sets for each query term from the manual index to calculate matches
            term_sets = []
            for term in q_terms:
                if term in self.index.index:
                    term_sets.append(
                        {p.doc_id for p in self.index.index[term]})
                else:
                    term_sets.append(set())

            all_hits = []
            for doc_id, score in hits_raw:
                # Calculate match count by verifying presence of doc_id in term sets
                matches_count = sum(
                    1 for term_set in term_sets if doc_id in term_set)
                matches_info = f"{matches_count}/{total_q_processed}/{total_q_raw}"

                if score > 0:
                    all_hits.append((doc_id, score, matches_info))
        else:
            # Retrieve postings (document IDs) for each individual term
            term_sets = []
            for term in q_terms:
                if term in self.index.index:
                    term_sets.append(
                        {p.doc_id for p in self.index.index[term]})
                else:
                    term_sets.append(set())

            # Apply Boolean logic to determine the initial set of relevant document IDs
            if search_logic == "AND":
                relevant_doc_ids = set.intersection(
                    *term_sets) if term_sets else set()
            elif search_logic == "OR":
                relevant_doc_ids = set.union(
                    *term_sets) if term_sets else set()
            else:  # HYBRID (Logic with relevance boosting)
                relevant_doc_ids = set.union(
                    *term_sets) if term_sets else set()

            all_hits = []
            for doc_id in relevant_doc_ids:
                score = 0.0
                # Calculate how many query terms are present in this specific document
                matches_count = sum(
                    1 for term_set in term_sets if doc_id in term_set)
                matches_info = f"{matches_count}/{total_q_processed}/{total_q_raw}"
                # Compute relevance score based on the requested ranking method
                if ranking_method == "cosine":
                    q_vec = self.weighter.make_query_vector(q_terms)
                    doc_vec = self.weighter.doc_vectors.get(doc_id, {})
                    score = self.weighter.cosine_similarity(q_vec, doc_vec)
                elif ranking_method == "jaccard":
                    score = self.weighter.jaccard_similarity(q_terms, doc_id)
                elif ranking_method == "bm25":
                    score = self.bm25_weighter.calculate_score(q_terms, doc_id)

                # Hybrid Boost: If the document satisfies the AND condition, boost the score
                if search_logic == "HYBRID" and term_sets:
                    if doc_id in set.intersection(*term_sets):
                        score *= 1.5  # 50% score multiplier for full matches

                if score > 0:
                    all_hits.append((doc_id, score, matches_info))

        # Sort results based on score and the requested sort order
        # reverse=True for 'desc' to have highest scores first
        # reverse=False for 'asc' to have lowest scores first
        is_reverse = True if sort_order == "desc" else False
        all_hits.sort(key=lambda x: x[1], reverse=is_reverse)

        total_results = len(all_hits)

        # Apply pagination slicing
        start = (page - 1) * page_size
        end = start + page_size
        paged_hits = all_hits[start:end]

        results = []
        for hit in paged_hits:
            doc_id, score, matches_info = hit
            doc = self.doc_store.get(doc_id)
            # Pass matching metadata to the result formatter
            results.append(self._create_result(doc, score, matches_info))

        # Serialize SearchResult objects to dictionaries for JSON compatibility
        results_as_dicts = [r.to_dict() for r in results]

        final_response = {
            "total": total_results,
            "page": page,
            "page_size": page_size,
            "results": results_as_dicts,  # Save dictionaries, not objects
            "sort_order": sort_order
        }

        # Update the search cache with the newly calculated results
        self.cache.set(cache_key, final_response)
        return final_response

    def set_mode(self, mode: str):
        """
        Switches the active NLP preprocessing strategy in the factory.

        Args:
            mode (str): The strategy identifier (custom, nltk, spacy, sklearn).
        """

        self.preprocessor = factory.get_preprocessor(mode)

    def list_documents(self):
        """
        Retrieves a summary of all indexed documents for corpus inspection.

        Returns:
            list: A collection of dictionaries containing doc_id and title.
        """

        return [{"doc_id": r[0], "title": r[1]} for r in self.doc_store.get_metadata_list()]

    def get_document(self, doc_id: int):
        """
        Fetches the complete content of a specific document.

        Args:
            doc_id (int): Unique identifier for the document.

        Returns:
            dict: Document details or None if retrieval fails.
        """

        try:
            d = self.doc_store.get(doc_id)
            return {"doc_id": d.doc_id, "title": d.title, "content": d.content}
        except:
            return None

    def _create_result(self, doc, score, matches_info=""):
        """
        Helper method to format a raw document into a SearchResult with a text snippet.

        This method cleans the text of newlines and generates a fixed-length snippet, 
        ensuring words are not split mid-character.

        Args:
            doc (Document): The source document object.
            score (float): The calculated relevance score.
            matches_info (str): Metadata regarding term matching ratios.

        Returns:
            SearchResult: A formatted result object ready for UI display.
        """

        # Remove newlines to ensure a clean snippet presentation
        text = doc.content.replace("\n", " ")

        # Limit snippet to 220 characters, trimming at the last space to prevent word fragmentation
        limit = 220
        if len(text) <= limit:
            snippet = text
        else:
            snippet = text[:limit].rsplit(' ', 1)[0] + "..."

        return SearchResult(
            doc_id=doc.doc_id,
            title=doc.title,
            score=round(float(score), 4),
            snippet=snippet,
            matches=matches_info
        )
