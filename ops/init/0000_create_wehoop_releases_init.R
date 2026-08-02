# Create the GitHub releases on sportsdataverse/sportsdataverse-data that
# the espn_wbb_*_creation.R parsers upload artifacts to via
# piggyback::pb_upload. Each release is created with an empty body; assets
# land later during the daily/weekly parser runs.
#
# Source-specific: this repo (wehoop-wbb-data) owns the
# espn_womens_college_basketball_* tags. The sister init scripts in
# wehoop-wnba-data and wehoop-wnba-stats-data own their own source's tags.
#
# Idempotent: a release that already exists is skipped, not re-created.
# Re-run this any time a new espn_wbb_*_creation.R script lands.

create_release <- function(tag, body) {
  tryCatch(
    piggyback::pb_release_create(
      repo = "sportsdataverse/sportsdataverse-data",
      tag  = tag,
      name = tag,
      body = body,
      .token = Sys.getenv("GITHUB_PAT")
    ),
    error = function(e) {
      # piggyback can wrap "already exists" across a newline depending on tag
      # length / cli width; collapse whitespace before matching so we don't
      # miss the line-broken variant.
      msg <- gsub("\\s+", " ", conditionMessage(e))
      if (grepl("already exists|already_exists|Validation Failed", msg, ignore.case = TRUE)) {
        message("Skipping (already exists): ", tag)
      } else {
        stop(e)
      }
    }
  )
}

#--- ESPN Women's College Basketball -----------------------------------------

# Original 4 (pre-Phase 1; pre-existing on sportsdataverse-data)
create_release(
  "espn_womens_college_basketball_schedules",
  "NCAA Women's College Basketball Schedules Data (from ESPN)"
)
create_release(
  "espn_womens_college_basketball_team_boxscores",
  "NCAA Women's College Basketball Team Boxscores Data (from ESPN)"
)
create_release(
  "espn_womens_college_basketball_player_boxscores",
  "NCAA Women's College Basketball Player Boxscores Data (from ESPN)"
)
create_release(
  "espn_womens_college_basketball_pbp",
  "NCAA Women's College Basketball Play-by-Play Data (from ESPN)"
)

# Phase 1-6 additions (per-season + per-game). No draft for women's college.
create_release(
  "espn_womens_college_basketball_rosters",
  "NCAA Women's College Basketball Team Rosters Data (from ESPN)"
)
create_release(
  "espn_womens_college_basketball_player_season_stats",
  "NCAA Women's College Basketball Player Season Stats Data (from ESPN)"
)
create_release(
  "espn_womens_college_basketball_team_season_stats",
  "NCAA Women's College Basketball Team Season Stats Data (from ESPN)"
)
create_release(
  "espn_womens_college_basketball_standings",
  "NCAA Women's College Basketball Standings Data (from ESPN)"
)
create_release(
  "espn_womens_college_basketball_shots",
  "NCAA Women's College Basketball Shots Data (from ESPN)"
)
create_release(
  "espn_womens_college_basketball_game_rosters",
  "NCAA Women's College Basketball Game Rosters Data (from ESPN)"
)
create_release(
  "espn_womens_college_basketball_officials",
  "NCAA Women's College Basketball Officials Data (from ESPN)"
)
