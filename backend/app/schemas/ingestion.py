from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

class DocumentUploadResponse(BaseModel):
    document_id: str
    filename: str
    status: str
    message: str
    chunks_created: int = 0
