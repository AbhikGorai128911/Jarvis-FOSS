import sys
import argparse
from core.router import route_command
from src.core.config_loader import load_llm_backend

def main():
    parser = argparse.ArgumentParser(description="Jarvis-FOSS CLI")
    parser.add_argument("--config", default="config/llm.json", help="Path to llm config file")
    args = parser.parse_args()

    try:
        backend = load_llm_backend(args.config)
    except Exception as e:
        print(f"Error loading configuration: {e}")
        sys.exit(1)

    if not backend.is_available():
        print("Error: LLM backend is not available.")
        sys.exit(1)

    print("Jarvis-FOSS ready. Type 'exit' to quit.")
    while True:
        user_input = input("> ").strip()
        if user_input.lower() == "exit":
            break

        # Pass-through router
        result = route_command(user_input)

        if result.get("llm_candidate"):
            try:
                response = backend.generate(user_input)
                print(response)
            except Exception as e:
                print(f"Error generating response: {e}")
        else:
            print(f"Command result: {result}")

if __name__ == "__main__":
    main()
