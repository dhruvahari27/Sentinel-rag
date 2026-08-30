from abc import ABC, abstractmethod
from typing import List
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class BaseEmbeddingProvider(ABC):
    @abstractmethod
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        pass
        
    @abstractmethod
    def embed_query(self, query: str) -> List[float]:
        pass

class SentenceTransformerProvider(BaseEmbeddingProvider):
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model_name = model_name
        self._model = None
        
    def _load_model(self):
        if not self._model:
            try:
                from sentence_transformers import SentenceTransformer
                logger.info(f"Loading SentenceTransformer model {self.model_name}...")
                self._model = SentenceTransformer(self.model_name)
            except ImportError:
                raise ImportError("sentence-transformers is not installed.")
                
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        self._load_model()
        embeddings = self._model.encode(texts, show_progress_bar=False)
        return embeddings.tolist()
        
    def embed_query(self, query: str) -> List[float]:
        self._load_model()
        embedding = self._model.encode(query, show_progress_bar=False)
        return embedding.tolist()

class MockEmbeddingProvider(BaseEmbeddingProvider):
    def __init__(self, dimensions: int = 1536):
        self.dimensions = dimensions
        
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        return [[0.1] * self.dimensions for _ in texts]
        
    def embed_query(self, query: str) -> List[float]:
        return [0.1] * self.dimensions

def get_embedding_provider() -> BaseEmbeddingProvider:
    # Use a mock provider for now to avoid requiring OpenAI keys
    # or downloading models during local dev, unless configured otherwise.
    # We use 1536 dimensions to match pgvector column default.
    return MockEmbeddingProvider(dimensions=1536)
