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


@app.get("/search/compare")
async def search_compare(
    query: str,
    k1: float = 1.5,
    b: float = 0.75,
    page: int = 1,
    page_size: int = 5,
    mode: str = "custom"
):
    # Executăm căutarea principală (returnează un dicționar cu o listă de obiecte SearchResult)
    base_results = engine.search(
        query=query,
        page=page,
        page_size=page_size,
        mode=mode,
        ranking_method="bm25",
        k1=k1,
        b=b
    )

    # Preprocesăm query-ul o singură dată
    query_terms = engine.preprocessor.process(query)
    query_vector = engine.weighter.make_query_vector(query_terms)

    compare_results = []
    # base_results["results"] conține obiecte SearchResult, nu dicționare
    for res in base_results["results"]:
        # Accesăm atributele folosind punct (.)
        doc_id = res.doc_id

        # Calculăm restul scorurilor
        doc_vector = engine.weighter.doc_vectors.get(doc_id, {})
        cosine_val = engine.weighter.cosine_similarity(
            query_vector, doc_vector)
        jaccard_val = engine.weighter.jaccard_similarity(query_terms, doc_id)

        compare_results.append({
            "doc_id": doc_id,
            "title": res.title,
            "snippet": res.snippet,
            "score": res.score,
            "bm25_score": res.score,
            "cosine_score": round(float(cosine_val), 4),
            "jaccard_score": round(float(jaccard_val), 4)
        })

    return {
        "total": base_results["total"],
        "page": base_results["page"],
        "page_size": base_results["page_size"],
        "results": compare_results
    }
