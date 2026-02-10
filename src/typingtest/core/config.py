"""Configuration management — persist user settings and score history."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from platformdirs import user_config_dir, user_data_dir

APP_NAME = "typing-test"

CONFIG_DIR = Path(user_config_dir(APP_NAME, ensure_exists=True))
DATA_DIR = Path(user_data_dir(APP_NAME, ensure_exists=True))

CONFIG_FILE = CONFIG_DIR / "config.json"
HISTORY_FILE = DATA_DIR / "history.json"

DEFAULTS: dict[str, Any] = {
    "language": "english",
    "theme": "midnight",
    "word_count": 30,
    "zoom": 1,
    "mode": "words",          # "words" or "code"
    "code_language": "python", # python, typescript, javascript, rust, go
}

THEMES = ["midnight", "forest", "sunset", "ocean", "mono"]
LANGUAGES = ["english", "french"]
MODES = ["words", "code"]
ZOOM_LEVELS = [0, 1, 2, 3]  # 0=compact, 1=normal, 2=large, 3=extra-large


# ── Zoom presets ──────────────────────────────────────────────────────
# Each level defines container width, padding, and letter spacing.

ZOOM_PRESETS: dict[int, dict[str, Any]] = {
    0: {"width": 90, "padding_x": 1, "padding_y": 0, "line_height": 0, "letter_spacing": 0, "label": "compact"},
    1: {"width": 76, "padding_x": 2, "padding_y": 1, "line_height": 0, "letter_spacing": 0, "label": "normal"},
    2: {"width": 60, "padding_x": 3, "padding_y": 1, "line_height": 1, "letter_spacing": 1, "label": "large"},
    3: {"width": 46, "padding_x": 4, "padding_y": 2, "line_height": 1, "letter_spacing": 2, "label": "x-large"},
}


def _load_json(path: Path) -> Any:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return None


def _save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


# ── Settings ──────────────────────────────────────────────────────────


def load_config() -> dict[str, Any]:
    """Load user settings, falling back to defaults."""
    data = _load_json(CONFIG_FILE)
    if data is None:
        data = dict(DEFAULTS)
        _save_json(CONFIG_FILE, data)
    # back-fill any new keys added in future versions
    for key, val in DEFAULTS.items():
        data.setdefault(key, val)
    return data


def save_config(cfg: dict[str, Any]) -> None:
    _save_json(CONFIG_FILE, cfg)


def cycle_option(cfg: dict[str, Any], key: str, options: list[str]) -> str:
    """Cycle a config value to the next option and persist."""
    current = cfg.get(key, options[0])
    idx = options.index(current) if current in options else -1
    new_val = options[(idx + 1) % len(options)]
    cfg[key] = new_val
    save_config(cfg)
    return new_val


def zoom_in(cfg: dict[str, Any]) -> int:
    """Increase zoom level (capped at max)."""
    current = cfg.get("zoom", 1)
    new_val = min(current + 1, max(ZOOM_LEVELS))
    cfg["zoom"] = new_val
    save_config(cfg)
    return new_val


def zoom_out(cfg: dict[str, Any]) -> int:
    """Decrease zoom level (capped at min)."""
    current = cfg.get("zoom", 1)
    new_val = max(current - 1, min(ZOOM_LEVELS))
    cfg["zoom"] = new_val
    save_config(cfg)
    return new_val


# ── Score History ─────────────────────────────────────────────────────


def load_history() -> list[dict[str, Any]]:
    data = _load_json(HISTORY_FILE)
    return data if isinstance(data, list) else []


def save_score(entry: dict[str, Any]) -> None:
    """Append a score entry to history."""
    history = load_history()
    history.append(entry)
    # keep last 100 scores
    if len(history) > 100:
        history = history[-100:]
    _save_json(HISTORY_FILE, history)
