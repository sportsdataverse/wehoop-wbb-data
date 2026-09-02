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

<div id="dyjctorydq" style="padding-left:0px;padding-right:0px;padding-top:10px;padding-bottom:10px;overflow-x:auto;overflow-y:auto;width:auto;height:auto;">
<style>
#dyjctorydq table {
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Helvetica Neue', 'Fira Sans', 'Droid Sans', Arial, sans-serif;
          -webkit-font-smoothing: antialiased;
          -moz-osx-font-smoothing: grayscale;
        }
&#10;#dyjctorydq thead, tbody, tfoot, tr, td, th { border-style: none; }
 tr { background-color: transparent; }
#dyjctorydq p { margin: 0; padding: 0; }
 #dyjctorydq .gt_table { display: table; border-collapse: collapse; line-height: normal; margin-left: auto; margin-right: auto; color: #333333; font-size: 16px; font-weight: normal; font-style: normal; background-color: #FFFFFF; width: auto; border-top-style: solid; border-top-width: 2px; border-top-color: #A8A8A8; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #A8A8A8; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; }
 #dyjctorydq .gt_caption { padding-top: 4px; padding-bottom: 4px; }
 #dyjctorydq .gt_title { color: #333333; font-size: 125%; font-weight: initial; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; border-bottom-color: #FFFFFF; border-bottom-width: 0; }
 #dyjctorydq .gt_subtitle { color: #333333; font-size: 85%; font-weight: initial; padding-top: 3px; padding-bottom: 5px; padding-left: 5px; padding-right: 5px; border-top-color: #FFFFFF; border-top-width: 0; }
 #dyjctorydq .gt_heading { background-color: #FFFFFF; text-align: center; border-bottom-color: #FFFFFF; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; }
 #dyjctorydq .gt_bottom_border { border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; }
 #dyjctorydq .gt_col_headings { border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; }
 #dyjctorydq .gt_col_heading { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: normal; text-transform: inherit; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; vertical-align: bottom; padding-top: 5px; padding-bottom: 5px; padding-left: 5px; padding-right: 5px; overflow-x: hidden; }
 #dyjctorydq .gt_column_spanner_outer { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: normal; text-transform: inherit; padding-top: 0; padding-bottom: 0; padding-left: 4px; padding-right: 4px; }
 #dyjctorydq .gt_column_spanner_outer:first-child { padding-left: 0; }
 #dyjctorydq .gt_column_spanner_outer:last-child { padding-right: 0; }
 #dyjctorydq .gt_column_spanner { border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; vertical-align: bottom; padding-top: 5px; padding-bottom: 5px; overflow-x: hidden; display: inline-block; width: 100%; }
 #dyjctorydq .gt_spanner_row { border-bottom-style: hidden; }
 #dyjctorydq .gt_group_heading { padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; text-transform: inherit; border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; vertical-align: middle; text-align: left; }
 #dyjctorydq .gt_empty_group_heading { padding: 0.5px; color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; vertical-align: middle; }
 #dyjctorydq .gt_from_md> :first-child { margin-top: 0; }
 #dyjctorydq .gt_from_md> :last-child { margin-bottom: 0; }
 #dyjctorydq .gt_row { padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; margin: 10px; border-top-style: solid; border-top-width: 1px; border-top-color: #D3D3D3; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; vertical-align: middle; overflow-x: hidden; }
 #dyjctorydq .gt_stub { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; text-transform: inherit; border-right-style: solid; border-right-width: 2px; border-right-color: #D3D3D3; padding-left: 5px; padding-right: 5px; }
 #dyjctorydq .gt_indent_1 { text-indent: 5px; }
 #dyjctorydq .gt_indent_2 { text-indent: calc(5px * 2); }
 #dyjctorydq .gt_indent_3 { text-indent: calc(5px * 3); }
 #dyjctorydq .gt_indent_4 { text-indent: calc(5px * 4); }
 #dyjctorydq .gt_indent_5 { text-indent: calc(5px * 5); }
 #dyjctorydq .gt_stub_row_group { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; text-transform: inherit; border-right-style: solid; border-right-width: 2px; border-right-color: #D3D3D3; padding-left: 5px; padding-right: 5px; vertical-align: top; }
 #dyjctorydq .gt_row_group_first td { border-top-width: 2px; }
 #dyjctorydq .gt_row_group_first th { border-top-width: 2px; }
 #dyjctorydq .gt_striped { color: #333333; background-color: #F4F4F4; }
 #dyjctorydq .gt_table_body { border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; }
 #dyjctorydq .gt_summary_row { color: #333333; background-color: #FFFFFF; text-transform: inherit; padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; }
 #dyjctorydq .gt_first_summary_row { border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; }
 #dyjctorydq .gt_last_summary_row_top { border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; }
 #dyjctorydq .gt_grand_summary_row { color: #333333; background-color: #FFFFFF; text-transform: inherit; padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; }
 #dyjctorydq .gt_first_grand_summary_row_bottom { border-top-style: double; border-top-width: 6px; border-top-color: #D3D3D3; }
 #dyjctorydq .gt_last_grand_summary_row_top { border-bottom-style: double; border-bottom-width: 6px; border-bottom-color: #D3D3D3; }
 #dyjctorydq .gt_sourcenotes { color: #333333; background-color: #FFFFFF; border-bottom-style: none; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; }
 #dyjctorydq .gt_sourcenote { font-size: 90%; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; text-align: left; }
 #dyjctorydq .gt_left { text-align: left; }
 #dyjctorydq .gt_center { text-align: center; }
 #dyjctorydq .gt_right { text-align: right; font-variant-numeric: tabular-nums; }
 #dyjctorydq .gt_font_normal { font-weight: normal; }
 #dyjctorydq .gt_font_bold { font-weight: bold; }
 #dyjctorydq .gt_font_italic { font-style: italic; }
 #dyjctorydq .gt_super { font-size: 65%; }
 #dyjctorydq .gt_footnotes { color: font-color(#FFFFFF); background-color: #FFFFFF; border-bottom-style: none; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; }
 #dyjctorydq .gt_footnote { margin: 0px; font-size: 90%; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; }
 #dyjctorydq .gt_sourcenotes { color: #333333; background-color: #FFFFFF; border-bottom-style: none; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; }
 #dyjctorydq .gt_sourcenote { font-size: 90%; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; text-align: left; }
 #dyjctorydq .gt_footnote_marks { font-size: 75%; vertical-align: 0.4em; position: initial; }
 #dyjctorydq .gt_asterisk { font-size: 100%; vertical-align: 0; }
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

<div id="wccqyntdzo" style="padding-left:0px;padding-right:0px;padding-top:10px;padding-bottom:10px;overflow-x:auto;overflow-y:auto;width:auto;height:auto;">
<style>
#wccqyntdzo table {
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Helvetica Neue', 'Fira Sans', 'Droid Sans', Arial, sans-serif;
          -webkit-font-smoothing: antialiased;
          -moz-osx-font-smoothing: grayscale;
        }
&#10;#wccqyntdzo thead, tbody, tfoot, tr, td, th { border-style: none; }
 tr { background-color: transparent; }
#wccqyntdzo p { margin: 0; padding: 0; }
 #wccqyntdzo .gt_table { display: table; border-collapse: collapse; line-height: normal; margin-left: auto; margin-right: auto; color: #333333; font-size: 16px; font-weight: normal; font-style: normal; background-color: #FFFFFF; width: auto; border-top-style: solid; border-top-width: 2px; border-top-color: #A8A8A8; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #A8A8A8; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; }
 #wccqyntdzo .gt_caption { padding-top: 4px; padding-bottom: 4px; }
 #wccqyntdzo .gt_title { color: #333333; font-size: 125%; font-weight: initial; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; border-bottom-color: #FFFFFF; border-bottom-width: 0; }
 #wccqyntdzo .gt_subtitle { color: #333333; font-size: 85%; font-weight: initial; padding-top: 3px; padding-bottom: 5px; padding-left: 5px; padding-right: 5px; border-top-color: #FFFFFF; border-top-width: 0; }
 #wccqyntdzo .gt_heading { background-color: #FFFFFF; text-align: center; border-bottom-color: #FFFFFF; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; }
 #wccqyntdzo .gt_bottom_border { border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; }
 #wccqyntdzo .gt_col_headings { border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; }
 #wccqyntdzo .gt_col_heading { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: normal; text-transform: inherit; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; vertical-align: bottom; padding-top: 5px; padding-bottom: 5px; padding-left: 5px; padding-right: 5px; overflow-x: hidden; }
 #wccqyntdzo .gt_column_spanner_outer { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: normal; text-transform: inherit; padding-top: 0; padding-bottom: 0; padding-left: 4px; padding-right: 4px; }
 #wccqyntdzo .gt_column_spanner_outer:first-child { padding-left: 0; }
 #wccqyntdzo .gt_column_spanner_outer:last-child { padding-right: 0; }
 #wccqyntdzo .gt_column_spanner { border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; vertical-align: bottom; padding-top: 5px; padding-bottom: 5px; overflow-x: hidden; display: inline-block; width: 100%; }
 #wccqyntdzo .gt_spanner_row { border-bottom-style: hidden; }
 #wccqyntdzo .gt_group_heading { padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; text-transform: inherit; border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; vertical-align: middle; text-align: left; }
 #wccqyntdzo .gt_empty_group_heading { padding: 0.5px; color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; vertical-align: middle; }
 #wccqyntdzo .gt_from_md> :first-child { margin-top: 0; }
 #wccqyntdzo .gt_from_md> :last-child { margin-bottom: 0; }
 #wccqyntdzo .gt_row { padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; margin: 10px; border-top-style: solid; border-top-width: 1px; border-top-color: #D3D3D3; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; vertical-align: middle; overflow-x: hidden; }
 #wccqyntdzo .gt_stub { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; text-transform: inherit; border-right-style: solid; border-right-width: 2px; border-right-color: #D3D3D3; padding-left: 5px; padding-right: 5px; }
 #wccqyntdzo .gt_indent_1 { text-indent: 5px; }
 #wccqyntdzo .gt_indent_2 { text-indent: calc(5px * 2); }
 #wccqyntdzo .gt_indent_3 { text-indent: calc(5px * 3); }
 #wccqyntdzo .gt_indent_4 { text-indent: calc(5px * 4); }
 #wccqyntdzo .gt_indent_5 { text-indent: calc(5px * 5); }
 #wccqyntdzo .gt_stub_row_group { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; text-transform: inherit; border-right-style: solid; border-right-width: 2px; border-right-color: #D3D3D3; padding-left: 5px; padding-right: 5px; vertical-align: top; }
 #wccqyntdzo .gt_row_group_first td { border-top-width: 2px; }
 #wccqyntdzo .gt_row_group_first th { border-top-width: 2px; }
 #wccqyntdzo .gt_striped { color: #333333; background-color: #F4F4F4; }
 #wccqyntdzo .gt_table_body { border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; }
 #wccqyntdzo .gt_summary_row { color: #333333; background-color: #FFFFFF; text-transform: inherit; padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; }
 #wccqyntdzo .gt_first_summary_row { border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; }
 #wccqyntdzo .gt_last_summary_row_top { border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; }
 #wccqyntdzo .gt_grand_summary_row { color: #333333; background-color: #FFFFFF; text-transform: inherit; padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; }
 #wccqyntdzo .gt_first_grand_summary_row_bottom { border-top-style: double; border-top-width: 6px; border-top-color: #D3D3D3; }
 #wccqyntdzo .gt_last_grand_summary_row_top { border-bottom-style: double; border-bottom-width: 6px; border-bottom-color: #D3D3D3; }
 #wccqyntdzo .gt_sourcenotes { color: #333333; background-color: #FFFFFF; border-bottom-style: none; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; }
 #wccqyntdzo .gt_sourcenote { font-size: 90%; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; text-align: left; }
 #wccqyntdzo .gt_left { text-align: left; }
 #wccqyntdzo .gt_center { text-align: center; }
 #wccqyntdzo .gt_right { text-align: right; font-variant-numeric: tabular-nums; }
 #wccqyntdzo .gt_font_normal { font-weight: normal; }
 #wccqyntdzo .gt_font_bold { font-weight: bold; }
 #wccqyntdzo .gt_font_italic { font-style: italic; }
 #wccqyntdzo .gt_super { font-size: 65%; }
 #wccqyntdzo .gt_footnotes { color: font-color(#FFFFFF); background-color: #FFFFFF; border-bottom-style: none; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; }
 #wccqyntdzo .gt_footnote { margin: 0px; font-size: 90%; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; }
 #wccqyntdzo .gt_sourcenotes { color: #333333; background-color: #FFFFFF; border-bottom-style: none; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; }
 #wccqyntdzo .gt_sourcenote { font-size: 90%; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; text-align: left; }
 #wccqyntdzo .gt_footnote_marks { font-size: 75%; vertical-align: 0.4em; position: initial; }
 #wccqyntdzo .gt_asterisk { font-size: 100%; vertical-align: 0; }
 &#10;</style>

| Out-of-band calibration — 2026 published season         |        |
|---------------------------------------------------------|--------|
| metric                                                  | value  |
| Brier score (all plays)                                 | 0.1045 |
| 20-bin calibration MAE                                  | 0.0143 |
| baseline Brier (constant = play-weighted home-win rate) | 0.2341 |

&#10;</div>

<img src="wp_enrich_files/figure-commonmark/cell-5-output-1.png"
width="420" height="300"
alt="Reliability diagram, 20 bins — predicted in-game probability vs realized outcome frequency." />

<div id="turxgoflrz" style="padding-left:0px;padding-right:0px;padding-top:10px;padding-bottom:10px;overflow-x:auto;overflow-y:auto;width:auto;height:auto;">
<style>
#turxgoflrz table {
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Helvetica Neue', 'Fira Sans', 'Droid Sans', Arial, sans-serif;
          -webkit-font-smoothing: antialiased;
          -moz-osx-font-smoothing: grayscale;
        }
&#10;#turxgoflrz thead, tbody, tfoot, tr, td, th { border-style: none; }
 tr { background-color: transparent; }
#turxgoflrz p { margin: 0; padding: 0; }
 #turxgoflrz .gt_table { display: table; border-collapse: collapse; line-height: normal; margin-left: auto; margin-right: auto; color: #333333; font-size: 16px; font-weight: normal; font-style: normal; background-color: #FFFFFF; width: auto; border-top-style: solid; border-top-width: 2px; border-top-color: #A8A8A8; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #A8A8A8; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; }
 #turxgoflrz .gt_caption { padding-top: 4px; padding-bottom: 4px; }
 #turxgoflrz .gt_title { color: #333333; font-size: 125%; font-weight: initial; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; border-bottom-color: #FFFFFF; border-bottom-width: 0; }
 #turxgoflrz .gt_subtitle { color: #333333; font-size: 85%; font-weight: initial; padding-top: 3px; padding-bottom: 5px; padding-left: 5px; padding-right: 5px; border-top-color: #FFFFFF; border-top-width: 0; }
 #turxgoflrz .gt_heading { background-color: #FFFFFF; text-align: center; border-bottom-color: #FFFFFF; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; }
 #turxgoflrz .gt_bottom_border { border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; }
 #turxgoflrz .gt_col_headings { border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; }
 #turxgoflrz .gt_col_heading { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: normal; text-transform: inherit; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; vertical-align: bottom; padding-top: 5px; padding-bottom: 5px; padding-left: 5px; padding-right: 5px; overflow-x: hidden; }
 #turxgoflrz .gt_column_spanner_outer { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: normal; text-transform: inherit; padding-top: 0; padding-bottom: 0; padding-left: 4px; padding-right: 4px; }
 #turxgoflrz .gt_column_spanner_outer:first-child { padding-left: 0; }
 #turxgoflrz .gt_column_spanner_outer:last-child { padding-right: 0; }
 #turxgoflrz .gt_column_spanner { border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; vertical-align: bottom; padding-top: 5px; padding-bottom: 5px; overflow-x: hidden; display: inline-block; width: 100%; }
 #turxgoflrz .gt_spanner_row { border-bottom-style: hidden; }
 #turxgoflrz .gt_group_heading { padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; text-transform: inherit; border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; vertical-align: middle; text-align: left; }
 #turxgoflrz .gt_empty_group_heading { padding: 0.5px; color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; vertical-align: middle; }
 #turxgoflrz .gt_from_md> :first-child { margin-top: 0; }
 #turxgoflrz .gt_from_md> :last-child { margin-bottom: 0; }
 #turxgoflrz .gt_row { padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; margin: 10px; border-top-style: solid; border-top-width: 1px; border-top-color: #D3D3D3; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; vertical-align: middle; overflow-x: hidden; }
 #turxgoflrz .gt_stub { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; text-transform: inherit; border-right-style: solid; border-right-width: 2px; border-right-color: #D3D3D3; padding-left: 5px; padding-right: 5px; }
 #turxgoflrz .gt_indent_1 { text-indent: 5px; }
 #turxgoflrz .gt_indent_2 { text-indent: calc(5px * 2); }
 #turxgoflrz .gt_indent_3 { text-indent: calc(5px * 3); }
 #turxgoflrz .gt_indent_4 { text-indent: calc(5px * 4); }
 #turxgoflrz .gt_indent_5 { text-indent: calc(5px * 5); }
 #turxgoflrz .gt_stub_row_group { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; text-transform: inherit; border-right-style: solid; border-right-width: 2px; border-right-color: #D3D3D3; padding-left: 5px; padding-right: 5px; vertical-align: top; }
 #turxgoflrz .gt_row_group_first td { border-top-width: 2px; }
 #turxgoflrz .gt_row_group_first th { border-top-width: 2px; }
 #turxgoflrz .gt_striped { color: #333333; background-color: #F4F4F4; }
 #turxgoflrz .gt_table_body { border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; }
 #turxgoflrz .gt_summary_row { color: #333333; background-color: #FFFFFF; text-transform: inherit; padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; }
 #turxgoflrz .gt_first_summary_row { border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; }
 #turxgoflrz .gt_last_summary_row_top { border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; }
 #turxgoflrz .gt_grand_summary_row { color: #333333; background-color: #FFFFFF; text-transform: inherit; padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; }
 #turxgoflrz .gt_first_grand_summary_row_bottom { border-top-style: double; border-top-width: 6px; border-top-color: #D3D3D3; }
 #turxgoflrz .gt_last_grand_summary_row_top { border-bottom-style: double; border-bottom-width: 6px; border-bottom-color: #D3D3D3; }
 #turxgoflrz .gt_sourcenotes { color: #333333; background-color: #FFFFFF; border-bottom-style: none; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; }
 #turxgoflrz .gt_sourcenote { font-size: 90%; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; text-align: left; }
 #turxgoflrz .gt_left { text-align: left; }
 #turxgoflrz .gt_center { text-align: center; }
 #turxgoflrz .gt_right { text-align: right; font-variant-numeric: tabular-nums; }
 #turxgoflrz .gt_font_normal { font-weight: normal; }
 #turxgoflrz .gt_font_bold { font-weight: bold; }
 #turxgoflrz .gt_font_italic { font-style: italic; }
 #turxgoflrz .gt_super { font-size: 65%; }
 #turxgoflrz .gt_footnotes { color: font-color(#FFFFFF); background-color: #FFFFFF; border-bottom-style: none; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; }
 #turxgoflrz .gt_footnote { margin: 0px; font-size: 90%; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; }
 #turxgoflrz .gt_sourcenotes { color: #333333; background-color: #FFFFFF; border-bottom-style: none; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; }
 #turxgoflrz .gt_sourcenote { font-size: 90%; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; text-align: left; }
 #turxgoflrz .gt_footnote_marks { font-size: 75%; vertical-align: 0.4em; position: initial; }
 #turxgoflrz .gt_asterisk { font-size: 100%; vertical-align: 0; }
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

<div id="nvcfoyidzk" style="padding-left:0px;padding-right:0px;padding-top:10px;padding-bottom:10px;overflow-x:auto;overflow-y:auto;width:auto;height:auto;">
<style>
#nvcfoyidzk table {
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Helvetica Neue', 'Fira Sans', 'Droid Sans', Arial, sans-serif;
          -webkit-font-smoothing: antialiased;
          -moz-osx-font-smoothing: grayscale;
        }
&#10;#nvcfoyidzk thead, tbody, tfoot, tr, td, th { border-style: none; }
 tr { background-color: transparent; }
#nvcfoyidzk p { margin: 0; padding: 0; }
 #nvcfoyidzk .gt_table { display: table; border-collapse: collapse; line-height: normal; margin-left: auto; margin-right: auto; color: #333333; font-size: 16px; font-weight: normal; font-style: normal; background-color: #FFFFFF; width: auto; border-top-style: solid; border-top-width: 2px; border-top-color: #A8A8A8; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #A8A8A8; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; }
 #nvcfoyidzk .gt_caption { padding-top: 4px; padding-bottom: 4px; }
 #nvcfoyidzk .gt_title { color: #333333; font-size: 125%; font-weight: initial; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; border-bottom-color: #FFFFFF; border-bottom-width: 0; }
 #nvcfoyidzk .gt_subtitle { color: #333333; font-size: 85%; font-weight: initial; padding-top: 3px; padding-bottom: 5px; padding-left: 5px; padding-right: 5px; border-top-color: #FFFFFF; border-top-width: 0; }
 #nvcfoyidzk .gt_heading { background-color: #FFFFFF; text-align: center; border-bottom-color: #FFFFFF; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; }
 #nvcfoyidzk .gt_bottom_border { border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; }
 #nvcfoyidzk .gt_col_headings { border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; }
 #nvcfoyidzk .gt_col_heading { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: normal; text-transform: inherit; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; vertical-align: bottom; padding-top: 5px; padding-bottom: 5px; padding-left: 5px; padding-right: 5px; overflow-x: hidden; }
 #nvcfoyidzk .gt_column_spanner_outer { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: normal; text-transform: inherit; padding-top: 0; padding-bottom: 0; padding-left: 4px; padding-right: 4px; }
 #nvcfoyidzk .gt_column_spanner_outer:first-child { padding-left: 0; }
 #nvcfoyidzk .gt_column_spanner_outer:last-child { padding-right: 0; }
 #nvcfoyidzk .gt_column_spanner { border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; vertical-align: bottom; padding-top: 5px; padding-bottom: 5px; overflow-x: hidden; display: inline-block; width: 100%; }
 #nvcfoyidzk .gt_spanner_row { border-bottom-style: hidden; }
 #nvcfoyidzk .gt_group_heading { padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; text-transform: inherit; border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; vertical-align: middle; text-align: left; }
 #nvcfoyidzk .gt_empty_group_heading { padding: 0.5px; color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; vertical-align: middle; }
 #nvcfoyidzk .gt_from_md> :first-child { margin-top: 0; }
 #nvcfoyidzk .gt_from_md> :last-child { margin-bottom: 0; }
 #nvcfoyidzk .gt_row { padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; margin: 10px; border-top-style: solid; border-top-width: 1px; border-top-color: #D3D3D3; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; vertical-align: middle; overflow-x: hidden; }
 #nvcfoyidzk .gt_stub { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; text-transform: inherit; border-right-style: solid; border-right-width: 2px; border-right-color: #D3D3D3; padding-left: 5px; padding-right: 5px; }
 #nvcfoyidzk .gt_indent_1 { text-indent: 5px; }
 #nvcfoyidzk .gt_indent_2 { text-indent: calc(5px * 2); }
 #nvcfoyidzk .gt_indent_3 { text-indent: calc(5px * 3); }
 #nvcfoyidzk .gt_indent_4 { text-indent: calc(5px * 4); }
 #nvcfoyidzk .gt_indent_5 { text-indent: calc(5px * 5); }
 #nvcfoyidzk .gt_stub_row_group { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; text-transform: inherit; border-right-style: solid; border-right-width: 2px; border-right-color: #D3D3D3; padding-left: 5px; padding-right: 5px; vertical-align: top; }
 #nvcfoyidzk .gt_row_group_first td { border-top-width: 2px; }
 #nvcfoyidzk .gt_row_group_first th { border-top-width: 2px; }
 #nvcfoyidzk .gt_striped { color: #333333; background-color: #F4F4F4; }
 #nvcfoyidzk .gt_table_body { border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; }
 #nvcfoyidzk .gt_summary_row { color: #333333; background-color: #FFFFFF; text-transform: inherit; padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; }
 #nvcfoyidzk .gt_first_summary_row { border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; }
 #nvcfoyidzk .gt_last_summary_row_top { border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; }
 #nvcfoyidzk .gt_grand_summary_row { color: #333333; background-color: #FFFFFF; text-transform: inherit; padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; }
 #nvcfoyidzk .gt_first_grand_summary_row_bottom { border-top-style: double; border-top-width: 6px; border-top-color: #D3D3D3; }
 #nvcfoyidzk .gt_last_grand_summary_row_top { border-bottom-style: double; border-bottom-width: 6px; border-bottom-color: #D3D3D3; }
 #nvcfoyidzk .gt_sourcenotes { color: #333333; background-color: #FFFFFF; border-bottom-style: none; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; }
 #nvcfoyidzk .gt_sourcenote { font-size: 90%; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; text-align: left; }
 #nvcfoyidzk .gt_left { text-align: left; }
 #nvcfoyidzk .gt_center { text-align: center; }
 #nvcfoyidzk .gt_right { text-align: right; font-variant-numeric: tabular-nums; }
 #nvcfoyidzk .gt_font_normal { font-weight: normal; }
 #nvcfoyidzk .gt_font_bold { font-weight: bold; }
 #nvcfoyidzk .gt_font_italic { font-style: italic; }
 #nvcfoyidzk .gt_super { font-size: 65%; }
 #nvcfoyidzk .gt_footnotes { color: font-color(#FFFFFF); background-color: #FFFFFF; border-bottom-style: none; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; }
 #nvcfoyidzk .gt_footnote { margin: 0px; font-size: 90%; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; }
 #nvcfoyidzk .gt_sourcenotes { color: #333333; background-color: #FFFFFF; border-bottom-style: none; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; }
 #nvcfoyidzk .gt_sourcenote { font-size: 90%; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; text-align: left; }
 #nvcfoyidzk .gt_footnote_marks { font-size: 75%; vertical-align: 0.4em; position: initial; }
 #nvcfoyidzk .gt_asterisk { font-size: 100%; vertical-align: 0; }
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
computed at render time – the release asset lacks the WP columns.

<div id="xxyisaicog" style="padding-left:0px;padding-right:0px;padding-top:10px;padding-bottom:10px;overflow-x:auto;overflow-y:auto;width:auto;height:auto;">
<style>
#xxyisaicog table {
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Helvetica Neue', 'Fira Sans', 'Droid Sans', Arial, sans-serif;
          -webkit-font-smoothing: antialiased;
          -moz-osx-font-smoothing: grayscale;
        }
&#10;#xxyisaicog thead, tbody, tfoot, tr, td, th { border-style: none; }
 tr { background-color: transparent; }
#xxyisaicog p { margin: 0; padding: 0; }
 #xxyisaicog .gt_table { display: table; border-collapse: collapse; line-height: normal; margin-left: auto; margin-right: auto; color: #333333; font-size: 16px; font-weight: normal; font-style: normal; background-color: #FFFFFF; width: auto; border-top-style: solid; border-top-width: 2px; border-top-color: #A8A8A8; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #A8A8A8; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; }
 #xxyisaicog .gt_caption { padding-top: 4px; padding-bottom: 4px; }
 #xxyisaicog .gt_title { color: #333333; font-size: 125%; font-weight: initial; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; border-bottom-color: #FFFFFF; border-bottom-width: 0; }
 #xxyisaicog .gt_subtitle { color: #333333; font-size: 85%; font-weight: initial; padding-top: 3px; padding-bottom: 5px; padding-left: 5px; padding-right: 5px; border-top-color: #FFFFFF; border-top-width: 0; }
 #xxyisaicog .gt_heading { background-color: #FFFFFF; text-align: center; border-bottom-color: #FFFFFF; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; }
 #xxyisaicog .gt_bottom_border { border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; }
 #xxyisaicog .gt_col_headings { border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; }
 #xxyisaicog .gt_col_heading { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: normal; text-transform: inherit; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; vertical-align: bottom; padding-top: 5px; padding-bottom: 5px; padding-left: 5px; padding-right: 5px; overflow-x: hidden; }
 #xxyisaicog .gt_column_spanner_outer { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: normal; text-transform: inherit; padding-top: 0; padding-bottom: 0; padding-left: 4px; padding-right: 4px; }
 #xxyisaicog .gt_column_spanner_outer:first-child { padding-left: 0; }
 #xxyisaicog .gt_column_spanner_outer:last-child { padding-right: 0; }
 #xxyisaicog .gt_column_spanner { border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; vertical-align: bottom; padding-top: 5px; padding-bottom: 5px; overflow-x: hidden; display: inline-block; width: 100%; }
 #xxyisaicog .gt_spanner_row { border-bottom-style: hidden; }
 #xxyisaicog .gt_group_heading { padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; text-transform: inherit; border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; vertical-align: middle; text-align: left; }
 #xxyisaicog .gt_empty_group_heading { padding: 0.5px; color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; vertical-align: middle; }
 #xxyisaicog .gt_from_md> :first-child { margin-top: 0; }
 #xxyisaicog .gt_from_md> :last-child { margin-bottom: 0; }
 #xxyisaicog .gt_row { padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; margin: 10px; border-top-style: solid; border-top-width: 1px; border-top-color: #D3D3D3; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; vertical-align: middle; overflow-x: hidden; }
 #xxyisaicog .gt_stub { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; text-transform: inherit; border-right-style: solid; border-right-width: 2px; border-right-color: #D3D3D3; padding-left: 5px; padding-right: 5px; }
 #xxyisaicog .gt_indent_1 { text-indent: 5px; }
 #xxyisaicog .gt_indent_2 { text-indent: calc(5px * 2); }
 #xxyisaicog .gt_indent_3 { text-indent: calc(5px * 3); }
 #xxyisaicog .gt_indent_4 { text-indent: calc(5px * 4); }
 #xxyisaicog .gt_indent_5 { text-indent: calc(5px * 5); }
 #xxyisaicog .gt_stub_row_group { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; text-transform: inherit; border-right-style: solid; border-right-width: 2px; border-right-color: #D3D3D3; padding-left: 5px; padding-right: 5px; vertical-align: top; }
 #xxyisaicog .gt_row_group_first td { border-top-width: 2px; }
 #xxyisaicog .gt_row_group_first th { border-top-width: 2px; }
 #xxyisaicog .gt_striped { color: #333333; background-color: #F4F4F4; }
 #xxyisaicog .gt_table_body { border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; }
 #xxyisaicog .gt_summary_row { color: #333333; background-color: #FFFFFF; text-transform: inherit; padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; }
 #xxyisaicog .gt_first_summary_row { border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; }
 #xxyisaicog .gt_last_summary_row_top { border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; }
 #xxyisaicog .gt_grand_summary_row { color: #333333; background-color: #FFFFFF; text-transform: inherit; padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; }
 #xxyisaicog .gt_first_grand_summary_row_bottom { border-top-style: double; border-top-width: 6px; border-top-color: #D3D3D3; }
 #xxyisaicog .gt_last_grand_summary_row_top { border-bottom-style: double; border-bottom-width: 6px; border-bottom-color: #D3D3D3; }
 #xxyisaicog .gt_sourcenotes { color: #333333; background-color: #FFFFFF; border-bottom-style: none; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; }
 #xxyisaicog .gt_sourcenote { font-size: 90%; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; text-align: left; }
 #xxyisaicog .gt_left { text-align: left; }
 #xxyisaicog .gt_center { text-align: center; }
 #xxyisaicog .gt_right { text-align: right; font-variant-numeric: tabular-nums; }
 #xxyisaicog .gt_font_normal { font-weight: normal; }
 #xxyisaicog .gt_font_bold { font-weight: bold; }
 #xxyisaicog .gt_font_italic { font-style: italic; }
 #xxyisaicog .gt_super { font-size: 65%; }
 #xxyisaicog .gt_footnotes { color: font-color(#FFFFFF); background-color: #FFFFFF; border-bottom-style: none; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; }
 #xxyisaicog .gt_footnote { margin: 0px; font-size: 90%; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; }
 #xxyisaicog .gt_sourcenotes { color: #333333; background-color: #FFFFFF; border-bottom-style: none; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; }
 #xxyisaicog .gt_sourcenote { font-size: 90%; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; text-align: left; }
 #xxyisaicog .gt_footnote_marks { font-size: 75%; vertical-align: 0.4em; position: initial; }
 #xxyisaicog .gt_asterisk { font-size: 100%; vertical-align: 0; }
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
