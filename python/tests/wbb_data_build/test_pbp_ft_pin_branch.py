"""Coverage for the R Free-Throw coordinate-pin branch (derived-from-real).

R (``wehoop/R/espn_wbb_data.R:3067-3074``) pins any play whose ``type.text``
matches ``"Free Throw"`` to raw coordinates (x=25, y=13.75) BEFORE the
home-flip transform. That vocabulary is historical: every released season with
coordinates (2021-2026) ships free throws as ``"MadeFreeThrow"`` only — zero
``"Free Throw"`` rows and zero 25/13.75 pin signatures exist in ANY published
asset (verified 2019-2026), so no golden-master fixture can exercise the
branch. Per the port-parity review's fallback, this test uses the REAL 2026
fixture payload (401804834) with the ``type.text`` of three real plays
relabeled to the historical form — everything else is untouched capture.

Expected transform after the pin (R lines 3075-3082):
  home team: coordinate_x = -(13.75 - 41.75) = 28.0, coordinate_y = -(25 - 25) = 0.0
  away team: coordinate_x =  (13.75 - 41.75) = -28.0, coordinate_y = 0.0
The pin applies regardless of the play's original coordinates (even null).
"""

import copy
import json
from pathlib import Path

import polars as pl

FX = Path(__file__).parent.parent / "fixtures"

_HISTORICAL_FT = "Free Throw - 1 of 2"


def test_ft_pin_and_flip_on_relabeled_real_payload():
    from sportsdataverse.wbb import helper_wbb_play_by_play

    final = copy.deepcopy(
        json.loads(
            (FX / "raw" / "wbb" / "json" / "final" / "401804834.json").read_text(encoding="utf-8")
        )
    )
    competitors = final["header"]["competitions"][0]["competitors"]
    home_id = next(int(c["id"]) for c in competitors if c["homeAway"] == "home")
    away_id = next(int(c["id"]) for c in competitors if c["homeAway"] == "away")

    def _plays_for(team_id):
        return [
            p
            for p in final["plays"]
            if p.get("coordinate.x") is not None and p.get("team.id") == str(team_id)
        ]

    # Three real plays, relabeled: a coordinate-bearing play per side (pin must
    # OVERWRITE real coordinates) and one with its coordinate keys removed
    # (every 2026 play ships coordinates, so the coordinate-less case is
    # derived by deleting the keys from a second real play -- the pin must
    # apply even when the original coordinates are absent; R sets them
    # outright).
    home_play, bare_play = _plays_for(home_id)[:2]
    away_play = _plays_for(away_id)[0]
    bare_play.pop("coordinate.x")
    bare_play.pop("coordinate.y")
    marked = {}
    for label, play in (("home", home_play), ("away", away_play), ("bare", bare_play)):
        play["type.text"] = _HISTORICAL_FT
        # Row locator: game_play_number (Int32, unique per game). The play
        # `id` is Int64 in the Python producer (exact), but the R releases
        # ship it Float64 with 1e17-magnitude collisions -- keep the habit of
        # never keying on it.
        marked[label] = play["game_play_number"]

    df = helper_wbb_play_by_play(final)

    def _row(gpn):
        return df.filter(pl.col("game_play_number") == gpn)

    for label, gpn in marked.items():
        row = _row(gpn)
        assert row.height == 1, label
        assert row.get_column("coordinate_x_raw")[0] == 25.0, label
        assert row.get_column("coordinate_y_raw")[0] == 13.75, label

    assert _row(marked["home"]).get_column("coordinate_x")[0] == 28.0
    assert _row(marked["home"]).get_column("coordinate_y")[0] == 0.0
    assert _row(marked["away"]).get_column("coordinate_x")[0] == -28.0
    assert _row(marked["away"]).get_column("coordinate_y")[0] == 0.0
    assert _row(marked["bare"]).get_column("coordinate_x")[0] == 28.0  # home side

    # And the pin didn't leak: an untouched play keeps its exact source
    # coordinates. (Can't use MadeFreeThrow x==25 as the tell -- ESPN's feed
    # natively centers FT x at 25.)
    witness = next(
        p
        for p in final["plays"]
        if p.get("coordinate.x") is not None
        and p["game_play_number"] not in marked.values()
        and p.get("coordinate.x") != 25
    )
    row = _row(witness["game_play_number"])
    assert row.get_column("coordinate_x_raw")[0] == float(witness["coordinate.x"])
    assert row.get_column("coordinate_y_raw")[0] == float(witness["coordinate.y"])
