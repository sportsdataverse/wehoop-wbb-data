"""The numbered builder entrypoints, one per Python-built dataset.

Numbers are build order, not registry order: shots project the built pbp
parquet, and schedules stamp flags from the built pbp/team_box/player_box
parquets, so those have to exist first.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest
from wbb_data_build.config import REGISTRY

PY_DIR = Path(__file__).resolve().parents[1] / "python"

# dataset -> its number. Dependency order, which is what the daily processor runs.
NUMBERED = {
    "pbp": 1,
    "team_box": 2,
    "player_box": 3,
    "player_core": 4,
    "schedules": 5,
    "shots": 6,
    "rosters": 7,
    "player_season_stats": 8,
    "team_season_stats": 9,
    "standings": 10,
    "game_rosters": 11,
    "officials": 12,
    "team_crosswalk": 13,
}

# Still R-only: the schedule and player crosswalks need ESPN scoreboard and
# roster coverage sdv-py does not yet have. They keep numbers 14/15 on the R
# side.
R_ONLY = {"schedule_crosswalk": 14, "player_crosswalk": 15}


def _path(dataset: str) -> Path:
    return PY_DIR / f"espn_wbb_{NUMBERED[dataset]:02d}_{dataset}_creation.py"


def test_every_python_built_dataset_has_a_script():
    missing = [d for d in sorted(NUMBERED) if not _path(d).exists()]
    assert missing == []


def test_the_numbering_covers_the_registry_exactly():
    """A registry entry with no script and no R owner is a dataset nobody can
    run directly."""
    assert set(NUMBERED) | set(R_ONLY) == set(REGISTRY)


def test_numbers_are_unique_and_contiguous():
    assert sorted(NUMBERED.values()) == list(range(1, len(NUMBERED) + 1))


def test_the_all_builder_exists():
    assert (PY_DIR / "espn_wbb_00_all_creation.py").exists()


@pytest.mark.parametrize("dataset", sorted(NUMBERED), ids=sorted(NUMBERED))
def test_script_declares_its_dataset(dataset):
    path = _path(dataset)
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[path.stem] = module
    try:
        spec.loader.exec_module(module)
    finally:
        sys.modules.pop(path.stem, None)
    assert module.DATASET == dataset


@pytest.mark.parametrize("dataset", sorted(NUMBERED), ids=sorted(NUMBERED))
def test_script_help_exits_zero(dataset):
    proc = subprocess.run(
        [sys.executable, str(_path(dataset)), "--help"],
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert proc.returncode == 0, proc.stderr
    assert "--start" in proc.stdout


def test_all_builder_runs_datasets_in_dependency_order():
    """pbp before shots (shots read the built pbp parquet) and before schedules
    (schedules stamp flags from the built parquets)."""
    path = PY_DIR / "espn_wbb_00_all_creation.py"
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[path.stem] = module
    try:
        spec.loader.exec_module(module)
    finally:
        sys.modules.pop(path.stem, None)
    order = list(module.ORDER)
    assert set(order) == set(NUMBERED)
    assert order.index("pbp") < order.index("shots")
    assert order.index("pbp") < order.index("schedules")
    assert order.index("team_box") < order.index("schedules")
    assert order.index("player_box") < order.index("schedules")
