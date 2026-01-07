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


class SearchEngine:
    """The main class for the search engine."""

    def __init__(self):
        self.doc_store = DocumentStore()
        self.sklearn_engine = SklearnTfIdf()
        self.index = InvertedIndex()
        self.weighter = TfIdfWeighter(self.index)
        self.bm25_weighter = BM25Weighter(self.index)  # Inițializare BM25
        self.preprocessor = factory.get_preprocessor("custom")
        self.cache = SearchCache("data/library.db")

    def index_corpus(self, folder: str = "data/docs") -> None:
        """ Sincronise the document store with files from disk (without duplicates)
                and rebuild the in-memory index.

            Args:
             folder (str): Path to the folder containing documents to index.

            Notes:
                Manages duplicates by checking existing document IDs in the database.
                Flexible to add new documents without re-indexing existing ones.
                Efficiently builds the in-memory index for fast searching.
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

        # Extragem textele tuturor documentelor pentru a face "fit" pe vectorizer-ul Sklearn
        corpus_texts = [d.content for d in all_docs]
        sklearn_proc = factory.get_preprocessor("sklearn")

        # Verificăm dacă preprocesorul are metoda 'fit' (specifică strategiei Sklearn)
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

        cache_key = f"{query}|{mode}|{ranking_method}|{k1}|{b}|{search_logic}|{sort_order}|{page}|{page_size}"

        # Încercăm să luăm din cache
        cached_res = self.cache.get(cache_key)
        if cached_res:
            print(f"DEBUG: Cache Hit for: {query}")
            return cached_res

        self.set_mode(mode)

        # Actualizăm parametrii BM25
        self.bm25_weighter.k1 = k1
        self.bm25_weighter.b = b

        # 1. Calculăm numărul de tokeni din query-ul original (brut)
        # Folosim o separare simplă sau regex pentru acuratețe
        raw_query_tokens = query.split()
        total_q_raw = len(raw_query_tokens)

        # 2. Obținem termenii procesați (fără stop-words, lematizați etc.)
        q_terms = self.preprocessor.process(query)
        total_q_processed = len(q_terms)

        if not q_terms:
            return {"total": 0, "results": []}

        if mode == "sklearn":
            # all_hits = self.sklearn_engine.search(query)
            # sklearn_engine.search returns (doc_id, score)
            hits_raw = self.sklearn_engine.search(query)

            # Obținem seturile de documente pentru fiecare termen din query folosind indexul manual
            # pentru a putea calcula matches_count
            term_sets = []
            for term in q_terms:
                if term in self.index.index:
                    term_sets.append(
                        {p.doc_id for p in self.index.index[term]})
                else:
                    term_sets.append(set())

            all_hits = []
            for doc_id, score in hits_raw:
                # Calculăm matches_count verificând prezența doc_id în seturile fiecărui termen
                matches_count = sum(
                    1 for term_set in term_sets if doc_id in term_set)
                matches_info = f"{matches_count}/{total_q_processed}/{total_q_raw}"

                if score > 0:
                    all_hits.append((doc_id, score, matches_info))
        else:
            # Obținem postings pentru fiecare termen separat
            term_sets = []
            for term in q_terms:
                if term in self.index.index:
                    term_sets.append(
                        {p.doc_id for p in self.index.index[term]})
                else:
                    term_sets.append(set())

            # Aplicăm logica booleană pentru a determina documentele relevante
            if search_logic == "AND":
                relevant_doc_ids = set.intersection(
                    *term_sets) if term_sets else set()
            elif search_logic == "OR":
                relevant_doc_ids = set.union(
                    *term_sets) if term_sets else set()
            else:  # HYBRID (Logică de Boost)
                relevant_doc_ids = set.union(
                    *term_sets) if term_sets else set()
                # Documentele care conțin toți termenii primesc un identificator de relevanță (opțional)

            all_hits = []
            for doc_id in relevant_doc_ids:
                score = 0.0
                # Calculăm câți termeni din query se află în acest document
                matches_count = sum(
                    1 for term_set in term_sets if doc_id in term_set)
                matches_info = f"{matches_count}/{total_q_processed}/{total_q_raw}"
                # Calculăm scorul folosind metodele existente
                if ranking_method == "cosine":
                    q_vec = self.weighter.make_query_vector(q_terms)
                    doc_vec = self.weighter.doc_vectors.get(doc_id, {})
                    score = self.weighter.cosine_similarity(q_vec, doc_vec)
                elif ranking_method == "jaccard":
                    score = self.weighter.jaccard_similarity(q_terms, doc_id)
                elif ranking_method == "bm25":
                    score = self.bm25_weighter.calculate_score(q_terms, doc_id)

                # Bonus Hibrid: dacă documentul conține toți termenii (AND), mărim scorul
                if search_logic == "HYBRID" and term_sets:
                    if doc_id in set.intersection(*term_sets):
                        score *= 1.5  # Boost de 50% pentru potrivire completă

                if score > 0:
                    all_hits.append((doc_id, score, matches_info))

        # Sorting
        # reverse=True for 'desc' to have highest scores first
        # reverse=False for 'asc' to have lowest scores first
        is_reverse = True if sort_order == "desc" else False
        all_hits.sort(key=lambda x: x[1], reverse=is_reverse)

        total_results = len(all_hits)

        # Calculăm slice-ul pentru pagină
        start = (page - 1) * page_size
        end = start + page_size
        paged_hits = all_hits[start:end]

        results = []
        for hit in paged_hits:
            doc_id, score, matches_info = hit  # Despachetăm cele 3 valori
            doc = self.doc_store.get(doc_id)
            # Trimitem matches_info către _create_result
            results.append(self._create_result(doc, score, matches_info))

        # Transformăm lista de obiecte SearchResult în listă de dicționare pentru JSON
        results_as_dicts = [r.to_dict() for r in results]

        final_response = {
            "total": total_results,
            "page": page,
            "page_size": page_size,
            "results": results_as_dicts,  # Salvăm dicționarele, nu obiectele
            "sort_order": sort_order
        }

        self.cache.set(cache_key, final_response)
        return final_response
        # return {
        #     "total": total_results,
        #     "page": page,
        #     "page_size": page_size,
        #     "results": results,
        #     "sort_order": sort_order
        # }

    def set_mode(self, mode: str):
        self.preprocessor = factory.get_preprocessor(mode)

    def list_documents(self):
        return [{"doc_id": r[0], "title": r[1]} for r in self.doc_store.get_metadata_list()]

    def get_document(self, doc_id: int):
        try:
            d = self.doc_store.get(doc_id)
            return {"doc_id": d.doc_id, "title": d.title, "content": d.content}
        except:
            return None

    def _create_result(self, doc, score, matches_info=""):
        # Găsim conținutul fără newline-uri
        text = doc.content.replace("\n", " ")

        # Limităm la 220 caractere, dar tăiem la ultimul spațiu pentru a nu fragmenta cuvinte
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
