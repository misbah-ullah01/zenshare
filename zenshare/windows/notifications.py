"""Notification suppression helpers for ZenShare."""

from __future__ import annotations

import sys
import ctypes

if sys.platform == "win32":  # pragma: no cover - Windows-only behavior
    import winreg

from ..utils.exceptions import WindowsOperationError
from .explorer import refresh_shell

NOTIFICATIONS_KEY = r"Software\Microsoft\Windows\CurrentVersion\PushNotifications"
NOTIFICATION_SETTINGS_KEY = r"Software\Microsoft\Windows\CurrentVersion\Notifications\Settings"
TOAST_ENABLED_VALUE = "ToastEnabled"
GLOBAL_TOASTS_ENABLED_VALUE = "NOC_GLOBAL_SETTING_TOASTS_ENABLED"
DO_NOT_DISTURB_ENABLED_VALUE = "NOC_GLOBAL_SETTING_DO_NOT_DISTURB_ENABLED"


class NotificationController:
    """Suppress and restore toast notifications."""

    def backup_state(self) -> dict[str, bool]:
        """Return every value ZenShare changes so it can restore it exactly."""

        return {
            "toast_enabled": self._read_value(NOTIFICATIONS_KEY, TOAST_ENABLED_VALUE, True),
            "global_toasts_enabled": self._read_value(
                NOTIFICATION_SETTINGS_KEY, GLOBAL_TOASTS_ENABLED_VALUE, True
            ),
            "do_not_disturb_enabled": self._read_value(
                NOTIFICATION_SETTINGS_KEY, DO_NOT_DISTURB_ENABLED_VALUE, False
            ),
        }

    def enable_suppression(self) -> None:
        """Enable Do Not Disturb, block new toast banners, and dismiss visible ones."""

        self._write_notifications_enabled(False)
        self._dismiss_visible_toasts()
        refresh_shell()

    def restore(self, state: dict[str, bool] | bool) -> None:
        """Restore toast notification state."""

        # Accept legacy Boolean state files created by earlier ZenShare releases.
        if isinstance(state, bool):
            self._write_notifications_enabled(state)
        else:
            self._write_values(state)
        refresh_shell()

    def _read_value(self, key_path: str, value_name: str, default: bool) -> bool:
        self._require_windows()
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ) as handle:
                value, _ = winreg.QueryValueEx(handle, value_name)
                return bool(value)
        except FileNotFoundError:
            return default
        except OSError as exc:  # pragma: no cover - platform specific
            raise WindowsOperationError(f"Unable to read notification state: {exc}") from exc

    def _read_notifications_enabled(self) -> bool:
        self._require_windows()
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, NOTIFICATIONS_KEY, 0, winreg.KEY_READ) as handle:
                value, _ = winreg.QueryValueEx(handle, TOAST_ENABLED_VALUE)
                toast_enabled = bool(value)
        except FileNotFoundError:
            toast_enabled = True
        except OSError as exc:  # pragma: no cover - platform specific
            raise WindowsOperationError(f"Unable to read notification state: {exc}") from exc

        return toast_enabled and self._read_global_toasts_enabled() and not self._read_do_not_disturb_enabled()

    def _read_global_toasts_enabled(self) -> bool:
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, NOTIFICATION_SETTINGS_KEY, 0, winreg.KEY_READ) as handle:
                value, _ = winreg.QueryValueEx(handle, GLOBAL_TOASTS_ENABLED_VALUE)
                return bool(value)
        except FileNotFoundError:
            return True
        except OSError as exc:  # pragma: no cover - platform specific
            raise WindowsOperationError(f"Unable to read focus assist state: {exc}") from exc

    def _read_do_not_disturb_enabled(self) -> bool:
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, NOTIFICATION_SETTINGS_KEY, 0, winreg.KEY_READ) as handle:
                value, _ = winreg.QueryValueEx(handle, DO_NOT_DISTURB_ENABLED_VALUE)
                return bool(value)
        except FileNotFoundError:
            return True
        except OSError as exc:  # pragma: no cover - platform specific
            raise WindowsOperationError(f"Unable to read do not disturb state: {exc}") from exc

    def _write_notifications_enabled(self, enabled: bool) -> None:
        self._require_windows()
        try:
            with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, NOTIFICATIONS_KEY, 0, winreg.KEY_WRITE) as handle:
                winreg.SetValueEx(handle, TOAST_ENABLED_VALUE, 0, winreg.REG_DWORD, int(enabled))
            with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, NOTIFICATION_SETTINGS_KEY, 0, winreg.KEY_WRITE) as handle:
                winreg.SetValueEx(handle, GLOBAL_TOASTS_ENABLED_VALUE, 0, winreg.REG_DWORD, int(enabled))
                winreg.SetValueEx(handle, DO_NOT_DISTURB_ENABLED_VALUE, 0, winreg.REG_DWORD, int(not enabled))
        except OSError as exc:  # pragma: no cover - platform specific
            raise WindowsOperationError(f"Unable to update notification state: {exc}") from exc

    def _write_values(self, state: dict[str, bool]) -> None:
        self._require_windows()
        try:
            with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, NOTIFICATIONS_KEY, 0, winreg.KEY_WRITE) as handle:
                winreg.SetValueEx(handle, TOAST_ENABLED_VALUE, 0, winreg.REG_DWORD, int(state["toast_enabled"]))
            with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, NOTIFICATION_SETTINGS_KEY, 0, winreg.KEY_WRITE) as handle:
                winreg.SetValueEx(
                    handle, GLOBAL_TOASTS_ENABLED_VALUE, 0, winreg.REG_DWORD, int(state["global_toasts_enabled"])
                )
                winreg.SetValueEx(
                    handle, DO_NOT_DISTURB_ENABLED_VALUE, 0, winreg.REG_DWORD, int(state["do_not_disturb_enabled"])
                )
        except OSError as exc:  # pragma: no cover - platform specific
            raise WindowsOperationError(f"Unable to restore notification state: {exc}") from exc

    def _dismiss_visible_toasts(self) -> None:
        """Close currently displayed Windows notification banners when they can be identified.

        Windows does not provide a public API that removes another application's toast.
        Shell-hosted toast windows can nevertheless be safely dismissed by asking their
        top-level window to close. New banners remain blocked by the settings above.
        """

        self._require_windows()
        wm_close = 0x0010
        shell_process_names = {"shellexperiencehost.exe", "startmenuexperiencehost.exe"}
        toast_classes = {"Windows.UI.Core.CoreWindow", "Windows.UI.Composition.DesktopWindowContentBridge"}
        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32

        @ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
        def close_toast(hwnd: int, _lparam: int) -> bool:
            if not user32.IsWindowVisible(hwnd):
                return True
            class_name = ctypes.create_unicode_buffer(256)
            user32.GetClassNameW(hwnd, class_name, len(class_name))
            if class_name.value not in toast_classes:
                return True
            process_id = ctypes.c_ulong()
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(process_id))
            process = ctypes.windll.kernel32.OpenProcess(0x1000, False, process_id.value)
            if not process:
                return True
            try:
                executable = ctypes.create_unicode_buffer(1024)
                length = ctypes.c_ulong(len(executable))
                if kernel32.QueryFullProcessImageNameW(process, 0, executable, ctypes.byref(length)):
                    process_name = executable.value.rsplit("\\", 1)[-1].lower()
                    if process_name in shell_process_names:
                        user32.PostMessageW(hwnd, wm_close, 0, 0)
            finally:
                kernel32.CloseHandle(process)
            return True

        try:
            user32.EnumWindows(close_toast, 0)
        except Exception as exc:  # pragma: no cover - platform specific
            raise WindowsOperationError(f"Unable to dismiss visible notifications: {exc}") from exc

    @staticmethod
    def _require_windows() -> None:
        if sys.platform != "win32":
            raise WindowsOperationError("Notification controls are only supported on Windows.")
