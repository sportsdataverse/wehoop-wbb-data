"""Per-dataset reshapers -- each takes one game's final.json + returns a frame.

Every reshaper delegates the actual reshape to a ``sportsdataverse.wbb``
producer (shared with WNBA later); this module is just the registry +
per-game glue. Signature contract: ``(final, *, season, game_id) -> pl.DataFrame``.
"""

from __future__ import annotations

import polars as pl
from sportsdataverse.wbb import helper_wbb_team_box


def team_box_reshaper(final: dict, *, season: int, game_id: int) -> pl.DataFrame:
    return helper_wbb_team_box(final)


RESHAPERS: dict = {
    "team_box": team_box_reshaper,
}
