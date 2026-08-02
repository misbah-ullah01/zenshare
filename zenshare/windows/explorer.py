"""Explorer refresh helpers for ZenShare."""

from __future__ import annotations

import ctypes

from ..utils.exceptions import WindowsOperationError


def refresh_shell() -> None:
    """Notify Windows that shell settings have changed."""

    try:
        ctypes.windll.shell32.SHChangeNotify(0x08000000, 0, None, None)
    except Exception as exc:  # pragma: no cover - Windows API guard
        raise WindowsOperationError(f"Unable to refresh Explorer: {exc}") from exc