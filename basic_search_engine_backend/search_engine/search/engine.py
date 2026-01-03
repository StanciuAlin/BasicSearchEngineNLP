from typing import List, Dict, Any
from ..models.search_result import SearchResult
from ..utils.text_loader import load_documents_from_folder
from ..indexing.document_store import DocumentStore
from ..indexing.sklearn_tfidf import SklearnTfIdf
from ..indexing.inverted_index import InvertedIndex
from ..indexing.tfidf import TfIdfWeighter
from ..preprocessing.factory import factory


class SearchEngine:
    def __init__(self):
        self.doc_store = DocumentStore()
        self.sklearn_engine = SklearnTfIdf()
        self.index = InvertedIndex()
        self.weighter = TfIdfWeighter(self.index)
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

    def search(self, query: str, top_k: int = 10, mode: str = "custom", ranking_method: str = "cosine") -> List[SearchResult]:
        self.set_mode(mode)
        q_terms = self.preprocessor.process(query)

        if not q_terms:
            return []

        results: List[SearchResult] = []

        if mode == "sklearn":
            # Folosește motorul Sklearn
            hits = self.sklearn_engine.search(query)
            for doc_id, score in hits[:top_k]:
                doc = self.doc_store.get(doc_id)
                results.append(self._create_result(doc, score))
        else:
            # Modurile educaționale (Custom/NLTK) folosind TfIdfWeighter
            q_vec = self.weighter.make_query_vector(q_terms)
            metadata = self.doc_store.get_metadata_list()

            for row in metadata:
                doc_id = row[0]
                score = 0.0
                if ranking_method == "cosine":
                    doc_vec = self.weighter.doc_vectors.get(doc_id, {})
                    score = self.weighter.cosine_similarity(q_vec, doc_vec)
                elif ranking_method == "jaccard":
                    score = self.weighter.jaccard_similarity(q_terms, doc_id)

                if score > 0:
                    doc = self.doc_store.get(doc_id)
                    results.append(self._create_result(doc, score))

        results.sort(key=lambda r: r.score, reverse=True)
        return results[:top_k]

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
