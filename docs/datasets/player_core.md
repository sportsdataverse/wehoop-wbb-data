# `player_core`



| | |
|---|---|
| **Builder** | [`python/espn_wbb_04_player_core_creation.py`](../../python/espn_wbb_04_player_core_creation.py) |
| **Release tag** | [`espn_womens_college_basketball_player_core`](https://github.com/sportsdataverse/sportsdataverse-data/releases/tag/espn_womens_college_basketball_player_core) |
| **File stem** | `player_core_{season}.{parquet,csv,rds}` |
| **Seasons built** | — |
| **Last published** | 2026-07-17 (newest release asset) |
| **Tag created** | 2026-07-17 |
| **Release assets** | 66 |

## Automation

`.github/workflows/daily_wbb.yml` — cron 07:00 UTC in season (late Oct, Nov–Dec, Jan–Mar, early Apr), plus `repository_dispatch` from `wehoop-wbb-raw`. Runs `scripts/daily_wbb_data_processor.sh` (`-l python` default, `-l R` rollback).

## Columns

| col_name | type | description |
|---|---|---|
| `season` | Int64 | Season identifier from the input games frame (named `sim` instead when the input used a `sim` column). |
| `athlete_id` | Int64 | ESPN numeric identifier for the athlete. |
| `guid` | String |  |
| `uid` | String | ESPN universal id for the athlete. |
| `slug` | String | URL slug for the recruit's On3 profile. |
| `type` | String | Institution type code (college / pro / high school). |
| `first_name` | String | Given name of the transfer player. |
| `last_name` | String | Family (surname) of the transfer player. |
| `full_name` | String | Full name of the program (school plus nickname). |
| `display_name` | String | Full display name of the team (e.g. 'Los Angeles Lakers'). |
| `short_name` | String | Abbreviated name (typically first initial plus last name). |
| `height` | Float64 | Recruit height (formatted string, e.g. "6-2"). |
| `display_height` | String | Athlete height, formatted for display. |
| `weight` | Float64 | Player's listed weight in pounds. |
| `display_weight` | String | Athlete weight, formatted for display. |
| `age` | Int64 | Athlete age in years. |
| `date_of_birth` | String | Athlete date of birth (ISO 8601). |
| `birth_city` | String | Athlete birth city. |
| `birth_state` | String |  |
| `birth_country` | String | Athlete birth country. |
| `jersey` | String | Athlete's jersey number as a string. |
| `position_id` | Int64 |  |
| `position_name` | String | Full position name (e.g. 'Point Guard', 'Goalkeeper'). |
| `position_abbreviation` | String | Abbreviation of the ranked position (e.g. QB, EDGE). |
| `position_display_name` | String |  |
| `college_id` | Int64 |  |
| `current_team_id` | Int64 |  |
| `headshot_href` | String | URL of the quarterback's ESPN headshot image. |
| `experience_years` | Int64 |  |
| `status_id` | Int64 |  |
| `status_name` | String |  |
| `status_type` | String |  |
| `draft_year` | Int64 |  |
| `draft_round` | Int64 | Round in which the player was drafted (null if undrafted). |
| `draft_selection` | Int64 |  |
| `active` | Boolean |  |

## Coverage

_No build manifest yet._
