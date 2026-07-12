"""Parity assertions: Python-built frame vs the R-released parquet (the oracle).

The oracle fixture is PRE-FILTERED to the captured game-ids (see Task 7 capture),
so `py` and `r` cover the same games and row counts are directly comparable.
"""

from __future__ import annotations

from pathlib import Path

import polars as pl


def assert_parquet_parity(
    py: pl.DataFrame, r_parquet: Path, *, keys: list[str], sample_cols: list[str]
) -> None:
    r = pl.read_parquet(r_parquet)
    assert set(py.columns) == set(r.columns), (
        f"column set diverges: only-py={set(py.columns) - set(r.columns)}, "
        f"only-r={set(r.columns) - set(py.columns)}"
    )
    for c in keys + sample_cols:
        assert py.schema[c] == r.schema[c], (
            f"dtype mismatch on {c}: py={py.schema[c]} r={r.schema[c]}"
        )
    assert py.height == r.height, f"row count: py={py.height} r={r.height}"
    cols = keys + sample_cols
    pys = py.sort(keys).select(cols)
    rs = r.sort(keys).select(cols)
    assert pys.equals(rs), "value mismatch on keys+sample cols after sort"
