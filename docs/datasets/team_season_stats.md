# `team_season_stats`



| | |
|---|---|
| **Builder** | [`python/espn_wbb_09_team_season_stats_creation.py`](../../python/espn_wbb_09_team_season_stats_creation.py) |
| **Release tag** | [`espn_womens_college_basketball_team_season_stats`](https://github.com/sportsdataverse/sportsdataverse-data/releases/tag/espn_womens_college_basketball_team_season_stats) |
| **File stem** | `team_season_stats_{season}.{parquet,csv,rds}` |
| **Seasons built** | 2026 (1 season) |
| **Last published** | 2026-08-24 (newest release asset) |
| **Tag created** | 2026-05-11 |
| **Release assets** | 49 |

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
| `category` | String | Statistic grouping the row belongs to (e.g. "averages", "totals"). |
| `stat_label` | String | Short statistic label (e.g. "GP"). |
| `stat_name` | String | Machine-readable statistic key (e.g. "gamesPlayed"). |
| `stat_display_name` | String | Statistic name formatted for display. |
| `stat_description` | String | Human-readable description of the statistic. |
| `display_value` | String | Statistic value formatted for display, as published by ESPN. |
| `value` | Float64 | Numeric value of the statistic. |

## Coverage

| season | rows | built (UTC) |
|---:|---:|---|
| 2026 | 25,740 | 2026-08-24 02:31:30 UTC |
