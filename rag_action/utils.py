import dataclasses
import logging
import os
from typing import Dict, Optional
from .constants import BaseConfig

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


def introduce(
    name: str, config: BaseConfig, params: dict, metadata: Optional[Dict] = None
) -> str:
    """
    Print a formatted introduction message.
    """
    message = ""
    message += f"{'=' * 80}\n{name}\n{'=' * 80}\n\n"
    message += "Configuration:\n"
    for k, v in dataclasses.asdict(config).items():
        if k in ["openai_api_key", "supabase_key"]:
            v = "********"
        message += f"  - {k}: {v}\n"
    message += "Parameters:\n"
    for k, v in params.items():
        message += f"  - {k}: {v}\n"
    if metadata:
        message += "Metadata:\n"
        for k, v in metadata.items():
            message += f"  - {k}: {v}\n"
    return message


def bash_escape(s):
    """
    Escape string for safe use as a bash variable value.
    """
    return "'" + s.replace("'", "'\"'\"'") + "'"


def set_action_ouput(name: str, value: str, multiline=False) -> None:
    """
    Set an output variable for GitHub Actions.
    """
    escaped_value = bash_escape(value)
    try:
        with open(os.environ.get("GITHUB_OUTPUT", "/tmp/nothing"), "a") as fh:
            if multiline:
                print(f"{name}<<EOF\n{escaped_value}\nEOF", file=fh)
            else:
                print(f"{name}={escaped_value}", file=fh)
    except Exception as e:
        logging.warning(f"Failed to set GitHub Actions output: {e}")
