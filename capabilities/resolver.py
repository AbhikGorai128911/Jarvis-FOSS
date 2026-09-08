from capabilities.capabilities import CAPABILITIES


def resolve(intent, text):
    text = text.lower()

    # DEVICE INTENT ONLY FOR NOW
    if intent != "device":
        return None

    if "torch" in text or "flashlight" in text:
        return ("torch", "on")

    if "battery" in text:
        return ("battery", None)

    if "bluetooth" in text:
        return ("bluetooth", None)

    if "wifi" in text:
        return ("wifi", None)

    if "volume" in text:
        return ("volume", None)

    return ("unsupported", None)
