"""Fox / Yahoo legs of the committed WBB schedule + player crosswalks, from wehoop-wbb-alt-data.

The live build (``daily_wbb.yml``) can only see today's Fox / Yahoo rosters and scoreboards,
so ``yahoo_player_id`` and past game ids stay null. This droplet step reads the committed
season crosswalk, the season's ESPN schedule + game rosters (this tree, else the release
asset), and the parsed alt-data season, fills only null provider ids
(``sportsdataverse._crosswalk_alt.with_alt_game_legs`` / ``with_alt_player_legs``), refuses
any change that loses a non-null value or a row / column, and writes (+ publishes) only when
an id changed. :func:`carry_forward` keeps those ids through the next live rebuild.

    uv run python -m wbb_data_build.alt_fill -s 2026 --base ../wbb [--out DIR] [--publish]
"""

from __future__ import annotations

import argparse
import os
from io import BytesIO
from pathlib import Path

import polars as pl

from wbb_data_build import ingest, io, publish
from wbb_data_build._logging import get_logger
from wbb_data_build.config import REGISTRY

log = get_logger()

RELEASE = f"https://github.com/{publish.DEFAULT_REPO}/releases/download"

LEAGUE = "wbb"
ALT_ENV = "WEHOOP_WBB_ALT_DATA_ROOT"
ALT_SIBLING = "wehoop-wbb-alt-data"
#: dataset -> stable row keys
KEYS = {
    "schedule_crosswalk": ["espn_game_id"],
    "player_crosswalk": ["espn_team_id", "espn_athlete_id"],
}


def _legs(dataset: str) -> dict[str, list[str]]:
    """Provider -> its crosswalk columns (id first), from sdv-py's basketball leg tables."""
    from sportsdataverse._crosswalk_alt import BASKETBALL_GAME_LEGS, BASKETBALL_PLAYER_LEGS

    legs = BASKETBALL_PLAYER_LEGS if dataset == "player_crosswalk" else BASKETBALL_GAME_LEGS
    return {p: [c for c in cols if c] for p, cols in legs.items()}


def alt_root(season: int) -> Path | None:
    """``$WEHOOP_WBB_ALT_DATA_ROOT`` or the sibling checkout, when it holds a parsed ``season``."""
    env = os.environ.get(ALT_ENV)
    root = Path(env) if env else Path(__file__).resolve().parents[3] / ALT_SIBLING
    parsed = (
        root / p / "game_rosters" / "parquet" / f"{LEAGUE}_{p}_game_rosters_{season}.parquet"
        for p in ("fox", "yahoo")
    )
    return root if any(f.exists() for f in parsed) else None


def _tree(dataset: str, season: int, base: Path) -> Path:
    spec = REGISTRY[dataset]
    return io.dataset_dir(spec, Path(base)) / "parquet" / f"{spec.stem}_{season}.parquet"


def _espn_input(dataset: str, season: int, base: Path) -> pl.DataFrame:
    """The season's ESPN ``schedules`` / ``game_rosters`` frame: this tree, else the release.

    The tree is not complete (``wbb/game_rosters/parquet`` holds 2004-07 and 2023+, the
    release 2004+), and reading it alone left every 2015-22 fill a silent no-op. Missing
    from both raises: the season has a crosswalk and a parsed alt season, so it is a gap.
    """
    path = _tree(dataset, season, base)
    if path.exists():
        return pl.read_parquet(path)
    spec = REGISTRY[dataset]
    url = f"{RELEASE}/{spec.tag}/{spec.stem}_{season}.parquet"
    body = ingest._http_get_bytes(url)  # retries 429 / 5xx with backoff
    if body is None:
        raise RuntimeError(f"{dataset} {season}: not in the tree and no release asset at {url}")
    log.info("%s %s: not in the tree, read %s", dataset, season, url)
    return pl.read_parquet(BytesIO(body))


def _non_null(df: pl.DataFrame) -> dict[str, int]:
    return df.select(pl.all().is_not_null().sum()).row(0, named=True)


def fill_frame(
    dataset: str,
    season: int,
    current: pl.DataFrame,
    schedule: pl.DataFrame,
    rosters: pl.DataFrame,
    root: Path,
) -> pl.DataFrame:
    """``current`` with its null Fox / Yahoo ids filled; raises if anything would be lost.

    A leg column sdv-py fills but this crosswalk lacks (the schedule crosswalk has no
    ``fox_home_team_id`` / ``fox_away_team_id``) is added null for the call and dropped
    after, so the published schema never changes.
    """
    from sportsdataverse._crosswalk_alt import with_alt_game_legs, with_alt_player_legs

    fn = with_alt_player_legs if dataset == "player_crosswalk" else with_alt_game_legs
    extra = [c for cols in _legs(dataset).values() for c in cols if c not in current.columns]
    if extra:
        log.info("%s %s: not in the schema, filled then dropped: %s", dataset, season, extra)
    padded = current.with_columns(pl.lit(None, dtype=pl.Utf8).alias(c) for c in extra)
    out = fn(LEAGUE, season, padded, schedule, rosters, root).select(current.columns)
    before, after = _non_null(current), _non_null(out)
    lost = {c: (before[c], after[c]) for c in before if after[c] < before[c]}
    if out.schema != current.schema or out.height != current.height or lost:
        raise RuntimeError(f"{dataset} {season}: fill would drop data {lost or 'rows/columns'}")
    return out


def fill(
    dataset: str,
    season: int,
    *,
    base: str | Path = "wbb",
    out: str | Path | None = None,
    publish_release: bool = False,
) -> pl.DataFrame | None:
    """Fill one committed crosswalk's Fox / Yahoo legs; None when there is nothing to fill.

    Reads from ``base``, writes to ``out`` (default ``base``) only when an id changed, and
    publishes that write when ``publish_release``.
    """
    base = Path(base)
    root = alt_root(season)
    path = _tree(dataset, season, base)
    if root is None or not path.exists():
        log.warning("%s %s: no parsed alt season or no %s; nothing to fill", dataset, season, path)
        return None
    schedule, rosters = (_espn_input(d, season, base) for d in ("schedules", "game_rosters"))
    current = pl.read_parquet(path)
    frame = fill_frame(dataset, season, current, schedule, rosters, root)
    before, after = _non_null(current), _non_null(frame)
    for cols in _legs(dataset).values():
        for c in (c for c in cols if c in before):
            log.info(
                "%s %s: %s %d -> %d / %d", dataset, season, c, before[c], after[c], frame.height
            )
    if frame.equals(current):
        log.info("%s %s: Fox / Yahoo ids unchanged; nothing written", dataset, season)
        return frame
    spec = REGISTRY[dataset]
    io.write_dataset(frame, spec, season, base=Path(out) if out else base)
    if publish_release:
        publish.publish_dataset(spec, season, base=Path(out) if out else base)
    return frame


def carry_forward(df: pl.DataFrame, dataset: str, season: int, base: str | Path) -> pl.DataFrame:
    """Keep the committed crosswalk's Fox / Yahoo legs where a fresh build left the id null.

    The live builder rebuilds the crosswalk from today's Fox / Yahoo feeds, which would blank
    every id :func:`fill` took from the history. Per provider, a row whose id is null takes
    that provider's columns (id + name) from the committed file on the stable keys, so a
    carried id never pairs with a fresh name. Columns, dtypes and row order are unchanged.
    """
    path = _tree(dataset, season, Path(base))
    if df.height == 0 or not path.exists():
        return df
    prev = pl.read_parquet(path)
    keys = KEYS[dataset]
    out = df
    for provider, cols in _legs(dataset).items():
        cols = [c for c in cols if c in df.columns and c in prev.columns]
        if not cols or not set(keys) <= set(prev.columns):
            continue
        for k in keys:
            assert df.schema[k] == prev.schema[k], (
                f"{k}: {df.schema[k]} vs committed {prev.schema[k]}"
            )
        old = (
            prev.filter(pl.col(cols[0]).is_not_null())
            .select(*keys, *[pl.col(c).alias(f"_prev_{c}") for c in cols])
            .unique(subset=keys, keep="none")
        )
        empty = pl.col(cols[0]).is_null()
        out = (
            out.join(old, on=keys, how="left", maintain_order="left")
            .with_columns(
                pl.when(empty).then(pl.col(f"_prev_{c}")).otherwise(pl.col(c)).alias(c)
                for c in cols
            )
            .select(df.columns)
        )
        log.info(
            "%s %s: %s carried forward %d",
            dataset,
            season,
            cols[0],
            out[cols[0]].is_not_null().sum() - df[cols[0]].is_not_null().sum(),
        )
    assert out.height == df.height, f"{dataset} carry-forward changed the row count"
    return out


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="wbb_data_build.alt_fill")
    p.add_argument("-s", "--start", type=int, required=True)
    p.add_argument("-e", "--end", type=int, default=None)
    p.add_argument("--base", default="wbb")
    p.add_argument("--out", default=None, help="write here instead of --base (dry runs)")
    p.add_argument("--dataset", choices=sorted(KEYS), action="append")
    p.add_argument("--publish", action="store_true")
    a = p.parse_args(argv)
    for season in range(a.start, (a.end or a.start) + 1):
        for ds in a.dataset or sorted(KEYS, reverse=True):  # schedule, then player
            fill(ds, season, base=a.base, out=a.out, publish_release=a.publish)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
