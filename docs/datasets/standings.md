# `standings`



| | |
|---|---|
| **Builder** | [`python/espn_wbb_10_standings_creation.py`](../../python/espn_wbb_10_standings_creation.py) |
| **Release tag** | [`espn_womens_college_basketball_standings`](https://github.com/sportsdataverse/sportsdataverse-data/releases/tag/espn_womens_college_basketball_standings) |
| **File stem** | `standings_{season}.{parquet,csv,rds}` |
| **Seasons built** | 2003–2026 (6 seasons) |
| **Last published** | — (newest release asset) |
| **Tag created** | — |
| **Release assets** | — |

## Automation

`.github/workflows/daily_wbb.yml` — cron 07:00 UTC in season (late Oct, Nov–Dec, Jan–Mar, early Apr), plus `repository_dispatch` from `wehoop-wbb-raw`. Runs `scripts/daily_wbb_data_processor.sh` (`-l python` default, `-l R` rollback).

## Columns

| col_name | type | description |
|---|---|---|
| `season` | Int64 | Season end-year (2026 = the 2025-26 season). |
| `group_id` | Int64 | ESPN group (conference) id the standings row belongs to. |
| `group_name` | String | Full conference name for the standings row. |
| `group_abbreviation` | String | Conference abbreviation (e.g. "aeast"). |
| `group_short_name` | String | Abbreviated conference name. |
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
| `stat_name` | String | Machine-readable statistic key (e.g. "gamesPlayed"). |
| `stat_display_name` | String | Statistic name formatted for display. |
| `stat_short_display_name` | String | Abbreviated statistic name. |
| `stat_description` | String | Human-readable description of the statistic. |
| `stat_abbreviation` | String | Statistic abbreviation (e.g. "OPP PPG"). |
| `stat_type` | String | Machine-readable standings statistic key (e.g. "avgpointsagainst"). |
| `display_value` | String | Statistic value formatted for display, as published by ESPN. |
| `value` | Float64 | Numeric value of the statistic. |

## Coverage

| season | rows | built (UTC) |
|---:|---:|---|
| 2003 | 26,558 | 2026-07-16 22:00:15 UTC |
| 2004 | 26,460 | 2026-07-16 22:07:11 UTC |
| 2005 | 26,544 | 2026-07-16 22:30:40 UTC |
| 2006 | 26,964 | 2026-07-16 23:47:41 UTC |
| 2007 | 27,216 | 2026-07-16 23:54:59 UTC |
| 2026 | 30,492 | 2026-05-30 08:36:33 UTC |
