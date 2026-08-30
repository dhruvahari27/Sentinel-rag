from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

from typing import Optional, Dict

class HealthResponse(BaseModel):
    status: str
    service: str

class ReadinessResponse(BaseModel):
    status: str
    services: Dict[str, str]

@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return HealthResponse(
        status="ok",
        service="sentinel-rag-api"
    )

@router.get("/health/ready", response_model=ReadinessResponse)
def readiness_check() -> ReadinessResponse:
    from app.db.session import engine
    from app.db.redis import ping_redis
    from sqlalchemy import text
    
    db_status = "ok"
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception:
        db_status = "error"
        
    redis_status = "ok" if ping_redis() else "error"
    
    overall_status = "ok" if db_status == "ok" and redis_status == "ok" else "error"
    
    return ReadinessResponse(
        status=overall_status,
        services={
            "database": db_status,
            "redis": redis_status
        }
    )
