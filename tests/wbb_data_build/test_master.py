"""Schedule master, the single games_in_data_repo manifest, and coverage."""

from __future__ import annotations

import polars as pl
import pytest
from wbb_data_build.master import (
    GAME_LEVEL,
    LEGACY_FLAGS,
    build_coverage,
    build_master,
    games_in_data_repo,
    normalize_flags,
)


def _season(season: int, n: int, with_pbp: int) -> pl.DataFrame:
    return pl.DataFrame(
        {
            "game_id": [900000 + season * 100 + i for i in range(n)],
            "season": [season] * n,
            "season_type": [2] * n,
            "date": ["2025-11-0%d" % (i % 9 + 1) for i in range(n)],
            "PBP": [i < with_pbp for i in range(n)],
            "team_box": [i < with_pbp for i in range(n)],
            "player_box": [i < with_pbp for i in range(n)],
        },
        schema_overrides={"game_id": pl.Int32},
    )


def test_legacy_published_names_are_mapped_not_renamed():
    """wehoop's load_wbb_schedule() reads PBP/team_box/player_box, so the season
    file's columns must survive; the master adds normalized aliases."""
    out = normalize_flags(_season(2026, 2, 1))
    for legacy, normalized in LEGACY_FLAGS.items():
        assert legacy in out.columns
        assert normalized in out.columns
    assert out["in_pbp"].to_list() == out["PBP"].to_list()


def test_every_game_level_dataset_gets_a_flag():
    out = normalize_flags(_season(2026, 2, 1))
    for dataset in GAME_LEVEL:
        assert f"in_{dataset}" in out.columns


def test_a_dataset_absent_this_season_is_false_not_missing():
    out = normalize_flags(_season(2026, 2, 1))
    assert out["in_shots"].to_list() == [False, False]
    assert out["in_shots"].null_count() == 0


def test_master_is_the_union_of_seasons():
    master = build_master([_season(2025, 4, 2), _season(2026, 6, 6)])
    assert master.height == 10
    assert set(master["season"].unique().to_list()) == {2025, 2026}


def test_master_canonicalizes_ids_to_int64():
    assert build_master([_season(2026, 2, 2)]).schema["game_id"] == pl.Int64


def test_master_pins_column_order_across_ragged_seasons():
    a = _season(2025, 2, 1)
    b = _season(2026, 2, 2).with_columns(pl.lit(1200).alias("venue_capacity"))
    assert build_master([a, b]).columns == build_master([b, a]).columns
    assert build_master([a, b])["venue_capacity"].null_count() == 2


def test_build_master_refuses_empty_input():
    with pytest.raises(ValueError, match="at least one"):
        build_master([])


def test_manifest_keeps_only_games_in_a_compilation():
    master = build_master([_season(2026, 4, 2)])
    manifest = games_in_data_repo(master)
    assert manifest.height == 2
    assert manifest.columns == master.columns


def test_manifest_is_empty_when_nothing_is_built():
    assert games_in_data_repo(build_master([_season(2026, 3, 0)])).height == 0


def test_coverage_is_one_row_per_season_and_type():
    coverage = build_coverage(build_master([_season(2025, 4, 2), _season(2026, 6, 6)]))
    assert coverage.height == 2
    row = coverage.filter(pl.col("season") == 2025).to_dicts()[0]
    assert row["n_games"] == 4
    assert row["pct_in_pbp"] == pytest.approx(0.5)


def test_coverage_has_a_pct_column_per_flag():
    coverage = build_coverage(build_master([_season(2026, 2, 1)]))
    for dataset in GAME_LEVEL:
        assert f"pct_in_{dataset}" in coverage.columns
