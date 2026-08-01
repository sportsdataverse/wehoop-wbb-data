# `team_box`



| | |
|---|---|
| **Builder** | [`python/espn_wbb_02_team_box_creation.py`](../../python/espn_wbb_02_team_box_creation.py) |
| **Release tag** | [`espn_womens_college_basketball_team_boxscores`](https://github.com/sportsdataverse/sportsdataverse-data/releases/tag/espn_womens_college_basketball_team_boxscores) |
| **File stem** | `team_box_{season}.{parquet,csv,rds}` |
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
| `team_id` | Int64 | 247Sports signed-institution team key as a string (falls back to the committed institution when unsigned). |
| `team_uid` | String |  |
| `team_slug` | String |  |
| `team_location` | String |  |
| `team_name` | String | Team name/abbreviation the player is credited to for the range. |
| `team_abbreviation` | String | Team abbreviation. |
| `team_display_name` | String |  |
| `team_short_display_name` | String |  |
| `team_color` | String |  |
| `team_alternate_color` | String |  |
| `team_logo` | String |  |
| `team_home_away` | String |  |
| `team_score` | Int64 |  |
| `team_winner` | Boolean |  |
| `assists` | Int64 | Assisted tackles. |
| `blocks` | Int64 |  |
| `defensive_rebounds` | Int64 |  |
| `fast_break_points` | String |  |
| `field_goal_pct` | Float64 |  |
| `field_goals_made` | Int64 |  |
| `field_goals_attempted` | Int64 |  |
| `fouls` | Int64 |  |
| `free_throw_pct` | Float64 |  |
| `free_throws_made` | Int64 |  |
| `free_throws_attempted` | Int64 |  |
| `largest_lead` | String |  |
| `lead_changes` | String |  |
| `lead_percentage` | String |  |
| `offensive_rebounds` | Int64 |  |
| `points_in_paint` | String |  |
| `steals` | Int64 |  |
| `team_turnovers` | Int64 |  |
| `technical_fouls` | Int64 |  |
| `three_point_field_goal_pct` | Float64 |  |
| `three_point_field_goals_made` | Int64 |  |
| `three_point_field_goals_attempted` | Int64 |  |
| `total_rebounds` | Int64 |  |
| `total_technical_fouls` | Int64 |  |
| `total_turnovers` | Int64 |  |
| `turnover_points` | String |  |
| `turnovers` | Int64 |  |
| `opponent_team_id` | Int64 |  |
| `opponent_team_uid` | String |  |
| `opponent_team_slug` | String |  |
| `opponent_team_location` | String |  |
| `opponent_team_name` | String |  |
| `opponent_team_abbreviation` | String |  |
| `opponent_team_display_name` | String |  |
| `opponent_team_short_display_name` | String |  |
| `opponent_team_color` | String |  |
| `opponent_team_alternate_color` | String |  |
| `opponent_team_logo` | String |  |
| `opponent_team_score` | Int64 |  |

## Coverage

| season | rows | built (UTC) |
|---:|---:|---|
| 2004 | 126 | 2026-07-17 05:07:07 UTC |
| 2005 | 230 | 2026-07-17 05:07:09 UTC |
| 2006 | 496 | 2026-07-17 05:07:12 UTC |
| 2007 | 928 | 2026-07-17 05:07:16 UTC |
| 2008 | 3,522 | 2026-07-17 05:07:25 UTC |
| 2009 | 2,590 | 2026-07-17 05:07:33 UTC |
| 2010 | 1,850 | 2026-07-17 05:07:39 UTC |
| 2011 | 1,462 | 2026-07-17 05:07:44 UTC |
| 2012 | 2,884 | 2026-07-17 05:07:52 UTC |
| 2013 | 3,662 | 2026-07-17 05:08:01 UTC |
