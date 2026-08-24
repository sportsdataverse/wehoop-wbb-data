# `player_box`



| | |
|---|---|
| **Builder** | [`python/espn_wbb_03_player_box_creation.py`](../../python/espn_wbb_03_player_box_creation.py) |
| **Release tag** | [`espn_womens_college_basketball_player_boxscores`](https://github.com/sportsdataverse/sportsdataverse-data/releases/tag/espn_womens_college_basketball_player_boxscores) |
| **File stem** | `player_box_{season}.{parquet,csv,rds}` |
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
| `athlete_id` | Int64 | ESPN numeric identifier for the athlete. |
| `athlete_display_name` | String | Athlete's full display name. |
| `team_id` | Int64 | ESPN numeric identifier for the team. |
| `team_name` | String | Team nickname (e.g. "Bruins"). |
| `team_location` | String | School or city the team represents (e.g. "UCLA"). |
| `team_short_display_name` | String | Shortened team display name. |
| `minutes` | Float64 | Minutes played. |
| `field_goals_made` | Int64 | Field goals made. |
| `field_goals_attempted` | Int64 | Field goals attempted. |
| `three_point_field_goals_made` | Int64 | Three-point field goals made. |
| `three_point_field_goals_attempted` | Int64 | Three-point field goals attempted. |
| `free_throws_made` | Int64 | Free throws made. |
| `free_throws_attempted` | Int64 | Free throws attempted. |
| `offensive_rebounds` | Int64 | Rebounds collected on the offensive end. |
| `defensive_rebounds` | Int64 | Rebounds collected on the defensive end. |
| `rebounds` | Int64 | Total rebounds. |
| `assists` | Int64 | Assists recorded. |
| `steals` | Int64 | Steals recorded. |
| `blocks` | Int64 | Blocked shots recorded. |
| `turnovers` | Int64 | Turnovers committed. |
| `fouls` | Int64 | Personal fouls committed. |
| `points` | Int64 | Points scored. |
| `starter` | Boolean | Whether the athlete started the game. |
| `ejected` | Boolean | Whether the athlete was ejected. |
| `did_not_play` | Boolean | Whether the athlete was available but did not play. |
| `active` | Boolean | Whether the athlete was active for the game. |
| `athlete_jersey` | String | Athlete's jersey number, as a string to preserve leading zeros. |
| `athlete_short_name` | String | Athlete's abbreviated name (first initial plus surname). |
| `athlete_headshot_href` | String | URL of the athlete's ESPN headshot image. |
| `athlete_position_name` | String | Athlete's full position name (e.g. "Forward"). |
| `athlete_position_abbreviation` | String | Athlete's position abbreviation (e.g. "F"). |
| `team_display_name` | String | Full team name including nickname (e.g. "UCLA Bruins"). |
| `team_uid` | String | ESPN universal id for the team. |
| `team_slug` | String | URL slug for the team on espn.com. |
| `team_logo` | String | URL of the team's ESPN logo image. |
| `team_abbreviation` | String | Team abbreviation (e.g. "UCLA"). |
| `team_color` | String | Primary team colour as a hex string, without the leading '#'. |
| `team_alternate_color` | String | Secondary team colour as a hex string, without the leading '#'. |
| `home_away` | String | Whether the athlete's team was the home or away side. |
| `team_winner` | Boolean | Whether this team won the game. |
| `team_score` | Int64 | Final points scored by this team. |
| `opponent_team_id` | Int64 | ESPN team id of the opponent in this game. |
| `opponent_team_name` | String | Opponent nickname. |
| `opponent_team_location` | String | School or city the opponent represents. |
| `opponent_team_display_name` | String | Full opponent name including nickname. |
| `opponent_team_abbreviation` | String | Opponent abbreviation. |
| `opponent_team_logo` | String | URL of the opponent's ESPN logo image. |
| `opponent_team_color` | String | Opponent primary colour as a hex string. |
| `opponent_team_alternate_color` | String | Opponent secondary colour as a hex string. |
| `opponent_team_score` | Int64 | Final points scored by the opponent. |

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
| 2026 | 168,228 | 2026-08-24 02:27:07 UTC |
