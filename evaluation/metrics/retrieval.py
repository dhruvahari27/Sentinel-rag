import math
from typing import List, Set

def calculate_recall_at_k(retrieved_ids: List[str], relevant_ids: Set[str], k: int) -> float:
    """
    Calculates Recall@K.
    Recall = (number of relevant items retrieved in top K) / (total number of relevant items)
    """
    if not relevant_ids:
        return 0.0
    
    top_k_retrieved = retrieved_ids[:k]
    relevant_retrieved = set(top_k_retrieved).intersection(relevant_ids)
    
    return len(relevant_retrieved) / len(relevant_ids)


def calculate_precision_at_k(retrieved_ids: List[str], relevant_ids: Set[str], k: int) -> float:
    """
    Calculates Precision@K.
    Precision = (number of relevant items retrieved in top K) / (K)
    Note: If fewer than K items are retrieved, the denominator is still K for standard Precision@K,
    but it's often bounded by len(retrieved_ids). We bound it by min(K, len(retrieved_ids)) or K.
    Let's bound it by K to penalize models that don't return enough results, but if K=0, return 0.
    """
    if not relevant_ids or k == 0:
        return 0.0
        
    top_k_retrieved = retrieved_ids[:k]
    relevant_retrieved = set(top_k_retrieved).intersection(relevant_ids)
    
    # We use min(K, max(1, len(top_k_retrieved))) to be fair if the system simply returns fewer
    # but the strict definition uses exactly K.
    denominator = k if len(top_k_retrieved) >= k else (len(top_k_retrieved) or 1)
    
    return len(relevant_retrieved) / denominator


def calculate_mrr(retrieved_ids: List[str], relevant_ids: Set[str]) -> float:
    """
    Calculates Mean Reciprocal Rank (MRR) for a single query.
    MRR = 1 / rank of the FIRST relevant item retrieved.
    """
    if not relevant_ids:
        return 0.0
        
    for i, item_id in enumerate(retrieved_ids):
        if item_id in relevant_ids:
            return 1.0 / (i + 1)
            
    return 0.0


def calculate_ndcg_at_k(retrieved_ids: List[str], relevant_ids: Set[str], k: int) -> float:
    """
    Calculates Normalized Discounted Cumulative Gain (NDCG) at K.
    For this binary relevance case: rel_i = 1 if retrieved_ids[i] in relevant_ids else 0.
    """
    if not relevant_ids or k == 0:
        return 0.0
        
    top_k_retrieved = retrieved_ids[:k]
    
    dcg = 0.0
    for i, item_id in enumerate(top_k_retrieved):
        if item_id in relevant_ids:
            # relevance is 1
            dcg += 1.0 / math.log2(i + 2) # rank is i+1, so log2(rank+1) = log2(i+2)
            
    # Calculate IDCG (Ideal DCG)
    idcg = 0.0
    num_relevant = min(k, len(relevant_ids))
    for i in range(num_relevant):
        idcg += 1.0 / math.log2(i + 2)
        
    if idcg == 0.0:
        return 0.0
        
    return dcg / idcg
