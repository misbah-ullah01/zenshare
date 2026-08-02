param(
    [switch]$Build
)

$ErrorActionPreference = 'Stop'

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptRoot
$venvPath = Join-Path $projectRoot '.venv'
$venvPython = Join-Path $venvPath 'Scripts\python.exe'

if (-not (Test-Path $venvPython)) {
    if (Get-Command py -ErrorAction SilentlyContinue) {
        & py -3 -m venv $venvPath
    }
    elseif (Get-Command python -ErrorAction SilentlyContinue) {
        & python -m venv $venvPath
    }
    else {
        throw 'Python 3.12+ is required and must be available through the Python Launcher or on PATH.'
    }
}

& $venvPython -m pip install --upgrade pip
& $venvPython -m pip install -r (Join-Path $projectRoot 'requirements.txt')

if ($Build) {
    & $venvPython -m PyInstaller --noconfirm --clean --onefile --console --name ZenShare --add-data "$projectRoot\config\defaults.yaml;config" --add-data "$projectRoot\assets\ZenShare.png;assets" --collect-all pystray --collect-all PIL --hidden-import zenshare.cli --hidden-import zenshare.tray --hidden-import zenshare.windows.notifications --hidden-import zenshare.windows.wallpaper --copy-metadata zenshare (Join-Path $projectRoot 'zenshare_cli.py')
}
