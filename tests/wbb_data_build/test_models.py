"""Typed schema declarations for the released datasets.

The models declare the schema, not the rows: they are asserted frame-level
against a built frame, never row-by-row (pydantic over a multi-million-row pbp
frame is a performance trap).
"""

from __future__ import annotations

import glob
from pathlib import Path

import polars as pl
import pytest
from wbb_data_build.config import REGISTRY
from wbb_data_build.ids import is_id_column
from wbb_data_build.models import MODELS, check_frame, polars_schema

REPO_ROOT = Path(__file__).resolve().parents[2]

# Datasets with no Python model. schedule/player_crosswalk are still R-built.
# team_crosswalk IS Python-built but is deliberately model-less: its id columns
# are the PUBLISHED contract (espn_team_id Int32, fox_team_id/yahoo_team_id
# String), so declaring one would either lie about the dtypes or force the
# Int64 invariant below onto an asset that never had it.
NO_MODEL = {"team_crosswalk", "schedule_crosswalk", "player_crosswalk"}


def test_every_modelled_dataset_is_in_the_registry():
    assert set(MODELS) == set(REGISTRY) - NO_MODEL


@pytest.mark.parametrize("dataset", sorted(MODELS), ids=sorted(MODELS))
def test_polars_schema_is_derivable(dataset):
    assert len(polars_schema(dataset)) > 0


@pytest.mark.parametrize("dataset", sorted(MODELS), ids=sorted(MODELS))
def test_every_id_column_is_declared_int64(dataset):
    """Ids are join keys. The released assets shipped the same id as Int32,
    Int64 and String across datasets, which made them unjoinable."""
    schema = polars_schema(dataset)
    wrong = {c: str(t) for c, t in schema.items() if is_id_column(c) and t != pl.Int64}
    assert wrong == {}, f"{dataset}: id columns not declared Int64: {wrong}"


def test_model_rejects_type_coercion():
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        MODELS["pbp"](game_id="401811123")  # str where an Int64 id is declared


def test_check_frame_accepts_a_matching_frame():
    schema = polars_schema("officials")
    frame = pl.DataFrame(schema=schema)
    assert check_frame("officials", frame) == []


def test_check_frame_reports_a_missing_column():
    frame = pl.DataFrame({"game_id": [1]}, schema={"game_id": pl.Int64})
    problems = check_frame("officials", frame)
    assert any("missing column" in p for p in problems)


def test_check_frame_tolerates_widening_but_not_narrowing():
    """An Int32 id read back from an older asset is losslessly an Int64; a
    String one is not."""
    ok = pl.DataFrame(schema={**polars_schema("officials"), "game_id": pl.Int32})
    assert [p for p in check_frame("officials", ok) if "game_id" in p] == []
    bad = pl.DataFrame(schema={**polars_schema("officials"), "game_id": pl.Utf8})
    assert any("game_id" in p for p in check_frame("officials", bad))


@pytest.mark.archive
@pytest.mark.parametrize("dataset", sorted(MODELS), ids=sorted(MODELS))
def test_model_matches_the_built_parquet(dataset):
    """The declared schema must describe what the pipeline actually writes."""
    spec = REGISTRY[dataset]
    built = sorted(
        glob.glob(str(REPO_ROOT / "wbb" / dataset / "parquet" / f"{spec.stem}_*.parquet"))
    )
    if not built:
        pytest.skip(f"no built parquet for {dataset}")
    frame = pl.read_parquet(built[-1], n_rows=1)
    problems = [p for p in check_frame(dataset, frame) if "missing column" in p]
    assert problems == [], "\n".join(problems)
