import json
import logging
import os
from typing import Dict, Optional
from .constants import StateMessage

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


def get_action_input() -> StateMessage:
    """
    Get JSON input from input `STATE_JSON` (`INPUT_STATE_JSON` env variable).
    If the variable is not set or is invalid, return an empty dictionary.
    """
    json_input = os.environ.get("INPUT_STATE_JSON", "{}")
    try:
        json_obj = json.loads(json_input)
        return StateMessage.model_validate(json_obj)
    except json.JSONDecodeError as e:
        logging.error(f"Invalid JSON input: {e}")
        return StateMessage()


def set_action_output(output: StateMessage) -> None:
    """
    Set JSON output as `state_json` in GitHub Actions output (`GITHUB_OUTPUT` env variable).
    """
    try:
        with open(os.environ.get("GITHUB_OUTPUT", "/tmp/nothing"), "a") as fh:
            print(f"state={output.model_dump_json()}", file=fh)
    except Exception as e:
        logging.warning(f"Failed to set GitHub Actions output: {e}")
