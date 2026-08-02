"""State persistence for ZenShare."""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from .constants import STATE_FILE_PATH
from .utils.exceptions import StateError
from .utils.helpers import current_timestamp, ensure_parent_directory


class PresentationState(BaseModel):
    """Snapshot of desktop state captured before presentation mode starts."""

    model_config = ConfigDict(extra="forbid")

    desktop_icons: bool | None = None
    wallpaper: str | None = None
    focus_assist: bool | None = None
    running_apps: list[str] = Field(default_factory=list)
    minimized: list[str] = Field(default_factory=list)
    created_at: str = Field(default_factory=current_timestamp)


class StateManager:
    """Read and write ZenShare state files."""

    def __init__(self, state_path: Path = STATE_FILE_PATH) -> None:
        self._state_path = state_path

    @property
    def state_path(self) -> Path:
        """Return the current state file path."""

        return self._state_path

    def exists(self) -> bool:
        """Return whether a state file currently exists."""

        return self._state_path.exists()

    def load(self) -> PresentationState | None:
        """Load the stored state or return ``None`` when it is missing."""

        if not self._state_path.exists():
            return None
        try:
            with self._state_path.open("r", encoding="utf-8") as handle:
                payload = json.load(handle)
            if not isinstance(payload, dict):
                raise StateError("State file must contain a JSON object.")
            return PresentationState.model_validate(payload)
        except Exception as exc:  # pragma: no cover - converted to domain exception
            raise StateError(f"Unable to load ZenShare state: {exc}") from exc

    def save(self, state: PresentationState) -> None:
        """Persist the provided state snapshot."""

        ensure_parent_directory(self._state_path)
        with self._state_path.open("w", encoding="utf-8") as handle:
            json.dump(state.model_dump(mode="json"), handle, indent=2)
            handle.write("\n")

    def delete(self) -> None:
        """Remove the stored state file if it exists."""

        if self._state_path.exists():
            self._state_path.unlink()