# `player_core`



| | |
|---|---|
| **Builder** | [`python/espn_wbb_04_player_core_creation.py`](../../python/espn_wbb_04_player_core_creation.py) |
| **Release tag** | [`espn_womens_college_basketball_player_core`](https://github.com/sportsdataverse/sportsdataverse-data/releases/tag/espn_womens_college_basketball_player_core) |
| **File stem** | `player_core_{season}.{parquet,csv,rds}` |
| **Seasons built** | 2026 (1 season) |
| **Last published** | 2026-08-24 (newest release asset) |
| **Tag created** | 2026-07-17 |
| **Release assets** | 66 |

## Automation

`.github/workflows/daily_wbb.yml` — cron 07:00 UTC in season (late Oct, Nov–Dec, Jan–Mar, early Apr), plus `repository_dispatch` from `wehoop-wbb-raw`. Runs `scripts/daily_wbb_data_processor.sh` (`-l python` default, `-l R` rollback).

## Columns

| col_name | type | description |
|---|---|---|
| `season` | Int64 | Season end-year (2026 = the 2025-26 season). |
| `athlete_id` | Int64 | ESPN numeric identifier for the athlete. |
| `guid` | String | ESPN global GUID for the entity, stable across seasons. |
| `uid` | String | ESPN universal id for the entity (e.g. "s:40~l:54~t:26"). |
| `slug` | String | URL slug for the entity on espn.com. |
| `type` | String | Classification code for the row's entity. |
| `first_name` | String | Athlete's given name. |
| `last_name` | String | Athlete's family name. |
| `full_name` | String | Full name of the entity. |
| `display_name` | String | Full display name of the entity. |
| `short_name` | String | Abbreviated name (typically first initial plus surname). |
| `height` | Float64 | Athlete's height in inches. |
| `display_height` | String | Athlete's height formatted for display (e.g. "6-2"). |
| `weight` | Float64 | Athlete's listed weight in pounds. |
| `display_weight` | String | Athlete's weight formatted for display. |
| `age` | Int64 | Athlete's age in years. |
| `date_of_birth` | String | Athlete's date of birth. |
| `birth_city` | String | City the athlete was born in. |
| `birth_state` | String | State or province the athlete was born in. |
| `birth_country` | String | Country the athlete was born in. |
| `jersey` | String | Jersey number, as a string to preserve leading zeros. |
| `position_id` | Int64 | ESPN identifier for the athlete's listed position. |
| `position_name` | String | Full position name. |
| `position_abbreviation` | String | Position abbreviation. |
| `position_display_name` | String | Full position name (e.g. "Forward"). |
| `college_id` | Int64 | ESPN identifier for the athlete's college. |
| `current_team_id` | Int64 | ESPN team id of the athlete's current team. |
| `headshot_href` | String | URL of the athlete's ESPN headshot image. |
| `experience_years` | Int64 | Seasons of collegiate eligibility used, as a string. |
| `status_id` | Int64 | ESPN identifier for the athlete's roster status. |
| `status_name` | String | Athlete's roster status (e.g. "Active"). |
| `status_type` | String | Athlete's roster status code. |
| `draft_year` | Int64 | Year the athlete was drafted, when applicable. |
| `draft_round` | Int64 | Round in which the athlete was drafted, when applicable. |
| `draft_selection` | Int64 | Overall pick number at which the athlete was drafted. |
| `active` | Boolean | Whether the athlete was active for the game. |

## Coverage

| season | rows | built (UTC) |
|---:|---:|---|
| 2026 | 9,870 | 2026-08-24 02:29:38 UTC |
