# -*- coding: utf-8 -*-

from pathlib import Path
import re

# =================== CONFIGURABLE SIGNATURE ===================
SIGNATURE_ENABLED = False
SIGNATURE_TEXT = ""

# =================== CONSTANTS & CONFIG ===================
APP_TITLE = "Traiter Log - Tableau Comparatif"
PREFS_FILE = Path.home() / ".log_compare_prefs.json"

REGEX_ETAPE = re.compile(r'^\[(\d{2}):(\d{2}):(\d{2}):(\d{3})]\s*=+>\s*(.*?)\s*<')
REGEX_DUREE_TEST = re.compile(r'\bDUREE\s*DU\s*TEST\s*:\s*(\d+)\s*secondes\b', re.IGNORECASE)

NOM_DEBUT = "DEBUT DE TEST"
NOM_FIN = "FIN DE TEST"

LIMITER_PREMIER_BLOC = True
INCLURE_INDEX_DEFAULT = True
AFFICHER_DELTAS_DEFAULT = False

DEFAULT_THRESH_NEAR = 5.0
DEFAULT_THRESH_YELLOW = 20.0

COLOR_EQUAL_DARK = "#1f8e2d"
COLOR_NEAR_LIGHT = "#bdf8a2"
COLOR_WARN = "#fff89a"
COLOR_BAD = "#ff8d8d"
COLOR_EMPTY = "#d9d9d9"
COLOR_REF_BG = "#e6ffe6"
COLOR_TOTAL_BG = "#b7d4ff"
COLOR_STEP_COLUMN_BG = "#f5f5f5"
COLOR_DELTA_BG_DEFAULT = "#ffffff"

MANDATORY_COLUMNS = {"Étape", "Reference", "Index"}