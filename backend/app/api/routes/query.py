from fastapi import APIRouter, Depends, HTTPException
from typing import Any

from app.schemas.retrieval import QueryRequest, QueryResponse
from app.services.retrieval.pipeline import RetrievalPipeline
from app.services.retrieval.reranker import CrossEncoderReranker
from app.core.config import settings

router = APIRouter()

# Instantiate globally or via dependency injection
_reranker = CrossEncoderReranker(
    model_name=settings.reranker_model, 
    device=settings.reranker_device
) if settings.reranker_enabled else None

_pipeline = RetrievalPipeline(reranker=_reranker)

@router.post("/", response_model=QueryResponse)
def run_query(request: QueryRequest) -> Any:
    try:
        return _pipeline.execute(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
