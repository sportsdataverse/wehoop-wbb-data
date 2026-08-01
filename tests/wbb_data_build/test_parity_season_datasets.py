"""Parity: rosters / player_season_stats / team_season_stats / standings vs
the R-released parquet oracles (all 2026 — those tags carry no earlier assets).

Port provenance: the script-local parsers in
``wehoop-wbb-data/R/espn_wbb_0{4,5,6,7}_*_creation.R`` (no wehoop helpers).
Fixtures: the two teams of fixture game 401804834 (team_ids 197/2429), the
five of their athletes present in the released player_season_stats asset, and
the first two standings conferences; every oracle is pre-filtered to match.
Long-format frames have no compact unique key, so ALL columns act as sort
keys (total order; duplicate rows compare as multisets).
"""

from pathlib import Path

import polars as pl
import pytest
from wbb_data_build import reshapers

from tests.wbb_data_build._parity_helpers import assert_parquet_parity

FX = Path(__file__).parent.parent / "fixtures"


@pytest.mark.parametrize(
    ("dataset", "stem", "keys"),
    [
        ("rosters", "rosters_2026", ["team_id", "athlete_id"]),
        ("player_season_stats", "player_season_stats_2026", None),
        ("team_season_stats", "team_season_stats_2026", None),
        ("standings", "standings_2026", None),
    ],
)
def test_season_dataset_parity_2026(dataset, stem, keys, tmp_path):
    py = reshapers.SEASON_BUILDERS[dataset](2026, raw_root=FX / "raw", base=tmp_path)
    oracle = FX / "released" / f"{stem}.parquet"
    all_cols = list(pl.read_parquet_schema(str(oracle)))
    keys = keys if keys is not None else all_cols
    sample = [c for c in all_cols if c not in keys]
    assert_parquet_parity(py, oracle, keys=keys, sample_cols=sample)
