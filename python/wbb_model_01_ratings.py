"""Stage 01 — WBB opponent-adjusted team ratings.

Thin numbered entry over ``wbb_model_publish ratings``; args forward verbatim (injects the ``ratings`` subcommand).
Compute-on-demand (engines in sdv-py); card sidecar is the per-publish ledger.
Usage::

    python -m wbb_model_01_ratings --start 2025 --end 2026
    scripts/wbb_models.sh 01
"""
from __future__ import annotations

import sys


def main(argv: list[str] | None = None) -> int:
    from wbb_model_publish.cli import main as _main

    argv = list(argv) if argv is not None else sys.argv[1:]
    return _main(["ratings", *argv])


if __name__ == "__main__":
    raise SystemExit(main())
