# Development Plan

This document defines the implementation phases for SENTINEL-RAG. 

## Phase 0: Architecture freeze
*   **Objective**: Define the technical blueprint, system architecture, and core design principles.
*   **Expected Files**: `docs/architecture.md`, `docs/decisions.md`, `docs/development-plan.md`, `docs/evaluation-plan.md`.
*   **Dependencies**: None.
*   **Tests**: N/A.
*   **Acceptance Criteria**: All architecture documentation is complete and approved.
*   **Risks**: Scope creep; architectural drift.

## Phase 1: Repository/backend skeleton
*   **Objective**: Establish the foundational repository structure, Docker environment, and base API.
*   **Expected Files**: `backend/`, `tests/`, `scripts/`, `Dockerfile`, `docker-compose.yml`, `pyproject.toml`, `.env.example`.
*   **Dependencies**: Phase 0.
*   **Tests**: Basic health check tests.
*   **Acceptance Criteria**: `docker compose up` successfully starts FastAPI, PostgreSQL (pgvector), and Redis. API returns 200 on `/health`.
*   **Risks**: Environment configuration issues across different OS setups.

## Phase 2: Document ingestion
*   **Objective**: Implement the pipeline to upload, parse, chunk, embed, and store documents in the database.
*   **Expected Files**: `backend/ingestion/`, database schemas/migrations for documents and chunks.
*   **Dependencies**: Phase 1.
*   **Tests**: Upload tests, chunking logic tests, DB storage verification.
*   **Acceptance Criteria**: A PDF/text document can be uploaded via API and successfully embedded and stored in pgvector.
*   **Risks**: Handling large files, parsing complex PDFs.

## Phase 3: Baseline RAG
*   **Objective**: Implement a simple, fixed-budget vector RAG pipeline (B1 Baseline).
*   **Expected Files**: `backend/retrieval/vector.py`, `backend/generation/`.
*   **Dependencies**: Phase 2.
*   **Tests**: End-to-end vector retrieval and generation tests.
*   **Acceptance Criteria**: System can answer queries using simple top-K vector retrieval.
*   **Risks**: Poor prompt formatting leading to hallucinations.

## Phase 4: Evaluation framework
*   **Objective**: Build the custom evaluation framework and benchmark dataset (60-100 labelled questions).
*   **Expected Files**: `evaluation/`, benchmark JSON/CSV datasets, metrics calculation scripts.
*   **Dependencies**: Phase 3.
*   **Tests**: Tests for metric calculations (Precision, Recall, Faithfulness).
*   **Acceptance Criteria**: The B1 baseline can be automatically evaluated against the benchmark dataset, producing real metrics.
*   **Risks**: Creating high-quality, unbiased ground truth data is time-consuming.

## Phase 5: Hybrid retrieval
*   **Objective**: Add BM25 lexical search and fuse results with vector search (B3 Baseline).
*   **Expected Files**: `backend/retrieval/bm25.py`, fusion logic.
*   **Dependencies**: Phase 4.
*   **Tests**: Lexical retrieval tests, fusion scoring tests.
*   **Acceptance Criteria**: Retrieval recall metrics improve on the benchmark compared to vector-only.
*   **Risks**: Tuning fusion weights.

## Phase 6: Reranking
*   **Objective**: Implement cross-encoder reranking to improve precision (B4 Baseline).
*   **Expected Files**: `backend/retrieval/reranker.py`.
*   **Dependencies**: Phase 5.
*   **Tests**: Reranking score ordering tests.
*   **Acceptance Criteria**: Reranker successfully filters and reorders hybrid results, improving Precision@K/NDCG.
*   **Risks**: Significant latency increases.

## Phase 7: Evidence assessment
*   **Objective**: Develop the deterministic scoring system for evidence (relevance, coverage, authority, freshness).
*   **Expected Files**: `backend/orchestration/assessment.py`.
*   **Dependencies**: Phase 6.
*   **Tests**: Unit tests for score calculations.
*   **Acceptance Criteria**: The system assigns a quantifiable sufficiency score to retrieved context.
*   **Risks**: Normalizing arbitrary scores into a coherent metric.

## Phase 8: Evidence graph
*   **Objective**: Map relationships between documents, chunks, and concepts to track duplicates and contradictions.
*   **Expected Files**: `backend/graph/`.
*   **Dependencies**: Phase 7.
*   **Tests**: Graph traversal and relationship tests.
*   **Acceptance Criteria**: System accurately identifies duplicate and derived information to calculate true evidence independence.
*   **Risks**: Memory overhead for graph operations.

## Phase 9: Adaptive Evidence Orchestrator
*   **Objective**: Implement the central control loop that dynamically manages retrieval budgets and routing.
*   **Expected Files**: `backend/orchestration/orchestrator.py`.
*   **Dependencies**: Phase 8.
*   **Tests**: State machine logic tests, routing tests.
*   **Acceptance Criteria**: The system executes multiple retrieval rounds only when evidence is insufficient, stopping when budgets run out.
*   **Risks**: Infinite loops (must have hard limits).

## Phase 10: Claim verification
*   **Objective**: Implement decoupled claim extraction and verification.
*   **Expected Files**: `backend/verification/`.
*   **Dependencies**: Phase 9.
*   **Tests**: Claim extraction accuracy, evidence matching accuracy.
*   **Acceptance Criteria**: Generated answers are split into claims and strictly classified as SUPPORTED, UNUPPORTED, etc.
*   **Risks**: LLM failure to accurately extract discrete claims.

## Phase 11: Temporal/conflict reasoning
*   **Objective**: Enhance the Evidence Orchestrator to resolve conflicting data and handle temporal document updates.
*   **Expected Files**: `backend/orchestration/conflict.py`.
*   **Dependencies**: Phase 10.
*   **Tests**: Contradiction resolution tests, superseded document tests.
*   **Acceptance Criteria**: System correctly prioritizes newer document versions and flags unresolved contradictions.
*   **Risks**: High complexity in logic branching.

## Phase 12: Budget/cost optimization
*   **Objective**: Enforce hard limits on cost and latency; implement answer repair and abstention.
*   **Expected Files**: `backend/orchestration/budget.py`.
*   **Dependencies**: Phase 11.
*   **Tests**: Cost calculation tests, abstention trigger tests.
*   **Acceptance Criteria**: Queries gracefully `ABSTAIN` rather than hallucinate if verification fails and budgets are exhausted.
*   **Risks**: Overly aggressive abstention lowering overall utility.

## Phase 13: Frontend
*   **Objective**: Build the Next.js user interface.
*   **Expected Files**: `frontend/`.
*   **Dependencies**: Phase 12.
*   **Tests**: UI component tests, API integration tests.
*   **Acceptance Criteria**: Users can upload documents and query the RAG system via a web interface.
*   **Risks**: State management complexities in the UI.

## Phase 14: RAG Flight Recorder
*   **Objective**: Implement execution trace logging and UI visualization for observability.
*   **Expected Files**: `backend/monitoring/`, `frontend/components/FlightRecorder.tsx`.
*   **Dependencies**: Phase 13.
*   **Tests**: Trace logging tests, frontend rendering tests.
*   **Acceptance Criteria**: Every query produces a detailed trace (rounds, decisions, latency, cost) viewable in the UI.
*   **Risks**: Massive log data generation.

## Phase 15: Security/testing/hardening
*   **Objective**: Implement auth, rate limiting, and finalize test coverage.
*   **Expected Files**: Security middleware, comprehensive test suites.
*   **Dependencies**: Phase 14.
*   **Tests**: Penetration tests, prompt injection tests, auth tests.
*   **Acceptance Criteria**: System safely rejects malicious inputs and unauthorized access.
*   **Risks**: Overlooking edge-case vulnerabilities.

## Phase 16: Deployment
*   **Objective**: Prepare the application for staging/production deployment.
*   **Expected Files**: CI/CD pipelines, production Docker configurations.
*   **Dependencies**: Phase 15.
*   **Tests**: Deployment smoke tests.
*   **Acceptance Criteria**: System deploys cleanly to a remote server with persistent volumes.
*   **Risks**: Database migration issues in production.

## Phase 17: Final benchmark
*   **Objective**: Run the final comparative evaluation (B0 through Final SENTINEL-RAG).
*   **Expected Files**: Final evaluation report, metrics documentation.
*   **Dependencies**: Phase 16.
*   **Tests**: Full benchmark suite execution.
*   **Acceptance Criteria**: Measurable, non-fabricated metrics demonstrating the value of the Evidence Orchestrator over fixed-budget RAG.
*   **Risks**: Results may show smaller improvements than anticipated.
