# `officials`



| | |
|---|---|
| **Builder** | [`python/espn_wbb_12_officials_creation.py`](../../python/espn_wbb_12_officials_creation.py) |
| **Release tag** | [`espn_womens_college_basketball_officials`](https://github.com/sportsdataverse/sportsdataverse-data/releases/tag/espn_womens_college_basketball_officials) |
| **File stem** | `officials_{season}.{parquet,csv,rds}` |
| **Seasons built** | 2026–2026 (1 seasons) |
| **Last published** | 2026-07-17 (newest release asset) |
| **Tag created** | 2026-05-11 |
| **Release assets** | 37 |

## Automation

`.github/workflows/daily_wbb.yml` — cron 07:00 UTC in season (late Oct, Nov–Dec, Jan–Mar, early Apr), plus `repository_dispatch` from `wehoop-wbb-raw`. Runs `scripts/daily_wbb_data_processor.sh` (`-l python` default, `-l R` rollback).

## Columns

| col_name | type | description |
|---|---|---|
| `season` | Int64 | Season identifier from the input games frame (named `sim` instead when the input used a `sim` column). |
| `game_id` | Int64 | Game identifier carried through from the input schedule. |
| `official_id` | Int64 |  |
| `official_uid` | String |  |
| `official_full_name` | String |  |
| `official_display_name` | String |  |
| `official_first_name` | String |  |
| `official_last_name` | String |  |
| `official_order` | Int64 |  |
| `position_name` | String | Full position name (e.g. 'Point Guard', 'Goalkeeper'). |
| `position_display_name` | String |  |

## Coverage

| season | rows | built (UTC) |
|---:|---:|---|
| 2026 | 17,458 | 2026-05-30 09:31:32 UTC |
