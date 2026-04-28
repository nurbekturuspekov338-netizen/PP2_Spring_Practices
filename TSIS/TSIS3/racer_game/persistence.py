import json
import os

LEADERBOARD_FILE = "leaderboard.json"
SETTINGS_FILE = "settings.json"

DEFAULT_SETTINGS = {
    "sound": True,
    "car_color": "blue",  # blue, red, green, yellow
    "difficulty": "medium"  # easy, medium, hard
}

# ── Leaderboard ──────────────────────────────────────────────────────────────

def load_leaderboard():
    if not os.path.exists(LEADERBOARD_FILE):
        return []
    try:
        with open(LEADERBOARD_FILE, "r") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, IOError):
        return []


def save_leaderboard(entries):
    """entries: list of dicts with keys: name, score, distance, coins"""
    entries_sorted = sorted(entries, key=lambda e: e.get("score", 0), reverse=True)
    top10 = entries_sorted[:10]
    try:
        with open(LEADERBOARD_FILE, "w") as f:
            json.dump(top10, f, indent=2)
    except IOError:
        pass
    return top10


def add_leaderboard_entry(name, score, distance, coins):
    entries = load_leaderboard()
    entries.append({"name": name, "score": score, "distance": int(distance), "coins": coins})
    return save_leaderboard(entries)


# ── Settings ─────────────────────────────────────────────────────────────────

def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        return dict(DEFAULT_SETTINGS)
    try:
        with open(SETTINGS_FILE, "r") as f:
            data = json.load(f)
        # Fill in any missing keys with defaults
        for k, v in DEFAULT_SETTINGS.items():
            data.setdefault(k, v)
        return data
    except (json.JSONDecodeError, IOError):
        return dict(DEFAULT_SETTINGS)


def save_settings(settings):
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(settings, f, indent=2)
    except IOError:
        pass
