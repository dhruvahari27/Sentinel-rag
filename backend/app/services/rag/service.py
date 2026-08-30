import time
import uuid
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from app.schemas.retrieval import QueryRequest, QueryResponse, Citation, RetrievalInfo
from app.services.retrieval.base import BaseRetriever
from app.services.generation.context import ContextBuilder
from app.services.generation.llm import BaseLLMProvider

class BaselineRAGService:
    def __init__(self, retriever: BaseRetriever, llm_provider: BaseLLMProvider):
        self.retriever = retriever
        self.llm = llm_provider
        self.context_builder = ContextBuilder()
        
    def answer_question(self, request: QueryRequest) -> QueryResponse:
        start_time = time.time()
        
        # 1. Retrieval
        retrieval_start = time.time()
        chunks = self.retriever.retrieve(request.question, top_k=request.top_k)
        retrieval_latency = (time.time() - retrieval_start) * 1000
        
        # Empty retrieval guard
        if not chunks:
            return QueryResponse(
                request_id=str(uuid.uuid4()),
                question=request.question,
                answer="I'm sorry, I couldn't find any relevant documents to answer your question.",
                citations=[],
                retrieval=RetrievalInfo(top_k=request.top_k, results=[], latency_ms=retrieval_latency),
                total_latency_ms=(time.time() - start_time) * 1000,
                tokens={},
                model="baseline-rag"
            )
        
        # 2. Context Construction
        context_str, citation_map = self.context_builder.build_context(chunks)
        
        # 3. Grounding Prompt
        system_prompt = (
            "You are a helpful assistant. Use the following context to answer the user's question.\n"
            "Rules:\n"
            "1. Answer using ONLY the supplied context.\n"
            "2. Do not invent information.\n"
            "3. Cite source identifiers provided by the application (e.g. [S1], [S2]).\n"
            "4. If the context does not contain enough information, state that explicitly.\n\n"
            f"CONTEXT:\n{context_str}"
        )
        
        # 4. LLM Generation
        llm_response = self.llm.generate(prompt=request.question, system_prompt=system_prompt)
        answer_text = llm_response["text"]
        
        # 5. Citation Mapping
        citations = []
        for citation_id, chunk in citation_map.items():
            # Only include citations actually used by the LLM (simple substring check for baseline)
            if f"[{citation_id}]" in answer_text:
                citations.append(
                    Citation(
                        citation_id=citation_id,
                        document_id=chunk.document_id,
                        chunk_id=chunk.id,
                        text_snippet=chunk.text[:100] + "..." # snippet for transparency
                    )
                )
                
        total_latency = (time.time() - start_time) * 1000
        
        return QueryResponse(
            request_id=str(uuid.uuid4()),
            question=request.question,
            answer=answer_text,
            citations=citations,
            retrieval=RetrievalInfo(top_k=request.top_k, results=chunks, latency_ms=retrieval_latency),
            total_latency_ms=total_latency,
            tokens=llm_response.get("tokens", {}),
            model=llm_response.get("model", "unknown")
        )
