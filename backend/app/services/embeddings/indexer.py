import time
import logging
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.document import DocumentChunk
from app.services.embeddings.provider import BaseEmbeddingProvider

logger = logging.getLogger(__name__)

class EmbeddingIndexer:
    def __init__(self, db: Session, provider: BaseEmbeddingProvider):
        self.db = db
        self.provider = provider
        
    def index_missing_embeddings(self, batch_size: int = 100):
        """
        Finds chunks with no embeddings and embeds them using the provider.
        """
        start_time = time.time()
        
        # We find chunks where embedding is NULL
        stmt = select(DocumentChunk).where(DocumentChunk.embedding == None)
        chunks = self.db.execute(stmt).scalars().all()
        
        if not chunks:
            logger.info("No chunks missing embeddings.")
            return
            
        logger.info(f"Found {len(chunks)} chunks needing embeddings.")
        
        processed = 0
        failures = 0
        
        # Batch process
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            texts = [c.text for c in batch]
            
            try:
                embeddings = self.provider.embed_texts(texts)
                for chunk, emb in zip(batch, embeddings):
                    chunk.embedding = emb
                self.db.commit()
                processed += len(batch)
            except Exception as e:
                logger.error(f"Failed to embed batch: {e}")
                self.db.rollback()
                failures += len(batch)
                
        duration = time.time() - start_time
        logger.info(f"Indexing complete in {duration:.2f}s. Processed: {processed}, Failures: {failures}.")
        
        return {
            "processed": processed,
            "failures": failures,
            "duration": duration
        }
