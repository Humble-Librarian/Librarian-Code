import os
import tomllib
from pathlib import Path

CONFIG_FILE = "librarian.toml"

DEFAULTS = {
    "model": "all-MiniLM-L6-v2",
    "max_results": 5,
    "distance_threshold": 2.5,
    "auto_verify": True,
    "max_history": 20,
}


def load_config() -> dict:
    config = dict(DEFAULTS)

    config_path = Path(CONFIG_FILE)
    if config_path.exists():
        with open(config_path, "rb") as f:
            user_config = tomllib.load(f)
        if "librarian" in user_config:
            config.update(user_config["librarian"])

    if os.getenv("GROQ_API_KEY"):
        config["provider"] = "groq"
    elif os.getenv("OPENROUTER_API_KEY"):
        config["provider"] = "openrouter"

    return config


def get_config_value(key: str, default=None):
    config = load_config()
    return config.get(key, default)
