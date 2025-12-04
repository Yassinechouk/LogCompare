# -*- coding: utf-8 -*-

from pathlib import Path
from typing import Optional, List, Dict, Tuple, Any
import csv
import time

from models import Etape
from parsing import (
    parse_etapes,
    affecter_blocs,
    filtrer_premier_bloc,
    construire_index_occurrences,
    extract_duree_test_seconds,
    normalize_nom,
)
from constants import NOM_DEBUT

def safe_write_csv(headers: List[str], rows: List[List[Any]], target_path: Path) -> Path:
    target_dir = target_path.parent
    target_dir.mkdir(parents=True, exist_ok=True)
    tmp_path = target_path.with_suffix(target_path.suffix + ".tmp")
    def _write(p: Path):
        with p.open("w", newline="", encoding="utf-8") as fcsv:
            w = csv.writer(fcsv)
            w.writerow(headers)
            w.writerows(rows)
    try:
        _write(tmp_path)
        if target_path.exists():
            try:
                target_path.unlink()
            except PermissionError:
                alt = target_path.parent / (target_path.stem + f"_old_{int(time.time())}.csv")
                try:
                    target_path.rename(alt)
                except Exception:
                    pass
        tmp_path.rename(target_path)
    except PermissionError:
        home_dir = Path.home() / "logs_export"
        home_dir.mkdir(parents=True, exist_ok=True)
        fallback = home_dir / target_path.name
        tmp_fb = fallback.with_suffix(fallback.suffix + ".tmp")
        _write(tmp_fb)
        if fallback.exists():
            try:
                fallback.unlink()
            except Exception:
                pass
        tmp_fb.rename(fallback)
        return fallback
    return target_path

def _build_index_and_duration_map(etapes_block: List[Etape]) -> Tuple[List[Tuple[int, str, int, Etape]], Dict[Tuple[str, int], int]]:
    idx = construire_index_occurrences(etapes_block)
    dur_map: Dict[Tuple[str, int], int] = {}
    for i, (seq, nom, occ, _et) in enumerate(idx):
        if i < len(etapes_block) - 1:
            dur = etapes_block[i + 1].total_ms - etapes_block[i].total_ms
        else:
            dur = 0
        dur_map[(nom, occ)] = dur
    return idx, dur_map

def construire_pivot(reference_path: Path,
                     reference_etapes: List[Etape],
                     dossier_logs: Path,
                     include_index: bool,
                     include_deltas: bool,
                     output_dir: Optional[Path] = None) -> Tuple[List[str], List[List[Any]], Path]:
    subset = filtrer_premier_bloc(reference_etapes)
    if not subset:
        raise ValueError("Référence vide (premier bloc).")

    ref_index, ref_map = _build_index_and_duration_map(subset)

    if not dossier_logs.is_dir():
        raise ValueError(f"Dossier logs invalide : {dossier_logs}")

    autres = sorted([p for p in dossier_logs.glob("*.log") if p.resolve() != reference_path.resolve()])

    label_map = {p: f"Fichier_{i+1}" for i, p in enumerate(autres)}

    pivot: Dict[Tuple[str, int], Dict[str, Optional[int]]] = {
        (nom, occ): {"Reference": ref_map[(nom, occ)]} for _, nom, occ, _ in ref_index
    }

    for f in autres:
        lbl = label_map[f]
        try:
            efs = parse_etapes(f, manage_rollover=True)
            affecter_blocs(efs)
            efs = filtrer_premier_bloc(efs)
            idx_f, fmap = _build_index_and_duration_map(efs)
        except Exception:
            fmap = {}
        for key in pivot:
            pivot[key][lbl] = fmap.get(key)

    ordered_files = [label_map[p] for p in autres]

    headers: List[str] = []
    if include_index:
        headers.append("Index")
    headers.append("Étape")
    headers.append("Reference")
    for lbl in ordered_files:
        headers.append(lbl)
        if include_deltas:
            headers.append(f"Δ_{lbl}")

    seq_map = {(nom, occ): seq for seq, nom, occ, _ in ref_index}
    rows: List[List[Any]] = []
    for (nom, occ), data in pivot.items():
        ref_val = data.get("Reference")
        row: List[Any] = []
        if include_index:
            row.append(seq_map[(nom, occ)])
        row.append(nom)
        row.append(ref_val if ref_val is not None else "")
        for lbl in ordered_files:
            v = data.get(lbl)
            row.append(v if v is not None else "")
            if include_deltas:
                if isinstance(ref_val, int) and isinstance(v, int):
                    row.append(v - ref_val)
                else:
                    row.append("")
        rows.append(row)

    # TOTAL row
    total_row: List[Any] = []
    if include_index:
        total_row.append("")
    total_row.append("TOTAL")
    col_offset = 1 + (1 if include_index else 0)
    total_ref_ms = sum(r[col_offset] for r in rows if isinstance(r[col_offset], int))
    total_row.append(total_ref_ms)
    for i, _lbl in enumerate(ordered_files):
        idx_duration = col_offset + 1 + i * (2 if include_deltas else 1)
        total_file_ms = sum(r[idx_duration] for r in rows if isinstance(r[idx_duration], int))
        total_row.append(total_file_ms)
        if include_deltas:
            total_row.append("")
    rows.append(total_row)

    # Format TOTAL ms + s
    last = rows[-1]
    for i in range(col_offset, len(last)):
        v = last[i]
        if isinstance(v, int):
            last[i] = f"{v} ({v/1000:.3f} s)"

    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)
        path_out = output_dir / (reference_path.stem + ".comparaison_pivot_unique.csv")
    else:
        path_out = reference_path.parent / (reference_path.stem + ".comparaison_pivot_unique.csv")
    final_path = safe_write_csv(headers, rows, path_out)
    return headers, rows, final_path