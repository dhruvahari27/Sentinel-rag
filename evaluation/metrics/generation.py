from typing import Dict, Any, List

def evaluate_citation_coverage(answer_text: str, citations: List[Dict[str, Any]]) -> float:
    """
    Very basic deterministic citation coverage.
    Checks if the answer contains citation markers and if those markers
    map to the provided citations.
    Returns 1.0 if all provided citations are used in the text.
    """
    if not citations:
        return 0.0
        
    used_citations = 0
    for citation in citations:
        cid = citation.get("citation_id", "")
        # Look for [S1], [S2] etc.
        if f"[{cid}]" in answer_text:
            used_citations += 1
            
    return used_citations / len(citations)


def evaluate_exact_match_correctness(generated_answer: str, expected_answer: str) -> float:
    """
    Evaluates correctness using simple string matching (case-insensitive).
    Returns 1.0 if expected_answer is in generated_answer.
    This is highly deterministic but limited for complex RAG answers.
    """
    if not expected_answer:
        return 0.0
        
    if expected_answer.lower().strip() in generated_answer.lower().strip():
        return 1.0
    return 0.0
