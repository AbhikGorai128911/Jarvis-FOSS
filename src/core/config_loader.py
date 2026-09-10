import json
import os
from src.llm.llamacpp_backend import LlamaCppBackend
from src.llm.mock_backend import MockLLMBackend

# Registry of supported backends
BACKEND_REGISTRY = {
    "llamacpp": LlamaCppBackend,
    "mock": MockLLMBackend
}

def load_llm_backend(config_path: str):
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(config_path, 'r') as f:
        try:
            config = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse configuration JSON: {e}")

    backend_type = config.get("backend")
    if backend_type not in BACKEND_REGISTRY:
        raise ValueError(f"Unsupported backend type: '{backend_type}'. Supported: {list(BACKEND_REGISTRY.keys())}")

    backend_class = BACKEND_REGISTRY[backend_type]
    
    # Instantiate backend
    return backend_class(
        model_name=config["model_name"],
        endpoint=config.get("endpoint", "http://localhost:11434"),
        generation_params=config.get("generation_params")
    )
