"""stats.ncaa.org id legs of the schedule + player crosswalks (``wbb_data_build.ncaa``).

Fixture rows are copied from the published 2024 / 2025 files (``ncaa_wbb_schedule_2024``,
``wbb_crosswalk/ncaa_espn_team_crosswalk``, ``wbb_schedule_crosswalk_2024``,
``wbb_player_crosswalk_2025``, ``wbb_groups/wbb_player_aliases``); the one synthetic row is
marked where it is made.
"""

from __future__ import annotations

from datetime import date

import polars as pl
from wbb_data_build import ncaa

TEAMS = pl.DataFrame(
    {
        "season": ["2023-24"] * 7 + ["2024-25"],
        "ncaa_team": [
            "Rutgers", "Monmouth", "TCU", "UTEP", "Ohio St.", "Iowa", "Fairleigh Dickinson", "FDU",
        ],
        "espn_team_id": ["164", "2405", "2628", "2638", "194", "2294", "161", "161"],
    }
)  # fmt: skip

SCHEDULE = pl.DataFrame(
    {
        "contest_id": ["3728200", "3972675", "3954628", "3953880"],
        "game_date": ["11/06/2023", "11/23/2023", "12/15/2023", "11/06/2023"],
        "home": ["Rutgers", "TCU", "Ohio St.", "Iowa"],
        "away": ["Monmouth", "UTEP", "Grand Valley St.", "FDU"],
        "home_score": [56, 85, 73, 102],
        "away_score": [51, 56, 49, 46],
        "season": [2024] * 4,
    }
)


def _xwalk(rows: list[tuple]) -> pl.DataFrame:
    return pl.DataFrame(
        rows,
        schema={
            "season": pl.Int32,
            "game_date": pl.Date,
            "home_espn_team_id": pl.Int32,
            "away_espn_team_id": pl.Int32,
            "espn_game_id": pl.Utf8,
            "fox_game_id": pl.Utf8,
            "yahoo_game_id": pl.Utf8,
            "match_method": pl.Utf8,
        },
        orient="row",
    )


def _contest_ids(df: pl.DataFrame) -> list:
    out = ncaa.add_ncaa_contest_id(df, 2024, schedule=SCHEDULE, teams=TEAMS)
    assert out.columns.index("ncaa_contest_id") == out.columns.index("yahoo_game_id") + 1
    assert out.drop("ncaa_contest_id").equals(df)
    assert out.schema["ncaa_contest_id"] == pl.Utf8
    return out["ncaa_contest_id"].to_list()


def test_pass1_pair_and_neutral_site_swap():
    df = _xwalk(
        [
            (2024, date(2023, 11, 6), 164, 2405, "401575820", None, None, "espn+bart"),
            # ESPN lists UTEP home; stats.ncaa.org lists TCU home.
            (2024, date(2023, 11, 23), 2638, 2628, "401582227", None, None, "espn+bart"),
            # Same pair, a day off: no match.
            (2024, date(2023, 11, 7), 164, 2405, "1", None, None, "espn"),
        ]
    )
    assert _contest_ids(df) == ["3728200", "3972675", None]


def test_pass2_single_mapped_team_against_non_d1():
    # Grand Valley St. is not in the NCAA->ESPN team crosswalk; ESPN has its own id for it.
    df = _xwalk([(2024, date(2023, 12, 15), 194, 125, "401606633", None, None, "espn")])
    assert _contest_ids(df) == ["3954628"]


def test_pass2_rejects_two_different_d1_opponents():
    # ESPN says Rutgers played TCU that day; NCAA says Monmouth. Both mapped: a conflict.
    df = _xwalk([(2024, date(2023, 11, 6), 164, 2628, "x", None, None, "espn")])
    assert _contest_ids(df) == [None]


def test_renamed_team_falls_back_to_another_seasons_name():
    # The 2024 schedule says "FDU"; the 2023-24 crosswalk row says "Fairleigh Dickinson".
    df = _xwalk([(2024, date(2023, 11, 6), 2294, 161, "401577050", None, None, "espn")])
    assert _contest_ids(df) == ["3953880"]


def test_no_schedule_keeps_null_column_and_rerun_is_stable():
    df = _xwalk([(2009, date(2008, 11, 14), 164, 2405, "1", None, None, "espn")])
    out = ncaa.add_ncaa_contest_id(df, 2009, schedule=None, teams=TEAMS)  # pre-2010: no source
    assert out["ncaa_contest_id"].to_list() == [None]
    assert out.columns.index("ncaa_contest_id") == out.columns.index("yahoo_game_id") + 1
    assert ncaa.add_ncaa_contest_id(out, 2009, schedule=None, teams=TEAMS).columns == out.columns


def test_join_key_dtype_mismatch_fails_loudly():
    df = _xwalk([(2024, date(2023, 11, 6), 164, 2405, "1", None, None, "espn")])
    bad = df.with_columns(pl.col("home_espn_team_id").cast(pl.Int64))
    try:
        ncaa.add_ncaa_contest_id(bad, 2024, schedule=SCHEDULE, teams=TEAMS)
    except AssertionError as e:
        assert "home_espn_team_id" in str(e)
    else:
        raise AssertionError("an Int64 team id must not join an Int32 one silently")


PLAYERS = pl.DataFrame(
    {
        "season": pl.Series([2025, 2025, 2025], dtype=pl.Int32),
        "espn_team_id": pl.Series([41, 2507, 2670], dtype=pl.Int32),
        "player_name": ["paige bueckers", "marta morales romero", "marta morales romero"],
        "espn_athlete_id": ["4433730", "4912216", "4912216"],
        "yahoo_player_id": [None, None, None],
        "yahoo_player_name": [None, None, None],
        "match_method": ["espn_only"] * 3,
    }
)

ALIASES = pl.DataFrame(
    {
        "athlete_id": ["4433730", "4912216", "4912216", "4912216"],
        "source": ["ncaa", "ncaa", "ncaa", "fox"],
        "source_player_id": ["8964856", "8367081", "8724495", "f1"],
        "team_id": ["41", "2507", "2507", "2507"],
        "valid_from": pl.Series([2025, 2024, 2025, 2025], dtype=pl.Int32),
        "valid_to": pl.Series([2025, 2024, 2025, 2025], dtype=pl.Int32),
    }
)


def test_player_id_season_window_and_team_preference():
    out = ncaa.add_ncaa_player_id(PLAYERS, 2025, aliases=ALIASES)
    assert out.columns.index("ncaa_player_id") == out.columns.index("yahoo_player_name") + 1
    assert out.drop("ncaa_player_id").equals(PLAYERS)
    # Morales Romero is listed on both ESPN teams; her one 2025 NCAA id was made on 2507, so
    # the 2670 row stays null (the 2024 id is outside the window, the fox row another source).
    assert out["ncaa_player_id"].to_list() == ["8964856", "8724495", None]


def test_player_multiple_ncaa_ids_prefer_the_rows_team():
    # Synthetic: a second 2025 NCAA id for Morales Romero, made on 2670 (a mid-season move).
    extra = ALIASES.slice(2, 1).with_columns(
        pl.lit("9999999").alias("source_player_id"), pl.lit("2670").alias("team_id")
    )
    two = pl.concat([ALIASES, extra])
    out = ncaa.add_ncaa_player_id(PLAYERS, 2025, aliases=two)
    assert out["ncaa_player_id"].to_list() == ["8964856", "8724495", "9999999"]
    # Two ids, neither on the row's team: ambiguous, left null.
    other = PLAYERS.with_columns(pl.lit(99, pl.Int32).alias("espn_team_id")).slice(1, 1)
    assert ncaa.add_ncaa_player_id(other, 2025, aliases=two)["ncaa_player_id"].to_list() == [None]


def test_player_no_aliases_keeps_null_column():
    out = ncaa.add_ncaa_player_id(PLAYERS, 2009, aliases=ALIASES)
    assert out["ncaa_player_id"].null_count() == 3
    assert out.columns.index("ncaa_player_id") == out.columns.index("yahoo_player_name") + 1


def test_season_label():
    assert ncaa.season_label(2024) == "2023-24" and ncaa.season_label(2010) == "2009-10"
    assert ncaa.season_label(2000) == "1999-00"
