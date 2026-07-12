"""Parity: Python play_by_play vs the R-released parquet oracle.

Port provenance: ``wehoop:::helper_espn_wbb_pbp``
(``wehoop/R/espn_wbb_data.R`` lines 2763-3160, wehoop 3.0.0). Oracles:
``tests/fixtures/released/play_by_play_{2025,2026}.parquet`` — the published
``espn_womens_college_basketball_pbp`` assets pre-filtered to the fixture
games. 2025 exercises the coordinate-less path (creation-script NA fallback);
2026 exercises the live coordinate transform (FT adjustment + home-flip).
``media_id`` (2025) is a season-union artifact — a column contributed by
other games in the season compile — hence ``allow_r_only_all_null=True``.
"""

from pathlib import Path

import polars as pl
import pytest

from tests.wbb_data_build._parity_helpers import assert_parquet_parity
from wbb_data_build.build import build_season

FX = Path(__file__).parent.parent / "fixtures"

KEYS = ["game_id", "game_play_number"]


@pytest.mark.parametrize("season", [2025, 2026])
def test_pbp_parity(season, tmp_path):
    # Production path: build_season owns the R arrange(desc(game_date)) sort.
    py = build_season("pbp", season, base=tmp_path, raw_root=FX / "raw")
    oracle = FX / "released" / f"play_by_play_{season}.parquet"
    sample = [c for c in pl.read_parquet_schema(str(oracle)) if c not in KEYS]
    assert_parquet_parity(
        py,
        oracle,
        keys=KEYS,
        sample_cols=sample,
        r_only_all_null_ok=("media_id",),
        # pbp column order is payload-first-seen; the raw repo has been
        # re-scraped since the oracle was compiled (the released 2025 and
        # 2026 assets already disagree on order), so order is not asserted.
        require_order=False,
    )
