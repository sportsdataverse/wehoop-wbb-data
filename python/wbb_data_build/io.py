"""Dataset IO -- polars port of the R write + ``.append_manifest`` steps.

Writes ``{base}/{dir}/parquet/{stem}_{season}.parquet`` and
``{base}/{dir}/csv/{stem}_{season}.csv`` (plain csv, matching the released
WBB assets), and upserts the ``{league}_{dataset}_in_data_repo.csv`` manifest.
``{dir}`` is the dataset name except for the crosswalks, which share one
``crosswalk/`` dir and commit no tree csv (see ``DatasetSpec``).
``.rds`` is R's native format and is produced by the retained R serialize step
(Plan 2); the parity bar here is the parquet.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import polars as pl
from sportsdataverse._rds import write_rds

from wbb_data_build._logging import get_logger, human_size
from wbb_data_build.config import (
    RDS_ATTR_PREFIX,
    RDS_CLASS,
    RDS_TYPE_TEMPLATE,
    DatasetSpec,
)
from wbb_data_build.ids import canonicalize_ids

_LEAGUE = "wbb"

log = get_logger()


def _utc_now_str() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def dataset_dir(spec: DatasetSpec, base: Path) -> Path:
    """Where this dataset's ``parquet/``/``rds/``/``csv/`` + manifest live.

    Almost always ``{base}/{dataset}``; the three crosswalks share one
    ``{base}/crosswalk`` dir (``spec.out_dir``).
    """
    return base / (spec.out_dir or spec.dataset)


def manifest_path(spec: DatasetSpec, base: Path) -> Path:
    return dataset_dir(spec, base) / f"{_LEAGUE}_{spec.dataset}_in_data_repo.csv"


def _append_manifest(spec: DatasetSpec, season: int, row_count: int, base: Path) -> Path:
    f = manifest_path(spec, base)
    f.parent.mkdir(parents=True, exist_ok=True)
    cols: dict[str, list] = {
        "season": [int(season)],
        "row_count": [int(row_count)],
        "generated_at_utc": [_utc_now_str()],
    }
    if spec.manifest_endpoint is not None:
        # Only the crosswalk manifests carry this column; adding it to the
        # others would change a published asset's schema.
        cols["source_endpoint"] = [spec.manifest_endpoint]
    row = pl.DataFrame(cols)
    if f.exists():
        old = pl.read_csv(f).filter(pl.col("season") != int(season))
        row = pl.concat([old, row], how="diagonal_relaxed")
    row.sort("season").write_csv(f)
    return f


def write_dataset(
    df: pl.DataFrame, spec: DatasetSpec, season: int, *, base: str | Path = "wbb"
) -> list[Path]:
    """Write parquet + csv + manifest for one dataset/season; return parquet+csv paths.

    Ids are canonicalized to Int64 here, at the single write boundary, so every
    dataset agrees. They did not: ``game_id`` shipped Int32 in pbp and String in
    officials, ``athlete_id`` shipped Int32/Int64/String across three datasets,
    and joining them raised ``SchemaError`` on the released data.
    """
    base = Path(base)
    if spec.canonicalize:
        df = canonicalize_ids(df)
    root = dataset_dir(spec, base)
    pq_dir = root / "parquet"
    pq_dir.mkdir(parents=True, exist_ok=True)
    pq = pq_dir / f"{spec.stem}_{season}.parquet"
    df.write_parquet(pq)
    csv = None
    if spec.write_tree_csv:
        csv_dir = root / "csv"
        csv_dir.mkdir(parents=True, exist_ok=True)
        csv = csv_dir / f"{spec.stem}_{season}.csv"
        df.write_csv(csv)
    # .rds is wehoop::load_wbb_*'s ONLY read path -- written natively here, in
    # the same pass as the parquet, so the two can never drift apart. The NBA
    # sibling proved they do: its rds was left to a retained R step it never
    # had, so the parquet updated daily while the rds froze.
    rds_dir = root / "rds"
    rds_dir.mkdir(parents=True, exist_ok=True)
    rds = rds_dir / f"{spec.stem}_{season}.rds"
    stamped = datetime.now(timezone.utc)
    write_rds(
        df,
        rds,
        cls=list(RDS_CLASS),
        # Attribute ORDER is the published contract (make_wehoop_data stamps
        # its pair first, sportsdataverse_save appends its own).
        attributes={
            f"{RDS_ATTR_PREFIX}_timestamp": stamped,
            f"{RDS_ATTR_PREFIX}_type": spec.rds_type
            or RDS_TYPE_TEMPLATE.format(dataset=spec.dataset),
            "sportsdataverse_type": spec.sdv_type or f"{spec.dataset} data",
            "sportsdataverse_timestamp": stamped,
        },
    )
    manifest = _append_manifest(spec, season, df.height, base)
    log.info(
        "wrote %s (%s) + %s (%s)%s, %d rows x %d cols; manifest %s upserted",
        pq,
        human_size(pq.stat().st_size),
        rds.name,
        human_size(rds.stat().st_size),
        f" + {csv.name} ({human_size(csv.stat().st_size)})" if csv is not None else "",
        df.height,
        df.width,
        manifest.name,
    )
    return [p for p in (pq, rds, csv) if p is not None]
