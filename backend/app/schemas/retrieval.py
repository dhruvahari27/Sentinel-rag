from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class RetrievalChunk(BaseModel):
    id: str
    document_id: str
    text: str
    score: float
    rank: int
    metadata_: Dict[str, Any] = Field(default_factory=dict, alias="metadata")

class QueryRequest(BaseModel):
    question: str
    top_k: int = 5

class QueryResponse(BaseModel):
    question: str
    results: List[RetrievalChunk]
    latency_ms: float
