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
| `season` | Int64 | Season end-year (2026 = the 2025-26 season). |
| `game_id` | Int64 | ESPN game identifier; the join key across every per-game dataset. Int64. |
| `team_id` | Int64 | ESPN numeric identifier for the team. |
| `team_slug` | String | URL slug for the team on espn.com. |
| `team_abbreviation` | String | Team abbreviation (e.g. "UCLA"). |
| `team_display_name` | String | Full team name including nickname (e.g. "UCLA Bruins"). |
| `home_away` | String | Whether the athlete's team was the home or away side. |
| `athlete_id` | Int64 | ESPN numeric identifier for the athlete. |
| `athlete_uid` | String | ESPN universal id for the athlete (e.g. "s:40~l:54~a:5315009"). |
| `athlete_guid` | String | ESPN global GUID for the athlete, stable across seasons. |
| `athlete_display_name` | String | Athlete's full display name. |
| `athlete_short_name` | String | Athlete's abbreviated name (first initial plus surname). |
| `athlete_first_name` | String | Athlete's given name. |
| `athlete_last_name` | String | Athlete's family name. |
| `athlete_jersey` | String | Athlete's jersey number, as a string to preserve leading zeros. |
| `athlete_position` | String | Athlete's position abbreviation. |
| `athlete_headshot` | String | URL of the athlete's ESPN headshot image. |
| `starter` | Boolean | Whether the athlete started the game. |
| `did_not_play` | Boolean | Whether the athlete was available but did not play. |
| `active` | Boolean | Whether the athlete was active for the game. |
| `ejected` | Boolean | Whether the athlete was ejected. |
| `reason` | String | ESPN's stated reason the athlete did not play, when given. |

## Coverage

| season | rows | built (UTC) |
|---:|---:|---|
| 2004 | 620 | 2026-07-16 22:08:47 UTC |
| 2005 | 1,181 | 2026-07-16 22:32:14 UTC |
| 2006 | 2,401 | 2026-07-16 23:49:14 UTC |
| 2007 | 5,024 | 2026-07-16 23:56:42 UTC |
| 2026 | 168,228 | 2026-05-30 09:15:56 UTC |
