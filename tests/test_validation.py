"""Tests for ZenShare validation helpers."""

from __future__ import annotations

from zenshare.utils.validation import app_name_matches, process_matches_target


def test_app_name_matches_windows_exe_names() -> None:
    """Configured app names should match Windows executable names."""

    assert app_name_matches("Discord.exe", "Discord") is True
    assert app_name_matches("C:/Program Files/Discord/Discord.exe", "Discord") is True
    assert app_name_matches("WhatsApp", "WhatsApp") is True


def test_process_matches_target_uses_executable_and_cmdline() -> None:
    """Process matching should check the executable path and command line too."""

    assert process_matches_target(
        process_name="Update.exe",
        process_executable="C:/Users/Test/AppData/Local/Discord/Update.exe",
        command_line=["C:/Users/Test/AppData/Local/Discord/Update.exe", "--processStart", "Discord.exe"],
        target="Discord",
    ) is True

    assert process_matches_target(
        process_name="chrome.exe",
        process_executable="C:/Program Files/Google/Chrome/Application/chrome.exe",
        command_line=["chrome.exe"],
        target="Slack",
    ) is False