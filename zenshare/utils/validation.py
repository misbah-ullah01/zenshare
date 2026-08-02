"""Validation helpers for ZenShare."""

from __future__ import annotations

from collections.abc import Sequence

from .helpers import deduplicate_preserve_order, normalize_display_name


def normalize_app_names(app_names: Sequence[str]) -> list[str]:
    """Normalize a sequence of application names."""

    cleaned = [name.strip() for name in app_names if name and name.strip()]
    return deduplicate_preserve_order(cleaned)


def app_name_matches(candidate: str, target: str) -> bool:
    """Return whether two application names refer to the same app."""

    return normalize_display_name(candidate) == normalize_display_name(target)