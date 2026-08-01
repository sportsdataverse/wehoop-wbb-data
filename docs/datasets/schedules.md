# `schedules`



| | |
|---|---|
| **Builder** | [`python/espn_wbb_05_schedules_creation.py`](../../python/espn_wbb_05_schedules_creation.py) |
| **Release tag** | [`espn_womens_college_basketball_schedules`](https://github.com/sportsdataverse/sportsdataverse-data/releases/tag/espn_womens_college_basketball_schedules) |
| **File stem** | `wbb_schedule_{season}.{parquet,csv,rds}` |
| **Seasons built** | — |
| **Last published** | 2026-07-17 (newest release asset) |
| **Tag created** | 2023-03-30 |
| **Release assets** | 85 |

## Automation

`.github/workflows/daily_wbb.yml` — cron 07:00 UTC in season (late Oct, Nov–Dec, Jan–Mar, early Apr), plus `repository_dispatch` from `wehoop-wbb-raw`. Runs `scripts/daily_wbb_data_processor.sh` (`-l python` default, `-l R` rollback).

## Columns

| col_name | type | description |
|---|---|---|
| `id` | Int64 | 247Sports tag id (prefixed key, e.g. Player_46151084). |
| `uid` | String | ESPN universal id for the athlete. |
| `date` | String | Calendar date of the game (YYYY-MM-DD). |
| `attendance` | Float64 |  |
| `time_valid` | Boolean | Whether the event time is confirmed. |
| `neutral_site` | Boolean | Whether the game is at a neutral site (home-field advantage is dropped when true). |
| `conference_competition` | Boolean |  |
| `play_by_play_available` | Boolean |  |
| `recent` | Boolean |  |
| `start_date` | String |  |
| `broadcast` | String |  |
| `highlights` | String |  |
| `notes_type` | String |  |
| `notes_headline` | String |  |
| `broadcast_market` | String |  |
| `broadcast_name` | String |  |
| `type_id` | Int64 |  |
| `type_abbreviation` | String |  |
| `venue_id` | Int64 |  |
| `venue_full_name` | String |  |
| `venue_address_city` | String |  |
| `venue_address_state` | String |  |
| `venue_indoor` | Boolean |  |
| `status_clock` | Float64 |  |
| `status_display_clock` | String |  |
| `status_period` | Float64 |  |
| `status_type_id` | Int64 |  |
| `status_type_name` | String |  |
| `status_type_state` | String |  |
| `status_type_completed` | Boolean |  |
| `status_type_description` | String |  |
| `status_type_detail` | String |  |
| `status_type_short_detail` | String |  |
| `format_regulation_periods` | Float64 |  |
| `home_id` | Int64 |  |
| `home_uid` | String |  |
| `home_location` | String |  |
| `home_name` | String |  |
| `home_abbreviation` | String |  |
| `home_display_name` | String |  |
| `home_short_display_name` | String |  |
| `home_color` | String |  |
| `home_alternate_color` | String |  |
| `home_is_active` | Boolean |  |
| `home_venue_id` | Int64 |  |
| `home_logo` | String |  |
| `home_conference_id` | Int64 |  |
| `home_score` | Int64 |  |
| `home_winner` | Boolean |  |
| `home_current_rank` | Float64 | Current AP/coaches poll ranking of the home team at the time of the game. |
| `home_linescores` | String | Points scored by the home team in each period or half of the game. |
| `home_records` | String | Win-loss record string for the home team at the time of the game. |
| `away_id` | Int64 |  |
| `away_uid` | String |  |
| `away_location` | String |  |
| `away_name` | String |  |
| `away_abbreviation` | String |  |
| `away_display_name` | String |  |
| `away_short_display_name` | String |  |
| `away_color` | String |  |
| `away_alternate_color` | String |  |
| `away_is_active` | Boolean |  |
| `away_venue_id` | Int64 |  |
| `away_logo` | String |  |
| `away_conference_id` | Int64 |  |
| `away_score` | Int64 |  |
| `away_winner` | Boolean |  |
| `away_current_rank` | Float64 | Current AP/coaches poll ranking of the away team at the time of the game. |
| `away_linescores` | String | Points scored by the away team in each period or half of the game. |
| `away_records` | String | Win-loss record string for the away team at the time of the game. |
| `game_id` | Int64 | Game identifier carried through from the input schedule. |
| `season` | Int64 | Season identifier from the input games frame (named `sim` instead when the input used a `sim` column). |
| `season_type` | Int64 | Season segment for the row ('REG' for regular-season weeks and the week-0 aggregate, 'POST' for playoff weeks). |
| `status_type_alt_detail` | String |  |
| `tournament_id` | Int64 |  |
| `groups_id` | Int64 |  |
| `groups_name` | String |  |
| `groups_short_name` | String |  |
| `groups_is_conference` | Boolean |  |
| `game_json` | Boolean |  |
| `game_json_url` | String |  |
| `game_date_time` | Datetime(time_unit='us', time_zone='America/New_York') |  |
| `game_date` | String | Calendar date of the game (YYYY-MM-DD). |
| `PBP` | Boolean |  |
| `team_box` | Boolean |  |
| `player_box` | Boolean |  |

## Coverage

_No build manifest yet._
