# `game_rosters`



| | |
|---|---|
| **Builder** | [`python/espn_wbb_11_game_rosters_creation.py`](../../python/espn_wbb_11_game_rosters_creation.py) |
| **Release tag** | [`espn_womens_college_basketball_game_rosters`](https://github.com/sportsdataverse/sportsdataverse-data/releases/tag/espn_womens_college_basketball_game_rosters) |
| **File stem** | `game_rosters_{season}.{parquet,csv,rds}` |
| **Seasons built** | 2004–2026 (5 seasons) |
| **Last published** | 2026-07-17 (newest release asset) |
| **Tag created** | 2026-05-11 |
| **Release assets** | 71 |

## Automation

`.github/workflows/daily_wbb.yml` — cron 07:00 UTC in season (late Oct, Nov–Dec, Jan–Mar, early Apr), plus `repository_dispatch` from `wehoop-wbb-raw`. Runs `scripts/daily_wbb_data_processor.sh` (`-l python` default, `-l R` rollback).

## Columns

| col_name | type | description |
|---|---|---|
| `season` | Int64 | Season identifier from the input games frame (named `sim` instead when the input used a `sim` column). |
| `game_id` | Int64 | Game identifier carried through from the input schedule. |
| `team_id` | Int64 | 247Sports signed-institution team key as a string (falls back to the committed institution when unsigned). |
| `team_slug` | String |  |
| `team_abbreviation` | String | Team abbreviation. |
| `team_display_name` | String |  |
| `home_away` | String |  |
| `athlete_id` | Int64 | ESPN numeric identifier for the athlete. |
| `athlete_uid` | String |  |
| `athlete_guid` | String |  |
| `athlete_display_name` | String |  |
| `athlete_short_name` | String |  |
| `athlete_first_name` | String |  |
| `athlete_last_name` | String |  |
| `athlete_jersey` | String |  |
| `athlete_position` | String |  |
| `athlete_headshot` | String |  |
| `starter` | Boolean |  |
| `did_not_play` | Boolean |  |
| `active` | Boolean |  |
| `ejected` | Boolean |  |
| `reason` | String |  |

## Coverage

| season | rows | built (UTC) |
|---:|---:|---|
| 2004 | 620 | 2026-07-16 22:08:47 UTC |
| 2005 | 1,181 | 2026-07-16 22:32:14 UTC |
| 2006 | 2,401 | 2026-07-16 23:49:14 UTC |
| 2007 | 5,024 | 2026-07-16 23:56:42 UTC |
| 2026 | 168,228 | 2026-05-30 09:15:56 UTC |
