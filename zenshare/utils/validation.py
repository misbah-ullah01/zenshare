"""Validation helpers for ZenShare."""

from __future__ import annotations

from pathlib import Path
from collections.abc import Sequence

from .helpers import deduplicate_preserve_order, normalize_display_name


def normalize_app_names(app_names: Sequence[str]) -> list[str]:
    """Normalize a sequence of application names."""

    cleaned = [name.strip() for name in app_names if name and name.strip()]
    return deduplicate_preserve_order(cleaned)


def app_name_matches(candidate: str, target: str) -> bool:
    """Return whether two application names refer to the same app."""

    candidate_normalized = normalize_display_name(candidate)
    target_normalized = normalize_display_name(target)
    candidate_stem = normalize_display_name(Path(candidate).stem)
    return candidate_normalized == target_normalized or candidate_stem == target_normalized


def process_matches_target(process_name: str, process_executable: str | None, command_line: Sequence[str], target: str) -> bool:
    """Return whether a process matches a configured ZenShare target."""

    if app_name_matches(process_name, target):
        return True
    if process_executable and app_name_matches(process_executable, target):
        return True
    for argument in command_line:
        if app_name_matches(argument, target):
            return True
        if target.casefold() in argument.casefold():
            return True
    return False