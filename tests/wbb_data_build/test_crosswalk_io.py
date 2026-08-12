"""The crosswalk output contract, pinned against the committed R goldens.

``wbb/crosswalk/`` is shaped unlike every other dataset dir and every clause
here was read off the committed 2026 assets: one shared dir for all three
crosswalks, no ``csv/`` subdir, a manifest carrying ``source_endpoint``, a
bespoke ``wehoop_type``, and id columns that are NOT canonicalized to Int64.
"""

from pathlib import Path

import polars as pl
import pytest
from wbb_data_build import io, publish
from wbb_data_build.config import REGISTRY

SPEC = REGISTRY["team_crosswalk"]
REPO = Path(__file__).resolve().parents[2]

FRAME = pl.DataFrame(
    {
        "season": pl.Series([2026], dtype=pl.Int32),
        "espn_team_id": pl.Series([2000], dtype=pl.Int32),
        "fox_team_id": pl.Series(["198"], dtype=pl.Utf8),
        "yahoo_team_id": pl.Series([None], dtype=pl.Utf8),
        "match_method": pl.Series(["fox+bart"], dtype=pl.Utf8),
    }
)


def test_writes_into_the_shared_crosswalk_dir_and_commits_no_tree_csv(tmp_path):
    paths = io.write_dataset(FRAME, SPEC, 2026, base=tmp_path)
    assert (tmp_path / "crosswalk" / "parquet" / "wbb_team_crosswalk_2026.parquet").exists()
    assert (tmp_path / "crosswalk" / "rds" / "wbb_team_crosswalk_2026.rds").exists()
    # The crosswalk/*.csv files are the MANIFESTS; a csv/ subdir would be a
    # tree copy R never wrote.
    assert not (tmp_path / "crosswalk" / "csv").exists()
    assert not (tmp_path / SPEC.dataset).exists()
    assert [p.suffix for p in paths] == [".parquet", ".rds"]


def test_ids_are_not_canonicalized(tmp_path):
    """espn_team_id Int32 / fox_team_id String IS the published contract."""
    io.write_dataset(FRAME, SPEC, 2026, base=tmp_path)
    got = pl.read_parquet(tmp_path / "crosswalk" / "parquet" / "wbb_team_crosswalk_2026.parquet")
    assert got.schema["espn_team_id"] == pl.Int32
    assert got.schema["fox_team_id"] == pl.Utf8
    assert got.schema["yahoo_team_id"] == pl.Utf8


def test_manifest_matches_the_committed_golden_shape(tmp_path):
    io.write_dataset(FRAME, SPEC, 2026, base=tmp_path)
    f = io.manifest_path(SPEC, tmp_path)
    assert f == tmp_path / "crosswalk" / "wbb_team_crosswalk_in_data_repo.csv"
    got = pl.read_csv(f)
    golden = pl.read_csv(REPO / "wbb/crosswalk/wbb_team_crosswalk_in_data_repo.csv")
    assert got.columns == golden.columns
    assert got["source_endpoint"].to_list() == ["wehoop::wbb_team_crosswalk()"]


def test_manifest_stays_one_row_per_season_across_reruns(tmp_path):
    for _ in range(3):
        io.write_dataset(FRAME, SPEC, 2026, base=tmp_path)
    assert pl.read_csv(io.manifest_path(SPEC, tmp_path)).height == 1


def test_per_game_manifests_gain_no_source_endpoint_column(tmp_path):
    """Adding the column repo-wide would change 12 published manifest assets."""
    spec = REGISTRY["team_box"]
    io.write_dataset(pl.DataFrame({"game_id": [1]}), spec, 2025, base=tmp_path)
    assert "source_endpoint" not in pl.read_csv(io.manifest_path(spec, tmp_path)).columns


@pytest.mark.parametrize(
    "field,expected",
    [
        ("rds_type", "WBB team crosswalk (ESPN / Fox / Torvik)"),
        ("sdv_type", "team crosswalk data"),
    ],
)
def test_rds_attribute_overrides_match_the_committed_rds(field, expected):
    """Read off wbb/crosswalk/rds/*.rds + R/wbb_13_*.R's sportsdataverse_save."""
    assert getattr(SPEC, field) == expected


def test_publish_ships_parquet_rds_csv_and_the_manifest(tmp_path):
    """R's file_types = c("rds", "csv", "parquet") + upload_wbb_manifest."""
    io.write_dataset(FRAME, SPEC, 2026, base=tmp_path)
    sent: list[list[str]] = []
    out = publish.publish_dataset(
        SPEC,
        2026,
        base=tmp_path,
        runner=sent.append,
        exists_check=lambda tag, repo: True,
    )
    names = sorted(Path(f).name for f in out["files"])
    assert names == [
        "wbb_team_crosswalk_2026.csv",
        "wbb_team_crosswalk_2026.parquet",
        "wbb_team_crosswalk_2026.rds",
        "wbb_team_crosswalk_in_data_repo.csv",
    ]
    assert out["uploaded"] == 4
    assert all(a[:3] == ["release", "upload", "wbb_crosswalk"] for a in sent)
