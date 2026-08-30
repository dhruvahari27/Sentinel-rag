import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../backend'))

import json
import time
import logging
from sqlalchemy.orm import Session
from app.db.session import engine, SessionLocal
from app.models.document import Document, DocumentChunk
from app.db.base import Base
from app.services.retrieval.vector import VectorRetriever
from app.services.embeddings.provider import get_embedding_provider
from app.services.ingestion.chunker import SimpleTextChunker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 5 Synthetic documents
CORPUS = {
    "doc1.txt": "Python is an interpreted, high-level, general-purpose programming language. Created by Guido van Rossum and first released in 1991, Python's design philosophy emphasizes code readability.",
    "doc2.txt": "The quick brown fox jumps over the lazy dog. This is an English language pangram, a sentence that contains all of the letters of the English alphabet.",
    "doc3.txt": "Machine learning is the study of computer algorithms that improve automatically through experience. It is seen as a subset of artificial intelligence.",
    "doc4.txt": "PostgreSQL is a powerful, open source object-relational database system that uses and extends the SQL language combined with many features that safely store and scale the most complicated data workloads.",
    "doc5.txt": "A neural network is a network or circuit of neurons, or in a modern sense, an artificial neural network, composed of artificial neurons or nodes."
}

# 20 Questions mapped to the relevant document filename
DATASET = [
    ("Who created Python?", "doc1.txt"),
    ("When was Python released?", "doc1.txt"),
    ("What is Python's design philosophy?", "doc1.txt"),
    ("Is Python high-level?", "doc1.txt"),
    
    ("What animal jumps over the dog?", "doc2.txt"),
    ("What is a pangram?", "doc2.txt"),
    ("Does the sentence contain all letters?", "doc2.txt"),
    ("What color is the fox?", "doc2.txt"),
    
    ("What is machine learning?", "doc3.txt"),
    ("How do algorithms improve?", "doc3.txt"),
    ("Is ML a subset of AI?", "doc3.txt"),
    ("Do algorithms improve automatically?", "doc3.txt"),
    
    ("What is PostgreSQL?", "doc4.txt"),
    ("Is PostgreSQL open source?", "doc4.txt"),
    ("What language does PostgreSQL extend?", "doc4.txt"),
    ("Can PostgreSQL scale workloads?", "doc4.txt"),
    
    ("What is a neural network?", "doc5.txt"),
    ("Are they composed of nodes?", "doc5.txt"),
    ("What is the modern sense of a neural network?", "doc5.txt"),
    ("Is a circuit of neurons a neural network?", "doc5.txt"),
]

def setup_corpus(db: Session):
    logger.info("Setting up corpus...")
    Base.metadata.create_all(bind=engine)
    db.query(DocumentChunk).delete()
    db.query(Document).delete()
    db.commit()
    
    chunker = SimpleTextChunker(chunk_size=50, chunk_overlap=10)
    provider = get_embedding_provider()
    
    doc_map = {}
    for filename, text in CORPUS.items():
        doc = Document(filename=filename, content_hash=str(hash(text)), metadata_={})
        db.add(doc)
        db.flush()
        doc_map[filename] = doc.id
        
        chunks = chunker.chunk_text(text)
        embeddings = provider.embed_texts(chunks)
        
        db_chunks = []
        for i, (chunk, emb) in enumerate(zip(chunks, embeddings)):
            db_chunks.append(DocumentChunk(
                document_id=doc.id,
                chunk_index=i,
                text=chunk,
                embedding=emb
            ))
        db.add_all(db_chunks)
    db.commit()
    logger.info("Corpus setup complete.")
    return doc_map

def calculate_mrr(rankings):
    mrr = 0.0
    for rank in rankings:
        if rank > 0:
            mrr += 1.0 / rank
    return mrr / len(rankings) if rankings else 0.0

def run_evaluation():
    db = SessionLocal()
    try:
        doc_map = setup_corpus(db)
        
        provider = get_embedding_provider()
        retriever = VectorRetriever(db, provider)
        
        logger.info("Running baseline retrieval experiment...")
        
        results_data = []
        ranks = []
        recall_3 = 0
        recall_5 = 0
        recall_10 = 0
        
        start_time = time.time()
        
        for question, expected_doc in DATASET:
            expected_id = doc_map[expected_doc]
            
            chunks = retriever.retrieve(question, top_k=10)
            
            # Find the rank of the first chunk from the expected document
            found_rank = 0
            for i, chunk in enumerate(chunks, 1):
                if chunk.document_id == expected_id:
                    found_rank = i
                    break
                    
            ranks.append(found_rank)
            
            if found_rank > 0 and found_rank <= 3: recall_3 += 1
            if found_rank > 0 and found_rank <= 5: recall_5 += 1
            if found_rank > 0 and found_rank <= 10: recall_10 += 1
            
            results_data.append({
                "question": question,
                "expected_document": expected_doc,
                "found_rank": found_rank,
                "retrieved": [{"chunk_id": c.id, "doc_id": c.document_id, "score": c.score} for c in chunks]
            })
            
        total_time = time.time() - start_time
        
        n = len(DATASET)
        metrics = {
            "Recall@3": recall_3 / n,
            "Recall@5": recall_5 / n,
            "Recall@10": recall_10 / n,
            "MRR": calculate_mrr(ranks),
            "total_latency_seconds": total_time,
            "average_latency_ms": (total_time / n) * 1000,
            "embedding_model": "mock-embeddings-1536",
            "retriever": "vector",
            "dataset_size": n
        }
        
        logger.info(f"Metrics: {metrics}")
        
        output = {
            "metrics": metrics,
            "results": results_data
        }
        
        out_path = os.path.join(os.path.dirname(__file__), "results", "baseline", "results.json")
        with open(out_path, "w") as f:
            json.dump(output, f, indent=2)
            
        logger.info(f"Results saved to {out_path}")
        
    finally:
        db.close()

if __name__ == "__main__":
    run_evaluation()
