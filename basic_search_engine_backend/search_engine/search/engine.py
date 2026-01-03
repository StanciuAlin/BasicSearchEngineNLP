from typing import List, Dict, Any
from ..models.search_result import SearchResult
from ..utils.text_loader import load_documents_from_folder
from ..indexing.document_store import DocumentStore
from ..indexing.inverted_index import InvertedIndex
from ..indexing.tfidf import TfIdfWeighter
from ..preprocessing.normalizer import normalize
from ..preprocessing.stemmer import simple_stem

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

    def index_corpus(self, folder: str) -> None:
        documents = load_documents_from_folder(folder)
        self.doc_store = DocumentStore(documents)
        self.index.build(documents)
        self.weighter = TfIdfWeighter(self.index)
        self.weighter.build_doc_vectors(documents)

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

    def search(self, query: str, top_k: int = 10) -> List[SearchResult]:
        if not self.doc_store or not self.weighter:
            return []
        q_terms = [simple_stem(t) for t in normalize(query)]
        q_vec = self.weighter.make_query_vector(q_terms)
        results: List[SearchResult] = []
        for doc in self.doc_store.documents:
            doc_vec = self.weighter.doc_vectors.get(doc.doc_id, {})
            score = self.weighter.cosine_similarity(q_vec, doc_vec)
            if score <= 0:
                continue
            snippet = doc.content[:220].replace("\n", " ")
            results.append(
                SearchResult(
                    doc_id=doc.doc_id,
                    title=doc.title,
                    score=round(score, 4),
                    snippet=snippet +
                    ("..." if len(doc.content) > 220 else ""),
                )
            )
        results.sort(key=lambda r: r.score, reverse=True)
        return results[:top_k]
