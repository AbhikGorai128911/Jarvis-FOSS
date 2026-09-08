from src.llm.base import LLMBackend

class MockLLMBackend(LLMBackend):
    def __init__(self, model_name: str = "mock-model", endpoint: str = "mock", generation_params: dict = None):
        self.model_name = model_name

    def generate(self, prompt: str) -> str:
        return f"[MOCK RESPONSE to: {prompt}]"

    def is_available(self) -> bool:
        return True
