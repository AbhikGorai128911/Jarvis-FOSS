import json
import urllib.request
import urllib.error
import socket
from src.llm.base import LLMBackend

class OllamaBackend(LLMBackend):
    def __init__(self, model_name: str, endpoint: str = "http://localhost:11434", generation_params: dict = None):
        self.model_name = model_name
        self.endpoint = endpoint.rstrip('/')
        self.timeout = 120  # Seconds
        self.generation_params = generation_params or {}

    def generate(self, prompt: str) -> str:
        url = f"{self.endpoint}/api/generate"
        data = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": self.generation_params
        }
        encoded_data = json.dumps(data).encode('utf-8')
        
        req = urllib.request.Request(
            url, 
            data=encoded_data, 
            headers={'Content-Type': 'application/json'}
        )
        
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                response_data = json.loads(response.read().decode('utf-8'))
                return response_data.get("response", "")
        except urllib.error.HTTPError as e:
            raise Exception(f"Ollama returned an error (status {e.code}): {e.read().decode('utf-8')}") from e
        except urllib.error.URLError as e:
            if isinstance(e.reason, socket.timeout):
                raise Exception(f"Ollama generation timed out after {self.timeout} seconds") from e
            raise Exception(f"Ollama connection failed: {e.reason}") from e
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to decode Ollama response: {e}") from e

    def is_available(self) -> bool:
        try:
            # Simple ping to base endpoint
            with urllib.request.urlopen(self.endpoint, timeout=5) as response:
                return response.status == 200
        except (urllib.error.URLError, OSError):
            return False
