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

log = get_logger()


def _gh(args: list[str]) -> None:
    subprocess.run(["gh", *args], check=True)


def _gh_release_exists(tag: str, repo: str) -> bool:
    return (
        subprocess.run(
            ["gh", "release", "view", tag, "--repo", repo],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        ).returncode
        == 0
    )


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
    files = _dataset_files(spec, season, Path(base))
    if not files:
        log.warning("%s %s: no files to publish under %s", spec.dataset, season, base)
    if not dry_run and not exists(spec.tag, repo):
        log.info("release %s missing on %s -- creating it", spec.tag, repo)
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
