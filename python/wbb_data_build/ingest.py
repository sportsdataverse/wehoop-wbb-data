"""Read the sibling wehoop-wbb-raw tree from disk.

R reads game JSON over HTTP from raw.githubusercontent; the Python producer reads
the sibling checkout directly (sdv-build-data convention). Game payloads live at
``{raw_root}/wbb/json/final/{game_id}.json``; the per-season schedule the R
scripts consult lives at ``{raw_root}/wbb/schedules/parquet/wbb_schedule_{season}.parquet``.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import polars as pl

from wbb_data_build.config import RAW_ROOT_ENV


def _resolve_root(explicit: str | Path | None) -> Path:
    """Resolve the wehoop-wbb-raw checkout root (arg > env)."""
    val = explicit or os.environ.get(RAW_ROOT_ENV)
    if not val:
        raise RuntimeError(
            f"set {RAW_ROOT_ENV} to the wehoop-wbb-raw checkout root, or pass raw_root="
        )
    return Path(val)


def raw_root(explicit: str | Path | None = None) -> Path:
    """Resolve the wehoop-wbb-raw checkout root (arg > env)."""
    return _resolve_root(explicit)


def season_game_ids(season: int, *, raw_root: str | Path | None = None) -> list[int]:
    """Game ids for ``season`` that have a final.json (R: ``game_json == TRUE``)."""
    root = _resolve_root(raw_root)
    sched = root / "wbb" / "schedules" / "parquet" / f"wbb_schedule_{season}.parquet"
    df = pl.read_parquet(sched)
    df = df.filter(pl.col("game_json") == True)  # noqa: E712
    return df.get_column("game_id").cast(pl.Int64).to_list()


def season_completed_game_ids(season: int, *, raw_root: str | Path | None = None) -> list[str]:
    """Completed-game ids for ``season`` (R ``list_game_ids`` in scripts 08/09).

    Unlike :func:`season_game_ids` this does NOT require ``game_json`` -- it
    filters to completed games (``status_type_completed`` truthy, with the
    ``status_type_name`` regex fallback) and returns ids as strings, matching
    the R producer's ``as.character(unique(game_id))``.
    """
    root = _resolve_root(raw_root)
    sched = root / "wbb" / "schedules" / "parquet" / f"wbb_schedule_{season}.parquet"
    df = pl.read_parquet(sched)
    if "game_id" not in df.columns:
        return []
    if "status_type_completed" in df.columns:
        df = df.filter(pl.col("status_type_completed") == True)  # noqa: E712
    elif "status_type_name" in df.columns:
        df = df.filter(
            pl.col("status_type_name")
            .str.to_uppercase()
            .str.contains("POSTPONED|CANCEL|SUSPENDED|FORFEIT")
            .fill_null(False)
            == False  # noqa: E712
        )
    ids = df.get_column("game_id").cast(pl.Int64).cast(pl.Utf8).unique(maintain_order=True)
    return [i for i in ids.to_list() if i]


def season_dir_ids(subdir: str, season: int, *, raw_root: str | Path | None = None) -> list[int]:
    """Numeric ids of the per-entity JSONs under ``wbb/{subdir}/json/{season}``.

    Mirrors the R scripts' GitHub-contents listing (alphabetical by file NAME,
    numeric names only) used by the rosters/season-stats creation scripts.
    """
    root = _resolve_root(raw_root)
    d = root / "wbb" / subdir / "json" / str(season)
    if not d.is_dir():
        return []
    names = sorted(f.stem for f in d.glob("*.json"))
    return [int(n) for n in names if n.isdigit()]


def read_final(
    game_id: int | str,
    *,
    raw_root: str | Path | None = None,
    subdir: str = "json/final",
) -> dict | None:
    """Read one game's raw JSON; ``None`` if absent/malformed (R tryCatch parity).

    ``subdir`` selects the raw subtree under ``wbb/`` -- ``"json/final"``
    (default), ``"game_rosters/json"``, or ``"officials/json"``.
    """
    root = _resolve_root(raw_root)
    f = root / "wbb" / subdir / f"{game_id}.json"
    if not f.exists():
        return None
    try:
        return json.loads(f.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
