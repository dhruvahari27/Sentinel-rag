import sys
import logging
from app.db.session import SessionLocal
from app.services.embeddings.provider import get_embedding_provider
from app.services.embeddings.indexer import EmbeddingIndexer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    logger.info("Starting embedding indexer...")
    
    db = SessionLocal()
    try:
        provider = get_embedding_provider()
        indexer = EmbeddingIndexer(db, provider)
        
        logger.info(f"Using provider dimension: {provider.get_dimension()}")
        
        stats = indexer.index_missing_embeddings()
        
        if stats:
            logger.info(f"Final stats: {stats}")
            
    except Exception as e:
        logger.error(f"Fatal error during indexing: {e}")
        sys.exit(1)
    finally:
        db.close()
        
if __name__ == "__main__":
    main()
