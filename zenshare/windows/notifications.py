"""Notification suppression helpers for ZenShare."""

from __future__ import annotations

import sys

if sys.platform == "win32":  # pragma: no cover - Windows-only behavior
    import winreg

from ..utils.exceptions import WindowsOperationError

NOTIFICATIONS_KEY = r"Software\Microsoft\Windows\CurrentVersion\PushNotifications"
TOAST_ENABLED_VALUE = "ToastEnabled"


class NotificationController:
    """Suppress and restore toast notifications."""

    def backup_state(self) -> bool:
        """Return whether toast notifications are currently enabled."""

        return self._read_toast_enabled()

    def enable_suppression(self) -> None:
        """Disable toast notifications as a quiet-hours equivalent."""

        self._write_toast_enabled(False)

    def restore(self, enabled: bool) -> None:
        """Restore toast notification state."""

        self._write_toast_enabled(enabled)

    def _read_toast_enabled(self) -> bool:
        self._require_windows()
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, NOTIFICATIONS_KEY, 0, winreg.KEY_READ) as handle:
                value, _ = winreg.QueryValueEx(handle, TOAST_ENABLED_VALUE)
                return bool(value)
        except FileNotFoundError:
            return True
        except OSError as exc:  # pragma: no cover - platform specific
            raise WindowsOperationError(f"Unable to read notification state: {exc}") from exc

    def _write_toast_enabled(self, enabled: bool) -> None:
        self._require_windows()
        try:
            with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, NOTIFICATIONS_KEY, 0, winreg.KEY_WRITE) as handle:
                winreg.SetValueEx(handle, TOAST_ENABLED_VALUE, 0, winreg.REG_DWORD, int(enabled))
        except OSError as exc:  # pragma: no cover - platform specific
            raise WindowsOperationError(f"Unable to update notification state: {exc}") from exc

    @staticmethod
    def _require_windows() -> None:
        if sys.platform != "win32":
            raise WindowsOperationError("Notification controls are only supported on Windows.")