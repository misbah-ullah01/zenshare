"""Desktop icon controls for ZenShare."""

from __future__ import annotations

import ctypes
import sys

if sys.platform == "win32":  # pragma: no cover - Windows-only behavior
    import winreg

from ..utils.exceptions import WindowsOperationError
from .explorer import refresh_shell

DESKTOP_ADVANCED_KEY = r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced"
HIDE_ICONS_VALUE = "HideIcons"
SW_HIDE = 0
SW_SHOW = 5
WM_SPAWN_WORKER = 0x052C
SMTO_ABORTIFHUNG = 0x0002


def _enum_windows(callback):
    """Enumerate top-level windows and return the callback result."""

    enum_proc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)(callback)
    ctypes.windll.user32.EnumWindows(enum_proc, 0)


class DesktopController:
    """Hide and restore desktop icons."""

    def backup_visibility(self) -> bool:
        """Return the current desktop icon visibility state."""

        desktop_handle = self._find_desktop_icon_listview()
        if desktop_handle:
            return bool(ctypes.windll.user32.IsWindowVisible(desktop_handle))
        return not self._read_hide_icons()

    def hide_icons(self) -> None:
        """Hide desktop icons."""

        desktop_handle = self._find_desktop_icon_listview()
        if desktop_handle:
            ctypes.windll.user32.ShowWindow(desktop_handle, SW_HIDE)
        self._write_hide_icons(True)
        refresh_shell()

    def restore_icons(self, visible: bool) -> None:
        """Restore desktop icon visibility."""

        desktop_handle = self._find_desktop_icon_listview()
        if desktop_handle:
            ctypes.windll.user32.ShowWindow(desktop_handle, SW_SHOW if visible else SW_HIDE)
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

    def _find_desktop_icon_listview(self) -> int:
        self._require_windows()
        def locate() -> int:
            found_handle = ctypes.c_void_p(0)

            def enum_callback(hwnd: int, _lparam: int) -> bool:
                shell_def_view = ctypes.windll.user32.FindWindowExW(hwnd, 0, "SHELLDLL_DefView", None)
                if not shell_def_view:
                    return True
                list_view = ctypes.windll.user32.FindWindowExW(shell_def_view, 0, "SysListView32", None)
                if list_view:
                    found_handle.value = list_view
                    return False
                return True

            _enum_windows(enum_callback)
            return int(found_handle.value or 0)

        try:
            handle = locate()
            if handle:
                return handle

            progman = ctypes.windll.user32.FindWindowW("Progman", None)
            if progman:
                ctypes.windll.user32.SendMessageTimeoutW(
                    progman,
                    WM_SPAWN_WORKER,
                    0,
                    0,
                    SMTO_ABORTIFHUNG,
                    1000,
                    None,
                )
                handle = locate()
                if handle:
                    return handle

            workerw = ctypes.windll.user32.FindWindowW("WorkerW", None)
            if workerw:
                shell_def_view = ctypes.windll.user32.FindWindowExW(workerw, 0, "SHELLDLL_DefView", None)
                if shell_def_view:
                    list_view = ctypes.windll.user32.FindWindowExW(shell_def_view, 0, "SysListView32", None)
                    if list_view:
                        return int(list_view)

            return 0
        except Exception as exc:  # pragma: no cover - platform specific
            raise WindowsOperationError(f"Unable to locate the desktop icon list view: {exc}") from exc

    @staticmethod
    def _require_windows() -> None:
        if sys.platform != "win32":
            raise WindowsOperationError("Desktop icon control is only supported on Windows.")