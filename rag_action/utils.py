import json
import logging
import os
from typing import Dict, Optional


# LOG_FORMAT = "%(name)-25s %(levelname)-7s %(message)s"
LOG_FORMAT = "%(message)s"


LOG_LEVELS = {
    "error": logging.ERROR,
    "warning": logging.WARNING,
    "info": logging.INFO,
    "debug": logging.DEBUG,
}


def setup_logger() -> None:
    log_level = os.getenv("LOG_LEVEL", "info").lower()
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("langsmith.utils").setLevel(logging.ERROR)
    logging.basicConfig(
        level=LOG_LEVELS.get(log_level, logging.INFO), format=LOG_FORMAT
    )


def introduce(name: str, config: dict, metadata: Optional[Dict] = None) -> str:
    """
    Print a formatted introduction message.
    """
    message = ""
    message += f"{'=' * 80}\n{name}\n{'=' * 80}\n\n"
    message += "Configuration:\n"
    for k, v in config.items():
        if k in ["openai_api_key", "supabase_key"]:
            v = "********"
        message += f"  - {k}: {v}\n"
    if metadata:
        message += "Metadata:\n"
        for k, v in metadata.items():
            message += f"  - {k}: {v}\n"
    return message


def get_action_input() -> dict:
    """
    Get JSON input from the environment variable 'JSON'.
    If the variable is not set or is invalid, return an empty dictionary.
    """
    json_input = os.environ.get("INPUT_JSON", "{}")
    try:
        return json.loads(json_input)
    except json.JSONDecodeError as e:
        logging.error(f"Invalid JSON input: {e}")
        return {}


def set_action_output(value: dict) -> None:
    """
    Set an output variable for GitHub Actions.
    """
    try:
        with open(os.environ.get("GITHUB_OUTPUT", "/tmp/nothing"), "a") as fh:
            print(f"json={json.dumps(value, separators=(',', ':'))}", file=fh)
    except Exception as e:
        logging.warning(f"Failed to set GitHub Actions output: {e}")
