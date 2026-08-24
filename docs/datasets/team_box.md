# `team_box`



| | |
|---|---|
| **Builder** | [`python/espn_wbb_02_team_box_creation.py`](../../python/espn_wbb_02_team_box_creation.py) |
| **Release tag** | [`espn_womens_college_basketball_team_boxscores`](https://github.com/sportsdataverse/sportsdataverse-data/releases/tag/espn_womens_college_basketball_team_boxscores) |
| **File stem** | `team_box_{season}.{parquet,csv,rds}` |
| **Seasons built** | 2004–2026 (11 seasons, non-contiguous) |
| **Last published** | 2026-08-24 (newest release asset) |
| **Tag created** | 2023-03-30 |
| **Release assets** | 72 |

## Automation

`.github/workflows/daily_wbb.yml` — cron 07:00 UTC in season (late Oct, Nov–Dec, Jan–Mar, early Apr), plus `repository_dispatch` from `wehoop-wbb-raw`. Runs `scripts/daily_wbb_data_processor.sh` (`-l python` default, `-l R` rollback).

## Columns

| col_name | type | description |
|---|---|---|
| `game_id` | Int64 | ESPN game identifier; the join key across every per-game dataset. Int64. |
| `season` | Int64 | Season end-year (2026 = the 2025-26 season). |
| `season_type` | Int64 | ESPN season segment code -- 2 regular season, 3 postseason. |
| `game_date` | Date | Calendar date of the game. |
| `game_date_time` | Datetime(time_unit='us', time_zone='America/New_York') | Tip-off timestamp in US Eastern time. |
| `team_id` | Int64 | ESPN numeric identifier for the team. |
| `team_uid` | String | ESPN universal id for the team. |
| `team_slug` | String | URL slug for the team on espn.com. |
| `team_location` | String | School or city the team represents (e.g. "UCLA"). |
| `team_name` | String | Team nickname (e.g. "Bruins"). |
| `team_abbreviation` | String | Team abbreviation (e.g. "UCLA"). |
| `team_display_name` | String | Full team name including nickname (e.g. "UCLA Bruins"). |
| `team_short_display_name` | String | Shortened team display name. |
| `team_color` | String | Primary team colour as a hex string, without the leading '#'. |
| `team_alternate_color` | String | Secondary team colour as a hex string, without the leading '#'. |
| `team_logo` | String | URL of the team's ESPN logo image. |
| `team_home_away` | String | Whether this team was the home or away side. |
| `team_score` | Int64 | Final points scored by this team. |
| `team_winner` | Boolean | Whether this team won the game. |
| `assists` | Int64 | Assists recorded. |
| `blocks` | Int64 | Blocked shots recorded. |
| `defensive_rebounds` | Int64 | Rebounds collected on the defensive end. |
| `fast_break_points` | String | Points scored in transition. |
| `field_goal_pct` | Float64 | Field goal percentage, 0-100. |
| `field_goals_made` | Int64 | Field goals made. |
| `field_goals_attempted` | Int64 | Field goals attempted. |
| `fouls` | Int64 | Personal fouls committed. |
| `free_throw_pct` | Float64 | Free throw percentage, 0-100. |
| `free_throws_made` | Int64 | Free throws made. |
| `free_throws_attempted` | Int64 | Free throws attempted. |
| `largest_lead` | String | Largest lead held during the game. |
| `lead_changes` | String | Number of times the lead changed hands. |
| `lead_percentage` | String | Share of game time this team led. |
| `offensive_rebounds` | Int64 | Rebounds collected on the offensive end. |
| `points_in_paint` | String | Points scored inside the paint. |
| `steals` | Int64 | Steals recorded. |
| `team_turnovers` | Int64 | Turnovers charged to the team rather than to an individual player. |
| `technical_fouls` | Int64 | Technical fouls committed. |
| `three_point_field_goal_pct` | Float64 | Three-point field goal percentage, 0-100. |
| `three_point_field_goals_made` | Int64 | Three-point field goals made. |
| `three_point_field_goals_attempted` | Int64 | Three-point field goals attempted. |
| `total_rebounds` | Int64 | Total rebounds (offensive plus defensive). |
| `total_technical_fouls` | Int64 | Total technical fouls, including bench and coaching technicals. |
| `total_turnovers` | Int64 | Total turnovers, including team turnovers. |
| `turnover_points` | String | Points scored off the opponent's turnovers. |
| `turnovers` | Int64 | Turnovers committed. |
| `opponent_team_id` | Int64 | ESPN team id of the opponent in this game. |
| `opponent_team_uid` | String | ESPN universal id for the opponent. |
| `opponent_team_slug` | String | URL slug for the opponent on espn.com. |
| `opponent_team_location` | String | School or city the opponent represents. |
| `opponent_team_name` | String | Opponent nickname. |
| `opponent_team_abbreviation` | String | Opponent abbreviation. |
| `opponent_team_display_name` | String | Full opponent name including nickname. |
| `opponent_team_short_display_name` | String | Shortened opponent display name. |
| `opponent_team_color` | String | Opponent primary colour as a hex string. |
| `opponent_team_alternate_color` | String | Opponent secondary colour as a hex string. |
| `opponent_team_logo` | String | URL of the opponent's ESPN logo image. |
| `opponent_team_score` | Int64 | Final points scored by the opponent. |

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
| 2026 | 12,058 | 2026-08-24 02:25:43 UTC |
