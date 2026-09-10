import sys
import json
import argparse
import memory.memory as memory
from core.router import route_command
from src.core.config_loader import load_llm_backend

MEMORY_LIMIT = 4  # number of recent messages (not turns) to include as context

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

    memory.initialize()

    print("Jarvis-FOSS ready. Type 'exit' to quit.")
    while True:
        user_input = input("> ").strip()
        if user_input.lower() == "exit":
            break

        # Pass-through router
        result = route_command(user_input)

        if result.get("llm_candidate"):
            try:
                history = memory.get_recent_messages(limit=MEMORY_LIMIT)
                history.reverse()
                context_str = "\n".join(f"{speaker}: {msg}" for speaker, msg in history)
                if context_str:
                    prompt = f"{context_str}\nuser: {user_input}"
                else:
                    prompt = user_input

                response = backend.generate(prompt)

                memory.save_message("user", user_input)
                memory.save_message("assistant", response)

                print(json.dumps({
                    "intent": result.get("intent", "unknown"),
                    "llm_input": user_input,
                    "llm_output": response
                }, indent=2))
            except Exception as e:
                print(f"Error generating response: {e}")
        else:
            print(f"Command result: {result}")

if __name__ == "__main__":
    main()
