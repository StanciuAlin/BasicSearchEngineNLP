import time
from fastapi import FastAPI, Query
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from search_engine import SearchEngine
from search_engine.preprocessing.factory import factory  # Importăm instanța globală

"""
Module: app.py
Description: This is the main entry point for the FastAPI backend. It exposes the RESTful 
endpoints required for the search operations, document management, and model comparison.
"""

app = FastAPI(title="Basic Search Engine API")

# Setup CORS middleware to allow the .NET Blazor frontend to access the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the Search Engine core and index the local corpus
engine = SearchEngine()
engine.index_corpus("data/docs")


@app.get("/health")
def health():
    """
    Service health check.

    Returns:
        dict: A status indicator showing the API is operational.
    """
    return {"status": "ok"}


@app.get("/documents")
def documents():
    """
    Retrieves all metadata for the indexed documents in the store.

    Returns:
        list: A collection of document records.
    """
    return engine.list_documents()


@app.get("/documents/{doc_id}")
def document(doc_id: int):
    """
    Fetches a specific document's details by its ID.

    Args:
        doc_id (int): The unique identifier of the document.

    Returns:
        dict: Document content and metadata.

    Raises:
        HTTPException: 404 error if the document ID is not found.
    """
    doc = engine.get_document(doc_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@app.get("/search/tfidf")
async def search_tfidf(
    query: str,
    page: int = 1,
    page_size: int = 5,
    mode: str = "custom",
    logic: str = "OR",
    sort_order: str = "desc"
):
    """
    Executes a search using the Vector Space Model (TF-IDF with Cosine Similarity).

    Args:
        query (str): The search keywords.
        page (int): Pagination: current page.
        page_size (int): Pagination: results per page.
        mode (str): NLP preprocessing strategy (custom/nltk/spacy).
        logic (str): Boolean logic (AND/OR/Hybrid).
        sort_order (str): Result sorting order (asc/desc).

    Returns:
        dict: Search results and performance metrics.
    """
    start_time = time.perf_counter()
    results = engine.search(
        query=query,
        page=page,
        page_size=page_size,
        mode=mode,
        ranking_method="cosine",
        search_logic=logic,
        sort_order=sort_order
    )
    end_time = time.perf_counter()
    execution_time = (end_time - start_time) * 1000  # Convert to ms

    results["execution_time_ms"] = round(
        execution_time, 2)
    return results


@app.get("/search/bm25")
async def search_bm25(
    query: str,
    k1: float = 1.5,
    b: float = 0.75,
    page: int = 1,
    page_size: int = 5,
    mode: str = "custom",
    logic: str = "OR",
    sort_order: str = "desc"
):
    """
    Executes a search using the Probabilistic Model (Okapi BM25).

    Args:
        query (str): The search keywords.
        page (int): Pagination: current page.
        page_size (int): Pagination: results per page.
        mode (str): NLP preprocessing strategy.
        k1 (float): BM25 parameter for term frequency saturation.
        b (float): BM25 parameter for document length normalization.
        logic (str): Boolean logic.
        sort_order (str): Result sorting order.

    Returns:
        dict: Search results and performance metrics.
    """
    start_time = time.perf_counter()

    results = engine.search(
        query=query,
        page=page,
        page_size=page_size,
        mode=mode,
        ranking_method="bm25",
        k1=k1,
        b=b,
        search_logic=logic,
        sort_order=sort_order
    )

    end_time = time.perf_counter()
    execution_time = (end_time - start_time) * 1000  # Convert to ms

    results["execution_time_ms"] = round(
        execution_time, 2)
    return results


@app.get("/search/jaccard")
async def search_jaccard(
    query: str,
    page: int = 1,
    page_size: int = 5,
    mode: str = "custom",
    logic: str = "OR",
    sort_order: str = "desc"
):
    """
    Executes a search using Jaccard Similarity, a set-theoretic approach to Information Retrieval.

    This method evaluates the relevance of documents based on the intersection over the 
    union of terms between the query and the document, ignoring term frequency and weights.

    Args:
        query (str): The search keywords provided by the user.
        page (int): Pagination: current page number.
        page_size (int): Pagination: number of results per page.
        mode (str): NLP preprocessing strategy (custom, nltk, spacy).
        logic (str): Boolean search logic (AND, OR, Hybrid).
        sort_order (str): Sorting direction for the results (asc, desc).

    Returns:
        dict: A dictionary containing the ranked search results and the execution time in ms.
    """
    start_time = time.perf_counter()

    results = engine.search(
        query=query,
        page=page,
        page_size=page_size,
        mode=mode,
        ranking_method="jaccard",
        search_logic=logic,
        sort_order=sort_order
    )

    end_time = time.perf_counter()
    execution_time = (end_time - start_time) * 1000  # Convert to ms

    results["execution_time_ms"] = round(
        execution_time, 2)
    return results


@app.get("/search/sklearn")
async def search_sklearn(
    query: str,
    page: int = 1,
    page_size: int = 5,
    logic: str = "OR",
    sort_order: str = "desc"
):
    """
    Executes a search using the baseline Scikit-Learn TF-IDF implementation.

    This endpoint serves as a validation baseline to compare the performance and 
    accuracy of the custom-built inverted index against an industry-standard library.

    Args:
        query (str): The search keywords.
        page (int): Pagination: current page number.
        page_size (int): Pagination: results per page.
        logic (str): Boolean search logic.
        sort_order (str): Sorting direction.

    Returns:
        dict: Paginated search results using the Sklearn-based vector space model.
    """
    start_time = time.perf_counter()

    results = engine.search(
        query=query,
        page=page,
        page_size=page_size,
        mode="sklearn",
        search_logic=logic,
        sort_order=sort_order
    )

    end_time = time.perf_counter()
    execution_time = (end_time - start_time) * 1000  # Convert to ms

    results["execution_time_ms"] = round(
        execution_time, 2)
    return results


@app.get("/search/compare")
async def search_compare(
    query: str,
    k1: float = 1.5,
    b: float = 0.75,
    page: int = 1,
    page_size: int = 5,
    mode: str = "custom",
    logic: str = "OR",
    sort_order: str = "desc"
):
    """
    Cross-model benchmarking endpoint. Compares BM25, Cosine, and Jaccard scores 
    for a specific query.

    Args:
        query (str): The search keywords.
        mode (str): Preprocessing mode.
        k1 (float): BM25 k1 parameter.
        b (float): BM25 b parameter.
        logic (str): Search logic.

    Returns:
        dict: Comparison results containing multiple scores per document.
    """

    start_time = time.perf_counter()

    # Use BM25 as the base search to identify candidate documents
    base_results = engine.search(
        query=query,
        page=page,
        page_size=page_size,
        mode=mode,
        ranking_method="bm25",
        k1=k1,
        b=b,
        search_logic=logic,
        sort_order=sort_order
    )

    # Preprocess the query to obtain terms for manual similarity calculations
    query_terms = engine.preprocessor.process(query)
    query_vector = engine.weighter.make_query_vector(query_terms)

    compare_results = []
    # base_results["results"] conține obiecte SearchResult, nu dicționare
    for res in base_results.get("results", []):
        doc_id = res["doc_id"]

        doc_vector = engine.weighter.doc_vectors.get(doc_id, {})
        cosine_val = engine.weighter.cosine_similarity(
            query_vector, doc_vector)
        jaccard_val = engine.weighter.jaccard_similarity(query_terms, doc_id)

        # sklearn_val = sklearn_scores.get(doc_id, 0.0)

        compare_results.append({
            "doc_id": doc_id,
            "title": res["title"],
            "snippet": res["snippet"],
            "score": res["score"],
            "bm25_score": res["score"],
            "cosine_score": round(float(cosine_val), 4),
            "jaccard_score": round(float(jaccard_val), 4),
            # "sklearn_score": round(float(sklearn_val), 4),
            "matches": res.get("matches", "")
        })

    end_time = time.perf_counter()
    execution_time_ms = round((end_time - start_time)
                              * 1000, 2)  # Copmpute in ms

    return {
        "total": base_results["total"],
        "page": base_results["page"],
        "page_size": base_results["page_size"],
        "sort_order": sort_order,
        "execution_time_ms": execution_time_ms,
        "results": compare_results
    }
