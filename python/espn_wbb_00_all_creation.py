"""Builder: every Python-built WBB dataset, in dependency order.

Order is load-bearing, not cosmetic:

* ``shots`` project the built ``pbp`` parquet.
* ``schedules`` stamp build-state flags from the built pbp/team_box/player_box
  parquets, so those three must exist first.

``team_crosswalk`` (13) and ``schedule_crosswalk`` (14) run last: they read
LIVE ESPN/Fox/Torvik rather than the raw tree, so nothing downstream depends on
them and a live-source outage cannot cost the raw-derived datasets. The player
crosswalk (15) stays on R and is run by the daily processor after this script;
it needs off-season ESPN roster coverage sdv-py does not yet carry.

Example:
    One season, everything::

        uv run python python/espn_wbb_00_all_creation.py -s 2026

    A range, publishing to the release tags::

        uv run python python/espn_wbb_00_all_creation.py -s 2004 -e 2026 --publish
"""

from __future__ import annotations

from wbb_data_build._logging import get_logger
from wbb_data_build.build import build_season
from wbb_data_build.entrypoint import season_parser

log = get_logger()

ORDER = [
    "pbp",
    "team_box",
    "player_box",
    "player_core",
    "schedules",
    "shots",
    "rosters",
    "player_season_stats",
    "team_season_stats",
    "standings",
    "game_rosters",
    "officials",
    "team_crosswalk",
    "schedule_crosswalk",
    "player_crosswalk",
]


def main(argv: list[str] | None = None) -> int:
    args = season_parser("all WBB datasets").parse_args(argv)
    end = args.end if args.end is not None else args.start
    failed: list[str] = []
    for season in range(args.start, end + 1):
        for dataset in ORDER:
            print(f"::group::{dataset} {season}", flush=True)
            try:
                frame = build_season(
                    dataset,
                    season,
                    base=args.base,
                    raw_root=args.raw_root,
                    publish_release=args.publish,
                    dry_run=args.dry_run,
                )
                log.info("%s %s: %d rows", dataset, season, frame.height)
            except Exception as exc:
                # One dataset failing must not cost the rest of the season, but
                # the run still goes red so somebody looks.
                print(f"::warning ::{dataset} {season} failed: {exc!r}", flush=True)
                failed.append(f"{dataset}:{season}")
            finally:
                print("::endgroup::", flush=True)
    for item in failed:
        print(f"::error ::{item} failed", flush=True)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
