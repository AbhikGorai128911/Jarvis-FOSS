import requests


def is_online():

    try:
        requests.get(
            "https://www.google.com",
            timeout=3
        )
        return True

    except Exception:
        return False