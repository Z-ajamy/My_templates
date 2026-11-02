import logging
import sys

from src.infrastructure.logger.json_formatter import JSONFormatter


def setup_logger(app_name: str = "clean_arch_app") -> logging.Logger:
    logger = logging.getLogger(app_name)

    if logger.hasHandlers():
        logger.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())

    logger.addHandler(handler)

    logger.setLevel(logging.INFO)

    return logger


app_logger = setup_logger()
