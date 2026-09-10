from reasoning.intent_classifier import classify
from reasoning.decision_engine import should_execute

from capabilities.resolver import resolve, check_pending_confirmation


def route_command(user_input):

    pending_result = check_pending_confirmation(user_input)
    if pending_result is not None:
        return pending_result

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
    return resolve(intent, user_input)
