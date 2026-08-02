"""Small reusable helper functions for ZenShare."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


def ensure_parent_directory(path: Path) -> None:
    """Create the parent directory for ``path`` if it does not exist."""

    path.parent.mkdir(parents=True, exist_ok=True)


def current_timestamp() -> str:
    """Return the current UTC timestamp in ISO-8601 format."""

    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def deduplicate_preserve_order(items: Iterable[str]) -> list[str]:
    """Return unique items while preserving the first-seen order."""

    seen: set[str] = set()
    unique_items: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            unique_items.append(item)
    return unique_items


def normalize_display_name(value: str) -> str:
    """Normalize a display name for case-insensitive comparisons."""

    return value.strip().casefold()