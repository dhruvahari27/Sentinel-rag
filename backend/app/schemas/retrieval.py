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
    retriever_type: str = "vector"
    filters: Optional[Dict[str, Any]] = None

class Citation(BaseModel):
    citation_id: str
    document_id: str
    chunk_id: str
    text_snippet: str

class RetrievalInfo(BaseModel):
    top_k: int
    results: List[RetrievalChunk]
    latency_ms: float

class QueryResponse(BaseModel):
    request_id: str
    question: str
    answer: str
    citations: List[Citation]
    retrieval: RetrievalInfo
    total_latency_ms: float
    tokens: Dict[str, int]
    model: str
