# Fixtures — provenance

Real-data fixtures for the `wbb_data_build` parity harness (Task 7/8). No
synthetic data.

## Captured 2026-07-12

- **3 game-ids**: `401700473`, `401700474`, `401700475` (2025 season).
- **`released/team_box_2025.parquet`**: the R-released oracle, downloaded from
  <https://github.com/sportsdataverse/sportsdataverse-data/releases/tag/espn_womens_college_basketball_team_boxscores>
  (asset `team_box_2025.parquet`), then filtered to the 3 game-ids above (6
  rows = 2 teams x 3 games). Because it's pre-filtered to exactly these
  games, `py` and `r` frames built from these fixtures cover the same games
  and are directly row-count comparable.
- **`raw/wbb/json/final/{game_id}.json`**: verbatim copies of the 3 raw ESPN
  game payloads from the sibling `wehoop-wbb-raw` checkout
  (`wbb/json/final/{game_id}.json`).
- **`raw/wbb/schedules/parquet/wbb_schedule_2025.parquet`**: the raw 2025
  schedule from `wehoop-wbb-raw` (`wbb/schedules/parquet/wbb_schedule_2025.parquet`),
  filtered to the same 3 game-ids. All 3 rows have `game_json == True`, so
  `ingest.season_game_ids(2025, raw_root=<fixtures>/raw)` returns exactly
  these 3 game-ids.

## Selection method

The 3 game-ids are the first 3 (sorted ascending) game-ids that satisfy all
of: present in the released `team_box_2025.parquet`, present in the raw
schedule with `game_json == True`, and have an on-disk
`wbb/json/final/{game_id}.json` in `wehoop-wbb-raw`.

## Captured 2026-07-12 (second wave — per-game oracles + season 2026)

All released oracles below are downloaded from the matching
`sportsdataverse-data` release tag and pre-filtered to the fixture game-ids
(same apples-to-apples design as `team_box_2025.parquet`).

- **Season 2025 oracles** (same 3 game-ids `401700473/4/5`):
  `released/wbb_schedule_2025.parquet` (tag `espn_womens_college_basketball_schedules`,
  3 rows), `released/play_by_play_2025.parquet` (tag `..._pbp`, 1008 rows),
  `released/player_box_2025.parquet` (tag `..._player_boxscores`, 86 rows).
- **Season 2026 fixture games**: `401804834`, `401804835`, `401804836` —
  chosen because the shots/rosters/season-stats/standings/game_rosters/officials
  release tags carry only 2026 assets (no 2025 backfill). All 3 are
  `game_json == True` AND `status_type_completed == True` and have all three
  raw sidecars on disk.
- **Raw (2026)**: `raw/wbb/json/final/{gid}.json`,
  `raw/wbb/game_rosters/json/{gid}.json`, `raw/wbb/officials/json/{gid}.json`
  (verbatim from `wehoop-wbb-raw`), plus
  `raw/wbb/schedules/parquet/wbb_schedule_2026.parquet` filtered to the 3 games.
- **Season 2026 oracles**: `released/shots_2026.parquet` (480 rows),
  `released/game_rosters_2026.parquet` (80 rows),
  `released/officials_2026.parquet` (9 rows) — each from its
  `espn_womens_college_basketball_*` tag, filtered to the 3 2026 game-ids.
