# Phase 7 Retrieval Benchmark

## Overall Performance
| System | Recall@3 | Recall@5 | Recall@10 | MRR | NDCG@5 | Avg Latency (ms) |
|--------|----------|----------|-----------|-----|--------|------------------|
| Vector | 0.0333 | 0.0333 | 0.0333 | 0.0167 | 0.0210 | 20.47 |
| BM25 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.62 |
| Hybrid | 0.2333 | 0.3333 | 1.0000 | 0.2553 | 0.1974 | 21.66 |

## Question Type Analysis (Recall@5)
| Type | Vector | BM25 | Hybrid |
|------|--------|------|--------|
| temporal | 0.0000 | 1.0000 | 0.3750 |
| factual | 0.0000 | 1.0000 | 0.1250 |
| comparison | 0.0000 | 1.0000 | 0.0000 |
| definition | 0.1667 | 1.0000 | 0.6667 |
| numerical | 0.0000 | 1.0000 | 0.3333 |
| multi-hop | 0.0000 | 1.0000 | 0.0000 |
