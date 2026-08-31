<<<<<<< Updated upstream
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
=======
import re
import time
from typing import List, Dict, Any, Optional
from rank_bm25 import BM25Okapi
from .base import BaseRetriever, RetrievedChunk

def tokenize(text: str) -> List[str]:
    """
    Clean tokenizer for BM25.
    - Lowercases text
    - Preserves numbers, IDs, abbreviations, and technical words.
    - Simple word boundary split using regex (alphanumeric and dashes).
    - No aggressive stopword removal since technical terms might be important.
    """
    text = text.lower()
    # Match alphanumeric words, allowing internal hyphens for tech terms like "cross-document"
    tokens = re.findall(r'\b[a-z0-9]+(?:-[a-z0-9]+)*\b', text)
    return tokens

class BM25Retriever(BaseRetriever):
    def __init__(self, chunks: List[Dict[str, Any]] = None):
        """
        Initialize the BM25 index with a given chunk corpus.
        chunks: List of dicts with 'chunk_id', 'document_id', 'text', 'metadata'.
        """
        self.chunks = chunks or []
        self.bm25 = None
        if self.chunks:
            self.build_index()

    def build_index(self):
        """Build the BM25 index."""
        start_time = time.time()
        tokenized_corpus = [tokenize(chunk.get("text", "")) for chunk in self.chunks]
        self.bm25 = BM25Okapi(tokenized_corpus)
        self.build_time_ms = (time.time() - start_time) * 1000

    def retrieve(self, query: str, top_k: int = 5, filters: Optional[Dict[str, Any]] = None) -> List[RetrievedChunk]:
        if not self.bm25 or not self.chunks:
            return []

        tokenized_query = tokenize(query)
        scores = self.bm25.get_scores(tokenized_query)
        
        # Apply filters if provided
        filtered_indices = []
        for i, chunk in enumerate(self.chunks):
            if filters:
                match = True
                for k, v in filters.items():
                    if chunk.get("metadata", {}).get(k) != v and chunk.get(k) != v:
                        match = False
                        break
                if match:
                    filtered_indices.append(i)
            else:
                filtered_indices.append(i)

        if not filtered_indices:
            return []

        # Sort filtered chunks by score
        scored_indices = [(i, scores[i]) for i in filtered_indices if scores[i] > 0]
        scored_indices.sort(key=lambda x: x[1], reverse=True)

        results = []
        for rank, (i, score) in enumerate(scored_indices[:top_k], start=1):
            chunk = self.chunks[i]
            results.append(RetrievedChunk(
                chunk_id=chunk["chunk_id"],
                document_id=chunk["document_id"],
                score=float(score),
                rank=rank,
                retrieval_method="bm25",
                metadata=chunk.get("metadata", {})
            ))

        return results
>>>>>>> Stashed changes
