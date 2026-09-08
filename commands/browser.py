import webbrowser
from urllib.parse import quote_plus


SITES = {
    "youtube": "https://youtube.com",
    "github": "https://github.com",
    "reddit": "https://reddit.com",
    "chatgpt": "https://chatgpt.com",
    "google": "https://google.com",
    "wikipedia": "https://wikipedia.org",
    "stackoverflow": "https://stackoverflow.com",
}


def execute(command):

    text = command.lower().strip()

    try:

        # Open known websites
        if text.startswith("open "):

            site = text[5:].strip()

            if site in SITES:

                webbrowser.open(
                    SITES[site]
                )

                return {
                    "success": True,
                    "message": f"Opening {site}"
                }

        # Google Search
        if text.startswith("search google for "):

            query = quote_plus(
                command[18:].strip()
            )

            webbrowser.open(
                f"https://www.google.com/search?q={query}"
            )

            return {
                "success": True,
                "message": "Searching Google"
            }

        # YouTube Search
        if text.startswith("search youtube for "):

            query = quote_plus(
                command[19:].strip()
            )

            webbrowser.open(
                f"https://www.youtube.com/results?search_query={query}"
            )

            return {
                "success": True,
                "message": "Searching YouTube"
            }

        # GitHub Search
        if text.startswith("search github for "):

            query = quote_plus(
                command[18:].strip()
            )

            webbrowser.open(
                f"https://github.com/search?q={query}"
            )

            return {
                "success": True,
                "message": "Searching GitHub"
            }

        return {
            "success": False,
            "message": "Browser command not recognized"
        }

    except Exception as error:

        return {
            "success": False,
            "message": str(error)
        }