# `pbp`



| | |
|---|---|
| **Builder** | [`python/espn_wbb_01_pbp_creation.py`](../../python/espn_wbb_01_pbp_creation.py) |
| **Release tag** | [`espn_womens_college_basketball_pbp`](https://github.com/sportsdataverse/sportsdataverse-data/releases/tag/espn_womens_college_basketball_pbp) |
| **File stem** | `play_by_play_{season}.{parquet,csv,rds}` |
| **Seasons built** | 2004–2026 (23 seasons) |
| **Last published** | 2026-07-29 (newest release asset) |
| **Tag created** | 2023-03-30 |
| **Release assets** | 73 |

## Automation

`.github/workflows/daily_wbb.yml` — cron 07:00 UTC in season (late Oct, Nov–Dec, Jan–Mar, early Apr), plus `repository_dispatch` from `wehoop-wbb-raw`. Runs `scripts/daily_wbb_data_processor.sh` (`-l python` default, `-l R` rollback).

## Columns

| col_name | type | description |
|---|---|---|
| `game_play_number` | Int64 |  |
| `id` | Int64 | 247Sports tag id (prefixed key, e.g. Player_46151084). |
| `sequence_number` | Int64 |  |
| `type_id` | Int64 |  |
| `type_text` | String |  |
| `text` | String |  |
| `away_score` | Int64 |  |
| `home_score` | Int64 |  |
| `period_number` | Int64 |  |
| `period_display_value` | String |  |
| `clock_display_value` | String |  |
| `scoring_play` | Boolean |  |
| `score_value` | Int64 |  |
| `wallclock` | String |  |
| `shooting_play` | Boolean |  |
| `coordinate_x_raw` | Float64 |  |
| `coordinate_y_raw` | Float64 |  |
| `points_attempted` | Int64 |  |
| `short_description` | String |  |
| `team_id` | Int64 | 247Sports signed-institution team key as a string (falls back to the committed institution when unsigned). |
| `athlete_id_1` | Int64 |  |
| `athlete_id_2` | Int64 |  |
| `game_id` | Int64 | Game identifier carried through from the input schedule. |
| `season` | Int64 | Season identifier from the input games frame (named `sim` instead when the input used a `sim` column). |
| `season_type` | Int64 | Season segment for the row ('REG' for regular-season weeks and the week-0 aggregate, 'POST' for playoff weeks). |
| `home_team_id` | Int64 | Home team ESPN id (character; the ratings `team_id` join key). |
| `home_team_name` | String |  |
| `home_team_mascot` | String |  |
| `home_team_abbrev` | String |  |
| `home_team_name_alt` | String |  |
| `away_team_id` | Int64 | Away team ESPN id (character; the ratings `team_id` join key). |
| `away_team_name` | String |  |
| `away_team_mascot` | String |  |
| `away_team_abbrev` | String |  |
| `away_team_name_alt` | String |  |
| `game_spread` | Float64 |  |
| `home_favorite` | Boolean |  |
| `game_spread_available` | Boolean |  |
| `home_team_spread` | Float64 |  |
| `qtr` | Int64 |  |
| `time` | String |  |
| `clock_minutes` | Int64 |  |
| `clock_seconds` | Int64 |  |
| `home_timeout_called` | Boolean |  |
| `away_timeout_called` | Boolean |  |
| `half` | Int64 | Half-inning ("top" or "bottom") -- which side is on offense. |
| `game_half` | Int64 |  |
| `lag_qtr` | Int64 |  |
| `lead_qtr` | Int64 |  |
| `lag_half` | Int64 |  |
| `lead_half` | Int64 |  |
| `start_quarter_seconds_remaining` | Int64 |  |
| `start_half_seconds_remaining` | Int64 |  |
| `start_game_seconds_remaining` | Int64 |  |
| `end_quarter_seconds_remaining` | Int64 |  |
| `end_half_seconds_remaining` | Int64 |  |
| `end_game_seconds_remaining` | Int64 |  |
| `period` | Int64 |  |
| `coordinate_x` | Float64 |  |
| `coordinate_y` | Float64 |  |
| `game_date` | Date | Calendar date of the game (YYYY-MM-DD). |
| `game_date_time` | Datetime(time_unit='us', time_zone='America/New_York') |  |
| `athlete_name_1` | String |  |
| `athlete_name_2` | String |  |
| `athlete_name_3` | String |  |

## Coverage

| season | rows | built (UTC) |
|---:|---:|---|
| 2004 | 16,774 | 2026-07-29 07:01:28 UTC |
| 2005 | 31,293 | 2026-07-29 07:01:46 UTC |
| 2006 | 69,106 | 2026-07-29 07:02:14 UTC |
| 2007 | 135,671 | 2026-07-29 07:03:13 UTC |
| 2008 | 536,606 | 2026-07-29 07:05:32 UTC |
| 2009 | 404,296 | 2026-07-29 07:12:12 UTC |
| 2010 | 320,068 | 2026-07-29 07:17:47 UTC |
| 2011 | 243,610 | 2026-07-29 07:20:36 UTC |
| 2012 | 499,865 | 2026-07-29 07:22:52 UTC |
| 2013 | 627,477 | 2026-07-29 07:27:09 UTC |
| 2014 | 524,623 | 2026-07-29 07:32:28 UTC |
| 2015 | 514,579 | 2026-07-29 07:36:31 UTC |
| 2016 | 562,754 | 2026-07-29 07:40:52 UTC |
| 2017 | 532,077 | 2026-07-29 07:45:16 UTC |
| 2018 | 515,714 | 2026-07-29 07:50:54 UTC |
| 2019 | 511,770 | 2026-07-29 07:55:39 UTC |
| 2020 | 1,652,273 | 2026-07-29 08:02:56 UTC |
| 2021 | 1,188,996 | 2026-07-29 08:19:43 UTC |
| 2022 | 1,760,851 | 2026-07-29 08:34:47 UTC |
| 2023 | 1,883,731 | 2026-07-29 08:53:10 UTC |
| 2024 | 1,908,679 | 2026-07-29 09:10:03 UTC |
| 2025 | 1,973,907 | 2026-07-29 09:27:59 UTC |
| 2026 | 2,824,090 | 2026-07-29 09:45:11 UTC |
