from memory.memory import remember
from memory.memory import recall


def execute(command):

    text = command.lower().strip()

    try:

        if text.startswith("remember "):

            content = command[9:].strip()

            if " is " not in content:

                return {
                    "success": False,
                    "message": "Use: remember key is value"
                }

            key, value = content.split(" is ", 1)

            key = key.strip().lower()
            value = value.strip()

            remember(key, value)

            return {
                "success": True,
                "message": f"I will remember that {key} is {value}"
            }

        if text.startswith("what is "):

            key = command[8:].strip().lower()

            value = recall(key)

            if value:

                return {
                    "success": True,
                    "message": f"{key} is {value}"
                }

            return {
                "success": False,
                "message": f"I don't know what {key} is"
            }

        return {
            "success": False,
            "message": "Unknown memory command"
        }

    except Exception as error:

        return {
            "success": False,
            "message": str(error)
        }