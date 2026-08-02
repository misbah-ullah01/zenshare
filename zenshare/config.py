"""Configuration management for ZenShare."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator

from .constants import DEFAULT_CONFIG_PATH, USER_CONFIG_PATH
from .utils.exceptions import ConfigurationError
from .utils.helpers import ensure_parent_directory
from .utils.validation import normalize_app_names


class ZenShareConfig(BaseModel):
    """Validated ZenShare configuration model."""

    model_config = ConfigDict(extra="forbid")

    desktop_icons: bool = True
    do_not_disturb: bool = True
    change_wallpaper: bool = True
    wallpaper: str = "default"
    minimize_apps: list[str] = Field(default_factory=list)
    close_apps: list[str] = Field(default_factory=list)
    restore_timeout: int = 10
    logging: bool = True

    @field_validator("minimize_apps", "close_apps", mode="before")
    @classmethod
    def _normalize_app_list(cls, value: Any) -> list[str]:
        if value is None:
            return []
        if isinstance(value, str):
            value = [value]
        if not isinstance(value, list):
            raise TypeError("Expected a list of application names.")
        return normalize_app_names(value)

    @field_validator("wallpaper")
    @classmethod
    def _validate_wallpaper(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Wallpaper cannot be empty.")
        return value

    @field_validator("restore_timeout")
    @classmethod
    def _validate_restore_timeout(cls, value: int) -> int:
        if value < 0:
            raise ValueError("restore_timeout must be greater than or equal to zero.")
        return value


class ConfigManager:
    """Load, validate, and save ZenShare configuration files."""

    def __init__(self, config_path: Path = USER_CONFIG_PATH, defaults_path: Path = DEFAULT_CONFIG_PATH) -> None:
        self._config_path = config_path
        self._defaults_path = defaults_path

    @property
    def config_path(self) -> Path:
        """Return the user configuration path."""

        return self._config_path

    def load(self) -> ZenShareConfig:
        """Load and validate the user configuration."""

        defaults = self._load_yaml(self._defaults_path)
        user_config = self._load_yaml(self._config_path) if self._config_path.exists() else {}
        merged = {**defaults, **user_config}
        try:
            return ZenShareConfig.model_validate(merged)
        except Exception as exc:  # pragma: no cover - converted to domain exception
            raise ConfigurationError(f"Invalid ZenShare configuration: {exc}") from exc

    def save(self, config: ZenShareConfig) -> None:
        """Persist the provided configuration to disk."""

        ensure_parent_directory(self._config_path)
        with self._config_path.open("w", encoding="utf-8") as handle:
            yaml.safe_dump(config.model_dump(), handle, sort_keys=False)

    def update(self, **changes: Any) -> ZenShareConfig:
        """Apply partial updates and save the result."""

        current = self.load()
        merged = current.model_dump()
        merged.update(changes)
        updated = ZenShareConfig.model_validate(merged)
        self.save(updated)
        return updated

    @staticmethod
    def _load_yaml(path: Path) -> dict[str, Any]:
        if not path.exists():
            return {}
        with path.open("r", encoding="utf-8") as handle:
            loaded = yaml.safe_load(handle) or {}
        if not isinstance(loaded, dict):
            raise ConfigurationError(f"Configuration file {path} must contain a mapping.")
        return loaded