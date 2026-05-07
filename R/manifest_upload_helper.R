# Shared helper -- upload the per-dataset manifest CSV to its release tag.
#
# Each creation script writes per-season rows into a CSV
# (`<dataset_dir>/wbb_<dataset_short>_in_data_repo.csv`) with columns
# `season`, `row_count`, `generated_at_utc`, `source_endpoint`. After the
# per-season loop is finished, source this helper and call
# `upload_wbb_manifest()` so the manifest CSV gets uploaded to the same
# release tag as the data files (overwriting on each run, last write wins
# per season).
#
# The function is intentionally tryCatch-wrapped at the call site so a
# manifest-upload failure does not abort the run -- the per-season data is
# what matters.

upload_wbb_manifest <- function(manifest_path,
                                release_tag,
                                file_name,
                                sportsdataverse_type = "manifest",
                                pkg_function         = NA_character_) {
  if (!file.exists(manifest_path)) {
    return(invisible(NULL))
  }
  manifest_df <- readr::read_csv(manifest_path, show_col_types = FALSE)
  if (nrow(manifest_df) == 0) return(invisible(NULL))
  manifest_df <- manifest_df %>%
    dplyr::distinct(.data$season, .keep_all = TRUE) %>%
    dplyr::arrange(.data$season)

  save_manifest <- purrr::insistently(
    sportsdataversedata::sportsdataverse_save,
    rate = purrr::rate_backoff(pause_base = 1, pause_min = 1, max_times = 5),
    quiet = FALSE
  )
  save_manifest(
    data_frame           = manifest_df,
    file_name            = file_name,
    sportsdataverse_type = sportsdataverse_type,
    release_tag          = release_tag,
    pkg_function         = pkg_function,
    file_types           = c("csv"),
    .token               = Sys.getenv("GITHUB_PAT")
  )
  invisible(manifest_df)
}
