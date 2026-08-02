"""Tests for the ZenShare CLI."""

from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner

from zenshare.cli import main


class FakeApp:
    def __init__(self) -> None:
        self.started = False
        self.stopped = False
        self.updated_config: dict[str, object] = {}

        class _ConfigManager:
            def __init__(self, outer: "FakeApp") -> None:
                self._outer = outer

            def update(self, **changes):
                self._outer.updated_config = dict(changes)
                return type("Config", (), {"model_dump_json": lambda self, indent=2: "{\n  \"updated\": true\n}"})()

        self.config_manager = _ConfigManager(self)

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


def test_cli_config_update(monkeypatch) -> None:
    """The config command should persist updates when --set is provided."""

    fake_app = FakeApp()
    monkeypatch.setattr("zenshare.cli._build_app", lambda: fake_app)
    runner = CliRunner()

    result = runner.invoke(main, ["config", "--set", "desktop_icons=false", "--set", "restore_timeout=15"])

    assert result.exit_code == 0
    assert fake_app.updated_config == {"desktop_icons": False, "restore_timeout": 15}
    assert "updated" in result.output