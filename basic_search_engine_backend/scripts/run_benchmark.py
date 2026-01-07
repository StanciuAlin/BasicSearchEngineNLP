import json
import argparse
import numpy as np
from search_engine.search.engine import SearchEngine
from search_engine.evaluation.evaluator import IREvaluator

"""
Module: benchmark.py
Description: A standardized benchmarking suite used to evaluate and compare the 
performance of different retrieval models (TF-IDF, BM25, Jaccard). It measures 
ranking quality using statistical metrics over a predefined set of evaluation queries.
"""


def run_benchmark(dataset_size):
    """
    Executes a performance audit of the search engine across various configurations.

    This function automates the evaluation process by:
    1. Loading a "ground truth" dataset containing queries and their relevant documents.
    2. Iterating through different ranking algorithms and hyperparameter sets.
    3. Calculating Mean Reciprocal Rank (MRR), nDCG, and Precision@K for each config.
    4. Aggregating results to determine the most effective retrieval strategy.

    Args:
        dataset_size (str): Specifies the evaluation scale ('normal' or 'large').
    """

    engine = SearchEngine()
    # Ensure the corpus is indexed before starting the benchmark
    engine.index_corpus("data/docs")

    # Select the evaluation ground truth based on the requested dataset scale
    if dataset_size == "large":
        file_path = "data/eval_queries_large.json"
    else:
        file_path = "data/eval_queries.json"

    print(f"--- Load queries from {file_path} ---")

    with open(file_path, "r") as f:
        queries = json.load(f)

    # Experimental configurations for comparative analysis
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
            # Execute search using the current experimental configuration
            res = engine.search(
                query=q_data["query"], ranking_method=config["method"], **config["params"])

            # Extract document IDs from the result set for metric calculation
            found_ids = [r.doc_id for r in res["results"]]

            # Ground truth: List of IDs manually labeled as relevant for this query
            rel_ids = [int(k) for k in q_data["relevant_map"].keys()]

            # Compute core IR performance metrics
            mrr_scores.append(IREvaluator.calculate_mrr(found_ids, rel_ids))
            ap_scores.append(IREvaluator.calculate_ap(found_ids, rel_ids))
            ndcg_scores.append(IREvaluator.calculate_ndcg(
                found_ids, q_data["relevant_map"], k=5))
            p5_scores.append(IREvaluator.calculate_precision_at_k(
                found_ids, rel_ids, k=5))

        # Aggregate individual query scores using the arithmetic mean
        results_table.append({
            "Metoda": config["name"],
            "MRR": np.mean(mrr_scores),
            "nDCG@5": np.mean(ndcg_scores),
            "P@5": np.mean(p5_scores)
        })

    # Tabular display of the benchmark results
    print(f"{'Method':<20} | {'MRR':<8} | {'nDCG@5':<8} | {'P@5':<8}")
    print("-" * 55)
    for r in results_table:
        print(
            f"{r['Method']:<20} | {r['MRR']:.3f}    | {r['nDCG@5']:.3f}    | {r['P@5']:.3f}")


def main():
    """
    Entry point for the benchmarking CLI.

    Provides a command-line interface to toggle between different evaluation 
    datasets, facilitating rapid testing of the engine's scalability.
    """

    parser = argparse.ArgumentParser(
        description="Runner for Benchmark on Search Engine")
    parser.add_argument(
        "--size",
        choices=["normal", "large"],
        default="normal",
        help="Choose between 'normal' and 'large' evaluation datasets."
    )

    args = parser.parse_args()

    # Initiate the benchmarking sequence
    run_benchmark(args.size)


if __name__ == "__main__":
    main()
