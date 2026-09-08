KNOWN_INTENTS = {
    "system",
    "web",
    "music",
    "time",
    "files",
    "memory",
    "browser",
    "device",
    "communication"
    
}


def should_execute(intent):

    return intent in KNOWN_INTENTS
