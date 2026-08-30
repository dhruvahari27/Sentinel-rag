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

    def retrieve(self, query: str, top_k: int = 5, filters: dict = None) -> List[RetrievalChunk]:
        # Embed the query
        query_embedding = self.embedding_provider.embed_query(query)
        
        # We use cosine distance (<=>) for nearest neighbors
        # For cosine similarity, it's 1 - cosine_distance
        distance_col = DocumentChunk.embedding.cosine_distance(query_embedding).label("distance")
        
        stmt = select(DocumentChunk, distance_col)
        
        if filters:
            if "document_id" in filters:
                stmt = stmt.where(DocumentChunk.document_id == filters["document_id"])
        
        stmt = stmt.order_by(distance_col).limit(top_k)
        
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
