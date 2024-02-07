"""Definition of the central logging system."""

import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Union

import rich.logging

logger_format = logging.Formatter(
    "%(name)s - %(asctime)s - %(levelname)s: %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)


class Logger(logging.Logger):
    """Custom Logger class that extends the functionality of logging.Logger.

    This class overrides the error method to handle logging based on log levels.
    If the log level is DEBUG or below, it logs the exception and raises
    SystemExit; otherwise, it emits an error message.

    Attributes
    ----------
        name: str
            Name of the logger.
    """

    name: str = "freva-stats-api"

    def __init__(self, debug: bool = False) -> None:
        """Initializes the CustomLogger instance and adds a rotating file handler.

        Parameters:
            debug: bool
                Turn on debugging mode.
        """
        level = logging.INFO
        if debug is True:
            level = logging.DEBUG
        super().__init__(self.name)
        self._file_handle: RotatingFileHandler = self._get_file_handle()
        self._add_stream_handler()
        self.addHandler(self._file_handle)
        self.setLevel(level)

    def _add_stream_handler(self) -> rich.logging.RichHandler:
        """
        Add a stream handler to the logger for logging to console.

        Returns:
            logging.StreamHandler: StreamHandler instance for logging to
                                   console.
        """

        stream_handler = rich.logging.RichHandler(rich_tracebacks=True)
        stream_handler.setLevel(self.level)
        # Set the format for the log messages
        stream_handler.setFormatter(logger_format)

        # Add the stream handler to the logger
        self.addHandler(stream_handler)
        return stream_handler

    def _get_file_handle(self) -> RotatingFileHandler:
        """Get a file log handle for the logger."""

        log_dir = Path(os.environ.get("API_LOGDIR") or f"/tmp/log/{self.name}")
        log_dir = Path("/tmp") / self.name / "log"
        log_dir.mkdir(exist_ok=True, parents=True)
        logger_file_handle = RotatingFileHandler(
            log_dir / f"{self.name}.log",
            mode="a",
            maxBytes=5 * 1024**2,
            backupCount=5,
            encoding="utf-8",
            delay=False,
        )
        logger_file_handle.setFormatter(logger_format)
        logger_file_handle.setLevel(self.level)
        return logger_file_handle

    def setLevel(self, level: Union[int, str]) -> None:
        """
        Overrides the setLevel method to synchronize the log level with the
        file handler.

        Parameters:
            level int, str:
                Log level to be set.
        """
        super().setLevel(level)
        for handle in self.handlers:
            handle.setLevel(level)
        self._file_handle.setLevel(level)
