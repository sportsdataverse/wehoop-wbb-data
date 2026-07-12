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


def read_final(game_id: int, *, raw_root: str | Path | None = None) -> dict | None:
    """Read one game's ``final.json``; ``None`` if absent/malformed (R tryCatch parity)."""
    root = _resolve_root(raw_root)
    f = root / "wbb" / "json" / "final" / f"{game_id}.json"
    if not f.exists():
        return None
    try:
        return json.loads(f.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
