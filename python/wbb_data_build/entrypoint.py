"""Shared ``__main__`` body for the numbered ``espn_wbb_NN_*_creation.py`` scripts.

Each numbered script is a thin entrypoint: a docstring, a ``DATASET`` constant,
and a call to :func:`run`. Everything they would otherwise duplicate lives here,
so the CLI contract is defined once and cannot drift between datasets.
"""

from __future__ import annotations

import argparse

from wbb_data_build._logging import get_logger
from wbb_data_build.build import build_season

log = get_logger()


def season_parser(dataset: str) -> argparse.ArgumentParser:
    """The argument contract every builder shares.

    Mirrors ``python -m wbb_data_build`` so the numbered scripts and the module
    CLI are interchangeable.
    """
    parser = argparse.ArgumentParser(description=f"Build the {dataset} dataset.")
    parser.add_argument("-s", "--start", type=int, required=True, help="Start season end-year")
    parser.add_argument("-e", "--end", type=int, default=None, help="End season end-year")
    parser.add_argument("--base", default="wbb", help="Output tree root")
    parser.add_argument("--raw-root", default=None, help="wehoop-wbb-raw checkout or HTTP root")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--publish", action="store_true", help="Upload to the release tag")
    group.add_argument("--dry-run", action="store_true", help="Build but write nothing")
    return parser


def run(dataset: str, argv: list[str] | None = None) -> int:
    """Build one dataset across a season range.

    Args:
        dataset: A key of ``wbb_data_build.config.REGISTRY``.
        argv: Argument list; defaults to ``sys.argv[1:]``.

    Returns:
        0 on success, 1 if any season raised.
    """
    args = season_parser(dataset).parse_args(argv)
    end = args.end if args.end is not None else args.start
    failed: list[int] = []
    for season in range(args.start, end + 1):
        try:
            frame = build_season(
                dataset,
                season,
                base=args.base,
                raw_root=args.raw_root,
                publish_release=args.publish,
                dry_run=args.dry_run,
            )
            log.info("%s %s: season complete -- %d rows", dataset, season, frame.height)
        except Exception as exc:
            # One bad season must not abort the range; the run still goes red.
            log.warning("%s %s failed: %r", dataset, season, exc)
            failed.append(season)
    for season in failed:
        print(f"::error ::{dataset} {season} failed", flush=True)
    return 1 if failed else 0
