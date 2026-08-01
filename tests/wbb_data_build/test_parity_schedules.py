"""Parity: Python schedules vs the R-released parquet oracle.

Port provenance: the schedule blocks of ``espn_wbb_0{1,2,3}_*_creation.R``
(casts + game_date_time/game_date + PBP/team_box/player_box flag stamping;
script 03 uploads). Oracle: ``tests/fixtures/released/wbb_schedule_2025.parquet``
— the published ``espn_womens_college_basketball_schedules`` asset pre-filtered
to the three fixture games. All three fixture games compiled in the real R run,
so all three flags are True on every oracle row; the fixture id-sets mirror that.
"""

from pathlib import Path

import polars as pl
from wbb_data_build import reshapers

from tests.wbb_data_build._parity_helpers import assert_parquet_parity

FX = Path(__file__).parent.parent / "fixtures"

GIDS = [401700473, 401700474, 401700475]


def test_schedules_parity_2025(tmp_path):
    from sportsdataverse.wbb import helper_wbb_schedule

    raw = pl.read_parquet(
        FX / "raw" / "wbb" / "schedules" / "parquet" / "wbb_schedule_2025.parquet"
    )
    py = helper_wbb_schedule(
        raw, pbp_game_ids=GIDS, team_box_game_ids=GIDS, player_box_game_ids=GIDS
    )
    oracle = FX / "released" / "wbb_schedule_2025.parquet"
    sample = [c for c in pl.read_parquet_schema(str(oracle)) if c != "game_id"]
    assert_parquet_parity(py, oracle, keys=["game_id"], sample_cols=sample)


def test_schedules_builder_reads_built_ids(tmp_path):
    # No built datasets under base -> all flags False (R empty-espn_df branch).
    out = reshapers.schedules_builder(2025, raw_root=FX / "raw", base=tmp_path)
    assert out.get_column("PBP").to_list() == [False] * out.height
    assert out.get_column("team_box").to_list() == [False] * out.height
