import logging
import sys
import colorlog


class log:
    def init():
        if len(logging.getLogger("").handlers) > 1:
            return

        shandler = logging.StreamHandler(stream=sys.stdout)
        shandler.setFormatter(colorlog.LevelFormatter(
            fmt = {
                "INFO": "{log_color}[{levelname}] {message}",
                "WARNING": "{log_color}[{levelname}] {message}",
                "ERROR": "{log_color}[{levelname}] {message}",
                "CRITICAL": "{log_color}[{levelname}] {message}"
            },
            log_colors = {
                "INFO":     "white",
                "WARNING":  "yellow",
                "ERROR":    "red",
                "CRITICAL": "bold_red"
        },
            style = "{",
            datefmt = ""
        ))
        shandler.setLevel(logging.INFO)
        logging.getLogger(__package__).addHandler(shandler)
        logging.getLogger(__package__).setLevel(logging.DEBUG)

    def info(msg):
        logging.getLogger(__package__).info(msg)

    def warning(msg):
        logging.getLogger(__package__).warning(msg)

    def error(msg):
        logging.getLogger(__package__).error(msg)

    def critical(msg):
        logging.getLogger(__package__).critical(msg)