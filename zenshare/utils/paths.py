"""Path helpers for ZenShare."""

from __future__ import annotations

import os
import sys
from pathlib import Path


def project_root() -> Path:
    """Return the repository root for the ZenShare workspace."""

    return Path(__file__).resolve().parents[2]


def bundled_root() -> Path:
    """Return the directory containing files bundled with the application."""

    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)  # type: ignore[attr-defined]
    return project_root()


def application_data_root() -> Path:
    """Return the per-user writable location used by ZenShare at runtime."""

    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        return Path(local_app_data) / "ZenShare"
    return project_root()


def resolve_path(*parts: str) -> Path:
    """Resolve a path relative to the project root."""

    return project_root().joinpath(*parts)
