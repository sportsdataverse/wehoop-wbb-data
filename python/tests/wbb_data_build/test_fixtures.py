from pathlib import Path

import polars as pl

FX = Path(__file__).parent.parent / "fixtures"


def test_released_oracle_present_and_small():
    r = pl.read_parquet(FX / "released" / "team_box_2025.parquet")
    assert r.height > 0 and "game_id" in r.columns
    assert r.get_column("game_id").n_unique() == 3


def test_raw_fixtures_present():
    finals = list((FX / "raw" / "wbb" / "json" / "final").glob("*.json"))
    assert len(finals) == 3
    sched = pl.read_parquet(
        FX / "raw" / "wbb" / "schedules" / "parquet" / "wbb_schedule_2025.parquet"
    )
    assert sched.filter(pl.col("game_json") == True).height == 3  # noqa: E712
