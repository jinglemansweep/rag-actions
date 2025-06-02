import json
import logging
import os
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


def write_file(file_path: str, content: str) -> None:
    """
    Write content to a file.
    """
    cwd = os.getcwd()
    workspace = os.environ.get("GITHUB_WORKSPACE", cwd)
    full_path = os.path.join(workspace, file_path)
    logger.info(f"CWD: {cwd}")
    logger.info(f"Workspace: {workspace}")
    logger.info(f"Full path: {full_path}")
    try:
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        logger.info(f"File written successfully: {file_path}")
    except Exception as e:
        logger.error(f"Failed to write file {file_path}: {e}")
        raise
