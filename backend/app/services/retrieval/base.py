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
