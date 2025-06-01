import logging
import os

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
