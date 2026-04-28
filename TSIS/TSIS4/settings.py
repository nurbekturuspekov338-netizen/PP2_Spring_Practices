# settings.py — Load / save user preferences from settings.json

import json
import os

SETTINGS_FILE = os.path.join(os.path.dirname(__file__), "settings.json")

DEFAULTS = {
    "snake_color": [200, 200, 0],   # RGB list
    "grid": True,
    "sound": True,
}


def load() -> dict:
    """Load settings from file; fill missing keys with defaults."""
    if not os.path.exists(SETTINGS_FILE):
        save(DEFAULTS.copy())
        return DEFAULTS.copy()
    try:
        with open(SETTINGS_FILE, "r") as f:
            data = json.load(f)
        # Fill any missing keys
        for k, v in DEFAULTS.items():
            data.setdefault(k, v)
        return data
    except (json.JSONDecodeError, OSError):
        return DEFAULTS.copy()


def save(settings: dict):
    """Persist settings to file."""
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=2)
