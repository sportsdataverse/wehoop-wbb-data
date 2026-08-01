"""Id canonicalization: every id column is Int64, cast losslessly or refused.

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
"""

from __future__ import annotations

import polars as pl

_WIDENABLE = (pl.Int8, pl.Int16, pl.Int32, pl.UInt8, pl.UInt16, pl.UInt32)

#: Suffix that marks a column as an id. ``id`` itself is matched exactly.
ID_SUFFIX = "_id"


def is_id_column(name: str) -> bool:
    """True for ``id`` and anything ending ``_id``."""
    return name == "id" or name.endswith(ID_SUFFIX)


def to_int64(series: pl.Series) -> pl.Series:
    """Canonicalize an id series to Int64, refusing any lossy conversion.

    Raises:
        ValueError: If a float carries a fractional part, a string is not
            numeric, or the dtype is not id-shaped.
    """
    dtype = series.dtype
    if dtype == pl.Int64:
        return series
    if dtype in _WIDENABLE:
        return series.cast(pl.Int64)
    if dtype in (pl.Float32, pl.Float64):
        nonnull = series.drop_nulls()
        if len(nonnull) and (nonnull != nonnull.round(0)).any():
            raise ValueError(f"lossy float->Int64 id cast on {series.name!r}")
        return series.cast(pl.Int64)
    if dtype == pl.Utf8:
        out = series.cast(pl.Int64, strict=False)
        if out.null_count() > series.null_count():
            raise ValueError(f"non-numeric id value in {series.name!r}")
        return out
    raise ValueError(f"unsupported id dtype {dtype} on {series.name!r}")


def canonicalize_ids(df: pl.DataFrame, *, strict: bool = False) -> pl.DataFrame:
    """Cast every id-shaped column in ``df`` to Int64.

    Args:
        df: Any built dataset frame.
        strict: Re-raise when a column cannot be cast. Default False leaves a
            non-numeric id (e.g. an ESPN slug in an ``*_id`` field) untouched
            rather than failing a whole season's build over one column.

    Returns:
        The frame with id columns widened to Int64.
    """
    casts = []
    for name in df.columns:
        if not is_id_column(name) or df.schema[name] == pl.Int64:
            continue
        try:
            casts.append(to_int64(df[name]).alias(name))
        except ValueError:
            if strict:
                raise
    return df.with_columns(casts) if casts else df
