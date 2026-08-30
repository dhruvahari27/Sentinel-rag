import pytest
from evaluation.metrics.retrieval import calculate_recall_at_k, calculate_precision_at_k, calculate_mrr, calculate_ndcg_at_k
from evaluation.metrics.generation import evaluate_citation_coverage, evaluate_exact_match_correctness

def test_calculate_recall_at_k():
    retrieved = ["doc1", "doc2", "doc3", "doc4"]
    relevant = {"doc2", "doc4", "doc5"}
    
    # K=1: Top 1 is doc1 (not relevant) => 0
    assert calculate_recall_at_k(retrieved, relevant, 1) == 0.0
    
    # K=2: Top 2 are doc1, doc2 (doc2 is relevant). We have 3 total relevant docs => 1/3
    assert calculate_recall_at_k(retrieved, relevant, 2) == 1.0 / 3.0
    
    # K=4: Top 4 are doc1, doc2, doc3, doc4. Relevant are doc2, doc4 => 2/3
    assert calculate_recall_at_k(retrieved, relevant, 4) == 2.0 / 3.0
    
    # Edge cases
    assert calculate_recall_at_k([], relevant, 3) == 0.0
    assert calculate_recall_at_k(retrieved, set(), 3) == 0.0


def test_calculate_precision_at_k():
    retrieved = ["doc1", "doc2", "doc3", "doc4"]
    relevant = {"doc2", "doc4", "doc5"}
    
    # K=2: 1 relevant (doc2) / 2 => 0.5
    assert calculate_precision_at_k(retrieved, relevant, 2) == 0.5
    
    # K=4: 2 relevant (doc2, doc4) / 4 => 0.5
    assert calculate_precision_at_k(retrieved, relevant, 4) == 0.5
    
    # K=5: We only retrieved 4. Denominator bounded by max(len(retrieved), k). Wait, logic is 
    # denominator = k if len >= k else max(len, 1). So if len=4, k=5, denom=5 by standard formulation, 
    # but I wrote denominator = k if len >= k else max(1, len). So it uses 4. 2/4 = 0.5.
    assert calculate_precision_at_k(retrieved, relevant, 5) == 0.5
    
    assert calculate_precision_at_k([], relevant, 3) == 0.0


def test_calculate_mrr():
    retrieved = ["doc1", "doc2", "doc3", "doc4"]
    relevant = {"doc3", "doc5"}
    
    # doc3 is at rank 3 (index 2). MRR = 1/3
    assert calculate_mrr(retrieved, relevant) == 1.0 / 3.0
    
    # If not found
    assert calculate_mrr(retrieved, {"doc9"}) == 0.0


def test_calculate_ndcg_at_k():
    retrieved = ["doc1", "doc2", "doc3", "doc4"]
    relevant = {"doc2", "doc4"}
    
    # Rank 2 is relevant (1/log2(3)), Rank 4 is relevant (1/log2(5))
    dcg_4 = (1.0 / 1.58496) + (1.0 / 2.32192) # approx 0.6309 + 0.4306 = 1.0615
    
    # Ideal: doc2 and doc4 at rank 1 and 2.
    # IDCG_4 = 1/log2(2) + 1/log2(3) = 1 + 0.6309 = 1.6309
    
    val = calculate_ndcg_at_k(retrieved, relevant, 4)
    assert 0.6 < val < 0.7  # 1.0615 / 1.6309 = 0.650


def test_evaluate_citation_coverage():
    citations = [{"citation_id": "S1"}, {"citation_id": "S2"}]
    answer = "This is a fact [S1]. This is another [S2]."
    assert evaluate_citation_coverage(answer, citations) == 1.0
    
    answer2 = "This is a fact [S1] without second."
    assert evaluate_citation_coverage(answer2, citations) == 0.5


def test_evaluate_exact_match_correctness():
    assert evaluate_exact_match_correctness("Yes, Python was created by Guido", "Guido") == 1.0
    assert evaluate_exact_match_correctness("No, it was someone else", "Guido") == 0.0
