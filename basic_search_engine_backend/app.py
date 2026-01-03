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


@app.get("/search")
def search(q: str = Query(..., min_length=1), top_k: int = 10, mode: str = "custom", ranking: str = "cosine"):
    engine.set_mode(mode)
    results = engine.search(q, top_k=top_k, ranking_method=ranking)

    return {
        "query": q,
        "count": len(results),
        "results": [
            {
                "doc_id": r.doc_id,
                "title": r.title,
                "score": r.score,
                "snippet": r.snippet
            } for r in results
        ],
    }
