"""Generated dataset documentation.

The interesting logic is the description lookup. The shared sdv-py store is
Descriptions are authored for this league and ship with the package. They used
to be borrowed from sdv-py's schema-keyed store by flattening it on column
name, which produced `assists` = "Assisted tackles" (NFL), `half` =
"Half-inning" (baseball) and `team_id` = a 247Sports recruiting key. A borrowed
description is an invented one.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from wbb_data_build.config import REGISTRY
from wbb_data_build.docs import (
    BUILDER,
    _descriptions,
    column_table,
    dataset_page,
    summary_table,
)
from wbb_data_build.models import MODELS, polars_schema


def test_every_column_in_every_dataset_is_described():
    """100% coverage is the gate. A new column without a description is a doc
    page with a blank cell, which is exactly the rot this generator exists to
    prevent."""
    descriptions = _descriptions()
    missing = sorted({c for ds in MODELS for c in polars_schema(ds) if not descriptions.get(c)})
    assert missing == [], f"columns with no description: {missing}"


# Text that would betray a description borrowed from another sport. The store
# used to be built by flattening sdv-py's schema-keyed file on column name,
# which produced `assists` = "Assisted tackles" (NFL), `half` = "Half-inning"
# (baseball) and `team_id` = a 247Sports recruiting key. Descriptions are now
# authored for this league; this is the regression guard.
_FOREIGN_MARKERS = (
    "tackle",
    "half-inning",
    "inning",
    "247sports",
    "quarterback",
    "nflverse",
    "transfer player",
    "recruit",
    "puck",
    "goalie",
    "pitcher",
    "batter",
    "touchdown",
    "yardage",
    "on3",
)


@pytest.mark.parametrize("dataset", sorted(MODELS), ids=sorted(MODELS))
def test_no_description_is_borrowed_from_another_sport(dataset):
    descriptions = _descriptions()
    offenders = {
        column: text
        for column in polars_schema(dataset)
        if (text := descriptions.get(column))
        and any(marker in text.lower() for marker in _FOREIGN_MARKERS)
    }
    assert offenders == {}, f"{dataset}: descriptions from another sport: {offenders}"


def test_the_store_ships_with_the_package():
    """CI has no sibling sdv-py checkout. Reading the store from one made every
    doc page render blank there, which failed the drift gate on every PR."""
    from wbb_data_build import docs as docs_mod

    store = Path(docs_mod.__file__).with_name("column_descriptions.yaml")
    assert store.exists()


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



def test_no_rendered_cell_is_blank():
    """Coverage is 100%, so a blank cell means a column slipped the store."""
    table = column_table("officials")
    body = [r for r in table.splitlines() if r.startswith("| `")]
    assert body
    assert all(not r.rstrip().endswith("|  |") for r in body), table
