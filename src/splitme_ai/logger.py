"""Custom logger implementation with color and emoji support."""

import logging
import sys
import typing

LOG_LEVEL_EMOJIS = {
    "DEBUG": "⚙︎",
    "INFO": "►",
    "WARNING": "⚠️",
    "ERROR": "ⓧ",
    "CRITICAL": "‼",
}

LOG_LEVEL_COLORS = {
    "DEBUG": "\033[34m",
    "INFO": "\033[35m",
    "WARNING": "\033[33m",
    "ERROR": "\033[31m",
    "CRITICAL": "\033[31m\033[1m",
}


RESET_COLOR = "\033[0m"


class CustomFormatter(logging.Formatter):
    """
    Custom logging formatter with color and emoji support.
    """

    def format(self, record: logging.LogRecord) -> str:
        """Format the log record."""
        record.emoji = LOG_LEVEL_EMOJIS.get(record.levelname, "")
        record.color = LOG_LEVEL_COLORS.get(record.levelname, "")
        super().format(record)
        return f"{record.color}{record.emoji} {record.levelname} | {record.asctime} | {record.name} | {RESET_COLOR}{record.message}"


class Logger:
    """
    Custom logger class for the splitme-ai package.
    """

    _instances: typing.ClassVar[dict[str, "Logger"]] = {}

    def __new__(
        cls: typing.Type["Logger"], name: str, level: str = "DEBUG"
    ) -> "Logger":
        """Creates a new logger instance."""
        if name not in cls._instances:
            instance = super().__new__(cls)
            instance._name = name
            instance._level = level
            instance._configure_logger()
            cls._instances[name] = instance
        return cls._instances[name]

    def _configure_logger(self) -> None:
        """Configures the logger."""
        formatter = CustomFormatter(
            "%(asctime)s | %(name)s | %(levelname)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(formatter)
        logger = logging.getLogger(self._name)
        logger.addHandler(handler)
        logger.setLevel(self._level)

    def info(self, msg: str, *args: typing.Any, **kwargs: typing.Any) -> None:
        """Logs an info message."""
        logging.getLogger(self._name).info(msg, *args, **kwargs)

    def debug(self, msg: str, *args: typing.Any, **kwargs: typing.Any) -> None:
        """Logs a debug message."""
        logging.getLogger(self._name).debug(msg, *args, **kwargs)

    def warning(self, msg: str, *args: typing.Any, **kwargs: typing.Any) -> None:
        """Logs a warning message."""
        logging.getLogger(self._name).warning(msg, *args, **kwargs)

    def error(self, msg: str, *args: typing.Any, **kwargs: typing.Any) -> None:
        """Logs an error message."""
        logging.getLogger(self._name).error(msg, *args, **kwargs)

    def critical(self, msg: str, *args: typing.Any, **kwargs: typing.Any) -> None:
        """Logs a critical message."""
        logging.getLogger(self._name).critical(msg, *args, **kwargs)

    def log(
        self, level: int, msg: str, *args: typing.Any, **kwargs: typing.Any
    ) -> None:
        """Logs a message at the specified level."""
        logging.getLogger(self._name).log(level, msg, *args, **kwargs)
