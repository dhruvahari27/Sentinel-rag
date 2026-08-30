from typing import List, Dict, Any, Optional
from app.schemas.retrieval import RetrievalChunk
from app.services.retrieval.base import BaseRetriever
from app.services.retrieval.vector import VectorRetriever
from app.services.retrieval.bm25 import BM25Retriever

class HybridRetriever(BaseRetriever):
    def __init__(self):
        self.vector_retriever = VectorRetriever()
        self.bm25_retriever = BM25Retriever()
        self.k = 60 # RRF constant

    def retrieve(
        self, 
        query: str, 
        top_k: int = 20, 
        filters: Optional[Dict[str, Any]] = None
    ) -> List[RetrievalChunk]:
        vector_results = self.vector_retriever.retrieve(query, top_k=top_k, filters=filters)
        bm25_results = self.bm25_retriever.retrieve(query, top_k=top_k, filters=filters)
        
        chunk_map: Dict[str, RetrievalChunk] = {}
        
        # RRF for Vector
        for rank, chunk in enumerate(vector_results, 1):
            if chunk.chunk_id not in chunk_map:
                chunk_map[chunk.chunk_id] = chunk
            else:
                chunk_map[chunk.chunk_id].vector_score = chunk.vector_score
            chunk_map[chunk.chunk_id].rrf_score = chunk_map[chunk.chunk_id].rrf_score or 0.0
            chunk_map[chunk.chunk_id].rrf_score += 1.0 / (self.k + rank)

        # RRF for BM25
        for rank, chunk in enumerate(bm25_results, 1):
            if chunk.chunk_id not in chunk_map:
                chunk_map[chunk.chunk_id] = chunk
            else:
                chunk_map[chunk.chunk_id].bm25_score = chunk.bm25_score
            chunk_map[chunk.chunk_id].rrf_score = chunk_map[chunk.chunk_id].rrf_score or 0.0
            chunk_map[chunk.chunk_id].rrf_score += 1.0 / (self.k + rank)
            
        # Sort by RRF score descending
        fused = sorted(chunk_map.values(), key=lambda x: x.rrf_score or 0.0, reverse=True)
        
        # Assign final rank and retrieval_method
        final_results = []
        for i, chunk in enumerate(fused[:top_k], 1):
            chunk.original_rank = i
            chunk.final_rank = i
            if chunk.vector_score is not None and chunk.bm25_score is not None:
                chunk.retrieval_method = "hybrid"
            elif chunk.vector_score is not None:
                chunk.retrieval_method = "vector"
            else:
                chunk.retrieval_method = "bm25"
            final_results.append(chunk)
            
        return final_results
