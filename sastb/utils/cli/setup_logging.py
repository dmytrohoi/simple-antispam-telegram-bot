__all__ = ("setup_logging",)

import sys
from logging import (
    Formatter,
    Handler,
    LogRecord,
    basicConfig,
)
from logging import (
    handlers as logging_handlers,
)
from pathlib import Path

import orjson as json
from loguru import logger


class InterceptHandler(Handler):
    """InterceptHandler for loguru logging."""

    def emit(self, record: LogRecord):
        """
        Emit a record.

        Args:
            record (LogRecord): The log record to emit.

        """
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        logger.opt(depth=6, exception=record.exc_info).log(
            level,
            record.getMessage(),
        )


class JsonFormatter(Formatter):
    """Custom JSON formatter for logging."""
    fmt_dict = {
        "timestamp": "asctime",
        "level": "levelname",
        "logger": "name",
        "message": "msg",
    }

    def __init__(
        self,
        time_format: str = "%Y-%m-%dT%H:%M:%S",
        msec_format: str = "%s.%03dZ",
    ):
        self.default_time_format = time_format
        self.default_msec_format = msec_format

    def formatMessage(self, record) -> dict:
        if "asctime" in self.fmt_dict.values():
            record.asctime = self.formatTime(record, self.default_time_format)

        return {
            fmt_key: record.__dict__[fmt_val]
            for fmt_key, fmt_val in self.fmt_dict.items()
        }

    def format(self, record) -> str:
        """Format the LogRecord into a JSON string."""
        return json.dumps({
            **self.formatMessage(record),
            "extra": record.__dict__.get("extra", {}),
            "exception": str(record.exc_info),
            "@version_log": 1,
        }, default=str).decode()


def setup_logging():
    """Setup logging configuration for the application."""
    basicConfig(handlers=[InterceptHandler()], level="INFO")

    loguru_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level> | "
        "<level>({extra})</level>"
    )
    logger.remove()
    logger.configure(handlers=[{"sink": sys.stdout, "format": loguru_format}])

    logs_file = "logs/app.jsonl"
    Path(logs_file).parent.mkdir(exist_ok=True, parents=True)

    file_handler = logging_handlers.RotatingFileHandler(
        logs_file,
        maxBytes=100_000_000,
        backupCount=50,  # NOTE: 50 files * 100 MB = 5 GB
    )
    file_handler.setFormatter(JsonFormatter())
    logger.add(
        file_handler,
        format="{message}",
        level="INFO",
    )

    errors_file = "logs/errors.jsonl"
    Path(errors_file).parent.mkdir(exist_ok=True, parents=True)

    error_file_handler = logging_handlers.RotatingFileHandler(
        errors_file,
        maxBytes=100_000_000,
        backupCount=50,  # NOTE: 50 files * 100 MB = 5 GB
    )
    error_file_handler.setFormatter(JsonFormatter())
    logger.add(
        error_file_handler,
        format="{message}",
        level="ERROR",
    )
