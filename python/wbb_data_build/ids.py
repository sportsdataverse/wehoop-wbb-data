"""Id canonicalization: every id column is Int32, cast losslessly or refused.

Ids are join keys, and a join is only as correct as the dtype agreement on
both sides. Before this module, the SAME id shipped with three different dtypes
across this repo's own datasets:

===============  ==================================================
``game_id``      Int32 (pbp, shots, team_box, player_box, schedules)
                 **String** (game_rosters, officials)
``athlete_id``   Int32 (player_box, player_season_stats, game_rosters)
                 Int64 (player_core), **String** (rosters)
===============  ==================================================

So ``player_box.join(rosters, on="athlete_id")`` and
``player_box.join(officials, on="game_id")`` both raise ``SchemaError`` on the
released data. This mirrors the CFB ``team_id`` canonicalization in sdv-py,
which fixes the same class at the loader boundary.

Refusing a lossy cast matters more than performing one: a truncated or
float-rounded id yields a structurally valid frame that joins to the WRONG row,
which is strictly worse than an exception.

**The target is Int32, which is the width the datasets already ship.** This
module targeted Int64 between 2026-08-01 and 2026-09-09, on the reasoning that
widening is always lossless. It is, but it was solving the wrong half of the
problem: the defect above is ids disagreeing with EACH OTHER, and any single
width fixes that. Int64 additionally put Python at odds with two things it did
not need to fight —

* the retained R chain, which writes R ``integer`` (Int32) and cannot write
  Int64 without ``bit64``; the weekly R/Python parity job reports that as a
  join-key dtype disagreement, and it is one.
* every already-published asset, all of which are Int32.

so the next publish would have silently rewritten the width of every id column
on the releases. Int32 agrees with R, with what shipped, and with itself.

Narrowing is only safe because it is CHECKED: an out-of-int32 value raises
rather than wrapping. Measured against full history in sdv-db (2004-, all
seasons), the widest wbb ids are game_id 401,865,139, athlete_id 5,343,112 and
team_id 131,833 — an order of magnitude inside the 2,147,483,647 ceiling. The
check is what makes that a fact rather than an assumption.

Postgres does not adjudicate this: the ingest widens every integer to
``bigint`` regardless of source width (the ``wbb`` schema holds 2,875 bigint
columns and zero ``integer`` ones, and the ``wnba`` schema — whose source is
Int32 — is bigint too), so both choices land identically in the database.
"""

from __future__ import annotations

import polars as pl

#: Narrower integer dtypes, widened to Int32 without a range check.
_WIDENABLE = (pl.Int8, pl.Int16, pl.UInt8, pl.UInt16)
#: Wider integer dtypes, narrowed to Int32 ONLY after a range check.
_NARROWABLE = (pl.Int64, pl.UInt32, pl.UInt64)

_INT32_MIN = -2_147_483_648
_INT32_MAX = 2_147_483_647

#: Suffix that marks a column as an id. ``id`` itself is matched exactly.
ID_SUFFIX = "_id"


def is_id_column(name: str) -> bool:
    """True for ``id`` and anything ending ``_id``."""
    return name == "id" or name.endswith(ID_SUFFIX)


def _check_range(series: pl.Series) -> None:
    """Raise if any value falls outside the Int32 range.

    Narrowing without this wraps silently, which is the failure mode this whole
    module exists to prevent — a wrapped id is a valid-looking number that joins
    to the wrong row.
    """
    non_null = series.drop_nulls()
    if non_null.is_empty():
        return
    if int(non_null.min()) < _INT32_MIN or int(non_null.max()) > _INT32_MAX:
        raise ValueError(f"id value outside Int32 range in {series.name!r}")


def to_int32(series: pl.Series) -> pl.Series:
    """Canonicalize an id series to Int32, refusing any lossy conversion.

    Raises:
        ValueError: If a value falls outside the Int32 range, a float carries a
            fractional part, a string is not numeric, or the dtype is not
            id-shaped.
    """
    dtype = series.dtype
    if dtype == pl.Int32:
        return series
    if dtype in _WIDENABLE:
        return series.cast(pl.Int32)
    if dtype in _NARROWABLE:
        _check_range(series)
        return series.cast(pl.Int32)
    if dtype in (pl.Float32, pl.Float64):
        nonnull = series.drop_nulls()
        if len(nonnull) and (nonnull != nonnull.round(0)).any():
            raise ValueError(f"lossy float->Int32 id cast on {series.name!r}")
        _check_range(series)
        return series.cast(pl.Int32)
    if dtype == pl.Utf8:
        # Via Int64 so an out-of-range string is caught by _check_range and
        # reported as such, rather than becoming a null and reading as
        # "non-numeric".
        out = series.cast(pl.Int64, strict=False)
        if out.null_count() > series.null_count():
            raise ValueError(f"non-numeric id value in {series.name!r}")
        _check_range(out)
        return out.cast(pl.Int32)
    raise ValueError(f"unsupported id dtype {dtype} on {series.name!r}")


def canonicalize_ids(df: pl.DataFrame, *, strict: bool = False) -> pl.DataFrame:
    """Cast every id-shaped column in ``df`` to Int32.

    Args:
        df: Any built dataset frame.
        strict: Re-raise when a column cannot be cast. Default False leaves a
            non-numeric id (e.g. an ESPN slug in an ``*_id`` field) untouched
            rather than failing a whole season's build over one column.

    Returns:
        The frame with id columns cast to Int32.
    """
    casts = []
    for name in df.columns:
        if not is_id_column(name) or df.schema[name] == pl.Int32:
            continue
        try:
            casts.append(to_int32(df[name]).alias(name))
        except ValueError:
            if strict:
                raise
    return df.with_columns(casts) if casts else df
