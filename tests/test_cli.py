"""Tests for the ZenShare CLI."""

from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner

from zenshare.cli import main


class FakeApp:
    def __init__(self) -> None:
        self.started = False
        self.stopped = False

    def start(self):
        self.started = True
        return type("Result", (), {"message": "Presentation mode enabled."})()

    def stop(self):
        self.stopped = True
        return type("Result", (), {"message": "Presentation state restored."})()

    def status(self):
        return {"state_exists": False, "state": None, "config": "mock-config"}

    def config(self):
        return type("Config", (), {"model_dump_json": lambda self, indent=2: "{\n  \"mock\": true\n}"})()

    def logs_path(self) -> Path:
        return Path("C:/temp/zenshare.log")


def test_cli_start_and_status(monkeypatch) -> None:
    """The CLI should dispatch commands through the app object."""

    fake_app = FakeApp()
    monkeypatch.setattr("zenshare.cli._build_app", lambda: fake_app)
    runner = CliRunner()

    start_result = runner.invoke(main, ["start"])
    status_result = runner.invoke(main, ["status"])

    assert start_result.exit_code == 0
    assert "Presentation mode enabled." in start_result.output
    assert status_result.exit_code == 0
    assert "mock-config" in status_result.output