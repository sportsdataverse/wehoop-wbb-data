# `officials`



| | |
|---|---|
| **Builder** | [`python/espn_wbb_12_officials_creation.py`](../../python/espn_wbb_12_officials_creation.py) |
| **Release tag** | [`espn_womens_college_basketball_officials`](https://github.com/sportsdataverse/sportsdataverse-data/releases/tag/espn_womens_college_basketball_officials) |
| **File stem** | `officials_{season}.{parquet,csv,rds}` |
| **Seasons built** | 2026 (1 season) |
| **Last published** | 2026-07-17 (newest release asset) |
| **Tag created** | 2026-05-11 |
| **Release assets** | 37 |

## Automation

`.github/workflows/daily_wbb.yml` — cron 07:00 UTC in season (late Oct, Nov–Dec, Jan–Mar, early Apr), plus `repository_dispatch` from `wehoop-wbb-raw`. Runs `scripts/daily_wbb_data_processor.sh` (`-l python` default, `-l R` rollback).

## Columns

| col_name | type | description |
|---|---|---|
| `season` | Int64 | Season end-year (2026 = the 2025-26 season). |
| `game_id` | Int64 | ESPN game identifier; the join key across every per-game dataset. Int64. |
| `official_id` | Int64 | ESPN numeric identifier for the game official. |
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
| 2026 | 17,458 | 2026-05-30 09:31:32 UTC |
