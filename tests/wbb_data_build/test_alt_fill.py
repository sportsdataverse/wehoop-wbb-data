"""Fox / Yahoo legs from wehoop-wbb-alt-data (``wbb_data_build.alt_fill``): fill nulls, never lose data."""

from __future__ import annotations

from io import BytesIO

import polars as pl
import pytest

alt = pytest.importorskip("sportsdataverse._crosswalk_alt")

from wbb_data_build import alt_fill  # noqa: E402

PLAYER = {
    "espn_team_id": pl.Series([150, 150, 153], dtype=pl.Int32),
    "espn_athlete_id": ["1", "2", "3"],
    "fox_athlete_id": ["f1", None, None],
    "fox_player": ["A", None, None],
    "yahoo_player_id": [None, "y2", None],
    "yahoo_player_name": [None, "B", None],
}


def test_alt_root_needs_a_parsed_season(tmp_path, monkeypatch):
    monkeypatch.setenv(alt_fill.ALT_ENV, str(tmp_path))
    f = alt.season_path(tmp_path, "yahoo", "wbb", "game_rosters", 2026)
    f.parent.mkdir(parents=True)
    f.touch()
    assert alt_fill.alt_root(2026) == tmp_path
    assert alt_fill.alt_root(2025) is None


def test_schedule_fill_drops_legs_outside_the_schema_and_refuses_a_loss(monkeypatch):
    current = pl.DataFrame(
        {"espn_game_id": ["9"], "fox_game_id": [None], "yahoo_game_id": ["y"]},
        schema_overrides={"fox_game_id": pl.Utf8},
    )

    def fill(league, season, xwalk, *args):
        assert {"fox_home_team_id", "fox_away_team_id"} <= set(xwalk.columns)  # padded for sdv-py
        return xwalk.with_columns(
            pl.lit("42").alias("fox_game_id"), pl.lit("t").alias("fox_home_team_id")
        )

    monkeypatch.setattr(alt, "with_alt_game_legs", fill)
    out = alt_fill.fill_frame("schedule_crosswalk", 2026, current, None, None, None)
    assert out.columns == current.columns and out["fox_game_id"].to_list() == ["42"]

    monkeypatch.setattr(
        alt,
        "with_alt_game_legs",
        lambda lg, s, x, *a: x.with_columns(pl.lit(None, dtype=pl.Utf8).alias("yahoo_game_id")),
    )
    with pytest.raises(RuntimeError, match="yahoo_game_id"):
        alt_fill.fill_frame("schedule_crosswalk", 2026, current, None, None, None)


def test_carry_forward_keeps_committed_legs_where_the_rebuild_is_null(tmp_path):
    base = tmp_path / "wbb"
    committed = pl.DataFrame(PLAYER).with_columns(
        pl.Series("yahoo_player_id", ["y1", "y2", "y3"]),
        pl.Series("yahoo_player_name", ["a", "b", "c"]),
    )
    path = alt_fill._tree("player_crosswalk", 2026, base)
    path.parent.mkdir(parents=True)
    committed.write_parquet(path)
    fresh = pl.DataFrame(PLAYER)  # the live rebuild: yahoo only for row 2, from today's roster
    out = alt_fill.carry_forward(fresh, "player_crosswalk", 2026, base)
    assert out.columns == fresh.columns and out.height == 3
    assert out["yahoo_player_id"].to_list() == ["y1", "y2", "y3"]
    # a fresh id keeps its fresh name; a carried id brings its own
    assert out["yahoo_player_name"].to_list() == ["a", "B", "c"]
    assert out["fox_athlete_id"].to_list() == ["f1", None, None]
    assert alt_fill.carry_forward(fresh, "player_crosswalk", 2025, base).equals(fresh)


def _tree_without_game_rosters(tmp_path, monkeypatch, body):
    """A 2015 tree with the crosswalk + schedule but no game rosters; the release GET mocked."""
    from wbb_data_build import ingest

    base = tmp_path / "wbb"
    for dataset, frame in (
        ("player_crosswalk", pl.DataFrame(PLAYER)),
        ("schedules", pl.DataFrame({"game_id": [1]})),
    ):
        path = alt_fill._tree(dataset, 2015, base)
        path.parent.mkdir(parents=True)
        frame.write_parquet(path)
    urls = []
    monkeypatch.setattr(ingest, "_http_get_bytes", lambda url: urls.append(url) or body)
    monkeypatch.setattr(alt_fill, "alt_root", lambda season: tmp_path)
    return base, urls


def test_fill_reads_espn_inputs_the_tree_lacks_from_the_release(tmp_path, monkeypatch):
    # wbb/game_rosters/parquet holds 2004-07 and 2023+ only; the release holds 2004+. Reading
    # the tree alone made every 2015-22 fill a silent "nothing to fill".
    buf = BytesIO()
    pl.DataFrame({"game_id": [7]}).write_parquet(buf)
    base, urls = _tree_without_game_rosters(tmp_path, monkeypatch, buf.getvalue())
    seen = {}

    def fill(league, season, xw, schedule, rosters, root):
        seen.update(schedule=schedule["game_id"].to_list(), rosters=rosters["game_id"].to_list())
        return xw.with_columns(pl.col("yahoo_player_id").fill_null("y"))

    monkeypatch.setattr(alt, "with_alt_player_legs", fill)
    out = tmp_path / "out"
    frame = alt_fill.fill("player_crosswalk", 2015, base=base, out=out)
    assert frame is not None and frame["yahoo_player_id"].to_list() == ["y", "y2", "y"]
    assert seen == {"schedule": [1], "rosters": [7]}  # tree schedule, released game rosters
    assert urls == [
        "https://github.com/sportsdataverse/sportsdataverse-data/releases/download/"
        "espn_womens_college_basketball_game_rosters/game_rosters_2015.parquet"
    ]
    assert alt_fill._tree("player_crosswalk", 2015, out).exists()


def test_fill_raises_when_an_espn_input_is_in_neither_the_tree_nor_the_release(
    tmp_path, monkeypatch
):
    base, _ = _tree_without_game_rosters(tmp_path, monkeypatch, None)
    with pytest.raises(RuntimeError, match="no release asset"):
        alt_fill.fill("player_crosswalk", 2015, base=base, out=tmp_path / "out")
