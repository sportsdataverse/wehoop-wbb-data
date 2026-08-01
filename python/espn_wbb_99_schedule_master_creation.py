"""Builder: WBB schedule master, games-in-data-repo manifest, and coverage index.

Runs LAST in the daily processor, after every dataset is built -- the flags it
unions only mean anything once the compilations they describe exist.

Emits two artifacts from one in-memory frame, so they cannot drift:

* ``wbb/wbb_schedule_master.parquet`` -- every game the schedule knows about.
* ``wbb/wbb_games_in_data_repo.parquet`` -- only games in >=1 compilation. This
  is the single manifest that replaces the seven per-dataset
  ``wbb/<ds>/wbb_<ds>_in_data_repo.csv`` files.

Example:
    Rebuild from the committed season schedules::

        uv run python python/espn_wbb_99_schedule_master_creation.py
"""

from __future__ import annotations

import argparse
from pathlib import Path

import polars as pl
from wbb_data_build.master import build_coverage, build_master, games_in_data_repo

REPO_ROOT = Path(__file__).resolve().parents[1]
LEAGUE = "wbb"
SEASON_DIR = REPO_ROOT / LEAGUE / "schedules" / "parquet"
MASTER_PATH = REPO_ROOT / LEAGUE / f"{LEAGUE}_schedule_master.parquet"
MANIFEST_PATH = REPO_ROOT / LEAGUE / f"{LEAGUE}_games_in_data_repo.parquet"
COVERAGE_PATH = REPO_ROOT / LEAGUE / f"{LEAGUE}_schedule_coverage.parquet"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build the WBB schedule master + manifest.")
    parser.add_argument("--base", default=str(REPO_ROOT / LEAGUE), help="Dataset tree root")
    args = parser.parse_args(argv)

    base = Path(args.base)
    season_dir = base / "schedules" / "parquet"
    paths = sorted(season_dir.glob(f"{LEAGUE}_schedule_*.parquet"))
    if not paths:
        print(f"::error ::no season schedules under {season_dir}")
        return 1

    master = build_master([pl.read_parquet(p) for p in paths])
    manifest = games_in_data_repo(master)
    coverage = build_coverage(master)

    for frame, path in (
        (master, base / f"{LEAGUE}_schedule_master.parquet"),
        (manifest, base / f"{LEAGUE}_games_in_data_repo.parquet"),
        (coverage, base / f"{LEAGUE}_schedule_coverage.parquet"),
    ):
        frame.write_parquet(path)

    print(f"master:   {master.height} games across {len(paths)} seasons")
    print(f"manifest: {manifest.height} games in >=1 compilation")
    print(f"coverage: {coverage.height} rows")
    for flag in sorted(c for c in master.columns if c.startswith("in_")):
        print(f"  {flag}: {master[flag].sum()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
