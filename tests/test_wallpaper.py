"""Tests for ZenShare wallpaper generation."""

from __future__ import annotations

from pathlib import Path

from zenshare.constants import DEFAULT_CLEAN_WALLPAPER_NAME
from zenshare.windows.wallpaper import WallpaperController


def test_clean_wallpaper_is_png(tmp_path: Path) -> None:
    """The clean wallpaper should be generated as a PNG file."""

    controller = WallpaperController()
    wallpaper_path = tmp_path / DEFAULT_CLEAN_WALLPAPER_NAME

    controller._create_solid_png(wallpaper_path)

    data = wallpaper_path.read_bytes()
    assert wallpaper_path.suffix == ".png"
    assert data.startswith(b"\x89PNG\r\n\x1a\n")
    assert b"IHDR" in data
    assert b"IEND" in data


def test_default_wallpaper_uses_the_bundled_asset(tmp_path: Path, monkeypatch) -> None:
    """The default setting should apply the authored ZenShare image, not generated pixels."""

    source = tmp_path / "ZenShare.png"
    source.write_bytes(b"custom-wallpaper")
    controller = WallpaperController()
    monkeypatch.setattr("zenshare.windows.wallpaper.DEFAULT_WALLPAPER_PATH", source)
    monkeypatch.setattr(controller, "_require_windows", lambda: None)
    monkeypatch.setattr(controller, "_set_wallpaper", lambda _path: None)

    applied = controller.apply_clean_wallpaper(tmp_path / "runtime")

    assert applied.read_bytes() == b"custom-wallpaper"
