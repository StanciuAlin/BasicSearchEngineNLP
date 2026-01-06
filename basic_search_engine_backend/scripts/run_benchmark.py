import json
import argparse
import numpy as np
from search_engine.search.engine import SearchEngine
from search_engine.evaluation.evaluator import IREvaluator


def run_benchmark(dataset_size):
    engine = SearchEngine()
    engine.index_corpus("data/docs")

    # Select the file based on dataset type
    if dataset_size == "large":
        file_path = "data/eval_queries_large.json"
    else:
        file_path = "data/eval_queries.json"

    print(f"--- Load queries from {file_path} ---")

    with open(file_path, "r") as f:
        queries = json.load(f)

    # Configs for benchmarking
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

            # Compute IR metrics
            mrr_scores.append(IREvaluator.calculate_mrr(found_ids, rel_ids))
            ap_scores.append(IREvaluator.calculate_ap(found_ids, rel_ids))
            ndcg_scores.append(IREvaluator.calculate_ndcg(
                found_ids, q_data["relevant_map"], k=5))
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


def main():
    # Define termainl arguments
    parser = argparse.ArgumentParser(
        description="Runner for Benchmark on Search Engine")
    parser.add_argument(
        "--size",
        choices=["normal", "large"],
        default="normal",
        help="Choose between 'normal' and 'large' evaluation datasets."
    )

    args = parser.parse_args()

    # Sent the read value to the run_benchmark function
    run_benchmark(args.size)


if __name__ == "__main__":
    main()
