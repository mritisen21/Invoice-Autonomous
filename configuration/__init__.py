from __future__ import annotations

import json
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent
CONFIG_FILE = BASE_DIR / "config.json"

__all__ = ["load_config", "BASE_DIR", "CONFIG_FILE"]


def load_config(path: Path | str | None = None) -> dict[str, Any]:
    config_path = Path(path) if path else CONFIG_FILE
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with config_path.open("r", encoding="utf-8") as file:
        return json.load(file)
