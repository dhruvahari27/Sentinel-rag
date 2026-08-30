from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import hashlib
from typing import Optional
from app.models.document import Document, DocumentChunk
from app.services.ingestion.chunker import SimpleTextChunker
from app.services.embeddings.provider import get_embedding_provider
import logging

logger = logging.getLogger(__name__)

class IngestionPipeline:
    def __init__(self, db: Session):
        self.db = db
        self.chunker = SimpleTextChunker()
        self.embedding_provider = get_embedding_provider()

    def process_document(self, filename: str, content: str) -> Document:
        # 1. Check for duplicates using content hash
        content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
        
        existing_doc = self.db.query(Document).filter(Document.content_hash == content_hash).first()
        if existing_doc:
            logger.info(f"Document {filename} already exists with hash {content_hash}")
            return existing_doc

        # 2. Create Document record
        doc = Document(
            filename=filename,
            content_hash=content_hash,
            metadata_={"length": len(content)}
        )
        self.db.add(doc)
        
        # We need the document ID before adding chunks, but we want it all in one transaction.
        # Since ID is generated on Python side or via default, we can flush to make sure it's available.
        self.db.flush()

        # 3. Chunk text
        chunks_text = self.chunker.chunk_text(content)
        
        # 4. Embed chunks
        if chunks_text:
            embeddings = self.embedding_provider.embed_texts(chunks_text)
            
            # 5. Create DocumentChunk records
            db_chunks = []
            for i, (text, emb) in enumerate(zip(chunks_text, embeddings)):
                chunk = DocumentChunk(
                    document_id=doc.id,
                    chunk_index=i,
                    text=text,
                    embedding=emb
                )
                db_chunks.append(chunk)
                
            self.db.add_all(db_chunks)

        self.db.commit()
        self.db.refresh(doc)
        return doc
