<<<<<<< Updated upstream
from abc import ABC, abstractmethod
from typing import List
from app.schemas.retrieval import RetrievalChunk

class BaseRetriever(ABC):
    @abstractmethod
    def retrieve(self, query: str, top_k: int = 5) -> List[RetrievalChunk]:
        """
        Retrieve chunks relevant to the query.
        """
        pass
=======
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class RetrievedChunk(BaseModel):
    chunk_id: str
    document_id: str
    document_version_id: Optional[str] = None
    score: float
    rank: int
    retrieval_method: str
    metadata: Dict[str, Any] = {}

class BaseRetriever:
    def retrieve(self, query: str, top_k: int = 5, filters: Optional[Dict[str, Any]] = None) -> List[RetrievedChunk]:
        raise NotImplementedError("Subclasses must implement the retrieve method.")
>>>>>>> Stashed changes
