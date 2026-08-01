# `schedules`



| | |
|---|---|
| **Builder** | [`python/espn_wbb_05_schedules_creation.py`](../../python/espn_wbb_05_schedules_creation.py) |
| **Release tag** | [`espn_womens_college_basketball_schedules`](https://github.com/sportsdataverse/sportsdataverse-data/releases/tag/espn_womens_college_basketball_schedules) |
| **File stem** | `wbb_schedule_{season}.{parquet,csv,rds}` |
| **Seasons built** | — |
| **Last published** | — (newest release asset) |
| **Tag created** | — |
| **Release assets** | — |

## Automation

`.github/workflows/daily_wbb.yml` — cron 07:00 UTC in season (late Oct, Nov–Dec, Jan–Mar, early Apr), plus `repository_dispatch` from `wehoop-wbb-raw`. Runs `scripts/daily_wbb_data_processor.sh` (`-l python` default, `-l R` rollback).

## Columns

| col_name | type | description |
|---|---|---|
| `id` | Int64 | ESPN identifier for the row's own entity (the play id in pbp, the game id in schedules). |
| `uid` | String | ESPN universal id for the entity (e.g. "s:40~l:54~t:26"). |
| `date` | String | Calendar date of the game. |
| `attendance` | Float64 | Announced attendance for the game. |
| `time_valid` | Boolean | Whether the published tip-off time is confirmed rather than a placeholder. |
| `neutral_site` | Boolean | Whether the game was played at a neutral site. |
| `conference_competition` | Boolean | Whether both teams are in the same conference. |
| `play_by_play_available` | Boolean | Whether ESPN publishes play-by-play for this game. |
| `recent` | Boolean | ESPN flag marking the game as recently played. |
| `start_date` | String | Scheduled tip-off timestamp as published by ESPN (UTC, ISO 8601). |
| `broadcast` | String | Broadcast network(s) carrying the game. |
| `highlights` | String | Raw ESPN highlight-clip metadata for the game, stringified. |
| `notes_type` | String | ESPN classification of the game note (e.g. "event"). |
| `notes_headline` | String | ESPN headline describing the game's context (e.g. a tournament round). |
| `broadcast_market` | String | Broadcast reach -- "national" or "home". |
| `broadcast_name` | String | Primary broadcast network name. |
| `type_id` | Int64 | ESPN play-type identifier (pbp) or event-type identifier (schedules). |
| `type_abbreviation` | String | Abbreviation of the ESPN event type (e.g. "TRNMNT"). |
| `venue_id` | Int64 | ESPN identifier for the venue hosting the game. |
| `venue_full_name` | String | Name of the arena hosting the game. |
| `venue_address_city` | String | City the venue is located in. |
| `venue_address_state` | String | State or province the venue is located in. |
| `venue_indoor` | Boolean | Whether the venue is indoors. |
| `status_clock` | Float64 | Seconds remaining on the game clock at the time of capture. |
| `status_display_clock` | String | Game clock at the time of capture, formatted MM:SS. |
| `status_period` | Float64 | Period the game was in at the time of capture. |
| `status_type_id` | Int64 | ESPN status-type identifier for the game state. |
| `status_type_name` | String | ESPN status constant (e.g. "STATUS_FINAL"). |
| `status_type_state` | String | Coarse game state -- "pre", "in" or "post". |
| `status_type_completed` | Boolean | Whether the game has finished. |
| `status_type_description` | String | Human-readable game status (e.g. "Final"). |
| `status_type_detail` | String | Detailed game status, including overtime notation. |
| `status_type_short_detail` | String | Abbreviated game status. |
| `format_regulation_periods` | Float64 | Number of regulation periods for the game (4 quarters, or 2 halves pre-2015). |
| `home_id` | Int64 | ESPN team id of the home team. |
| `home_uid` | String | ESPN universal id for the home team. |
| `home_location` | String | School or city the home team represents. |
| `home_name` | String | Home team nickname. |
| `home_abbreviation` | String | Home team abbreviation. |
| `home_display_name` | String | Full home team name including nickname. |
| `home_short_display_name` | String | Shortened home team display name. |
| `home_color` | String | Home team primary colour as a hex string. |
| `home_alternate_color` | String | Home team secondary colour as a hex string. |
| `home_is_active` | Boolean | Whether ESPN lists the home team as currently active. |
| `home_venue_id` | Int64 | ESPN venue id of the home team's usual arena. |
| `home_logo` | String | URL of the home team's ESPN logo image. |
| `home_conference_id` | Int64 | ESPN conference (group) id of the home team. |
| `home_score` | Int64 | Home team score at this point in the game (pbp) or final (schedules). |
| `home_winner` | Boolean | Whether the home team won. |
| `home_current_rank` | Float64 | AP/coaches poll ranking of the home team at game time. |
| `home_linescores` | String | Home team points scored in each period, stringified. |
| `home_records` | String | Home team win-loss record at game time, stringified. |
| `away_id` | Int64 | ESPN team id of the away team. |
| `away_uid` | String | ESPN universal id for the away team. |
| `away_location` | String | School or city the away team represents. |
| `away_name` | String | Away team nickname. |
| `away_abbreviation` | String | Away team abbreviation. |
| `away_display_name` | String | Full away team name including nickname. |
| `away_short_display_name` | String | Shortened away team display name. |
| `away_color` | String | Away team primary colour as a hex string. |
| `away_alternate_color` | String | Away team secondary colour as a hex string. |
| `away_is_active` | Boolean | Whether ESPN lists the away team as currently active. |
| `away_venue_id` | Int64 | ESPN venue id of the away team's usual arena. |
| `away_logo` | String | URL of the away team's ESPN logo image. |
| `away_conference_id` | Int64 | ESPN conference (group) id of the away team. |
| `away_score` | Int64 | Away team score at this point in the game (pbp) or final (schedules). |
| `away_winner` | Boolean | Whether the away team won. |
| `away_current_rank` | Float64 | AP/coaches poll ranking of the away team at game time. |
| `away_linescores` | String | Away team points scored in each period, stringified. |
| `away_records` | String | Away team win-loss record at game time, stringified. |
| `game_id` | Int64 | ESPN game identifier; the join key across every per-game dataset. Int64. |
| `season` | Int64 | Season end-year (2026 = the 2025-26 season). |
| `season_type` | Int64 | ESPN season segment code -- 2 regular season, 3 postseason. |
| `status_type_alt_detail` | String | Alternate status detail, typically the overtime marker. |
| `tournament_id` | Int64 | ESPN tournament identifier when the game is part of a bracket. |
| `groups_id` | Int64 | ESPN group (conference) id the game is classified under. |
| `groups_name` | String | Full conference name the game is classified under. |
| `groups_short_name` | String | Abbreviated conference name. |
| `groups_is_conference` | Boolean | Whether the group represents a conference rather than a broader grouping. |
| `game_json` | Boolean | Whether the raw per-game summary JSON was captured in wehoop-wbb-raw. |
| `game_json_url` | String | Public raw.githubusercontent URL of the captured per-game summary JSON. |
| `game_date_time` | Datetime(time_unit='us', time_zone='America/New_York') | Tip-off timestamp in US Eastern time. |
| `game_date` | String | Calendar date of the game. |
| `PBP` | Boolean | Whether this game contributed rows to the released play-by-play dataset. |
| `team_box` | Boolean | Whether this game contributed rows to the released team box score dataset. |
| `player_box` | Boolean | Whether this game contributed rows to the released player box score dataset. |

## Coverage

_No build manifest yet._
