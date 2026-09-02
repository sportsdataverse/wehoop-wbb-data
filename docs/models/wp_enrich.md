# WBB in-game win probability — pbp enrichment


The WBB rule-era win-probability suite (trained, bundled, and
oracle-gated in sdv-py) is applied **in place** to every published
season of `espn_womens_college_basketball_pbp`: `home_win_prob` and the
pregame prior (`pregame_home_prob`) are added to each play with every
original column preserved. The published pbp itself is how the model
reaches consumers — there is no separate WP asset to fall out of sync
with the plays.

The model is an XGBoost classifier over game state — score margin,
seconds left (and its square root), the pregame logit, and possession —
fit on one recent season. Operationally the enrichment **is** the pbp
publisher: `scripts/daily_wbb_data_processor.sh` builds the plain season
pbp into the tree and never uploads it; stage `wbb_model_03_wp_enrich`
reads the tree pbp/schedules/team_box, appends the two columns and
publishes parquet+csv+rds; and `wbb_data_build.publish` refuses any pbp
parquet without finite WP columns, asserted on the file about to upload.
That design closes a recorded incident: the old
publish-plain-then-re-enrich order stripped the columns off the release
on every nightly, and the 2026-08 whole-history republish left only the
in-season seasons enriched — measured 2026-09-01, 2024–2026 carry the
columns and every earlier season sampled (2004, 2008, 2012, 2015, 2016,
2020) does not. Until those seasons are republished, this document
computes the holdout era’s probabilities itself and says so.

This document is the model’s **out-of-band evaluation**: it downloads a
full published season at render time and holds the in-game probabilities
against each game’s realized outcome — first in-era, then for an era the
booster never saw. If the enrichment ever regressed, went stale, or was
stripped, the calibration sections below would show it on the next
render.

## Evaluation data

<div id="eztbvnsliq" style="padding-left:0px;padding-right:0px;padding-top:10px;padding-bottom:10px;overflow-x:auto;overflow-y:auto;width:auto;height:auto;">
<style>
#eztbvnsliq table {
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Helvetica Neue', 'Fira Sans', 'Droid Sans', Arial, sans-serif;
          -webkit-font-smoothing: antialiased;
          -moz-osx-font-smoothing: grayscale;
        }
&#10;#eztbvnsliq thead, tbody, tfoot, tr, td, th { border-style: none; }
 tr { background-color: transparent; }
#eztbvnsliq p { margin: 0; padding: 0; }
 #eztbvnsliq .gt_table { display: table; border-collapse: collapse; line-height: normal; margin-left: auto; margin-right: auto; color: #333333; font-size: 16px; font-weight: normal; font-style: normal; background-color: #FFFFFF; width: auto; border-top-style: solid; border-top-width: 2px; border-top-color: #A8A8A8; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #A8A8A8; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; }
 #eztbvnsliq .gt_caption { padding-top: 4px; padding-bottom: 4px; }
 #eztbvnsliq .gt_title { color: #333333; font-size: 125%; font-weight: initial; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; border-bottom-color: #FFFFFF; border-bottom-width: 0; }
 #eztbvnsliq .gt_subtitle { color: #333333; font-size: 85%; font-weight: initial; padding-top: 3px; padding-bottom: 5px; padding-left: 5px; padding-right: 5px; border-top-color: #FFFFFF; border-top-width: 0; }
 #eztbvnsliq .gt_heading { background-color: #FFFFFF; text-align: center; border-bottom-color: #FFFFFF; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; }
 #eztbvnsliq .gt_bottom_border { border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; }
 #eztbvnsliq .gt_col_headings { border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; }
 #eztbvnsliq .gt_col_heading { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: normal; text-transform: inherit; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; vertical-align: bottom; padding-top: 5px; padding-bottom: 5px; padding-left: 5px; padding-right: 5px; overflow-x: hidden; }
 #eztbvnsliq .gt_column_spanner_outer { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: normal; text-transform: inherit; padding-top: 0; padding-bottom: 0; padding-left: 4px; padding-right: 4px; }
 #eztbvnsliq .gt_column_spanner_outer:first-child { padding-left: 0; }
 #eztbvnsliq .gt_column_spanner_outer:last-child { padding-right: 0; }
 #eztbvnsliq .gt_column_spanner { border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; vertical-align: bottom; padding-top: 5px; padding-bottom: 5px; overflow-x: hidden; display: inline-block; width: 100%; }
 #eztbvnsliq .gt_spanner_row { border-bottom-style: hidden; }
 #eztbvnsliq .gt_group_heading { padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; text-transform: inherit; border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; vertical-align: middle; text-align: left; }
 #eztbvnsliq .gt_empty_group_heading { padding: 0.5px; color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; vertical-align: middle; }
 #eztbvnsliq .gt_from_md> :first-child { margin-top: 0; }
 #eztbvnsliq .gt_from_md> :last-child { margin-bottom: 0; }
 #eztbvnsliq .gt_row { padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; margin: 10px; border-top-style: solid; border-top-width: 1px; border-top-color: #D3D3D3; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; vertical-align: middle; overflow-x: hidden; }
 #eztbvnsliq .gt_stub { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; text-transform: inherit; border-right-style: solid; border-right-width: 2px; border-right-color: #D3D3D3; padding-left: 5px; padding-right: 5px; }
 #eztbvnsliq .gt_indent_1 { text-indent: 5px; }
 #eztbvnsliq .gt_indent_2 { text-indent: calc(5px * 2); }
 #eztbvnsliq .gt_indent_3 { text-indent: calc(5px * 3); }
 #eztbvnsliq .gt_indent_4 { text-indent: calc(5px * 4); }
 #eztbvnsliq .gt_indent_5 { text-indent: calc(5px * 5); }
 #eztbvnsliq .gt_stub_row_group { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; text-transform: inherit; border-right-style: solid; border-right-width: 2px; border-right-color: #D3D3D3; padding-left: 5px; padding-right: 5px; vertical-align: top; }
 #eztbvnsliq .gt_row_group_first td { border-top-width: 2px; }
 #eztbvnsliq .gt_row_group_first th { border-top-width: 2px; }
 #eztbvnsliq .gt_striped { color: #333333; background-color: #F4F4F4; }
 #eztbvnsliq .gt_table_body { border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; }
 #eztbvnsliq .gt_summary_row { color: #333333; background-color: #FFFFFF; text-transform: inherit; padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; }
 #eztbvnsliq .gt_first_summary_row { border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; }
 #eztbvnsliq .gt_last_summary_row_top { border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; }
 #eztbvnsliq .gt_grand_summary_row { color: #333333; background-color: #FFFFFF; text-transform: inherit; padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; }
 #eztbvnsliq .gt_first_grand_summary_row_bottom { border-top-style: double; border-top-width: 6px; border-top-color: #D3D3D3; }
 #eztbvnsliq .gt_last_grand_summary_row_top { border-bottom-style: double; border-bottom-width: 6px; border-bottom-color: #D3D3D3; }
 #eztbvnsliq .gt_sourcenotes { color: #333333; background-color: #FFFFFF; border-bottom-style: none; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; }
 #eztbvnsliq .gt_sourcenote { font-size: 90%; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; text-align: left; }
 #eztbvnsliq .gt_left { text-align: left; }
 #eztbvnsliq .gt_center { text-align: center; }
 #eztbvnsliq .gt_right { text-align: right; font-variant-numeric: tabular-nums; }
 #eztbvnsliq .gt_font_normal { font-weight: normal; }
 #eztbvnsliq .gt_font_bold { font-weight: bold; }
 #eztbvnsliq .gt_font_italic { font-style: italic; }
 #eztbvnsliq .gt_super { font-size: 65%; }
 #eztbvnsliq .gt_footnotes { color: font-color(#FFFFFF); background-color: #FFFFFF; border-bottom-style: none; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; }
 #eztbvnsliq .gt_footnote { margin: 0px; font-size: 90%; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; }
 #eztbvnsliq .gt_sourcenotes { color: #333333; background-color: #FFFFFF; border-bottom-style: none; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; }
 #eztbvnsliq .gt_sourcenote { font-size: 90%; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; text-align: left; }
 #eztbvnsliq .gt_footnote_marks { font-size: 75%; vertical-align: 0.4em; position: initial; }
 #eztbvnsliq .gt_asterisk { font-size: 100%; vertical-align: 0; }
 &#10;</style>

| Published season evaluated at render time — 2026 |  |  |  |  |
|----|----|----|----|----|
| every play of the published pbp joined to its game's realized outcome (ties from data artifacts excluded) |  |  |  |  |
| season | enriched_plays | games | home_win_rate | mean_home_win_prob |
| 2026 | 2,817,338 | 5998 | 62.3% | 0.6266 |

&#10;</div>

The mean predicted probability sitting close to the realized home-win
rate is the zeroth-order calibration check; the college home floor is
one of the strongest in sports and both numbers reflect it.

## Calibration

<div id="ztgyzjzsjy" style="padding-left:0px;padding-right:0px;padding-top:10px;padding-bottom:10px;overflow-x:auto;overflow-y:auto;width:auto;height:auto;">
<style>
#ztgyzjzsjy table {
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Helvetica Neue', 'Fira Sans', 'Droid Sans', Arial, sans-serif;
          -webkit-font-smoothing: antialiased;
          -moz-osx-font-smoothing: grayscale;
        }
&#10;#ztgyzjzsjy thead, tbody, tfoot, tr, td, th { border-style: none; }
 tr { background-color: transparent; }
#ztgyzjzsjy p { margin: 0; padding: 0; }
 #ztgyzjzsjy .gt_table { display: table; border-collapse: collapse; line-height: normal; margin-left: auto; margin-right: auto; color: #333333; font-size: 16px; font-weight: normal; font-style: normal; background-color: #FFFFFF; width: auto; border-top-style: solid; border-top-width: 2px; border-top-color: #A8A8A8; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #A8A8A8; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; }
 #ztgyzjzsjy .gt_caption { padding-top: 4px; padding-bottom: 4px; }
 #ztgyzjzsjy .gt_title { color: #333333; font-size: 125%; font-weight: initial; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; border-bottom-color: #FFFFFF; border-bottom-width: 0; }
 #ztgyzjzsjy .gt_subtitle { color: #333333; font-size: 85%; font-weight: initial; padding-top: 3px; padding-bottom: 5px; padding-left: 5px; padding-right: 5px; border-top-color: #FFFFFF; border-top-width: 0; }
 #ztgyzjzsjy .gt_heading { background-color: #FFFFFF; text-align: center; border-bottom-color: #FFFFFF; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; }
 #ztgyzjzsjy .gt_bottom_border { border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; }
 #ztgyzjzsjy .gt_col_headings { border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; }
 #ztgyzjzsjy .gt_col_heading { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: normal; text-transform: inherit; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; vertical-align: bottom; padding-top: 5px; padding-bottom: 5px; padding-left: 5px; padding-right: 5px; overflow-x: hidden; }
 #ztgyzjzsjy .gt_column_spanner_outer { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: normal; text-transform: inherit; padding-top: 0; padding-bottom: 0; padding-left: 4px; padding-right: 4px; }
 #ztgyzjzsjy .gt_column_spanner_outer:first-child { padding-left: 0; }
 #ztgyzjzsjy .gt_column_spanner_outer:last-child { padding-right: 0; }
 #ztgyzjzsjy .gt_column_spanner { border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; vertical-align: bottom; padding-top: 5px; padding-bottom: 5px; overflow-x: hidden; display: inline-block; width: 100%; }
 #ztgyzjzsjy .gt_spanner_row { border-bottom-style: hidden; }
 #ztgyzjzsjy .gt_group_heading { padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; text-transform: inherit; border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; vertical-align: middle; text-align: left; }
 #ztgyzjzsjy .gt_empty_group_heading { padding: 0.5px; color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; vertical-align: middle; }
 #ztgyzjzsjy .gt_from_md> :first-child { margin-top: 0; }
 #ztgyzjzsjy .gt_from_md> :last-child { margin-bottom: 0; }
 #ztgyzjzsjy .gt_row { padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; margin: 10px; border-top-style: solid; border-top-width: 1px; border-top-color: #D3D3D3; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; vertical-align: middle; overflow-x: hidden; }
 #ztgyzjzsjy .gt_stub { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; text-transform: inherit; border-right-style: solid; border-right-width: 2px; border-right-color: #D3D3D3; padding-left: 5px; padding-right: 5px; }
 #ztgyzjzsjy .gt_indent_1 { text-indent: 5px; }
 #ztgyzjzsjy .gt_indent_2 { text-indent: calc(5px * 2); }
 #ztgyzjzsjy .gt_indent_3 { text-indent: calc(5px * 3); }
 #ztgyzjzsjy .gt_indent_4 { text-indent: calc(5px * 4); }
 #ztgyzjzsjy .gt_indent_5 { text-indent: calc(5px * 5); }
 #ztgyzjzsjy .gt_stub_row_group { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; text-transform: inherit; border-right-style: solid; border-right-width: 2px; border-right-color: #D3D3D3; padding-left: 5px; padding-right: 5px; vertical-align: top; }
 #ztgyzjzsjy .gt_row_group_first td { border-top-width: 2px; }
 #ztgyzjzsjy .gt_row_group_first th { border-top-width: 2px; }
 #ztgyzjzsjy .gt_striped { color: #333333; background-color: #F4F4F4; }
 #ztgyzjzsjy .gt_table_body { border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; }
 #ztgyzjzsjy .gt_summary_row { color: #333333; background-color: #FFFFFF; text-transform: inherit; padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; }
 #ztgyzjzsjy .gt_first_summary_row { border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; }
 #ztgyzjzsjy .gt_last_summary_row_top { border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; }
 #ztgyzjzsjy .gt_grand_summary_row { color: #333333; background-color: #FFFFFF; text-transform: inherit; padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; }
 #ztgyzjzsjy .gt_first_grand_summary_row_bottom { border-top-style: double; border-top-width: 6px; border-top-color: #D3D3D3; }
 #ztgyzjzsjy .gt_last_grand_summary_row_top { border-bottom-style: double; border-bottom-width: 6px; border-bottom-color: #D3D3D3; }
 #ztgyzjzsjy .gt_sourcenotes { color: #333333; background-color: #FFFFFF; border-bottom-style: none; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; }
 #ztgyzjzsjy .gt_sourcenote { font-size: 90%; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; text-align: left; }
 #ztgyzjzsjy .gt_left { text-align: left; }
 #ztgyzjzsjy .gt_center { text-align: center; }
 #ztgyzjzsjy .gt_right { text-align: right; font-variant-numeric: tabular-nums; }
 #ztgyzjzsjy .gt_font_normal { font-weight: normal; }
 #ztgyzjzsjy .gt_font_bold { font-weight: bold; }
 #ztgyzjzsjy .gt_font_italic { font-style: italic; }
 #ztgyzjzsjy .gt_super { font-size: 65%; }
 #ztgyzjzsjy .gt_footnotes { color: font-color(#FFFFFF); background-color: #FFFFFF; border-bottom-style: none; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; }
 #ztgyzjzsjy .gt_footnote { margin: 0px; font-size: 90%; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; }
 #ztgyzjzsjy .gt_sourcenotes { color: #333333; background-color: #FFFFFF; border-bottom-style: none; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; }
 #ztgyzjzsjy .gt_sourcenote { font-size: 90%; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; text-align: left; }
 #ztgyzjzsjy .gt_footnote_marks { font-size: 75%; vertical-align: 0.4em; position: initial; }
 #ztgyzjzsjy .gt_asterisk { font-size: 100%; vertical-align: 0; }
 &#10;</style>

| Out-of-band calibration — 2026 published season |        |
|-------------------------------------------------|--------|
| metric                                          | value  |
| Brier score (all plays)                         | 0.1045 |
| 20-bin calibration MAE                          | 0.0143 |
| baseline Brier (constant home-win rate)         | 0.2341 |

&#10;</div>

<img src="wp_enrich_files/figure-commonmark/cell-5-output-1.png"
width="420" height="300"
alt="Reliability diagram, 20 bins — predicted in-game probability vs realized outcome frequency." />

<div id="eklkjqkgcp" style="padding-left:0px;padding-right:0px;padding-top:10px;padding-bottom:10px;overflow-x:auto;overflow-y:auto;width:auto;height:auto;">
<style>
#eklkjqkgcp table {
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Helvetica Neue', 'Fira Sans', 'Droid Sans', Arial, sans-serif;
          -webkit-font-smoothing: antialiased;
          -moz-osx-font-smoothing: grayscale;
        }
&#10;#eklkjqkgcp thead, tbody, tfoot, tr, td, th { border-style: none; }
 tr { background-color: transparent; }
#eklkjqkgcp p { margin: 0; padding: 0; }
 #eklkjqkgcp .gt_table { display: table; border-collapse: collapse; line-height: normal; margin-left: auto; margin-right: auto; color: #333333; font-size: 16px; font-weight: normal; font-style: normal; background-color: #FFFFFF; width: auto; border-top-style: solid; border-top-width: 2px; border-top-color: #A8A8A8; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #A8A8A8; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; }
 #eklkjqkgcp .gt_caption { padding-top: 4px; padding-bottom: 4px; }
 #eklkjqkgcp .gt_title { color: #333333; font-size: 125%; font-weight: initial; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; border-bottom-color: #FFFFFF; border-bottom-width: 0; }
 #eklkjqkgcp .gt_subtitle { color: #333333; font-size: 85%; font-weight: initial; padding-top: 3px; padding-bottom: 5px; padding-left: 5px; padding-right: 5px; border-top-color: #FFFFFF; border-top-width: 0; }
 #eklkjqkgcp .gt_heading { background-color: #FFFFFF; text-align: center; border-bottom-color: #FFFFFF; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; }
 #eklkjqkgcp .gt_bottom_border { border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; }
 #eklkjqkgcp .gt_col_headings { border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; }
 #eklkjqkgcp .gt_col_heading { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: normal; text-transform: inherit; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; vertical-align: bottom; padding-top: 5px; padding-bottom: 5px; padding-left: 5px; padding-right: 5px; overflow-x: hidden; }
 #eklkjqkgcp .gt_column_spanner_outer { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: normal; text-transform: inherit; padding-top: 0; padding-bottom: 0; padding-left: 4px; padding-right: 4px; }
 #eklkjqkgcp .gt_column_spanner_outer:first-child { padding-left: 0; }
 #eklkjqkgcp .gt_column_spanner_outer:last-child { padding-right: 0; }
 #eklkjqkgcp .gt_column_spanner { border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; vertical-align: bottom; padding-top: 5px; padding-bottom: 5px; overflow-x: hidden; display: inline-block; width: 100%; }
 #eklkjqkgcp .gt_spanner_row { border-bottom-style: hidden; }
 #eklkjqkgcp .gt_group_heading { padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; text-transform: inherit; border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; vertical-align: middle; text-align: left; }
 #eklkjqkgcp .gt_empty_group_heading { padding: 0.5px; color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; vertical-align: middle; }
 #eklkjqkgcp .gt_from_md> :first-child { margin-top: 0; }
 #eklkjqkgcp .gt_from_md> :last-child { margin-bottom: 0; }
 #eklkjqkgcp .gt_row { padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; margin: 10px; border-top-style: solid; border-top-width: 1px; border-top-color: #D3D3D3; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; vertical-align: middle; overflow-x: hidden; }
 #eklkjqkgcp .gt_stub { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; text-transform: inherit; border-right-style: solid; border-right-width: 2px; border-right-color: #D3D3D3; padding-left: 5px; padding-right: 5px; }
 #eklkjqkgcp .gt_indent_1 { text-indent: 5px; }
 #eklkjqkgcp .gt_indent_2 { text-indent: calc(5px * 2); }
 #eklkjqkgcp .gt_indent_3 { text-indent: calc(5px * 3); }
 #eklkjqkgcp .gt_indent_4 { text-indent: calc(5px * 4); }
 #eklkjqkgcp .gt_indent_5 { text-indent: calc(5px * 5); }
 #eklkjqkgcp .gt_stub_row_group { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; text-transform: inherit; border-right-style: solid; border-right-width: 2px; border-right-color: #D3D3D3; padding-left: 5px; padding-right: 5px; vertical-align: top; }
 #eklkjqkgcp .gt_row_group_first td { border-top-width: 2px; }
 #eklkjqkgcp .gt_row_group_first th { border-top-width: 2px; }
 #eklkjqkgcp .gt_striped { color: #333333; background-color: #F4F4F4; }
 #eklkjqkgcp .gt_table_body { border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; }
 #eklkjqkgcp .gt_summary_row { color: #333333; background-color: #FFFFFF; text-transform: inherit; padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; }
 #eklkjqkgcp .gt_first_summary_row { border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; }
 #eklkjqkgcp .gt_last_summary_row_top { border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; }
 #eklkjqkgcp .gt_grand_summary_row { color: #333333; background-color: #FFFFFF; text-transform: inherit; padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; }
 #eklkjqkgcp .gt_first_grand_summary_row_bottom { border-top-style: double; border-top-width: 6px; border-top-color: #D3D3D3; }
 #eklkjqkgcp .gt_last_grand_summary_row_top { border-bottom-style: double; border-bottom-width: 6px; border-bottom-color: #D3D3D3; }
 #eklkjqkgcp .gt_sourcenotes { color: #333333; background-color: #FFFFFF; border-bottom-style: none; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; }
 #eklkjqkgcp .gt_sourcenote { font-size: 90%; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; text-align: left; }
 #eklkjqkgcp .gt_left { text-align: left; }
 #eklkjqkgcp .gt_center { text-align: center; }
 #eklkjqkgcp .gt_right { text-align: right; font-variant-numeric: tabular-nums; }
 #eklkjqkgcp .gt_font_normal { font-weight: normal; }
 #eklkjqkgcp .gt_font_bold { font-weight: bold; }
 #eklkjqkgcp .gt_font_italic { font-style: italic; }
 #eklkjqkgcp .gt_super { font-size: 65%; }
 #eklkjqkgcp .gt_footnotes { color: font-color(#FFFFFF); background-color: #FFFFFF; border-bottom-style: none; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; }
 #eklkjqkgcp .gt_footnote { margin: 0px; font-size: 90%; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; }
 #eklkjqkgcp .gt_sourcenotes { color: #333333; background-color: #FFFFFF; border-bottom-style: none; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; }
 #eklkjqkgcp .gt_sourcenote { font-size: 90%; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; text-align: left; }
 #eklkjqkgcp .gt_footnote_marks { font-size: 75%; vertical-align: 0.4em; position: initial; }
 #eklkjqkgcp .gt_asterisk { font-size: 100%; vertical-align: 0; }
 &#10;</style>

| Brier by period — uncertainty should resolve as the game progresses |  |  |
|----|----|----|
| a well-behaved WP model gets sharper (lower Brier) in later periods |  |  |
| period_number | plays | brier |
| 1 | 655,639 | 0.1478 |
| 2 | 693,809 | 0.1219 |
| 3 | 709,816 | 0.0952 |
| 4 | 739,209 | 0.0571 |
| 5 | 16,120 | 0.1649 |

&#10;</div>

<img src="wp_enrich_files/figure-commonmark/cell-7-output-1.png"
width="420" height="300"
alt="The season’s wildest game by WP swing: in-game home win probability trace." />

<div id="qggapcfznk" style="padding-left:0px;padding-right:0px;padding-top:10px;padding-bottom:10px;overflow-x:auto;overflow-y:auto;width:auto;height:auto;">
<style>
#qggapcfznk table {
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Helvetica Neue', 'Fira Sans', 'Droid Sans', Arial, sans-serif;
          -webkit-font-smoothing: antialiased;
          -moz-osx-font-smoothing: grayscale;
        }
&#10;#qggapcfznk thead, tbody, tfoot, tr, td, th { border-style: none; }
 tr { background-color: transparent; }
#qggapcfznk p { margin: 0; padding: 0; }
 #qggapcfznk .gt_table { display: table; border-collapse: collapse; line-height: normal; margin-left: auto; margin-right: auto; color: #333333; font-size: 16px; font-weight: normal; font-style: normal; background-color: #FFFFFF; width: auto; border-top-style: solid; border-top-width: 2px; border-top-color: #A8A8A8; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #A8A8A8; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; }
 #qggapcfznk .gt_caption { padding-top: 4px; padding-bottom: 4px; }
 #qggapcfznk .gt_title { color: #333333; font-size: 125%; font-weight: initial; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; border-bottom-color: #FFFFFF; border-bottom-width: 0; }
 #qggapcfznk .gt_subtitle { color: #333333; font-size: 85%; font-weight: initial; padding-top: 3px; padding-bottom: 5px; padding-left: 5px; padding-right: 5px; border-top-color: #FFFFFF; border-top-width: 0; }
 #qggapcfznk .gt_heading { background-color: #FFFFFF; text-align: center; border-bottom-color: #FFFFFF; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; }
 #qggapcfznk .gt_bottom_border { border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; }
 #qggapcfznk .gt_col_headings { border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; }
 #qggapcfznk .gt_col_heading { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: normal; text-transform: inherit; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; vertical-align: bottom; padding-top: 5px; padding-bottom: 5px; padding-left: 5px; padding-right: 5px; overflow-x: hidden; }
 #qggapcfznk .gt_column_spanner_outer { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: normal; text-transform: inherit; padding-top: 0; padding-bottom: 0; padding-left: 4px; padding-right: 4px; }
 #qggapcfznk .gt_column_spanner_outer:first-child { padding-left: 0; }
 #qggapcfznk .gt_column_spanner_outer:last-child { padding-right: 0; }
 #qggapcfznk .gt_column_spanner { border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; vertical-align: bottom; padding-top: 5px; padding-bottom: 5px; overflow-x: hidden; display: inline-block; width: 100%; }
 #qggapcfznk .gt_spanner_row { border-bottom-style: hidden; }
 #qggapcfznk .gt_group_heading { padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; text-transform: inherit; border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; vertical-align: middle; text-align: left; }
 #qggapcfznk .gt_empty_group_heading { padding: 0.5px; color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; vertical-align: middle; }
 #qggapcfznk .gt_from_md> :first-child { margin-top: 0; }
 #qggapcfznk .gt_from_md> :last-child { margin-bottom: 0; }
 #qggapcfznk .gt_row { padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; margin: 10px; border-top-style: solid; border-top-width: 1px; border-top-color: #D3D3D3; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; vertical-align: middle; overflow-x: hidden; }
 #qggapcfznk .gt_stub { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; text-transform: inherit; border-right-style: solid; border-right-width: 2px; border-right-color: #D3D3D3; padding-left: 5px; padding-right: 5px; }
 #qggapcfznk .gt_indent_1 { text-indent: 5px; }
 #qggapcfznk .gt_indent_2 { text-indent: calc(5px * 2); }
 #qggapcfznk .gt_indent_3 { text-indent: calc(5px * 3); }
 #qggapcfznk .gt_indent_4 { text-indent: calc(5px * 4); }
 #qggapcfznk .gt_indent_5 { text-indent: calc(5px * 5); }
 #qggapcfznk .gt_stub_row_group { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; text-transform: inherit; border-right-style: solid; border-right-width: 2px; border-right-color: #D3D3D3; padding-left: 5px; padding-right: 5px; vertical-align: top; }
 #qggapcfznk .gt_row_group_first td { border-top-width: 2px; }
 #qggapcfznk .gt_row_group_first th { border-top-width: 2px; }
 #qggapcfznk .gt_striped { color: #333333; background-color: #F4F4F4; }
 #qggapcfznk .gt_table_body { border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; }
 #qggapcfznk .gt_summary_row { color: #333333; background-color: #FFFFFF; text-transform: inherit; padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; }
 #qggapcfznk .gt_first_summary_row { border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; }
 #qggapcfznk .gt_last_summary_row_top { border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; }
 #qggapcfznk .gt_grand_summary_row { color: #333333; background-color: #FFFFFF; text-transform: inherit; padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; }
 #qggapcfznk .gt_first_grand_summary_row_bottom { border-top-style: double; border-top-width: 6px; border-top-color: #D3D3D3; }
 #qggapcfznk .gt_last_grand_summary_row_top { border-bottom-style: double; border-bottom-width: 6px; border-bottom-color: #D3D3D3; }
 #qggapcfznk .gt_sourcenotes { color: #333333; background-color: #FFFFFF; border-bottom-style: none; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; }
 #qggapcfznk .gt_sourcenote { font-size: 90%; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; text-align: left; }
 #qggapcfznk .gt_left { text-align: left; }
 #qggapcfznk .gt_center { text-align: center; }
 #qggapcfznk .gt_right { text-align: right; font-variant-numeric: tabular-nums; }
 #qggapcfznk .gt_font_normal { font-weight: normal; }
 #qggapcfznk .gt_font_bold { font-weight: bold; }
 #qggapcfznk .gt_font_italic { font-style: italic; }
 #qggapcfznk .gt_super { font-size: 65%; }
 #qggapcfznk .gt_footnotes { color: font-color(#FFFFFF); background-color: #FFFFFF; border-bottom-style: none; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; }
 #qggapcfznk .gt_footnote { margin: 0px; font-size: 90%; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; }
 #qggapcfznk .gt_sourcenotes { color: #333333; background-color: #FFFFFF; border-bottom-style: none; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; }
 #qggapcfznk .gt_sourcenote { font-size: 90%; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; text-align: left; }
 #qggapcfznk .gt_footnote_marks { font-size: 75%; vertical-align: 0.4em; position: initial; }
 #qggapcfznk .gt_asterisk { font-size: 100%; vertical-align: 0; }
 &#10;</style>

| Pregame vs in-game — the value the enrichment adds over the prior |        |
|-------------------------------------------------------------------|--------|
| model                                                             | brier  |
| pregame prior (one prob per game)                                 | 0.1638 |
| in-game WP (all plays)                                            | 0.1045 |

&#10;</div>

The reliability diagram hugging the diagonal, the per-period Brier
falling monotonically, and the in-game model beating its own pregame
prior are the three signatures of a healthy applied WP surface. The
volatile-game trace is the demonstration consumers care about: the
column tells the story of a comeback without any narrative input.

## Unseen-era holdout

Holdout season **2013** — 627,477 plays in 1,857 games; probabilities
from probabilities computed at render time – the release asset lacks the
WP columns.

<div id="ojgfgfdbkq" style="padding-left:0px;padding-right:0px;padding-top:10px;padding-bottom:10px;overflow-x:auto;overflow-y:auto;width:auto;height:auto;">
<style>
#ojgfgfdbkq table {
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Helvetica Neue', 'Fira Sans', 'Droid Sans', Arial, sans-serif;
          -webkit-font-smoothing: antialiased;
          -moz-osx-font-smoothing: grayscale;
        }
&#10;#ojgfgfdbkq thead, tbody, tfoot, tr, td, th { border-style: none; }
 tr { background-color: transparent; }
#ojgfgfdbkq p { margin: 0; padding: 0; }
 #ojgfgfdbkq .gt_table { display: table; border-collapse: collapse; line-height: normal; margin-left: auto; margin-right: auto; color: #333333; font-size: 16px; font-weight: normal; font-style: normal; background-color: #FFFFFF; width: auto; border-top-style: solid; border-top-width: 2px; border-top-color: #A8A8A8; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #A8A8A8; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; }
 #ojgfgfdbkq .gt_caption { padding-top: 4px; padding-bottom: 4px; }
 #ojgfgfdbkq .gt_title { color: #333333; font-size: 125%; font-weight: initial; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; border-bottom-color: #FFFFFF; border-bottom-width: 0; }
 #ojgfgfdbkq .gt_subtitle { color: #333333; font-size: 85%; font-weight: initial; padding-top: 3px; padding-bottom: 5px; padding-left: 5px; padding-right: 5px; border-top-color: #FFFFFF; border-top-width: 0; }
 #ojgfgfdbkq .gt_heading { background-color: #FFFFFF; text-align: center; border-bottom-color: #FFFFFF; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; }
 #ojgfgfdbkq .gt_bottom_border { border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; }
 #ojgfgfdbkq .gt_col_headings { border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; }
 #ojgfgfdbkq .gt_col_heading { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: normal; text-transform: inherit; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; vertical-align: bottom; padding-top: 5px; padding-bottom: 5px; padding-left: 5px; padding-right: 5px; overflow-x: hidden; }
 #ojgfgfdbkq .gt_column_spanner_outer { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: normal; text-transform: inherit; padding-top: 0; padding-bottom: 0; padding-left: 4px; padding-right: 4px; }
 #ojgfgfdbkq .gt_column_spanner_outer:first-child { padding-left: 0; }
 #ojgfgfdbkq .gt_column_spanner_outer:last-child { padding-right: 0; }
 #ojgfgfdbkq .gt_column_spanner { border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; vertical-align: bottom; padding-top: 5px; padding-bottom: 5px; overflow-x: hidden; display: inline-block; width: 100%; }
 #ojgfgfdbkq .gt_spanner_row { border-bottom-style: hidden; }
 #ojgfgfdbkq .gt_group_heading { padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; text-transform: inherit; border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; vertical-align: middle; text-align: left; }
 #ojgfgfdbkq .gt_empty_group_heading { padding: 0.5px; color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; vertical-align: middle; }
 #ojgfgfdbkq .gt_from_md> :first-child { margin-top: 0; }
 #ojgfgfdbkq .gt_from_md> :last-child { margin-bottom: 0; }
 #ojgfgfdbkq .gt_row { padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; margin: 10px; border-top-style: solid; border-top-width: 1px; border-top-color: #D3D3D3; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; vertical-align: middle; overflow-x: hidden; }
 #ojgfgfdbkq .gt_stub { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; text-transform: inherit; border-right-style: solid; border-right-width: 2px; border-right-color: #D3D3D3; padding-left: 5px; padding-right: 5px; }
 #ojgfgfdbkq .gt_indent_1 { text-indent: 5px; }
 #ojgfgfdbkq .gt_indent_2 { text-indent: calc(5px * 2); }
 #ojgfgfdbkq .gt_indent_3 { text-indent: calc(5px * 3); }
 #ojgfgfdbkq .gt_indent_4 { text-indent: calc(5px * 4); }
 #ojgfgfdbkq .gt_indent_5 { text-indent: calc(5px * 5); }
 #ojgfgfdbkq .gt_stub_row_group { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; text-transform: inherit; border-right-style: solid; border-right-width: 2px; border-right-color: #D3D3D3; padding-left: 5px; padding-right: 5px; vertical-align: top; }
 #ojgfgfdbkq .gt_row_group_first td { border-top-width: 2px; }
 #ojgfgfdbkq .gt_row_group_first th { border-top-width: 2px; }
 #ojgfgfdbkq .gt_striped { color: #333333; background-color: #F4F4F4; }
 #ojgfgfdbkq .gt_table_body { border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; }
 #ojgfgfdbkq .gt_summary_row { color: #333333; background-color: #FFFFFF; text-transform: inherit; padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; }
 #ojgfgfdbkq .gt_first_summary_row { border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; }
 #ojgfgfdbkq .gt_last_summary_row_top { border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; }
 #ojgfgfdbkq .gt_grand_summary_row { color: #333333; background-color: #FFFFFF; text-transform: inherit; padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; }
 #ojgfgfdbkq .gt_first_grand_summary_row_bottom { border-top-style: double; border-top-width: 6px; border-top-color: #D3D3D3; }
 #ojgfgfdbkq .gt_last_grand_summary_row_top { border-bottom-style: double; border-bottom-width: 6px; border-bottom-color: #D3D3D3; }
 #ojgfgfdbkq .gt_sourcenotes { color: #333333; background-color: #FFFFFF; border-bottom-style: none; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; }
 #ojgfgfdbkq .gt_sourcenote { font-size: 90%; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; text-align: left; }
 #ojgfgfdbkq .gt_left { text-align: left; }
 #ojgfgfdbkq .gt_center { text-align: center; }
 #ojgfgfdbkq .gt_right { text-align: right; font-variant-numeric: tabular-nums; }
 #ojgfgfdbkq .gt_font_normal { font-weight: normal; }
 #ojgfgfdbkq .gt_font_bold { font-weight: bold; }
 #ojgfgfdbkq .gt_font_italic { font-style: italic; }
 #ojgfgfdbkq .gt_super { font-size: 65%; }
 #ojgfgfdbkq .gt_footnotes { color: font-color(#FFFFFF); background-color: #FFFFFF; border-bottom-style: none; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; }
 #ojgfgfdbkq .gt_footnote { margin: 0px; font-size: 90%; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; }
 #ojgfgfdbkq .gt_sourcenotes { color: #333333; background-color: #FFFFFF; border-bottom-style: none; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; }
 #ojgfgfdbkq .gt_sourcenote { font-size: 90%; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; text-align: left; }
 #ojgfgfdbkq .gt_footnote_marks { font-size: 75%; vertical-align: 0.4em; position: initial; }
 #ojgfgfdbkq .gt_asterisk { font-size: 100%; vertical-align: 0; }
 &#10;</style>

| Era transfer — the same booster in-era and on an era it never saw |  |  |  |  |  |  |
|----|----|----|----|----|----|----|
| the calibration-MAE gap between the rows is the era-transfer error, bounded here rather than assumed |  |  |  |  |  |  |
| era | plays | brier | baseline_brier | skill_vs_baseline | calibration_mae_20bin | pregame_brier |
| 2026 (in-era) | 2,817,338 | 0.1045 | 0.2341 | 55.4% | 0.0143 | 0.1638 |
| 2013 (unseen: halves era, before the 2016 move to quarters) | 627,477 | 0.1136 | 0.2313 | 50.9% | 0.0273 | 0.1815 |

&#10;</div>

<img src="wp_enrich_files/figure-commonmark/cell-10-output-1.png"
width="420" height="300"
alt="Reliability, in-era vs unseen era. A curve that stays on the diagonal in the halves era means the game-state features transfer across the quarters change; a bowed curve is the era-transfer error made visible." />

The booster sees only game state, so what an unseen era tests is whether
“down 6 with 4:00 left” meant the same thing when the game was played in
two halves rather than four quarters. The table bounds that explicitly:
the skill-versus-baseline and calibration MAE of the old era sit next to
the in-era numbers rather than being assumed equal. The pregame prior
also moves across eras — it is an as-of team-rating model over that
season’s own results — so the holdout tests the whole applied surface,
not just the tree.

## Provenance & reproducibility

- **Model:** XGBoost in-game WP over game state (score margin, seconds
  left, its square root, pregame logit, possession), fit on one recent
  season, bundled and oracle-gated in sdv-py
  (`wbb/models/wbb_in_game_wp.ubj`). WBB play-by-play is **halves before
  season 2016**; the game-state features are period-agnostic, and the
  holdout section above is what bounds the transfer across that change
  instead of assuming it.
- **Applied to:** every published season of
  `espn_womens_college_basketball_pbp`, in place, columns
  `home_win_prob` + `pregame_home_prob`, by the enrichment stage — the
  pbp asset’s only publisher.
  `wbb_data_build.publish.assert_wp_enriched` refuses any pbp parquet
  missing the columns or below a 0.999 finite-rate floor (observed 1.0
  on 2024–2026), asserted on the file about to upload.
- **Pipeline:** `scripts/wbb_models.sh 03` → stage
  `python/wbb_model_03_wp_enrich.py -s <season> -e <season>`, wired at
  the end of `scripts/daily_wbb_data_processor.sh` (after schedules +
  team_box exist in the tree). Single home: `models/manifest.yaml`.
- **Release state (2026-09-01):** 2024–2026 carry the columns; every
  earlier season sampled (2004, 2008, 2012, 2015, 2016, 2020) does not
  and needs one `wbb_model_03_wp_enrich -s 2003 -e 2023` republish. This
  document falls back to computing the holdout era itself while that is
  outstanding.
- **This document** evaluates two published seasons downloaded at render
  time (~90 MB + ~50 MB) — the exact frames consumers read.
- **Rebuild:** `scripts/render_model_docs.sh` (Quarto → GFM;
  `uv sync --group docs`).

## Avenues for improvement & open issues

- **Possession-state features** — foul counts, bonus state, and timeout
  inventory are absent from the WP inputs.
- **Resolved (2026-09-01, PR \#32):** the nightly publish no longer
  strips the WP columns — the enrichment stage is the pbp asset’s only
  publisher and the publish path refuses an un-enriched pbp parquet, so
  no publish window exists in which a season lacks WP. The pre-2024
  seasons stripped by the history republish still need the one-off
  republish listed above.
- **Resolved (2026-09-01, PR \#32):** season-holdout curve — the
  unseen-era section above renders the same calibration for a season the
  booster never saw and reports the era-transfer error as a number.
