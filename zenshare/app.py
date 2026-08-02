"""High-level ZenShare application services."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .config import ConfigManager, ZenShareConfig
from .constants import LOG_FILE_PATH
from .logger import configure_logging
from .presentation import PresentationManager, PresentationResult
from .state import StateManager
from .windows.desktop import DesktopController
from .windows.notifications import NotificationController
from .windows.processes import ProcessController
from .windows.wallpaper import WallpaperController


@dataclass(slots=True)
class ZenShareApp:
    """Application service object used by the CLI and tests."""

    config_manager: ConfigManager
    state_manager: StateManager
    presentation_manager: PresentationManager

    @classmethod
    def default(cls) -> "ZenShareApp":
        """Build the default application wiring."""

        config_manager = ConfigManager()
        state_manager = StateManager()
        presentation_manager = PresentationManager(
            state_manager=state_manager,
            desktop_controller=DesktopController(),
            notification_controller=NotificationController(),
            wallpaper_controller=WallpaperController(),
            process_controller=ProcessController(),
        )
        return cls(config_manager=config_manager, state_manager=state_manager, presentation_manager=presentation_manager)

    def initialize_logging(self, config: ZenShareConfig) -> None:
        """Set up logging for the current command."""

        configure_logging(enabled=config.logging, log_path=LOG_FILE_PATH)

    def start(self) -> PresentationResult:
        """Start presentation mode."""

        config = self.config_manager.load()
        self.initialize_logging(config)
        return self.presentation_manager.start(config)

    def stop(self) -> PresentationResult:
        """Stop presentation mode and restore the previous state."""

        config = self.config_manager.load()
        self.initialize_logging(config)
        return self.presentation_manager.stop()

    def status(self) -> dict[str, object]:
        """Return application status information."""

        config = self.config_manager.load()
        self.initialize_logging(config)
        return {"config": config, "state_exists": self.state_manager.exists(), "state": self.state_manager.load()}

    def config(self) -> ZenShareConfig:
        """Return the loaded configuration."""

        return self.config_manager.load()

    def logs_path(self) -> Path:
        """Return the log file path."""

        return LOG_FILE_PATH