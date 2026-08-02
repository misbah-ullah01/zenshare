"""Convenience helpers for restoring ZenShare state."""

from __future__ import annotations

from .presentation import PresentationManager, PresentationResult


def restore_presentation(manager: PresentationManager) -> PresentationResult:
    """Restore the last saved ZenShare presentation state."""

    return manager.stop()