"""Per-dataset reshapers -- each takes one game's final.json + returns a frame.

Every reshaper delegates the actual reshape to a ``sportsdataverse.wbb``
producer (shared with WNBA later); this module is just the registry +
per-game glue. Signature contract: ``(final, *, season, game_id) -> pl.DataFrame``.
"""

from __future__ import annotations

from pathlib import Path

import polars as pl
from sportsdataverse.wbb import (
    helper_wbb_play_by_play,
    helper_wbb_player_box,
    helper_wbb_schedule,
    helper_wbb_team_box,
)


def team_box_reshaper(final: dict, *, season: int, game_id: int) -> pl.DataFrame:
    return helper_wbb_team_box(final)


def pbp_reshaper(final: dict, *, season: int, game_id: int) -> pl.DataFrame:
    return helper_wbb_play_by_play(final)


def player_box_reshaper(final: dict, *, season: int, game_id: int) -> pl.DataFrame:
    return helper_wbb_player_box(final)


RESHAPERS: dict = {
    "team_box": team_box_reshaper,
    "pbp": pbp_reshaper,
    "player_box": player_box_reshaper,
}

# --- season-level builders (no per-game loop) --------------------------------
# Signature contract: (season, *, raw_root, base) -> pl.DataFrame. Each reads
# the raw season tree and/or the already-built parquets under ``base``.

_SHOTS_COLS = (
    "game_id",
    "season",
    "period_number",
    "clock_display_value",
    "team_id",
    "athlete_id_1",
    "athlete_id_2",
    "type_id",
    "type_text",
    "scoring_play",
    "score_value",
    "coordinate_x",
    "coordinate_y",
    "coordinate_x_raw",
    "coordinate_y_raw",
)


def shots_from_pbp(pbp: pl.DataFrame) -> pl.DataFrame:
    """R espn_wbb_01 shots block: filter shooting plays, project the shot cols."""
    if pbp.is_empty():
        return pl.DataFrame()
    out = pbp.filter(pl.col("shooting_play") == True)  # noqa: E712
    return out.select([c for c in _SHOTS_COLS if c in out.columns])


def _built_game_ids(base: Path, dataset: str, stem: str, season: int) -> list[int]:
    p = base / dataset / "parquet" / f"{stem}_{season}.parquet"
    if not p.exists():
        return []
    return (
        pl.read_parquet(p, columns=["game_id"])
        .get_column("game_id")
        .cast(pl.Int64)
        .unique()
        .to_list()
    )


def schedules_builder(season: int, *, raw_root: Path, base: Path) -> pl.DataFrame:
    """Released schedule = raw schedule + casts/dates + PBP/team_box/player_box flags."""
    raw = pl.read_parquet(
        raw_root / "wbb" / "schedules" / "parquet" / f"wbb_schedule_{season}.parquet"
    )
    return helper_wbb_schedule(
        raw,
        pbp_game_ids=_built_game_ids(base, "pbp", "play_by_play", season),
        team_box_game_ids=_built_game_ids(base, "team_box", "team_box", season),
        player_box_game_ids=_built_game_ids(base, "player_box", "player_box", season),
    )


def shots_builder(season: int, *, raw_root: Path, base: Path) -> pl.DataFrame:
    """Shots derive from the already-built play_by_play parquet (no extra I/O in R)."""
    p = base / "pbp" / "parquet" / f"play_by_play_{season}.parquet"
    if not p.exists():
        return pl.DataFrame()
    return shots_from_pbp(pl.read_parquet(p))


def _sidecar_builder(subdir: str, helper) -> object:
    """Per-game sidecar loop (R scripts 08/09): completed games, tryCatch skips."""

    def _build(season: int, *, raw_root: Path, base: Path) -> pl.DataFrame:
        from wbb_data_build import ingest

        frames: list[pl.DataFrame] = []
        for gid in ingest.season_completed_game_ids(season, raw_root=raw_root):
            payload = ingest.read_final(gid, raw_root=raw_root, subdir=subdir)
            if payload is None:
                continue
            try:
                frame = helper(payload, season=season, game_id=gid)
            except Exception as e:  # R tryCatch(...) -> NULL parity
                print(f"{subdir} parse failed for {gid}: {e}")
                continue
            if frame.height:
                frames.append(frame)
        if not frames:
            return pl.DataFrame()
        return pl.concat(frames, how="diagonal_relaxed")

    return _build


def _game_rosters_builder() -> object:
    from sportsdataverse.wbb import helper_wbb_game_rosters

    return _sidecar_builder("game_rosters/json", helper_wbb_game_rosters)


def _officials_builder() -> object:
    from sportsdataverse.wbb import helper_wbb_officials

    return _sidecar_builder("officials/json", helper_wbb_officials)


def _per_entity_frames(
    subdir: str, season: int, raw_root: Path, helper, id_kw: str
) -> list[pl.DataFrame]:
    """R scripts 04/05/06: loop the season's per-entity JSONs, tryCatch skips."""
    from wbb_data_build import ingest

    frames: list[pl.DataFrame] = []
    for eid in ingest.season_dir_ids(subdir, season, raw_root=raw_root):
        payload = ingest.read_final(eid, raw_root=raw_root, subdir=f"{subdir}/json/{season}")
        if payload is None:
            continue
        try:
            frame = helper(payload, **{"season": season, id_kw: eid})
        except Exception as e:  # R tryCatch(...) -> NULL parity
            print(f"{subdir} parse failed for {eid}: {e}")
            continue
        if frame.height:
            frames.append(frame)
    return frames


def _season_concat(frames: list[pl.DataFrame]) -> pl.DataFrame:
    if not frames:
        return pl.DataFrame()
    # R: season-level distinct().
    return pl.concat(frames, how="diagonal_relaxed").unique(maintain_order=True, keep="first")


def rosters_builder(season: int, *, raw_root: Path, base: Path) -> pl.DataFrame:
    from sportsdataverse.wbb import helper_wbb_rosters

    return _season_concat(
        _per_entity_frames("team_rosters", season, raw_root, helper_wbb_rosters, "team_id")
    )


def team_season_stats_builder(season: int, *, raw_root: Path, base: Path) -> pl.DataFrame:
    from sportsdataverse.wbb import helper_wbb_team_season_stats

    return _season_concat(
        _per_entity_frames("team_stats", season, raw_root, helper_wbb_team_season_stats, "team_id")
    )


def player_season_stats_builder(season: int, *, raw_root: Path, base: Path) -> pl.DataFrame:
    from sportsdataverse.wbb import build_athlete_identity_lookup, helper_wbb_player_season_stats

    from wbb_data_build import ingest

    rosters = {
        tid: ingest.read_final(tid, raw_root=raw_root, subdir=f"team_rosters/json/{season}")
        for tid in ingest.season_dir_ids("team_rosters", season, raw_root=raw_root)
    }
    lookup = build_athlete_identity_lookup({t: r for t, r in rosters.items() if r})

    def _helper(payload: dict, *, season: int, athlete_id: int) -> pl.DataFrame:
        return helper_wbb_player_season_stats(
            payload, season=season, athlete_id=athlete_id, identity_lookup=lookup
        )

    return _season_concat(
        _per_entity_frames("player_season_stats", season, raw_root, _helper, "athlete_id")
    )


def standings_builder(season: int, *, raw_root: Path, base: Path) -> pl.DataFrame:
    from sportsdataverse.wbb import helper_wbb_standings

    from wbb_data_build import ingest

    payload = ingest.read_final(season, raw_root=raw_root, subdir="standings/json")
    if payload is None:
        return pl.DataFrame()
    return helper_wbb_standings(payload, season=season)


SEASON_BUILDERS: dict = {
    "schedules": schedules_builder,
    "shots": shots_builder,
    "game_rosters": _game_rosters_builder(),
    "officials": _officials_builder(),
    "rosters": rosters_builder,
    "team_season_stats": team_season_stats_builder,
    "player_season_stats": player_season_stats_builder,
    "standings": standings_builder,
}
