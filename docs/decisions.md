# Architecture Decision Records (ADR)

## ADR-001: Why FastAPI
*   **Status**: Accepted
*   **Context**: We need a high-performance, async-capable Python framework for the backend API.
*   **Decision**: Use FastAPI.
*   **Alternatives**: Flask, Django, native asyncio HTTP server.
*   **Trade-offs**: FastAPI provides excellent Pydantic integration and async support out of the box, but may lack some built-in heavy ORM features of Django.
*   **Consequences**: Pydantic schemas will be our standard data validation layer. The system will inherently support async operations, which is crucial for IO-bound LLM and database calls.

## ADR-002: Why PostgreSQL + pgvector
*   **Status**: Accepted
*   **Context**: We need robust relational storage for document metadata and vector storage for embeddings.
*   **Decision**: Use PostgreSQL combined with the `pgvector` extension.
*   **Alternatives**: Separate relational DB (MySQL) + Vector DB (Pinecone, Milvus, Qdrant).
*   **Trade-offs**: Single operational dependency simplifies deployment and allows ACID transactions across metadata and embeddings. `pgvector` may be slightly less performant at massive scale than specialized vector databases, but is sufficient for our scope.
*   **Consequences**: Reduced infrastructure complexity. We can write SQL queries that filter on metadata and similarity in the same transaction.

## ADR-003: Why hybrid retrieval
*   **Status**: Accepted
*   **Context**: Vector search struggles with exact keyword matches and domain-specific acronyms. Lexical search struggles with semantic meaning.
*   **Decision**: Implement Hybrid Retrieval (Vector + BM25).
*   **Alternatives**: Pure vector search or pure BM25 search.
*   **Trade-offs**: Increases ingestion time, index size, and retrieval latency, but significantly boosts recall.
*   **Consequences**: We need a reciprocal rank fusion or normalization mechanism to merge scores from both systems before reranking.

## ADR-004: Why cross-encoder reranking
*   **Status**: Accepted
*   **Context**: Fast bi-encoder retrieval (Vector/BM25) has high recall but lower precision, which can clutter the context window.
*   **Decision**: Use a cross-encoder model to rerank the fused retrieved candidates.
*   **Alternatives**: No reranking, or using an LLM-based reranker (like RankGPT).
*   **Trade-offs**: Cross-encoders add significant computational overhead and latency per query but massively improve top-K precision compared to bi-encoders.
*   **Consequences**: We must enforce strict limits on the number of candidates sent to the reranker to maintain latency budgets.

## ADR-005: Why Redis caching
*   **Status**: Accepted
*   **Context**: RAG systems frequently see repeated queries or require intermediate state tracking for orchestration.
*   **Decision**: Use Redis for caching and fast state management.
*   **Alternatives**: In-memory Python caching, Memcached, Postgres tables.
*   **Trade-offs**: Requires another infrastructure component. However, it provides fast, persistent, scalable key-value storage.
*   **Consequences**: Cache invalidation strategies will need to be carefully designed, especially when underlying documents update.

## ADR-006: Why modular architecture
*   **Status**: Accepted
*   **Context**: RAG systems can easily become monolithic "black boxes".
*   **Decision**: Strictly separate ingestion, retrieval, reranking, orchestration, generation, and verification.
*   **Alternatives**: End-to-end framework implementations (e.g., heavily relying on LangChain's black box abstractions).
*   **Trade-offs**: More boilerplate code upfront, but allows precise observation, unit testing, and isolated upgrades of individual components.
*   **Consequences**: Strong internal API boundaries and clear schema contracts between modules.

## ADR-007: Why deterministic orchestration before learned policy
*   **Status**: Accepted
*   **Context**: The Evidence Orchestrator must make complex routing and retrieval decisions.
*   **Decision**: Implement the policy deterministically using explicit rules and measurable thresholds first.
*   **Alternatives**: Use Reinforcement Learning (RL) or autonomous LLM agents (ReAct) immediately.
*   **Trade-offs**: Deterministic rules are rigid and require manual tuning, but they are predictable, testable, and have zero hallucination risk during orchestration.
*   **Consequences**: We will establish a strong baseline. Advanced agentic behavior will only be introduced if experiments prove the deterministic policy is insufficient.

## ADR-008: Why evidence verification is separate from generation
*   **Status**: Accepted
*   **Context**: LLMs tend to hallucinate or confirm their own biases if asked to generate and verify simultaneously.
*   **Decision**: Separate the generation pipeline from the claim verification pipeline.
*   **Alternatives**: Prompting the generator LLM to "only use the provided text and self-correct."
*   **Trade-offs**: Increases cost and latency due to an extra LLM call, but fundamentally improves reliability and trust metrics.
*   **Consequences**: Requires explicit claim extraction logic and a dedicated verification module that evaluates `SUPPORTED`, `CONTRADICTED`, etc.

## ADR-009: Why documents are treated as untrusted data
*   **Status**: Accepted
*   **Context**: External documents may contain malicious prompt injections or contradictory data.
*   **Decision**: Treat all retrieved documents as untrusted user input.
*   **Alternatives**: Blindly appending document content into system prompts.
*   **Trade-offs**: Requires defensive prompt engineering, explicit delimiters, and robust parsing, slightly complicating prompt design.
*   **Consequences**: Prompt injections from documents must not override system-level instructions.

## ADR-010: Why evaluation is built alongside the application
*   **Status**: Accepted
*   **Context**: It is impossible to know if orchestration improves the system without quantitative baselines.
*   **Decision**: The project must be evaluation-driven from Phase 0, building a custom benchmark dataset and evaluation framework in parallel with the application.
*   **Alternatives**: Build the app first, evaluate later via vibe-checks or external tools.
*   **Trade-offs**: Slows initial feature delivery but guarantees measurable progress and prevents regression.
*   **Consequences**: Every architectural change or orchestration rule tuning must be validated against the evaluation suite. No benchmark number may be fabricated.

## ADR-011: Why PostgreSQL + pgvector + Redis for Development Infrastructure
*   **Status**: Accepted
*   **Context**: We need to establish a local development environment for SENTINEL-RAG Phase 2 that mirrors our target production capabilities.
*   **Decision**: Use PostgreSQL (with pgvector) and Redis via Docker Compose.
*   **Alternatives**: SQLite/DuckDB for local development, or cloud-hosted DBs.
*   **Trade-offs**: Docker Compose introduces a dependency on Docker for local development, which can be heavy. However, it ensures parity with production architectures, avoids the limitations of local file-based databases (like SQLite's lack of pgvector), and removes network latency/costs of cloud DBs.
*   **Consequences**: Developers must run `docker compose up -d` before starting the application locally. Database connection strings are managed via environment variables.