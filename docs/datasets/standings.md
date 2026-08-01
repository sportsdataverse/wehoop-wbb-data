# `standings`



| | |
|---|---|
| **Builder** | [`python/espn_wbb_10_standings_creation.py`](../../python/espn_wbb_10_standings_creation.py) |
| **Release tag** | [`espn_womens_college_basketball_standings`](https://github.com/sportsdataverse/sportsdataverse-data/releases/tag/espn_womens_college_basketball_standings) |
| **File stem** | `standings_{season}.{parquet,csv,rds}` |
| **Seasons built** | 2003–2026 (6 seasons) |
| **Last published** | 2026-07-17 (newest release asset) |
| **Tag created** | 2026-05-11 |
| **Release assets** | 68 |

## Automation

`.github/workflows/daily_wbb.yml` — cron 07:00 UTC in season (late Oct, Nov–Dec, Jan–Mar, early Apr), plus `repository_dispatch` from `wehoop-wbb-raw`. Runs `scripts/daily_wbb_data_processor.sh` (`-l python` default, `-l R` rollback).

## Columns

| col_name | type | description |
|---|---|---|
| `season` | Int64 | Season identifier from the input games frame (named `sim` instead when the input used a `sim` column). |
| `group_id` | Int64 |  |
| `group_name` | String |  |
| `group_abbreviation` | String |  |
| `group_short_name` | String |  |
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
| `stat_name` | String |  |
| `stat_display_name` | String |  |
| `stat_short_display_name` | String |  |
| `stat_description` | String |  |
| `stat_abbreviation` | String |  |
| `stat_type` | String |  |
| `display_value` | String |  |
| `value` | Float64 | A class year for which the 247Sports RDB has data for the sport. |

## Coverage

| season | rows | built (UTC) |
|---:|---:|---|
| 2003 | 26,558 | 2026-07-16 22:00:15 UTC |
| 2004 | 26,460 | 2026-07-16 22:07:11 UTC |
| 2005 | 26,544 | 2026-07-16 22:30:40 UTC |
| 2006 | 26,964 | 2026-07-16 23:47:41 UTC |
| 2007 | 27,216 | 2026-07-16 23:54:59 UTC |
| 2026 | 30,492 | 2026-05-30 08:36:33 UTC |
