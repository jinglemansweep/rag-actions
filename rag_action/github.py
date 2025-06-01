import json
import logging
import os
from .constants import StateMessage
from .utils import setup_logger

setup_logger()
logger = logging.getLogger(__name__)


def get_action_input() -> StateMessage:
    """
    Get JSON input from input `STATE_JSON` (`INPUT_STATE_JSON` env variable).
    If the variable is not set or is invalid, return an empty dictionary.
    """
    json_input = os.environ.get("INPUT_STATE_JSON", "{}")
    try:
        json_obj = json.loads(json_input)
        state_message = StateMessage.model_validate(json_obj)
        logger.info(f"Input: {state_message.model_dump_json()}")
        return state_message
    except json.JSONDecodeError as e:
        logging.error(f"Invalid JSON input: {e}")
        return StateMessage()


def set_action_output(output: StateMessage) -> None:
    """
    Set JSON output as `state_json` in GitHub Actions output (`GITHUB_OUTPUT` env variable).
    """
    logger.info(f"Output: {output.model_dump_json()}")
    try:
        with open(os.environ.get("GITHUB_OUTPUT", "/tmp/nothing"), "a") as fh:
            print(f"state={output.model_dump_json()}", file=fh)
    except Exception as e:
        logging.warning(f"Failed to set GitHub Actions output: {e}")
