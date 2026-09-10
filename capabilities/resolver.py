"""
capabilities/resolver.py

Resolves a classified intent + raw user input into a structured request.
This module performs NO execution. It only validates input and produces
a structured dict describing what a downstream client app should do.
"""

import hashlib
import time
import urllib.request
import urllib.parse
import json

_PENDING_CONFIRMATION = None

_AFFIRMATIVE = {"yes", "y", "yeah", "yep", "sure", "ok", "okay"}


def _is_affirmative(text):
    return text.strip().lower() in _AFFIRMATIVE


def check_pending_confirmation(user_input):
    global _PENDING_CONFIRMATION

    if _PENDING_CONFIRMATION is None:
        return None

    pending = _PENDING_CONFIRMATION
    _PENDING_CONFIRMATION = None  # one-shot: cleared whether used or not

    if _is_affirmative(user_input):
        return {
            "intent": pending["intent"],
            "value": pending["value"],
            "confirmation_code": pending["token"],
            "success": True
        }

    return None


def _make_confirmation_code(intent, value):
    payload = f"{intent}|{value}|{time.time()}"
    digest = hashlib.sha256(payload.encode()).hexdigest()[:8]
    return f"{intent}-{digest}"


def _resolve_files(text, original_input):
    action = "create" if "create" in text else "list"

    path = None
    original_tokens = original_input.split()
    for token in original_tokens:
        lower_token = token.lower()
        if lower_token.startswith("~") or lower_token.startswith("/") or lower_token.startswith("."):
            path = token
            break

    if path is None:
        return {
            "intent": "files",
            "value": None,
            "confirmation_code": None,
            "success": False,
            "message": "Missing required parameter: path"
        }

    value = {"action": action, "path": path}
    return {
        "intent": "files",
        "value": value,
        "confirmation_code": _make_confirmation_code("files", value),
        "success": True
    }


def _resolve_device(text):
    if "torch" in text or "flashlight" in text:
        device, state = "torch", "on"
    elif "battery" in text:
        device, state = "battery", None
    elif "bluetooth" in text:
        device, state = "bluetooth", None
    elif "wifi" in text:
        device, state = "wifi", None
    elif "volume" in text:
        device, state = "volume", None
    else:
        return {
            "intent": "device",
            "value": None,
            "confirmation_code": None,
            "success": False,
            "message": "Unsupported device command"
        }

    value = {"device": device, "state": state}
    return {
        "intent": "device",
        "value": value,
        "confirmation_code": _make_confirmation_code("device", value),
        "success": True
    }


def _resolve_time(text):
    value = {"query": "current_time"}
    return {
        "intent": "time",
        "value": value,
        "confirmation_code": _make_confirmation_code("time", value),
        "success": True
    }


def _resolve_communication(text, original_input):
    global _PENDING_CONFIRMATION

    if "call" in text or "dial" in text:
        action = "call"
        trigger = "call" if "call" in text else "dial"
    elif "text" in text or "sms" in text or "message" in text:
        action = "text"
        trigger = None
        for word in ["text", "sms", "message"]:
            if word in text:
                trigger = word
                break
    else:
        return {
            "intent": "communication",
            "value": None,
            "confirmation_code": None,
            "success": False,
            "message": "Could not determine communication action"
        }

    lower_tokens = text.split()
    original_tokens = original_input.split()
    target = None
    if trigger in lower_tokens:
        idx = lower_tokens.index(trigger)
        if idx + 1 < len(original_tokens):
            target = " ".join(original_tokens[idx + 1:])

    if target is None:
        return {
            "intent": "communication",
            "value": None,
            "confirmation_code": None,
            "success": False,
            "message": "Missing required parameter: target"
        }

    value = {"action": action, "target": target}
    code = _make_confirmation_code("communication", value)
    _PENDING_CONFIRMATION = {"token": code, "intent": "communication", "value": value}

    return {
        "intent": "communication",
        "value": None,
        "confirmation_code": code,
        "success": True,
        "requires_confirmation": True,
        "message": f"{action.capitalize()} {target}? (yes/no)"
    }


def _resolve_web(text, original_input):
    global _PENDING_CONFIRMATION

    query = original_input.strip()

    if not query:
        return {
            "intent": "web",
            "value": None,
            "confirmation_code": None,
            "success": False,
            "message": "Missing required parameter: query"
        }

    params = urllib.parse.urlencode({
        "q": query,
        "format": "json",
        "no_html": "1",
        "skip_disambig": "1"
    })
    url = f"https://api.duckduckgo.com/?{params}"

    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            data = json.loads(response.read().decode())
    except Exception as e:
        return {
            "intent": "web",
            "value": None,
            "confirmation_code": None,
            "success": False,
            "message": f"Web search failed: {e}"
        }

    summary = data.get("AbstractText", "").strip()

    if not summary:
        value = {"query": query, "result": None}
        return {
            "intent": "web",
            "value": value,
            "confirmation_code": _make_confirmation_code("web", value),
            "success": True,
            "message": "No summary found for this query."
        }

    value = {"query": query, "result": summary}
    code = _make_confirmation_code("web", value)

    browser_value = {"query": query}
    _PENDING_CONFIRMATION = {
        "token": code,
        "intent": "browser",
        "value": browser_value
    }

    return {
        "intent": "web",
        "value": value,
        "confirmation_code": code,
        "success": True,
        "requires_confirmation": True,
        "message": "Want a visual look? (yes/no)"
    }


def _resolve_system(text, original_input):
    global _PENDING_CONFIRMATION

    if "poweroff" in text or "power off" in text or "shutdown" in text:
        action = "poweroff"
    elif "restart" in text or "reboot" in text:
        action = "restart"
    else:
        action = None

    if action is not None:
        value = {"action": action}
        code = _make_confirmation_code("system", value)
        _PENDING_CONFIRMATION = {
            "token": code,
            "intent": "system",
            "value": value
        }
        return {
            "intent": "system",
            "value": None,
            "confirmation_code": code,
            "success": True,
            "requires_confirmation": True,
            "message": f"{action.capitalize()} the device? (yes/no)"
        }

    trigger = None
    for word in ["open", "launch", "start"]:
        if word in text:
            trigger = word
            break

    if trigger is None:
        return {
            "intent": "system",
            "value": None,
            "confirmation_code": None,
            "success": False,
            "message": "Could not determine system command"
        }

    lower_tokens = text.split()
    original_tokens = original_input.split()
    target = None
    if trigger in lower_tokens:
        idx = lower_tokens.index(trigger)
        if idx + 1 < len(original_tokens):
            target = " ".join(original_tokens[idx + 1:])

    if target is None:
        return {
            "intent": "system",
            "value": None,
            "confirmation_code": None,
            "success": False,
            "message": "Missing required parameter: target"
        }

    value = {"action": "open", "target": target}
    return {
        "intent": "system",
        "value": value,
        "confirmation_code": _make_confirmation_code("system", value),
        "success": True
    }


def _resolve_memory(text, original_input):
    if text.startswith("remember"):
        remainder = original_input[len("remember"):].strip()
        if remainder.lower().startswith("that "):
            remainder = remainder[5:].strip()

        lower_remainder = remainder.lower()
        idx = lower_remainder.find(" is ")

        if idx == -1:
            return {
                "intent": "memory",
                "value": None,
                "confirmation_code": None,
                "success": False,
                "message": "Missing required parameter: expected format "
                            "'remember <key> is <value>'"
            }

        key = remainder[:idx].strip()
        content = remainder[idx + 4:].strip()

        if not key or not content:
            return {
                "intent": "memory",
                "value": None,
                "confirmation_code": None,
                "success": False,
                "message": "Missing required parameter: key or value is empty"
            }

        value = {"action": "store", "key": key, "content": content}
        return {
            "intent": "memory",
            "value": value,
            "confirmation_code": _make_confirmation_code("memory", value),
            "success": True
        }

    if text.startswith("what is"):
        topic = original_input[len("what is"):].strip()

        if not topic:
            return {
                "intent": "memory",
                "value": None,
                "confirmation_code": None,
                "success": False,
                "message": "Missing required parameter: topic"
            }

        value = {"action": "recall", "topic": topic}
        return {
            "intent": "memory",
            "value": value,
            "confirmation_code": _make_confirmation_code("memory", value),
            "success": True
        }

    return {
        "intent": "memory",
        "value": None,
        "confirmation_code": None,
        "success": False,
        "message": "Could not determine memory action"
    }


_RESOLVERS = {
    "files": _resolve_files,
    "device": _resolve_device,
    "time": _resolve_time,
    "communication": _resolve_communication,
    "web": _resolve_web,
    "system": _resolve_system,
    "memory": _resolve_memory,
}


def resolve(intent, user_input):
    text = user_input.lower()

    resolver_fn = _RESOLVERS.get(intent)
    if resolver_fn is None:
        return {
            "intent": intent,
            "value": None,
            "confirmation_code": None,
            "success": False,
            "message": f"No resolver implemented for intent '{intent}'"
        }

    if intent == "files":
        return resolver_fn(text, user_input)

    if intent == "communication":
        return resolver_fn(text, user_input)

    if intent == "web":
        return resolver_fn(text, user_input)

    if intent == "system":
        return resolver_fn(text, user_input)

    if intent == "memory":
        return resolver_fn(text, user_input)

    return resolver_fn(text)
