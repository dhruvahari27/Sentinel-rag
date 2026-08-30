import logging
from typing import List, Optional, Dict, Any

from app.schemas.retrieval import QueryRequest, QueryResponse, RetrievalMetadata, RerankingMetadata
from app.services.retrieval.base import BaseRetriever
from app.services.retrieval.vector import VectorRetriever
from app.services.retrieval.bm25 import BM25Retriever
from app.services.retrieval.hybrid import HybridRetriever
from app.services.retrieval.reranker import CrossEncoderReranker

logger = logging.getLogger(__name__)

class RetrievalPipeline:
    def __init__(
        self,
        vector_retriever: Optional[BaseRetriever] = None,
        bm25_retriever: Optional[BaseRetriever] = None,
        hybrid_retriever: Optional[BaseRetriever] = None,
        reranker: Optional[CrossEncoderReranker] = None,
        fallback_policy: str = "fallback"  # "strict" or "fallback"
    ):
        self.vector_retriever = vector_retriever or VectorRetriever()
        self.bm25_retriever = bm25_retriever or BM25Retriever()
        self.hybrid_retriever = hybrid_retriever or HybridRetriever()
        self.reranker = reranker
        self.fallback_policy = fallback_policy

    def _get_retriever(self, method: str) -> BaseRetriever:
        if method == "vector":
            return self.vector_retriever
        elif method == "bm25":
            return self.bm25_retriever
        elif method == "hybrid":
            return self.hybrid_retriever
        else:
            raise ValueError(f"Unknown retrieval method: {method}")

    def execute(self, request: QueryRequest) -> QueryResponse:
        retriever = self._get_retriever(request.retrieval_method)
        
        # Determine candidate count
        candidate_count = request.candidate_k if request.rerank else request.top_k
        
        # 1. Base Retrieval
        candidates = retriever.retrieve(
            query=request.question, 
            top_k=candidate_count, 
            filters=request.filters
        )
        
        applied_reranking = False
        reranker_model = self.reranker.model_name if self.reranker else "none"

        # 2. Reranking Stage
        if request.rerank and self.reranker:
            try:
                candidates = self.reranker.rerank(request.question, candidates)
                applied_reranking = True
            except Exception as e:
                logger.error(f"Reranking failed: {e}")
                if self.fallback_policy == "strict":
                    raise RuntimeError(f"Reranking failed and policy is strict: {e}")
                else:
                    logger.warning("Falling back to original retrieval ranking.")
        
        # 3. Truncate to Final Top-K
        final_results = candidates[:request.top_k]
        
        # 4. Final Final Rank Re-adjustment (just in case)
        for idx, chunk in enumerate(final_results, 1):
            chunk.final_rank = idx

        return QueryResponse(
            question=request.question,
            results=final_results,
            retrieval=RetrievalMetadata(
                method=request.retrieval_method,
                candidate_count=len(candidates) if not applied_reranking else candidate_count,
                final_k=len(final_results)
            ),
            reranking=RerankingMetadata(
                enabled=request.rerank,
                model=reranker_model,
                applied=applied_reranking
            )
        )
