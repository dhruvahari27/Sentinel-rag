from typing import List, Dict, Any, Optional
from app.schemas.retrieval import RetrievalChunk
from app.services.retrieval.base import BaseRetriever

class VectorRetriever(BaseRetriever):
    def retrieve(
        self, 
        query: str, 
        top_k: int = 20, 
        filters: Optional[Dict[str, Any]] = None
    ) -> List[RetrievalChunk]:
        # Minimal stub
        results = []
        for i in range(top_k):
            results.append(RetrievalChunk(
                chunk_id=f"chunk_{i}",
                document_id=f"doc_{i % 5}",
                text=f"Mock vector chunk {i} for query: {query}",
                vector_score=0.9 - (i * 0.01),
                retrieval_method="vector"
            ))
        return results
