"""PowerShell helpers for ZenShare."""

from __future__ import annotations

import subprocess

from ..utils.exceptions import WindowsOperationError


def run_script(script: str) -> str:
    """Run a PowerShell script and return its standard output."""

    completed = subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script],
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise WindowsOperationError(completed.stderr.strip() or "PowerShell command failed.")
    return completed.stdout.strip()