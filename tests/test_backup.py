"""Tests for ZenShare backup and start flow."""

from __future__ import annotations

from pathlib import Path

from zenshare.config import ZenShareConfig
from zenshare.presentation import PresentationManager
from zenshare.state import PresentationState, StateManager


class FakeDesktopController:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def backup_visibility(self) -> bool:
        return True

    def hide_icons(self) -> None:
        self.calls.append("hide")

    def restore_icons(self, visible: bool) -> None:
        self.calls.append(f"restore:{visible}")


class FakeNotificationController:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def backup_state(self) -> dict[str, bool]:
        return {"toast_enabled": True, "global_toasts_enabled": True, "do_not_disturb_enabled": False}

    def enable_suppression(self) -> None:
        self.calls.append("suppress")

    def restore(self, enabled: dict[str, bool] | bool) -> None:
        self.calls.append(f"restore:{enabled}")


class FakeWallpaperController:
    def __init__(self, wallpaper_path: str) -> None:
        self.calls: list[str] = []
        self.wallpaper_path = wallpaper_path

    def backup_wallpaper(self) -> str:
        return self.wallpaper_path

    def apply_clean_wallpaper(self, target_directory: Path, wallpaper: str = "default") -> Path:
        self.calls.append(str(target_directory))
        wallpaper_file = target_directory / "clean.bmp"
        wallpaper_file.write_text("bmp", encoding="utf-8")
        return wallpaper_file

    def restore_wallpaper(self, wallpaper_path: str) -> None:
        self.calls.append(f"restore:{wallpaper_path}")


class FakeProcessController:
    def __init__(self) -> None:
        self.calls: list[tuple[str, tuple[str, ...]]] = []

    def find_running_apps(self, app_names: list[str]) -> list[str]:
        self.calls.append(("find", tuple(app_names)))
        return list(app_names)

    def minimize_apps(self, app_names: list[str]):
        self.calls.append(("minimize", tuple(app_names)))
        return type("Result", (), {"matched_apps": ["Discord"]})()

    def close_apps(self, app_names: list[str]):
        self.calls.append(("close", tuple(app_names)))
        return type("Result", (), {"matched_apps": ["Teams"]})()

    def restore_apps(self, app_names: list[str]) -> None:
        self.calls.append(("restore", tuple(app_names)))


def test_start_writes_a_backup_and_tracks_minimized_apps(tmp_path: Path) -> None:
    """Starting presentation mode should persist a backup state."""

    state_manager = StateManager(state_path=tmp_path / "state.json")
    desktop = FakeDesktopController()
    notifications = FakeNotificationController()
    wallpaper = FakeWallpaperController("C:/Users/Test/wallpaper.jpg")
    processes = FakeProcessController()
    manager = PresentationManager(
        state_manager=state_manager,
        desktop_controller=desktop,
        notification_controller=notifications,
        wallpaper_controller=wallpaper,
        process_controller=processes,
        state_directory=tmp_path,
    )
    config = ZenShareConfig(
        desktop_icons=True,
        do_not_disturb=True,
        change_wallpaper=True,
        wallpaper="default",
        minimize_apps=["Discord"],
        close_apps=["Teams"],
        restore_timeout=10,
        logging=False,
    )

    result = manager.start(config)

    assert result.state is not None
    assert state_manager.exists() is True
    loaded = state_manager.load()
    assert loaded is not None
    assert loaded.desktop_icons is True
    assert loaded.wallpaper == "C:/Users/Test/wallpaper.jpg"
    assert loaded.focus_assist == {"toast_enabled": True, "global_toasts_enabled": True, "do_not_disturb_enabled": False}
    assert loaded.running_apps == ["Discord", "Teams"]
    assert loaded.minimized == ["Discord"]
    assert desktop.calls == ["hide"]
    assert notifications.calls == ["suppress"]
    assert processes.calls == [
        ("find", ("Discord", "Teams")),
        ("minimize", ("Discord",)),
        ("close", ("Teams",)),
    ]
