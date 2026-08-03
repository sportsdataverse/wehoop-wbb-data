"""Post-publish win-probability enrichment for the season's pbp release assets.

Why this exists as a separate step rather than a pbp reshaper:

* The enrichment needs the season's **team_box**, and `pbp` is built *before*
  `team_box`, so it cannot run inside the pbp build without inverting a
  load-bearing build order.
* Its contract is "rewrite the season's pbp with the two WP columns appended,
  every original column preserved" — an operation on the *published* season, not
  on the in-memory frame mid-build.

Without this step nothing ever calls `sportsdataverse.wbb.build_wbb_season_wp`,
and each nightly pbp publish silently strips the WP columns off the release.
That is what happened between 2026-07-12 (columns verified present) and
2026-08-02 (absent from every season), breaking the platform's win-probability
page.

Publishing goes through the normal `io.write_dataset` + `publish.publish_dataset`
path so **parquet, csv and rds are all regenerated together**. Writing only the
parquet is how the formats drift: `wehoop::load_wbb_*` reads `.rds` exclusively,
so a parquet-only republish leaves every R user on un-enriched data from a
release that looks fresh. Mirrors `mbb_data_build.wp_enrich` in hoopR-mbb-data.
"""

from __future__ import annotations

from pathlib import Path

from wbb_data_build import io, publish
from wbb_data_build._logging import get_logger
from wbb_data_build.config import REGISTRY

log = get_logger()

WP_COLS = ("pregame_home_prob", "home_win_prob")


def enrich_and_publish(
    season: int,
    *,
    base: str | Path = "wbb",
    dry_run: bool = False,
) -> bool:
    """Rebuild the season's pbp with WP columns and republish all three formats.

    Returns True when the season was republished (or would be, under dry_run).
    Never raises: a WP failure must not fail the nightly, since the plain pbp
    published moments earlier is still valid data.
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

    if dry_run:
        log.info(
            "wp %s: would rewrite + publish %s_%s parquet/csv/rds (%d rows)",
            season,
            spec.stem,
            season,
            frame.height,
        )
        return True

    io.write_dataset(frame, spec, season, base=base)
    publish.publish_dataset(spec, season, base=base, dry_run=False)
    log.info(
        "wp %s: republished parquet+csv+rds with %s (%d rows)",
        season,
        list(WP_COLS),
        frame.height,
    )
    return True


def main(argv: list[str] | None = None) -> int:
    import argparse

    p = argparse.ArgumentParser(prog="wbb_data_build.wp_enrich")
    p.add_argument("-s", "--start", type=int, required=True)
    p.add_argument("-e", "--end", type=int, required=True)
    p.add_argument("--base", default="wbb")
    p.add_argument("--dry-run", action="store_true")
    a = p.parse_args(argv)
    ok = True
    for season in range(a.start, a.end + 1):
        ok = enrich_and_publish(season, base=a.base, dry_run=a.dry_run) and ok
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
