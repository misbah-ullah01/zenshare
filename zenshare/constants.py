"""Project-wide constants for ZenShare."""

from .utils.paths import application_data_root, bundled_root

APP_NAME = "ZenShare"
APP_VERSION = "0.1.0"

ROOT_DIR = application_data_root()
BUNDLED_ROOT_DIR = bundled_root()
CONFIG_DIR = ROOT_DIR / "config"
DEFAULT_CONFIG_PATH = BUNDLED_ROOT_DIR / "config" / "defaults.yaml"
USER_CONFIG_PATH = CONFIG_DIR / "config.yaml"
LOG_DIR = ROOT_DIR / "logs"
LOG_FILE_PATH = LOG_DIR / "zenshare.log"
STATE_DIR = ROOT_DIR / "state"
STATE_FILE_PATH = STATE_DIR / "state.json"
SCRIPTS_DIR = ROOT_DIR / "scripts"
DEFAULT_WALLPAPER_PATH = BUNDLED_ROOT_DIR / "assets" / "ZenShare.png"

SUPPORTED_APPS = ["Discord", "WhatsApp", "Slack", "Telegram", "Teams"]

DEFAULT_CLEAN_WALLPAPER_NAME = "zenshare_clean_wallpaper.png"
DEFAULT_WALLPAPER_SIZE = (1920, 1080)
