import pytest
from app.schemas.retrieval import RetrievalChunk
from app.services.retrieval.reranker import CrossEncoderReranker

@pytest.mark.skip(reason="Requires downloading model; run manually for smoke testing")
def test_real_cross_encoder():
    reranker = CrossEncoderReranker(model_name="cross-encoder/ms-marco-MiniLM-L-6-v2", device="cpu")
    candidates = [
        RetrievalChunk(chunk_id="c1", document_id="d1", text="The capital of France is Paris.", original_rank=1),
        RetrievalChunk(chunk_id="c2", document_id="d2", text="I love eating cheese.", original_rank=2)
    ]
    reranked = reranker.rerank("What is the capital of France?", candidates)
    
    # Model should score c1 much higher than c2
    assert reranked[0].chunk_id == "c1"
    assert reranked[1].chunk_id == "c2"
    assert reranked[0].reranker_score > reranked[1].reranker_score
