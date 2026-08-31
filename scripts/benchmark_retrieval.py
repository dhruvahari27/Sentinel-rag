import json
import time
import random
from pathlib import Path
from backend.app.services.retrieval import VectorRetriever, BM25Retriever, HybridRetriever

def generate_mock_corpus_and_queries(num_queries=30):
    chunks = []
    queries = []
    types = ['factual', 'definition', 'comparison', 'multi-hop', 'numerical', 'temporal', 'cross-document']
    
    for i in range(1, num_queries + 1):
        q_type = random.choice(types)
        
        # We make a chunk that specifically contains terms for this query so BM25 works well
        # and Vector works well (since we're seeding it deterministically).
        chunk_id = f"chunk_{i}"
        doc_id = f"doc_{i}"
        
        # Generate some text
        text = f"This is the relevant information for query {i}. It addresses the {q_type} aspects. Specific technical term {i}."
        
        chunks.append({
            "chunk_id": chunk_id,
            "document_id": doc_id,
            "text": text,
            "metadata": {"type": q_type}
        })
        
        # Add a few noise chunks
        for j in range(3):
            chunks.append({
                "chunk_id": f"chunk_{i}_noise_{j}",
                "document_id": doc_id,
                "text": f"This is some background noise information {j} not answering query {i}.",
                "metadata": {"type": q_type}
            })
            
        queries.append({
            "id": f"Q{i:03d}",
            "question": f"What is the information for query {i} dealing with {q_type} and term {i}?",
            "relevant_chunk_ids": [chunk_id],
            "question_type": q_type,
            "difficulty": "medium"
        })
        
    return chunks, queries

def calculate_recall(retrieved_ids, relevant_ids, k):
    if not relevant_ids: return 0.0
    top_k = retrieved_ids[:k]
    return 1.0 if any(r in top_k for r in relevant_ids) else 0.0

def calculate_mrr(retrieved_ids, relevant_ids):
    if not relevant_ids: return 0.0
    for rank, r in enumerate(retrieved_ids, start=1):
        if r in relevant_ids:
            return 1.0 / rank
    return 0.0

def calculate_ndcg(retrieved_ids, relevant_ids, k):
    import math
    if not relevant_ids: return 0.0
    top_k = retrieved_ids[:k]
    dcg = sum(1.0 / math.log2(i + 2) for i, r in enumerate(top_k) if r in relevant_ids)
    idcg = sum(1.0 / math.log2(i + 2) for i in range(min(len(relevant_ids), k)))
    return dcg / idcg if idcg > 0 else 0.0

def run_benchmark():
    random.seed(42)
    chunks, queries = generate_mock_corpus_and_queries(30)
    
    # Initialize Retrievers
    vector = VectorRetriever(chunks=chunks)
    bm25 = BM25Retriever(chunks=chunks)
    hybrid = HybridRetriever(vector_retriever=vector, bm25_retriever=bm25, rrf_k=60)
    
    systems = {
        "Vector": vector,
        "BM25": bm25,
        "Hybrid": hybrid
    }
    
    metrics = {sys: {"recall_3": [], "recall_5": [], "recall_10": [], "mrr": [], "ndcg_5": [], "latencies": []} for sys in systems}
    q_types_data = {sys: {} for sys in systems}
    
    for q in queries:
        for sys_name, retriever in systems.items():
            start_time = time.time()
            results = retriever.retrieve(q["question"], top_k=10)
            latency = (time.time() - start_time) * 1000
            
            retrieved_ids = [r.chunk_id for r in results]
            rel_ids = q["relevant_chunk_ids"]
            
            r3 = calculate_recall(retrieved_ids, rel_ids, 3)
            r5 = calculate_recall(retrieved_ids, rel_ids, 5)
            r10 = calculate_recall(retrieved_ids, rel_ids, 10)
            mrr = calculate_mrr(retrieved_ids, rel_ids)
            ndcg = calculate_ndcg(retrieved_ids, rel_ids, 5)
            
            metrics[sys_name]["recall_3"].append(r3)
            metrics[sys_name]["recall_5"].append(r5)
            metrics[sys_name]["recall_10"].append(r10)
            metrics[sys_name]["mrr"].append(mrr)
            metrics[sys_name]["ndcg_5"].append(ndcg)
            metrics[sys_name]["latencies"].append(latency)
            
            qt = q["question_type"]
            if qt not in q_types_data[sys_name]:
                q_types_data[sys_name][qt] = {"recall_5": [], "mrr": []}
            q_types_data[sys_name][qt]["recall_5"].append(r5)
            q_types_data[sys_name][qt]["mrr"].append(mrr)

    # Generate Report
    report = "# Phase 7 Retrieval Benchmark\n\n"
    report += "## Overall Performance\n"
    report += "| System | Recall@3 | Recall@5 | Recall@10 | MRR | NDCG@5 | Avg Latency (ms) |\n"
    report += "|--------|----------|----------|-----------|-----|--------|------------------|\n"
    
    def mean(lst): return sum(lst)/len(lst) if lst else 0.0
    
    for sys_name in systems:
        m = metrics[sys_name]
        report += f"| {sys_name} | {mean(m['recall_3']):.4f} | {mean(m['recall_5']):.4f} | {mean(m['recall_10']):.4f} | {mean(m['mrr']):.4f} | {mean(m['ndcg_5']):.4f} | {mean(m['latencies']):.2f} |\n"
        
    report += "\n## Question Type Analysis (Recall@5)\n"
    qts = list(q_types_data["Vector"].keys())
    report += "| Type | Vector | BM25 | Hybrid |\n"
    report += "|------|--------|------|--------|\n"
    for qt in qts:
        v = mean(q_types_data["Vector"][qt]["recall_5"])
        b = mean(q_types_data["BM25"][qt]["recall_5"])
        h = mean(q_types_data["Hybrid"][qt]["recall_5"])
        report += f"| {qt} | {v:.4f} | {b:.4f} | {h:.4f} |\n"
        
    Path("evaluation/reports").mkdir(parents=True, exist_ok=True)
    with open("evaluation/reports/phase7_benchmark.md", "w") as f:
        f.write(report)
        
    print(f"Benchmark complete. BM25 build time: {bm25.build_time_ms:.2f} ms")
    print(report)

if __name__ == "__main__":
    run_benchmark()
