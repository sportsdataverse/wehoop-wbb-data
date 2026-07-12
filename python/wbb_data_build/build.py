"""Per-season build driver -- polars port of the R ``wbb_<dataset>_games(y)`` loop.

Enumerate season game-ids -> read each final.json -> reshape (delegating to
the sdv-py producer) -> drift-safe union -> write -> (opt) publish. Per-game
failures are swallowed (R tryCatch parity) so one bad payload can't sink the
season.
"""

from __future__ import annotations

from pathlib import Path

import polars as pl
from tqdm import tqdm

from wbb_data_build import ingest, io, publish, reshapers
from wbb_data_build.config import REGISTRY


def build_season(
    dataset: str,
    season: int,
    *,
    base: str | Path = "wbb",
    raw_root: str | Path | None = None,
    publish_release: bool = False,
    dry_run: bool = False,
) -> pl.DataFrame:
    """Build one dataset/season from the raw checkout: reshape, union, write, (opt) publish.

    Args:
        dataset: Key into ``config.REGISTRY`` (e.g. ``"team_box"``).
        season: Season year to build.
        base: Output root directory for ``io.write_dataset``.
        raw_root: Sibling ``wehoop-wbb-raw`` checkout root (arg > ``WEHOOP_WBB_RAW_ROOT`` env).
        publish_release: If True, upload the written files via ``publish.publish_dataset``.
        dry_run: If True, run the publish step in dry-run mode (no ``gh`` calls).

    Returns:
        pl.DataFrame: The built season frame, or an empty frame if no games qualified.

    Example:
        Quick start::

            from wbb_data_build.build import build_season
            df = build_season("team_box", 2025)
            print(df.shape)
    """
    spec = REGISTRY[dataset]
    if dataset not in reshapers.SEASON_BUILDERS and spec.reshaper not in reshapers.RESHAPERS:
        # The three crosswalks build from LIVE ESPN+Torvik+Fox inputs (not the
        # raw repo) via wehoop::wbb_*_crosswalk; they stay on the R scripts
        # (wbb_1{1,2,3}_*_creation.R) until the Torvik/Fox source surfaces are
        # ported to sportsdataverse.
        raise NotImplementedError(f"{dataset}: crosswalks still build via the R creation scripts")
    root = ingest.raw_root(raw_root)
    if dataset in reshapers.SEASON_BUILDERS:
        # Season-level datasets (schedules/shots/...) build from the raw season
        # tree and/or already-built parquets -- no per-game loop.
        out = reshapers.SEASON_BUILDERS[dataset](season, raw_root=root, base=Path(base))
        if out.height == 0:
            return out
        io.write_dataset(out, spec, season, base=base)
        if publish_release or dry_run:
            publish.publish_dataset(spec, season, base=base, dry_run=dry_run)
        return out
    game_ids = ingest.season_game_ids(season, raw_root=root)
    if not game_ids:
        return pl.DataFrame()
    reshape = reshapers.RESHAPERS[spec.reshaper]
    frames: list[pl.DataFrame] = []
    for gid in tqdm(game_ids, desc=f"{dataset} {season}"):
        final = ingest.read_final(gid, raw_root=root)
        if final is None:
            continue
        try:
            frame = reshape(final, season=season, game_id=gid)
        except Exception as e:  # R tryCatch(...) -> NULL parity
            print(f"{dataset} reshape failed for {gid}: {e}")
            continue
        if frame is not None and frame.height:
            frames.append(frame)
    if not frames:
        return pl.DataFrame()
    out = pl.concat(frames, how="diagonal_relaxed")
    # R: every per-game season compile is arrange(desc(game_date)) before
    # write/publish (stable, NA last).
    if "game_date" in out.columns:
        out = out.sort("game_date", descending=True, nulls_last=True, maintain_order=True)
    io.write_dataset(out, spec, season, base=base)
    if publish_release or dry_run:
        publish.publish_dataset(spec, season, base=base, dry_run=dry_run)
    return out
