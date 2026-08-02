"""Tray mode for background ZenShare control."""

from __future__ import annotations

import os

import pystray
from PIL import Image, ImageDraw

from .app import ZenShareApp
from .constants import APP_NAME


class TrayController:
    """Run ZenShare as a Windows tray application."""

    def __init__(self, app: ZenShareApp) -> None:
        self._app = app
        self._icon = pystray.Icon(APP_NAME, self._build_icon(), APP_NAME, self._build_menu())

    def run(self) -> None:
        """Run the tray icon until the user exits."""

        self._icon.run()

    def _build_menu(self) -> pystray.Menu:
        return pystray.Menu(
            pystray.MenuItem("Start presentation mode", self._start_from_tray),
            pystray.MenuItem("Stop presentation mode", self._stop_from_tray),
            pystray.MenuItem("Show status", self._show_status_from_tray),
            pystray.MenuItem("Open config", self._open_config_from_tray),
            pystray.MenuItem("Open logs", self._open_logs_from_tray),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Exit", self._exit_from_tray),
        )

    def _build_icon(self) -> Image.Image:
        image = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.rounded_rectangle((6, 6, 58, 58), radius=14, fill=(32, 32, 32, 255))
        draw.rounded_rectangle((14, 14, 50, 50), radius=10, fill=(248, 248, 248, 255))
        draw.line((20, 32, 44, 32), fill=(32, 32, 32, 255), width=4)
        draw.line((32, 20, 32, 44), fill=(32, 32, 32, 255), width=4)
        return image

    def _start_from_tray(self, _icon: pystray.Icon, _item: pystray.MenuItem) -> None:
        self._app.start()

    def _stop_from_tray(self, _icon: pystray.Icon, _item: pystray.MenuItem) -> None:
        self._app.stop()

    def _show_status_from_tray(self, _icon: pystray.Icon, _item: pystray.MenuItem) -> None:
        status = self._app.status()
        print(status)

    def _open_config_from_tray(self, _icon: pystray.Icon, _item: pystray.MenuItem) -> None:
        os.startfile(str(self._app.config_manager.config_path))

    def _open_logs_from_tray(self, _icon: pystray.Icon, _item: pystray.MenuItem) -> None:
        log_path = self._app.logs_path()
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_path.touch(exist_ok=True)
        os.startfile(str(log_path))

    def _exit_from_tray(self, icon: pystray.Icon, _item: pystray.MenuItem) -> None:
        icon.stop()