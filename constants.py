# -*- coding: utf-8 -*-
"""
constants.py – Application-wide Constants & Configuration
===========================================================

Centralises all tuneable parameters, colour codes, regex patterns,
and default threshold values used throughout the LOGCOMPARE tool.
"""

from pathlib import Path
import re

# ─────────────────────────────────────────────
#  OPTIONAL SIGNATURE / BRANDING
# ─────────────────────────────────────────────
SIGNATURE_ENABLED = False
SIGNATURE_TEXT = ""

# ─────────────────────────────────────────────
#  APPLICATION METADATA
# ─────────────────────────────────────────────
APP_TITLE = "Traiter Log - Tableau Comparatif"

# ─────────────────────────────────────────────
#  PATHS
# ─────────────────────────────────────────────
PREFS_FILE = Path.home() / ".log_compare_prefs.json"

# ─────────────────────────────────────────────
#  LOG PARSING – REGEX PATTERNS
# ─────────────────────────────────────────────
# Matches a timestamped step line, e.g.:
#   [12:34:56:789] ==> STEP NAME <
REGEX_ETAPE = re.compile(r'^\[(\d{2}):(\d{2}):(\d{2}):(\d{3})]\s*=+>\s*(.*?)\s*<')

# Matches the total test duration at the end of a log file, e.g.:
#   DUREE DU TEST : 42 secondes
REGEX_DUREE_TEST = re.compile(r'\bDUREE\s*DU\s*TEST\s*:\s*(\d+)\s*secondes\b', re.IGNORECASE)

# ─────────────────────────────────────────────
#  BLOCK BOUNDARY STEP NAMES (normalised / uppercased)
# ─────────────────────────────────────────────
NOM_DEBUT = "DEBUT DE TEST"
NOM_FIN = "FIN DE TEST"

# ─────────────────────────────────────────────
#  DEFAULT BEHAVIOUR FLAGS
# ─────────────────────────────────────────────
# When True, only the first test block is used for comparison
LIMITER_PREMIER_BLOC = True
# Whether the sequential index column is shown by default
INCLURE_INDEX_DEFAULT = True
# Whether delta (Δ) columns are shown by default
AFFICHER_DELTAS_DEFAULT = False

# ─────────────────────────────────────────────
#  COMPARISON THRESHOLDS  (percentage)
# ─────────────────────────────────────────────
DEFAULT_THRESH_NEAR = 5.0    # ≤ this %  → "close" colour
DEFAULT_THRESH_YELLOW = 20.0 # ≤ this %  → "warning" colour; > this → "bad"

# ─────────────────────────────────────────────
#  COLOUR PALETTE  (hex, used in GUI and Excel export)
# ─────────────────────────────────────────────
COLOR_EQUAL_DARK = "#1f8e2d"      # exact match (dark green)
COLOR_NEAR_LIGHT = "#bdf8a2"      # within THRESH_NEAR (light green)
COLOR_WARN = "#fff89a"            # within THRESH_YELLOW (yellow)
COLOR_BAD = "#ff8d8d"            # exceeds THRESH_YELLOW (red)
COLOR_EMPTY = "#d9d9d9"           # missing value (grey)
COLOR_REF_BG = "#e6ffe6"          # reference column background
COLOR_TOTAL_BG = "#b7d4ff"        # TOTAL row background (blue)
COLOR_STEP_COLUMN_BG = "#f5f5f5"  # step-name column background
COLOR_DELTA_BG_DEFAULT = "#ffffff" # delta column default background

# ─────────────────────────────────────────────
#  COLUMN MANAGEMENT
# ─────────────────────────────────────────────
# Columns that cannot be hidden by the user
MANDATORY_COLUMNS = {"Étape", "Reference", "Index"}