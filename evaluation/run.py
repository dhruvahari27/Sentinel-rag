import argparse
import sys
import os
import logging
import json

# Add backend to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../backend'))

from evaluation.core.runner import EvaluationRunner
from evaluation.core.aggregator import aggregate_results
from evaluation.core.reporter import generate_report
from evaluation.run_baseline import setup_corpus
from app.db.session import SessionLocal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="SENTINEL-RAG Evaluation Framework")
    parser.add_argument("--config", type=str, required=True, help="Path to evaluation config JSON")
    parser.add_argument("--setup-corpus", action="store_true", help="Populate the database with the synthetic 5-doc corpus before running")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.config):
        logger.error(f"Config file not found: {args.config}")
        sys.exit(1)
        
    if args.setup_corpus:
        logger.info("Setting up synthetic corpus...")
        db = SessionLocal()
        setup_corpus(db)
        db.close()
        
    logger.info(f"Loading configuration from {args.config}")
    runner = EvaluationRunner(args.config)
    
    raw_results = runner.run()
    
    logger.info("Aggregating results...")
    agg_results = aggregate_results(raw_results)
    
    run_id = raw_results["run_id"]
    report_path = os.path.join("evaluation", "reports", f"{run_id}_report.md")
    
    logger.info(f"Generating report at {report_path}...")
    generate_report(agg_results, raw_results, report_path)
    
    logger.info("Evaluation complete. Key metrics:")
    for k, v in agg_results.get("retrieval_metrics", {}).items():
        logger.info(f"  {k}: {v:.4f}")
        
if __name__ == "__main__":
    main()
