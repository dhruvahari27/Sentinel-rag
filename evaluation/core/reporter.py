import os
import json
from typing import Dict, Any

def generate_report(agg_results: Dict[str, Any], raw_results: Dict[str, Any], output_path: str):
    """
    Generates a Markdown report and simple console output.
    """
    config = raw_results["config"]
    
    md_content = f"""# Benchmark Report: {agg_results['run_id']}

## 1. Dataset
- **Name**: {agg_results['dataset_name']}
- **Version**: {agg_results['dataset_version']}
- **Size**: {agg_results['total_questions']} questions

## 2. Configuration
- **Retriever**: {config.get('retriever', 'unknown')}
- **Embedding Model**: {config.get('embedding_model', 'unknown')}
- **Chunking Strategy**: {config.get('chunking_strategy', 'unknown')}

## 3. Retrieval Metrics
"""
    for k, v in agg_results["retrieval_metrics"].items():
        md_content += f"- **{k}**: {v:.4f}\n"
        
    md_content += "\n## 4. Generation Metrics\n"
    if not agg_results["generation_metrics"]:
        md_content += "*Generation not evaluated.*\n"
    else:
        for k, v in agg_results["generation_metrics"].items():
            md_content += f"- **{k}**: {v:.4f}\n"
            
    md_content += "\n## 5. Latency\n"
    for k, v in agg_results["latency_metrics"].items():
        md_content += f"- **{k}**: {v:.4f} sec\n"
        
    md_content += "\n## 6. Token Usage\n"
    for k, v in agg_results["token_usage"].items():
        if v == 0:
             md_content += f"- **{k}**: NOT_AVAILABLE\n"
        else:
             md_content += f"- **{k}**: {v:.1f}\n"
             
    md_content += f"\n## 7. Cost\n- {agg_results['cost']}\n"
    
    md_content += "\n## 8. Failure Analysis\n"
    md_content += "*Failure analysis categorization not yet fully implemented.*\n"
    
    md_content += "\n## 9. Per-category performance\n"
    if not agg_results["subgroup_metrics"]:
        md_content += "*Not enough data for subgroups.*\n"
    else:
        for cat, mets in agg_results["subgroup_metrics"].items():
            md_content += f"\n### {cat} (Count: {mets['count']})\n"
            for mk, mv in mets.items():
                if mk != "count":
                    md_content += f"- **{mk}**: {mv:.4f}\n"
                    
    md_content += "\n## 10. Limitations\n"
    md_content += "- Mock embeddings currently yield random ordering since all chunks output parallel vectors.\n"
    md_content += "- Token counting uses basic heuristics without a live LLM tokenizer.\n"

    with open(output_path, "w") as f:
        f.write(md_content)
