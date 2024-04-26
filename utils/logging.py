import logging
from typing import Optional
import sys
import os


def configure_logging(
    loglevel: int, console_level: int, log_file: str = "py_log.log"
) -> None:
    # if log_file is None we assume we don't need a log file
    if log_file is not None and os.path.exists(log_file):
        os.remove(log_file)

    logging.basicConfig(level=logging.INFO)
    root_logger = logging.getLogger()

    formatter = logging.Formatter(
        fmt="%(asctime)s %(levelname)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S%Z"
    )

    if log_file is not None:
        file_handler = logging.FileHandler(log_file, mode="w")
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    else:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(console_level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

    # root_logger.setLevel(loglevel)


def handle_log_messages(messages: Optional[str]) -> None:
    if not messages:
        return
    sys.stderr.write("\n")
    sys.stderr.write("Python version: " + sys.version + "\n")
    sys.stderr.write("\n")
    sys.stderr.write(messages)
    sys.stderr.write("\n")
    sys.exit(1)
