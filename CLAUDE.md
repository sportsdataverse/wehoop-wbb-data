# CLAUDE.md — wehoop-wbb-data Development Guide

## Repo Overview

`wehoop-wbb-data` is the R-side parser that consumes per-game ESPN JSON
already scraped into `wehoop-wbb-raw`, compiles tidy per-season tables
(play-by-play, team box, player box), and uploads them as releases on
`sportsdataverse/sportsdataverse-data` via `piggyback` /
`sportsdataversedata::sportsdataverse_save()`. The `wehoop` R package
then loads from those releases — this repo is the link between the raw
JSON cache and the final tidy data surface.

## Pipeline Position

```
ESPN APIs --[python]--> wehoop-wbb-raw --[push trigger]--> wehoop-wbb-data [HERE]
                                                                |
                                                                | sportsdataverse_save()
                                                                v
                                                          sportsdataverse-data releases
                                                                |
                                                                | load_wbb_*()
                                                                v
                                                            wehoop R package
```

CI in `.github/workflows/daily_wbb.yml` runs on schedule, on
`repository_dispatch: daily_wbb_data` (fired by `wehoop-wbb-raw`), and on
manual `workflow_dispatch`. It calls `scripts/daily_wbb_R_processor.sh`,
which loops the season range and runs the three creation scripts in order.

## Build & Development Commands

```sh
# Full daily flow for one or more seasons (CI entry point)
bash scripts/daily_wbb_R_processor.sh -s 2025 -e 2025

# Or call the creation scripts directly
Rscript R/espn_wbb_01_pbp_creation.R         -s 2025 -e 2025
Rscript R/espn_wbb_02_team_box_creation.R    -s 2025 -e 2025
Rscript R/espn_wbb_03_player_box_creation.R  -s 2025 -e 2025
```

The creation scripts pull schedule + per-game JSON from
`https://raw.githubusercontent.com/sportsdataverse/wehoop-wbb-raw/main/wbb/...`,
parse via `wehoop::espn_wbb_pbp()` family functions, write per-season
parquet/rds locally under `wbb/`, and call
`sportsdataversedata::sportsdataverse_save()` with
`file_types = c("rds", "csv", "parquet")` to upload to the release tags
(`espn_womens_college_basketball_pbp`,
`espn_womens_college_basketball_team_boxscores`, etc.).

## Project Structure

```
R/
  0000_create_wehoop_releases_init.R   # One-shot release-tag bootstrapper
  0001_push_existing_release_data.R    # Backfill existing local data into releases
  espn_wbb_01_pbp_creation.R           # Per-season PBP compile + upload
  espn_wbb_02_team_box_creation.R      # Per-season team box compile + upload
  espn_wbb_03_player_box_creation.R    # Per-season player box compile + upload
  minify_json_folders.R                # Strip whitespace from json/raw blobs
scripts/
  daily_wbb_R_processor.sh             # CI entry point — loops seasons, commits, pushes
.github/workflows/
  daily_wbb.yml                        # Scheduled + dispatch + manual triggers
DESCRIPTION                            # R deps (uses wehoop, sportsdataversedata, piggyback)
requirements.txt                       # Python deps (used by helpers if present)
```

## Cross-Repo References

- Shared coding conventions, tidyverse style, cli messaging, ESPN wrapper pattern: <https://github.com/sportsdataverse/wehoop/blob/main/CLAUDE.md>
- Upstream raw data source: <https://github.com/sportsdataverse/wehoop-wbb-raw>
- Downstream consumer: <https://github.com/sportsdataverse/wehoop>

The actual ESPN parser lives in `wehoop` (not here). The creation scripts
are thin compile-and-upload wrappers; bug fixes to per-game parsing belong
in `wehoop` itself.

## Project-Specific Gotchas

- The three creation scripts MUST run in order (`01_pbp` → `02_team_box` → `03_player_box`). The team/player box scripts read state set up by the PBP step.
- `sportsdataversedata::sportsdataverse_save()` with `file_types = c("rds", "csv", "parquet")` is the upload boundary. Set `SPORTSDATAVERSE.UPLOAD.MAX_TIMES` (CI sets `20`) to control retry budget on flaky GitHub release uploads.
- The CI workflow runs on `windows-latest`. R-version- or platform-sensitive code (e.g., file path separators in glue strings) should be tested with that in mind.
- `scripts/daily_wbb_R_processor.sh` does `git pull` / `git commit` / `git push` between seasons — local artifacts under `wbb/` are committed back to this repo. Don't add new files there casually.
- Schedules are sourced from `wehoop-wbb-raw` over raw.githubusercontent.com. If raw URLs start 404'ing, the upstream commit may not have landed on `main` yet — wait for the trigger workflow to settle.

## Commit Convention

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
feat(pbp): add new espn_wbb shot zone columns to play_by_play export
fix(team-box): handle missing OT periods in season-aggregate compile
chore(release): rotate piggyback token rotation steps in daily_wbb.yml
docs: expand README pipeline diagram
```

Prefer scoped subjects. Use `type!:` or a `BREAKING CHANGE:` footer for
breaking changes. Split unrelated work into separate commits.

**Important: Never include AI agents or assistants (e.g., Claude, Copilot, Cursor, GPT, Gemini) as co-authors on commits.** Omit all `Co-Authored-By` trailers referencing AI tools. This applies whether the change was generated, refactored, or reviewed with AI assistance — the human author is the sole attributable contributor.
