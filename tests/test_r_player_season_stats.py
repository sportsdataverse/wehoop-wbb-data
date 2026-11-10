"""R twin of player_season_stats reads the same season row as the Python build.

ESPN's per-category flat ``totals`` array is the CAREER line; the season line is
the ``statistics[]`` entry whose ``season.year`` matches (wehoop-wnba-data#29,
sportsdataverse-py#1094). These run the R stage's parsers on the real 2026
fixtures: values and team fields must equal sdv-py's helper, and the team
fields follow the season row, not an earlier school or the roster identity.
The traded-player Totals-row case is covered on real data by the WNBA twin of
this stage (same code); no WBB fixture has one. Needs a local ``Rscript`` with
jsonlite/purrr/tibble/glue/rlang; skipped otherwise (the CI runner has no R).
"""

from __future__ import annotations

import io
import json
import shutil
import subprocess
from pathlib import Path

import polars as pl
import pytest
from sportsdataverse.wbb import helper_wbb_player_season_stats

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "R" / "espn_wbb_08_player_season_stats_creation.R"
RAW = REPO / "tests" / "fixtures" / "raw" / "wbb" / "player_season_stats" / "json"
SEASON = 2026
TRANSFER = 4703656  # real payload: Houston 2021, Jackson State 2023-24, Charlotte 2026
COLS = ["athlete_id", "team_id", "team_display_name", "category", "stat_name", "display_value"]

# Evaluates only the script's `name <- function(...)` definitions, so its
# optparse / network main loop never runs. Args: script, raw_base, season,
# optional identity-lookup JSON ({athlete_id: {team_id, ...}}).
R_DRIVER = r"""
args <- commandArgs(trailingOnly = TRUE)
suppressPackageStartupMessages({ library(rlang); library(purrr); library(tibble) })
for (e in parse(file = args[[1]])) {
  if (is.call(e) && identical(e[[1]], as.name("<-")) && is.call(e[[3]]) &&
      identical(e[[3]][[1]], as.name("function"))) eval(e, globalenv())
}
season <- as.integer(args[[3]])
ident <- if (length(args) >= 4) jsonlite::fromJSON(args[[4]], simplifyVector = FALSE) else list()
ids <- sub("\\.json$", "", list.files(file.path(args[[2]], season), pattern = "\\.json$"))
out <- purrr::map_dfr(ids, function(a) parse_one_athlete(season, a, ident, args[[2]]))
cols <- c("athlete_id", "team_id", "team_display_name", "category", "stat_name", "display_value")
utils::write.csv(out[, cols], stdout(), row.names = FALSE)
"""


def _r_available() -> bool:
    if shutil.which("Rscript") is None:
        return False
    probe = 'q(status = !all(sapply(c("jsonlite","purrr","tibble","glue","rlang"), requireNamespace, quietly = TRUE)))'
    return subprocess.run(["Rscript", "-e", probe], capture_output=True).returncode == 0


pytestmark = pytest.mark.skipif(
    not _r_available(), reason="needs Rscript + jsonlite/purrr/tibble/glue/rlang"
)


def _run_r(tmp_path: Path, raw_base: Path, ident: dict | None = None) -> pl.DataFrame:
    driver = tmp_path / "driver.R"
    driver.write_text(R_DRIVER, encoding="utf-8")
    cmd = ["Rscript", str(driver), str(SCRIPT), raw_base.as_posix(), str(SEASON)]
    if ident is not None:
        (tmp_path / "ident.json").write_text(json.dumps(ident), encoding="utf-8")
        cmd.append((tmp_path / "ident.json").as_posix())
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", check=True)
    return pl.read_csv(
        io.StringIO(res.stdout),
        schema_overrides={"display_value": pl.String, "team_display_name": pl.String},
        null_values="NA",
    ).with_columns(pl.col("athlete_id", "team_id").cast(pl.Int32))


def test_r_player_season_stats_matches_the_python_build(tmp_path):
    r = _run_r(tmp_path, RAW)
    py = pl.concat(
        [
            helper_wbb_player_season_stats(
                json.loads(f.read_text(encoding="utf-8")), season=SEASON, athlete_id=int(f.stem)
            )
            for f in sorted(RAW.joinpath(str(SEASON)).glob("*.json"))
        ]
    ).select(COLS)
    assert r.schema["athlete_id"] == py.schema["athlete_id"]
    assert r.schema["team_id"] == py.schema["team_id"]
    assert r.sort(COLS, nulls_last=True).equals(py.sort(COLS, nulls_last=True))
    # The season line, not the career one: no college season reaches 42 games.
    gp = r.filter(pl.col("stat_name") == "gamesPlayed")
    assert gp.height > 0
    assert gp["display_value"].cast(pl.Float64).max() <= 42


def test_r_team_fields_follow_the_season_row(tmp_path):
    root = tmp_path / "raw"
    (root / str(SEASON)).mkdir(parents=True)
    shutil.copy(RAW / str(SEASON) / f"{TRANSFER}.json", root / str(SEASON))
    payload = json.loads((root / str(SEASON) / f"{TRANSFER}.json").read_text(encoding="utf-8"))
    cat = next(c for c in payload["categories"] if c["name"] == "averages")
    row = next(s for s in cat["statistics"] if s["season"]["year"] == SEASON)
    ident = {str(TRANSFER): {"team_id": 999, "team_display_name": "Roster Team"}}
    r = _run_r(tmp_path, root, ident)
    gp = r.filter((pl.col("category") == "averages") & (pl.col("stat_name") == "gamesPlayed"))
    assert gp["display_value"].to_list() == [str(row["stats"][cat["names"].index("gamesPlayed")])]
    # The 2026 row's team: not the first school listed (Houston), not the roster identity.
    team = payload["teams"][row["teamSlug"]]
    assert gp.select("team_id", "team_display_name").row(0) == (
        int(row["teamId"]),
        team["displayName"],
    )
