from typing import List, Dict, Any
from ..models.search_result import SearchResult
from ..utils.text_loader import load_documents_from_folder
from ..indexing.document_store import DocumentStore
from ..indexing.sklearn_tfidf import SklearnTfIdf
from ..indexing.inverted_index import InvertedIndex
from ..indexing.tfidf import TfIdfWeighter
from ..indexing.bm25 import BM25Weighter
from ..preprocessing.factory import factory


class SearchEngine:
    def __init__(self):
        self.doc_store = DocumentStore()
        self.sklearn_engine = SklearnTfIdf()
        self.index = InvertedIndex()
        self.weighter = TfIdfWeighter(self.index)
        self.bm25_weighter = BM25Weighter(self.index)  # Inițializare BM25
        self.preprocessor = factory.get_preprocessor("custom")

    def index_corpus(self, folder: str) -> None:
        # 1. Încărcăm documentele din SQLite dacă există, altfel din folder
        all_docs = []
        metadata = self.doc_store.get_metadata_list()

        if not metadata and folder:
            print("Populăm baza de date din folder...")
            all_docs = load_documents_from_folder(folder)
            self.doc_store.add_documents(all_docs)
        else:
            print(
                f"Încărcăm {len(metadata)} documente din SQLite pentru indexare...")
            for row in metadata:
                all_docs.append(self.doc_store.get(row[0]))

        if not all_docs:
            print("Atenție: Nu există documente de indexat!")
            return

        # 2. Construim indexul manual (pentru modurile Custom/Pro)
        self.index.build(all_docs)
        self.weighter.build_doc_vectors(all_docs)

        # 3. Construim/Încărcăm indexul Sklearn
        if not self.sklearn_engine.load_index():
            self.sklearn_engine.build_index(all_docs)

    def search(self, query: str,
               page: int = 1,
               page_size: int = 10,
               mode: str = "custom",
               ranking_method: str = "cosine",
               k1: float = 1.5,
               b: float = 0.75) -> dict:
        self.set_mode(mode)
        
        # Actualizăm parametrii BM25
        self.bm25_weighter.k1 = k1
        self.bm25_weighter.b = b
        
        q_terms = self.preprocessor.process(query)

        if not q_terms:
            return {"total": 0, "results": []}

        all_hits = []
        if mode == "sklearn":
            all_hits = self.sklearn_engine.search(query)
        else:
            # Optimizare: Căutăm doar în documentele care conțin termenii din query
            relevant_doc_ids = set()
            for term in q_terms:
                if term in self.index.index:
                    relevant_doc_ids.update(
                        p.doc_id for p in self.index.index[term])

            for doc_id in relevant_doc_ids:
                score = 0.0
                if ranking_method == "cosine":
                    q_vec = self.weighter.make_query_vector(q_terms)
                    doc_vec = self.weighter.doc_vectors.get(doc_id, {})
                    score = self.weighter.cosine_similarity(q_vec, doc_vec)
                elif ranking_method == "jaccard":
                    score = self.weighter.jaccard_similarity(q_terms, doc_id)
                elif ranking_method == "bm25":
                    # Folosim noua metodă de ranking
                    score = self.bm25_weighter.calculate_score(q_terms, doc_id)

                if score > 0:
                    all_hits.append((doc_id, score))

            # Sortăm rezultatele educaționale după scor
            all_hits.sort(key=lambda x: x[1], reverse=True)

        total_results = len(all_hits)

        # Calculăm slice-ul pentru pagină
        start = (page - 1) * page_size
        end = start + page_size
        paged_hits = all_hits[start:end]

        results = []
        for doc_id, score in paged_hits:
            doc = self.doc_store.get(doc_id)
            results.append(self._create_result(doc, score))

        return {
            "total": total_results,
            "page": page,
            "page_size": page_size,
            "results": results
        }

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

    def _create_result(self, doc, score):
        snippet = doc.content[:220].replace("\n", " ")
        return SearchResult(
            doc_id=doc.doc_id,
            title=doc.title,
            score=round(float(score), 4),
            snippet=snippet + ("..." if len(doc.content) > 220 else "")
        )
