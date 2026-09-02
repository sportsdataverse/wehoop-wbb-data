# WBB player value — box Plus/Minus


Per-player box Plus/Minus publishes on the `wbb_player_value` tag
(`box_obpm` / `box_dbpm` / `box_bpm`): a box-score value model over the
published player/team season stats, sharing the design of the WBB
player-value spine in sdv-py (oracle-gated where trained). Per-100 box
features are standardized and scored through ridge coefficients fit at
the team level, then a uniform team adjustment makes each team’s
minutes-weighted player scores sum to its adjusted efficiency margin;
offensive and defensive components are estimated separately and summed.
It is compute-on-demand — every run recomputes from the current
published season assets, so a data correction upstream flows through on
the next publish, and each publish writes a card sidecar plus the fitted
coefficient vector.

Box Plus/Minus and on/off RAPM (the `ncaa_wbb_rapm` model in the NCAA
hoops repos) deliberately measure different things: BPM sees only what
reaches the box score and is therefore stable at small samples but blind
to screening, defensive attention, and everything else the box misses;
RAPM sees all of it but drowns in noise for low-minute players. The two
are cross-references, not substitutes — the natural hybrid (an SPM-prior
RAPM, as the NBA impact suite builds) is the catalogued next step.

Everything below is computed at render time from the published release
assets — the exact frames consumers download.

## Training data

<div id="iovsjrcxtc" style="padding-left:0px;padding-right:0px;padding-top:10px;padding-bottom:10px;overflow-x:auto;overflow-y:auto;width:auto;height:auto;">
<style>
#iovsjrcxtc table {
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Helvetica Neue', 'Fira Sans', 'Droid Sans', Arial, sans-serif;
          -webkit-font-smoothing: antialiased;
          -moz-osx-font-smoothing: grayscale;
        }
&#10;#iovsjrcxtc thead, tbody, tfoot, tr, td, th { border-style: none; }
 tr { background-color: transparent; }
#iovsjrcxtc p { margin: 0; padding: 0; }
 #iovsjrcxtc .gt_table { display: table; border-collapse: collapse; line-height: normal; margin-left: auto; margin-right: auto; color: #333333; font-size: 16px; font-weight: normal; font-style: normal; background-color: #FFFFFF; width: auto; border-top-style: solid; border-top-width: 2px; border-top-color: #A8A8A8; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #A8A8A8; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; }
 #iovsjrcxtc .gt_caption { padding-top: 4px; padding-bottom: 4px; }
 #iovsjrcxtc .gt_title { color: #333333; font-size: 125%; font-weight: initial; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; border-bottom-color: #FFFFFF; border-bottom-width: 0; }
 #iovsjrcxtc .gt_subtitle { color: #333333; font-size: 85%; font-weight: initial; padding-top: 3px; padding-bottom: 5px; padding-left: 5px; padding-right: 5px; border-top-color: #FFFFFF; border-top-width: 0; }
 #iovsjrcxtc .gt_heading { background-color: #FFFFFF; text-align: center; border-bottom-color: #FFFFFF; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; }
 #iovsjrcxtc .gt_bottom_border { border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; }
 #iovsjrcxtc .gt_col_headings { border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; }
 #iovsjrcxtc .gt_col_heading { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: normal; text-transform: inherit; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; vertical-align: bottom; padding-top: 5px; padding-bottom: 5px; padding-left: 5px; padding-right: 5px; overflow-x: hidden; }
 #iovsjrcxtc .gt_column_spanner_outer { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: normal; text-transform: inherit; padding-top: 0; padding-bottom: 0; padding-left: 4px; padding-right: 4px; }
 #iovsjrcxtc .gt_column_spanner_outer:first-child { padding-left: 0; }
 #iovsjrcxtc .gt_column_spanner_outer:last-child { padding-right: 0; }
 #iovsjrcxtc .gt_column_spanner { border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; vertical-align: bottom; padding-top: 5px; padding-bottom: 5px; overflow-x: hidden; display: inline-block; width: 100%; }
 #iovsjrcxtc .gt_spanner_row { border-bottom-style: hidden; }
 #iovsjrcxtc .gt_group_heading { padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; text-transform: inherit; border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; vertical-align: middle; text-align: left; }
 #iovsjrcxtc .gt_empty_group_heading { padding: 0.5px; color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; vertical-align: middle; }
 #iovsjrcxtc .gt_from_md> :first-child { margin-top: 0; }
 #iovsjrcxtc .gt_from_md> :last-child { margin-bottom: 0; }
 #iovsjrcxtc .gt_row { padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; margin: 10px; border-top-style: solid; border-top-width: 1px; border-top-color: #D3D3D3; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; vertical-align: middle; overflow-x: hidden; }
 #iovsjrcxtc .gt_stub { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; text-transform: inherit; border-right-style: solid; border-right-width: 2px; border-right-color: #D3D3D3; padding-left: 5px; padding-right: 5px; }
 #iovsjrcxtc .gt_indent_1 { text-indent: 5px; }
 #iovsjrcxtc .gt_indent_2 { text-indent: calc(5px * 2); }
 #iovsjrcxtc .gt_indent_3 { text-indent: calc(5px * 3); }
 #iovsjrcxtc .gt_indent_4 { text-indent: calc(5px * 4); }
 #iovsjrcxtc .gt_indent_5 { text-indent: calc(5px * 5); }
 #iovsjrcxtc .gt_stub_row_group { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; text-transform: inherit; border-right-style: solid; border-right-width: 2px; border-right-color: #D3D3D3; padding-left: 5px; padding-right: 5px; vertical-align: top; }
 #iovsjrcxtc .gt_row_group_first td { border-top-width: 2px; }
 #iovsjrcxtc .gt_row_group_first th { border-top-width: 2px; }
 #iovsjrcxtc .gt_striped { color: #333333; background-color: #F4F4F4; }
 #iovsjrcxtc .gt_table_body { border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; }
 #iovsjrcxtc .gt_summary_row { color: #333333; background-color: #FFFFFF; text-transform: inherit; padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; }
 #iovsjrcxtc .gt_first_summary_row { border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; }
 #iovsjrcxtc .gt_last_summary_row_top { border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; }
 #iovsjrcxtc .gt_grand_summary_row { color: #333333; background-color: #FFFFFF; text-transform: inherit; padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; }
 #iovsjrcxtc .gt_first_grand_summary_row_bottom { border-top-style: double; border-top-width: 6px; border-top-color: #D3D3D3; }
 #iovsjrcxtc .gt_last_grand_summary_row_top { border-bottom-style: double; border-bottom-width: 6px; border-bottom-color: #D3D3D3; }
 #iovsjrcxtc .gt_sourcenotes { color: #333333; background-color: #FFFFFF; border-bottom-style: none; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; }
 #iovsjrcxtc .gt_sourcenote { font-size: 90%; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; text-align: left; }
 #iovsjrcxtc .gt_left { text-align: left; }
 #iovsjrcxtc .gt_center { text-align: center; }
 #iovsjrcxtc .gt_right { text-align: right; font-variant-numeric: tabular-nums; }
 #iovsjrcxtc .gt_font_normal { font-weight: normal; }
 #iovsjrcxtc .gt_font_bold { font-weight: bold; }
 #iovsjrcxtc .gt_font_italic { font-style: italic; }
 #iovsjrcxtc .gt_super { font-size: 65%; }
 #iovsjrcxtc .gt_footnotes { color: font-color(#FFFFFF); background-color: #FFFFFF; border-bottom-style: none; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; }
 #iovsjrcxtc .gt_footnote { margin: 0px; font-size: 90%; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; }
 #iovsjrcxtc .gt_sourcenotes { color: #333333; background-color: #FFFFFF; border-bottom-style: none; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; }
 #iovsjrcxtc .gt_sourcenote { font-size: 90%; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; text-align: left; }
 #iovsjrcxtc .gt_footnote_marks { font-size: 75%; vertical-align: 0.4em; position: initial; }
 #iovsjrcxtc .gt_asterisk { font-size: 100%; vertical-align: 0; }
 &#10;</style>

| Published wbb_player_value assets, by season |  |  |  |
|----|----|----|----|
| computed at render time from the release; qualified = min \>= 300 |  |  |  |
| season | players | total_minutes | qualified_players |
| 2014 | 4000 | 691,332 | 605 |
| 2015 | 3954 | 634,556 | 597 |
| 2016 | 4141 | 716,100 | 626 |
| 2017 | 4674 | 2,109,874 | 2793 |
| 2018 | 4444 | 2,124,684 | 2775 |
| 2019 | 4574 | 2,156,612 | 2849 |
| 2020 | 6811 | 2,190,577 | 2814 |
| 2021 | 5522 | 1,540,568 | 2248 |
| 2022 | 7410 | 2,217,684 | 2899 |
| 2023 | 7289 | 2,340,580 | 2981 |
| 2024 | 7746 | 2,373,446 | 3008 |
| 2025 | 7841 | 2,264,711 | 2920 |
| 2026 | 8305 | 2,426,836 | 3012 |

&#10;</div>

## Exploratory data analysis

<img src="player_value_files/figure-commonmark/cell-4-output-1.png"
width="420" height="300"
alt="Box BPM distribution, latest season — the full player pool vs the qualified pool. The unfiltered frame carries heavy low-minute noise by design; the flag marks it, it never removes it." />

<img src="player_value_files/figure-commonmark/cell-5-output-1.png"
width="420" height="300"
alt="Minutes vs |BPM|: with no shrinkage prior, extreme values concentrate at LOW minutes. The vertical line is the qualified floor." />

<div id="gruvsqbwvc" style="padding-left:0px;padding-right:0px;padding-top:10px;padding-bottom:10px;overflow-x:auto;overflow-y:auto;width:auto;height:auto;">
<style>
#gruvsqbwvc table {
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Helvetica Neue', 'Fira Sans', 'Droid Sans', Arial, sans-serif;
          -webkit-font-smoothing: antialiased;
          -moz-osx-font-smoothing: grayscale;
        }
&#10;#gruvsqbwvc thead, tbody, tfoot, tr, td, th { border-style: none; }
 tr { background-color: transparent; }
#gruvsqbwvc p { margin: 0; padding: 0; }
 #gruvsqbwvc .gt_table { display: table; border-collapse: collapse; line-height: normal; margin-left: auto; margin-right: auto; color: #333333; font-size: 16px; font-weight: normal; font-style: normal; background-color: #FFFFFF; width: auto; border-top-style: solid; border-top-width: 2px; border-top-color: #A8A8A8; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #A8A8A8; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; }
 #gruvsqbwvc .gt_caption { padding-top: 4px; padding-bottom: 4px; }
 #gruvsqbwvc .gt_title { color: #333333; font-size: 125%; font-weight: initial; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; border-bottom-color: #FFFFFF; border-bottom-width: 0; }
 #gruvsqbwvc .gt_subtitle { color: #333333; font-size: 85%; font-weight: initial; padding-top: 3px; padding-bottom: 5px; padding-left: 5px; padding-right: 5px; border-top-color: #FFFFFF; border-top-width: 0; }
 #gruvsqbwvc .gt_heading { background-color: #FFFFFF; text-align: center; border-bottom-color: #FFFFFF; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; }
 #gruvsqbwvc .gt_bottom_border { border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; }
 #gruvsqbwvc .gt_col_headings { border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; }
 #gruvsqbwvc .gt_col_heading { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: normal; text-transform: inherit; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; vertical-align: bottom; padding-top: 5px; padding-bottom: 5px; padding-left: 5px; padding-right: 5px; overflow-x: hidden; }
 #gruvsqbwvc .gt_column_spanner_outer { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: normal; text-transform: inherit; padding-top: 0; padding-bottom: 0; padding-left: 4px; padding-right: 4px; }
 #gruvsqbwvc .gt_column_spanner_outer:first-child { padding-left: 0; }
 #gruvsqbwvc .gt_column_spanner_outer:last-child { padding-right: 0; }
 #gruvsqbwvc .gt_column_spanner { border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; vertical-align: bottom; padding-top: 5px; padding-bottom: 5px; overflow-x: hidden; display: inline-block; width: 100%; }
 #gruvsqbwvc .gt_spanner_row { border-bottom-style: hidden; }
 #gruvsqbwvc .gt_group_heading { padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; text-transform: inherit; border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; vertical-align: middle; text-align: left; }
 #gruvsqbwvc .gt_empty_group_heading { padding: 0.5px; color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; vertical-align: middle; }
 #gruvsqbwvc .gt_from_md> :first-child { margin-top: 0; }
 #gruvsqbwvc .gt_from_md> :last-child { margin-bottom: 0; }
 #gruvsqbwvc .gt_row { padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; margin: 10px; border-top-style: solid; border-top-width: 1px; border-top-color: #D3D3D3; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; vertical-align: middle; overflow-x: hidden; }
 #gruvsqbwvc .gt_stub { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; text-transform: inherit; border-right-style: solid; border-right-width: 2px; border-right-color: #D3D3D3; padding-left: 5px; padding-right: 5px; }
 #gruvsqbwvc .gt_indent_1 { text-indent: 5px; }
 #gruvsqbwvc .gt_indent_2 { text-indent: calc(5px * 2); }
 #gruvsqbwvc .gt_indent_3 { text-indent: calc(5px * 3); }
 #gruvsqbwvc .gt_indent_4 { text-indent: calc(5px * 4); }
 #gruvsqbwvc .gt_indent_5 { text-indent: calc(5px * 5); }
 #gruvsqbwvc .gt_stub_row_group { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; text-transform: inherit; border-right-style: solid; border-right-width: 2px; border-right-color: #D3D3D3; padding-left: 5px; padding-right: 5px; vertical-align: top; }
 #gruvsqbwvc .gt_row_group_first td { border-top-width: 2px; }
 #gruvsqbwvc .gt_row_group_first th { border-top-width: 2px; }
 #gruvsqbwvc .gt_striped { color: #333333; background-color: #F4F4F4; }
 #gruvsqbwvc .gt_table_body { border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; }
 #gruvsqbwvc .gt_summary_row { color: #333333; background-color: #FFFFFF; text-transform: inherit; padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; }
 #gruvsqbwvc .gt_first_summary_row { border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; }
 #gruvsqbwvc .gt_last_summary_row_top { border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; }
 #gruvsqbwvc .gt_grand_summary_row { color: #333333; background-color: #FFFFFF; text-transform: inherit; padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; }
 #gruvsqbwvc .gt_first_grand_summary_row_bottom { border-top-style: double; border-top-width: 6px; border-top-color: #D3D3D3; }
 #gruvsqbwvc .gt_last_grand_summary_row_top { border-bottom-style: double; border-bottom-width: 6px; border-bottom-color: #D3D3D3; }
 #gruvsqbwvc .gt_sourcenotes { color: #333333; background-color: #FFFFFF; border-bottom-style: none; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; }
 #gruvsqbwvc .gt_sourcenote { font-size: 90%; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; text-align: left; }
 #gruvsqbwvc .gt_left { text-align: left; }
 #gruvsqbwvc .gt_center { text-align: center; }
 #gruvsqbwvc .gt_right { text-align: right; font-variant-numeric: tabular-nums; }
 #gruvsqbwvc .gt_font_normal { font-weight: normal; }
 #gruvsqbwvc .gt_font_bold { font-weight: bold; }
 #gruvsqbwvc .gt_font_italic { font-style: italic; }
 #gruvsqbwvc .gt_super { font-size: 65%; }
 #gruvsqbwvc .gt_footnotes { color: font-color(#FFFFFF); background-color: #FFFFFF; border-bottom-style: none; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; }
 #gruvsqbwvc .gt_footnote { margin: 0px; font-size: 90%; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; }
 #gruvsqbwvc .gt_sourcenotes { color: #333333; background-color: #FFFFFF; border-bottom-style: none; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; }
 #gruvsqbwvc .gt_sourcenote { font-size: 90%; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; text-align: left; }
 #gruvsqbwvc .gt_footnote_marks { font-size: 75%; vertical-align: 0.4em; position: initial; }
 #gruvsqbwvc .gt_asterisk { font-size: 100%; vertical-align: 0; }
 &#10;</style>

| How the qualified floor was set — sd(box_bpm) by minutes bin, all published seasons |  |  |  |  |
|----|----|----|----|----|
| the floor is the first bin whose sd sits within 2% of the 600–800 plateau (nan); every table below uses the flag |  |  |  |  |
| minutes_bin | players | sd_box_bpm | abs_bpm_p99 | vs_600_800_plateau |
| 0-25 | 18,551 | <na> | 24.07 | <na> |
| 25-50 | 9,231 | <na> | 19.54 | <na> |
| 50-75 | 4,300 | <na> | 17.26 | <na> |
| 75-100 | 2,765 | <na> | 19.18 | <na> |
| 100-150 | 4,127 | <na> | <na> | <na> |
| 150-200 | 2,982 | <na> | <na> | <na> |
| 200-250 | 2,488 | <na> | <na> | <na> |
| 250-300 | 2,183 | <na> | <na> | <na> |
| 300-350 | 2,134 | <na> | <na> | <na> |
| 350-400 | 2,064 | <na> | <na> | <na> |
| 400-500 | 4,050 | <na> | <na> | <na> |
| 500-600 | 4,042 | <na> | <na> | <na> |
| 600-800 | 7,802 | <na> | <na> | <na> |
| 800-1000 | 6,956 | <na> | <na> | <na> |
| 1000-1400 | 3,036 | <na> | <na> | <na> |

&#10;</div>

Flag source in this render: derived at render time as min \>= 300 (the
published frames predate the flag).

<img src="player_value_files/figure-commonmark/cell-7-output-1.png"
width="420" height="300"
alt="Offense vs defense components, qualified players, latest season." />

The minutes-vs-\|BPM\| funnel is this model’s most important
consumer-facing fact, shown rather than footnoted: the published frame
keeps **every** player, so the most extreme values in the file belong to
20-minute seasons. The additive `qualified` flag encodes the floor the
funnel itself justifies — the bin where the spread of BPM stops
shrinking — so a consumer filters with one boolean instead of
re-deriving a threshold. The engine’s own fit floor (`min_minutes` in
the artifact) governs only the team-sum weights and is lower; the two
floors answer different questions.

## Coefficient importance

Coefficients from the bundled sdv-py artifact (the sidecar is not on the
release yet); fit on seasons \[2025, 2026\] (ridge λ offense 3.0,
defense 3.0; z-clip 4.0; fit floor 150.0 minutes).

<div id="vkwhjjxiec" style="padding-left:0px;padding-right:0px;padding-top:10px;padding-bottom:10px;overflow-x:auto;overflow-y:auto;width:auto;height:auto;">
<style>
#vkwhjjxiec table {
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Helvetica Neue', 'Fira Sans', 'Droid Sans', Arial, sans-serif;
          -webkit-font-smoothing: antialiased;
          -moz-osx-font-smoothing: grayscale;
        }
&#10;#vkwhjjxiec thead, tbody, tfoot, tr, td, th { border-style: none; }
 tr { background-color: transparent; }
#vkwhjjxiec p { margin: 0; padding: 0; }
 #vkwhjjxiec .gt_table { display: table; border-collapse: collapse; line-height: normal; margin-left: auto; margin-right: auto; color: #333333; font-size: 16px; font-weight: normal; font-style: normal; background-color: #FFFFFF; width: auto; border-top-style: solid; border-top-width: 2px; border-top-color: #A8A8A8; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #A8A8A8; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; }
 #vkwhjjxiec .gt_caption { padding-top: 4px; padding-bottom: 4px; }
 #vkwhjjxiec .gt_title { color: #333333; font-size: 125%; font-weight: initial; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; border-bottom-color: #FFFFFF; border-bottom-width: 0; }
 #vkwhjjxiec .gt_subtitle { color: #333333; font-size: 85%; font-weight: initial; padding-top: 3px; padding-bottom: 5px; padding-left: 5px; padding-right: 5px; border-top-color: #FFFFFF; border-top-width: 0; }
 #vkwhjjxiec .gt_heading { background-color: #FFFFFF; text-align: center; border-bottom-color: #FFFFFF; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; }
 #vkwhjjxiec .gt_bottom_border { border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; }
 #vkwhjjxiec .gt_col_headings { border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; }
 #vkwhjjxiec .gt_col_heading { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: normal; text-transform: inherit; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; vertical-align: bottom; padding-top: 5px; padding-bottom: 5px; padding-left: 5px; padding-right: 5px; overflow-x: hidden; }
 #vkwhjjxiec .gt_column_spanner_outer { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: normal; text-transform: inherit; padding-top: 0; padding-bottom: 0; padding-left: 4px; padding-right: 4px; }
 #vkwhjjxiec .gt_column_spanner_outer:first-child { padding-left: 0; }
 #vkwhjjxiec .gt_column_spanner_outer:last-child { padding-right: 0; }
 #vkwhjjxiec .gt_column_spanner { border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; vertical-align: bottom; padding-top: 5px; padding-bottom: 5px; overflow-x: hidden; display: inline-block; width: 100%; }
 #vkwhjjxiec .gt_spanner_row { border-bottom-style: hidden; }
 #vkwhjjxiec .gt_group_heading { padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; text-transform: inherit; border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; vertical-align: middle; text-align: left; }
 #vkwhjjxiec .gt_empty_group_heading { padding: 0.5px; color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; vertical-align: middle; }
 #vkwhjjxiec .gt_from_md> :first-child { margin-top: 0; }
 #vkwhjjxiec .gt_from_md> :last-child { margin-bottom: 0; }
 #vkwhjjxiec .gt_row { padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; margin: 10px; border-top-style: solid; border-top-width: 1px; border-top-color: #D3D3D3; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; vertical-align: middle; overflow-x: hidden; }
 #vkwhjjxiec .gt_stub { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; text-transform: inherit; border-right-style: solid; border-right-width: 2px; border-right-color: #D3D3D3; padding-left: 5px; padding-right: 5px; }
 #vkwhjjxiec .gt_indent_1 { text-indent: 5px; }
 #vkwhjjxiec .gt_indent_2 { text-indent: calc(5px * 2); }
 #vkwhjjxiec .gt_indent_3 { text-indent: calc(5px * 3); }
 #vkwhjjxiec .gt_indent_4 { text-indent: calc(5px * 4); }
 #vkwhjjxiec .gt_indent_5 { text-indent: calc(5px * 5); }
 #vkwhjjxiec .gt_stub_row_group { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; text-transform: inherit; border-right-style: solid; border-right-width: 2px; border-right-color: #D3D3D3; padding-left: 5px; padding-right: 5px; vertical-align: top; }
 #vkwhjjxiec .gt_row_group_first td { border-top-width: 2px; }
 #vkwhjjxiec .gt_row_group_first th { border-top-width: 2px; }
 #vkwhjjxiec .gt_striped { color: #333333; background-color: #F4F4F4; }
 #vkwhjjxiec .gt_table_body { border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; }
 #vkwhjjxiec .gt_summary_row { color: #333333; background-color: #FFFFFF; text-transform: inherit; padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; }
 #vkwhjjxiec .gt_first_summary_row { border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; }
 #vkwhjjxiec .gt_last_summary_row_top { border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; }
 #vkwhjjxiec .gt_grand_summary_row { color: #333333; background-color: #FFFFFF; text-transform: inherit; padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; }
 #vkwhjjxiec .gt_first_grand_summary_row_bottom { border-top-style: double; border-top-width: 6px; border-top-color: #D3D3D3; }
 #vkwhjjxiec .gt_last_grand_summary_row_top { border-bottom-style: double; border-bottom-width: 6px; border-bottom-color: #D3D3D3; }
 #vkwhjjxiec .gt_sourcenotes { color: #333333; background-color: #FFFFFF; border-bottom-style: none; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; }
 #vkwhjjxiec .gt_sourcenote { font-size: 90%; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; text-align: left; }
 #vkwhjjxiec .gt_left { text-align: left; }
 #vkwhjjxiec .gt_center { text-align: center; }
 #vkwhjjxiec .gt_right { text-align: right; font-variant-numeric: tabular-nums; }
 #vkwhjjxiec .gt_font_normal { font-weight: normal; }
 #vkwhjjxiec .gt_font_bold { font-weight: bold; }
 #vkwhjjxiec .gt_font_italic { font-style: italic; }
 #vkwhjjxiec .gt_super { font-size: 65%; }
 #vkwhjjxiec .gt_footnotes { color: font-color(#FFFFFF); background-color: #FFFFFF; border-bottom-style: none; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; }
 #vkwhjjxiec .gt_footnote { margin: 0px; font-size: 90%; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; }
 #vkwhjjxiec .gt_sourcenotes { color: #333333; background-color: #FFFFFF; border-bottom-style: none; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; }
 #vkwhjjxiec .gt_sourcenote { font-size: 90%; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; text-align: left; }
 #vkwhjjxiec .gt_footnote_marks { font-size: 75%; vertical-align: 0.4em; position: initial; }
 #vkwhjjxiec .gt_asterisk { font-size: 100%; vertical-align: 0; }
 &#10;</style>

| Fitted box-BPM coefficients (slopes per one SD of the standardized feature) |  |  |  |  |
|----|----|----|----|----|
| intercepts are team-level and absorbed by the team adjustment; \|slope\| is the BPM moved by one standard deviation of the feature |  |  |  |  |
| feature | obpm_slope | dbpm_slope | feature_mean | feature_sd |
| pts_per100 | 6.932 | −5.442 | 30.9617 | 11.4135 |
| usage | −4.567 | 2.661 | 39.0833 | 10.8115 |
| ts_pct | −0.358 | 1.818 | 0.4875 | 0.0740 |
| ast_per100 | 1.112 | −0.877 | 6.1305 | 3.3904 |
| reb_per100 | 0.025 | 1.312 | 16.3477 | 7.3573 |
| blk_pct | 0.681 | −0.639 | 0.0642 | 0.0807 |
| tov_pct | −0.183 | −0.908 | 0.2018 | 0.0675 |
| three_share | −0.482 | 0.547 | 0.3359 | 0.2353 |
| efg_pct | 0.370 | −0.520 | 0.4515 | 0.0776 |
| stl_pct | −0.244 | 0.457 | 0.1535 | 0.0890 |
| ftr | −0.275 | 0.388 | 0.2898 | 0.1551 |
| mid_share | 0.223 | −0.246 | 0.4562 | 0.2817 |
| rim_share | 0.200 | −0.234 | 0.2078 | 0.2528 |
| ast_pct | 0.035 | 0.391 | 0.2420 | 0.1730 |
| oreb_pct | 0.342 | 0.055 | 0.2815 | 0.1164 |
| dreb_pct | −0.342 | −0.055 | 0.7185 | 0.1164 |

&#10;</div>

<img src="player_value_files/figure-commonmark/cell-9-output-1.png"
width="420" height="300"
alt="Coefficient importance: BPM change per one SD of each standardized per-100 feature, offense and defense." />

Because every feature is standardized before scoring, the slopes are
directly comparable: a slope of 2 means one standard deviation of that
rate moves a player’s BPM by two points per 100 possessions. The
scoring-volume group — points per 100, usage and true shooting — carries
most of the offensive weight, and the defensive vector mirrors it with
the signs flipped, which is what the team constraint forces: the two
components must sum to one team rating, so a feature that buys offense
is charged against defense. Rebounding and steals are the distinctly
defensive contributors. The vector is republished with every run as
`wbb_player_value_coefficients.json`, alongside the artifact’s
standardization moments, so a consumer can reproduce any player’s raw
score from the published per-100 features.

## Evaluation

<div id="luzacjxjct" style="padding-left:0px;padding-right:0px;padding-top:10px;padding-bottom:10px;overflow-x:auto;overflow-y:auto;width:auto;height:auto;">
<style>
#luzacjxjct table {
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Helvetica Neue', 'Fira Sans', 'Droid Sans', Arial, sans-serif;
          -webkit-font-smoothing: antialiased;
          -moz-osx-font-smoothing: grayscale;
        }
&#10;#luzacjxjct thead, tbody, tfoot, tr, td, th { border-style: none; }
 tr { background-color: transparent; }
#luzacjxjct p { margin: 0; padding: 0; }
 #luzacjxjct .gt_table { display: table; border-collapse: collapse; line-height: normal; margin-left: auto; margin-right: auto; color: #333333; font-size: 16px; font-weight: normal; font-style: normal; background-color: #FFFFFF; width: auto; border-top-style: solid; border-top-width: 2px; border-top-color: #A8A8A8; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #A8A8A8; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; }
 #luzacjxjct .gt_caption { padding-top: 4px; padding-bottom: 4px; }
 #luzacjxjct .gt_title { color: #333333; font-size: 125%; font-weight: initial; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; border-bottom-color: #FFFFFF; border-bottom-width: 0; }
 #luzacjxjct .gt_subtitle { color: #333333; font-size: 85%; font-weight: initial; padding-top: 3px; padding-bottom: 5px; padding-left: 5px; padding-right: 5px; border-top-color: #FFFFFF; border-top-width: 0; }
 #luzacjxjct .gt_heading { background-color: #FFFFFF; text-align: center; border-bottom-color: #FFFFFF; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; }
 #luzacjxjct .gt_bottom_border { border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; }
 #luzacjxjct .gt_col_headings { border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; }
 #luzacjxjct .gt_col_heading { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: normal; text-transform: inherit; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; vertical-align: bottom; padding-top: 5px; padding-bottom: 5px; padding-left: 5px; padding-right: 5px; overflow-x: hidden; }
 #luzacjxjct .gt_column_spanner_outer { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: normal; text-transform: inherit; padding-top: 0; padding-bottom: 0; padding-left: 4px; padding-right: 4px; }
 #luzacjxjct .gt_column_spanner_outer:first-child { padding-left: 0; }
 #luzacjxjct .gt_column_spanner_outer:last-child { padding-right: 0; }
 #luzacjxjct .gt_column_spanner { border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; vertical-align: bottom; padding-top: 5px; padding-bottom: 5px; overflow-x: hidden; display: inline-block; width: 100%; }
 #luzacjxjct .gt_spanner_row { border-bottom-style: hidden; }
 #luzacjxjct .gt_group_heading { padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; text-transform: inherit; border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; vertical-align: middle; text-align: left; }
 #luzacjxjct .gt_empty_group_heading { padding: 0.5px; color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; vertical-align: middle; }
 #luzacjxjct .gt_from_md> :first-child { margin-top: 0; }
 #luzacjxjct .gt_from_md> :last-child { margin-bottom: 0; }
 #luzacjxjct .gt_row { padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; margin: 10px; border-top-style: solid; border-top-width: 1px; border-top-color: #D3D3D3; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; vertical-align: middle; overflow-x: hidden; }
 #luzacjxjct .gt_stub { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; text-transform: inherit; border-right-style: solid; border-right-width: 2px; border-right-color: #D3D3D3; padding-left: 5px; padding-right: 5px; }
 #luzacjxjct .gt_indent_1 { text-indent: 5px; }
 #luzacjxjct .gt_indent_2 { text-indent: calc(5px * 2); }
 #luzacjxjct .gt_indent_3 { text-indent: calc(5px * 3); }
 #luzacjxjct .gt_indent_4 { text-indent: calc(5px * 4); }
 #luzacjxjct .gt_indent_5 { text-indent: calc(5px * 5); }
 #luzacjxjct .gt_stub_row_group { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; text-transform: inherit; border-right-style: solid; border-right-width: 2px; border-right-color: #D3D3D3; padding-left: 5px; padding-right: 5px; vertical-align: top; }
 #luzacjxjct .gt_row_group_first td { border-top-width: 2px; }
 #luzacjxjct .gt_row_group_first th { border-top-width: 2px; }
 #luzacjxjct .gt_striped { color: #333333; background-color: #F4F4F4; }
 #luzacjxjct .gt_table_body { border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; }
 #luzacjxjct .gt_summary_row { color: #333333; background-color: #FFFFFF; text-transform: inherit; padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; }
 #luzacjxjct .gt_first_summary_row { border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; }
 #luzacjxjct .gt_last_summary_row_top { border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; }
 #luzacjxjct .gt_grand_summary_row { color: #333333; background-color: #FFFFFF; text-transform: inherit; padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; }
 #luzacjxjct .gt_first_grand_summary_row_bottom { border-top-style: double; border-top-width: 6px; border-top-color: #D3D3D3; }
 #luzacjxjct .gt_last_grand_summary_row_top { border-bottom-style: double; border-bottom-width: 6px; border-bottom-color: #D3D3D3; }
 #luzacjxjct .gt_sourcenotes { color: #333333; background-color: #FFFFFF; border-bottom-style: none; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; }
 #luzacjxjct .gt_sourcenote { font-size: 90%; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; text-align: left; }
 #luzacjxjct .gt_left { text-align: left; }
 #luzacjxjct .gt_center { text-align: center; }
 #luzacjxjct .gt_right { text-align: right; font-variant-numeric: tabular-nums; }
 #luzacjxjct .gt_font_normal { font-weight: normal; }
 #luzacjxjct .gt_font_bold { font-weight: bold; }
 #luzacjxjct .gt_font_italic { font-style: italic; }
 #luzacjxjct .gt_super { font-size: 65%; }
 #luzacjxjct .gt_footnotes { color: font-color(#FFFFFF); background-color: #FFFFFF; border-bottom-style: none; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; }
 #luzacjxjct .gt_footnote { margin: 0px; font-size: 90%; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; }
 #luzacjxjct .gt_sourcenotes { color: #333333; background-color: #FFFFFF; border-bottom-style: none; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; }
 #luzacjxjct .gt_sourcenote { font-size: 90%; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; text-align: left; }
 #luzacjxjct .gt_footnote_marks { font-size: 75%; vertical-align: 0.4em; position: initial; }
 #luzacjxjct .gt_asterisk { font-size: 100%; vertical-align: 0; }
 &#10;</style>

| Published-asset checks |  |  |
|----|----|----|
| YoY reliability is the box model's core virtue; a near-zero O/D correlation means the components carry distinct information |  |  |
| check | pairs | pearson |
| box BPM year-over-year (same player, qualified both seasons) | 15290 | <na> |
| corr(box_obpm, box_dbpm) — 2026, qualified | 3012 | −0.054 |

&#10;</div>

A box model’s justification is exactly this reliability: with
roster-level churn as violent as college basketball’s, a player metric
that persists season-over-season for returning players is measuring the
player. The engine’s own oracle gates (against the sdv-py player-value
spine’s references) run where the model is trained.

## Results

<div id="ucobidryht" style="padding-left:0px;padding-right:0px;padding-top:10px;padding-bottom:10px;overflow-x:auto;overflow-y:auto;width:auto;height:auto;">
<style>
#ucobidryht table {
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Helvetica Neue', 'Fira Sans', 'Droid Sans', Arial, sans-serif;
          -webkit-font-smoothing: antialiased;
          -moz-osx-font-smoothing: grayscale;
        }
&#10;#ucobidryht thead, tbody, tfoot, tr, td, th { border-style: none; }
 tr { background-color: transparent; }
#ucobidryht p { margin: 0; padding: 0; }
 #ucobidryht .gt_table { display: table; border-collapse: collapse; line-height: normal; margin-left: auto; margin-right: auto; color: #333333; font-size: 16px; font-weight: normal; font-style: normal; background-color: #FFFFFF; width: auto; border-top-style: solid; border-top-width: 2px; border-top-color: #A8A8A8; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #A8A8A8; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; }
 #ucobidryht .gt_caption { padding-top: 4px; padding-bottom: 4px; }
 #ucobidryht .gt_title { color: #333333; font-size: 125%; font-weight: initial; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; border-bottom-color: #FFFFFF; border-bottom-width: 0; }
 #ucobidryht .gt_subtitle { color: #333333; font-size: 85%; font-weight: initial; padding-top: 3px; padding-bottom: 5px; padding-left: 5px; padding-right: 5px; border-top-color: #FFFFFF; border-top-width: 0; }
 #ucobidryht .gt_heading { background-color: #FFFFFF; text-align: center; border-bottom-color: #FFFFFF; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; }
 #ucobidryht .gt_bottom_border { border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; }
 #ucobidryht .gt_col_headings { border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; }
 #ucobidryht .gt_col_heading { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: normal; text-transform: inherit; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; vertical-align: bottom; padding-top: 5px; padding-bottom: 5px; padding-left: 5px; padding-right: 5px; overflow-x: hidden; }
 #ucobidryht .gt_column_spanner_outer { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: normal; text-transform: inherit; padding-top: 0; padding-bottom: 0; padding-left: 4px; padding-right: 4px; }
 #ucobidryht .gt_column_spanner_outer:first-child { padding-left: 0; }
 #ucobidryht .gt_column_spanner_outer:last-child { padding-right: 0; }
 #ucobidryht .gt_column_spanner { border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; vertical-align: bottom; padding-top: 5px; padding-bottom: 5px; overflow-x: hidden; display: inline-block; width: 100%; }
 #ucobidryht .gt_spanner_row { border-bottom-style: hidden; }
 #ucobidryht .gt_group_heading { padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; text-transform: inherit; border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; vertical-align: middle; text-align: left; }
 #ucobidryht .gt_empty_group_heading { padding: 0.5px; color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; vertical-align: middle; }
 #ucobidryht .gt_from_md> :first-child { margin-top: 0; }
 #ucobidryht .gt_from_md> :last-child { margin-bottom: 0; }
 #ucobidryht .gt_row { padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; margin: 10px; border-top-style: solid; border-top-width: 1px; border-top-color: #D3D3D3; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; vertical-align: middle; overflow-x: hidden; }
 #ucobidryht .gt_stub { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; text-transform: inherit; border-right-style: solid; border-right-width: 2px; border-right-color: #D3D3D3; padding-left: 5px; padding-right: 5px; }
 #ucobidryht .gt_indent_1 { text-indent: 5px; }
 #ucobidryht .gt_indent_2 { text-indent: calc(5px * 2); }
 #ucobidryht .gt_indent_3 { text-indent: calc(5px * 3); }
 #ucobidryht .gt_indent_4 { text-indent: calc(5px * 4); }
 #ucobidryht .gt_indent_5 { text-indent: calc(5px * 5); }
 #ucobidryht .gt_stub_row_group { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; text-transform: inherit; border-right-style: solid; border-right-width: 2px; border-right-color: #D3D3D3; padding-left: 5px; padding-right: 5px; vertical-align: top; }
 #ucobidryht .gt_row_group_first td { border-top-width: 2px; }
 #ucobidryht .gt_row_group_first th { border-top-width: 2px; }
 #ucobidryht .gt_striped { color: #333333; background-color: #F4F4F4; }
 #ucobidryht .gt_table_body { border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; }
 #ucobidryht .gt_summary_row { color: #333333; background-color: #FFFFFF; text-transform: inherit; padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; }
 #ucobidryht .gt_first_summary_row { border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; }
 #ucobidryht .gt_last_summary_row_top { border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; }
 #ucobidryht .gt_grand_summary_row { color: #333333; background-color: #FFFFFF; text-transform: inherit; padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; }
 #ucobidryht .gt_first_grand_summary_row_bottom { border-top-style: double; border-top-width: 6px; border-top-color: #D3D3D3; }
 #ucobidryht .gt_last_grand_summary_row_top { border-bottom-style: double; border-bottom-width: 6px; border-bottom-color: #D3D3D3; }
 #ucobidryht .gt_sourcenotes { color: #333333; background-color: #FFFFFF; border-bottom-style: none; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; }
 #ucobidryht .gt_sourcenote { font-size: 90%; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; text-align: left; }
 #ucobidryht .gt_left { text-align: left; }
 #ucobidryht .gt_center { text-align: center; }
 #ucobidryht .gt_right { text-align: right; font-variant-numeric: tabular-nums; }
 #ucobidryht .gt_font_normal { font-weight: normal; }
 #ucobidryht .gt_font_bold { font-weight: bold; }
 #ucobidryht .gt_font_italic { font-style: italic; }
 #ucobidryht .gt_super { font-size: 65%; }
 #ucobidryht .gt_footnotes { color: font-color(#FFFFFF); background-color: #FFFFFF; border-bottom-style: none; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; }
 #ucobidryht .gt_footnote { margin: 0px; font-size: 90%; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; }
 #ucobidryht .gt_sourcenotes { color: #333333; background-color: #FFFFFF; border-bottom-style: none; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; }
 #ucobidryht .gt_sourcenote { font-size: 90%; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; text-align: left; }
 #ucobidryht .gt_footnote_marks { font-size: 75%; vertical-align: 0.4em; position: initial; }
 #ucobidryht .gt_asterisk { font-size: 100%; vertical-align: 0; }
 &#10;</style>

| Top 15 box BPM — 2026 (qualified players) |  |  |  |  |  |  |
|----|----|----|----|----|----|----|
|  | Player | Team | Min | O-BPM | D-BPM | BPM |
| <img
src="https://a.espncdn.com/i/headshots/womens-college-basketball/players/full/5125264.png"
height="40" /> | Jana El Alfy | UConn Huskies | 402 | 6.70 | 11.43 | 18.13 |
| <img
src="https://a.espncdn.com/i/headshots/womens-college-basketball/players/full/4682860.png"
height="40" /> | Kyla Oldacre | Texas Longhorns | 830 | 10.39 | 7.54 | 17.92 |
| <img
src="https://a.espncdn.com/i/headshots/womens-college-basketball/players/full/5108587.png"
height="40" /> | Madina Okot | South Carolina Gamecocks | 906 | 10.56 | 6.86 | 17.41 |
| <img
src="https://a.espncdn.com/i/headshots/womens-college-basketball/players/full/5239592.png"
height="40" /> | Sarah Strong | UConn Huskies | 1,044 | 15.80 | 1.61 | 17.41 |
| <img
src="https://a.espncdn.com/i/headshots/womens-college-basketball/players/full/5311614.png"
height="40" /> | ZaKiyah Johnson | LSU Tigers | 642 | 10.97 | 5.41 | 16.38 |
| <img
src="https://a.espncdn.com/i/headshots/womens-college-basketball/players/full/5105737.png"
height="40" /> | Lauren Betts | UCLA Bruins | 1,026 | 15.34 | 0.83 | 16.17 |
| <img
src="https://a.espncdn.com/i/headshots/womens-college-basketball/players/full/4565525.png"
height="40" /> | Amiya Joyner | LSU Tigers | 709 | 8.22 | 7.86 | 16.07 |
| <img
src="https://a.espncdn.com/i/headshots/womens-college-basketball/players/full/5174491.png"
height="40" /> | KK Arnold | UConn Huskies | 928 | 5.01 | 10.66 | 15.67 |
| <img
src="https://a.espncdn.com/i/headshots/womens-college-basketball/players/full/5238305.png"
height="40" /> | Kate Koval | LSU Tigers | 582 | 8.37 | 7.27 | 15.64 |
| <img
src="https://a.espncdn.com/i/headshots/womens-college-basketball/players/full/5238291.png"
height="40" /> | Anaya Hardy | Louisville Cardinals | 399 | 9.09 | 6.49 | 15.58 |
| <img
src="https://a.espncdn.com/i/headshots/womens-college-basketball/players/full/5311611.png"
height="40" /> | Grace Knox | LSU Tigers | 611 | 9.59 | 5.76 | 15.35 |
| <img
src="https://a.espncdn.com/i/headshots/womens-college-basketball/players/full/4433737.png"
height="40" /> | Mir McLean | Maryland Terrapins | 463 | 6.90 | 8.39 | 15.29 |
| <img
src="https://a.espncdn.com/i/headshots/womens-college-basketball/players/full/4565505.png"
height="40" /> | Kiki Rice | UCLA Bruins | 1,170 | 10.85 | 4.21 | 15.05 |
| <img
src="https://a.espncdn.com/i/headshots/womens-college-basketball/players/full/5105751.png"
height="40" /> | Teya Sidberry | Texas Longhorns | 487 | 5.33 | 9.70 | 15.03 |
| <img
src="https://a.espncdn.com/i/headshots/womens-college-basketball/players/full/5105732.png"
height="40" /> | Raegan Beers | Oklahoma Sooners | 843 | 13.33 | 1.70 | 15.02 |

&#10;</div>

## Provenance & reproducibility

- **Computed from:** this repository’s published player/team season
  stats for the seasons in the corpus table; recomputed in full on every
  run (compute-on-demand — no fitted artifact is stored here).
- **Engine:** the WBB player-value spine in sdv-py (oracle-gated where
  trained); O/D estimated separately and summed. The fitted coefficient
  vector ships with every publish as
  `wbb_player_value_coefficients.json` (features, intercept + slopes on
  standardized features, moments, λ, fit floor, train seasons,
  sportsdataverse version, artifact sha256).
- **`qualified`:** additive flag, `min >= 300`, set where sd(box_bpm)
  first sits within 2% of its 600–800-minute plateau on the published
  2014–2026 assets (derivation table above; constant
  `QUALIFIED_MIN_MINUTES` in `python/wbb_model_publish/builders.py`,
  recorded in `models/REGISTRY.md`). No row is filtered.
- **Known gap:** every 2015 row carries a NaN box BPM (974 players),
  inherited from the all-NaN `wbb_ratings_2015` asset the values are
  constrained to; the figures and tables above compute over the finite
  rows.
- **Pipeline:** `scripts/wbb_models.sh 02` → stage
  `python/wbb_model_02_player_value.py`; card sidecar
  [`wbb_models_eval_card.json`](wbb_models_eval_card.json). Single home:
  `models/manifest.yaml`.
- **Rebuild this document:** `scripts/render_model_docs.sh` (Quarto →
  GFM; `uv sync --group docs`). Requires network for the release
  download and the ESPN headshot CDN.

## Avenues for improvement & open issues

- **Blend with on/off** — box Plus/Minus and the league-wide RAPM
  measure different things; a stabilized hybrid (SPM-prior RAPM, as the
  NBA impact suite does) is the natural next step.
- **Resolved (2026-09-01, PR \#32):** the fitted coefficient vector
  ships with every publish as `wbb_player_value_coefficients.json`, and
  the coefficient-importance section above is drawn from it.
- **Resolved (2026-09-01, PR \#32):** the published frame now carries an
  additive `qualified` flag (`min >= 300`, derived from the funnel’s own
  noise curve); low-minute rows are still published, now marked.
