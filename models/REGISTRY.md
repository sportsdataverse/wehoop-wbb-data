# Model registry

One row per model surface this repo operates (Track C step 1). The WP model
itself is trained and bundled in **sdv-py** (the WBB rule-era WP suite); this
repo's surface is the ENRICHMENT — applying it to the published season pbp in
place, which is how the model reaches consumers (`in_published_data` = the
`espn_womens_college_basketball_pbp` assets themselves).
`tests/test_model_registry.py` keeps this table in lockstep.

| model | artifact(s) | release tag | training data | fitting script | gates at publish | last retrain | cadence |
|---|---|---|---|---|---|---|---|
| WBB per-play win probability (enrichment of the published pbp) | WP columns added in place to `play_by_play_{season}` assets, every original column preserved. Contract 2003–2026; **measured on the release 2026-09-01: only 2024–2026 carry the columns** — every earlier season sampled (2004, 2008, 2012, 2015, 2016, 2020) lost them to the 2026-08 history republish and awaits `wbb_model_03_wp_enrich -s 2003 -e 2023` | `espn_womens_college_basketball_pbp` (no separate model tag) | sdv-py WBB WP training corpus (rule-era models; WBB is HALVES before 2016 — inherited caveat) | `python/wbb_model_03_wp_enrich.py` (wraps `wbb_data_build/wp_enrich.py`) via `scripts/daily_wbb_data_processor.sh` (the pbp asset's ONLY publisher -- the pbp build stage writes the tree and never uploads; the enrichment reads pbp/schedules/team_box from the tree, appends the WP columns, and publishes parquet+csv+rds) | oracle gates live with the model in sdv-py; enrichment invariant: every original column preserved and the row count unchanged; **publish guard** `publish.assert_wp_enriched` (asserted on the parquet FILE about to upload, by every caller incl. dry runs) refuses a pbp asset missing `pregame_home_prob`/`home_win_prob` or below a 0.999 finite-rate floor -- observed 2026-09-01: 1.0 on 2024/2025/2026 (2026 = 2,824,090 plays, 0 nulls, 0 NaN), while the earlier seasons had lost the columns entirely (the strip incident; the guard would have refused it) | model: see sdv-py; enrichment re-applied per run | in-season daily 13:00 UTC (Nov–Apr, `wbb_models_cron.yml`) |

Note: the fitted WP boosters are registered where they are trained (sdv-py);
this registry deliberately covers only what this repo owns — the enrichment
op and its schedule.

## Publish gates & derived columns (added 2026-09-01; every constant cites the observation that set it)

- **`wbb_ratings` — absolute level-band gate** (`wbb_model_publish.builders.assert_ratings_level`), the scale
  check beside sdv-py's rank (Spearman) gates, which are blind to any monotone rescale. Over the qualified subset
  (teams with `games >= 10` — the D1 core; the full frame carries every opponent ever seen), the season must have
  mean `adj_o` in [85, 105], mean `adj_d` in [80, 100], mean `adj_em` in [-12, 12], sd `adj_em` in [14, 28], mean
  `adj_tempo` in [64, 78], and no non-finite value (checked before the applicability floor); the band check applies
  once >= 150 teams qualify, logged as not-applied below that. Observed on the published 2017–2026 assets (the
  full-coverage era) + 2024/2025/2026 in-season engine snapshots: qualified teams 333–363 (151+ from ~Dec 10–20),
  mean adj_o 91.9–97.6, mean adj_d 86.95–94.2, mean adj_em −1.2–10.6, sd adj_em 18.1–23.1, mean adj_tempo 69.9–72.6.
  **Deliberate consequences, recorded rather than papered over:** `wbb_ratings_2015.parquet` (335/335 teams NaN) is
  refused; the 2008 asset (158 core teams, mean adj_o 119.4, mean adj_tempo 54.5 — the pre-2013 box schema
  under-counts possessions) is refused; 2009–2016 (45–101 core teams) sit below the applicability floor. These are
  inputs to repair, not reasons to widen a band. Per-season record lands in the card (`gates_by_season`).
- **`wbb_player_value` — additive `qualified` flag** (`min >= 300`; `builders.QUALIFIED_MIN_MINUTES`), never a
  filter: every published column and row is preserved. Derived from the published 2014–2026 assets (finite rows;
  2015 is entirely NaN — see below): sd(box_bpm) by minutes bin 7.84 (0–25) → 5.01 (100–150) → 4.69 (250–300) →
  4.59 (300–350) → 4.51 (600–800) → 4.50 (800–1000); 300 is the first bin within 2% of the 600–800 plateau (the MBB
  twin lands on the same floor at 10%); same-player YoY r 0.54 (all) / 0.818 (>= 300) / 0.830 (>= 500); >= 300 keeps
  88.1% of 2026 minutes (36.3% of rows). The engine's own fit floor (artifact `min_minutes` = 150) governs team-sum
  weights only.
- **`wbb_player_value_coefficients.json`** (additive asset on the same tag; `builders.write_player_value_coefficients`):
  the fitted box-BPM artifact — 16 `feature_cols`, `obpm_coef`/`dbpm_coef` as [intercept, *slopes] on standardized
  z-clipped features (so |slope| = BPM per SD = coefficient importance), `feature_mean`/`feature_sd`, `lambda_o`/`lambda_d`
  (3/3), `min_minutes` 150, `z_clip` 4, `train_seasons` [2025, 2026] — plus the sportsdataverse version, the artifact's
  canonical-JSON sha256 and the write time.
- **Known data gaps (not gate failures):** `wbb_ratings_2015` is all-NaN, and it propagates — all 974 rows of
  `wbb_player_value_2015` carry a NaN box BPM. Repair is upstream (engine/inputs), then a republish.
- **`espn_womens_college_basketball_pbp` — WP publish guard**: see the row above (`publish.assert_wp_enriched`).

## Operability (Track C steps 2–6)

- `models/manifest.yaml` — single home for the model/stage list (guarded by `tests/test_model_manifest.py`).
- One model = one numbered pipeline, flat in `python/` beside the data stages; run subsets with `scripts/wbb_models.sh`.
- Compute-on-demand / enrichment surfaces: no fitted artifacts to commit, no fingerprint skip (living upstream inputs), card sidecars carry per-publish metadata.
- `wbb_ratings` + `wbb_player_value` rows: see `models/manifest.yaml` (stages 01/02 wrap `wbb_model_publish ratings` / `player-value`, wired via `wbb_models_cron.yml`); engines + gates live in sdv-py, card sidecars per publish.
