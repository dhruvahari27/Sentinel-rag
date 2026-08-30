# SENTINEL-RAG

Self-Evaluating Evidence-Navigating, Trust-Calibrated, Intelligent and Latency-Aware Retrieval-Augmented Generation

## 1. Project Description
SENTINEL-RAG is a closed-loop evidence orchestration framework designed for reliable, cost-aware, conflict-resilient, and verifiable RAG. Unlike fixed-budget document chatbots, SENTINEL-RAG features a dynamic Evidence Orchestration Policy that adaptively controls retrieval, evidence assessment, claim verification, answer repair, and abstention.

## 2. Current Status
> **Current Phase: PHASE 1 — Project Skeleton**
> 
> *The repository skeleton, FastAPI backend, Next.js frontend shell, Docker configuration, and test suites are initialized. RAG intelligence, document ingestion, and orchestrator policies will be added in subsequent phases.*

## 3. Architecture Overview
- **Frontend**: Next.js 14, TypeScript, React
- **Backend**: Python 3.12+, FastAPI, Pydantic v2, SQLAlchemy
- **Database**: PostgreSQL with `pgvector`
- **Cache**: Redis
- **Containerization**: Docker & Docker Compose
- **Central Component**: Evidence Orchestrator Policy (Phase 9)

## 4. Repository Structure
```text
sentinel-rag/
├── AGENTS.md
├── README.md
├── LICENSE
├── .gitignore
├── .env.example
├── docker-compose.yml
│
├── docs/
│   ├── architecture.md
│   ├── decisions.md
│   ├── development-plan.md
│   └── evaluation-plan.md
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── main.py
│   ├── tests/
│   ├── alembic/
│   ├── pyproject.toml
│   └── README.md
│
├── frontend/
│   ├── app/
│   ├── package.json
│   └── README.md
│
├── evaluation/
│   └── README.md
│
├── scripts/
│   └── README.md
│
└── tests/
    └── README.md
```

## 5. Prerequisites
- Python 3.12+
- Node.js 20+ & npm
- Docker & Docker Compose

## 6. Local Development Instructions

### 7. Environment Setup
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

### 8. Backend Startup
```bash
cd backend
pip install -e .[dev]
uvicorn app.main:app --reload --port 8000
```
API Documentation will be available at `http://localhost:8000/docs`.

### 9. Frontend Startup
```bash
cd frontend
npm install
npm run dev
```
Frontend will be available at `http://localhost:3000`.

### 10. Docker Startup
```bash
docker compose up --build
```

### 11. Testing
Run backend unit and health tests:
```bash
cd backend
pytest
```

## 12. Current Limitations
- RAG pipeline, document ingestion, embeddings, and Evidence Orchestrator are not yet implemented (scheduled for Phases 2–12).
- Database tables (documents, chunks, claims) have not yet been migrated.

## 13. Development Roadmap
- **Phase 0**: Architecture freeze (Completed)
- **Phase 1**: Production Project Skeleton (Completed)
- **Phase 2**: Document Intelligence & Ingestion Pipeline
- **Phase 3**: Baseline Vector RAG
- **Phase 4**: Evaluation Framework & Benchmark Dataset
- **Phase 5**: Hybrid Retrieval (Vector + BM25)
- **Phase 6**: Reranking Integration
- **Phase 7**: Evidence Sufficiency Assessment
- **Phase 8**: Evidence Graph & Independence
- **Phase 9**: Adaptive Evidence Orchestrator
- **Phase 10**: Claim Verification Engine
- **Phase 11**: Temporal Reasoning & Conflict Resolution
- **Phase 12**: Budget Management & Answer Repair
- **Phase 13**: Frontend UI Implementation
- **Phase 14**: RAG Flight Recorder & Observability
- **Phase 15**: Hardening, Security & Testing
- **Phase 16**: Containerized Staging Deployment
- **Phase 17**: Final Benchmark & Comparative Evaluation
