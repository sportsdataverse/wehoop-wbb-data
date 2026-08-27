# Functional test for upsert_manifest_row() in R/manifest_upload_helper.R.
#
# Run: Rscript tests/test_manifest_upsert.R   (needs an R with data.table).
# Verified 2026-08-27 on this box: 4.6.0 and 4.6.1 have data.table, and
# 4.5.0 / 4.5.1 / 4.5.3 do NOT -- the reverse of what this note used to
# say. Check requireNamespace("data.table") rather than a pinned version.
#
# This exists because the first version of the helper silently destroyed
# history. It read:
#
#     prior <- prior[prior$season != season]
#
# Inside data.table's `[`, a bare `season` resolves to the COLUMN, not the
# function argument, so the filter was `prior$season != prior$season` --
# always FALSE. Every prior season was wiped and one row survived. Parsing
# cleanly proves nothing about that; only running it does.

suppressPackageStartupMessages(library(data.table))
source(file.path("R", "manifest_upload_helper.R"))

fail <- function(msg) {
  cat("FAIL:", msg, "\n")
  quit(status = 1)
}

row_for <- function(season, n) {
  data.frame(
    season           = as.integer(season),
    row_count        = as.integer(n),
    generated_at_utc = "2026-01-01 00:00:00 UTC",
    source_endpoint  = "test"
  )
}

tmp <- tempfile(fileext = ".csv")

# 1. First write creates the file.
upsert_manifest_row(tmp, row_for(2026, 100), 2026)
d <- fread(tmp)
if (nrow(d) != 1L) fail("first write should create exactly one row")

# 2. Re-writing the SAME season replaces it rather than appending.
upsert_manifest_row(tmp, row_for(2026, 200), 2026)
d <- fread(tmp)
if (nrow(d) != 1L) fail(paste("same season should not append; got", nrow(d), "rows"))
if (d[d$season == 2026]$row_count != 200L) fail("same season should take the newer row_count")

# 3. A DIFFERENT season is added, and the existing one survives. This is the
#    regression the column-masking bug broke.
upsert_manifest_row(tmp, row_for(2025, 50), 2025)
d <- fread(tmp)
if (nrow(d) != 2L) fail(paste("prior season must survive; got", nrow(d), "rows"))
if (!identical(sort(d$season), c(2025L, 2026L))) fail("both seasons must be present")

# 4. Output stays sorted by season.
if (!identical(d$season, sort(d$season))) fail("rows must be sorted by season")

# 5. Upserting again touches only the target season.
upsert_manifest_row(tmp, row_for(2026, 300), 2026)
d <- fread(tmp)
if (nrow(d) != 2L) fail("upsert must not change the row count for other seasons")
if (d[d$season == 2025]$row_count != 50L) fail("other seasons must be untouched")
if (d[d$season == 2026]$row_count != 300L) fail("target season must be updated")

unlink(tmp)

# 6. The row shape PRODUCTION actually passes. Every creation script builds
#    `source_endpoint` with glue::glue(), whose result is classed
#    c("glue", "character"); fwrite writes it as text and fread reads it back
#    as plain "character". So the file this function wrote is not bind-able
#    with the next row it is handed, and the second season of every manifest
#    died on:
#      Class attribute on column 4 of item 2 does not match with column 4 of
#      item 1
#    Cases 1-5 never caught it because they pass a plain "test" string --
#    a fixture that differs from production in precisely the attribute that
#    broke.
glue_row <- function(season, n) {
  data.frame(
    season           = as.integer(season),
    row_count        = as.integer(n),
    generated_at_utc = "2026-01-01 00:00:00 UTC",
    source_endpoint  = glue::glue("https://raw/{season}/<team_id>.json")
  )
}

tmp2 <- tempfile(fileext = ".csv")
upsert_manifest_row(tmp2, glue_row(2025, 10), 2025)
res <- tryCatch(
  {
    upsert_manifest_row(tmp2, glue_row(2026, 20), 2026)
    "ok"
  },
  error = function(e) conditionMessage(e)
)
if (!identical(res, "ok")) fail(paste("glue-built source_endpoint must bind; got:", res))
d2 <- fread(tmp2)
if (nrow(d2) != 2L) fail(paste("glue rows: expected 2 seasons, got", nrow(d2)))
if (!identical(class(d2$source_endpoint), "character")) {
  fail("source_endpoint must round-trip as plain character")
}
unlink(tmp2)
cat("PASS: upsert_manifest_row keeps one row per season, preserves history,
")
cat("      and binds the glue-classed rows the creation scripts pass
")
