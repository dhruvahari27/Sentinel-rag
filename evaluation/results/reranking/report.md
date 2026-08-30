# Reranking Benchmark Report

## Overall Metrics
| System | Recall@5 | MRR | Latency (s) |
|--------|----------|-----|-------------|
| Hybrid | 1.000 | 0.688 | 0.0005 |
| Hybrid + Reranker | 1.000 | 0.688 | 0.0007 |

*Note: Results were generated using a stubbed retrieval corpus and a deterministic mock reranker to fulfill Phase 8 architecture evaluation requirements without downloading large models during CI.*
