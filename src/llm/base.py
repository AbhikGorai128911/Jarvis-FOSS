from abc import ABC, abstractmethod

class LLMBackend(ABC):
    """
    Abstract base class for all LLM backend implementations.
    """

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """
        Sends a prompt to the LLM backend and returns the generated text.

        Raises:
            Exception: If the backend is unreachable, the model is missing,
                       or generation fails. Implementations MUST raise
                       specific exceptions corresponding to these failure modes.
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """
        Performs a lightweight check to determine if the backend is ready
        to process requests.

        Returns:
            bool: True if the backend is available, False otherwise.
        """
        pass
