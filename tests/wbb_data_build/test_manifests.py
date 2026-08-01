"""Build manifests carry one row per season.

They did not. The R creation scripts wrote them with
`data.table::fwrite(..., append = TRUE)` -- a blind append with no dedupe -- so
the weekly roster refresh left 12 rows for season 2026 alone. Anything counting
rows was counting RUNS, which is how the generated docs came to claim
"2026-2026 (12 seasons)".
"""

from __future__ import annotations

import re
from pathlib import Path

import polars as pl
import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFESTS = sorted(REPO_ROOT.glob("wbb/*/wbb_*_in_data_repo.csv"))


@pytest.mark.archive
@pytest.mark.parametrize("path", MANIFESTS, ids=lambda p: p.stem)
def test_one_row_per_season(path):
    frame = pl.read_csv(path)
    if "season" not in frame.columns:
        pytest.skip(f"{path.name} has no season column")
    duplicated = frame.group_by("season").len().filter(pl.col("len") > 1).sort("season").to_dicts()
    assert duplicated == [], f"{path.name}: seasons with multiple rows: {duplicated}"


@pytest.mark.archive
@pytest.mark.parametrize("path", MANIFESTS, ids=lambda p: p.stem)
def test_seasons_are_sorted(path):
    frame = pl.read_csv(path)
    if "season" not in frame.columns:
        pytest.skip(f"{path.name} has no season column")
    seasons = frame["season"].to_list()
    assert seasons == sorted(seasons), f"{path.name}: seasons out of order"


@pytest.mark.archive
def test_at_least_one_manifest_exists():
    """If the glob silently matched nothing the tests above would all pass."""
    assert MANIFESTS


def test_no_r_script_appends_to_a_manifest():
    """The writers must upsert. A blind append is what produced the duplicates,
    and it would reintroduce them the next time a season is rebuilt.

    Scoped to fwrite calls that target a manifest path, so an unrelated
    `append = TRUE` elsewhere in a script is not a false positive.
    """
    pattern = re.compile(
        r"fwrite\((?:[^()]|\([^()]*\))*manifest(?:[^()]|\([^()]*\))*append\s*=\s*TRUE",
        re.S | re.I,
    )
    offenders = [
        p.name
        for p in sorted((REPO_ROOT / "R").glob("*.R"))
        if pattern.search(p.read_text(encoding="utf-8"))
    ]
    assert offenders == [], f"R scripts still appending to a manifest: {offenders}"


def test_every_manifest_writer_uses_the_shared_helper():
    """Ten copies of the upsert is how the scope bug happened: four of them
    referenced `y` while sitting inside a function whose argument was
    `season`."""
    writers = [
        p
        for p in sorted((REPO_ROOT / "R").glob("*.R"))
        if "manifest_path" in p.read_text(encoding="utf-8")
        or "shots_manifest_path" in p.read_text(encoding="utf-8")
    ]
    assert writers, "no manifest-writing R scripts found"
    missing = [
        p.name
        for p in writers
        if "upsert_manifest_row(" not in p.read_text(encoding="utf-8")
        and p.name != "manifest_upload_helper.R"
    ]
    assert missing == [], f"manifest writers not using the helper: {missing}"
