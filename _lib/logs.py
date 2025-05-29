import logging
import sys


def initialize_logger(stdout: bool = True, file: bool = False, file_path: str = None) -> logging.Logger:
    logger = logging.getLogger("patchpilot-bot")
    logger.setLevel(logging.DEBUG)
    if stdout:
        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
        stdout_handler.setFormatter(stdout_formatter)
        logger.addHandler(stdout_handler)

    if file:
        file_handler = logging.FileHandler(file_path, encoding="utf-8", errors="xmlcharrefreplace")
        file_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger
