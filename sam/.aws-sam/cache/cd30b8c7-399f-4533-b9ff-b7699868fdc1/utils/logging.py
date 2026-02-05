"""
Logging configuration for Virtual Me chatbot.

Provides JSON-formatted logging for better CloudWatch Insights queries.
Uses INFO level by default to minimize CloudWatch costs.

Example CloudWatch Insights queries:
    - fields @timestamp, level, module, message | filter level = "ERROR"
    - stats count(*) by module | sort count desc
"""

import json
import logging
import os
from typing import Any


# Log level from environment (default INFO for cost efficiency)
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()


class JSONFormatter(logging.Formatter):
    """
    Custom formatter that outputs JSON for CloudWatch Insights.

    Output format:
        {"timestamp": "...", "level": "INFO", "module": "...", "message": "..."}
    """

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON string."""
        log_data: dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "module": record.name,
            "message": record.getMessage(),
        }

        # Include exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)


def get_logger(name: str) -> logging.Logger:
    """
    Get a configured logger instance with JSON formatting.

    Args:
        name: Logger name (typically __name__ of the calling module)

    Returns:
        Configured logger instance

    Example:
        >>> from utils.logging import get_logger
        >>> logger = get_logger(__name__)
        >>> logger.info("Processing request")
        {"timestamp": "2025-01-02 12:00:00", "level": "INFO", "module": "...", "message": "Processing request"}
    """
    logger = logging.getLogger(name)

    # Only configure if not already configured
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = JSONFormatter(datefmt='%Y-%m-%d %H:%M:%S')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))

    return logger
