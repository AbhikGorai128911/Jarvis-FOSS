from reasoning.intent_classifier import classify
from reasoning.decision_engine import should_execute

from capabilities.executor import execute


def route_command(user_input):

    intent = classify(user_input)

    #
    # UNKNOWN → LLM candidate
    #
    if intent == "unknown":
        return {
            "success": False,
            "llm_candidate": True,
            "message": "This may require deeper reasoning."
        }

    #
    # blocked intents
    #
    if not should_execute(intent):
        return {
            "success": False,
            "message": "I cannot execute that command."
        }

    #
    # normal execution
    #
    return execute(intent)
