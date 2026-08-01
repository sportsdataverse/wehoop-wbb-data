#!/bin/bash
# Compile wehoop-wbb-data datasets, per season (Python-first cutover).
#
# The 11 raw-derived datasets are built by `wbb_data_build` (parity-validated
# port of espn_wbb_01..09). Build order matters: shots project the built pbp
# parquet; schedules stamp flags from the built pbp/team_box/player_box
# parquets. Crosswalks (wbb_11-13) stay on R (live ESPN+Torvik+Fox inputs),
# and R also serializes every Python parquet to .rds (wehoop's load_* reads
#
# Usage: bash scripts/daily_wbb_data_processor.sh -s 2026 -e 2026
set -uo pipefail

# -l selects the language for the 12 raw-derived datasets. Python is the
# production default; `-l R` is the rollback path that used to live in a
# separate daily_wbb_R_processor.sh. One script, so the two paths cannot drift
# in season handling, logging or the load-bearing commit format.
while getopts s:e:l: flag; do
  case "${flag}" in
    s) START_YEAR=${OPTARG};;
    e) END_YEAR=${OPTARG};;
    l) LANG_MODE=${OPTARG};;
    *) echo "usage: $0 -s <start> [-e <end>] [-l python|R]" >&2; exit 2;;
  esac
done
END_YEAR=${END_YEAR:-$START_YEAR}
LANG_MODE=${LANG_MODE:-python}
case "$LANG_MODE" in
  python|R) ;;
  *) echo "::error ::unknown -l '$LANG_MODE' (expected python or R)" >&2; exit 2;;
esac

# The 58GB raw repo can't be checked out in CI -- read it over HTTP like the
# R pipeline did (per-run cache under .wbb_raw_cache/, gitignored).
export WEHOOP_WBB_RAW_ROOT="${WEHOOP_WBB_RAW_ROOT:-https://raw.githubusercontent.com/sportsdataverse/wehoop-wbb-raw/main}"

# Scrape-log conventions: unbuffered + utf-8 so wbb_data_build's timestamped
# log lines land in the Actions console AND the tee'd season logfile live.
export PYTHONUNBUFFERED=1
export PYTHONIOENCODING=utf-8

# Dependency order: pbp/team_box/player_box first (schedules reads their
# game-id sets; shots read the pbp parquet), then the rest.
PY_DATASETS="pbp team_box player_box player_core schedules shots rosters player_season_stats team_season_stats standings game_rosters officials"
R_CROSSWALKS=(R/wbb_13_team_crosswalk_creation.R R/wbb_14_schedule_crosswalk_creation.R R/wbb_15_player_crosswalk_creation.R)
# The `-l R` rollback path. R has no counterpart for player_core (04),
# schedules (05) or shots (06) -- hence the gaps, which are deliberate.
R_DATASETS=(
  R/espn_wbb_01_pbp_creation.R
  R/espn_wbb_02_team_box_creation.R
  R/espn_wbb_03_player_box_creation.R
  R/espn_wbb_07_rosters_creation.R
  R/espn_wbb_08_player_season_stats_creation.R
  R/espn_wbb_09_team_season_stats_creation.R
  R/espn_wbb_10_standings_creation.R
  R/espn_wbb_11_game_rosters_creation.R
  R/espn_wbb_12_officials_creation.R
)

mkdir -p logs
ANY_FAILED=0
for i in $(seq "${START_YEAR}" "${END_YEAR}"); do
  LOGFILE="logs/wehoop_wbb_data_logfile_${i}.log"
  TMPLOG=$(mktemp "/tmp/wehoop_wbb_data_${i}.XXXXXX.log")
  # Tee inside the block writes to /tmp (untracked) so the `git pull` calls
  # don't trip over their own log output being written to a tracked file.
  {
    git pull >/dev/null
    git config --local user.email "action@github.com"
    git config --local user.name "Github Action"
    SEASON_RC=0

    # ::group:: markers collapse each dataset in the Actions UI; in the tee'd
    # season logfile they read as plain section headers.
    run_py() {
      local ds="$1"
      echo "::group::wbb_data_build $ds $i"
      # Packaging moved to the repo root, so no `cd python` and no ../wbb.
      uv run python -m wbb_data_build --dataset "$ds" --base wbb -s "$i" -e "$i" --publish || {
        rc=$?; echo "::warning ::wbb_data_build $ds for season $i exited with code $rc"; SEASON_RC=$rc
      }
      echo "::endgroup::"
    }
    run_r() {
      local script="$1"
      echo "::group::$script $i"
      Rscript "$script" -s "$i" -e "$i" || {
        rc=$?; echo "::warning ::$script for season $i exited with code $rc"; SEASON_RC=$rc
      }
      echo "::endgroup::"
    }

    if [ "$LANG_MODE" = "R" ]; then
      for SCRIPT in "${R_DATASETS[@]}"; do run_r "$SCRIPT"; done
    else
      for ds in $PY_DATASETS; do run_py "$ds"; done
    fi

    # Crosswalks are R in BOTH modes: they need Fox + Bart Torvik surfaces
    # sdv-py does not carry yet.
    for SCRIPT in "${R_CROSSWALKS[@]}"; do run_r "$SCRIPT"; done

    # Last: the schedule master, games_in_data_repo manifest and coverage
    # index, which union the season schedules AFTER every dataset above has
    # been built -- the in_* flags only mean anything once the compilations
    # they describe exist.
    echo "::group::schedule master $i"
    uv run python python/espn_wbb_99_schedule_master_creation.py || {
      rc=$?; echo "::warning ::schedule master exited with code $rc"; SEASON_RC=$rc
    }
    echo "::endgroup::"

    echo "RSCRIPT_RC=$SEASON_RC" > "/tmp/_rc_${i}"
    # Grep-able terminal line for the season logfile (scrape-log convention).
    echo "season $i EXIT=$SEASON_RC"
    # Commit whatever datasets succeeded even if one step errored -- the
    # per-dataset tryCatch/warning handling keeps partial output usable.
    git pull >/dev/null
    git add wbb/* >/dev/null 2>&1 || true
    git commit -m "WBB Data update (Start: $i End: $i)" || echo "No changes to commit"
    git pull >/dev/null
    git push >/dev/null
  } 2>&1 | tee "$TMPLOG"

  RSCRIPT_RC=$(sed 's/RSCRIPT_RC=//' "/tmp/_rc_${i}" 2>/dev/null); rm -f "/tmp/_rc_${i}"
  cp "$TMPLOG" "$LOGFILE"
  git pull --rebase >/dev/null || true
  git add "$LOGFILE"
  git commit -m "WBB Data log update (Start: $i End: $i)" >/dev/null || echo "No log changes to commit"
  git push >/dev/null
  rm -f "$TMPLOG"
  if [ "${RSCRIPT_RC:-0}" != "0" ]; then
    echo "::error ::At least one creation step for season $i exited with code $RSCRIPT_RC"
    ANY_FAILED=1
  fi
done

# ---- Run summary: updated releases + remaining warnings/errors ----
uv run python -m wbb_data_build.summary -s "$START_YEAR" -e "$END_YEAR" || true
[ "${ANY_FAILED:-0}" = "0" ] || exit 1
