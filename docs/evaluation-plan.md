# Evaluation Plan

This document outlines how SENTINEL-RAG will be evaluated.

## Principles
- **No fabricated metrics:** All experimental results must come from actual experiments.
- **Reproducibility:** All query execution traces must be reproducible.

## Evaluation Dimensions (Planned)

1.  **Retrieval Quality:** Precision, Recall, NDCG (Normalized Discounted Cumulative Gain).
2.  **Generation Quality:** Faithfulness (to evidence), Answer Relevance, Helpfulness.
3.  **Orchestration Performance:**
    -   Latency (Time to first token, total generation time).
    -   Cost (Token usage, API calls).
    -   Abstention Rate (How often the system correctly refuses to answer when evidence is insufficient).
    -   Repair Rate (How often the system successfully repairs a flawed generation based on verification).

## Framework (Planned)
A Python-based evaluation framework will be built to run offline benchmarks against curated datasets.
