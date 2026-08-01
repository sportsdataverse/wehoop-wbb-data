"""Generated dataset documentation.

The interesting logic is the description lookup. The shared sdv-py store is
keyed by schema, and flattening it by column name pulls other sports' text: it
gave `season` a CFB simulation blurb and `game_id` an nflverse id example
("2023_06_DET_TB"). A borrowed description is an invented one, so anything
naming another sport is rejected and the cell is left empty.
"""

from __future__ import annotations

import pytest
from wbb_data_build.config import REGISTRY
from wbb_data_build.docs import (
    BUILDER,
    _is_foreign,
    column_table,
    dataset_page,
    summary_table,
)


@pytest.mark.parametrize(
    "text",
    [
        "Game identifier from the schedule (nflverse id, e.g. 2023_06_DET_TB).",
        "consumed as the sim/season identifier by cfb_standings and cfb_simulations",
        "The NHL team abbreviation.",
        "Men's college basketball team id.",
    ],
)
def test_foreign_descriptions_are_rejected(text):
    assert _is_foreign(text) is True


@pytest.mark.parametrize(
    "text",
    [
        "Game identifier carried through from the input schedule.",
        "Unique identifier for the athlete.",
        "Number of points scored.",
    ],
)
def test_sport_agnostic_descriptions_are_kept(text):
    assert _is_foreign(text) is False


def test_every_dataset_has_a_builder_entry():
    """A dataset with no builder would render a broken link."""
    assert set(BUILDER) == set(REGISTRY)


@pytest.mark.parametrize("dataset", sorted(REGISTRY), ids=sorted(REGISTRY))
def test_dataset_page_renders(dataset):
    page = dataset_page(dataset, live=False)
    assert page.startswith(f"# `{dataset}`")
    assert REGISTRY[dataset].tag in page
    assert BUILDER[dataset] in page


@pytest.mark.parametrize("dataset", sorted(REGISTRY), ids=sorted(REGISTRY))
def test_column_table_is_a_markdown_table_or_an_honest_note(dataset):
    table = column_table(dataset)
    assert "| col_name | type | description |" in table or "R-only" in table


def test_summary_table_links_every_dataset():
    block = summary_table(live=False)
    for dataset in REGISTRY:
        assert f"docs/datasets/{dataset}.md" in block


def test_no_page_claims_a_description_it_does_not_have():
    """An empty cell is the designed outcome for an undescribed column."""
    table = column_table("officials")
    assert "|  |" in table or "| |" in table
