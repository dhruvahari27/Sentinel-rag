import pytest
from app.schemas.retrieval import RetrievalChunk, QueryRequest
from app.services.retrieval.reranker import BaseReranker
from app.services.retrieval.pipeline import RetrievalPipeline
from typing import List

class MockReranker(BaseReranker):
    def __init__(self):
        self.model_name = "mock-reranker"
        
    def rerank(self, query: str, candidates: List[RetrievalChunk]) -> List[RetrievalChunk]:
        for chunk in candidates:
            # deterministic score
            chunk.reranker_score = 0.5 if "relevant" in chunk.text else 0.1
        reranked = sorted(candidates, key=lambda x: x.reranker_score, reverse=True)
        for idx, chunk in enumerate(reranked, 1):
            chunk.final_rank = idx
        return reranked

def test_reranker_sorting():
    reranker = MockReranker()
    candidates = [
        RetrievalChunk(chunk_id="c1", document_id="d1", text="some text", original_rank=1),
        RetrievalChunk(chunk_id="c2", document_id="d2", text="highly relevant text", original_rank=2)
    ]
    reranked = reranker.rerank("query", candidates)
    
    assert reranked[0].chunk_id == "c2"
    assert reranked[0].reranker_score == 0.5
    assert reranked[0].final_rank == 1
    
    assert reranked[1].chunk_id == "c1"
    assert reranked[1].reranker_score == 0.1
    assert reranked[1].final_rank == 2

def test_empty_candidates():
    reranker = MockReranker()
    assert reranker.rerank("query", []) == []

def test_pipeline_with_reranking():
    pipeline = RetrievalPipeline(reranker=MockReranker())
    req = QueryRequest(question="query", rerank=True, candidate_k=5, top_k=2)
    resp = pipeline.execute(req)
    
    assert resp.reranking.enabled is True
    assert resp.reranking.applied is True
    assert len(resp.results) <= 2
    
def test_pipeline_fallback():
    # If reranker raises exception, it should fallback (default policy)
    class FailingReranker(BaseReranker):
        def __init__(self):
            self.model_name = "failing-reranker"
        def rerank(self, q, c):
            raise Exception("Mock failure")
            
    pipeline = RetrievalPipeline(reranker=FailingReranker())
    req = QueryRequest(question="query", rerank=True, candidate_k=5, top_k=2)
    resp = pipeline.execute(req)
    
    assert resp.reranking.applied is False
    assert len(resp.results) <= 2
