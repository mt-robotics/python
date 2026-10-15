import json
import logging


def load_user_settings(user_id):
    """Load user settings from file, create defaults if missing"""
    filename = f"user_{user_id}.json"

    # TODO: Try to load existing settings
    # If file doesn't exist, return default settings:
    # {"theme": "dark", "notifications": True, "language": "en"}
    # If JSON is corrupted, print error and return defaults
    defaults = {"theme": "dark", "notifications": True, "language": "en"}
    try:
        with open(filename, "r", encoding="utf-8") as f:
            settings = json.load(f)
            return settings
    except FileNotFoundError as e:
        logging.error("File not found: %s", str(e))
        return defaults
    except json.JSONDecodeError as e:
        logging.error("Json Serialization failed: %s", str(e))
        return defaults


def save_user_settings(user_id, settings):
    """Save user settings to file with pretty formatting"""
    filename = f"user_{user_id}.json"

    # TODO: Save settings to file with 2-space indentation
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2)
    except TypeError as e:
        logging.error("Settings contain non-serializable objects: %s", str(e))
        raise
    except OSError as e:
        logging.error("Could not write file: %s", str(e))
        raise


if __name__ == "__main__":
    # Test your functions
    settings = load_user_settings(123)
    settings["theme"] = "light"
    save_user_settings(123, settings)
