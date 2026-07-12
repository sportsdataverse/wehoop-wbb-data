"""Dataset registry -- one row per released WBB dataset.

Mirrors each ``espn_wbb_NN_*_creation.R`` script: ``(dataset, stem, tag,
reshaper)`` where ``reshaper`` keys into ``wbb_data_build.reshapers.RESHAPERS``.
Tags are verbatim from ``wehoop::load_wbb_*`` URL builders -- do not rename.
"""

from __future__ import annotations

from dataclasses import dataclass

RAW_ROOT_ENV = "WEHOOP_WBB_RAW_ROOT"  # sibling wehoop-wbb-raw checkout root
_T = "espn_womens_college_basketball_"


@dataclass(frozen=True)
class DatasetSpec:
    """How to build one released dataset.

    Attributes:
        dataset: directory name under ``wbb/`` and the manifest key.
        stem: output file stem (``{stem}_{season}.parquet`` / ``.csv``).
        tag: the ``sportsdataverse-data`` release tag (load-bearing).
        reshaper: key into ``reshapers.RESHAPERS``.
    """

    dataset: str
    stem: str
    tag: str
    reshaper: str


REGISTRY: dict[str, DatasetSpec] = {
    "pbp": DatasetSpec("pbp", "play_by_play", _T + "pbp", "pbp"),
    "schedules": DatasetSpec("schedules", "wbb_schedule", _T + "schedules", "schedules"),
    "shots": DatasetSpec("shots", "shots", _T + "shots", "shots"),
    "team_box": DatasetSpec("team_box", "team_box", _T + "team_boxscores", "team_box"),
    "player_box": DatasetSpec("player_box", "player_box", _T + "player_boxscores", "player_box"),
    "rosters": DatasetSpec("rosters", "rosters", _T + "rosters", "rosters"),
    "player_season_stats": DatasetSpec(
        "player_season_stats",
        "player_season_stats",
        _T + "player_season_stats",
        "player_season_stats",
    ),
    "team_season_stats": DatasetSpec(
        "team_season_stats", "team_season_stats", _T + "team_season_stats", "team_season_stats"
    ),
    "standings": DatasetSpec("standings", "standings", _T + "standings", "standings"),
    "game_rosters": DatasetSpec(
        "game_rosters", "game_rosters", _T + "game_rosters", "game_rosters"
    ),
    "officials": DatasetSpec("officials", "officials", _T + "officials", "officials"),
    # crosswalks -- tag/stem confirmed via Step 0 discovery grep against
    # R/wbb_1{1,2,3}_*_creation.R: all three publish to the SAME shared
    # release tag "wbb_crosswalk" (not the per-dataset espn_womens_college_
    # basketball_* prefix used by the per-game datasets above); stems match
    # each script's `file_name = glue::glue("wbb_{...}_crosswalk_{y}")`.
    "team_crosswalk": DatasetSpec(
        "team_crosswalk", "wbb_team_crosswalk", "wbb_crosswalk", "team_crosswalk"
    ),
    "schedule_crosswalk": DatasetSpec(
        "schedule_crosswalk", "wbb_schedule_crosswalk", "wbb_crosswalk", "schedule_crosswalk"
    ),
    "player_crosswalk": DatasetSpec(
        "player_crosswalk", "wbb_player_crosswalk", "wbb_crosswalk", "player_crosswalk"
    ),
}
