import json
import urllib.request
import urllib.error
import socket
from src.llm.base import LLMBackend

class LlamaCppConnectionError(Exception): pass
class LlamaCppTimeoutError(Exception): pass
class LlamaCppMalformedResponseError(Exception): pass

class LlamaCppBackend(LLMBackend):
    def __init__(self, model_name: str, endpoint: str = "http://localhost:8080", generation_params: dict = None):
        self.model_name = model_name
        self.endpoint = endpoint.rstrip('/')
        self.timeout = 120  # Seconds
        self.generation_params = generation_params or {}

    def generate(self, prompt: str) -> str:
        url = f"{self.endpoint}/v1/chat/completions"
        data = {
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            **self.generation_params
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
                # Extract content from openai-compatible response structure
                if "choices" not in response_data or not response_data["choices"]:
                     raise LlamaCppMalformedResponseError("Missing 'choices' in response")
                return response_data["choices"][0]["message"]["content"]
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            raise LlamaCppConnectionError(f"LlamaCpp returned an error (status {e.code}): {error_body}") from e
        except urllib.error.URLError as e:
            if isinstance(e.reason, socket.timeout):
                raise LlamaCppTimeoutError(f"LlamaCpp generation timed out after {self.timeout} seconds") from e
            raise LlamaCppConnectionError(f"LlamaCpp connection failed: {e.reason}") from e
        except (json.JSONDecodeError, KeyError) as e:
            raise LlamaCppMalformedResponseError(f"Failed to process LlamaCpp response: {e}") from e

    def is_available(self) -> bool:
        try:
            # Use /v1/models as a health check
            with urllib.request.urlopen(f"{self.endpoint}/v1/models", timeout=5) as response:
                return response.status == 200
        except (urllib.error.URLError, OSError):
            return False
