import logging
from src.settings import LOG_LEVEL

LOG_FORMAT_DEBUG = "%(levelname)s:     %(message)s : %(funcName)s"


def configure_logging() -> None:
    logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT_DEBUG)
