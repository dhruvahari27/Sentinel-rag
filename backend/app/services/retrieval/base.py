from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from app.schemas.retrieval import RetrievalChunk

class BaseRetriever(ABC):
    @abstractmethod
    def retrieve(
        self, 
        query: str, 
        top_k: int = 20, 
        filters: Optional[Dict[str, Any]] = None
    ) -> List[RetrievalChunk]:
        pass
