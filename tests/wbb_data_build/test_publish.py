import subprocess
from pathlib import Path

import polars as pl
import pytest
from wbb_data_build import io, publish
from wbb_data_build.config import REGISTRY

#: release metadata sidecars -- asserted separately, not a data asset
SIDECARS = ("timestamp.", "package_function.")


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
    uploads = [
        c
        for c in calls
        if c[:2] == ["release", "upload"] and not Path(c[3]).name.startswith(SIDECARS)
    ]
    assert len(uploads) == 3  # parquet + rds + csv (rds is the R loader's read path)
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


def test_gh_release_exists_true_on_zero_exit(monkeypatch):
    def fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(args, 0, stdout="", stderr="")

    monkeypatch.setattr(publish.subprocess, "run", fake_run)
    assert publish._gh_release_exists("tag", "repo") is True


def test_gh_release_exists_false_on_genuine_not_found(monkeypatch):
    def fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(args, 1, stdout="", stderr="release not found")

    monkeypatch.setattr(publish.subprocess, "run", fake_run)
    assert publish._gh_release_exists("tag", "repo") is False


def test_gh_release_exists_raises_loudly_on_other_failure(monkeypatch):
    # Regression: a rate-limit / auth / network failure must never be read as
    # "release missing" -- that's the 2026-08-23 incident (fail-open crashed
    # a backfill mid-publish because `gh release create` ran on a live tag).
    def fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(args, 1, stdout="", stderr="API rate limit exceeded")

    monkeypatch.setattr(publish.subprocess, "run", fake_run)
    with pytest.raises(RuntimeError, match="rate limit"):
        publish._gh_release_exists("tag", "repo")


def test_publish_tolerates_create_race(tmp_path):
    # exists() said missing, but the injected runner's create call races
    # against a concurrent creator and gh reports "already exists" -- the
    # publish must continue (log + proceed to upload), not crash.
    spec = REGISTRY["team_box"]
    io.write_dataset(pl.DataFrame({"game_id": [1]}), spec, 2025, base=tmp_path)
    calls = []

    def runner(args):
        calls.append(args)
        if args[:2] == ["release", "create"]:
            raise subprocess.CalledProcessError(1, args, stderr="already exists")

    res = publish.publish_dataset(
        spec,
        2025,
        base=tmp_path,
        runner=runner,
        exists_check=lambda tag, repo: False,
    )
    uploads = [
        c
        for c in calls
        if c[:2] == ["release", "upload"] and not Path(c[3]).name.startswith(SIDECARS)
    ]
    assert len(uploads) == 3
    assert res["uploaded"] == 3
