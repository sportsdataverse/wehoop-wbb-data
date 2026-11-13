# `officials`



| | |
|---|---|
| **Builder** | [`python/espn_wbb_12_officials_creation.py`](../../python/espn_wbb_12_officials_creation.py) |
| **Release tag** | [`espn_womens_college_basketball_officials`](https://github.com/sportsdataverse/sportsdataverse-data/releases/tag/espn_womens_college_basketball_officials) |
| **File stem** | `officials_{season}.{parquet,csv,rds}` |
| **Seasons built** | 2023–2027 (5 seasons) |
| **Last published** | 2026-11-13 (newest release asset) |
| **Tag created** | 2026-05-11 |
| **Release assets** | 47 |

## Load it

| | |
|---|---|
| **R** | `wehoop::load_wbb_officials()` |
| **Python** | `sportsdataverse.wbb.load_wbb_officials()` |

## Join keys

| column | joins to |
|---|---|
| `game_id` | ESPN game id. `schedules` has one row per game; `pbp`, `shots`, `team_box`, `player_box`, `game_rosters` and `officials` key on it. `schedule_crosswalk.espn_game_id` maps it to Fox / Yahoo game ids. |

## Automation

`.github/workflows/daily_wbb.yml` — cron 07:00 UTC in season (late Oct, Nov–Dec, Jan–Mar, early Apr), plus `repository_dispatch` from `wehoop-wbb-raw`. Runs `scripts/daily_wbb_data_processor.sh` (`-l python` default, `-l R` rollback).

## Columns

| col_name | type | description |
|---|---|---|
| `season` | Int64 | Season end-year (2026 = the 2025-26 season). |
| `game_id` | Int32 | ESPN game identifier; the join key across every per-game dataset. Int32. |
| `official_id` | Int32 | ESPN numeric identifier for the game official. |
| `official_uid` | String | ESPN universal id for the game official. |
| `official_full_name` | String | Official's full name. |
| `official_display_name` | String | Official's name formatted for display. |
| `official_first_name` | String | Official's given name. |
| `official_last_name` | String | Official's family name. |
| `official_order` | Int64 | Position of the official in ESPN's listing for the game (1 is the referee). |
| `position_name` | String | Full position name. |
| `position_display_name` | String | Full position name (e.g. "Forward"). |

## Coverage

| season | rows | built (UTC) |
|---:|---:|---|
| 2023 | 16,057 | 2026-11-13 08:27:52 UTC |
| 2024 | 16,245 | 2026-11-13 08:18:52 UTC |
| 2025 | 15,621 | 2026-11-13 08:20:16 UTC |
| 2026 | 17,458 | 2026-11-03 15:21:24 UTC |
| 2027 | 2,002 | 2026-11-13 12:08:39 UTC |
