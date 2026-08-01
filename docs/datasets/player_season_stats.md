# `player_season_stats`



| | |
|---|---|
| **Builder** | [`python/espn_wbb_08_player_season_stats_creation.py`](../../python/espn_wbb_08_player_season_stats_creation.py) |
| **Release tag** | [`espn_womens_college_basketball_player_season_stats`](https://github.com/sportsdataverse/sportsdataverse-data/releases/tag/espn_womens_college_basketball_player_season_stats) |
| **File stem** | `player_season_stats_{season}.{parquet,csv,rds}` |
| **Seasons built** | 2006–2026 (3 seasons) |
| **Last published** | 2026-07-17 (newest release asset) |
| **Tag created** | 2026-05-11 |
| **Release assets** | 61 |

## Automation

`.github/workflows/daily_wbb.yml` — cron 07:00 UTC in season (late Oct, Nov–Dec, Jan–Mar, early Apr), plus `repository_dispatch` from `wehoop-wbb-raw`. Runs `scripts/daily_wbb_data_processor.sh` (`-l python` default, `-l R` rollback).

## Columns

| col_name | type | description |
|---|---|---|
| `season` | Int64 | Season identifier from the input games frame (named `sim` instead when the input used a `sim` column). |
| `athlete_id` | Int64 | ESPN numeric identifier for the athlete. |
| `athlete_display_name` | String |  |
| `athlete_first_name` | String |  |
| `athlete_last_name` | String |  |
| `athlete_position_abbreviation` | String |  |
| `athlete_jersey` | String |  |
| `team_id` | Int64 | 247Sports signed-institution team key as a string (falls back to the committed institution when unsigned). |
| `team_display_name` | String |  |
| `category` | String |  |
| `stat_label` | String |  |
| `stat_name` | String |  |
| `stat_display_name` | String |  |
| `stat_description` | String |  |
| `display_value` | String |  |
| `value` | Float64 | A class year for which the 247Sports RDB has data for the sport. |

## Coverage

| season | rows | built (UTC) |
|---:|---:|---|
| 2006 | 201 | 2026-07-16 23:47:34 UTC |
| 2007 | 2,553 | 2026-07-16 23:54:52 UTC |
| 2026 | 41,919 | 2026-05-30 08:34:52 UTC |
