<<<<<<< Updated upstream
from typing import List, Dict
from sqlalchemy.orm import Session
from app.schemas.retrieval import RetrievalChunk
from app.services.retrieval.base import BaseRetriever
from app.services.retrieval.vector import VectorRetriever
from app.services.retrieval.bm25 import BM25Retriever
from app.services.embeddings.provider import BaseEmbeddingProvider

class HybridRetriever(BaseRetriever):
    def __init__(self, db: Session, embedding_provider: BaseEmbeddingProvider, rrf_k: int = 60):
        self.vector_retriever = VectorRetriever(db, embedding_provider)
        self.bm25_retriever = BM25Retriever(db)
        self.rrf_k = rrf_k

    def retrieve(self, query: str, top_k: int = 5) -> List[RetrievalChunk]:
        # We fetch more results individually to allow better fusion overlaps
        fetch_k = max(top_k * 2, 20)
        
        vector_results = self.vector_retriever.retrieve(query, top_k=fetch_k)
        bm25_results = self.bm25_retriever.retrieve(query, top_k=fetch_k)
        
        return self._rrf_fuse(vector_results, bm25_results, top_k)

    def _rrf_fuse(
        self, 
        vector_results: List[RetrievalChunk], 
        bm25_results: List[RetrievalChunk],
        top_k: int
    ) -> List[RetrievalChunk]:
        
        chunk_map: Dict[str, RetrievalChunk] = {}
        rrf_scores: Dict[str, float] = {}
        
        # Add vector scores
        for chunk in vector_results:
            chunk_map[chunk.id] = chunk
            # chunk.rank is 1-indexed
            rrf_scores[chunk.id] = 1.0 / (self.rrf_k + chunk.rank)
            
        # Add bm25 scores
        for chunk in bm25_results:
            if chunk.id not in chunk_map:
                chunk_map[chunk.id] = chunk
                rrf_scores[chunk.id] = 0.0
            rrf_scores[chunk.id] += 1.0 / (self.rrf_k + chunk.rank)
            
        # Sort by RRF score descending
        sorted_ids = sorted(rrf_scores.keys(), key=lambda x: rrf_scores[x], reverse=True)
        
        # Build final top_k
        fused_results = []
        for rank, chunk_id in enumerate(sorted_ids[:top_k], 1):
            original_chunk = chunk_map[chunk_id]
            fused_chunk = RetrievalChunk(
                id=original_chunk.id,
                document_id=original_chunk.document_id,
                text=original_chunk.text,
                score=rrf_scores[chunk_id],
                rank=rank,
                metadata={
                    "chunk_index": original_chunk.metadata.get("chunk_index"),
                    "retriever": "hybrid",
                    "rrf_score": rrf_scores[chunk_id]
                }
            )
            fused_results.append(fused_chunk)
            
        return fused_results
=======
from typing import List, Dict, Any, Optional
from .base import BaseRetriever, RetrievedChunk

class HybridRetriever(BaseRetriever):
    def __init__(self, vector_retriever: BaseRetriever, bm25_retriever: BaseRetriever, rrf_k: int = 60):
        """
        Initialize with configured underlying retrievers.
        """
        self.vector_retriever = vector_retriever
        self.bm25_retriever = bm25_retriever
        self.rrf_k = rrf_k

    def retrieve(self, query: str, top_k: int = 5, filters: Optional[Dict[str, Any]] = None) -> List[RetrievedChunk]:
        # Usually hybrid fetches more candidates from underlying to improve fusion quality
        candidate_k = top_k * 2
        
        vector_results = self.vector_retriever.retrieve(query, top_k=candidate_k, filters=filters)
        bm25_results = self.bm25_retriever.retrieve(query, top_k=candidate_k, filters=filters)
        
        # Merge duplicates and compute RRF
        chunk_map = {}
        
        # Process Vector results
        for item in vector_results:
            rrf_score = 1.0 / (self.rrf_k + item.rank)
            chunk_map[item.chunk_id] = {
                "chunk_id": item.chunk_id,
                "document_id": item.document_id,
                "document_version_id": item.document_version_id,
                "vector_rank": item.rank,
                "vector_score": item.score,
                "bm25_rank": None,
                "bm25_score": None,
                "rrf_score": rrf_score,
                "metadata": item.metadata
            }
            
        # Process BM25 results
        for item in bm25_results:
            rrf_score = 1.0 / (self.rrf_k + item.rank)
            if item.chunk_id in chunk_map:
                chunk_map[item.chunk_id]["bm25_rank"] = item.rank
                chunk_map[item.chunk_id]["bm25_score"] = item.score
                chunk_map[item.chunk_id]["rrf_score"] += rrf_score
            else:
                chunk_map[item.chunk_id] = {
                    "chunk_id": item.chunk_id,
                    "document_id": item.document_id,
                    "document_version_id": item.document_version_id,
                    "vector_rank": None,
                    "vector_score": None,
                    "bm25_rank": item.rank,
                    "bm25_score": item.score,
                    "rrf_score": rrf_score,
                    "metadata": item.metadata
                }
                
        # Sort by RRF score descending
        fused_list = sorted(chunk_map.values(), key=lambda x: x["rrf_score"], reverse=True)
        
        results = []
        for rank, item in enumerate(fused_list[:top_k], start=1):
            results.append(RetrievedChunk(
                chunk_id=item["chunk_id"],
                document_id=item["document_id"],
                document_version_id=item["document_version_id"],
                score=item["rrf_score"],
                rank=rank,
                retrieval_method="hybrid",
                metadata={
                    **item["metadata"],
                    "vector_rank": item["vector_rank"],
                    "vector_score": item["vector_score"],
                    "bm25_rank": item["bm25_rank"],
                    "bm25_score": item["bm25_score"]
                }
            ))
            
        return results
>>>>>>> Stashed changes
