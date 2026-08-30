from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field


class RetrievalChunk(BaseModel):
    chunk_id: str
    text: str
    document_id: str
    original_rank: int = 0
    vector_score: Optional[float] = None
    bm25_score: Optional[float] = None
    rrf_score: Optional[float] = None
    reranker_score: Optional[float] = None
    final_rank: int = 0
    retrieval_method: str = "unknown"
    metadata: Dict[str, Any] = Field(default_factory=dict)


class QueryRequest(BaseModel):
    question: str
    retrieval_method: str = "hybrid"
    rerank: bool = False
    candidate_k: int = 20
    top_k: int = 5
    filters: Optional[Dict[str, Any]] = None


class RetrievalMetadata(BaseModel):
    method: str
    candidate_count: int
    final_k: int

class RerankingMetadata(BaseModel):
    enabled: bool
    model: str
    applied: bool

class QueryResponse(BaseModel):
    question: str
    results: List[RetrievalChunk]
    retrieval: RetrievalMetadata
    reranking: RerankingMetadata
