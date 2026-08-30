# Evaluation Plan

SENTINEL-RAG is an evaluation-driven project. Every architectural change and policy rule will be measured against a rigorous benchmark. No metrics will be fabricated; all results must be derived from actual experimental runs.

## 1. Dataset construction
We will construct a custom evaluation dataset of 60–100 labelled questions based on the ingested document corpus. The dataset must cover diverse complexities to test the adaptive retrieval system adequately.

## 2. Question categories
The dataset will explicitly include:
*   **Factual**: Simple entity/fact retrieval.
*   **Definition**: Concept explanation.
*   **Comparison**: Contrasting entities across documents.
*   **Multi-hop**: Requiring traversal across multiple distinct chunks/documents.
*   **Numerical**: Aggregations or specific numerical thresholds.
*   **Temporal**: Version-aware questions (e.g., "What was the policy before 2023?").
*   **Cross-document**: Synthesizing information from completely different sources.
*   **Unanswerable**: Queries with no evidence in the corpus (tests Abstention).
*   **Adversarial**: Misleading premises.
*   **Prompt-injection**: Attempts to override system instructions via documents.

## 3. Ground truth format
Each benchmark entry will contain:
*   `query_id`
*   `query`
*   `category`
*   `expected_answer` (for automated LLM-as-a-judge grading)
*   `golden_chunks` (list of chunk IDs required to answer fully)
*   `is_answerable` (boolean)

## 4. Retrieval evaluation
Evaluated independently from generation. Metrics:
*   **Recall@3, Recall@5, Recall@10**: Did we find the golden chunks?
*   **Precision@K**: How much noise is in the top K?
*   **MRR (Mean Reciprocal Rank)**: How high is the first relevant chunk?
*   **NDCG (Normalized Discounted Cumulative Gain)**: Overall ranking quality.

## 5. Generation evaluation
Metrics focused on the final output:
*   **Answer Correctness**: Semantic similarity/accuracy against the expected answer.
*   **Faithfulness**: Is the answer derived *only* from retrieved context?
*   **Answer Relevance**: Does the answer actually address the user's query?

## 6. Citation evaluation
*   **Citation Coverage**: Are all claims backed by citations?
*   **Citation Precision**: Do the cited chunks actually contain the claimed information?
*   **Unsupported Claim Rate**: Percentage of claims classified as `UNSUPPORTED` during verification.

## 7. Conflict evaluation
*   **Contradiction Rate**: How often the system outputs conflicting claims.
*   Success rate of the Orchestrator resolving known injected contradictions in the dataset.

## 8. Abstention evaluation
*   **Refusal Accuracy**: True positive rate on unanswerable queries (correctly abstaining) vs. False positive rate (abstaining when evidence actually exists).

## 9. Calibration evaluation
*   **Expected Calibration Error (ECE)**: If the system assigns a confidence score to its answer, how well does that score correlate with actual correctness?
*   **Brier Score**: Accuracy of probabilistic predictions.
*   **Risk-Coverage Analysis**: Trade-off between abstaining and answering correctly.

## 10. Cost evaluation
*   **Average Token Usage**: Broken down by prompt/completion and module (retrieval vs. verification).
*   **Cost per Query**: Calculated using exact API pricing.
*   **Evidence Efficiency**: Ratio of useful tokens to total retrieved context tokens.

## 11. Latency evaluation
*   **Latency**: End-to-end response time.
*   **P50 Latency**: Median response time.
*   **P95 Latency**: Tail latency (crucial for evaluating adaptive retrieval loops).
*   **Cache Hit Rate**: Impact of Redis caching on overall latency.

## 12. Ablation studies
We will compare SENTINEL-RAG against several baselines to isolate the value of each component:
*   **B0**: LLM without retrieval
*   **B1**: Simple vector RAG
*   **B2**: Vector + reranker
*   **B3**: Hybrid vector + BM25
*   **B4**: Hybrid + reranker
*   **B5**: Adaptive retrieval (early Orchestrator)
*   **B6**: Adaptive + verification
*   **B7**: Adaptive + verification + conflict awareness
*   **Final**: Full SENTINEL-RAG pipeline

## 13. Failure analysis
Failed queries will be categorized manually:
*   Retrieval Failure (golden chunks not found)
*   Reranking Failure (golden chunks found but ranked too low)
*   Generation Failure (evidence present, but LLM hallucinated/failed)
*   Verification Failure (strict verification blocked a correct answer)

## 14. Statistical reporting
All final metrics will be reported with statistical significance where applicable, averaged over multiple runs if LLM temperatures > 0 are used. (Though temperature 0 is preferred for reproducibility).

## 15. Reproducibility
The benchmark dataset, evaluation scripts, and exact model versions will be version-controlled to ensure that any developer can reproduce the exact trace and metrics of the baseline and final runs.
