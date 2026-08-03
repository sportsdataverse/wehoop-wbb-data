"""Post-publish win-probability enrichment for the season's pbp release asset.

Why this exists as a separate step rather than a pbp reshaper:

* The enrichment needs the season's **team_box**, and `pbp` is built *before*
  `team_box`, so it cannot run inside the pbp build without inverting a
  load-bearing build order.
* Its contract is "overwrite `play_by_play_<season>.parquet` with the two WP
  columns appended, every original column preserved" — an operation on the
  *published* asset, not on the in-memory frame.

Without this step nothing ever calls `sportsdataverse.wbb.build_wbb_season_wp`,
and each nightly pbp publish silently strips the WP columns off the release.
That is what happened between 2026-07-12 (columns verified present) and
2026-08-02 (absent from every season), breaking the platform's win-probability
page. Mirrors `mbb_data_build.wp_enrich` in hoopR-mbb-data.
"""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

from wbb_data_build._logging import get_logger
from wbb_data_build.config import REGISTRY

log = get_logger()

WP_COLS = ("pregame_home_prob", "home_win_prob")


def enrich_and_publish(
    season: int,
    *,
    repo: str = "sportsdataverse/sportsdataverse-data",
    dry_run: bool = False,
) -> bool:
    """Rebuild the season's pbp with WP columns and clobber the release asset.

    Returns True when the asset was republished (or would be, under dry_run).
    Never raises: a WP failure must not fail the nightly, since the plain pbp
    asset published moments earlier is still valid data.
    """
    spec = REGISTRY["pbp"]
    try:
        from sportsdataverse.wbb import build_wbb_season_wp

        frame = build_wbb_season_wp(season)
    except Exception as exc:  # noqa: BLE001 - best-effort enrichment
        log.warning("wp %s: build failed (%s); release keeps plain pbp", season, exc)
        return False

    missing = [c for c in WP_COLS if c not in frame.columns]
    if missing:
        log.warning("wp %s: builder returned no %s; skipping publish", season, missing)
        return False
    if frame.height == 0 or frame[WP_COLS[1]].null_count() == frame.height:
        log.warning("wp %s: win probability is entirely null; skipping publish", season)
        return False

    name = f"{spec.stem}_{season}.parquet"
    if dry_run:
        log.info("wp %s: would publish %s (%d rows)", season, name, frame.height)
        return True

    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / name
        frame.write_parquet(path, compression="zstd")
        res = subprocess.run(
            ["gh", "release", "upload", spec.tag, str(path), "--clobber", "--repo", repo],
            capture_output=True,
            text=True,
            timeout=1800,
        )
    if res.returncode != 0:
        log.warning("wp %s: upload failed: %s", season, res.stderr.strip()[:200])
        return False
    log.info("wp %s: republished %s with %s (%d rows)", season, name, list(WP_COLS), frame.height)
    return True


def main(argv: list[str] | None = None) -> int:
    import argparse

    p = argparse.ArgumentParser(prog="wbb_data_build.wp_enrich")
    p.add_argument("-s", "--start", type=int, required=True)
    p.add_argument("-e", "--end", type=int, required=True)
    p.add_argument("--dry-run", action="store_true")
    a = p.parse_args(argv)
    ok = True
    for season in range(a.start, a.end + 1):
        ok = enrich_and_publish(season, dry_run=a.dry_run) and ok
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
