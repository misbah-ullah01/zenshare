"""Process management helpers for ZenShare."""

from __future__ import annotations

import ctypes
import sys
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

import psutil

from ..utils.exceptions import WindowsOperationError
from ..utils.validation import app_name_matches, normalize_app_names, process_matches_target

SW_MINIMIZE = 6
SW_RESTORE = 9


@dataclass(slots=True)
class ProcessActionResult:
    """Result for minimizing or restoring target process windows."""

    matched_apps: list[str]


class ProcessController:
    """Minimize and restore application windows."""

    def find_running_apps(self, app_names: Iterable[str]) -> list[str]:
        """Return running process names that match the provided app names."""

        normalized_targets = normalize_app_names(list(app_names))
        return self._matching_process_names(normalized_targets)

    def minimize_apps(self, app_names: Iterable[str]) -> ProcessActionResult:
        """Minimize windows that belong to the requested applications."""

        normalized_targets = normalize_app_names(list(app_names))
        matched_apps = self._apply_window_action(normalized_targets, SW_MINIMIZE)
        return ProcessActionResult(matched_apps=matched_apps)

    def restore_apps(self, app_names: Iterable[str]) -> None:
        """Restore windows that belong to the requested applications."""

        normalized_targets = normalize_app_names(list(app_names))
        self._apply_window_action(normalized_targets, SW_RESTORE)

    def close_apps(self, app_names: Iterable[str]) -> ProcessActionResult:
        """Request a graceful close for matching applications."""

        normalized_targets = normalize_app_names(list(app_names))
        matched_apps: list[str] = []
        for process in psutil.process_iter(["name", "pid", "exe", "cmdline"]):
            if not self._process_matches_targets(process, normalized_targets):
                continue
            try:
                # Best effort only: request a normal exit first and avoid forced termination.
                process.terminate()
                process.wait(timeout=5)
                matched_apps.append(self._process_display_name(process))
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
                continue
        return ProcessActionResult(matched_apps=matched_apps)

    def _apply_window_action(self, targets: list[str], command: int) -> list[str]:
        self._require_windows()
        matched_apps: list[str] = []
        for process_name, pid in self._iter_matching_processes(targets):
            if self._set_windows_state_for_pid(pid, command):
                matched_apps.append(process_name)
        return matched_apps

    def _matching_process_names(self, targets: list[str]) -> list[str]:
        return [process_name for process_name, _pid in self._iter_matching_processes(targets)]

    def _iter_matching_processes(self, targets: list[str]) -> list[tuple[str, int]]:
        matches: list[tuple[str, int]] = []
        for process in psutil.process_iter(["name", "pid", "exe", "cmdline"]):
            if not self._process_matches_targets(process, targets):
                continue
            matches.append((self._process_display_name(process), process.info["pid"]))
        return matches

    def _process_matches_targets(self, process: psutil.Process, targets: list[str]) -> bool:
        process_name = process.info.get("name") or ""
        process_executable = process.info.get("exe") or ""
        command_line = process.info.get("cmdline") or []
        return any(
            process_matches_target(process_name, process_executable or None, command_line, target)
            for target in targets
        )

    @staticmethod
    def _process_display_name(process: psutil.Process) -> str:
        process_name = process.info.get("name") or ""
        process_executable = process.info.get("exe") or ""
        if process_executable:
            return Path(process_executable).stem or process_name
        return Path(process_name).stem or process_name

    def _set_windows_state_for_pid(self, pid: int, command: int) -> bool:
        found_window = False

        def enum_callback(hwnd: int, _lparam: int) -> bool:
            nonlocal found_window
            window_pid = ctypes.c_ulong()
            ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(window_pid))
            if window_pid.value != pid:
                return True
            # Skip invisible helper windows so we only affect real user-facing windows.
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