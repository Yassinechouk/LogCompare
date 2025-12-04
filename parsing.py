

from pathlib import Path
from typing import Optional, List, Dict, Tuple, Any
import re

from models import Etape
from constants import REGEX_ETAPE, NOM_DEBUT, NOM_FIN, REGEX_DUREE_TEST

def normalize_nom(n: str) -> str:
    return " ".join(n.strip().upper().split())

def hmsm_to_total_ms(hh: str, mm: str, ss: str, ms: str) -> int:
    return (int(hh)*3600 + int(mm)*60 + int(ss))*1000 + int(ms)

def detect_rollover(prev_total_ms: int, current_total_ms: int) -> bool:
    return current_total_ms < prev_total_ms

def parse_etapes(log_path: Path, manage_rollover: bool = True) -> List[Etape]:
    etapes: List[Etape] = []
    offset_jour = 0
    prev_total_raw: Optional[int] = None
    with log_path.open("r", encoding="utf-8", errors="replace") as f:
        for num_ligne, ligne in enumerate(f, start=1):
            m = REGEX_ETAPE.match(ligne.rstrip("\n"))
            if not m:
                continue
            hh, mm, ss, ms, nom_brut = m.groups()
            nom = " ".join(nom_brut.split())
            raw = hmsm_to_total_ms(hh, mm, ss, ms)
            if manage_rollover and prev_total_raw is not None and detect_rollover(prev_total_raw, raw):
                offset_jour += 24*3600*1000
            prev_total_raw = raw
            total_ms = raw + offset_jour
            etapes.append(Etape(
                ligne=num_ligne, heure=hh, minute=mm, seconde=ss, millis=ms,
                total_ms=total_ms, nom_etape=nom, texte=ligne.rstrip("\n")
            ))
    for i, e in enumerate(etapes):
        e.duree_ms_depuis_precedente = 0 if i == 0 else e.total_ms - etapes[i-1].total_ms
    return etapes

def affecter_blocs(etapes: List[Etape]) -> None:
    debut_indices = [i for i, e in enumerate(etapes) if normalize_nom(e.nom_etape) == NOM_DEBUT]
    fin_indices = [i for i, e in enumerate(etapes) if normalize_nom(e.nom_etape) == NOM_FIN]
    fin_iter = iter(fin_indices)
    current_fin = next(fin_iter, None)
    bloc_id = 0
    for idx_deb in debut_indices:
        while current_fin is not None and current_fin < idx_deb:
            current_fin = next(fin_iter, None)
        if current_fin is None:
            break
        e_deb = etapes[idx_deb]
        for e in etapes[idx_deb: current_fin + 1]:
            e.id_bloc = bloc_id
            e.delta_depuis_debut_bloc_ms = e.total_ms - e_deb.total_ms
        bloc_id += 1
        current_fin = next(fin_iter, None)

def filtrer_premier_bloc(etapes: List[Etape]) -> List[Etape]:
    blocs = sorted({e.id_bloc for e in etapes if e.id_bloc is not None})
    if not blocs:
        return etapes
    return [e for e in etapes if e.id_bloc == blocs[0]]

def construire_index_occurrences(etapes: List[Etape]) -> List[Tuple[int, str, int, Etape]]:
    compte: Dict[str, int] = {}
    res = []
    for idx, e in enumerate(etapes):
        compte[e.nom_etape] = compte.get(e.nom_etape, 0) + 1
        res.append((idx, e.nom_etape, compte[e.nom_etape], e))
    return res

def extract_duree_test_seconds(log_path: Path) -> Optional[int]:
    try:
        with log_path.open("r", encoding="utf-8", errors="replace") as f:
            for line in f:
                m = REGEX_DUREE_TEST.search(line)
                if m:
                    return int(m.group(1))
    except Exception:
        return None
    return None