import json
import time
import math
from pathlib import Path
from typing import List, Dict, Any
from app.schemas.retrieval import QueryRequest, RetrievalChunk
from app.services.retrieval.pipeline import RetrievalPipeline
from app.services.retrieval.reranker import CrossEncoderReranker
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))
from tests.test_reranker import MockReranker

QUERIES = [
    {"question": "What is hybrid retrieval?", "relevant_docs": ["doc_1", "doc_2"], "type": "factual"},
    {"question": "Compare vector and BM25", "relevant_docs": ["doc_0"], "type": "comparison"},
    {"question": "How to deploy?", "relevant_docs": ["doc_3", "doc_4"], "type": "multi-hop"},
    {"question": "Latency numbers?", "relevant_docs": ["doc_2"], "type": "numerical"}
]

def get_metrics(results: List[RetrievalChunk], relevant_docs: List[str]) -> Dict[str, Any]:
    docs_order = [res.document_id for res in results]
    
    def recall_at(k):
        top = docs_order[:k]
        hits = sum(1 for d in top if d in relevant_docs)
        return hits / len(relevant_docs) if relevant_docs else 0.0

    def ndcg_at(k):
        dcg = sum(1.0 / math.log2(idx + 1) for idx, doc in enumerate(docs_order[:k], 1) if doc in relevant_docs)
        idcg = sum(1.0 / math.log2(idx + 1) for idx in range(1, min(len(relevant_docs), k) + 1))
        return dcg / idcg if idcg > 0 else 0.0

    mrr = 0.0
    for idx, doc in enumerate(docs_order, 1):
        if doc in relevant_docs:
            mrr = 1.0 / idx
            break

    return {
        "recall_3": recall_at(3),
        "recall_5": recall_at(5),
        "recall_10": recall_at(10),
        "mrr": mrr,
        "ndcg_5": ndcg_at(5)
    }

def run_benchmark():
    output_dir = Path("evaluation/results/reranking")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    pipeline = RetrievalPipeline(reranker=MockReranker())

    results = []
    hybrid_lats = []
    rerank_lats = []
    
    for q in QUERIES:
        req_hybrid = QueryRequest(question=q["question"], rerank=False, top_k=10)
        start = time.time()
        resp_hybrid = pipeline.execute(req_hybrid)
        t_hybrid = time.time() - start
        hybrid_lats.append(t_hybrid)
        m_hybrid = get_metrics(resp_hybrid.results, q["relevant_docs"])
        
        req_rerank = QueryRequest(question=q["question"], rerank=True, candidate_k=20, top_k=10)
        start = time.time()
        resp_rerank = pipeline.execute(req_rerank)
        t_rerank = time.time() - start
        rerank_lats.append(t_rerank)
        m_rerank = get_metrics(resp_rerank.results, q["relevant_docs"])
        
        results.append({
            "question": q["question"],
            "type": q["type"],
            "hybrid": m_hybrid,
            "rerank": m_rerank
        })
        
    def avg(lst): return sum(lst) / len(lst) if lst else 0.0
    def p50(lst): return sorted(lst)[len(lst)//2] if lst else 0.0
    def p95(lst): return sorted(lst)[int(len(lst)*0.95)] if lst else 0.0

    r = {
        "hybrid": {
            "recall_3": avg([x["hybrid"]["recall_3"] for x in results]),
            "recall_5": avg([x["hybrid"]["recall_5"] for x in results]),
            "recall_10": avg([x["hybrid"]["recall_10"] for x in results]),
            "mrr": avg([x["hybrid"]["mrr"] for x in results]),
            "ndcg_5": avg([x["hybrid"]["ndcg_5"] for x in results]),
            "avg_lat": avg(hybrid_lats),
            "p50_lat": p50(hybrid_lats),
            "p95_lat": p95(hybrid_lats)
        },
        "rerank": {
            "recall_3": avg([x["rerank"]["recall_3"] for x in results]),
            "recall_5": avg([x["rerank"]["recall_5"] for x in results]),
            "recall_10": avg([x["rerank"]["recall_10"] for x in results]),
            "mrr": avg([x["rerank"]["mrr"] for x in results]),
            "ndcg_5": avg([x["rerank"]["ndcg_5"] for x in results]),
            "avg_lat": avg(rerank_lats),
            "p50_lat": p50(rerank_lats),
            "p95_lat": p95(rerank_lats)
        }
    }

    report = f"""# Reranking Benchmark Report
| Metric | Hybrid | Hybrid + Reranker |
|--------|--------|-------------------|
| Recall@3 | {r['hybrid']['recall_3']:.3f} | {r['rerank']['recall_3']:.3f} |
| Recall@5 | {r['hybrid']['recall_5']:.3f} | {r['rerank']['recall_5']:.3f} |
| Recall@10 | {r['hybrid']['recall_10']:.3f} | {r['rerank']['recall_10']:.3f} |
| MRR | {r['hybrid']['mrr']:.3f} | {r['rerank']['mrr']:.3f} |
| NDCG@5 | {r['hybrid']['ndcg_5']:.3f} | {r['rerank']['ndcg_5']:.3f} |
| Avg Latency | {r['hybrid']['avg_lat']:.4f} | {r['rerank']['avg_lat']:.4f} |
| P50 Latency | {r['hybrid']['p50_lat']:.4f} | {r['rerank']['p50_lat']:.4f} |
| P95 Latency | {r['hybrid']['p95_lat']:.4f} | {r['rerank']['p95_lat']:.4f} |
"""
    print(report)

if __name__ == "__main__":
    run_benchmark()
