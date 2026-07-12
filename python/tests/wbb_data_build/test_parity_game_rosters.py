"""Parity: Python game_rosters + officials vs the R-released parquet oracles.

Port provenance: script-local ``parse_one_game``/``parse_one_athlete`` in
``wehoop-wbb-data/R/espn_wbb_08_game_rosters_creation.R`` and
``parse_one_game``/``parse_one_official`` in ``espn_wbb_09_officials_creation.R``
(no wehoop helpers exist for these datasets). Oracles:
``tests/fixtures/released/{game_rosters,officials}_2026.parquet`` — the
published 2026-only assets pre-filtered to the three 2026 fixture games.
``game_id`` is String in both (R keeps ``as.character``).
"""

from pathlib import Path

import polars as pl
import pytest

from tests.wbb_data_build._parity_helpers import assert_parquet_parity
from wbb_data_build import reshapers

FX = Path(__file__).parent.parent / "fixtures"


@pytest.mark.parametrize(
    ("dataset", "stem", "keys"),
    [
        ("game_rosters", "game_rosters_2026", ["game_id", "athlete_id"]),
        ("officials", "officials_2026", ["game_id", "official_id"]),
    ],
)
def test_sidecar_parity_2026(dataset, stem, keys, tmp_path):
    py = reshapers.SEASON_BUILDERS[dataset](2026, raw_root=FX / "raw", base=tmp_path)
    oracle = FX / "released" / f"{stem}.parquet"
    sample = [c for c in pl.read_parquet_schema(str(oracle)) if c not in keys]
    assert_parquet_parity(py, oracle, keys=keys, sample_cols=sample)
