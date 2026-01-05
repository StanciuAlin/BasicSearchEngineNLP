import json
import numpy as np
from search_engine.search.engine import SearchEngine
from search_engine.evaluation.evaluator import IREvaluator


def run_benchmark():
    engine = SearchEngine()
    engine.index_corpus("data/docs")  # Asigură-te că indexul e gata

    with open("data/eval_queries.json", "r") as f:
        queries = json.load(f)

    # Configurări de testat
    configs = [
        {"name": "TF-IDF", "method": "cosine", "params": {}},
        {"name": "BM25 (Standard)", "method": "bm25",
         "params": {"k1": 1.5, "b": 0.75}},
        {"name": "BM25 (Tuned)", "method": "bm25",
         "params": {"k1": 1.2, "b": 0.8}},
        {"name": "Jaccard", "method": "jaccard", "params": {}}
    ]

    results_table = []

    for config in configs:
        mrr_scores, ap_scores, ndcg_scores, p5_scores = [], [], [], []

        for q_data in queries:
            res = engine.search(
                query=q_data["query"], ranking_method=config["method"], **config["params"])
            found_ids = [r.doc_id for r in res["results"]]

            rel_ids = [int(k) for k in q_data["relevant_map"].keys()]

            mrr_scores.append(IREvaluator.calculate_mrr(found_ids, rel_ids))
            ap_scores.append(IREvaluator.calculate_ap(found_ids, rel_ids))
            ndcg_scores.append(IREvaluator.calculate_ndcg(
                found_ids, q_data["relevant_map"], k=5))
            # Adăugăm P@5
            p5_scores.append(IREvaluator.calculate_precision_at_k(
                found_ids, rel_ids, k=5))

        results_table.append({
            "Metoda": config["name"],
            "MRR": np.mean(mrr_scores),
            "nDCG@5": np.mean(ndcg_scores),
            "P@5": np.mean(p5_scores)
        })

    # Afișare
    print(f"{'Metodă':<20} | {'MRR':<8} | {'nDCG@5':<8} | {'P@5':<8}")
    print("-" * 55)
    for r in results_table:
        print(
            f"{r['Metoda']:<20} | {r['MRR']:.3f}    | {r['nDCG@5']:.3f}    | {r['P@5']:.3f}")


if __name__ == "__main__":
    run_benchmark()
