#!/usr/bin/env Rscript
# Serialize the Python-built parquet datasets to .rds and upload rds-only.
#
# R does ZERO reshaping here (design spec 2026-07-12 §5): the published .rds
# is byte-derived from the parity-passed parquet, so wehoop::load_wbb_*
# keeps its rds contract while Python (wbb_data_build) owns the reshape and
# publishes the parquet/csv assets itself.
#
# Usage: Rscript R/serialize_rds.R -s 2026 -e 2026 [--no-upload]
suppressPackageStartupMessages({
  library(arrow)
  library(glue)
  library(optparse)
  library(purrr)
})

option_list <- list(
  make_option(
    c("-s", "--start_year"),
    action = "store",
    default = wehoop:::most_recent_wbb_season(),
    type = "integer"
  ),
  make_option(
    c("-e", "--end_year"),
    action = "store",
    default = wehoop:::most_recent_wbb_season(),
    type = "integer"
  ),
  make_option(
    "--no-upload",
    action = "store_true",
    default = FALSE,
    dest = "no_upload",
    help = "serialize locally, skip the release upload"
  )
)
opt <- parse_args(OptionParser(option_list = option_list))

# dataset dir | file stem | release tag | pkg_function
# Mirrors wbb_data_build.config.REGISTRY exactly (tags are load-bearing).
T_ <- "espn_womens_college_basketball_"
DATASETS <- list(
  list("pbp",                 "play_by_play",        paste0(T_, "pbp"),                 "wehoop::load_wbb_pbp()"),
  list("schedules",           "wbb_schedule",        paste0(T_, "schedules"),           "wehoop::load_wbb_schedule()"),
  list("shots",               "shots",               paste0(T_, "shots"),               "wehoop::load_wbb_pbp()"),
  list("team_box",            "team_box",            paste0(T_, "team_boxscores"),      "wehoop::load_wbb_team_box()"),
  list("player_box",          "player_box",          paste0(T_, "player_boxscores"),    "wehoop::load_wbb_player_box()"),
  list("rosters",             "rosters",             paste0(T_, "rosters"),             "wehoop::load_wbb_rosters()"),
  list("player_season_stats", "player_season_stats", paste0(T_, "player_season_stats"), "wehoop::load_wbb_player_stats()"),
  list("player_core",         "player_core",         paste0(T_, "player_core"),         "wehoop::load_wbb_player_core()"),
  list("team_season_stats",   "team_season_stats",   paste0(T_, "team_season_stats"),   "wehoop::load_wbb_team_stats()"),
  list("standings",           "standings",           paste0(T_, "standings"),           "wehoop::load_wbb_standings()"),
  list("game_rosters",        "game_rosters",        paste0(T_, "game_rosters"),        "wehoop::load_wbb_pbp()"),
  list("officials",           "officials",           paste0(T_, "officials"),           "wehoop::load_wbb_pbp()")
)

retry_rate <- purrr::rate_backoff(pause_base = 1, pause_min = 1, max_times = 5)
any_failed <- FALSE

for (y in opt$s:opt$e) {
  for (d in DATASETS) {
    ds <- d[[1]]
    stem <- d[[2]]
    tag <- d[[3]]
    pkg_fn <- d[[4]]
    pq <- glue("wbb/{ds}/parquet/{stem}_{y}.parquet")
    if (!file.exists(pq)) {
      cli::cli_alert_info("{Sys.time()}: no parquet for {ds} {y}; skipping rds")
      next
    }
    ok <- tryCatch(
      {
        df <- arrow::read_parquet(pq)
        df <- wehoop:::make_wehoop_data(
          df,
          glue("ESPN WBB {ds} from wehoop data repository"),
          Sys.time()
        )
        dir.create(glue("wbb/{ds}/rds"), recursive = TRUE, showWarnings = FALSE)
        saveRDS(df, glue("wbb/{ds}/rds/{stem}_{y}.rds"))
        if (!opt$no_upload) {
          purrr::insistently(
            sportsdataversedata::sportsdataverse_save,
            rate = retry_rate,
            quiet = FALSE
          )(
            data_frame = df,
            file_name = glue("{stem}_{y}"),
            sportsdataverse_type = glue("{ds} data"),
            release_tag = tag,
            pkg_function = pkg_fn,
            file_types = c("rds"),
            .token = Sys.getenv("GITHUB_PAT")
          )
        }
        TRUE
      },
      error = function(e) {
        cli::cli_alert_warning(
          "{Sys.time()}: rds serialize failed for {ds} {y}: {e$message}"
        )
        FALSE
      }
    )
    if (!ok) any_failed <- TRUE
  }
}
if (any_failed) quit(status = 1)
