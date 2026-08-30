# Benchmark Report: baseline_vector_v1_2026_08_30_232929

## 1. Dataset
- **Name**: rag_eval_v1
- **Version**: v1.0
- **Size**: 30 questions

## 2. Configuration
- **Retriever**: vector
- **Embedding Model**: mock-embeddings-1536
- **Chunking Strategy**: simple_text_50_10

## 3. Retrieval Metrics
- **Overall MRR**: 0.2956
- **Overall Recall@3**: 0.2333
- **Overall Precision@3**: 0.0778
- **Overall Recall@5**: 0.4333
- **Overall Precision@5**: 0.0867
- **Overall Recall@10**: 0.6333
- **Overall Precision@10**: 0.0633

## 4. Generation Metrics
- **Overall citation_coverage**: 0.0000
- **Overall exact_correctness**: 0.0333

## 5. Latency
- **Average latency**: 0.0040 sec
- **P50 latency**: 0.0040 sec
- **P95 latency**: 0.0045 sec

## 6. Token Usage
- **Average input tokens**: NOT_AVAILABLE
- **Average output tokens**: NOT_AVAILABLE

## 7. Cost
- NOT_MEASURED

## 8. Failure Analysis
*Failure analysis categorization not yet fully implemented.*

## 9. Per-category performance

### factual (Count: 21)
- **MRR**: 0.2593
- **Recall@3**: 0.1905
- **Precision@3**: 0.0635
- **Recall@5**: 0.4286
- **Precision@5**: 0.0857
- **Recall@10**: 0.6190
- **Precision@10**: 0.0619

### definition (Count: 6)
- **MRR**: 0.0704
- **Recall@3**: 0.0000
- **Precision@3**: 0.0000
- **Recall@5**: 0.1667
- **Precision@5**: 0.0333
- **Recall@10**: 0.5000
- **Precision@10**: 0.0500

## 10. Limitations
- Mock embeddings currently yield random ordering since all chunks output parallel vectors.
- Token counting uses basic heuristics without a live LLM tokenizer.
