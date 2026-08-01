# `team_crosswalk`



| | |
|---|---|
| **Builder** | [`R/wbb_13_team_crosswalk_creation.R`](../../R/wbb_13_team_crosswalk_creation.R) |
| **Release tag** | [`wbb_crosswalk`](https://github.com/sportsdataverse/sportsdataverse-data/releases/tag/wbb_crosswalk) |
| **File stem** | `wbb_team_crosswalk_{season}.{parquet,csv,rds}` |
| **Seasons built** | — |
| **Last published** | — (newest release asset) |
| **Tag created** | — |
| **Release assets** | — |

## Automation

`.github/workflows/daily_wbb.yml` — cron 07:00 UTC in season (late Oct, Nov–Dec, Jan–Mar, early Apr), plus `repository_dispatch` from `wehoop-wbb-raw`. Runs `scripts/daily_wbb_data_processor.sh` (`-l python` default, `-l R` rollback).

## Columns

_R-only dataset; no Python schema model yet._

## Coverage

_No build manifest yet._
