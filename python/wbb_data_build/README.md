# wbb_data_build — Python producer for the ESPN WBB release datasets

Parity port of the R creation scripts (`R/espn_wbb_*_creation.R`). Reshapes
the sibling [wehoop-wbb-raw](https://github.com/sportsdataverse/wehoop-wbb-raw)
checkout into the released season files (parquet + csv + manifest) and
publishes them to the `espn_womens_college_basketball_*` release tags on
`sportsdataverse-data`. R is retained as the byte-parity oracle: a dataset
ships only when its Python parquet matches the R-released parquet (column
set/order, dtypes, row count, values) on real captured fixtures.

## Flow

```
wehoop-wbb-raw (sibling, on disk)
  └─ ingest.py     season_game_ids / season_completed_game_ids /
                   season_dir_ids / read_final(subdir=...)
      └─ reshapers.py   per-game RESHAPERS (delegate to sportsdataverse.wbb
                        helper_wbb_* producers) + season-level SEASON_BUILDERS
          └─ build.py   build_season(): reshape -> union -> arrange(desc(game_date))
              └─ io.py  {base}/{dataset}/parquet + csv + manifest upsert
                  └─ publish.py  per-file `gh release upload --clobber`
```

## Setup

```sh
cd python
uv sync            # sportsdataverse resolves from git+main ([tool.uv.sources])

# raw_root: a sibling checkout on disk...
export WEHOOP_WBB_RAW_ROOT=/path/to/wehoop-wbb-raw
# ...or (what CI uses -- the 58GB raw repo is never cloned) the HTTP base:
export WEHOOP_WBB_RAW_ROOT=https://raw.githubusercontent.com/sportsdataverse/wehoop-wbb-raw/main
# HTTP mode caches per-game JSON under $WEHOOP_WBB_CACHE (default .wbb_raw_cache/)
```

## CLI

```sh
uv run python -m wbb_data_build --dataset team_box -s 2025 -e 2025 --dry-run
uv run python -m wbb_data_build --dataset pbp      -s 2025 -e 2026 --publish
```

Build `pbp` before `shots` (shots project the built pbp parquet) and before
`schedules` (the schedule stamps `PBP`/`team_box`/`player_box` flags from the
built datasets' game-id sets).

## Dataset status

All 11 raw-derived datasets are parity-green against the released assets:
`pbp`, `schedules`, `shots`, `team_box`, `player_box`, `rosters`,
`player_season_stats`, `team_season_stats`, `standings`, `game_rosters`,
`officials`. The three `*_crosswalk` datasets still build via the R scripts
(`wbb_1{1,2,3}_*_creation.R`) — they consume live ESPN + Torvik + Fox inputs,
not the raw repo, and move to Python when those source surfaces land in
sportsdataverse.

The daily cron (`.github/workflows/daily_wbb.yml` →
`scripts/daily_wbb_data_processor.sh`) runs this producer for all 11
datasets, then R serializes each parquet to `.rds` (`R/serialize_rds.R`,
rds-only upload — wehoop's `load_wbb_*` reads rds) and runs the crosswalks
and `run_summary.R`.
