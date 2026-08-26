# -*- coding: utf-8 -*-
"""
parsing.py – Log File Parsing for LOGCOMPARE
=============================================

Provides functions to:
  - Parse structured timestamped log files into :class:`~models.Etape` objects.
  - Detect and correct midnight rollovers in timestamps.
  - Assign test-block identifiers to parsed steps.
  - Build occurrence-indexed step sequences for pivot comparison.
  - Extract the total test duration (in seconds) from log footers.

Expected log-line format::

    [HH:MM:SS:mmm] ==> STEP NAME <...rest of line...
"""

from pathlib import Path
from typing import Optional, List, Dict, Tuple

from models import Etape
from constants import REGEX_ETAPE, NOM_DEBUT, NOM_FIN, REGEX_DUREE_TEST


def normalize_nom(n: str) -> str:
    """Normalise a step name for comparison.

    Strips surrounding whitespace, collapses internal whitespace,
    and converts to upper-case so that names match reliably.

    Args:
        n: Raw step name string.

    Returns:
        Normalised step name (upper-case, single-spaced).
    """
    return " ".join(n.strip().upper().split())


def hmsm_to_total_ms(hh: str, mm: str, ss: str, ms: str) -> int:
    """Convert a HH:MM:SS:mmm timestamp to a total millisecond value.

    Args:
        hh: Hours string (e.g. "12").
        mm: Minutes string (e.g. "34").
        ss: Seconds string (e.g. "56").
        ms: Milliseconds string (e.g. "789").

    Returns:
        Total number of milliseconds since midnight.
    """
    return (int(hh) * 3600 + int(mm) * 60 + int(ss)) * 1000 + int(ms)


def detect_rollover(prev_total_ms: int, current_total_ms: int) -> bool:
    """Detect a midnight timestamp rollover between two consecutive steps.

    Args:
        prev_total_ms:    Millisecond timestamp of the previous step.
        current_total_ms: Millisecond timestamp of the current step.

    Returns:
        True if the current timestamp is strictly less than the previous
        one, indicating that midnight was crossed.
    """
    return current_total_ms < prev_total_ms


def parse_etapes(log_path: Path, manage_rollover: bool = True) -> List[Etape]:
    """Parse all timestamped steps from a log file.

    Reads the file line-by-line, matches lines against :data:`~constants.REGEX_ETAPE`,
    and builds a list of :class:`~models.Etape` objects with cumulative millisecond
    timestamps and inter-step durations.

    Args:
        log_path:        Path to the ``.log`` file to parse.
        manage_rollover: When True, adds 24 h worth of milliseconds to every
                         timestamp after a detected midnight rollover so that
                         comparisons across midnight remain monotonic.

    Returns:
        Ordered list of :class:`~models.Etape` objects. The first step always
        has ``duree_ms_depuis_precedente == 0``.
    """
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
                offset_jour += 24 * 3600 * 1000
            prev_total_raw = raw
            total_ms = raw + offset_jour
            etapes.append(Etape(
                ligne=num_ligne, heure=hh, minute=mm, seconde=ss, millis=ms,
                total_ms=total_ms, nom_etape=nom, texte=ligne.rstrip("\n")
            ))

    # Compute inter-step durations
    for i, e in enumerate(etapes):
        e.duree_ms_depuis_precedente = 0 if i == 0 else e.total_ms - etapes[i - 1].total_ms

    return etapes


def affecter_blocs(etapes: List[Etape]) -> None:
    """Assign test-block identifiers and block-relative deltas to each step.

    A *block* is the sequence of steps between a ``DEBUT DE TEST`` and the
    next ``FIN DE TEST`` step (inclusive).  Each block receives a monotonically
    increasing integer ``id_bloc`` starting at 0, and each step within the
    block receives a ``delta_depuis_debut_bloc_ms`` relative to the block's
    opening step.

    Modifies ``etapes`` in-place.

    Args:
        etapes: List of :class:`~models.Etape` objects (as returned by
                :func:`parse_etapes`).
    """
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
    """Return only the steps belonging to the first test block.

    If no block has been assigned (i.e. no ``DEBUT DE TEST`` / ``FIN DE TEST``
    boundaries were found), the full list is returned unchanged.

    Args:
        etapes: List of :class:`~models.Etape` objects with block IDs assigned.

    Returns:
        Filtered list containing only steps where ``id_bloc == 0``, or the
        original list if no blocks exist.
    """
    blocs = sorted({e.id_bloc for e in etapes if e.id_bloc is not None})
    if not blocs:
        return etapes
    return [e for e in etapes if e.id_bloc == blocs[0]]


def construire_index_occurrences(etapes: List[Etape]) -> List[Tuple[int, str, int, Etape]]:
    """Build an occurrence-indexed sequence of steps.

    When the same step name appears multiple times, each occurrence gets a
    separate index counter so that repeated steps can be matched positionally
    across different log files.

    Args:
        etapes: Ordered list of :class:`~models.Etape` objects.

    Returns:
        A list of ``(sequence_index, step_name, occurrence_count, etape)``
        tuples, one per step.
    """
    compte: Dict[str, int] = {}
    res = []
    for idx, e in enumerate(etapes):
        compte[e.nom_etape] = compte.get(e.nom_etape, 0) + 1
        res.append((idx, e.nom_etape, compte[e.nom_etape], e))
    return res


def extract_duree_test_seconds(log_path: Path) -> Optional[int]:
    """Scan a log file for the total test duration line.

    Searches for a line matching::

        DUREE DU TEST : <N> secondes

    Args:
        log_path: Path to the ``.log`` file to scan.

    Returns:
        The total test duration in **seconds** as an integer, or ``None`` if
        the pattern is not found or an I/O error occurs.
    """
    try:
        with log_path.open("r", encoding="utf-8", errors="replace") as f:
            for line in f:
                m = REGEX_DUREE_TEST.search(line)
                if m:
                    return int(m.group(1))
    except Exception:
        return None
    return None