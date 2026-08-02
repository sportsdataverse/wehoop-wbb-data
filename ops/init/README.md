One-time bootstrap scripts; run manually from the repo root (all paths inside are repo-root-relative).
`Rscript ops/init/0000_create_wehoop_releases_init.R` idempotently creates this repo's release tags on sportsdataverse-data.
`Rscript ops/init/0001_push_existing_release_data.R` backfills already-built `wbb/*/rds/` outputs onto those tags.
