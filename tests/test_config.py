"""Tests for ZenShare configuration loading and saving."""

from __future__ import annotations

from pathlib import Path

import pytest

from zenshare.config import ConfigManager, ZenShareConfig
from zenshare.utils.exceptions import ConfigurationError


def test_loads_defaults_when_user_config_is_missing(tmp_path: Path) -> None:
    """The manager should fall back to defaults when no user config exists."""

    defaults_path = tmp_path / "defaults.yaml"
    defaults_path.write_text(
        """
desktop_icons: false
do_not_disturb: true
change_wallpaper: false
wallpaper: default
minimize_apps:
  - Discord
close_apps: []
restore_timeout: 7
logging: false
""".strip(),
        encoding="utf-8",
    )
    manager = ConfigManager(config_path=tmp_path / "config.yaml", defaults_path=defaults_path)

    loaded = manager.load()

    assert loaded.desktop_icons is False
    assert loaded.change_wallpaper is False
    assert loaded.minimize_apps == ["Discord"]
    assert loaded.restore_timeout == 7
    assert loaded.logging is False


def test_save_and_update_roundtrip(tmp_path: Path) -> None:
    """Saving then updating should keep the config valid."""

    defaults_path = tmp_path / "defaults.yaml"
    defaults_path.write_text("desktop_icons: true\nwallpaper: default\n", encoding="utf-8")
    config_path = tmp_path / "config.yaml"
    manager = ConfigManager(config_path=config_path, defaults_path=defaults_path)

    manager.save(
        ZenShareConfig(
            desktop_icons=True,
            do_not_disturb=True,
            change_wallpaper=True,
            wallpaper="default",
            minimize_apps=["Discord"],
            close_apps=[],
            restore_timeout=10,
            logging=True,
        )
    )

    updated = manager.update(logging=False, minimize_apps=["Slack", "Slack", "Telegram"])

    assert updated.logging is False
    assert updated.minimize_apps == ["Slack", "Telegram"]
    assert config_path.exists()


def test_invalid_config_raises_configuration_error(tmp_path: Path) -> None:
    """A malformed YAML structure should be rejected."""

    defaults_path = tmp_path / "defaults.yaml"
    defaults_path.write_text("desktop_icons: true\nwallpaper: default\n", encoding="utf-8")
    config_path = tmp_path / "config.yaml"
    config_path.write_text("- not-a-mapping\n- still-not-a-mapping\n", encoding="utf-8")
    manager = ConfigManager(config_path=config_path, defaults_path=defaults_path)

    with pytest.raises(ConfigurationError):
        manager.load()