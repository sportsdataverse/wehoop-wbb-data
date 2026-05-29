# CLAUDE.md — wehoop-wbb-data Development Guide

## Repo Overview

`wehoop.wbb` (package name on `DESCRIPTION`) is the R-side parser/compiler
that turns per-game ESPN women's college basketball JSON from
[wehoop-wbb-raw](https://github.com/sportsdataverse/wehoop-wbb-raw) into
season-level compiled ESPN WBB datasets and uploads them as GitHub
Releases on
[sportsdataverse-data](https://github.com/sportsdataverse/sportsdataverse-data).
The package depends on `sportsdataverse/wehoop` for parsing helpers and
`ropensci/piggyback` for release uploads. This repo is not on CRAN — it
is a data-processing workspace whose job is to read raw, compile clean,
and push to releases.

The downstream `wehoop::load_wbb_*()` helpers in `wehoop` read from those
releases via piggyback URLs, so the per-dataset release tags listed below
are load-bearing.

## Pipeline Position

```
ESPN APIs --[python scrape]--> wehoop-wbb-raw
                                    | raw JSON
                                    v
                              wehoop-wbb-data [HERE]
                                    | release upload (piggyback)
                                    v
                              sportsdataverse-data (GitHub Releases)
                                    |
                                    v
                              wehoop::load_wbb_*()
```

The compile scripts pull per-game `wbb/json/final/{game_id}.json` from
`https://raw.githubusercontent.com/sportsdataverse/wehoop-wbb-raw/main`,
extract each per-game field into its corresponding season table, and
upload `.rds` + `.csv` + `.parquet` assets to the release tags below using
`sportsdataversedata::sportsdataverse_save()` (which wraps
`piggyback::pb_upload()`).

## Build & Development Commands

The repo is driven by `scripts/daily_wbb_R_processor.sh`, which calls the
numbered R scripts in `R/` for each season in a range:

```sh
# Daily flow for a single end-year season (the CI entry point)
bash scripts/daily_wbb_R_processor.sh -s 2026 -e 2026 -r false

# Range of seasons
bash scripts/daily_wbb_R_processor.sh -s 2024 -e 2026 -r false

# Call individual R scripts directly when iterating
Rscript R/espn_wbb_01_pbp_creation.R           -s 2026 -e 2026
Rscript R/espn_wbb_02_team_box_creation.R      -s 2026 -e 2026
Rscript R/espn_wbb_03_player_box_creation.R    -s 2026 -e 2026
Rscript R/espn_wbb_04_rosters_creation.R       -s 2026 -e 2026
Rscript R/espn_wbb_05_player_season_stats_creation.R -s 2026 -e 2026
Rscript R/espn_wbb_06_team_season_stats_creation.R   -s 2026 -e 2026
Rscript R/espn_wbb_07_standings_creation.R     -s 2026 -e 2026
Rscript R/espn_wbb_08_game_rosters_creation.R  -s 2026 -e 2026
Rscript R/espn_wbb_09_officials_creation.R     -s 2026 -e 2026
```

**Season convention**: `-s` / `-e` are the *end year* of the season
(2026 = 2025-26 season). All compiled dataset filenames embed that year:
`play_by_play_{year}.{rds,csv,parquet}`,
`wbb_player_box_{year}.{rds,csv,parquet}`, etc.

The shell flag `-r` is passed through to maintain a consistent CLI with
the upstream raw repo, but the compile scripts always rebuild the season
from the raw cache (no per-game skip-if-exists).

## Repo Layout

```
R/
  espn_wbb_01_pbp_creation.R            # Compile schedule + PBP -> wbb/pbp/, espn_womens_college_basketball_pbp release
  espn_wbb_02_team_box_creation.R       # Compile team boxscores -> wbb/team_box/, espn_womens_college_basketball_team_boxscores
  espn_wbb_03_player_box_creation.R     # Compile player boxscores -> wbb/player_box/, espn_womens_college_basketball_player_boxscores
  espn_wbb_04_rosters_creation.R        # Compile team rosters (Phase 1)
  espn_wbb_05_player_season_stats_creation.R  # Compile per-athlete season stats
  espn_wbb_06_team_season_stats_creation.R    # Compile per-team season stats
  espn_wbb_07_standings_creation.R      # Compile per-season standings
  espn_wbb_08_game_rosters_creation.R   # Compile per-game rosters
  espn_wbb_09_officials_creation.R      # Compile per-game officials
  0000_create_wehoop_releases_init.R    # One-time bootstrap of release tags on sportsdataverse-data
  0001_push_existing_release_data.R     # One-time backfill of historical seasons into releases
  manifest_upload_helper.R              # Release manifest upload helper
  minify_json_folders.R                 # Optional JSON minification utility
scripts/
  daily_wbb_R_processor.sh              # CI entry point; loops seasons, commits + pushes
wbb/                                    # Committed compiled output (one folder per dataset)
  schedules/{rds,parquet}/              # Master schedule mirror (also re-released)
  pbp/{rds,parquet}/                    # Per-season play-by-play
  team_box/{rds,parquet}/               # Per-season team boxscores
  player_box/{rds,parquet}/             # Per-season player boxscores
  rosters/                              # Compiled team rosters
.github/workflows/daily_wbb.yml        # CI cron + repository_dispatch + workflow_dispatch
```

## Compiled Datasets

| File prefix    | Local folder        | Release tag (on sportsdataverse-data)                   | Loader                                  |
|----------------|---------------------|---------------------------------------------------------|-----------------------------------------|
| `wbb_schedule` | `wbb/schedules/`    | `espn_womens_college_basketball_schedules`              | `wehoop::load_wbb_schedule()`           |
| `play_by_play` | `wbb/pbp/`          | `espn_womens_college_basketball_pbp`                    | `wehoop::load_wbb_pbp()`                |
| `team_box`     | `wbb/team_box/`     | `espn_womens_college_basketball_team_boxscores`         | `wehoop::load_wbb_team_box()`           |
| `player_box`   | `wbb/player_box/`   | `espn_womens_college_basketball_player_boxscores`       | `wehoop::load_wbb_player_box()`         |

Add a new compiled dataset by writing a new `R/espn_wbb_0N_*.R` script,
appending the matching `wbb/<key>/` subdirectory, adding the script to
`scripts/daily_wbb_R_processor.sh`, and creating the release tag (one-time
via `R/0000_create_wehoop_releases_init.R`). The corresponding loader on
the `wehoop` package side (`load_wbb_<key>()`) also needs a catalog entry.

## Daily CI Workflow

`.github/workflows/daily_wbb.yml`:

- **Cron cadence** (UTC):
  - `0 7 18-31 10 *` — late October (season opens)
  - `0 7 * 11-12 *`  — November - December
  - `0 7 * 1-3 *`    — January - March (regular season + conference tourneys)
  - `0 7 1-12 4 *`   — early April (NCAA Tournament tail)
- **`repository_dispatch`** event type `daily_wbb_data` — fired by
  `wehoop-wbb-raw` after its daily push. The dispatch payload's
  `commit_message` is regex-grepped (`Start:\s*\K[0-9]{4}` /
  `End:\s*\K[0-9]{4}`) for the start/end years, which become
  `START_YEAR` / `END_YEAR`. The raw-side commit format `"WBB Raw Update
  (Start: 2026 End: 2026)"` is therefore load-bearing — do not change it
  without updating the regex in the `Extract years from trigger dispatch`
  step.
- **`workflow_dispatch`** inputs: `start_year`, `end_year` strings.
- Empty inputs fall back to `wehoop::most_recent_wbb_season()`.
- Calls `bash scripts/daily_wbb_R_processor.sh -s $START_YEAR -e $END_YEAR`.

The shell script commits with `"WBB Data update (Start: $i End: $i)"`
per season. That message format may be parsed by downstream automation;
keep the `Start:`/`End:` integers in the subject.

## Conventions

- **Season is end year** everywhere user-facing. `2026` means the 2025-26
  season. File names embed end year only.
- **Compile scripts must be idempotent.** Re-running for a season should
  produce byte-identical output (modulo the timestamp embedded in the S3
  class via `wehoop:::make_wehoop_data()`).
- **`.rds`, `.csv`, and `.parquet`** are uploaded for every per-season
  dataset via `sportsdataversedata::sportsdataverse_save(file_types =
  c("rds", "csv", "parquet"))`. Local `wbb/` mirror keeps `.rds` +
  `.parquet`; CSV is release-only.
- **CLI messaging** uses `cli::cli_progress_step()` /
  `cli::cli_alert_info()`. No `print()` or bare `message()` for status
  updates.
- **Parallelism** is via `furrr::future_map_dfr()` over
  `future::plan("multisession")`. Configured at the top of each compile
  script.
- **Schema drift is wehoop's problem, not this repo's.** If ESPN drops
  or renames a field, the fix belongs in `sportsdataverse/wehoop`'s
  `espn_wbb_*()` helpers. This repo only orchestrates the compile.
- **`wehoop:::espn_wbb_pbp_helper(url)`** and friends are the per-game
  parsers used by the compile scripts. Tag-renaming or signature changes
  in `wehoop` must be coordinated here.

## Cross-Repo References

- Upstream raw cache: <https://github.com/sportsdataverse/wehoop-wbb-raw>
- Parsing functions + loaders: <https://github.com/sportsdataverse/wehoop>
- Release destination: <https://github.com/sportsdataverse/sportsdataverse-data>
- Shared SDV conventions: <https://github.com/sportsdataverse/wehoop/blob/main/CLAUDE.md>
- Sister repos (same shape):
  <https://github.com/sportsdataverse/wehoop-wnba-data>,
  <https://github.com/sportsdataverse/hoopR-mbb-data>,
  <https://github.com/sportsdataverse/hoopR-nba-data>,
  <https://github.com/sportsdataverse/fastRhockey-nhl-data>

## Project-Specific Gotchas

- The `Remotes:` field in `DESCRIPTION` pins `sportsdataverse/wehoop`,
  `sportsdataverse/sportsdataverse-data`, and `ropensci/piggyback`. CI
  installs from those; do not add packages here that are not present in
  those upstreams or on CRAN.
- The compile scripts read raw JSON from `raw.githubusercontent.com`,
  not from a local clone of `wehoop-wbb-raw`. CI race conditions between
  the raw push landing and the data compile starting are avoided by the
  cron offset (raw scrapes at `0 5 UTC`, data compile at `0 7 UTC`) and
  by the `repository_dispatch` mechanism described above.
- Releases on `sportsdataverse-data` are append-only per season — the
  per-season asset is overwritten on re-compile, but the release tag
  itself stays put. Renaming a release tag is a breaking change to all
  downstream `wehoop::load_wbb_*()` consumers.
- Each script calls `rm(list = ls())` + `gc()` on entry and rebuilds the
  full per-season frame; do not assume in-memory state survives between
  scripts in the same shell run.
- The package name in `DESCRIPTION` is `wehoop.wbb` (with a dot), but no
  one imports it as a library — it's metadata for the workspace. Don't
  bother with `library(wehoop.wbb)`.
- License is **CC BY 4.0** (data-repo convention), not MIT like the
  parent `wehoop` package. Compiled datasets carry an attribution
  requirement.

## Commit Convention

Use [Conventional Commits](https://www.conventionalcommits.org/) for
hand-authored changes:

```
feat(compile): add wbb_standings dataset compile script
fix(compile): handle empty game_json field in postseason games
chore(deps): bump wehoop pin in DESCRIPTION Remotes
ci: align cron windows with NCAA WBB tournament calendar
```

The **daily CI commit** uses the load-bearing umbrella format
`"WBB Data update (Start: <year> End: <year>)"` — do not retroactively
re-style those commits or downstream year-parsing will break.

Prefer scoped subjects (`feat(compile): ...`, `fix(pbp): ...`). Use
`type!:` or a `BREAKING CHANGE:` footer for breaking changes (renaming
release tags, changing season conventions, etc.).

**Important**: Never include AI agents or assistants (e.g., Claude,
Copilot, Cursor, GPT, Gemini) as co-authors on commits. Omit all
`Co-Authored-By` trailers referencing AI tools. This applies whether the
change was generated, refactored, or reviewed with AI assistance — the
human author is the sole attributable contributor.
