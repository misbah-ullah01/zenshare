"""Presentation mode orchestration for ZenShare."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from loguru import logger

from .config import ZenShareConfig
from .constants import STATE_DIR
from .state import PresentationState, StateManager
from .utils.exceptions import ZenShareError
from .windows.desktop import DesktopController
from .windows.notifications import NotificationController
from .windows.processes import ProcessController
from .windows.wallpaper import WallpaperController


@dataclass(slots=True)
class PresentationResult:
    """Result returned by presentation mode operations."""

    message: str
    state: PresentationState | None = None


class PresentationManager:
    """Coordinate backup, presentation mode, and restoration steps."""

    def __init__(
        self,
        *,
        state_manager: StateManager,
        desktop_controller: DesktopController,
        notification_controller: NotificationController,
        wallpaper_controller: WallpaperController,
        process_controller: ProcessController,
        state_directory: Path = STATE_DIR,
    ) -> None:
        self._state_manager = state_manager
        self._desktop_controller = desktop_controller
        self._notification_controller = notification_controller
        self._wallpaper_controller = wallpaper_controller
        self._process_controller = process_controller
        self._state_directory = state_directory

    def start(self, config: ZenShareConfig) -> PresentationResult:
        """Apply presentation mode while backing up the original state."""

        logger.info("Preparing presentation mode.")
        backup = self._build_backup_state()
        self._state_manager.save(backup)

        try:
            if config.desktop_icons:
                self._desktop_controller.hide_icons()
                logger.info("Desktop icons hidden.")

            if config.do_not_disturb:
                self._notification_controller.enable_suppression()
                logger.info("Notification suppression enabled.")

            if config.change_wallpaper:
                clean_wallpaper = self._wallpaper_controller.apply_clean_wallpaper(self._state_directory)
                logger.info("Wallpaper changed to {}.", clean_wallpaper)

            minimized_result = self._process_controller.minimize_apps(config.minimize_apps)
            if minimized_result.matched_apps:
                backup = backup.model_copy(update={"minimized": minimized_result.matched_apps})
                self._state_manager.save(backup)
                logger.info("Minimized apps: {}.", ", ".join(minimized_result.matched_apps))

            logger.info("Presentation mode enabled.")
            return PresentationResult(message="Presentation mode enabled.", state=backup)
        except Exception as exc:
            logger.exception("Presentation mode failed; starting rollback.")
            self._restore_from_backup(backup)
            raise ZenShareError(f"Failed to start presentation mode: {exc}") from exc

    def stop(self) -> PresentationResult:
        """Restore the previously backed up desktop state."""

        backup = self._state_manager.load()
        if backup is None:
            return PresentationResult(message="No active ZenShare state file was found.")

        self._restore_from_backup(backup)
        self._state_manager.delete()
        logger.info("Presentation state restored.")
        return PresentationResult(message="Presentation state restored.", state=backup)

    def status(self) -> dict[str, object]:
        """Return a status snapshot for the CLI."""

        return {"active": self._state_manager.exists(), "state": self._state_manager.load()}

    def _build_backup_state(self) -> PresentationState:
        return PresentationState(
            desktop_icons=self._desktop_controller.backup_visibility(),
            wallpaper=self._wallpaper_controller.backup_wallpaper(),
            focus_assist=self._notification_controller.backup_state(),
        )

    def _restore_from_backup(self, backup: PresentationState) -> None:
        try:
            if backup.minimized:
                self._process_controller.restore_apps(backup.minimized)
                logger.info("Restored minimized apps.")
            if backup.wallpaper is not None:
                self._wallpaper_controller.restore_wallpaper(backup.wallpaper)
                logger.info("Wallpaper restored.")
            if backup.focus_assist is not None:
                self._notification_controller.restore(backup.focus_assist)
                logger.info("Notification state restored.")
            if backup.desktop_icons is not None:
                self._desktop_controller.restore_icons(backup.desktop_icons)
                logger.info("Desktop icons restored.")
        except Exception as exc:
            raise ZenShareError(f"Failed to restore ZenShare state: {exc}") from exc