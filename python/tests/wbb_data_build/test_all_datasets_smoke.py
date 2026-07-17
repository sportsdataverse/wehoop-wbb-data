"""Every implemented dataset builds end-to-end from the fixture raw tree.

Per-game datasets use the 3-game fixture seasons; season-level datasets use
whichever fixture season carries their raw inputs (2025 for the four with
2025 releases, 2026 for the tags that only publish 2026). The three
crosswalks raise NotImplementedError (they build from live ESPN+Torvik+Fox
inputs via the retained R scripts, not from the raw repo).
"""

from pathlib import Path

import pytest

from wbb_data_build.build import build_season
from wbb_data_build.config import REGISTRY

FX = Path(__file__).parent.parent / "fixtures"

_SEASON = {
    "pbp": 2025,
    "schedules": 2025,
    "team_box": 2025,
    "player_box": 2025,
    "shots": 2026,
    "game_rosters": 2026,
    "officials": 2026,
    "rosters": 2026,
    "player_season_stats": 2026,
    # 2025, not 2026 like this league's player_season_stats: player_core is
    # keyed off the built player_box (which athletes played that season), and
    # the player_box fixture season is 2025.
    "player_core": 2025,
    "team_season_stats": 2026,
    "standings": 2026,
}


@pytest.mark.parametrize("dataset", sorted(REGISTRY))
def test_each_dataset_builds(dataset, tmp_path):
    if dataset.endswith("_crosswalk"):
        with pytest.raises(NotImplementedError):
            build_season(dataset, 2026, base=tmp_path, raw_root=FX / "raw")
        return
    season = _SEASON[dataset]
    if dataset == "shots":  # shots read the built pbp parquet
        build_season("pbp", season, base=tmp_path, raw_root=FX / "raw")
    if dataset == "player_core":  # player_core reads the built player_box parquet
        build_season("player_box", season, base=tmp_path, raw_root=FX / "raw")
    df = build_season(dataset, season, base=tmp_path, raw_root=FX / "raw", dry_run=True)
    assert df.height > 0
    spec = REGISTRY[dataset]
    assert (tmp_path / spec.dataset / "parquet" / f"{spec.stem}_{season}.parquet").exists()
    assert (tmp_path / spec.dataset / "csv" / f"{spec.stem}_{season}.csv").exists()
