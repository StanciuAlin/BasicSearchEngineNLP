import numpy as np


class IREvaluator:
    @staticmethod
    def calculate_mrr(results_ids, relevant_ids):
        """Mean Reciprocal Rank: Cât de sus e primul rezultat relevant."""
        for i, doc_id in enumerate(results_ids):
            if doc_id in relevant_ids:
                return 1 / (i + 1)
        return 0

    @staticmethod
    def calculate_ap(results_ids, relevant_ids):
        """Average Precision: Calitatea întregii liste de rezultate."""
        hits = 0
        sum_precisions = 0
        for i, doc_id in enumerate(results_ids):
            if doc_id in relevant_ids:
                hits += 1
                sum_precisions += hits / (i + 1)
        return sum_precisions / len(relevant_ids) if relevant_ids else 0

    @staticmethod
    def calculate_dcg(results_ids, relevant_scores_map, k=10):
        """Discounted Cumulative Gain la poziția k."""
        score = 0.0
        for i, doc_id in enumerate(results_ids[:k]):
            # Extragem gradul de relevanță (implicit 0 dacă nu e în listă)
            rel = relevant_scores_map.get(str(doc_id), 0)
            # Formula: rel_i / log2(i + 2)
            score += rel / np.log2(i + 2)
        return score

    @staticmethod
    def calculate_ndcg(results_ids, relevant_scores_map, k=10):
        """Normalized DCG la poziția k."""
        actual_dcg = IREvaluator.calculate_dcg(
            results_ids, relevant_scores_map, k)

        # Calculăm Ideal DCG (cele mai relevante documente puse primele)
        sorted_relevances = sorted(relevant_scores_map.values(), reverse=True)
        ideal_dcg = 0.0
        for i, rel in enumerate(sorted_relevances[:k]):
            ideal_dcg += rel / np.log2(i + 2)

        return actual_dcg / ideal_dcg if ideal_dcg > 0 else 0.0

    @staticmethod
    def calculate_precision_at_k(results_ids, relevant_ids, k=5):
        """Calculează Precision@K: (Documente relevante găsite în top K) / K"""
        if not results_ids:
            return 0.0

        top_k_results = results_ids[:k]
        hits = len(set(top_k_results) & set(relevant_ids))

        return hits / k
