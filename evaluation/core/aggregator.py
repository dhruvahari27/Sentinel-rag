import json
import os
import statistics
from typing import Dict, Any, List

def aggregate_results(raw_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Takes the output of runner and calculates aggregate statistics.
    """
    results = raw_results["results"]
    if not results:
        return {}
        
    num_questions = len(results)
    
    # 1. Metrics aggregation
    metrics_keys = list(results[0]["metrics"].keys())
    aggregated_metrics = {}
    
    for k in metrics_keys:
        vals = [r["metrics"][k] for r in results]
        aggregated_metrics[f"Overall {k}"] = sum(vals) / num_questions
        
    # Generation metrics
    gen_keys = list(results[0].get("generation_metrics", {}).keys())
    aggregated_gen_metrics = {}
    for k in gen_keys:
        vals = [r["generation_metrics"][k] for r in results if k in r["generation_metrics"]]
        if vals:
            aggregated_gen_metrics[f"Overall {k}"] = sum(vals) / len(vals)
            
    # Latency aggregation
    latencies = [r["latency_sec"] for r in results]
    latencies.sort()
    
    avg_latency = sum(latencies) / num_questions
    p50_latency = statistics.median(latencies)
    
    p95_index = int(num_questions * 0.95)
    p95_latency = latencies[p95_index] if p95_index < num_questions else latencies[-1]
    
    # Subgroup analysis
    subgroups = {}
    for r in results:
        qtype = r["question_type"]
        if qtype not in subgroups:
            subgroups[qtype] = []
        subgroups[qtype].append(r)
        
    subgroup_metrics = {}
    for qtype, group_results in subgroups.items():
        if len(group_results) < 2:
            continue # Skip groups with too few items
            
        group_agg = {}
        for k in metrics_keys:
            vals = [gr["metrics"][k] for gr in group_results]
            group_agg[k] = sum(vals) / len(vals)
        group_agg["count"] = len(group_results)
        subgroup_metrics[qtype] = group_agg
        
    # Token & cost
    input_tokens = [r.get("tokens", {}).get("input", 0) for r in results]
    output_tokens = [r.get("tokens", {}).get("output", 0) for r in results]
    
    avg_input_tokens = sum(input_tokens) / num_questions
    avg_output_tokens = sum(output_tokens) / num_questions
    
    aggregation = {
        "run_id": raw_results["run_id"],
        "dataset_name": raw_results["dataset_name"],
        "dataset_version": raw_results["dataset_version"],
        "total_questions": num_questions,
        "retrieval_metrics": aggregated_metrics,
        "generation_metrics": aggregated_gen_metrics,
        "latency_metrics": {
            "Average latency": avg_latency,
            "P50 latency": p50_latency,
            "P95 latency": p95_latency
        },
        "token_usage": {
            "Average input tokens": avg_input_tokens,
            "Average output tokens": avg_output_tokens
        },
        "cost": "NOT_MEASURED",
        "subgroup_metrics": subgroup_metrics
    }
    
    agg_path = os.path.join("evaluation", "results", "aggregate", f"{raw_results['run_id']}_agg.json")
    with open(agg_path, "w") as f:
        json.dump(aggregation, f, indent=2)
        
    return aggregation
