# ZenShare

ZenShare gets a Windows desktop ready for screen sharing. It hides desktop icons, blocks and dismisses notification banners, applies your ZenShare wallpaper, and minimizes selected chat apps. When you finish, it restores the settings it changed.

## Fastest way to use it

1. Open [ZenShare.exe](dist/ZenShare.exe).
2. At the `zenshare>` prompt, type `start` and press Enter.
3. Share your screen.
4. Type `stop` when you are done to restore your desktop.

The prompt always accepts `help` if you want to see the available commands again.

## Keep ZenShare running in the tray

When you close the ZenShare command window with the **X**, ZenShare stays available in the Windows system tray (next to the clock).

Right-click the ZenShare tray icon to:

- **Open ZenShare command window** — bring back a full CLI window.
- **Start presentation mode** — prepare your desktop without reopening the CLI.
- **Stop and restore desktop** — return icons, wallpaper, and notification settings.
- **Show status** — see whether presentation mode is active.
- **Open config** or **Open logs** — open the relevant file.
- **Exit** — close the tray application.

Type `exit` in the CLI only when you want to close ZenShare completely.

## Commands

| Command | What it does |
| --- | --- |
| `start` | Turns on presentation mode. |
| `stop` | Restores the desktop to its saved state. |
| `status` | Shows whether presentation mode is active. |
| `config` | Shows current settings. |
| `config --set KEY=VALUE` | Changes and saves a setting. |
| `logs` | Shows recent activity and errors. |
| `help` | Shows the command reference in the interactive CLI. |
| `exit` | Closes ZenShare and its tray icon. |

Useful examples:

```powershell
ZenShare.exe start
ZenShare.exe status
ZenShare.exe config --set minimize_apps=Discord,Slack
ZenShare.exe config --set wallpaper=C:\Pictures\my-wallpaper.png
ZenShare.exe stop
```

## What `start` changes

- Hides desktop icons.
- Enables Do Not Disturb and disables new Windows toast banners.
- Dismisses any currently visible Windows notification banner where Windows exposes it.
- Applies the bundled ZenShare wallpaper.
- Minimizes Discord, WhatsApp, Slack, and Telegram by default.

ZenShare never closes your apps unless you explicitly add them to `close_apps` in the configuration.

## Wallpaper

The bundled ZenShare wallpaper is used by default. To use your own image, give its absolute path:

```powershell
ZenShare.exe config --set wallpaper=C:\Pictures\my-wallpaper.png
```

Use `ZenShare.exe stop` to restore your previous wallpaper.

## Configuration and logs

The EXE is self-contained. It does not need this repository, Python, or a virtual environment after it has been built. Its writable files are stored here:

```text
%LOCALAPPDATA%\ZenShare\config\config.yaml
%LOCALAPPDATA%\ZenShare\logs\zenshare.log
%LOCALAPPDATA%\ZenShare\state\state.json
```

## Build from source

Run this from the project root:

```powershell
scripts\install.ps1 -Build
```

The resulting single-file application is `dist\ZenShare.exe`.

## Browser login-page privacy

The optional `browser-privacy-extension` can blur browser login and password pages. It affects your browser view as well as the shared view; Windows cannot selectively blur an arbitrary third-party app for viewers only.
