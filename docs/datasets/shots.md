# `shots`



| | |
|---|---|
| **Builder** | [`python/espn_wbb_06_shots_creation.py`](../../python/espn_wbb_06_shots_creation.py) |
| **Release tag** | [`espn_womens_college_basketball_shots`](https://github.com/sportsdataverse/sportsdataverse-data/releases/tag/espn_womens_college_basketball_shots) |
| **File stem** | `shots_{season}.{parquet,csv,rds}` |
| **Seasons built** | 2004–2026 (23 seasons) |
| **Last published** | 2026-07-29 (newest release asset) |
| **Tag created** | 2026-05-11 |
| **Release assets** | 74 |

## Automation

`.github/workflows/daily_wbb.yml` — cron 07:00 UTC in season (late Oct, Nov–Dec, Jan–Mar, early Apr), plus `repository_dispatch` from `wehoop-wbb-raw`. Runs `scripts/daily_wbb_data_processor.sh` (`-l python` default, `-l R` rollback).

## Columns

| col_name | type | description |
|---|---|---|
| `game_id` | Int64 | Game identifier carried through from the input schedule. |
| `season` | Int64 | Season identifier from the input games frame (named `sim` instead when the input used a `sim` column). |
| `period_number` | Int64 |  |
| `clock_display_value` | String |  |
| `team_id` | Int64 | 247Sports signed-institution team key as a string (falls back to the committed institution when unsigned). |
| `athlete_id_1` | Int64 |  |
| `athlete_id_2` | Int64 |  |
| `type_id` | Int64 |  |
| `type_text` | String |  |
| `scoring_play` | Boolean |  |
| `score_value` | Int64 |  |
| `coordinate_x` | Float64 |  |
| `coordinate_y` | Float64 |  |
| `coordinate_x_raw` | Float64 |  |
| `coordinate_y_raw` | Float64 |  |
| `athlete_name_1` | String |  |
| `athlete_name_2` | String |  |
| `team_name` | String | Team name/abbreviation the player is credited to for the range. |
| `team_mascot` | String |  |
| `team_abbrev` | String |  |

## Coverage

| season | rows | built (UTC) |
|---:|---:|---|
| 2004 | 9,431 | 2026-07-29 10:18:51 UTC |
| 2005 | 17,113 | 2026-07-29 10:18:59 UTC |
| 2006 | 37,699 | 2026-07-29 10:19:08 UTC |
| 2007 | 71,911 | 2026-07-29 10:19:23 UTC |
| 2008 | 275,637 | 2026-07-29 10:19:47 UTC |
| 2009 | 195,912 | 2026-07-29 10:20:53 UTC |
| 2010 | 143,088 | 2026-07-29 10:21:50 UTC |
| 2011 | 108,937 | 2026-07-29 10:22:28 UTC |
| 2012 | 223,250 | 2026-07-29 10:23:00 UTC |
| 2013 | 280,321 | 2026-07-29 10:23:59 UTC |
| 2014 | 239,798 | 2026-07-29 10:24:49 UTC |
| 2015 | 231,742 | 2026-07-29 10:25:53 UTC |
| 2016 | 255,435 | 2026-07-29 10:26:56 UTC |
| 2017 | 243,424 | 2026-07-29 10:28:08 UTC |
| 2018 | 237,615 | 2026-07-29 10:29:18 UTC |
| 2019 | 234,861 | 2026-07-29 10:30:28 UTC |
| 2020 | 750,351 | 2026-07-29 10:31:43 UTC |
| 2021 | 542,119 | 2026-07-29 10:34:55 UTC |
| 2022 | 799,239 | 2026-07-29 10:37:06 UTC |
| 2023 | 855,000 | 2026-07-29 10:40:20 UTC |
| 2024 | 867,657 | 2026-07-29 10:43:08 UTC |
| 2025 | 804,750 | 2026-07-29 10:46:39 UTC |
| 2026 | 907,805 | 2026-07-29 10:49:50 UTC |
