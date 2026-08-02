"""Project-wide constants for ZenShare."""

from .utils.paths import project_root

APP_NAME = "ZenShare"
APP_VERSION = "0.1.0"

ROOT_DIR = project_root()
CONFIG_DIR = ROOT_DIR / "config"
DEFAULT_CONFIG_PATH = CONFIG_DIR / "defaults.yaml"
USER_CONFIG_PATH = CONFIG_DIR / "config.yaml"
LOG_DIR = ROOT_DIR / "logs"
LOG_FILE_PATH = LOG_DIR / "zenshare.log"
STATE_DIR = ROOT_DIR / "state"
STATE_FILE_PATH = STATE_DIR / "state.json"
SCRIPTS_DIR = ROOT_DIR / "scripts"

SUPPORTED_APPS = ["Discord", "WhatsApp", "Slack", "Telegram", "Teams"]

DEFAULT_CLEAN_WALLPAPER_NAME = "zenshare_clean_wallpaper.bmp"
DEFAULT_WALLPAPER_SIZE = (1920, 1080)