from fastapi import FastAPI, Query
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from search_engine import SearchEngine
from search_engine.preprocessing.factory import factory  # Importăm instanța globală

app = FastAPI(title="Basic Search Engine API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = SearchEngine()
engine.index_corpus("data/docs")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/documents")
def documents():
    return engine.list_documents()


@app.get("/documents/{doc_id}")
def document(doc_id: int):
    doc = engine.get_document(doc_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc

# Endpoint pentru TF-IDF (Cosine Similarity)


@app.get("/search/tfidf")
async def search_tfidf(
    query: str,
    page: int = 1,
    page_size: int = 5,
    mode: str = "custom"
):
    return engine.search(
        query=query,
        page=page,
        page_size=page_size,
        mode=mode,
        ranking_method="cosine"
    )

# Endpoint pentru BM25 (Parametri specifici obligatorii)


@app.get("/search/bm25")
async def search_bm25(
    query: str,
    k1: float = 1.5,
    b: float = 0.75,
    page: int = 1,
    page_size: int = 5,
    mode: str = "custom"
):
    return engine.search(
        query=query,
        page=page,
        page_size=page_size,
        mode=mode,
        ranking_method="bm25",
        k1=k1,
        b=b
    )

# Endpoint pentru Jaccard


@app.get("/search/jaccard")
async def search_jaccard(
    query: str,
    page: int = 1,
    page_size: int = 5,
    mode: str = "custom"
):
    return engine.search(
        query=query,
        page=page,
        page_size=page_size,
        mode=mode,
        ranking_method="jaccard"
    )

# Endpoint pentru Sklearn (Mod separat)


@app.get("/search/sklearn")
async def search_sklearn(
    query: str,
    page: int = 1,
    page_size: int = 5
):
    return engine.search(
        query=query,
        page=page,
        page_size=page_size,
        mode="sklearn"
    )

# @app.get("/search")
# def search(query: str = Query(..., min_length=1),
#            page: int = 1,
#            page_size: int = 5,
#            mode: str = "custom",
#            ranking: str = "cosine",
#            k1: float = 1.5,
#            b: float = 0.75):
#     data = engine.search(
#         query=q,
#         page=page,
#         mode=mode,
#         ranking_method=ranking,
#         k1=k1,
#         b=b
#     )

#     # Mapăm rezultatele pentru a menține compatibilitatea cu DTO-ul de SearchResult
#     return {
#         "total": data["total"],
#         "results": [
#             {
#                 "doc_id": r.doc_id,
#                 "title": r.title,
#                 "score": r.score,
#                 "snippet": r.snippet
#             } for r in data["results"]
#         ]
#     }
