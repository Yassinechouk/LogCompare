# -*- coding: utf-8 -*-

from dataclasses import dataclass
from typing import Optional

@dataclass
class Etape:
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