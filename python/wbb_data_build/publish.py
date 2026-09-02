"""Release publishing -- per-file ``gh release upload --clobber`` (create-if-missing).

Port of the R ``sportsdataverse_save`` upload. Multi-asset globs silently drop
large files, so upload one file at a time. ``runner``/``exists_check`` are
injectable for hermetic tests.
"""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path
from typing import Callable

import polars as pl

from wbb_data_build import io as build_io
from wbb_data_build._logging import get_logger, human_size
from wbb_data_build.config import DatasetSpec

DEFAULT_REPO = "sportsdataverse/sportsdataverse-data"

# Win-probability contract for the pbp release asset. ``wp_enrich`` appends the
# two WP columns in place; a pbp parquet WITHOUT them is the un-enriched
# intermediate, and uploading it is exactly the 2026-07/08 strip incident (every
# nightly overwrote the enriched asset with the plain build, and the platform's
# WP page broke). The guard reads the FILE that would be uploaded -- not the
# frame that produced it -- so any caller, any code path, is covered.
WP_COLS = ("pregame_home_prob", "home_win_prob")
# Observed 2026-09-01 on the release: 2024/2025/2026 -- the only seasons still
# carrying the columns -- are 100% finite (0 nulls, 0 NaN; 2026 = 2,824,090
# plays); 2004/2008/2012/2015/2016/2020 had lost the columns entirely (the
# incident this guard exists to catch). Floor set just below the observed 1.0
# -- a real enrichment scores every play; a partial one is a bug, not a state.
WP_MIN_FINITE_RATE = 0.999

log = get_logger()


class UnenrichedPbpError(ValueError):
    """The pbp parquet about to be uploaded lacks (or barely carries) the WP columns."""


def assert_wp_enriched(
    parquet: Path,
    *,
    cols: tuple[str, ...] = WP_COLS,
    min_finite_rate: float = WP_MIN_FINITE_RATE,
) -> dict[str, float]:
    """Refuse a pbp parquet that is not WP-enriched; return the per-column finite rates.

    Checks the on-disk file (columns present, then the finite -- non-null AND
    non-NaN -- share of each WP column) so the assertion is on the OUTPUT that
    ships, never on which code path ran.

    Raises:
        UnenrichedPbpError: A WP column is missing, or its finite rate is below
            ``min_finite_rate``.
    """
    lf = pl.scan_parquet(parquet)
    schema = lf.collect_schema()
    missing = [c for c in cols if c not in schema]
    if missing:
        raise UnenrichedPbpError(
            f"{parquet.name}: missing WP columns {missing} -- refusing to publish an "
            "un-enriched pbp asset (run wp_enrich first)"
        )
    # is_finite: null -> null (dropped by sum), NaN and +/-inf -> False. strict=False
    # so a mistyped (string) WP column counts as non-finite and trips the floor
    # instead of escaping as a cast error.
    counts = lf.select(
        pl.len().alias("_n"),
        *[pl.col(c).cast(pl.Float64, strict=False).is_finite().sum().alias(c) for c in cols],
    ).collect()
    n = int(counts["_n"][0])
    rates = {c: (int(counts[c][0]) / n if n else 0.0) for c in cols}
    low = {c: r for c, r in rates.items() if r < min_finite_rate}
    if low:
        raise UnenrichedPbpError(
            f"{parquet.name}: WP columns below the {min_finite_rate:.3f} finite-rate floor: "
            f"{ {c: round(r, 4) for c, r in low.items()} } over {n} plays -- refusing to publish"
        )
    return rates


def _gh(args: list[str]) -> None:
    subprocess.run(["gh", *args], check=True, stderr=subprocess.PIPE, text=True)


def _gh_release_exists(tag: str, repo: str) -> bool:
    """True when ``tag`` exists on ``repo``.

    Only a genuine "not found" answer from ``gh`` counts as absence -- a rate
    limit / auth / network failure must never be read as "release missing"
    (that misreading is what makes the caller run ``release create`` on a tag
    that already exists and crash the whole publish run).
    """
    proc = subprocess.run(
        ["gh", "release", "view", tag, "--repo", repo],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
    )
    if proc.returncode == 0:
        return True
    stderr = (proc.stderr or "").strip()
    if "release not found" in stderr.lower():
        return False
    raise RuntimeError(f"gh release view {tag} --repo {repo} failed: {stderr}")


def _dataset_files(spec: DatasetSpec, season: int, base: Path) -> list[Path]:
    root = build_io.dataset_dir(spec, base)
    pq = root / "parquet" / f"{spec.stem}_{season}.parquet"
    cands = [
        pq,
        # .rds is wehoop::load_wbb_*'s ONLY read path -- publishing the parquet
        # without it silently freezes every downstream loader.
        root / "rds" / f"{spec.stem}_{season}.rds",
        root / "csv" / f"{spec.stem}_{season}.csv",
    ]
    files = [f for f in cands if f.exists()]
    if not spec.write_tree_csv and pq.exists():
        # Crosswalks commit no tree csv (their crosswalk/*.csv IS the
        # manifest), but R's file_types = c("rds", "csv", "parquet") still
        # ships a plain .csv asset -- generate it from the parquet.
        tmp = Path(tempfile.mkdtemp(prefix="wbb_publish_")) / f"{spec.stem}_{season}.csv"
        pl.read_parquet(pq).write_csv(tmp)
        files.append(tmp)
    if spec.publish_manifest:
        # R's upload_wbb_manifest ships the manifest csv to the same release
        # tag; only the crosswalk scripts call it. Asset name == file name.
        manifest = build_io.manifest_path(spec, base)
        if manifest.exists():
            files.append(manifest)
    return files


def publish_dataset(
    spec: DatasetSpec,
    season: int,
    *,
    base: str | Path = "wbb",
    repo: str = DEFAULT_REPO,
    dry_run: bool = False,
    runner: Callable[[list[str]], None] | None = None,
    exists_check: Callable[[str, str], bool] | None = None,
) -> dict:
    """Upload a dataset/season's parquet + csv to the release, creating it if missing.

    Args:
        spec: Dataset spec (``dataset``/``stem``/``tag``) from ``config.REGISTRY``.
        season: Season year; must match the files already written by ``io.write_dataset``.
        base: Root directory containing ``{dataset}/{parquet,csv}/...``.
        repo: ``owner/repo`` slug for the release target.
        dry_run: If True, skip all ``gh`` calls and print the would-be uploads.
        runner: Injectable ``gh`` arg-list executor; defaults to a real subprocess call.
        exists_check: Injectable ``(tag, repo) -> bool`` release-existence check.

    Returns:
        dict: ``{"tag": ..., "files": [...], "uploaded": <count>}``.

    Example:
        Quick start::

            from wbb_data_build.config import REGISTRY
            from wbb_data_build import publish
            publish.publish_dataset(REGISTRY["team_box"], 2025)
    """
    run = runner or _gh
    exists = exists_check or _gh_release_exists
    if spec.dataset == "pbp":
        # Before anything else (before the on-the-fly csv is even generated):
        # the pbp asset ships WP-enriched or not at all. Applies to dry runs
        # too -- a dry run that would be refused for real says so.
        pq = build_io.dataset_dir(spec, Path(base)) / "parquet" / f"{spec.stem}_{season}.parquet"
        if not pq.exists():
            raise UnenrichedPbpError(
                f"{pq.name}: no pbp parquet under {base}; refusing to publish a pbp "
                "release asset from leftover files"
            )
        rates = assert_wp_enriched(pq)
        log.info("%s %s: WP contract ok -- finite rates %s", spec.dataset, season, rates)
    files = _dataset_files(spec, season, Path(base))
    if not files:
        log.warning("%s %s: no files to publish under %s", spec.dataset, season, base)
    if not dry_run and not exists(spec.tag, repo):
        log.info("release %s missing on %s -- creating it", spec.tag, repo)
        try:
            run(
                [
                    "release",
                    "create",
                    spec.tag,
                    "--repo",
                    repo,
                    "--title",
                    spec.tag,
                    "--notes",
                    f"{spec.tag} (WBB dataset, Python-built).",
                ]
            )
        except subprocess.CalledProcessError as exc:
            # Belt-and-suspenders for the race exists() didn't catch (e.g. a
            # concurrent run created the tag between the check and here).
            stderr = (exc.stderr or "").lower() if isinstance(exc.stderr, str) else ""
            if "already exists" in stderr:
                log.info("release %s already exists on %s -- continuing", spec.tag, repo)
            else:
                raise
    count = 0
    for f in files:
        size = human_size(f.stat().st_size)
        if dry_run:
            log.info("[dry-run] upload %s (%s) -> %s:%s", f, size, repo, spec.tag)
            continue
        log.info("uploading %s (%s) -> %s:%s", f.name, size, repo, spec.tag)
        run(["release", "upload", spec.tag, str(f), "--repo", repo, "--clobber"])
        count += 1
        log.info("uploaded %s -> %s (asset %d/%d)", f.name, spec.tag, count, len(files))
    return {"tag": spec.tag, "files": [str(f) for f in files], "uploaded": count}
