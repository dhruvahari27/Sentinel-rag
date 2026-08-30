from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.ingestion import DocumentUploadResponse
from app.services.ingestion.pipeline import IngestionPipeline

router = APIRouter()

@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
        
    try:
        content = await file.read()
        text_content = content.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="File must be a valid UTF-8 text document."
        )

    pipeline = IngestionPipeline(db)
    try:
        doc = pipeline.process_document(file.filename, text_content)
        return DocumentUploadResponse(
            document_id=doc.id,
            filename=doc.filename,
            status="success",
            message="Document successfully processed and ingested.",
            chunks_created=len(doc.chunks) if doc.chunks else 0
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process document: {str(e)}"
        )
