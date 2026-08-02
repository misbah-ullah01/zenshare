"""Tests for ZenShare start rollback behavior."""

from __future__ import annotations

from pathlib import Path

import pytest

from zenshare.config import ZenShareConfig
from zenshare.presentation import PresentationManager
from zenshare.state import StateManager


class FailingProcessController:
    def find_running_apps(self, app_names: list[str]) -> list[str]:
        return list(app_names)

    def minimize_apps(self, app_names: list[str]):
        raise RuntimeError("minimize failed")

    def capture_launch_specs(self, app_names: list[str]):
        return []

    def close_apps(self, app_names: list[str]):
        raise RuntimeError("close failed")


class NoOpDesktopController:
    def backup_visibility(self) -> bool:
        return True

    def hide_icons(self) -> None:
        return None

    def restore_icons(self, visible: bool) -> None:
        return None


class NoOpNotificationController:
    def backup_state(self) -> bool:
        return True

    def enable_suppression(self) -> None:
        return None

    def restore(self, enabled: dict[str, bool] | bool) -> None:
        return None


class NoOpWallpaperController:
    def backup_wallpaper(self) -> str:
        return "C:/wallpaper.jpg"

    def apply_clean_wallpaper(self, target_directory: Path, wallpaper: str = "default") -> Path:
        return target_directory / "clean.bmp"

    def restore_wallpaper(self, wallpaper_path: str) -> None:
        return None


def test_failed_start_restores_backup_and_deletes_state_file(tmp_path: Path) -> None:
    """A failed start should not leave a temporary state file behind."""

    state_manager = StateManager(state_path=tmp_path / "state.json")
    manager = PresentationManager(
        state_manager=state_manager,
        desktop_controller=NoOpDesktopController(),
        notification_controller=NoOpNotificationController(),
        wallpaper_controller=NoOpWallpaperController(),
        process_controller=FailingProcessController(),
        state_directory=tmp_path,
    )
    config = ZenShareConfig(
        desktop_icons=True,
        do_not_disturb=True,
        change_wallpaper=False,
        wallpaper="default",
        minimize_apps=["Discord"],
        close_apps=[],
        restore_timeout=10,
        logging=False,
    )

    with pytest.raises(Exception):
        manager.start(config)

    assert state_manager.exists() is False
