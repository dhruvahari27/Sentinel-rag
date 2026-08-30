import logging
from abc import ABC, abstractmethod
from typing import List, Optional

from app.schemas.retrieval import RetrievalChunk

logger = logging.getLogger(__name__)

class BaseReranker(ABC):
    @abstractmethod
    def rerank(self, query: str, candidates: List[RetrievalChunk]) -> List[RetrievalChunk]:
        """
        Rerank a pool of candidates based on a query.
        Must preserve original_rank, vector_score, bm25_score, rrf_score.
        Must set reranker_score and final_rank.
        """
        pass

class CrossEncoderReranker(BaseReranker):
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2", device: str = "cpu"):
        self.model_name = model_name
        self.device = device
        self._model = None
        self._is_loaded = False
        self._load_failed = False

    def _lazy_load_model(self):
        if self._is_loaded or self._load_failed:
            return

        try:
            from sentence_transformers import CrossEncoder
            logger.info(f"Loading CrossEncoder model '{self.model_name}' on device '{self.device}'...")
            # We use max_length to limit memory usage
            self._model = CrossEncoder(self.model_name, device=self.device, max_length=512)
            self._is_loaded = True
            logger.info("CrossEncoder loaded successfully.")
        except ImportError:
            logger.error("sentence-transformers is not installed. Reranking unavailable.")
            self._load_failed = True
        except Exception as e:
            logger.error(f"Failed to load CrossEncoder model: {e}")
            self._load_failed = True

    def rerank(self, query: str, candidates: List[RetrievalChunk]) -> List[RetrievalChunk]:
        if not candidates:
            return []

        self._lazy_load_model()

        if self._load_failed or not self._model:
            raise RuntimeError("Reranker model is unavailable.")

        # Prepare batch for cross-encoder: (query, chunk_text)
        pairs = [[query, chunk.text] for chunk in candidates]
        
        try:
            scores = self._model.predict(pairs)
        except Exception as e:
            logger.error(f"CrossEncoder inference failed: {e}")
            raise RuntimeError(f"Reranking inference failed: {e}")

        # Update candidate scores
        for chunk, score in zip(candidates, scores):
            # The model predicts float32. Convert to standard python float.
            chunk.reranker_score = float(score)

        # Sort based on reranker score descending
        # Ensure we maintain stable sorting for identical scores
        reranked_candidates = sorted(candidates, key=lambda x: x.reranker_score, reverse=True)

        # Update final_rank
        for idx, chunk in enumerate(reranked_candidates, 1):
            chunk.final_rank = idx
            
        return reranked_candidates
