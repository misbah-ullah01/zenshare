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

The `config` command also supports updates, for example:

```powershell
zenshare config --set desktop_icons=false --set restore_timeout=15
```

## Install

For a fresh Windows machine:

```powershell
scripts\install.ps1
```

That creates `.venv`, installs the dependencies, and gets the project ready to run.

To start ZenShare from the virtual environment:

```powershell
scripts\run.ps1 start
```

To build a single executable:

```powershell
scripts\install.ps1 -Build
```

## Browser Privacy Shield

An optional Chromium-based companion extension lives in [browser-privacy-extension](browser-privacy-extension). It blurs pages that look like login, signup, registration, password, or verification screens.

This is separate from the CLI and can be loaded as an unpacked extension in Chrome or Edge.

## Next Steps

The remaining work is mostly operational hardening and real-machine validation for the Windows shell settings and the browser privacy companion.