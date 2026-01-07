import numpy as np

"""
Module: evaluator.py
Description: Provides a comprehensive suite of metrics for evaluating the 
effectiveness of Information Retrieval models. It supports rank-based metrics 
(MRR, Precision@K) and gain-based metrics (NDCG) to benchmark search quality.
"""


class IREvaluator:
    """
    A utility class for Information Retrieval evaluation.

    This class implements industry-standard algorithms to quantify how well 
    the search engine's ranking matches a "ground truth" (a set of manually 
    verified relevant documents).
    """

    @staticmethod
    def calculate_mrr(results_ids, relevant_ids):
        """
        Calculates the Mean Reciprocal Rank (MRR).

        MRR measures how deep the user has to look into the result list to 
        find the FIRST relevant document. It is the reciprocal of the rank 
        of the first correct answer.

        Args:
            results_ids (list): List of document IDs returned by the search engine.
            relevant_ids (list): Set/list of document IDs known to be relevant.

        Returns:
            float: Reciprocal rank score between 0 and 1.
        """

        for i, doc_id in enumerate(results_ids):
            if doc_id in relevant_ids:
                return 1 / (i + 1)
        return 0

    @staticmethod
    def calculate_ap(results_ids, relevant_ids):
        """
        Calculates Average Precision (AP).

        AP evaluates the quality of the entire ranked list by averaging the 
        precision scores at each point where a relevant document is retrieved.

        Args:
            results_ids (list): Ordered document IDs from the engine.
            relevant_ids (list): Ground truth relevant document IDs.

        Returns:
            float: The area under the Precision-Recall curve.
        """

        hits = 0
        sum_precisions = 0
        for i, doc_id in enumerate(results_ids):
            if doc_id in relevant_ids:
                hits += 1
                sum_precisions += hits / (i + 1)
        return sum_precisions / len(relevant_ids) if relevant_ids else 0

    @staticmethod
    def calculate_dcg(results_ids, relevant_scores_map, k=10):
        """
        Calculates Discounted Cumulative Gain (DCG) at position K.

        DCG accounts for the degree of relevance (graded relevance) and 
        penalizes relevant documents appearing lower in the list using a 
        logarithmic decay.

        Formula: Sum of (Rel_i / log2(i + 1))

        Args:
            results_ids (list): Result list of IDs.
            relevant_scores_map (dict): Mapping of {doc_id: relevance_grade}.
            k (int): Cut-off rank.

        Returns:
            float: Cumulative gain score.
        """

        score = 0.0
        for i, doc_id in enumerate(results_ids[:k]):
            # Extract relevance grade (default to 0 if not explicitly labeled)
            rel = relevant_scores_map.get(str(doc_id), 0)
            # Logarithmic discount based on position
            score += rel / np.log2(i + 2)
        return score

    @staticmethod
    def calculate_ndcg(results_ids, relevant_scores_map, k=10):
        """
        Calculates Normalized Discounted Cumulative Gain (NDCG) at position K.

        NDCG normalizes the DCG score against an "Ideal DCG" (the best possible 
        ranking for that query), allowing for cross-query performance comparisons.

        Returns:
            float: Score between 0 and 1, where 1 is a perfect ranking.
        """

        actual_dcg = IREvaluator.calculate_dcg(
            results_ids, relevant_scores_map, k)

        # Calculate Ideal DCG (IDCG) by sorting relevant documents by grade
        sorted_relevances = sorted(relevant_scores_map.values(), reverse=True)
        ideal_dcg = 0.0
        for i, rel in enumerate(sorted_relevances[:k]):
            ideal_dcg += rel / np.log2(i + 2)

        return actual_dcg / ideal_dcg if ideal_dcg > 0 else 0.0

    @staticmethod
    def calculate_precision_at_k(results_ids, relevant_ids, k=5):
        """
        Calculates Precision@K.

        Measures the proportion of documents in the top K results that are 
        actually relevant to the user's query.

        Args:
            results_ids (list): List of retrieved IDs.
            relevant_ids (list): List of relevant IDs.
            k (int): Number of top results to inspect.

        Returns:
            float: Proportion (e.g., 0.8 if 4 out of 5 are relevant).
        """

        if not results_ids:
            return 0.0

        top_k_results = results_ids[:k]
        hits = len(set(top_k_results) & set(relevant_ids))

        return hits / k
