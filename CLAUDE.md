# CLAUDE.md — wehoop-wbb-data

R compiler (`DESCRIPTION` package `wehoop.wbb`, not on CRAN) that reshapes
per-game ESPN women's college basketball JSON from the paired
[wehoop-wbb-raw](https://github.com/sportsdataverse/wehoop-wbb-raw) into
season-level parquet/csv/rds, then uploads them as GitHub Releases on
`sportsdataverse/sportsdataverse-data`. The `wehoop` package's `load_wbb_*()`
loaders read those releases via piggyback URLs.

Pipeline: `ESPN -> wehoop-wbb-raw --push--> wehoop-wbb-data [HERE] --release--> sportsdataverse-data --> wehoop`.

## Commands (verified)

Driven by `scripts/daily_wbb_data_processor.sh` (getopts `-s -e`; Python
`wbb_data_build` builds + publishes the 11 raw-derived datasets, then R runs
the crosswalks, `serialize_rds.R`, and `run_summary.R`; commits + pushes).
Reads raw JSON from `raw.githubusercontent.com/sportsdataverse/wehoop-wbb-raw`
over HTTP (the 58GB raw repo is never cloned), caching under `.wbb_raw_cache/`.

```sh
bash scripts/daily_wbb_data_processor.sh -s 2025 -e 2025   # full daily compile (CI entry point)
bash scripts/daily_wbb_R_processor.sh -s 2025 -e 2025      # legacy full-R fallback (manual only)
Rscript R/espn_wbb_01_pbp_creation.R -s 2025 -e 2025        # any single R creation script
Rscript R/serialize_rds.R -s 2025 -e 2025 --no-upload       # parquet -> rds, local only
```

Creation scripts run in order: `espn_wbb_01_pbp` (also writes schedules + the
`shots` filtered subset), `_02_team_box`, `_03_player_box`, `_04_rosters`,
`_05_player_season_stats`, `_06_team_season_stats`, `_07_standings`,
`_08_game_rosters`, `_09_officials`, then `wbb_11_team_crosswalk`,
`wbb_12_schedule_crosswalk`, `wbb_13_player_crosswalk`. One-time bootstraps:
`R/0000_create_wehoop_releases_init.R` (creates release tags idempotently),
`R/0001_push_existing_release_data.R`. `R/run_summary.R` writes a CI summary.

`GITHUB_PAT` is required for uploads (CI injects `secrets.SDV_GH_TOKEN`).

The **Python producer** (`python/wbb_data_build/`, uv + polars, parity-tested
against the released parquets) owns the 11 raw-derived datasets in the daily
cron — see `python/wbb_data_build/README.md`. R is retained for the three
crosswalk datasets (live ESPN+Torvik+Fox inputs), the `.rds` serialization
(`R/serialize_rds.R` — wehoop's `load_wbb_*` reads rds), and `run_summary.R`.

```sh
cd python && uv run pytest        # offline parity + smoke suite
uv run python -m wbb_data_build --dataset team_box -s 2025 -e 2025 --dry-run
```

## Outputs

Local committed output under `wbb/<dataset>/{rds,csv,parquet}/`; each script
also uploads to its release tag on `sportsdataverse-data`:

| Release tag | Loader |
|---|---|
| `espn_womens_college_basketball_schedules` | `wehoop::load_wbb_schedule()` |
| `espn_womens_college_basketball_pbp` | `load_wbb_pbp()` |
| `espn_womens_college_basketball_team_boxscores` | `load_wbb_team_box()` |
| `espn_womens_college_basketball_player_boxscores` | `load_wbb_player_box()` |

…plus rosters / player_season_stats / team_season_stats / standings /
game_rosters / officials / shots / crosswalk tags (one per creation script).

## CI

- `.github/workflows/daily_wbb.yml` — cron (in-season, `0 7 UTC`) +
  `repository_dispatch` type `daily_wbb_data` (fired by the raw repo) +
  `workflow_dispatch`; Windows runner. Extracts years from the dispatch commit
  message (`Start:`/`End:` regex), defaulting to `wehoop::most_recent_wbb_season()`.
- `.github/workflows/weekly_wbb.yml` — Sunday `0 6 UTC` roster refresh (runs `espn_wbb_04_rosters_creation.R`).

## Gotchas

- Daily CI commit subject `"WBB Data update (Start: <yr> End: <yr>)"` is load-bearing — don't restyle.
- Schedules + shots are emitted inside `espn_wbb_01_pbp_creation.R`; don't add a separate schedule/shots script — extend `01`.
- Release tags are load-bearing for `wehoop::load_wbb_*()` URL builders; renaming a tag or reorganizing `wbb/` is a breaking change.
- `DESCRIPTION` `Remotes:` pins `wehoop` + `sportsdataverse-data` + `piggyback`; license is CC BY 4.0 (data-repo convention), not MIT.
- Never add AI co-author trailers to commits. Use Conventional Commits (`feat(compile):`, `fix(pbp):`, `ci:`).

## Datasets

<!-- BEGIN GENERATED: datasets -->
| Script | Dataset | Release tag | Last published |
|---|---|---|---|
| [`python/espn_wbb_01_pbp_creation.py`](python/espn_wbb_01_pbp_creation.py) | [`pbp`](docs/datasets/pbp.md) | [`espn_womens_college_basketball_pbp`](https://github.com/sportsdataverse/sportsdataverse-data/releases/tag/espn_womens_college_basketball_pbp) | — |
| [`python/espn_wbb_02_team_box_creation.py`](python/espn_wbb_02_team_box_creation.py) | [`team_box`](docs/datasets/team_box.md) | [`espn_womens_college_basketball_team_boxscores`](https://github.com/sportsdataverse/sportsdataverse-data/releases/tag/espn_womens_college_basketball_team_boxscores) | — |
| [`python/espn_wbb_03_player_box_creation.py`](python/espn_wbb_03_player_box_creation.py) | [`player_box`](docs/datasets/player_box.md) | [`espn_womens_college_basketball_player_boxscores`](https://github.com/sportsdataverse/sportsdataverse-data/releases/tag/espn_womens_college_basketball_player_boxscores) | — |
| [`python/espn_wbb_04_player_core_creation.py`](python/espn_wbb_04_player_core_creation.py) | [`player_core`](docs/datasets/player_core.md) | [`espn_womens_college_basketball_player_core`](https://github.com/sportsdataverse/sportsdataverse-data/releases/tag/espn_womens_college_basketball_player_core) | — |
| [`python/espn_wbb_05_schedules_creation.py`](python/espn_wbb_05_schedules_creation.py) | [`schedules`](docs/datasets/schedules.md) | [`espn_womens_college_basketball_schedules`](https://github.com/sportsdataverse/sportsdataverse-data/releases/tag/espn_womens_college_basketball_schedules) | — |
| [`python/espn_wbb_06_shots_creation.py`](python/espn_wbb_06_shots_creation.py) | [`shots`](docs/datasets/shots.md) | [`espn_womens_college_basketball_shots`](https://github.com/sportsdataverse/sportsdataverse-data/releases/tag/espn_womens_college_basketball_shots) | — |
| [`python/espn_wbb_07_rosters_creation.py`](python/espn_wbb_07_rosters_creation.py) | [`rosters`](docs/datasets/rosters.md) | [`espn_womens_college_basketball_rosters`](https://github.com/sportsdataverse/sportsdataverse-data/releases/tag/espn_womens_college_basketball_rosters) | — |
| [`python/espn_wbb_08_player_season_stats_creation.py`](python/espn_wbb_08_player_season_stats_creation.py) | [`player_season_stats`](docs/datasets/player_season_stats.md) | [`espn_womens_college_basketball_player_season_stats`](https://github.com/sportsdataverse/sportsdataverse-data/releases/tag/espn_womens_college_basketball_player_season_stats) | — |
| [`python/espn_wbb_09_team_season_stats_creation.py`](python/espn_wbb_09_team_season_stats_creation.py) | [`team_season_stats`](docs/datasets/team_season_stats.md) | [`espn_womens_college_basketball_team_season_stats`](https://github.com/sportsdataverse/sportsdataverse-data/releases/tag/espn_womens_college_basketball_team_season_stats) | — |
| [`python/espn_wbb_10_standings_creation.py`](python/espn_wbb_10_standings_creation.py) | [`standings`](docs/datasets/standings.md) | [`espn_womens_college_basketball_standings`](https://github.com/sportsdataverse/sportsdataverse-data/releases/tag/espn_womens_college_basketball_standings) | — |
| [`python/espn_wbb_11_game_rosters_creation.py`](python/espn_wbb_11_game_rosters_creation.py) | [`game_rosters`](docs/datasets/game_rosters.md) | [`espn_womens_college_basketball_game_rosters`](https://github.com/sportsdataverse/sportsdataverse-data/releases/tag/espn_womens_college_basketball_game_rosters) | — |
| [`python/espn_wbb_12_officials_creation.py`](python/espn_wbb_12_officials_creation.py) | [`officials`](docs/datasets/officials.md) | [`espn_womens_college_basketball_officials`](https://github.com/sportsdataverse/sportsdataverse-data/releases/tag/espn_womens_college_basketball_officials) | — |
| [`R/wbb_13_team_crosswalk_creation.R`](R/wbb_13_team_crosswalk_creation.R) | [`team_crosswalk`](docs/datasets/team_crosswalk.md) | [`wbb_crosswalk`](https://github.com/sportsdataverse/sportsdataverse-data/releases/tag/wbb_crosswalk) | — |
| [`R/wbb_14_schedule_crosswalk_creation.R`](R/wbb_14_schedule_crosswalk_creation.R) | [`schedule_crosswalk`](docs/datasets/schedule_crosswalk.md) | [`wbb_crosswalk`](https://github.com/sportsdataverse/sportsdataverse-data/releases/tag/wbb_crosswalk) | — |
| [`R/wbb_15_player_crosswalk_creation.R`](R/wbb_15_player_crosswalk_creation.R) | [`player_crosswalk`](docs/datasets/player_crosswalk.md) | [`wbb_crosswalk`](https://github.com/sportsdataverse/sportsdataverse-data/releases/tag/wbb_crosswalk) | — |
<!-- END GENERATED: datasets -->
