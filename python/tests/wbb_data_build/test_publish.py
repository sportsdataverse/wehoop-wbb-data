import polars as pl

from wbb_data_build.config import REGISTRY
from wbb_data_build import io, publish


def test_publish_uploads_each_file_with_clobber(tmp_path):
    spec = REGISTRY["team_box"]
    io.write_dataset(pl.DataFrame({"game_id": [1]}), spec, 2025, base=tmp_path)
    calls = []
    res = publish.publish_dataset(
        spec,
        2025,
        base=tmp_path,
        runner=lambda args: calls.append(args),
        exists_check=lambda tag, repo: True,  # release already exists
    )
    uploads = [c for c in calls if c[:2] == ["release", "upload"]]
    assert len(uploads) == 2  # parquet + csv
    assert all("--clobber" in c for c in uploads)
    assert res["tag"] == spec.tag


def test_publish_creates_release_when_missing(tmp_path):
    spec = REGISTRY["team_box"]
    io.write_dataset(pl.DataFrame({"game_id": [1]}), spec, 2025, base=tmp_path)
    calls = []
    publish.publish_dataset(
        spec,
        2025,
        base=tmp_path,
        runner=lambda args: calls.append(args),
        exists_check=lambda tag, repo: False,
    )
    assert any(c[:2] == ["release", "create"] for c in calls)
