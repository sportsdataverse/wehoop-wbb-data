# CLAUDE.md — wehoop-wbb-data

R compiler (`DESCRIPTION` package `wehoop.wbb`, not on CRAN) that reshapes
per-game ESPN women's college basketball JSON from the paired
[wehoop-wbb-raw](https://github.com/sportsdataverse/wehoop-wbb-raw) into
season-level parquet/csv/rds, then uploads them as GitHub Releases on
`sportsdataverse/sportsdataverse-data`. The `wehoop` package's `load_wbb_*()`
loaders read those releases via piggyback URLs.

Pipeline: `ESPN -> wehoop-wbb-raw --push--> wehoop-wbb-data [HERE] --release--> sportsdataverse-data --> wehoop`.

## Commands (verified)

Driven by `scripts/daily_wbb_R_processor.sh` (getopts `-s -e`; loops seasons,
runs each creation script, commits + pushes). Reads raw JSON from
`raw.githubusercontent.com/sportsdataverse/wehoop-wbb-raw`, not a local clone.

```sh
bash scripts/daily_wbb_R_processor.sh -s 2025 -e 2025   # full daily compile
Rscript R/espn_wbb_01_pbp_creation.R -s 2025 -e 2025     # any single creation script
```

Creation scripts run in order: `espn_wbb_01_pbp` (also writes schedules + the
`shots` filtered subset), `_02_team_box`, `_03_player_box`, `_04_rosters`,
`_05_player_season_stats`, `_06_team_season_stats`, `_07_standings`,
`_08_game_rosters`, `_09_officials`, then `wbb_11_team_crosswalk`,
`wbb_12_schedule_crosswalk`, `wbb_13_player_crosswalk`. One-time bootstraps:
`R/0000_create_wehoop_releases_init.R` (creates release tags idempotently),
`R/0001_push_existing_release_data.R`. `R/run_summary.R` writes a CI summary.

`GITHUB_PAT` is required for uploads (CI injects `secrets.SDV_GH_TOKEN`).

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
