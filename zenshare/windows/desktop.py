"""Desktop icon controls for ZenShare."""

from __future__ import annotations

import sys

if sys.platform == "win32":  # pragma: no cover - Windows-only behavior
    import winreg

from ..utils.exceptions import WindowsOperationError
from .explorer import refresh_shell

DESKTOP_ADVANCED_KEY = r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced"
HIDE_ICONS_VALUE = "HideIcons"


class DesktopController:
    """Hide and restore desktop icons."""

    def backup_visibility(self) -> bool:
        """Return the current desktop icon visibility state."""

        return not self._read_hide_icons()

    def hide_icons(self) -> None:
        """Hide desktop icons."""

        self._write_hide_icons(True)
        refresh_shell()

    def restore_icons(self, visible: bool) -> None:
        """Restore desktop icon visibility."""

        self._write_hide_icons(not visible)
        refresh_shell()

    def _read_hide_icons(self) -> bool:
        self._require_windows()
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, DESKTOP_ADVANCED_KEY, 0, winreg.KEY_READ) as handle:
                value, _ = winreg.QueryValueEx(handle, HIDE_ICONS_VALUE)
                return bool(value)
        except FileNotFoundError:
            return False
        except OSError as exc:  # pragma: no cover - platform specific
            raise WindowsOperationError(f"Unable to read desktop icon state: {exc}") from exc

    def _write_hide_icons(self, hide_icons: bool) -> None:
        self._require_windows()
        try:
            with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, DESKTOP_ADVANCED_KEY, 0, winreg.KEY_WRITE) as handle:
                winreg.SetValueEx(handle, HIDE_ICONS_VALUE, 0, winreg.REG_DWORD, int(hide_icons))
        except OSError as exc:  # pragma: no cover - platform specific
            raise WindowsOperationError(f"Unable to update desktop icon state: {exc}") from exc

    @staticmethod
    def _require_windows() -> None:
        if sys.platform != "win32":
            raise WindowsOperationError("Desktop icon control is only supported on Windows.")