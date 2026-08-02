"""Tests for ZenShare notification registry writes."""

from __future__ import annotations

from types import SimpleNamespace

from zenshare.windows.notifications import (
    DO_NOT_DISTURB_ENABLED_VALUE,
    GLOBAL_TOASTS_ENABLED_VALUE,
    NOTIFICATION_SETTINGS_KEY,
    NOTIFICATIONS_KEY,
    TOAST_ENABLED_VALUE,
    NotificationController,
)


class _FakeKey:
    def __init__(self, store: dict[str, dict[str, int]], path: str) -> None:
        self._store = store
        self._path = path

    def __enter__(self) -> "_FakeKey":
        self._store.setdefault(self._path, {})
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None


def test_enable_suppression_writes_expected_registry_values(monkeypatch) -> None:
    """Suppression should disable normal notifications and enable Do Not Disturb."""

    store: dict[str, dict[str, int]] = {}

    def fake_create_key_ex(root, path, *_args, **_kwargs):
        return _FakeKey(store, path)

    def fake_set_value_ex(handle, name, _reserved, _type, value):
        handle._store[handle._path][name] = value

    monkeypatch.setattr("zenshare.windows.notifications.winreg.CreateKeyEx", fake_create_key_ex)
    monkeypatch.setattr("zenshare.windows.notifications.winreg.SetValueEx", fake_set_value_ex)
    monkeypatch.setattr("zenshare.windows.notifications.refresh_shell", lambda: None)

    controller = NotificationController()
    controller.enable_suppression()

    assert store[NOTIFICATIONS_KEY][TOAST_ENABLED_VALUE] == 0
    assert store[NOTIFICATION_SETTINGS_KEY][GLOBAL_TOASTS_ENABLED_VALUE] == 0
    assert store[NOTIFICATION_SETTINGS_KEY][DO_NOT_DISTURB_ENABLED_VALUE] == 1


def test_restore_writes_expected_registry_values(monkeypatch) -> None:
    """Restoring should re-enable notifications and disable Do Not Disturb."""

    store: dict[str, dict[str, int]] = {}

    def fake_create_key_ex(root, path, *_args, **_kwargs):
        return _FakeKey(store, path)

    def fake_set_value_ex(handle, name, _reserved, _type, value):
        handle._store[handle._path][name] = value

    monkeypatch.setattr("zenshare.windows.notifications.winreg.CreateKeyEx", fake_create_key_ex)
    monkeypatch.setattr("zenshare.windows.notifications.winreg.SetValueEx", fake_set_value_ex)
    monkeypatch.setattr("zenshare.windows.notifications.refresh_shell", lambda: None)

    controller = NotificationController()
    controller.restore(True)

    assert store[NOTIFICATIONS_KEY][TOAST_ENABLED_VALUE] == 1
    assert store[NOTIFICATION_SETTINGS_KEY][GLOBAL_TOASTS_ENABLED_VALUE] == 1
    assert store[NOTIFICATION_SETTINGS_KEY][DO_NOT_DISTURB_ENABLED_VALUE] == 0