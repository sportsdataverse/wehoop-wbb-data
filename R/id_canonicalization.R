# Id canonicalization for the R chain's PARQUET output -- the R-side mirror of
# python/wbb_data_build/ids.py.
#
# Why this exists: the weekly R/Python output-parity job compares the two
# pipelines and reported, on 2026-09-09,
#   game_id: R=Int32 python=Int64, team_id: R=Int32 python=Int64
# which is a join-key dtype disagreement -- a join across the two would match
# nothing. Python canonicalizes every id to Int64 at its single write boundary
# (ids.py, landed 2026-08-01, so that this repo's own datasets stop raising
# SchemaError when joined to each other). The retained R fallback chain never
# got that treatment. Python is canonical; this brings R in line.
#
# PARQUET ONLY, deliberately. sdv-py's rds writer (sportsdataverse/_rds.py)
# writes an Int64 column back as an R `integer` whenever the values fit int32
# -- "R has no 64-bit integer" -- and every ESPN id does fit. So Python is
# already asymmetric across formats on purpose, and the two pipelines' .rds
# output ALREADY agrees. Casting the whole frame instead of just the parquet
# argument would therefore invent a divergence rather than remove one, and
# would hand `wehoop::load_wbb_team_box()` consumers bit64 columns they would
# need bit64 attached to read. Cast at the arrow call, nowhere else.
#
# Not applied to the crosswalk stages (wbb_13/14/15_*_creation.R): Python sets
# canonicalize=False for all three, because their ids carry three different
# declared contracts (Int32 team ids beside String game/athlete ids) and
# widening them would break downstream joins against the released assets.

if (!requireNamespace("bit64", quietly = TRUE)) {
  stop("bit64 is required to write Int64 ids to parquet")
}

.wbb_id_to_int64 <- function(x, nm) {
  if (inherits(x, "integer64")) {
    return(x)
  }
  if (is.integer(x)) {
    return(bit64::as.integer64(x))
  }
  if (is.double(x)) {
    # Refusing a lossy cast matters more than performing one: a rounded id
    # yields a structurally valid frame that joins to the WRONG row, which is
    # strictly worse than an error. Same rule as ids.to_int64().
    nonnull <- x[!is.na(x)]
    if (length(nonnull) && any(nonnull != round(nonnull))) {
      stop(sprintf("lossy double->integer64 id cast on '%s'", nm))
    }
    return(bit64::as.integer64(x))
  }
  if (is.character(x)) {
    out <- suppressWarnings(bit64::as.integer64(x))
    if (sum(is.na(out)) > sum(is.na(x))) {
      stop(sprintf("non-numeric id value in '%s'", nm))
    }
    return(out)
  }
  stop(sprintf("column '%s' is not id-shaped (%s)", nm, paste(class(x), collapse = "/")))
}

#' Widen every id column to Int64 for a parquet write.
#'
#' An id column is one named exactly `id` or ending `_id` -- the same rule as
#' `ids.is_id_column()` on the Python side. Every other column is untouched.
canonicalize_ids <- function(df) {
  for (nm in names(df)) {
    if (!(nm == "id" || endsWith(nm, "_id"))) next
    df[[nm]] <- .wbb_id_to_int64(df[[nm]], nm)
  }
  df
}
