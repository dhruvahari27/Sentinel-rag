from abc import ABC, abstractmethod
from typing import Dict, Any
import time

class BaseLLMProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str, system_prompt: str = "") -> Dict[str, Any]:
        """
        Generate a response given a prompt.
        Returns a dict containing 'text', 'latency_ms', and 'tokens'.
        """
        pass

class MockLLMProvider(BaseLLMProvider):
    def generate(self, prompt: str, system_prompt: str = "") -> Dict[str, Any]:
        start = time.time()
        
        # Simple heuristic to pretend to cite things it found
        citations = []
        if "[S1]" in prompt:
            citations.append("[S1]")
            
        answer = "Based on the provided context, here is the answer. "
        if citations:
            answer += f"This is supported by {', '.join(citations)}."
        else:
            answer = "The provided documents do not contain enough information to answer the question."
            
        latency = (time.time() - start) * 1000
        
        return {
            "text": answer,
            "latency_ms": latency,
            "tokens": {"prompt": len(prompt) // 4, "completion": len(answer) // 4, "total": (len(prompt) + len(answer)) // 4},
            "model": "mock-llm-1.0"
        }

def get_llm_provider() -> BaseLLMProvider:
    # In the future, this would check config to return OpenAI, Anthropic, etc.
    return MockLLMProvider()
