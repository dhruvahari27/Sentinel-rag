# SENTINEL-RAG Backend API

FastAPI backend service for SENTINEL-RAG.

## Features
- FastAPI asynchronous Web API framework
- Pydantic Settings environment configuration
- SQLAlchemy ORM with PostgreSQL + pgvector readiness
- Redis connection configuration
- Structured logging & Health check endpoints (`/health`, `/api/v1/health`)

## Development Setup

### Prerequisites
- Python 3.12+

### Running the API locally
```bash
pip install -e .[dev]
uvicorn app.main:app --reload --port 8000
```

### Running Tests
```bash
pytest
```
