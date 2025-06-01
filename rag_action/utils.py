import json
import logging
from typing import Dict


logger = logging.getLogger(__name__)


def parse_json(json_str: str) -> Dict:
    """
    Parse JSON string into a dictionary.
    """
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        logger.warning(f"Invalid JSON in metadata: {e}")
        return {}
