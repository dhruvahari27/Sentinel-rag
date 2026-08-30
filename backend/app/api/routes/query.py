from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.retrieval import QueryRequest, QueryResponse
from app.services.retrieval.vector import VectorRetriever
from app.services.retrieval.bm25 import BM25Retriever
from app.services.retrieval.hybrid import HybridRetriever
from app.services.embeddings.provider import get_embedding_provider
import time

router = APIRouter()

@router.post("/", response_model=QueryResponse)
def query_documents(
    request: QueryRequest,
    db: Session = Depends(get_db)
):
    start_time = time.time()
    
    try:
        embedding_provider = get_embedding_provider()
        
        if request.retriever_type == "vector":
            retriever = VectorRetriever(db, embedding_provider)
        elif request.retriever_type == "bm25":
            retriever = BM25Retriever(db)
        elif request.retriever_type == "hybrid":
            retriever = HybridRetriever(db, embedding_provider)
        else:
            raise ValueError(f"Unknown retriever_type: {request.retriever_type}")
            
        results = retriever.retrieve(request.question, top_k=request.top_k)
        
        latency = (time.time() - start_time) * 1000  # ms
        
        return QueryResponse(
            question=request.question,
            results=results,
            latency_ms=latency
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to query documents: {str(e)}"
        )
