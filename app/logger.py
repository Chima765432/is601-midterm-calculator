"""Logging setup: one Logger class configures the file every module writes to."""

import logging


class Logger:
    """Sets up file logging from the config and hands out named loggers."""

    FORMAT = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"

    @staticmethod
    def setup(config):
        """Send log records at INFO and above to the configured log file."""
        config.log_file.parent.mkdir(parents=True, exist_ok=True)
        handler = logging.FileHandler(config.log_file, encoding=config.encoding)
        handler.setFormatter(logging.Formatter(Logger.FORMAT))
        root = logging.getLogger()
        for old in root.handlers[:]:
            root.removeHandler(old)
            old.close()
        root.addHandler(handler)
        root.setLevel(logging.INFO)

    @staticmethod
    def get(name):
        return logging.getLogger(name)
