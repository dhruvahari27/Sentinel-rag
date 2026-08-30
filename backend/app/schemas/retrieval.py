from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class RetrievalChunk(BaseModel):
    id: str
    document_id: str
    text: str
    score: float
    rank: int
    metadata: Dict[str, Any] = Field(default_factory=dict)

class QueryRequest(BaseModel):
    question: str
    top_k: int = 5
    retriever_type: str = "hybrid" # "vector", "bm25", or "hybrid"

class QueryResponse(BaseModel):
    question: str
    results: List[RetrievalChunk]
    latency_ms: float
