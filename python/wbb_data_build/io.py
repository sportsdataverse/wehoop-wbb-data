"""Dataset IO -- polars port of the R write + ``.append_manifest`` steps.

Writes ``{base}/{dataset}/parquet/{stem}_{season}.parquet`` and
``{base}/{dataset}/csv/{stem}_{season}.csv`` (plain csv, matching the released
WBB assets), and upserts the ``{league}_{dataset}_in_data_repo.csv`` manifest.
``.rds`` is R's native format and is produced by the retained R serialize step
(Plan 2); the parity bar here is the parquet.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import polars as pl

from wbb_data_build._logging import get_logger, human_size
from wbb_data_build.config import DatasetSpec

_LEAGUE = "wbb"

log = get_logger()


def _utc_now_str() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def _append_manifest(spec: DatasetSpec, season: int, row_count: int, base: Path) -> Path:
    f = base / spec.dataset / f"{_LEAGUE}_{spec.dataset}_in_data_repo.csv"
    f.parent.mkdir(parents=True, exist_ok=True)
    row = pl.DataFrame(
        {
            "season": [int(season)],
            "row_count": [int(row_count)],
            "generated_at_utc": [_utc_now_str()],
        }
    )
    if f.exists():
        old = pl.read_csv(f).filter(pl.col("season") != int(season))
        row = pl.concat([old, row], how="diagonal_relaxed")
    row.sort("season").write_csv(f)
    return f


def write_dataset(
    df: pl.DataFrame, spec: DatasetSpec, season: int, *, base: str | Path = "wbb"
) -> list[Path]:
    """Write parquet + csv + manifest for one dataset/season; return parquet+csv paths."""
    base = Path(base)
    pq_dir = base / spec.dataset / "parquet"
    csv_dir = base / spec.dataset / "csv"
    pq_dir.mkdir(parents=True, exist_ok=True)
    csv_dir.mkdir(parents=True, exist_ok=True)
    pq = pq_dir / f"{spec.stem}_{season}.parquet"
    csv = csv_dir / f"{spec.stem}_{season}.csv"
    df.write_parquet(pq)
    df.write_csv(csv)
    manifest = _append_manifest(spec, season, df.height, base)
    log.info(
        "wrote %s (%s) + %s (%s), %d rows x %d cols; manifest %s upserted",
        pq,
        human_size(pq.stat().st_size),
        csv.name,
        human_size(csv.stat().st_size),
        df.height,
        df.width,
        manifest.name,
    )
    return [pq, csv]
