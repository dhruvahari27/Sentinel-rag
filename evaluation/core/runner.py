import os
import time
import json
import uuid
import datetime
import logging
from typing import Dict, Any

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.services.retrieval.vector import VectorRetriever
from app.services.embeddings.provider import get_embedding_provider
from app.services.rag.service import BaselineRAGService
from app.services.generation.llm import get_llm_provider
from app.schemas.retrieval import QueryRequest

from evaluation.core.validator import validate_dataset
from evaluation.metrics.retrieval import calculate_recall_at_k, calculate_precision_at_k, calculate_mrr
from evaluation.metrics.generation import evaluate_citation_coverage, evaluate_exact_match_correctness

logger = logging.getLogger(__name__)

class EvaluationRunner:
    def __init__(self, config_path: str):
        with open(config_path, "r") as f:
            self.config = json.load(f)
            
        self.dataset = validate_dataset(self.config["dataset"])
        self.db: Session = SessionLocal()
        
        self.emb_provider = get_embedding_provider()
        self.llm_provider = get_llm_provider()
        self.retriever = VectorRetriever(self.db, self.emb_provider)
        self.rag_service = BaselineRAGService(self.retriever, self.llm_provider)
        
    def __del__(self):
        self.db.close()
        
    def run(self) -> Dict[str, Any]:
        run_id = f"{self.config['run_name']}_{datetime.datetime.now().strftime('%Y_%m_%d_%H%M%S')}"
        logger.info(f"Starting evaluation run: {run_id}")
        
        questions = self.dataset["questions"]
        top_k_list = self.config.get("top_k_evaluations", [3, 5, 10])
        max_k = max(top_k_list)
        
        query_results = []
        
        for q in questions:
            q_id = q["id"]
            question_text = q["question"]
            relevant_docs = set(q.get("relevant_document_ids", []))
            # If relevant_chunks exist, use them. For now, baseline uses document-level relevance
            # because we only know the document IDs in our mock setup.
            
            # 1. Measure Retrieval Latency
            start_retrieval = time.time()
            retrieved_chunks = self.retriever.retrieve(question_text, top_k=max_k)
            retrieval_latency = time.time() - start_retrieval
            
            # Fetch document filenames for retrieved chunks
            doc_ids = [c.document_id for c in retrieved_chunks]
            doc_map = {}
            if doc_ids:
                from app.models.document import Document
                docs = self.db.query(Document).filter(Document.id.in_(doc_ids)).all()
                doc_map = {d.id: d.filename for d in docs}
                
            retrieved_doc_filenames = [doc_map.get(c.document_id, c.document_id) for c in retrieved_chunks]
            
            # Compute Retrieval Metrics
            metrics = {
                "MRR": calculate_mrr(retrieved_doc_filenames, relevant_docs)
            }
            for k in top_k_list:
                metrics[f"Recall@{k}"] = calculate_recall_at_k(retrieved_doc_filenames, relevant_docs, k)
                metrics[f"Precision@{k}"] = calculate_precision_at_k(retrieved_doc_filenames, relevant_docs, k)
                
            # 2. Measure Generation (if configured)
            generation_metrics = {}
            total_latency = retrieval_latency
            answer_data = None
            tokens = {"input": 0, "output": 0}
            
            if self.config.get("evaluate_generation", False):
                req = QueryRequest(question=question_text, top_k=max_k, retriever_type=self.config["retriever"])
                start_rag = time.time()
                ans_resp = self.rag_service.answer_question(req)
                rag_latency = time.time() - start_rag
                total_latency = rag_latency
                
                answer_data = ans_resp.answer
                tokens = ans_resp.tokens
                
                # Generation Metrics
                citation_dicts = [c.model_dump() for c in ans_resp.citations]
                cov = evaluate_citation_coverage(answer_data, citation_dicts)
                generation_metrics["citation_coverage"] = cov
                
                if "expected_answer" in q:
                    corr = evaluate_exact_match_correctness(answer_data, q["expected_answer"])
                    generation_metrics["exact_correctness"] = corr
                    
            query_results.append({
                "question_id": q_id,
                "question": question_text,
                "question_type": q.get("question_type", "unknown"),
                "difficulty": q.get("difficulty", "unknown"),
                "retrieved_results": [{"doc_id": c.document_id, "score": c.score} for c in retrieved_chunks],
                "relevant_documents": list(relevant_docs),
                "metrics": metrics,
                "generation_metrics": generation_metrics,
                "generated_answer": answer_data,
                "latency_sec": total_latency,
                "tokens": tokens
            })
            
        result = {
            "run_id": run_id,
            "timestamp": datetime.datetime.now().isoformat(),
            "config": self.config,
            "dataset_version": self.dataset["version"],
            "dataset_name": self.dataset["dataset_name"],
            "total_questions": len(questions),
            "results": query_results
        }
        
        # Save raw results
        raw_path = os.path.join("evaluation", "results", "raw", f"{run_id}.json")
        with open(raw_path, "w") as f:
            json.dump(result, f, indent=2)
            
        logger.info(f"Saved raw results to {raw_path}")
        return result
