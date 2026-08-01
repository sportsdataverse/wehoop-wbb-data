"""Schedule master and the single ``games_in_data_repo`` manifest.

Two artifacts, one pass, derived from the same in-memory frame so they cannot
drift:

``wbb_schedule_master.parquet``
    Every game the schedule knows about -- the denominator, including games
    with nothing built.

``wbb_games_in_data_repo.parquet``
    Only games present in at least one compilation -- the numerator, and what
    consumers join against. It replaces the per-dataset
    ``wbb/<ds>/wbb_<ds>_in_data_repo.csv`` files (seven of them).

The season files are the ORIGIN of every flag; this module computes none of
them, it unions and normalizes. ``helper_wbb_schedule`` stamps wehoop's
published ``PBP`` / ``team_box`` / ``player_box`` names, which
``load_wbb_schedule()`` consumers read and which therefore cannot be renamed in
the season files. Here they are normalized to ``in_*`` alongside the rest, so
anything reading the master sees one convention.
"""

from __future__ import annotations

import polars as pl

from wbb_data_build.ids import canonicalize_ids

#: wehoop's published flag name -> the normalized one used in the master.
LEGACY_FLAGS = {"PBP": "in_pbp", "team_box": "in_team_box", "player_box": "in_player_box"}

#: Game-level datasets that roll up into a season release and so get a flag.
GAME_LEVEL = ("pbp", "team_box", "player_box", "shots", "game_rosters", "officials")


def normalize_flags(schedule: pl.DataFrame) -> pl.DataFrame:
    """Add an ``in_<dataset>`` column for each of :data:`GAME_LEVEL`.

    Legacy published names are mapped, not renamed: the source column stays so
    the season file's contract is untouched.
    """
    out = schedule
    for legacy, normalized in LEGACY_FLAGS.items():
        if legacy in out.columns and normalized not in out.columns:
            out = out.with_columns(pl.col(legacy).cast(pl.Boolean).alias(normalized))
    # A dataset absent from this season still gets a column: absence must be
    # representable, not missing.
    missing = [pl.lit(False).alias(f"in_{d}") for d in GAME_LEVEL if f"in_{d}" not in out.columns]
    return out.with_columns(missing) if missing else out


def build_master(season_frames: list[pl.DataFrame]) -> pl.DataFrame:
    """Union season schedules into one frame with a pinned column order.

    Ragged seasons reconcile via ``diagonal_relaxed``, so a column present in
    one season is null-filled in the others -- which is what fixes the drift
    where the master carried columns the yearly files did not.

    Raises:
        ValueError: If no frames are given.
    """
    if not season_frames:
        raise ValueError("build_master() requires at least one season frame")
    frames = [normalize_flags(canonicalize_ids(df)) for df in season_frames]
    master = pl.concat(frames, how="diagonal_relaxed")
    master = master.select(sorted(master.columns))
    keys = [k for k in ("season", "game_id") if k in master.columns]
    return master.sort(keys) if keys else master


def games_in_data_repo(master: pl.DataFrame) -> pl.DataFrame:
    """Only games present in at least one compilation."""
    flags = [c for c in master.columns if c.startswith("in_")]
    if not flags:
        return master.head(0)
    return master.filter(pl.any_horizontal([pl.col(c) == True for c in flags]))


def build_coverage(master: pl.DataFrame) -> pl.DataFrame:
    """One row per ``(season, season_type)`` with per-dataset coverage."""
    flags = [c for c in master.columns if c.startswith("in_")]
    keys = [k for k in ("season", "season_type") if k in master.columns]
    if not keys:
        raise ValueError("master frame has neither season nor season_type")
    aggs: list[pl.Expr] = [pl.len().alias("n_games")]
    if "date" in master.columns:
        aggs += [
            pl.col("date").min().alias("first_date"),
            pl.col("date").max().alias("last_date"),
        ]
    aggs += [pl.col(f).mean().alias(f"pct_{f}") for f in flags]
    # maintain_order keeps grouping deterministic; the sort then pins it.
    return master.group_by(keys, maintain_order=True).agg(aggs).sort(keys)
