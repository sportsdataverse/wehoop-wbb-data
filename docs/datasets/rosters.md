# `rosters`



| | |
|---|---|
| **Builder** | [`python/espn_wbb_07_rosters_creation.py`](../../python/espn_wbb_07_rosters_creation.py) |
| **Release tag** | [`espn_womens_college_basketball_rosters`](https://github.com/sportsdataverse/sportsdataverse-data/releases/tag/espn_womens_college_basketball_rosters) |
| **File stem** | `rosters_{season}.{parquet,csv,rds}` |
| **Seasons built** | 2026–2026 (12 seasons) |
| **Last published** | 2026-07-26 (newest release asset) |
| **Tag created** | 2026-05-11 |
| **Release assets** | 8 |

## Automation

`.github/workflows/daily_wbb.yml` — cron 07:00 UTC in season (late Oct, Nov–Dec, Jan–Mar, early Apr), plus `repository_dispatch` from `wehoop-wbb-raw`. Runs `scripts/daily_wbb_data_processor.sh` (`-l python` default, `-l R` rollback).

## Columns

| col_name | type | description |
|---|---|---|
| `season` | Int64 | Season identifier from the input games frame (named `sim` instead when the input used a `sim` column). |
| `team_id` | Int64 | 247Sports signed-institution team key as a string (falls back to the committed institution when unsigned). |
| `team_slug` | String |  |
| `team_abbreviation` | String | Team abbreviation. |
| `team_display_name` | String |  |
| `team_short_display_name` | String |  |
| `team_color` | String |  |
| `team_alternate_color` | String |  |
| `team_logo` | String |  |
| `athlete_id` | Int64 | ESPN numeric identifier for the athlete. |
| `uid` | String | ESPN universal id for the athlete. |
| `guid` | String |  |
| `full_name` | String | Full name of the program (school plus nickname). |
| `display_name` | String | Full display name of the team (e.g. 'Los Angeles Lakers'). |
| `short_name` | String | Abbreviated name (typically first initial plus last name). |
| `first_name` | String | Given name of the transfer player. |
| `last_name` | String | Family (surname) of the transfer player. |
| `jersey` | String | Athlete's jersey number as a string. |
| `position_abbreviation` | String | Abbreviation of the ranked position (e.g. QB, EDGE). |
| `position_name` | String | Full position name (e.g. 'Point Guard', 'Goalkeeper'). |
| `position_id` | Int64 |  |
| `height` | String | Recruit height (formatted string, e.g. "6-2"). |
| `weight` | String | Player's listed weight in pounds. |
| `age` | String | Athlete age in years. |
| `date_of_birth` | String | Athlete date of birth (ISO 8601). |
| `birth_place_city` | String |  |
| `birth_place_state` | String |  |
| `birth_place_country` | String |  |
| `experience_years` | String |  |
| `experience_display_value` | String |  |
| `headshot_href` | String | URL of the quarterback's ESPN headshot image. |
| `headshot_alt` | String |  |
| `link_web` | String |  |
| `status_id` | Int64 |  |
| `status_name` | String |  |
| `status_type` | String |  |

## Coverage

| season | rows | built (UTC) |
|---:|---:|---|
| 2026 | 9,778 | 2026-05-17 08:32:54 UTC |
| 2026 | 9,778 | 2026-05-24 08:50:03 UTC |
| 2026 | 9,778 | 2026-05-30 08:32:53 UTC |
| 2026 | 9,778 | 2026-05-31 09:03:39 UTC |
| 2026 | 9,778 | 2026-06-07 09:10:47 UTC |
| 2026 | 9,778 | 2026-06-14 09:46:23 UTC |
| 2026 | 9,778 | 2026-06-21 10:07:31 UTC |
| 2026 | 9,778 | 2026-06-28 09:06:07 UTC |
| 2026 | 9,778 | 2026-07-05 09:09:20 UTC |
| 2026 | 9,778 | 2026-07-12 08:30:44 UTC |
| 2026 | 9,778 | 2026-07-19 08:37:16 UTC |
| 2026 | 9,778 | 2026-07-26 08:35:45 UTC |
