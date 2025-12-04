# -*- coding: utf-8 -*-

import json
from typing import Dict, Any
from constants import PREFS_FILE

def load_prefs() -> Dict[str, Any]:
    if PREFS_FILE.is_file():
        try:
            return json.loads(PREFS_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}

def save_prefs(data: Dict[str, Any]):
    try:
        PREFS_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass