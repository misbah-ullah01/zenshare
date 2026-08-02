"""Registry helpers for ZenShare Windows operations."""

from __future__ import annotations

from typing import Any

from ..utils.exceptions import WindowsOperationError

try:  # pragma: no cover - Windows-only dependency
    import winreg
except ImportError:  # pragma: no cover - platform guard
    winreg = None  # type: ignore[assignment]


def _require_windows() -> None:
    if winreg is None:
        raise WindowsOperationError("Windows registry access is only available on Windows.")


def read_value(root: Any, subkey: str, value_name: str) -> Any | None:
    """Read a registry value and return ``None`` if it does not exist."""

    _require_windows()
    try:
        with winreg.OpenKey(root, subkey, 0, winreg.KEY_READ) as handle:  # type: ignore[union-attr]
            value, _ = winreg.QueryValueEx(handle, value_name)  # type: ignore[union-attr]
            return value
    except FileNotFoundError:
        return None


def write_value(root: Any, subkey: str, value_name: str, value: Any, value_type: int) -> None:
    """Write a registry value."""

    _require_windows()
    try:
        with winreg.CreateKeyEx(root, subkey, 0, winreg.KEY_WRITE) as handle:  # type: ignore[union-attr]
            winreg.SetValueEx(handle, value_name, 0, value_type, value)  # type: ignore[union-attr]
    except OSError as exc:  # pragma: no cover - platform specific
        raise WindowsOperationError(f"Failed to write registry value {subkey}\\{value_name}: {exc}") from exc


def delete_value(root: Any, subkey: str, value_name: str) -> None:
    """Delete a registry value if it exists."""

    _require_windows()
    try:
        with winreg.OpenKey(root, subkey, 0, winreg.KEY_WRITE) as handle:  # type: ignore[union-attr]
            winreg.DeleteValue(handle, value_name)  # type: ignore[union-attr]
    except FileNotFoundError:
        return
    except OSError as exc:  # pragma: no cover - platform specific
        raise WindowsOperationError(f"Failed to delete registry value {subkey}\\{value_name}: {exc}") from exc