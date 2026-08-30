import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from sqlalchemy import text
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
        doc = Document(filename="hybrid_test.txt", content_hash="hash_hybrid", metadata_={})
        session.add(doc)
        session.flush()
        
        # Chunk 1: Relevant for Vector (since vector matches [0.9, 0.0] heavily).
        # We also make sure the word "banana" is here but maybe less prominent for BM25.
        chunk1 = DocumentChunk(
            document_id=doc.id,
            chunk_index=0,
            text="This is heavily about python. Python is a snake.",
            embedding=[0.9, 0.0] + [0.0] * 1534
        )
        
        # Chunk 2: Relevant for BM25 (word "banana" appears a lot).
        # But for Vector, it is [0.1, 0.1].
        chunk2 = DocumentChunk(
            document_id=doc.id,
            chunk_index=1,
            text="banana banana banana! A fruit called banana.",
            embedding=[0.1, 0.1] + [0.1] * 1534
        )
        
        # Chunk 3: Relevant for BOTH!
        # "python" and "banana", with intermediate vector.
        chunk3 = DocumentChunk(
            document_id=doc.id,
            chunk_index=2,
            text="A python eating a banana.",
            embedding=[0.5, 0.5] + [0.0] * 1534
        )
        
        session.add_all([chunk1, chunk2, chunk3])
        session.commit()
        
    yield
    
    with Session(engine) as session:
        session.query(Document).delete()
        session.commit()

def test_bm25_retrieval(setup_db):
    response = client.post(
        "/api/v1/query/",
        json={"question": "banana", "top_k": 3, "retriever_type": "bm25"}
    )
    
    assert response.status_code == 200
    results = response.json()["results"]
    assert len(results) > 0
    # The chunk with the most 'banana's should win in BM25
    assert results[0]["text"] == "banana banana banana! A fruit called banana."

def test_hybrid_retrieval(setup_db):
    # Vector query default mock embedding is [0.1]*1536.
    # [0.1, 0.1] has cosine distance 0 from [0.1, 0.1] (chunk 2).
    # [0.5, 0.5] also has cosine distance 0 from [0.1, 0.1] (chunk 3).
    # Wait, the dummy vector for `query` is [0.1] * 1536 from MockEmbeddingProvider.
    # We want a query that tests RRF properly.
    
    response = client.post(
        "/api/v1/query/",
        json={"question": "banana", "top_k": 3, "retriever_type": "hybrid"}
    )
    
    assert response.status_code == 200
    results = response.json()["results"]
    assert len(results) > 0
    assert "rrf_score" in results[0]["metadata"]
