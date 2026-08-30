import pytest
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
    assert "answer" in data
    assert "citations" in data
    
    # Check the inner retrieval object
    retrieval_data = data["retrieval"]
    assert len(retrieval_data["results"]) == 2
    
    results = retrieval_data["results"]
    assert results[0]["text"] == "This is totally unrelated text about bananas."
    assert results[1]["text"] == "This is highly relevant text about python."
    assert results[0]["score"] > results[1]["score"]
