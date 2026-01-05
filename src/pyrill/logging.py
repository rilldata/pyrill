"""
Logging interface for RillClient.

This module provides a simple logging protocol that allows applications
to receive log events from the client. By default, the client uses a
NullLogger which has zero overhead.

Applications can implement the ClientLogger protocol to receive and handle
log events however they want (stdout, files, structured storage, etc).

Example:
    >>> import logging
    >>>
    >>> class MyLogger:
    ...     def debug(self, message: str, **details):
    ...         logging.debug(message, extra=details)
    ...     def info(self, message: str, **details):
    ...         logging.info(message, extra=details)
    ...     # ... etc
    >>>
    >>> from src.client import RillClient
    >>> client = RillClient(logger=MyLogger())
"""

from typing import Protocol, Any
from enum import Enum


class LogLevel(Enum):
    """Standard logging levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class ClientLogger(Protocol):
    """
    Protocol for logging client operations.

    Applications can implement this interface to receive log events from
    the RillClient. Each method receives a message and optional details
    as keyword arguments.

    The details dict may contain operation-specific information such as:
    - duration: float (seconds)
    - status_code: int (HTTP status)
    - return_code: int (CLI exit code)
    - command: str (CLI command executed)
    - method: str (HTTP method)
    - url: str (API endpoint)
    - error: str (error details)
    """

    def debug(self, message: str, **details: Any) -> None:
        """Log debug-level message with optional details."""
        ...

    def info(self, message: str, **details: Any) -> None:
        """Log info-level message with optional details."""
        ...

    def warning(self, message: str, **details: Any) -> None:
        """Log warning-level message with optional details."""
        ...

    def error(self, message: str, **details: Any) -> None:
        """Log error-level message with optional details."""
        ...


class NullLogger:
    """
    No-op logger implementation (default).

    This logger discards all log events and has zero overhead.
    Used by default when no logger is provided to RillClient.
    """

    def debug(self, message: str, **details: Any) -> None:
        """Discard debug message."""
        pass

    def info(self, message: str, **details: Any) -> None:
        """Discard info message."""
        pass

    def warning(self, message: str, **details: Any) -> None:
        """Discard warning message."""
        pass

    def error(self, message: str, **details: Any) -> None:
        """Discard error message."""
        pass
