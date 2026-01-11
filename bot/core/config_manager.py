from importlib import import_module
from os import getenv


class Config:
    AS_DOCUMENT = False
    AUTHORIZED_CHATS = ""
    BASE_URL = ""
    BASE_URL_PORT = 80
    BOT_TOKEN = ""
    BOT_MAX_TASKS = 0
    BOT_PM = False
    CMD_SUFFIX = ""
    DEFAULT_LANG = "en"
    DATABASE_URL = ""
    DELETE_LINKS = False
    DISABLE_BULK = False
    DISABLE_MULTI = False
    DISABLE_FF_MODE = False
    EQUAL_SPLITS = False
    EXCLUDED_EXTENSIONS = ""
    FFMPEG_CMDS = {}
    HELPER_TOKENS = ""
    MEDIA_STORE = True
    AUTHOR_NAME = "WZML-X"
    AUTHOR_URL = "https://t.me/WZML_X"
    INCOMPLETE_TASK_NOTIFIER = False
    INDEX_URL = ""
    YTDLP_LIMIT = 0
    PLAYLIST_LIMIT = 0
    LEECH_LIMIT = 0
    EXTRACT_LIMIT = 0
    ARCHIVE_LIMIT = 0
    STORAGE_LIMIT = 0
    LEECH_DUMP_CHAT = ""
    LINKS_LOG_ID = ""
    MIRROR_LOG_ID = ""
    CLEAN_LOG_MSG = False
    LEECH_PREFIX = ""
    LEECH_CAPTION = ""
    LEECH_SUFFIX = ""
    LEECH_FONT = ""
    LEECH_SPLIT_SIZE = 2097152000
    MEDIA_GROUP = False
    HYBRID_LEECH = True
    NAME_SWAP = ""
    OWNER_ID = 0
    QUEUE_ALL = 0
    QUEUE_DOWNLOAD = 0
    QUEUE_UPLOAD = 0
    RSS_CHAT = ""
    RSS_DELAY = 600
    RSS_SIZE_LIMIT = 0
    RCLONE_FLAGS = ""
    SET_COMMANDS = True
    STATUS_LIMIT = 10
    STATUS_UPDATE_INTERVAL = 15
    STOP_DUPLICATE = False
    SUDO_USERS = ""
    TELEGRAM_API = 0
    TELEGRAM_HASH = ""
    TG_PROXY = None
    THUMBNAIL_LAYOUT = ""
    LOGIN_PASS = ""
    TIMEZONE = "Asia/Kolkata"
    USER_MAX_TASKS = 0
    USER_TIME_INTERVAL = 0
    UPLOAD_PATHS = {}
    UPSTREAM_REPO = ""
    UPSTREAM_BRANCH = "master"
    UPDATE_PKGS = True
    USER_SESSION_STRING = ""
    USER_TRANSMISSION = True
    USE_SERVICE_ACCOUNTS = False
    YT_DLP_OPTIONS = {}

    @classmethod
    def get(cls, key):
        return getattr(cls, key) if hasattr(cls, key) else None

    @classmethod
    def set(cls, key, value):
        if hasattr(cls, key):
            value = cls._convert_env_type(key, value)
            setattr(cls, key, value)
        else:
            raise KeyError(f"{key} is not a valid configuration key.")

    @classmethod
    def get_all(cls):
        return {
            key: getattr(cls, key)
            for key in cls.__dict__.keys()
            if not key.startswith("__") and not callable(getattr(cls, key))
        }

    @classmethod
    def load(cls):
        cls.load_config()
        cls.load_env()

    @classmethod
    def load_config(cls):
        try:
            settings = import_module("config")
        except ModuleNotFoundError:
            return
        for attr in dir(settings):
            if hasattr(cls, attr):
                value = getattr(settings, attr)
                if not value:
                    continue
                if isinstance(value, str):
                    value = value.strip()
                if attr in [
                    "BASE_URL",
                    "INDEX_URL",
                ]:
                    if value:
                        value = value.strip("/")
                setattr(cls, attr, value)
        for key in ["BOT_TOKEN", "OWNER_ID", "TELEGRAM_API", "TELEGRAM_HASH"]:
            value = getattr(cls, key)
            if isinstance(value, str):
                value = value.strip()
            if not value:
                raise ValueError(f"{key} variable is missing!")

    @classmethod
    def load_env(cls):
        config_vars = cls.get_all()
        for key in config_vars:
            env_value = getenv(key)
            if env_value is not None:
                converted_value = cls._convert_env_type(key, env_value)
                cls.set(key, converted_value)

    @classmethod
    def _convert_env_type(cls, key, value):
        original_value = getattr(cls, key, None)
        if original_value is None:
            return value
        elif isinstance(original_value, bool):
            if isinstance(value, bool):
                return value
            return str(value).lower() in ("true", "1", "yes")
        elif isinstance(original_value, int):
            if isinstance(value, int):
                return value
            try:
                return int(value)
            except (ValueError, TypeError):
                return original_value
        elif isinstance(original_value, float):
            if isinstance(value, float):
                return value
            try:
                return float(value)
            except (ValueError, TypeError):
                return original_value
        return value

    @classmethod
    def load_dict(cls, config_dict):
        for key, value in config_dict.items():
            if hasattr(cls, key):
                if key in [
                    "BASE_URL",
                    "INDEX_URL",
                ]:
                    if value:
                        value = value.strip("/")
                value = cls._convert_env_type(key, value)
                setattr(cls, key, value)
        for key in ["BOT_TOKEN", "OWNER_ID", "TELEGRAM_API", "TELEGRAM_HASH"]:
            value = getattr(cls, key)
            if isinstance(value, str):
                value = value.strip()
            if not value:
                raise ValueError(f"{key} variable is missing!")


class BinConfig:
    FFMPEG_NAME = "ffmpeg"
