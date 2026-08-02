"""Wallpaper helpers for ZenShare."""

from __future__ import annotations

import struct
import sys
from pathlib import Path

if sys.platform == "win32":  # pragma: no cover - Windows-only behavior
    import ctypes

from ..constants import DEFAULT_CLEAN_WALLPAPER_NAME, DEFAULT_WALLPAPER_SIZE
from ..utils.exceptions import WindowsOperationError
from ..utils.helpers import ensure_parent_directory

SPI_GETDESKWALLPAPER = 0x0073
SPI_SETDESKWALLPAPER = 0x0014
SPIF_UPDATEINIFILE = 0x0001
SPIF_SENDCHANGE = 0x0002


class WallpaperController:
    """Backup, replace, and restore the Windows wallpaper."""

    def backup_wallpaper(self) -> str:
        """Return the current wallpaper path or an empty string when missing."""

        self._require_windows()
        buffer = ctypes.create_unicode_buffer(4096)
        try:
            success = ctypes.windll.user32.SystemParametersInfoW(SPI_GETDESKWALLPAPER, len(buffer), buffer, 0)
        except Exception as exc:  # pragma: no cover - Windows API guard
            raise WindowsOperationError(f"Unable to read wallpaper path: {exc}") from exc
        if not success:
            return ""
        return buffer.value

    def apply_clean_wallpaper(self, target_directory: Path) -> Path:
        """Create and apply a neutral wallpaper image."""

        self._require_windows()
        wallpaper_path = target_directory / DEFAULT_CLEAN_WALLPAPER_NAME
        ensure_parent_directory(wallpaper_path)
        self._create_solid_bmp(wallpaper_path)
        self._set_wallpaper(str(wallpaper_path))
        return wallpaper_path

    def restore_wallpaper(self, wallpaper_path: str) -> None:
        """Restore a previously backed-up wallpaper path."""

        self._require_windows()
        if wallpaper_path:
            self._set_wallpaper(wallpaper_path)

    def _set_wallpaper(self, wallpaper_path: str) -> None:
        try:
            # SystemParametersInfoW updates the live desktop and the persisted user setting.
            ctypes.windll.user32.SystemParametersInfoW(
                SPI_SETDESKWALLPAPER,
                0,
                wallpaper_path,
                SPIF_UPDATEINIFILE | SPIF_SENDCHANGE,
            )
        except Exception as exc:  # pragma: no cover - Windows API guard
            raise WindowsOperationError(f"Unable to apply wallpaper: {exc}") from exc

    def _create_solid_bmp(self, wallpaper_path: Path) -> None:
        width, height = DEFAULT_WALLPAPER_SIZE
        pixel_row_size = (width * 3 + 3) & ~3
        pixel_data_size = pixel_row_size * height
        file_size = 54 + pixel_data_size
        header = struct.pack(
            "<2sIHHIIIIHHIIIIII",
            b"BM",
            file_size,
            0,
            0,
            54,
            40,
            width,
            height,
            1,
            24,
            0,
            pixel_data_size,
            2835,
            2835,
            0,
            0,
        )
        pixel_row = bytes([240, 240, 240]) * width
        padding = b"\x00" * (pixel_row_size - width * 3)
        with wallpaper_path.open("wb") as handle:
            handle.write(header)
            for _ in range(height):
                handle.write(pixel_row)
                handle.write(padding)

    @staticmethod
    def _require_windows() -> None:
        if sys.platform != "win32":
            raise WindowsOperationError("Wallpaper control is only supported on Windows.")