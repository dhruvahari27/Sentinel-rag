import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.db.session import engine, get_db
from app.models.document import Document, DocumentChunk
from app.db.base import Base
import os

client = TestClient(app)

@pytest.fixture(scope="module")
def setup_db():
    # Make sure we don't drop everything in prod, but this is a test db
    Base.metadata.create_all(bind=engine)
    yield
    # Optionally clean up documents after tests
    with Session(engine) as session:
        session.query(Document).delete()
        session.commit()

def test_ingestion_chunker():
    from app.services.ingestion.chunker import SimpleTextChunker
    chunker = SimpleTextChunker(chunk_size=10, chunk_overlap=2)
    text = "0123456789ABCDEFGH"
    # "0123456789" (len 10)
    # "89ABCDEFGH" (len 10)
    chunks = chunker.chunk_text(text)
    assert len(chunks) == 2
    assert chunks[0] == "0123456789"
    assert chunks[1] == "89ABCDEFGH"

def test_upload_endpoint(setup_db):
    content = b"This is a test document. " * 50  # ~1250 characters
    
    response = client.post(
        "/api/v1/ingestion/upload",
        files={"file": ("test_doc.txt", content, "text/plain")}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["filename"] == "test_doc.txt"
    assert data["chunks_created"] > 0
    
    # Check if duplicate upload returns same document gracefully
    response2 = client.post(
        "/api/v1/ingestion/upload",
        files={"file": ("test_doc.txt", content, "text/plain")}
    )
    assert response2.status_code == 200
    assert response2.json()["document_id"] == data["document_id"]

def test_upload_invalid_file():
    # Non-utf8 binary content
    content = bytes([0xFF, 0xFE, 0xFD])
    response = client.post(
        "/api/v1/ingestion/upload",
        files={"file": ("bad_doc.bin", content, "application/octet-stream")}
    )
    assert response.status_code == 400
