import json
from typing import Dict, Any

def validate_dataset(dataset_path: str) -> Dict[str, Any]:
    """
    Validates that the dataset adheres to the required schema.
    Raises ValueError if invalid.
    Returns the loaded dataset.
    """
    with open(dataset_path, "r") as f:
        data = json.load(f)
        
    required_meta = ["version", "dataset_name", "questions"]
    for k in required_meta:
        if k not in data:
            raise ValueError(f"Dataset missing required metadata field: {k}")
            
    questions = data["questions"]
    if not questions:
        raise ValueError("Dataset has no questions.")
        
    seen_ids = set()
    for q in questions:
        if "id" not in q or not q["id"]:
            raise ValueError("Question missing valid ID.")
        if q["id"] in seen_ids:
            raise ValueError(f"Duplicate question ID: {q['id']}")
        seen_ids.add(q["id"])
        
        if "question" not in q or not q["question"].strip():
            raise ValueError(f"Question {q['id']} has empty question text.")
            
        if "answerable" not in q:
            raise ValueError(f"Question {q['id']} missing 'answerable' flag.")
            
        if "relevant_document_ids" not in q and "relevant_chunk_ids" not in q:
            raise ValueError(f"Question {q['id']} missing relevant item arrays.")
            
    return data
