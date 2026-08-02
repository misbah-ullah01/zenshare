"""Process management helpers for ZenShare."""

from __future__ import annotations

import ctypes
import sys
from dataclasses import dataclass
from collections.abc import Iterable

import psutil

from ..utils.exceptions import WindowsOperationError
from ..utils.validation import app_name_matches, normalize_app_names

SW_MINIMIZE = 6
SW_RESTORE = 9


@dataclass(slots=True)
class ProcessActionResult:
    """Result for minimizing or restoring target process windows."""

    matched_apps: list[str]


class ProcessController:
    """Minimize and restore application windows."""

    def minimize_apps(self, app_names: Iterable[str]) -> ProcessActionResult:
        """Minimize windows that belong to the requested applications."""

        normalized_targets = normalize_app_names(list(app_names))
        matched_apps = self._apply_window_action(normalized_targets, SW_MINIMIZE)
        return ProcessActionResult(matched_apps=matched_apps)

    def restore_apps(self, app_names: Iterable[str]) -> None:
        """Restore windows that belong to the requested applications."""

        normalized_targets = normalize_app_names(list(app_names))
        self._apply_window_action(normalized_targets, SW_RESTORE)

    def _apply_window_action(self, targets: list[str], command: int) -> list[str]:
        self._require_windows()
        matched_apps: list[str] = []
        for process in psutil.process_iter(["name", "pid"]):
            process_name = process.info.get("name") or ""
            if not any(app_name_matches(process_name, target) for target in targets):
                continue
            if self._set_windows_state_for_pid(process.info["pid"], command):
                matched_apps.append(process_name)
        return matched_apps

    def _set_windows_state_for_pid(self, pid: int, command: int) -> bool:
        found_window = False

        def enum_callback(hwnd: int, _lparam: int) -> bool:
            nonlocal found_window
            window_pid = ctypes.c_ulong()
            ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(window_pid))
            if window_pid.value != pid:
                return True
            if not ctypes.windll.user32.IsWindowVisible(hwnd):
                return True
            ctypes.windll.user32.ShowWindow(hwnd, command)
            found_window = True
            return True

        try:
            callback_type = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
            ctypes.windll.user32.EnumWindows(callback_type(enum_callback), 0)
        except Exception as exc:  # pragma: no cover - Windows API guard
            raise WindowsOperationError(f"Unable to update window state for process {pid}: {exc}") from exc
        return found_window

    @staticmethod
    def _require_windows() -> None:
        if sys.platform != "win32":
            raise WindowsOperationError("Process controls are only supported on Windows.")