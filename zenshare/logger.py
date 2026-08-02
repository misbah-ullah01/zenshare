"""Logging configuration for ZenShare."""

from __future__ import annotations

import sys
from pathlib import Path

from loguru import logger

from .utils.helpers import ensure_parent_directory


def configure_logging(*, enabled: bool, log_path: Path) -> None:
    """Configure loguru sinks for console and file output."""

    logger.remove()
    if not enabled:
        return

    ensure_parent_directory(log_path)
    logger.add(sys.stderr, level="INFO", format="{time:HH:mm:ss} | {level:<8} | {message}")
    logger.add(log_path, level="INFO", rotation="1 MB", retention=3, format="{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | {message}")