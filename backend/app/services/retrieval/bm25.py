from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import select, func, text
from app.models.document import DocumentChunk
from app.schemas.retrieval import RetrievalChunk
from app.services.retrieval.base import BaseRetriever

class BM25Retriever(BaseRetriever):
    def __init__(self, db: Session):
        self.db = db

    def retrieve(self, query: str, top_k: int = 5) -> List[RetrievalChunk]:
        # We use PostgreSQL's native Full Text Search.
        # websearch_to_tsquery is great for handling raw user input gracefully.
        
        tsquery = func.websearch_to_tsquery('english', query)
        
        # ts_rank_cd computes the cover density rank
        rank_func = func.ts_rank_cd(DocumentChunk.text_search_vector, tsquery).label("rank_score")
        
        stmt = (
            select(DocumentChunk, rank_func)
            .where(DocumentChunk.text_search_vector.op('@@')(tsquery))
            .order_by(rank_func.desc())
            .limit(top_k)
        )
        
        results = self.db.execute(stmt).all()
        
        retrieval_chunks = []
        for rank, (chunk, score) in enumerate(results, 1):
            retrieval_chunks.append(
                RetrievalChunk(
                    id=chunk.id,
                    document_id=chunk.document_id,
                    text=chunk.text,
                    score=float(score),
                    rank=rank,
                    metadata={
                        "chunk_index": chunk.chunk_index,
                        "retriever": "bm25"
                    }
                )
            )
            
        return retrieval_chunks
