"""ESPN win probability joined onto pbp.

ESPN ships one winprobability row per play (``playId``, ``homeWinPercentage``,
``tiePercentage``) as JSON *strings* for the id. pbp carries ``id`` as Int64.
The cast happens once, in the join, with both sides asserted equal -- a
mismatch matches nothing and produces an all-null column that reads exactly
like "ESPN published no win probability for this game".
"""

from __future__ import annotations

import polars as pl
import pytest
from wbb_data_build.reshapers import WP_COLUMNS, join_win_probability, wp_frame

PLAYS = pl.DataFrame(
    {
        "game_id": [401811123] * 3,
        "id": [401811123113565895, 401811123113565896, 401811123113565897],
    },
    schema={"game_id": pl.Int64, "id": pl.Int64},
)


def _wp(rows: list[dict]) -> pl.DataFrame:
    return pl.DataFrame(
        rows,
        schema={
            "playId": pl.Utf8,
            "homeWinPercentage": pl.Float64,
            "tiePercentage": pl.Float64,
        },
        orient="row" if rows else None,
    )


def _one(home: float = 0.6, tie: float = 0.0) -> pl.DataFrame:
    return _wp([{"playId": "401811123113565895", "homeWinPercentage": home, "tiePercentage": tie}])


def test_columns_added_and_row_count_unchanged():
    out = join_win_probability(PLAYS, _one())
    assert out.height == PLAYS.height
    for column in WP_COLUMNS:
        assert column in out.columns


def test_away_wp_is_the_complement():
    out = join_win_probability(PLAYS, _one(home=0.6, tie=0.1))
    row = out.filter(pl.col("id") == 401811123113565895).to_dicts()[0]
    assert row["espn_away_wp"] == pytest.approx(0.3)


def test_unmatched_plays_get_null_not_zero():
    """A 0.0 win probability is a claim; a null is an absence."""
    out = join_win_probability(PLAYS, _one())
    assert out["espn_home_wp"].null_count() == 2


def test_missing_section_yields_all_null_columns():
    out = join_win_probability(PLAYS, _wp([]))
    assert out.height == 3
    for column in WP_COLUMNS:
        assert out[column].null_count() == 3
        assert out.schema[column] == pl.Float64


def test_join_keys_are_int64_on_both_sides():
    out = join_win_probability(PLAYS, _one())
    assert out.schema["id"] == pl.Int64
    assert out.filter(pl.col("id") == 401811123113565895)["espn_home_wp"][0] == 0.6


def test_duplicate_wp_rows_do_not_multiply_plays():
    dupes = _wp(
        [
            {"playId": "401811123113565895", "homeWinPercentage": 0.6, "tiePercentage": 0.0},
            {"playId": "401811123113565895", "homeWinPercentage": 0.7, "tiePercentage": 0.0},
        ]
    )
    assert join_win_probability(PLAYS, dupes).height == 3


def test_empty_plays_frame_still_gains_the_columns():
    """Empty frames carry the documented schema, per the module pattern."""
    empty = PLAYS.head(0)
    out = join_win_probability(empty, _one())
    assert out.height == 0
    for column in WP_COLUMNS:
        assert column in out.columns


# --- payload extraction ------------------------------------------------------


def test_wp_frame_reads_the_payload_section():
    payload = {
        "winprobability": [
            {"playId": "1", "homeWinPercentage": 0.5, "tiePercentage": 0.0},
            {"playId": "2", "homeWinPercentage": 0.7, "tiePercentage": 0.0},
        ]
    }
    assert wp_frame(payload).height == 2


def test_wp_frame_handles_an_absent_section():
    assert wp_frame({}).height == 0
    assert wp_frame({"winprobability": None}).height == 0


def test_wp_frame_handles_the_dict_variant():
    """The section is a list in most payloads and a dict in some -- the sdv-py
    raw schema declares it as a union for exactly this reason."""
    assert wp_frame({"winprobability": {}}).height == 0
