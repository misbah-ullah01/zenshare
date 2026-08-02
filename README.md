# ZenShare

ZenShare is a Windows-only command-line utility that prepares a machine for screen sharing and restores the desktop afterward.

It is designed around a simple flow:

1. Save the current desktop state.
2. Apply presentation mode.
3. Restore everything on stop.

## What ZenShare Changes

- Desktop icons are hidden and restored.
- Notifications are suppressed and restored.
- Wallpaper is replaced with a clean temporary wallpaper and restored.
- Configured apps can be minimized.
- Configured apps can optionally be closed gracefully.
- The active state is stored in `state/state.json` while presentation mode is running.

## Install

ZenShare is meant to be easy to install on a new Windows PC.

### Option 1: Scripted setup

Run this from PowerShell in the project root:

```powershell
scripts\install.ps1
```

That script will:

- Create a local virtual environment in `.venv` if needed.
- Upgrade `pip`.
- Install the dependencies from `requirements.txt`.
- Install the tray and packaging dependencies needed for the background mode and exe build.

### Option 2: Build a single executable

To install dependencies and build a standalone executable:

```powershell
scripts\install.ps1 -Build
```

The executable is generated in `dist\ZenShare.exe`.

## Tray Mode

ZenShare can run in the Windows tray so you can keep it available in the background.

Start the tray app from the virtual environment:

```powershell
scripts\run.ps1 tray
```

From the tray menu you can:

- Start presentation mode.
- Stop and restore the desktop.
- Show the current status.
- Open the config file.
- Open the logs.
- Exit the tray app.

If you build the exe, the same command line works:

```powershell
ZenShare.exe tray
```

## Run

If you want to run the CLI from the virtual environment, use:

```powershell
scripts\run.ps1 start
```

The main commands are:

- `zenshare start`
- `zenshare stop`
- `zenshare status`
- `zenshare config`
- `zenshare logs`
- `zenshare tray`

## Configuration

The default configuration lives in `config/config.yaml`.

Useful settings:

- `desktop_icons`: set to `true` so ZenShare hides and restores desktop icons during start and stop.
- `do_not_disturb`: set to `true` to suppress notifications.
- `change_wallpaper`: set to `true` to swap in a clean wallpaper.
- `minimize_apps`: list of apps to minimize, for example `Discord`, `WhatsApp`, `Slack`, and `Telegram`.
- `close_apps`: list of apps to close gracefully.
- `restore_timeout`: restore timeout in seconds.

You can update the config from the CLI:

```powershell
zenshare config --set desktop_icons=true --set do_not_disturb=true --set restore_timeout=15
```

## Start And Stop

Start presentation mode:

```powershell
zenshare start
```

Stop and restore the desktop state:

```powershell
zenshare stop
```

## Browser Privacy Shield

The optional Chromium-based companion extension is in [browser-privacy-extension](browser-privacy-extension).

It blurs pages that look like login, signup, registration, password, or verification screens. That helps keep sensitive content harder to read when a browser is on screen.

Install it in Chrome or Edge as an unpacked extension if you want browser-level privacy protection alongside the CLI.

## Notes

- ZenShare is Windows-only.
- The project is already wired for Python 3.12+.
- Use the scripts above for the easiest setup path on a fresh machine.
- The clean wallpaper is generated as a PNG in `state\zenshare_clean_wallpaper.png` while presentation mode is active.