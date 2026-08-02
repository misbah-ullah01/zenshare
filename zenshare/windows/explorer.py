"""Explorer refresh helpers for ZenShare."""

from __future__ import annotations

import ctypes

from ..utils.exceptions import WindowsOperationError

WM_SETTINGCHANGE = 0x001A
HWND_BROADCAST = 0xFFFF
SMTO_ABORTIFHUNG = 0x0002


def refresh_shell() -> None:
    """Notify Windows that shell settings have changed."""

    try:
        ctypes.windll.user32.SendMessageTimeoutW(
            HWND_BROADCAST,
            WM_SETTINGCHANGE,
            0,
            ctypes.c_wchar_p("TraySettings"),
            SMTO_ABORTIFHUNG,
            1000,
            None,
        )
        ctypes.windll.shell32.SHChangeNotify(0x08000000, 0, None, None)
    except Exception as exc:  # pragma: no cover - Windows API guard
        raise WindowsOperationError(f"Unable to refresh Explorer: {exc}") from exc