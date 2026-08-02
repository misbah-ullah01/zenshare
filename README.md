# ZenShare

ZenShare is a Windows-only command-line utility for preparing a desktop for professional screen sharing and restoring the original desktop state afterward.

## Current Scope

This workspace now contains the initial Python package scaffold for ZenShare v1.0:

- Click-based CLI entry points
- YAML configuration loading and saving
- JSON state persistence
- Loguru-based logging setup
- Windows controller abstractions for desktop icons, wallpaper, notifications, and processes
- Core presentation flow with rollback-friendly orchestration

## Commands

- `zenshare start`
- `zenshare stop`
- `zenshare status`
- `zenshare config`
- `zenshare logs`

## Next Steps

The next work item is adding unit tests for the config/state managers and the presentation flow, then validating the Windows-specific controllers more deeply.