from typing import List, Dict, Any, Optional
from app.schemas.retrieval import RetrievalChunk
from app.services.retrieval.base import BaseRetriever

class BM25Retriever(BaseRetriever):
    def retrieve(
        self, 
        query: str, 
        top_k: int = 20, 
        filters: Optional[Dict[str, Any]] = None
    ) -> List[RetrievalChunk]:
        # Minimal stub
        results = []
        for i in range(top_k):
            # Offset chunk IDs to create some overlap and some disjoint chunks with vector
            chunk_idx = i + 2
            results.append(RetrievalChunk(
                chunk_id=f"chunk_{chunk_idx}",
                document_id=f"doc_{chunk_idx % 5}",
                text=f"Mock BM25 chunk {chunk_idx} for query: {query}",
                bm25_score=15.0 - (i * 0.5),
                retrieval_method="bm25"
            ))
        return results
