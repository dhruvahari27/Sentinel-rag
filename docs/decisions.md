# Architecture Decision Records (ADRs)

This document logs significant architectural decisions made during the development of SENTINEL-RAG.

## Decision 1: Foundation Tech Stack
**Date:** 2026-08-29
**Status:** Accepted

**Context:** The project requires a robust, production-oriented RAG system.
**Decision:** We will use Python/FastAPI for the backend, PostgreSQL/pgvector for storage and vector search, BM25 for lexical search, Redis for caching, and Next.js/TypeScript for the frontend.
**Consequences:** This stack provides a balance of performance, ecosystem maturity, and developer familiarity. PostgreSQL handles both relational data and vectors, reducing the number of moving parts compared to a standalone vector database.
