"""Dataset registry -- one row per released WBB dataset.

Mirrors each ``espn_wbb_NN_*_creation.R`` script: ``(dataset, stem, tag,
reshaper)`` where ``reshaper`` keys into ``wbb_data_build.reshapers.RESHAPERS``.
Tags are verbatim from ``wehoop::load_wbb_*`` URL builders -- do not rename.
"""

from __future__ import annotations

from dataclasses import dataclass

RAW_ROOT_ENV = "WEHOOP_WBB_RAW_ROOT"  # sibling wehoop-wbb-raw checkout root
_T = "espn_womens_college_basketball_"

# --- rds contract -------------------------------------------------------------
# wehoop::load_wbb_* reads .rds EXCLUSIVELY -- the rds is the R package's entire
# read path, not a courtesy format. Python writes it natively via
# sportsdataverse._rds.write_rds (byte-validated against R's saveRDS); there is
# no R serialize step. Reproduces wehoop:::make_wehoop_data() +
# sportsdataverse_save() in the published attribute order. The class is
# load-bearing -- wehoop registers print.wehoop_data on it.
RDS_CLASS: tuple[str, ...] = ("wehoop_data", "tbl_df", "tbl", "data.table", "data.frame")
RDS_ATTR_PREFIX = "wehoop"
RDS_TYPE_TEMPLATE = "ESPN WBB {dataset} from wehoop data repository"


@dataclass(frozen=True)
class DatasetSpec:
    """How to build one released dataset.

    Attributes:
        dataset: directory name under ``wbb/`` and the manifest key.
        stem: output file stem (``{stem}_{season}.parquet`` / ``.csv``).
        tag: the ``sportsdataverse-data`` release tag (load-bearing).
        reshaper: key into ``reshapers.RESHAPERS``.
        out_dir: directory under ``wbb/`` when it is NOT the dataset name.
            The three crosswalks share one ``wbb/crosswalk/`` dir (their R
            scripts hard-code it); the manifest FILE name still carries the
            dataset (``wbb_team_crosswalk_in_data_repo.csv``).
        write_tree_csv: whether a local csv copy is committed at all. The
            three crosswalks write none -- the ``wbb/crosswalk/*.csv`` files
            are the MANIFESTS, not a tree copy of the data -- but the release
            asset csv is still built from the parquet at publish time
            (R ``file_types = c("rds", "csv", "parquet")``).
        manifest_endpoint: ``source_endpoint`` value for the manifest row, or
            None for the datasets whose manifest carries no such column. The
            crosswalk manifests are the only ones R writes it into, and the
            column is part of their published asset.
        publish_manifest: upload the manifest csv to the release tag. Only the
            crosswalks do (R ``upload_wbb_manifest`` runs in their scripts and
            nowhere else in the Python-built set).
        canonicalize: run ``ids.canonicalize_ids`` before writing. False for
            the crosswalks: their id dtypes ARE the published contract
            (``espn_athlete_id``/``espn_game_id``/``fox_team_id`` ship as
            String in every released crosswalk asset), and widening them to
            Int64 would silently break every downstream join against them.
        rds_type: ``wehoop_type`` attribute override. Defaults to
            ``RDS_TYPE_TEMPLATE``; the crosswalks carry the bespoke string
            ``wehoop::wbb_*_crosswalk()`` stamps on the frame (verified
            against the committed ``wbb/crosswalk/rds/*.rds``).
        sdv_type: ``sportsdataverse_type`` attribute override. Defaults to
            ``"{dataset} data"``; R passes the spaced form for crosswalks.
    """

    dataset: str
    stem: str
    tag: str
    reshaper: str
    out_dir: str | None = None
    write_tree_csv: bool = True
    manifest_endpoint: str | None = None
    publish_manifest: bool = False
    canonicalize: bool = True
    rds_type: str | None = None
    sdv_type: str | None = None


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
    # Athlete identity + bio. NEW dataset -- no R creation script exists, and
    # nothing published this before: the player_season_stats payload carries no
    # identity at all (not even the athlete id -- only the filename does).
    # NB: unlike this league's player_season_stats, the raw tree is FLAT (no
    # {season} segment) -- a core record is per-athlete and the core-v2 athlete
    # resource takes no season param. "Who played in season Y" comes from the
    # built player_box.
    "player_core": DatasetSpec(
        "player_core",
        "player_core",
        _T + "player_core",
        "player_core",
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
    # They also share one output dir (wbb/crosswalk/), write no tree csv (the
    # wbb/crosswalk/*.csv files are the MANIFESTS), publish that manifest as a
    # release asset, and carry a bespoke wehoop_type -- all verbatim from
    # R/wbb_1{3,4,5}_*_crosswalk_creation.R.
    #
    # Only team_crosswalk is Python-built. schedule_crosswalk and
    # player_crosswalk stay on R and therefore carry no build metadata here:
    # against the committed 2026 R goldens the live Python builders fail the
    # parity gate outright -- schedule matches 1,037 ESPN games where R matched
    # 6,054 (match_method `both` 991 vs 5,562), and player returns 0 rows with
    # every column null against R's 5,018. Both are sdv-py source-layer gaps
    # (ESPN scoreboard coverage / off-season ESPN rosters), not wiring, so
    # flipping them would publish a gutted asset.
    "team_crosswalk": DatasetSpec(
        "team_crosswalk",
        "wbb_team_crosswalk",
        "wbb_crosswalk",
        "team_crosswalk",
        out_dir="crosswalk",
        write_tree_csv=False,
        manifest_endpoint="wehoop::wbb_team_crosswalk()",
        publish_manifest=True,
        canonicalize=False,
        rds_type="WBB team crosswalk (ESPN / Fox / Torvik)",
        sdv_type="team crosswalk data",
    ),
    "schedule_crosswalk": DatasetSpec(
        "schedule_crosswalk", "wbb_schedule_crosswalk", "wbb_crosswalk", "schedule_crosswalk"
    ),
    "player_crosswalk": DatasetSpec(
        "player_crosswalk", "wbb_player_crosswalk", "wbb_crosswalk", "player_crosswalk"
    ),
}
