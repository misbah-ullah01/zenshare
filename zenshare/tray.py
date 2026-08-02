"""Tray mode for background ZenShare control."""

from __future__ import annotations

import os
import threading

import pystray
from PIL import Image, ImageDraw

from .app import ZenShareApp
from .constants import APP_NAME, STATE_DIR


class TrayController:
    """Run ZenShare as a Windows tray application."""

    def __init__(self, app: ZenShareApp) -> None:
        self._app = app
        self._icon = pystray.Icon(APP_NAME, self._build_icon(), APP_NAME, self._build_menu())
        self._notification_guard_stop = threading.Event()

    def run(self) -> None:
        """Run the tray icon until the user exits."""

        pid_path = STATE_DIR / "tray.pid"
        pid_path.parent.mkdir(parents=True, exist_ok=True)
        pid_path.write_text(str(os.getpid()), encoding="utf-8")
        threading.Thread(target=self._guard_notification_banners, daemon=True).start()
        try:
            self._icon.run()
        finally:
            self._notification_guard_stop.set()
            if pid_path.exists() and pid_path.read_text(encoding="utf-8").strip() == str(os.getpid()):
                pid_path.unlink()

    def _build_menu(self) -> pystray.Menu:
        return pystray.Menu(
            pystray.MenuItem("Open ZenShare command window", self._open_console),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Start presentation mode", self._start_from_tray),
            pystray.MenuItem("Stop and restore desktop", self._stop_from_tray),
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
        self._run_action("Presentation mode", self._app.start)

    def _stop_from_tray(self, _icon: pystray.Icon, _item: pystray.MenuItem) -> None:
        self._run_action("Desktop restore", self._app.stop)

    def _show_status_from_tray(self, _icon: pystray.Icon, _item: pystray.MenuItem) -> None:
        status = self._app.status()
        message = "Presentation mode is active." if status["state_exists"] else "Presentation mode is not active."
        self._icon.notify(message, APP_NAME)

    def _open_console(self, _icon: pystray.Icon, _item: pystray.MenuItem) -> None:
        from .shell import open_console

        open_console()

    def _run_action(self, label: str, action) -> None:
        """Run a potentially slow Windows operation without freezing the tray menu."""

        def worker() -> None:
            try:
                result = action()
                self._icon.notify(result.message, label)
            except Exception as exc:
                self._icon.notify(f"Failed: {exc}", label)

        threading.Thread(target=worker, daemon=True).start()

    def _guard_notification_banners(self) -> None:
        """Continuously remove shell-hosted banners while presentation mode is active."""

        from .windows.notifications import NotificationController

        controller = NotificationController()
        while not self._notification_guard_stop.wait(0.5):
            if not self._app.state_manager.exists():
                continue
            try:
                controller.dismiss_visible_notifications()
            except Exception:
                # This guard is best-effort; it must never interrupt tray control.
                continue

    def _open_config_from_tray(self, _icon: pystray.Icon, _item: pystray.MenuItem) -> None:
        config = self._app.config_manager.load()
        self._app.config_manager.save(config)
        os.startfile(str(self._app.config_manager.config_path))

    def _open_logs_from_tray(self, _icon: pystray.Icon, _item: pystray.MenuItem) -> None:
        log_path = self._app.logs_path()
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_path.touch(exist_ok=True)
        os.startfile(str(log_path))

    def _exit_from_tray(self, icon: pystray.Icon, _item: pystray.MenuItem) -> None:
        icon.stop()
