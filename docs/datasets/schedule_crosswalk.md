# `schedule_crosswalk`



| | |
|---|---|
| **Builder** | [`python/espn_wbb_14_schedule_crosswalk_creation.py`](../../python/espn_wbb_14_schedule_crosswalk_creation.py) |
| **Release tag** | [`wbb_crosswalk`](https://github.com/sportsdataverse/sportsdataverse-data/releases/tag/wbb_crosswalk) |
| **File stem** | `wbb_schedule_crosswalk_{season}.{parquet,csv,rds}` |
| **Seasons built** | — |
| **Last published** | 2026-07-17 (newest release asset) |
| **Tag created** | 2026-06-13 |
| **Release assets** | 79 |

## Automation

`.github/workflows/daily_wbb.yml` — cron 07:00 UTC in season (late Oct, Nov–Dec, Jan–Mar, early Apr), plus `repository_dispatch` from `wehoop-wbb-raw`. Runs `scripts/daily_wbb_data_processor.sh` (`-l python` default, `-l R` rollback).

## Columns

_R-only dataset; no Python schema model yet._

## Coverage

_No build manifest yet._
