from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
import uuid

from app.db.base import Base

def generate_uuid():
    return str(uuid.uuid4())

class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, default=generate_uuid)
    filename = Column(String, nullable=False)
    content_hash = Column(String, nullable=False, unique=True, index=True)
    metadata_ = Column("metadata", JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(String, primary_key=True, default=generate_uuid)
    document_id = Column(String, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)
    
    # 1536 is standard for text-embedding-3-small, but adjust as needed
    embedding = Column(Vector(1536))
    
    document = relationship("Document", back_populates="chunks")
