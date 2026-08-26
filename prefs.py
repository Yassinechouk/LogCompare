# -*- coding: utf-8 -*-
"""
prefs.py – User Preferences Persistence
=========================================

Loads and saves application preferences (last-used paths, thresholds, etc.)
to a JSON file located in the user's home directory.
"""

import json
from typing import Dict, Any

from constants import PREFS_FILE


def load_prefs() -> Dict[str, Any]:
    """Load user preferences from disk.

    Returns:
        A dictionary with the saved preferences, or an empty dict
        if the preferences file does not exist or is invalid JSON.
    """
    if PREFS_FILE.is_file():
        try:
            return json.loads(PREFS_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_prefs(data: Dict[str, Any]) -> None:
    """Save user preferences to disk.

    Args:
        data: A dictionary of preference keys and values to persist.
              Silently ignores any I/O errors to avoid crashing the app.
    """
    try:
        PREFS_FILE.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
    except Exception:
        pass