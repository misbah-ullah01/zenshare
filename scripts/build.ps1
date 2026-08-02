$ErrorActionPreference = 'Stop'

python -m PyInstaller `
  --clean `
  --onefile `
  --name ZenShare `
  --console `
  zenshare\__main__.py