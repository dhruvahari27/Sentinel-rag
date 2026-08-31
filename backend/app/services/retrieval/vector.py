<<<<<<< Updated upstream
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.document import DocumentChunk
from app.schemas.retrieval import RetrievalChunk
from app.services.retrieval.base import BaseRetriever
from app.services.embeddings.provider import BaseEmbeddingProvider

class VectorRetriever(BaseRetriever):
    def __init__(self, db: Session, embedding_provider: BaseEmbeddingProvider):
        self.db = db
        self.embedding_provider = embedding_provider

    def retrieve(self, query: str, top_k: int = 5) -> List[RetrievalChunk]:
        # Embed the query
        query_embedding = self.embedding_provider.embed_query(query)
        
        # We use cosine distance (<=>) for nearest neighbors
        # For cosine similarity, it's 1 - cosine_distance
        distance_col = DocumentChunk.embedding.cosine_distance(query_embedding).label("distance")
        
        stmt = (
            select(DocumentChunk, distance_col)
            .order_by(distance_col)
            .limit(top_k)
        )
        
        results = self.db.execute(stmt).all()
        
        retrieval_chunks = []
        for rank, (chunk, distance) in enumerate(results, 1):
            score = 1.0 - distance
            
            retrieval_chunks.append(
                RetrievalChunk(
                    id=chunk.id,
                    document_id=chunk.document_id,
                    text=chunk.text,
                    score=score,
                    rank=rank,
                    metadata={
                        "chunk_index": chunk.chunk_index,
                        "retriever": "vector"
                    }
                )
            )
            
        return retrieval_chunks
=======
import random
import time
from typing import List, Dict, Any, Optional
from .base import BaseRetriever, RetrievedChunk

class VectorRetriever(BaseRetriever):
    def __init__(self, chunks: List[Dict[str, Any]] = None):
        """
        Stub initialization. In real system, this connects to pgvector.
        """
        self.chunks = chunks or []

    def retrieve(self, query: str, top_k: int = 5, filters: Optional[Dict[str, Any]] = None) -> List[RetrievedChunk]:
        """
        Simulate a vector retrieval search.
        Since we don't have embeddings here, we'll return a deterministic but semi-randomized set 
        based on a hash of the query to keep it stable for tests.
        """
        if not self.chunks:
            return []

        # Simulate latency
        time.sleep(0.02)
        
        # Apply filters
        filtered_chunks = []
        for chunk in self.chunks:
            if filters:
                match = True
                for k, v in filters.items():
                    if chunk.get("metadata", {}).get(k) != v and chunk.get(k) != v:
                        match = False
                        break
                if match:
                    filtered_chunks.append(chunk)
            else:
                filtered_chunks.append(chunk)

        if not filtered_chunks:
            return []

        # Use random with seed based on query length and first char to be stable for tests
        seed = len(query) + (ord(query[0]) if query else 0)
        rng = random.Random(seed)
        
        # Sample chunks
        sampled = rng.sample(filtered_chunks, min(top_k, len(filtered_chunks)))
        
        results = []
        for rank, chunk in enumerate(sampled, start=1):
            # Simulated cosine similarity score
            score = 1.0 - (rank * 0.05)
            results.append(RetrievedChunk(
                chunk_id=chunk["chunk_id"],
                document_id=chunk["document_id"],
                score=score,
                rank=rank,
                retrieval_method="vector",
                metadata=chunk.get("metadata", {})
            ))

        return results
>>>>>>> Stashed changes
