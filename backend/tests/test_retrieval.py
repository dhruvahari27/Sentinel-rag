import pytest
<<<<<<< Updated upstream
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.db.session import engine
from app.models.document import Document, DocumentChunk
from app.db.base import Base

client = TestClient(app)

@pytest.fixture(scope="module")
def setup_db():
    Base.metadata.create_all(bind=engine)
    
    with Session(engine) as session:
        session.query(Document).delete()
        session.commit()
        
        # Insert dummy document
        doc = Document(filename="retrieval_test.txt", content_hash="hash123", metadata_={})
        session.add(doc)
        session.flush()
        
        # Insert chunks with mock embeddings (dimension 1536)
        # We will make the first one very close to query (all 0.9)
        # Second one further (all 0.1)
        chunk1 = DocumentChunk(
            document_id=doc.id,
            chunk_index=0,
            text="This is highly relevant text about python.",
            embedding=[0.9, 0.0] + [0.0] * 1534
        )
        chunk2 = DocumentChunk(
            document_id=doc.id,
            chunk_index=1,
            text="This is totally unrelated text about bananas.",
            embedding=[0.1, 0.1] + [0.1] * 1534
        )
        
        session.add_all([chunk1, chunk2])
        session.commit()
        
    yield
    
    with Session(engine) as session:
        session.query(Document).delete()
        session.commit()

def test_vector_retrieval(setup_db):
    response = client.post(
        "/api/v1/query/",
        json={"question": "python programming", "top_k": 2}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["question"] == "python programming"
    assert len(data["results"]) == 2
    
    # In the mock provider, embed_query returns [0.1]*1536 by default.
    # So chunk2 ([0.1]) will be closest to the query ([0.1]), meaning chunk2 ranks first!
    # Let's verify that sorting actually happened.
    results = data["results"]
    assert results[0]["text"] == "This is totally unrelated text about bananas."
    assert results[1]["text"] == "This is highly relevant text about python."
    assert results[0]["score"] > results[1]["score"]
=======
from backend.app.services.retrieval import VectorRetriever, BM25Retriever, HybridRetriever

@pytest.fixture
def sample_chunks():
    return [
        {"chunk_id": "c1", "document_id": "d1", "text": "The quick brown fox jumps over the lazy dog.", "metadata": {"type": "animal"}},
        {"chunk_id": "c2", "document_id": "d1", "text": "SENTINEL-RAG is a hybrid retrieval system.", "metadata": {"type": "tech"}},
        {"chunk_id": "c3", "document_id": "d2", "text": "BM25 uses term frequency and inverse document frequency.", "metadata": {"type": "tech"}},
        {"chunk_id": "c4", "document_id": "d2", "text": "Vector dense search uses embeddings like text-embedding-3-small.", "metadata": {"type": "tech"}},
    ]

def test_bm25_retrieval(sample_chunks):
    bm25 = BM25Retriever(chunks=sample_chunks)
    results = bm25.retrieve("BM25 term frequency", top_k=2)
    assert len(results) > 0
    assert results[0].chunk_id == "c3"
    assert results[0].retrieval_method == "bm25"

def test_vector_retrieval_stub(sample_chunks):
    vector = VectorRetriever(chunks=sample_chunks)
    results = vector.retrieve("vector dense search", top_k=2)
    assert len(results) == 2
    assert results[0].retrieval_method == "vector"

def test_hybrid_retrieval(sample_chunks):
    vector = VectorRetriever(chunks=sample_chunks)
    bm25 = BM25Retriever(chunks=sample_chunks)
    hybrid = HybridRetriever(vector, bm25, rrf_k=60)
    
    results = hybrid.retrieve("BM25 hybrid system", top_k=3)
    assert len(results) > 0
    assert results[0].retrieval_method == "hybrid"
    # Metadata should contain ranks
    assert "bm25_rank" in results[0].metadata
    assert "vector_rank" in results[0].metadata

def test_metadata_filters(sample_chunks):
    bm25 = BM25Retriever(chunks=sample_chunks)
    results = bm25.retrieve("quick brown fox", top_k=5, filters={"type": "tech"})
    # c1 is "animal", so it should be filtered out despite matching text
    assert len(results) == 0

    results2 = bm25.retrieve("BM25", top_k=5, filters={"type": "tech"})
    assert len(results2) > 0
    assert results2[0].chunk_id == "c3"
>>>>>>> Stashed changes
