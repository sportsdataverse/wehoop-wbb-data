"""Per-dataset reshape functions -- TEMPORARY STUB.

Real reshapers (one per ``config.REGISTRY`` reshaper key, each delegating to
the sdv-py producer) land in Task 8. This stub only unblocks ``build.py``
imports; ``build_season`` never looks up ``RESHAPERS`` for an empty season.
"""

from __future__ import annotations

RESHAPERS: dict = {}
