"""Path helpers for ZenShare."""

from __future__ import annotations

from pathlib import Path


def project_root() -> Path:
    """Return the repository root for the ZenShare workspace."""

    return Path(__file__).resolve().parents[2]


def resolve_path(*parts: str) -> Path:
    """Resolve a path relative to the project root."""

    return project_root().joinpath(*parts)