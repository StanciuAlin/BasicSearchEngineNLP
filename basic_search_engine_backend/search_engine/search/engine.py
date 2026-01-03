from typing import List, Dict, Any
from ..models.search_result import SearchResult
from ..utils.text_loader import load_documents_from_folder
from ..indexing.document_store import DocumentStore
from ..indexing.inverted_index import InvertedIndex
from ..indexing.tfidf import TfIdfWeighter
from ..preprocessing.factory import factory
from ..indexing.sklearn_tfidf import SklearnTfIdf

# TODO: Add caching for indexed corpora to speed up repeated indexing.
#       Use TfidfVectorizer from sklearn for more efficient vectorization if needed
#           to compare with custom implementation.
#       Use BM25 and analyse performance differences with k1 and b parameters.

# BM25: Este standardul actual în regăsirea informației (folosit de Elasticsearch).
# Analiza parametrilor k1 (saturația frecvenței termenilor) și b
# (penalizarea lungimii documentului) va arăta cum poți "acorda"
# motorul de căutare pentru documente lungi versus documente scurte.

# Analiza Query-urilor Multi-Cuvânt
# În codul curent din engine.py, query-ul este deja tratat ca un set de termeni:
# q_terms = [simple_stem(t) for t in normalize(query)].

# Provocare: Trebuie să decizi dacă motorul de căutare trebuie să returneze
# documente care conțin oricare din cuvinte(OR logic) sau toate(AND logic).

# Implementarea actuală: Folosește produsul scalar în cosine_similarity,
# ceea ce înseamnă că documentele care conțin mai mulți termeni din query
# vor primi automat un scor mai mare.


class SearchEngine:
    def __init__(self):
        self.doc_store: DocumentStore | None = None
        self.index = InvertedIndex()
        self.weighter: TfIdfWeighter | None = None
        self.preprocessor = factory.get_preprocessor("custom")  # Default
        self.sklearn_engine = SklearnTfIdf()

    def set_mode(self, mode: str):
        """Schimbă strategia de preprocesare în timpul rulării."""
        self.preprocessor = factory.get_preprocessor(mode)

    def index_corpus(self, folder: str) -> None:
        documents = load_documents_from_folder(folder)
        self.doc_store = DocumentStore(documents)

        # 1. Indexarea ta manuală (Educațională)
        self.index.build(documents)
        self.weighter = TfIdfWeighter(self.index)
        self.weighter.build_doc_vectors(documents)

        # 2. Indexarea Sklearn (Profesională)
        self.sklearn_engine.build_index(documents)

    def list_documents(self) -> List[Dict[str, Any]]:
        if not self.doc_store:
            return []
        return [
            {"doc_id": d.doc_id, "title": d.title}
            for d in self.doc_store.documents
        ]

    def get_document(self, doc_id: int) -> Dict[str, Any] | None:
        if not self.doc_store:
            return None
        try:
            d = self.doc_store.get(doc_id)
        except KeyError:
            return None
        return {"doc_id": d.doc_id, "title": d.title, "content": d.content}

    def search(self, query: str, top_k: int = 10,
               mode: str = "custom",
               ranking_method: str = "cosine") -> List[SearchResult]:
        if not self.doc_store:
            return []

        results: List[SearchResult] = []

        # Modul Sklearn: Folosește motorul optimizat extern
        if mode == "sklearn":
            search_hits = self.sklearn_engine.search(query)
            for doc_id, score in search_hits:
                doc = self.doc_store.get(doc_id)
                if doc:
                    results.append(self._create_result(doc, score))
        else:
            # 1. Preprocesare query (o singură dată)
            q_terms = self.preprocessor.process(query)

            # OPTIMIZARE: Calculăm vectorul query-ului O SINGURĂ DATĂ înainte de buclă
            q_vec = None
            if ranking_method == "cosine":
                q_vec = self.weighter.make_query_vector(q_terms)

            # 2. Calcul scor bazat pe metoda aleasă
            for doc in self.doc_store.documents:
                score = 0.0
                if ranking_method == "cosine":
                    doc_vec = self.weighter.doc_vectors.get(doc.doc_id, {})
                    score = self.weighter.cosine_similarity(q_vec, doc_vec)
                elif ranking_method == "jaccard":
                    score = self.weighter.jaccard_similarity(
                        q_terms, doc.doc_id)

                if score > 0:
                    results.append(self._create_result(doc, score))

        # 3. Sortare și returnare
        results.sort(key=lambda r: r.score, reverse=True)
        return results[:top_k]

    def _create_result(self, doc, score):
        snippet = doc.content[:220].replace("\n", " ")
        return SearchResult(
            doc_id=doc.doc_id,
            title=doc.title,
            score=round(score, 4),
            snippet=snippet + ("..." if len(doc.content) > 220 else "")
        )


'''Notes:
De ce este importantă această clasă separată?

1. Performanță: SklearnTfIdf folosește matrici rare (sparse matrices) din scipy, ceea ce înseamnă 
că ocupă mult mai puțină memorie decât dicționarele de vectori din Python.
2. Modularitate: Dacă vrei să schimbi ceva la modul de calcul profesional 
(de exemplu, să adaugi n-grame), modifici doar în sklearn_tfidf.py, fără să strici logica educațională.
3. Corectitudinea Importurilor: Această structură previne erorile de import circular, 
deoarece engine.py este singurul care coordonează fluxul.
'''
