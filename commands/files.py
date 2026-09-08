from pathlib import Path
from pathlib import Path
import shutil


def execute(command):

    text = command.lower()

    try:

        if text.startswith("create file "):

            filename = command[12:].strip()

            Path(filename).touch()

            return {
                "success": True,
                "message": f"Created file {filename}"
            }

        if text.startswith("create folder "):

            foldername = command[14:].strip()

            Path(foldername).mkdir(
                parents=True,
                exist_ok=True
            )

            return {
                "success": True,
                "message": f"Created folder {foldername}"
            }



        if text.startswith("delete file "):

            filename = command[12:].strip()

            path = Path(filename)

            if not path.exists():
                return {
                    "success": False,
                    "message": "File not found"
                }
            

            path.unlink()
            return {
                "success": True,
                "message": f"Deleted file {filename}"
            }



        if text.startswith("delete folder "):

            foldername = command[14:].strip()

            path = Path(foldername)

            if not path.exists():
                return {
                    "success": False,
                    "message": "Folder not found"
                }

            shutil.rmtree(path)

            return {
                "success": True,
                "message": f"Deleted folder {foldername}"
            }


        if text.startswith("show file "):

            filename = command[10:].strip()

            path = Path(filename)

            if not path.exists():
                return {
                    "success": False,
                    "message": "File not found"
                }

            content = path.read_text()

            return {
                "success": True,
                "message": content
            }
        


        if text.startswith("rename file "):

            remainder = command[12:]

            if " to " not in remainder:

                return {
                    "success": False,
                    "message": "Use: rename file old.txt to new.txt"
                }

            old_name, new_name = remainder.split(
                " to ",
                1
            )

            Path(old_name.strip()).rename(
                new_name.strip()
            )

            return {
                "success": True,
                "message": f"Renamed {old_name} to {new_name}"
            }



        if text.startswith("copy file "):

            remainder = command[10:]

            if " to " not in remainder:

                return {
                    "success": False,
                    "message": "Use: copy file source to destination"
                }

            source, destination = remainder.split(
                " to ",
                1
            )

            shutil.copy2(
                source.strip(),
                destination.strip()
            )

            return {
                "success": True,
                "message": "File copied"
            }





        if text.startswith("move file "):

            remainder = command[10:]

            if " to " not in remainder:

                return {
                    "success": False,
                    "message": "Use: move file source to destination"
                }

            source, destination = remainder.split(
                " to ",
                1
            )

            shutil.move(
                source.strip(),
            destination.strip()
        )

            return {
                "success": True,
                "message": "File moved"
            }





        if text == "list files":

            files = [
                item.name
                for item in Path(".").iterdir()
            ]

            if not files:
                return {
                    "success": True,
                    "message": "No files found"
                }

            return {
                "success": True,
                "message": ", ".join(files)
            }

        return {
            "success": False,
            "message": "Unknown file command"
        }

    except Exception as error:

        return {
            "success": False,
            "message": str(error)
        }