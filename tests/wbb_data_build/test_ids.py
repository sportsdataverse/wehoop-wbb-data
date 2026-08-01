"""Id canonicalization at the write boundary.

The released datasets shipped the same id with three different dtypes, so
joining them raised SchemaError. These tests pin the fix and its refusals.
"""

from __future__ import annotations

import polars as pl
import pytest
from wbb_data_build.ids import canonicalize_ids, is_id_column, to_int64


@pytest.mark.parametrize(
    "values,dtype",
    [
        ([401811123], pl.Int32),
        ([401811123], pl.Int64),
        (["401811123"], pl.Utf8),
        ([401811123.0], pl.Float64),
    ],
    ids=["int32", "int64", "utf8", "float64"],
)
def test_every_source_dtype_lands_on_int64(values, dtype):
    out = to_int64(pl.Series("game_id", values, dtype=dtype))
    assert out.dtype == pl.Int64
    assert out[0] == 401811123


def test_nulls_survive():
    assert to_int64(pl.Series("game_id", [None, 1], dtype=pl.Int32)).null_count() == 1


def test_lossy_float_refuses():
    with pytest.raises(ValueError, match="lossy"):
        to_int64(pl.Series("game_id", [401811123.5]))


def test_non_numeric_string_refuses():
    with pytest.raises(ValueError, match="non-numeric"):
        to_int64(pl.Series("game_id", ["not-an-id"]))


@pytest.mark.parametrize(
    "name,expected",
    [
        ("id", True),
        ("game_id", True),
        ("athlete_id", True),
        ("season", False),
        ("identifier", False),
    ],
)
def test_id_column_detection(name, expected):
    assert is_id_column(name) is expected


def test_canonicalize_widens_every_id_column():
    df = pl.DataFrame(
        {"game_id": [1], "athlete_id": ["2"], "team_id": [3], "season": [2026], "text": ["x"]},
        schema={
            "game_id": pl.Int32,
            "athlete_id": pl.Utf8,
            "team_id": pl.Int32,
            "season": pl.Int32,
            "text": pl.Utf8,
        },
    )
    out = canonicalize_ids(df)
    assert out.schema["game_id"] == pl.Int64
    assert out.schema["athlete_id"] == pl.Int64
    assert out.schema["team_id"] == pl.Int64
    # Non-id columns are untouched -- season stays Int32, text stays Utf8.
    assert out.schema["season"] == pl.Int32
    assert out.schema["text"] == pl.Utf8


def test_the_two_joins_that_used_to_raise_now_work():
    """player_box x rosters on athlete_id, and player_box x officials on
    game_id, both raised SchemaError on the released data."""
    player_box = canonicalize_ids(
        pl.DataFrame(
            {"athlete_id": [1, 2], "game_id": [9, 9]},
            schema={"athlete_id": pl.Int32, "game_id": pl.Int32},
        )
    )
    rosters = canonicalize_ids(
        pl.DataFrame({"athlete_id": ["1", "2"]}, schema={"athlete_id": pl.Utf8})
    )
    officials = canonicalize_ids(pl.DataFrame({"game_id": ["9"]}, schema={"game_id": pl.Utf8}))
    assert player_box.join(rosters, on="athlete_id", how="inner").height == 2
    assert player_box.join(officials, on="game_id", how="inner").height == 2


def test_a_non_numeric_id_is_left_alone_rather_than_failing_the_build():
    """Default is non-strict: one unparseable id column must not cost a whole
    season's build. strict=True is available for callers that want the raise."""
    df = pl.DataFrame(
        {"group_id": ["50-conf"], "team_id": [1]}, schema={"group_id": pl.Utf8, "team_id": pl.Int32}
    )
    out = canonicalize_ids(df)
    assert out.schema["group_id"] == pl.Utf8
    assert out.schema["team_id"] == pl.Int64
    with pytest.raises(ValueError):
        canonicalize_ids(df, strict=True)
