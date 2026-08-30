from typing import List, Dict, Any, Tuple
from app.schemas.retrieval import RetrievalChunk

class ContextBuilder:
    def build_context(self, chunks: List[RetrievalChunk]) -> Tuple[str, Dict[str, RetrievalChunk]]:
        """
        Constructs a string context for the LLM and a mapping of citation IDs to chunks.
        Returns:
            context_string: The formatted context.
            citation_map: Dict mapping citation ID (e.g., 'S1') to the RetrievalChunk.
        """
        context_parts = []
        citation_map = {}
        
        for i, chunk in enumerate(chunks, 1):
            citation_id = f"S{i}"
            citation_map[citation_id] = chunk
            
            # Format according to the spec
            part = f"[{citation_id}]\n"
            part += f"Document ID: {chunk.document_id}\n"
            if "chunk_index" in chunk.metadata:
                part += f"Chunk Index: {chunk.metadata['chunk_index']}\n"
            part += f"Text:\n{chunk.text}\n"
            
            context_parts.append(part)
            
        return "\n".join(context_parts), citation_map
