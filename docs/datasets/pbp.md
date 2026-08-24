# `pbp`



| | |
|---|---|
| **Builder** | [`python/espn_wbb_01_pbp_creation.py`](../../python/espn_wbb_01_pbp_creation.py) |
| **Release tag** | [`espn_womens_college_basketball_pbp`](https://github.com/sportsdataverse/sportsdataverse-data/releases/tag/espn_womens_college_basketball_pbp) |
| **File stem** | `play_by_play_{season}.{parquet,csv,rds}` |
| **Seasons built** | 2004–2026 (23 seasons) |
| **Last published** | 2026-08-24 (newest release asset) |
| **Tag created** | 2023-03-30 |
| **Release assets** | 73 |

## Automation

`.github/workflows/daily_wbb.yml` — cron 07:00 UTC in season (late Oct, Nov–Dec, Jan–Mar, early Apr), plus `repository_dispatch` from `wehoop-wbb-raw`. Runs `scripts/daily_wbb_data_processor.sh` (`-l python` default, `-l R` rollback).

## Columns

| col_name | type | description |
|---|---|---|
| `game_play_number` | Int64 | 1-based ordinal of the play within the game, assigned during compilation. |
| `id` | Int64 | ESPN identifier for the row's own entity (the play id in pbp, the game id in schedules). |
| `sequence_number` | Int64 | ESPN's monotonically increasing sequence number for the play within the game. |
| `type_id` | Int64 | ESPN play-type identifier (pbp) or event-type identifier (schedules). |
| `type_text` | String | Play type as published by ESPN (e.g. "Jumpball"). |
| `text` | String | Full narrative description of the play as published by ESPN. |
| `away_score` | Int64 | Away team score at this point in the game (pbp) or final (schedules). |
| `home_score` | Int64 | Home team score at this point in the game (pbp) or final (schedules). |
| `period_number` | Int64 | Period number the play occurred in. |
| `period_display_value` | String | Period formatted for display (e.g. "1st Quarter"). |
| `clock_display_value` | String | Game clock at the time of the play, formatted MM:SS. |
| `scoring_play` | Boolean | Whether the play resulted in points. |
| `score_value` | Int64 | Points the play was worth (0, 1, 2 or 3). |
| `wallclock` | String | Real-world UTC timestamp at which ESPN recorded the play. |
| `shooting_play` | Boolean | Whether the play was a shot attempt. |
| `coordinate_x_raw` | Float64 | Shot x-coordinate exactly as published by ESPN, before translation. |
| `coordinate_y_raw` | Float64 | Shot y-coordinate exactly as published by ESPN, before translation. |
| `points_attempted` | Int64 | Points the shot attempt would have been worth had it gone in. |
| `short_description` | String | Abbreviated play description. |
| `team_id` | Int64 | ESPN numeric identifier for the team. |
| `athlete_id_1` | Int64 | ESPN id of the primary athlete involved in the play (shooter, rebounder, fouler). |
| `athlete_id_2` | Int64 | ESPN id of the secondary athlete involved in the play (assister, blocker, fouled). |
| `game_id` | Int64 | ESPN game identifier; the join key across every per-game dataset. Int64. |
| `season` | Int64 | Season end-year (2026 = the 2025-26 season). |
| `season_type` | Int64 | ESPN season segment code -- 2 regular season, 3 postseason. |
| `home_team_id` | Int64 | ESPN team id of the home team. |
| `home_team_name` | String | Home team location name. |
| `home_team_mascot` | String | Home team nickname/mascot. |
| `home_team_abbrev` | String | Home team abbreviation. |
| `home_team_name_alt` | String | Alternate home team name as published in the play feed. |
| `away_team_id` | Int64 | ESPN team id of the away team. |
| `away_team_name` | String | Away team location name. |
| `away_team_mascot` | String | Away team nickname/mascot. |
| `away_team_abbrev` | String | Away team abbreviation. |
| `away_team_name_alt` | String | Alternate away team name as published in the play feed. |
| `game_spread` | Float64 | Absolute pre-game point spread used for win-probability inputs. |
| `home_favorite` | Boolean | Whether the home team was the pre-game favourite. |
| `game_spread_available` | Boolean | Whether a pre-game spread was published for this game. |
| `home_team_spread` | Float64 | Pre-game point spread from the home team's perspective. |
| `qtr` | Int64 | Quarter number the play occurred in. |
| `time` | String | Game clock at the time of the play, formatted MM:SS. |
| `clock_minutes` | Int64 | Whole minutes remaining on the game clock. |
| `clock_seconds` | Int64 | Seconds component remaining on the game clock. |
| `home_timeout_called` | Boolean | Whether the home team called a timeout on this play. |
| `away_timeout_called` | Boolean | Whether the away team called a timeout on this play. |
| `half` | Int64 | Half the play occurred in (1 or 2); the women's game is played in quarters, so this is derived from the period. |
| `game_half` | Int64 | Half the play occurred in (1 or 2). |
| `lag_qtr` | Int64 | Quarter of the preceding play; used for period-boundary logic. |
| `lead_qtr` | Int64 | Quarter of the following play; used for period-boundary logic. |
| `lag_half` | Int64 | Half of the preceding play; used for period-boundary logic. |
| `lead_half` | Int64 | Half of the following play; used for period-boundary logic. |
| `start_quarter_seconds_remaining` | Int64 | Seconds left in the quarter at the start of the play. |
| `start_half_seconds_remaining` | Int64 | Seconds left in the half at the start of the play. |
| `start_game_seconds_remaining` | Int64 | Seconds left in the game at the start of the play. |
| `end_quarter_seconds_remaining` | Int64 | Seconds left in the quarter at the end of the play. |
| `end_half_seconds_remaining` | Int64 | Seconds left in the half at the end of the play. |
| `end_game_seconds_remaining` | Int64 | Seconds left in the game at the end of the play. |
| `period` | Int64 | Period number the play occurred in. |
| `coordinate_x` | Float64 | Shot x-coordinate translated to a half-court frame, in feet from the basket. |
| `coordinate_y` | Float64 | Shot y-coordinate translated to a half-court frame, in feet from the basket. |
| `game_date` | Date | Calendar date of the game. |
| `game_date_time` | Datetime(time_unit='us', time_zone='America/New_York') | Tip-off timestamp in US Eastern time. |
| `athlete_name_1` | String | Display name of the primary athlete involved in the play. |
| `athlete_name_2` | String | Display name of the secondary athlete involved in the play. |
| `athlete_name_3` | String | Display name of a third athlete involved in the play; rarely populated. |

## Coverage

| season | rows | built (UTC) |
|---:|---:|---|
| 2004 | 16,774 | 2026-08-24 01:49:43 UTC |
| 2005 | 31,293 | 2026-08-24 01:50:08 UTC |
| 2006 | 69,106 | 2026-08-24 01:50:46 UTC |
| 2007 | 135,671 | 2026-08-24 01:52:18 UTC |
| 2008 | 536,606 | 2026-08-24 01:56:18 UTC |
| 2009 | 404,296 | 2026-08-24 01:45:49 UTC |
| 2010 | 320,068 | 2026-08-24 01:46:22 UTC |
| 2011 | 243,610 | 2026-08-24 01:46:38 UTC |
| 2012 | 499,865 | 2026-08-24 01:47:07 UTC |
| 2013 | 627,477 | 2026-08-24 01:47:46 UTC |
| 2014 | 524,623 | 2026-08-24 01:48:19 UTC |
| 2015 | 514,579 | 2026-08-24 01:48:50 UTC |
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
| 2026 | 2,824,090 | 2026-08-24 02:40:56 UTC |
