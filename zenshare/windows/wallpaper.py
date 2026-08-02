"""Wallpaper helpers for ZenShare."""

from __future__ import annotations

import shutil
import struct
import sys
from pathlib import Path
import zlib

if sys.platform == "win32":  # pragma: no cover - Windows-only behavior
    import ctypes

from ..constants import DEFAULT_CLEAN_WALLPAPER_NAME, DEFAULT_WALLPAPER_PATH, DEFAULT_WALLPAPER_SIZE
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

    def apply_clean_wallpaper(self, target_directory: Path, wallpaper: str = "default") -> Path:
        """Apply the bundled ZenShare wallpaper or a user-selected image."""

        self._require_windows()
        wallpaper_path = target_directory / DEFAULT_CLEAN_WALLPAPER_NAME
        ensure_parent_directory(wallpaper_path)
        source_path = self._resolve_wallpaper(wallpaper)
        if source_path is None:
            self._create_solid_bmp(wallpaper_path)
        else:
            shutil.copy2(source_path, wallpaper_path)
        self._set_wallpaper(str(wallpaper_path))
        return wallpaper_path

    @staticmethod
    def _resolve_wallpaper(wallpaper: str) -> Path | None:
        if wallpaper.strip().lower() == "none":
            return None
        source = DEFAULT_WALLPAPER_PATH if wallpaper.strip().lower() == "default" else Path(wallpaper).expanduser()
        if not source.is_file():
            raise WindowsOperationError(f"Wallpaper image was not found: {source}")
        return source

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
        self._create_solid_png(wallpaper_path)

    def _create_solid_png(self, wallpaper_path: Path) -> None:
        width, height = DEFAULT_WALLPAPER_SIZE
        red, green, blue = 242, 242, 242

        def chunk(tag: bytes, payload: bytes) -> bytes:
            return struct.pack(">I", len(payload)) + tag + payload + struct.pack(">I", zlib.crc32(tag + payload) & 0xFFFFFFFF)

        signature = b"\x89PNG\r\n\x1a\n"
        ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
        row = bytes([0]) + bytes([red, green, blue]) * width
        compressed = zlib.compress(row * height, level=9)
        with wallpaper_path.open("wb") as handle:
            handle.write(signature)
            handle.write(chunk(b"IHDR", ihdr))
            handle.write(chunk(b"IDAT", compressed))
            handle.write(chunk(b"IEND", b""))

    @staticmethod
    def _require_windows() -> None:
        if sys.platform != "win32":
            raise WindowsOperationError("Wallpaper control is only supported on Windows.")
