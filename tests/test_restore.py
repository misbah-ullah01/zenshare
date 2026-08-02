"""Tests for ZenShare restoration behavior."""

from __future__ import annotations

from pathlib import Path

from zenshare.presentation import PresentationManager
from zenshare.state import PresentationState, StateManager


class RecordingDesktopController:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def backup_visibility(self) -> bool:
        return False

    def hide_icons(self) -> None:
        self.calls.append("hide")

    def restore_icons(self, visible: bool) -> None:
        self.calls.append(f"desktop:{visible}")


class RecordingNotificationController:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def backup_state(self) -> bool:
        return False

    def enable_suppression(self) -> None:
        self.calls.append("suppress")

    def restore(self, enabled: dict[str, bool] | bool) -> None:
        self.calls.append(f"notifications:{enabled}")


class RecordingWallpaperController:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def backup_wallpaper(self) -> str:
        return "C:/wallpaper.jpg"

    def apply_clean_wallpaper(self, target_directory: Path, wallpaper: str = "default") -> Path:
        path = target_directory / "clean.bmp"
        path.write_text("bmp", encoding="utf-8")
        return path

    def restore_wallpaper(self, wallpaper_path: str) -> None:
        self.calls.append(f"wallpaper:{wallpaper_path}")


class RecordingProcessController:
    def __init__(self) -> None:
        self.calls: list[tuple[str, tuple[str, ...]]] = []

    def minimize_apps(self, app_names: list[str]):
        self.calls.append(("minimize", tuple(app_names)))
        return type("Result", (), {"matched_apps": ["Discord", "Slack"]})()

    def restore_apps(self, app_names: list[str]) -> None:
        self.calls.append(("restore", tuple(app_names)))


def test_stop_restores_state_in_reverse_order_and_removes_state_file(tmp_path: Path) -> None:
    """Stopping should restore the backed-up state and remove the file."""

    state_manager = StateManager(state_path=tmp_path / "state.json")
    backup = PresentationState(
        desktop_icons=False,
        wallpaper="C:/wallpaper.jpg",
        focus_assist=False,
        minimized=["Discord", "Slack"],
        created_at="2026-08-01T21:00:00+00:00",
    )
    state_manager.save(backup)

    desktop = RecordingDesktopController()
    notifications = RecordingNotificationController()
    wallpaper = RecordingWallpaperController()
    processes = RecordingProcessController()
    manager = PresentationManager(
        state_manager=state_manager,
        desktop_controller=desktop,
        notification_controller=notifications,
        wallpaper_controller=wallpaper,
        process_controller=processes,
        state_directory=tmp_path,
    )

    result = manager.stop()

    assert result.state == backup
    assert state_manager.exists() is False
    assert processes.calls == [("restore", ("Discord", "Slack"))]
    assert wallpaper.calls == ["wallpaper:C:/wallpaper.jpg"]
    assert notifications.calls == ["notifications:False"]
    assert desktop.calls == ["desktop:False"]
