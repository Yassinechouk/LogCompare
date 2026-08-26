# -*- coding: utf-8 -*-
"""
models.py – Data models for LOGCOMPARE.

Defines the core dataclass used to represent a single timestamped
step extracted from a structured log file.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Etape:
    """A single timestamped step extracted from a log file.

    Attributes:
        ligne:                      Line number in the source file.
        heure:                      Hour component of the timestamp (HH).
        minute:                     Minute component of the timestamp (MM).
        seconde:                    Second component of the timestamp (SS).
        millis:                     Millisecond component of the timestamp (mmm).
        total_ms:                   Absolute timestamp in milliseconds from midnight
                                    (with day-rollover correction applied).
        nom_etape:                  Normalised step name extracted from the log line.
        texte:                      Full raw log line (without trailing newline).
        duree_ms_depuis_precedente: Duration since the previous step in milliseconds.
                                    Zero for the first step in the sequence.
        id_bloc:                    Identifier of the test-block this step belongs to
                                    (None if not assigned to any block).
        delta_depuis_debut_bloc_ms: Elapsed time since the start of the current block
                                    in milliseconds (None if not in a block).
    """

    ligne: int
    heure: str
    minute: str
    seconde: str
    millis: str
    total_ms: int
    nom_etape: str
    texte: str
    duree_ms_depuis_precedente: int = 0
    id_bloc: Optional[int] = None
    delta_depuis_debut_bloc_ms: Optional[int] = None