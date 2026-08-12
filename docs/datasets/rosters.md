# `rosters`



| | |
|---|---|
| **Builder** | [`python/espn_wbb_07_rosters_creation.py`](../../python/espn_wbb_07_rosters_creation.py) |
| **Release tag** | [`espn_womens_college_basketball_rosters`](https://github.com/sportsdataverse/sportsdataverse-data/releases/tag/espn_womens_college_basketball_rosters) |
| **File stem** | `rosters_{season}.{parquet,csv,rds}` |
| **Seasons built** | 2026 (1 season) |
| **Last published** | 2026-08-09 (newest release asset) |
| **Tag created** | 2026-05-11 |
| **Release assets** | 8 |

## Automation

`.github/workflows/daily_wbb.yml` — cron 07:00 UTC in season (late Oct, Nov–Dec, Jan–Mar, early Apr), plus `repository_dispatch` from `wehoop-wbb-raw`. Runs `scripts/daily_wbb_data_processor.sh` (`-l python` default, `-l R` rollback).

## Columns

| col_name | type | description |
|---|---|---|
| `season` | Int64 | Season end-year (2026 = the 2025-26 season). |
| `team_id` | Int64 | ESPN numeric identifier for the team. |
| `team_slug` | String | URL slug for the team on espn.com. |
| `team_abbreviation` | String | Team abbreviation (e.g. "UCLA"). |
| `team_display_name` | String | Full team name including nickname (e.g. "UCLA Bruins"). |
| `team_short_display_name` | String | Shortened team display name. |
| `team_color` | String | Primary team colour as a hex string, without the leading '#'. |
| `team_alternate_color` | String | Secondary team colour as a hex string, without the leading '#'. |
| `team_logo` | String | URL of the team's ESPN logo image. |
| `athlete_id` | Int64 | ESPN numeric identifier for the athlete. |
| `uid` | String | ESPN universal id for the entity (e.g. "s:40~l:54~t:26"). |
| `guid` | String | ESPN global GUID for the entity, stable across seasons. |
| `full_name` | String | Full name of the entity. |
| `display_name` | String | Full display name of the entity. |
| `short_name` | String | Abbreviated name (typically first initial plus surname). |
| `first_name` | String | Athlete's given name. |
| `last_name` | String | Athlete's family name. |
| `jersey` | String | Jersey number, as a string to preserve leading zeros. |
| `position_abbreviation` | String | Position abbreviation. |
| `position_name` | String | Full position name. |
| `position_id` | Int64 | ESPN identifier for the athlete's listed position. |
| `height` | String | Athlete's height in inches. |
| `weight` | String | Athlete's listed weight in pounds. |
| `age` | String | Athlete's age in years. |
| `date_of_birth` | String | Athlete's date of birth. |
| `birth_place_city` | String | City the athlete was born in. |
| `birth_place_state` | String | State or province the athlete was born in. |
| `birth_place_country` | String | Country the athlete was born in. |
| `experience_years` | String | Seasons of collegiate eligibility used, as a string. |
| `experience_display_value` | String | Class standing formatted for display (e.g. "Freshman"). |
| `headshot_href` | String | URL of the athlete's ESPN headshot image. |
| `headshot_alt` | String | Alt text for the athlete's headshot image. |
| `link_web` | String | URL of the athlete's ESPN profile page. |
| `status_id` | Int64 | ESPN identifier for the athlete's roster status. |
| `status_name` | String | Athlete's roster status (e.g. "Active"). |
| `status_type` | String | Athlete's roster status code. |

## Coverage

| season | rows | built (UTC) |
|---:|---:|---|
| 2026 | 9,778 | 2026-07-26 08:35:45 UTC |
