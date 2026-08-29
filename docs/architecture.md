# SENTINEL-RAG Architecture

This document describes the architecture of the SENTINEL-RAG system.

> **Status:** All features described in this document are currently **PLANNED**. There is no implemented functionality at this stage.

## Core Concept: Evidence Orchestration Policy

The central architectural concept is the Evidence Orchestration Policy. This policy dynamically controls:
- Retrieval
- Evidence assessment
- Verification
- Repair
- Abstention

The policy operates under explicit quality, latency, and cost constraints.

## System Components (Planned)

1. **Frontend (Next.js + TypeScript)**
   - User interface for querying and interacting with the RAG system.
   - (Planned)

2. **Backend API (Python + FastAPI)**
   - Exposes endpoints for the frontend.
   - Orchestrates the Evidence Orchestration Policy.
   - (Planned)

3. **Retrieval Engine (PostgreSQL + pgvector + BM25)**
   - Hybrid retrieval combining dense vector search (pgvector) and lexical search (BM25).
   - (Planned)

4. **Caching Layer (Redis)**
   - Caches query results, intermediate evidence, and LLM responses to meet latency and cost constraints.
   - (Planned)

5. **Evaluation Framework (Python)**
   - Offline framework for benchmarking retrieval quality, generation accuracy, and orchestration policy performance.
   - (Planned)

## Feature Status Classification

To maintain clarity, all features and components will be classified as follows:

*   **Planned Functionality:** Features that are designed but not yet coded (Current State).
*   **Implemented Functionality:** Features that are fully coded, tested, and integrated.
*   **Experimental Functionality:** Features currently being tested or evaluated in isolation, not yet production-ready.
*   **Future Functionality:** Ideas and roadmap items not yet fully designed or scheduled for the current development phase.

## Modularity and Security

As per our agent directives:
- Retrieval, generation, verification, and orchestration must remain modular.
- Evidence verification is logically independent from answer generation.
- Retrieved documents are treated as untrusted data.
- Prompt injection from documents must not override system-level instructions.
