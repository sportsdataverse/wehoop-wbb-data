# `player_season_stats`



| | |
|---|---|
| **Builder** | [`python/espn_wbb_08_player_season_stats_creation.py`](../../python/espn_wbb_08_player_season_stats_creation.py) |
| **Release tag** | [`espn_womens_college_basketball_player_season_stats`](https://github.com/sportsdataverse/sportsdataverse-data/releases/tag/espn_womens_college_basketball_player_season_stats) |
| **File stem** | `player_season_stats_{season}.{parquet,csv,rds}` |
| **Seasons built** | 2006–2026 (3 seasons) |
| **Last published** | 2026-07-17 (newest release asset) |
| **Tag created** | 2026-05-11 |
| **Release assets** | 61 |

## Automation

`.github/workflows/daily_wbb.yml` — cron 07:00 UTC in season (late Oct, Nov–Dec, Jan–Mar, early Apr), plus `repository_dispatch` from `wehoop-wbb-raw`. Runs `scripts/daily_wbb_data_processor.sh` (`-l python` default, `-l R` rollback).

## Columns

| col_name | type | description |
|---|---|---|
| `season` | Int64 | Season end-year (2026 = the 2025-26 season). |
| `athlete_id` | Int64 | ESPN numeric identifier for the athlete. |
| `athlete_display_name` | String | Athlete's full display name. |
| `athlete_first_name` | String | Athlete's given name. |
| `athlete_last_name` | String | Athlete's family name. |
| `athlete_position_abbreviation` | String | Athlete's position abbreviation (e.g. "F"). |
| `athlete_jersey` | String | Athlete's jersey number, as a string to preserve leading zeros. |
| `team_id` | Int64 | ESPN numeric identifier for the team. |
| `team_display_name` | String | Full team name including nickname (e.g. "UCLA Bruins"). |
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
| 2006 | 201 | 2026-07-16 23:47:34 UTC |
| 2007 | 2,553 | 2026-07-16 23:54:52 UTC |
| 2026 | 41,919 | 2026-05-30 08:34:52 UTC |
