"""Interactive console shell that keeps ZenShare available in the notification area."""

from __future__ import annotations

import os
import shlex
import subprocess
import sys

import click
import psutil
from rich.console import Console
from rich.panel import Panel

from .constants import APP_NAME, STATE_DIR

console = Console()


def _tray_pid_path():
    return STATE_DIR / "tray.pid"


def _tray_is_running() -> bool:
    pid_path = _tray_pid_path()
    try:
        return psutil.pid_exists(int(pid_path.read_text(encoding="utf-8").strip()))
    except (FileNotFoundError, ValueError):
        return False


def _start_tray_process() -> None:
    """Start one detached tray process for this interactive console session."""

    if _tray_is_running():
        return
    creationflags = 0
    if sys.platform == "win32":
        creationflags = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.CREATE_NO_WINDOW
    command = [sys.executable, "tray", "--quiet"]
    if not getattr(sys, "frozen", False):
        command = [sys.executable, "-m", "zenshare", "tray", "--quiet"]
    subprocess.Popen(
        command,
        close_fds=True,
        creationflags=creationflags,
    )


def _stop_tray_process() -> None:
    """Stop the tray process started for the console shell."""

    pid_path = _tray_pid_path()
    try:
        process = psutil.Process(int(pid_path.read_text(encoding="utf-8").strip()))
        process.terminate()
    except (FileNotFoundError, ValueError, psutil.Error):
        pass


def open_console() -> None:
    """Open a fresh interactive ZenShare command window from the tray."""

    creationflags = 0
    command = [sys.executable]
    if sys.platform == "win32":
        creationflags = subprocess.CREATE_NEW_CONSOLE
    if not getattr(sys, "frozen", False):
        command = [sys.executable, "-m", "zenshare"]
    subprocess.Popen(command, close_fds=True, creationflags=creationflags)


def run_shell(command: click.BaseCommand) -> None:
    """Run an interactive command prompt and leave the tray active on window close."""

    _start_tray_process()
    console.print(
        Panel(
            "Presentation mode is changed only by `start` and `stop`.\n"
            "Commands: start, stop, status, config, logs, help, exit\n"
            "Closing this console keeps ZenShare running in the system tray.\n"
            "Type `exit` to close ZenShare completely.",
            title=APP_NAME,
        )
    )
    while True:
        try:
            line = input("zenshare> ").strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\nZenShare is still running in the system tray.")
            return
        if not line:
            continue
        if line.lower() in {"exit", "quit"}:
            _stop_tray_process()
            console.print("ZenShare exited.")
            return
        if line.lower() in {"help", "?"}:
            command.main(args=["--help"], standalone_mode=False)
            continue
        try:
            command.main(args=shlex.split(line), standalone_mode=False)
        except (click.ClickException, click.Abort) as exc:
            console.print(f"[red]{exc}[/red]")
        except SystemExit:
            # Click uses SystemExit for help and validation failures.
            continue
