# `player_box`



| | |
|---|---|
| **Builder** | [`python/espn_wbb_03_player_box_creation.py`](../../python/espn_wbb_03_player_box_creation.py) |
| **Release tag** | [`espn_womens_college_basketball_player_boxscores`](https://github.com/sportsdataverse/sportsdataverse-data/releases/tag/espn_womens_college_basketball_player_boxscores) |
| **File stem** | `player_box_{season}.{parquet,csv,rds}` |
| **Seasons built** | 2004–2013 (10 seasons) |
| **Last published** | 2026-07-17 (newest release asset) |
| **Tag created** | 2023-03-30 |
| **Release assets** | 72 |

## Automation

`.github/workflows/daily_wbb.yml` — cron 07:00 UTC in season (late Oct, Nov–Dec, Jan–Mar, early Apr), plus `repository_dispatch` from `wehoop-wbb-raw`. Runs `scripts/daily_wbb_data_processor.sh` (`-l python` default, `-l R` rollback).

## Columns

| col_name | type | description |
|---|---|---|
| `game_id` | Int64 | Game identifier carried through from the input schedule. |
| `season` | Int64 | Season identifier from the input games frame (named `sim` instead when the input used a `sim` column). |
| `season_type` | Int64 | Season segment for the row ('REG' for regular-season weeks and the week-0 aggregate, 'POST' for playoff weeks). |
| `game_date` | Date | Calendar date of the game (YYYY-MM-DD). |
| `game_date_time` | Datetime(time_unit='us', time_zone='America/New_York') |  |
| `athlete_id` | Int64 | ESPN numeric identifier for the athlete. |
| `athlete_display_name` | String |  |
| `team_id` | Int64 | 247Sports signed-institution team key as a string (falls back to the committed institution when unsigned). |
| `team_name` | String | Team name/abbreviation the player is credited to for the range. |
| `team_location` | String |  |
| `team_short_display_name` | String |  |
| `minutes` | Float64 |  |
| `field_goals_made` | Int64 |  |
| `field_goals_attempted` | Int64 |  |
| `three_point_field_goals_made` | Int64 |  |
| `three_point_field_goals_attempted` | Int64 |  |
| `free_throws_made` | Int64 |  |
| `free_throws_attempted` | Int64 |  |
| `offensive_rebounds` | Int64 |  |
| `defensive_rebounds` | Int64 |  |
| `rebounds` | Int64 |  |
| `assists` | Int64 | Assisted tackles. |
| `steals` | Int64 |  |
| `blocks` | Int64 |  |
| `turnovers` | Int64 |  |
| `fouls` | Int64 |  |
| `points` | Int64 | Competition points. |
| `starter` | Boolean |  |
| `ejected` | Boolean |  |
| `did_not_play` | Boolean |  |
| `active` | Boolean |  |
| `athlete_jersey` | String |  |
| `athlete_short_name` | String |  |
| `athlete_headshot_href` | String |  |
| `athlete_position_name` | String |  |
| `athlete_position_abbreviation` | String |  |
| `team_display_name` | String |  |
| `team_uid` | String |  |
| `team_slug` | String |  |
| `team_logo` | String |  |
| `team_abbreviation` | String | Team abbreviation. |
| `team_color` | String |  |
| `team_alternate_color` | String |  |
| `home_away` | String |  |
| `team_winner` | Boolean |  |
| `team_score` | Int64 |  |
| `opponent_team_id` | Int64 |  |
| `opponent_team_name` | String |  |
| `opponent_team_location` | String |  |
| `opponent_team_display_name` | String |  |
| `opponent_team_abbreviation` | String |  |
| `opponent_team_logo` | String |  |
| `opponent_team_color` | String |  |
| `opponent_team_alternate_color` | String |  |
| `opponent_team_score` | Int64 |  |

## Coverage

| season | rows | built (UTC) |
|---:|---:|---|
| 2004 | 610 | 2026-07-17 05:08:07 UTC |
| 2005 | 1,161 | 2026-07-17 05:08:10 UTC |
| 2006 | 2,301 | 2026-07-17 05:08:13 UTC |
| 2007 | 4,452 | 2026-07-17 05:08:16 UTC |
| 2008 | 17,461 | 2026-07-17 05:08:25 UTC |
| 2009 | 12,648 | 2026-07-17 05:08:32 UTC |
| 2010 | 12,791 | 2026-07-17 05:08:40 UTC |
| 2011 | 12,235 | 2026-07-17 05:08:46 UTC |
| 2012 | 14,452 | 2026-07-17 05:08:54 UTC |
| 2013 | 18,239 | 2026-07-17 05:09:04 UTC |
