# wehoop-wbb-data Copilot Instructions

## Project Context

This repo is the R-side parser/compiler for ESPN women's college
basketball. It reads per-game JSON from
[wehoop-wbb-raw](https://github.com/sportsdataverse/wehoop-wbb-raw),
compiles season-level `.rds`/`.csv`/`.parquet` files under `wbb/`, and
uploads them as GitHub Releases on
[sportsdataverse-data](https://github.com/sportsdataverse/sportsdataverse-data).
Downstream `wehoop::load_wbb_*()` loaders consume those releases.

Pipeline: `ESPN -> wehoop-wbb-raw -> wehoop-wbb-data [HERE] -> sportsdataverse-data -> wehoop`.

Package name in `DESCRIPTION` is `wehoop.wbb`. Not on CRAN. License is
**CC BY 4.0** (data-repo convention).

## Repository Workflow

- Branch from `main`; `main` is the default branch.
- The CI entry point is
  `scripts/daily_wbb_R_processor.sh -s <START> -e <END> -r <true|false>`.
- Compile scripts orchestrate `wehoop` helpers — fix ESPN parser bugs
  upstream in `sportsdataverse/wehoop`, not here.
- Do not reorganize the `wbb/` output tree without aligning the matching
  loaders in `sportsdataverse/wehoop`.

## Build & Development Commands

```sh
bash scripts/daily_wbb_R_processor.sh -s 2026 -e 2026 -r false

Rscript R/espn_wbb_01_pbp_creation.R               -s 2026 -e 2026
Rscript R/espn_wbb_02_team_box_creation.R          -s 2026 -e 2026
Rscript R/espn_wbb_03_player_box_creation.R        -s 2026 -e 2026
Rscript R/espn_wbb_04_rosters_creation.R           -s 2026 -e 2026
Rscript R/espn_wbb_05_player_season_stats_creation.R -s 2026 -e 2026
Rscript R/espn_wbb_06_team_season_stats_creation.R   -s 2026 -e 2026
Rscript R/espn_wbb_07_standings_creation.R         -s 2026 -e 2026
Rscript R/espn_wbb_08_game_rosters_creation.R      -s 2026 -e 2026
Rscript R/espn_wbb_09_officials_creation.R         -s 2026 -e 2026
```

Season convention: `-s` / `-e` are the *end year* of the season
(`2026` = 2025-26). Output filenames embed that year.

## Outputs and Release Tags

| File prefix    | Local folder        | Release tag (on sportsdataverse-data)                   |
|----------------|---------------------|---------------------------------------------------------|
| `wbb_schedule` | `wbb/schedules/`    | `espn_womens_college_basketball_schedules`              |
| `play_by_play` | `wbb/pbp/`          | `espn_womens_college_basketball_pbp`                    |
| `team_box`     | `wbb/team_box/`     | `espn_womens_college_basketball_team_boxscores`         |
| `player_box`   | `wbb/player_box/`   | `espn_womens_college_basketball_player_boxscores`       |

Release tags are load-bearing — renaming a tag breaks downstream
`wehoop::load_wbb_*()` consumers.

## Code Style

- Follow the parent `wehoop` package's R conventions: tidyverse style,
  `snake_case`, 2-space indentation.
- Prefer `furrr::future_map_dfr()` over `future::plan("multisession")`
  for per-game compile parallelism.
- Use `cli::cli_progress_step()` / `cli::cli_alert_info()` for status —
  no `print()` or bare `message()`.
- Keep compile scripts idempotent: re-running a season produces
  byte-identical output (modulo the timestamp from
  `wehoop:::make_wehoop_data()`).
- Don't add bespoke ESPN parsing here — call into `wehoop:::espn_wbb_*`
  helpers and persist their output.

## Daily CI Workflow

`.github/workflows/daily_wbb.yml`:

- Cron cadence (UTC): `0 7 18-31 10 *` (late Oct), `0 7 * 11-12 *`
  (Nov-Dec), `0 7 * 1-3 *` (Jan-Mar), `0 7 1-12 4 *` (early Apr).
- `repository_dispatch` event-type `daily_wbb_data` — fired by
  `wehoop-wbb-raw` after its daily push. The dispatch payload's
  `commit_message` is regex-grepped for `Start:\s*\K[0-9]{4}` and
  `End:\s*\K[0-9]{4}` to extract `START_YEAR` / `END_YEAR`. The raw
  repo's commit format `"WBB Raw Update (Start: YYYY End: YYYY)"` is
  therefore load-bearing.
- `workflow_dispatch` inputs: `start_year`, `end_year` strings.
- Empty inputs fall back to `wehoop::most_recent_wbb_season()`.
- Calls `bash scripts/daily_wbb_R_processor.sh -s $START_YEAR -e $END_YEAR`.

## Cross-Repo References

- Shared SDV conventions: <https://github.com/sportsdataverse/wehoop/blob/main/CLAUDE.md>
- Upstream raw cache: <https://github.com/sportsdataverse/wehoop-wbb-raw>
- Release destination: <https://github.com/sportsdataverse/sportsdataverse-data>

## Conventional Commits

Use: `type(scope): description`. Common types: `feat`, `fix`, `chore`,
`ci`, `docs`, `refactor`. Use `type!:` or a `BREAKING CHANGE:` footer
for breaking changes.

The **daily CI commit** uses the load-bearing umbrella format
`"WBB Data update (Start: <year> End: <year>)"` — do not retroactively
re-style those commits or downstream year-parsing will break.

**Important: Never include AI agents or assistants (e.g., Claude, Copilot, Cursor, GPT, Gemini) as co-authors on commits.** Omit all `Co-Authored-By` trailers referencing AI tools. This applies whether the change was generated, refactored, or reviewed with AI assistance — the human author is the sole attributable contributor.
