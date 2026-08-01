import polars as pl
from wbb_data_build import io
from wbb_data_build.config import REGISTRY


def test_write_dataset_emits_parquet_csv_and_manifest(tmp_path):
    df = pl.DataFrame({"game_id": [1, 2], "score": [70, 65]})
    spec = REGISTRY["team_box"]
    paths = io.write_dataset(df, spec, 2025, base=tmp_path)
    names = sorted(p.name for p in paths)
    assert names == ["team_box_2025.csv", "team_box_2025.parquet", "team_box_2025.rds"]
    assert (tmp_path / "team_box" / "parquet" / "team_box_2025.parquet").exists()
    assert (tmp_path / "team_box" / "csv" / "team_box_2025.csv").exists()
    manifest = tmp_path / "team_box" / "wbb_team_box_in_data_repo.csv"
    assert manifest.exists()
    m = pl.read_csv(manifest)
    assert m["season"].to_list() == [2025] and m["row_count"].to_list() == [2]


def test_manifest_upsert_replaces_same_season(tmp_path):
    spec = REGISTRY["team_box"]
    io.write_dataset(pl.DataFrame({"game_id": [1]}), spec, 2025, base=tmp_path)
    io.write_dataset(pl.DataFrame({"game_id": [1, 2, 3]}), spec, 2025, base=tmp_path)
    m = pl.read_csv(tmp_path / "team_box" / "wbb_team_box_in_data_repo.csv")
    assert m.height == 1 and m["row_count"].to_list() == [3]
