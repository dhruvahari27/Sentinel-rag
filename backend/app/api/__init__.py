from fastapi import APIRouter
from .routes.health import router as health_router
from .routes.ingestion import router as ingestion_router
from .routes.query import router as query_router

api_router = APIRouter()
api_router.include_router(health_router, tags=["health"])
api_router.include_router(ingestion_router, prefix="/ingestion", tags=["ingestion"])
api_router.include_router(query_router, prefix="/query", tags=["query"])
