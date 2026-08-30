from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.retrieval import QueryRequest, QueryResponse
from app.services.retrieval.vector import VectorRetriever
from app.services.embeddings.provider import get_embedding_provider
from app.services.generation.llm import get_llm_provider
from app.services.rag.service import BaselineRAGService

router = APIRouter()

@router.post("/", response_model=QueryResponse)
def query_documents(
    request: QueryRequest,
    db: Session = Depends(get_db)
):
    try:
        # Currently we only support vector in this baseline phase
        if request.retriever_type != "vector":
            request.retriever_type = "vector"
            
        embedding_provider = get_embedding_provider()
        retriever = VectorRetriever(db, embedding_provider)
        
        llm_provider = get_llm_provider()
        
        rag_service = BaselineRAGService(retriever, llm_provider)
        
        # answer_question encapsulates retrieval, context building, LLM generation, and formatting
        response = rag_service.answer_question(request)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to query documents: {str(e)}"
        )
