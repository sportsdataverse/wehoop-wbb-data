# WBB player value — box Plus/Minus


Per-player box Plus/Minus publishes on the `wbb_player_value` tag
(`box_obpm` / `box_dbpm` / `box_bpm`): a box-score value model over the
published player/team season stats, sharing the design of the WBB
player-value spine in sdv-py (oracle-gated where trained). Box-score
features are regressed onto team-level results to apportion value;
offensive and defensive components are estimated separately and summed.
It is compute-on-demand — every run recomputes from the current
published season assets, so a data correction upstream flows through on
the next publish, and each publish writes a card sidecar.

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

<div id="meklnpqzxc" style="padding-left:0px;padding-right:0px;padding-top:10px;padding-bottom:10px;overflow-x:auto;overflow-y:auto;width:auto;height:auto;">
<style>
#meklnpqzxc table {
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Helvetica Neue', 'Fira Sans', 'Droid Sans', Arial, sans-serif;
          -webkit-font-smoothing: antialiased;
          -moz-osx-font-smoothing: grayscale;
        }
&#10;#meklnpqzxc thead, tbody, tfoot, tr, td, th { border-style: none; }
 tr { background-color: transparent; }
#meklnpqzxc p { margin: 0; padding: 0; }
 #meklnpqzxc .gt_table { display: table; border-collapse: collapse; line-height: normal; margin-left: auto; margin-right: auto; color: #333333; font-size: 16px; font-weight: normal; font-style: normal; background-color: #FFFFFF; width: auto; border-top-style: solid; border-top-width: 2px; border-top-color: #A8A8A8; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #A8A8A8; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; }
 #meklnpqzxc .gt_caption { padding-top: 4px; padding-bottom: 4px; }
 #meklnpqzxc .gt_title { color: #333333; font-size: 125%; font-weight: initial; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; border-bottom-color: #FFFFFF; border-bottom-width: 0; }
 #meklnpqzxc .gt_subtitle { color: #333333; font-size: 85%; font-weight: initial; padding-top: 3px; padding-bottom: 5px; padding-left: 5px; padding-right: 5px; border-top-color: #FFFFFF; border-top-width: 0; }
 #meklnpqzxc .gt_heading { background-color: #FFFFFF; text-align: center; border-bottom-color: #FFFFFF; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; }
 #meklnpqzxc .gt_bottom_border { border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; }
 #meklnpqzxc .gt_col_headings { border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; }
 #meklnpqzxc .gt_col_heading { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: normal; text-transform: inherit; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; vertical-align: bottom; padding-top: 5px; padding-bottom: 5px; padding-left: 5px; padding-right: 5px; overflow-x: hidden; }
 #meklnpqzxc .gt_column_spanner_outer { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: normal; text-transform: inherit; padding-top: 0; padding-bottom: 0; padding-left: 4px; padding-right: 4px; }
 #meklnpqzxc .gt_column_spanner_outer:first-child { padding-left: 0; }
 #meklnpqzxc .gt_column_spanner_outer:last-child { padding-right: 0; }
 #meklnpqzxc .gt_column_spanner { border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; vertical-align: bottom; padding-top: 5px; padding-bottom: 5px; overflow-x: hidden; display: inline-block; width: 100%; }
 #meklnpqzxc .gt_spanner_row { border-bottom-style: hidden; }
 #meklnpqzxc .gt_group_heading { padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; text-transform: inherit; border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; vertical-align: middle; text-align: left; }
 #meklnpqzxc .gt_empty_group_heading { padding: 0.5px; color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; vertical-align: middle; }
 #meklnpqzxc .gt_from_md> :first-child { margin-top: 0; }
 #meklnpqzxc .gt_from_md> :last-child { margin-bottom: 0; }
 #meklnpqzxc .gt_row { padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; margin: 10px; border-top-style: solid; border-top-width: 1px; border-top-color: #D3D3D3; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; vertical-align: middle; overflow-x: hidden; }
 #meklnpqzxc .gt_stub { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; text-transform: inherit; border-right-style: solid; border-right-width: 2px; border-right-color: #D3D3D3; padding-left: 5px; padding-right: 5px; }
 #meklnpqzxc .gt_indent_1 { text-indent: 5px; }
 #meklnpqzxc .gt_indent_2 { text-indent: calc(5px * 2); }
 #meklnpqzxc .gt_indent_3 { text-indent: calc(5px * 3); }
 #meklnpqzxc .gt_indent_4 { text-indent: calc(5px * 4); }
 #meklnpqzxc .gt_indent_5 { text-indent: calc(5px * 5); }
 #meklnpqzxc .gt_stub_row_group { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; text-transform: inherit; border-right-style: solid; border-right-width: 2px; border-right-color: #D3D3D3; padding-left: 5px; padding-right: 5px; vertical-align: top; }
 #meklnpqzxc .gt_row_group_first td { border-top-width: 2px; }
 #meklnpqzxc .gt_row_group_first th { border-top-width: 2px; }
 #meklnpqzxc .gt_striped { color: #333333; background-color: #F4F4F4; }
 #meklnpqzxc .gt_table_body { border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; }
 #meklnpqzxc .gt_summary_row { color: #333333; background-color: #FFFFFF; text-transform: inherit; padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; }
 #meklnpqzxc .gt_first_summary_row { border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; }
 #meklnpqzxc .gt_last_summary_row_top { border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; }
 #meklnpqzxc .gt_grand_summary_row { color: #333333; background-color: #FFFFFF; text-transform: inherit; padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; }
 #meklnpqzxc .gt_first_grand_summary_row_bottom { border-top-style: double; border-top-width: 6px; border-top-color: #D3D3D3; }
 #meklnpqzxc .gt_last_grand_summary_row_top { border-bottom-style: double; border-bottom-width: 6px; border-bottom-color: #D3D3D3; }
 #meklnpqzxc .gt_sourcenotes { color: #333333; background-color: #FFFFFF; border-bottom-style: none; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; }
 #meklnpqzxc .gt_sourcenote { font-size: 90%; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; text-align: left; }
 #meklnpqzxc .gt_left { text-align: left; }
 #meklnpqzxc .gt_center { text-align: center; }
 #meklnpqzxc .gt_right { text-align: right; font-variant-numeric: tabular-nums; }
 #meklnpqzxc .gt_font_normal { font-weight: normal; }
 #meklnpqzxc .gt_font_bold { font-weight: bold; }
 #meklnpqzxc .gt_font_italic { font-style: italic; }
 #meklnpqzxc .gt_super { font-size: 65%; }
 #meklnpqzxc .gt_footnotes { color: font-color(#FFFFFF); background-color: #FFFFFF; border-bottom-style: none; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; }
 #meklnpqzxc .gt_footnote { margin: 0px; font-size: 90%; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; }
 #meklnpqzxc .gt_sourcenotes { color: #333333; background-color: #FFFFFF; border-bottom-style: none; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; }
 #meklnpqzxc .gt_sourcenote { font-size: 90%; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; text-align: left; }
 #meklnpqzxc .gt_footnote_marks { font-size: 75%; vertical-align: 0.4em; position: initial; }
 #meklnpqzxc .gt_asterisk { font-size: 100%; vertical-align: 0; }
 &#10;</style>

| Published wbb_player_value assets, by season |  |  |  |
|----|----|----|----|
| computed at render time from the release |  |  |  |
| season | players | total_minutes | players_300min |
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
alt="Box BPM distribution, latest season — the full player pool vs the ≥300-minute pool. The unfiltered frame carries heavy low-minute noise by design." />

<img src="player_value_files/figure-commonmark/cell-5-output-1.png"
width="420" height="300"
alt="Minutes vs |BPM|: with no shrinkage prior, extreme values concentrate at LOW minutes — the reason consumers must filter." />

<img src="player_value_files/figure-commonmark/cell-6-output-1.png"
width="420" height="300"
alt="Offense vs defense components, ≥300 minutes, latest season." />

The minutes-vs-\|BPM\| funnel is this model’s most important
consumer-facing fact, shown rather than footnoted: the published frame
enforces **no minutes floor**, so the most extreme values in the file
belong to 20-minute seasons. Every table below applies a floor;
consumers must too.

## Attribution

The model is a linear apportionment of team results onto box-score
features, so the published O/D columns are its native attribution — the
scatter above is the decomposition. The fitted coefficient vector lives
with the engine in sdv-py (oracle-gated where trained) rather than in
the published asset; surfacing it alongside the release is listed in the
avenues below.

## Evaluation

<div id="gtrzewyoxc" style="padding-left:0px;padding-right:0px;padding-top:10px;padding-bottom:10px;overflow-x:auto;overflow-y:auto;width:auto;height:auto;">
<style>
#gtrzewyoxc table {
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Helvetica Neue', 'Fira Sans', 'Droid Sans', Arial, sans-serif;
          -webkit-font-smoothing: antialiased;
          -moz-osx-font-smoothing: grayscale;
        }
&#10;#gtrzewyoxc thead, tbody, tfoot, tr, td, th { border-style: none; }
 tr { background-color: transparent; }
#gtrzewyoxc p { margin: 0; padding: 0; }
 #gtrzewyoxc .gt_table { display: table; border-collapse: collapse; line-height: normal; margin-left: auto; margin-right: auto; color: #333333; font-size: 16px; font-weight: normal; font-style: normal; background-color: #FFFFFF; width: auto; border-top-style: solid; border-top-width: 2px; border-top-color: #A8A8A8; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #A8A8A8; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; }
 #gtrzewyoxc .gt_caption { padding-top: 4px; padding-bottom: 4px; }
 #gtrzewyoxc .gt_title { color: #333333; font-size: 125%; font-weight: initial; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; border-bottom-color: #FFFFFF; border-bottom-width: 0; }
 #gtrzewyoxc .gt_subtitle { color: #333333; font-size: 85%; font-weight: initial; padding-top: 3px; padding-bottom: 5px; padding-left: 5px; padding-right: 5px; border-top-color: #FFFFFF; border-top-width: 0; }
 #gtrzewyoxc .gt_heading { background-color: #FFFFFF; text-align: center; border-bottom-color: #FFFFFF; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; }
 #gtrzewyoxc .gt_bottom_border { border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; }
 #gtrzewyoxc .gt_col_headings { border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; }
 #gtrzewyoxc .gt_col_heading { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: normal; text-transform: inherit; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; vertical-align: bottom; padding-top: 5px; padding-bottom: 5px; padding-left: 5px; padding-right: 5px; overflow-x: hidden; }
 #gtrzewyoxc .gt_column_spanner_outer { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: normal; text-transform: inherit; padding-top: 0; padding-bottom: 0; padding-left: 4px; padding-right: 4px; }
 #gtrzewyoxc .gt_column_spanner_outer:first-child { padding-left: 0; }
 #gtrzewyoxc .gt_column_spanner_outer:last-child { padding-right: 0; }
 #gtrzewyoxc .gt_column_spanner { border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; vertical-align: bottom; padding-top: 5px; padding-bottom: 5px; overflow-x: hidden; display: inline-block; width: 100%; }
 #gtrzewyoxc .gt_spanner_row { border-bottom-style: hidden; }
 #gtrzewyoxc .gt_group_heading { padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; text-transform: inherit; border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; vertical-align: middle; text-align: left; }
 #gtrzewyoxc .gt_empty_group_heading { padding: 0.5px; color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; vertical-align: middle; }
 #gtrzewyoxc .gt_from_md> :first-child { margin-top: 0; }
 #gtrzewyoxc .gt_from_md> :last-child { margin-bottom: 0; }
 #gtrzewyoxc .gt_row { padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; margin: 10px; border-top-style: solid; border-top-width: 1px; border-top-color: #D3D3D3; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; vertical-align: middle; overflow-x: hidden; }
 #gtrzewyoxc .gt_stub { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; text-transform: inherit; border-right-style: solid; border-right-width: 2px; border-right-color: #D3D3D3; padding-left: 5px; padding-right: 5px; }
 #gtrzewyoxc .gt_indent_1 { text-indent: 5px; }
 #gtrzewyoxc .gt_indent_2 { text-indent: calc(5px * 2); }
 #gtrzewyoxc .gt_indent_3 { text-indent: calc(5px * 3); }
 #gtrzewyoxc .gt_indent_4 { text-indent: calc(5px * 4); }
 #gtrzewyoxc .gt_indent_5 { text-indent: calc(5px * 5); }
 #gtrzewyoxc .gt_stub_row_group { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; text-transform: inherit; border-right-style: solid; border-right-width: 2px; border-right-color: #D3D3D3; padding-left: 5px; padding-right: 5px; vertical-align: top; }
 #gtrzewyoxc .gt_row_group_first td { border-top-width: 2px; }
 #gtrzewyoxc .gt_row_group_first th { border-top-width: 2px; }
 #gtrzewyoxc .gt_striped { color: #333333; background-color: #F4F4F4; }
 #gtrzewyoxc .gt_table_body { border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; }
 #gtrzewyoxc .gt_summary_row { color: #333333; background-color: #FFFFFF; text-transform: inherit; padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; }
 #gtrzewyoxc .gt_first_summary_row { border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; }
 #gtrzewyoxc .gt_last_summary_row_top { border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; }
 #gtrzewyoxc .gt_grand_summary_row { color: #333333; background-color: #FFFFFF; text-transform: inherit; padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; }
 #gtrzewyoxc .gt_first_grand_summary_row_bottom { border-top-style: double; border-top-width: 6px; border-top-color: #D3D3D3; }
 #gtrzewyoxc .gt_last_grand_summary_row_top { border-bottom-style: double; border-bottom-width: 6px; border-bottom-color: #D3D3D3; }
 #gtrzewyoxc .gt_sourcenotes { color: #333333; background-color: #FFFFFF; border-bottom-style: none; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; }
 #gtrzewyoxc .gt_sourcenote { font-size: 90%; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; text-align: left; }
 #gtrzewyoxc .gt_left { text-align: left; }
 #gtrzewyoxc .gt_center { text-align: center; }
 #gtrzewyoxc .gt_right { text-align: right; font-variant-numeric: tabular-nums; }
 #gtrzewyoxc .gt_font_normal { font-weight: normal; }
 #gtrzewyoxc .gt_font_bold { font-weight: bold; }
 #gtrzewyoxc .gt_font_italic { font-style: italic; }
 #gtrzewyoxc .gt_super { font-size: 65%; }
 #gtrzewyoxc .gt_footnotes { color: font-color(#FFFFFF); background-color: #FFFFFF; border-bottom-style: none; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; }
 #gtrzewyoxc .gt_footnote { margin: 0px; font-size: 90%; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; }
 #gtrzewyoxc .gt_sourcenotes { color: #333333; background-color: #FFFFFF; border-bottom-style: none; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; }
 #gtrzewyoxc .gt_sourcenote { font-size: 90%; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; text-align: left; }
 #gtrzewyoxc .gt_footnote_marks { font-size: 75%; vertical-align: 0.4em; position: initial; }
 #gtrzewyoxc .gt_asterisk { font-size: 100%; vertical-align: 0; }
 &#10;</style>

| Published-asset checks |  |  |
|----|----|----|
| YoY reliability is the box model's core virtue; a near-zero O/D correlation means the components carry distinct information |  |  |
| check | pairs | pearson |
| box BPM year-over-year (same player, ≥300 min both seasons) | 9651 | 0.822 |
| corr(box_obpm, box_dbpm) — 2026, ≥300 min | 3012 | −0.054 |

&#10;</div>

A box model’s justification is exactly this reliability: with
roster-level churn as violent as college basketball’s, a player metric
that persists season-over-season for returning players is measuring the
player. The engine’s own oracle gates (against the sdv-py player-value
spine’s references) run where the model is trained.

## Results

<div id="xdyesegwye" style="padding-left:0px;padding-right:0px;padding-top:10px;padding-bottom:10px;overflow-x:auto;overflow-y:auto;width:auto;height:auto;">
<style>
#xdyesegwye table {
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Helvetica Neue', 'Fira Sans', 'Droid Sans', Arial, sans-serif;
          -webkit-font-smoothing: antialiased;
          -moz-osx-font-smoothing: grayscale;
        }
&#10;#xdyesegwye thead, tbody, tfoot, tr, td, th { border-style: none; }
 tr { background-color: transparent; }
#xdyesegwye p { margin: 0; padding: 0; }
 #xdyesegwye .gt_table { display: table; border-collapse: collapse; line-height: normal; margin-left: auto; margin-right: auto; color: #333333; font-size: 16px; font-weight: normal; font-style: normal; background-color: #FFFFFF; width: auto; border-top-style: solid; border-top-width: 2px; border-top-color: #A8A8A8; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #A8A8A8; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; }
 #xdyesegwye .gt_caption { padding-top: 4px; padding-bottom: 4px; }
 #xdyesegwye .gt_title { color: #333333; font-size: 125%; font-weight: initial; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; border-bottom-color: #FFFFFF; border-bottom-width: 0; }
 #xdyesegwye .gt_subtitle { color: #333333; font-size: 85%; font-weight: initial; padding-top: 3px; padding-bottom: 5px; padding-left: 5px; padding-right: 5px; border-top-color: #FFFFFF; border-top-width: 0; }
 #xdyesegwye .gt_heading { background-color: #FFFFFF; text-align: center; border-bottom-color: #FFFFFF; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; }
 #xdyesegwye .gt_bottom_border { border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; }
 #xdyesegwye .gt_col_headings { border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; }
 #xdyesegwye .gt_col_heading { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: normal; text-transform: inherit; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; vertical-align: bottom; padding-top: 5px; padding-bottom: 5px; padding-left: 5px; padding-right: 5px; overflow-x: hidden; }
 #xdyesegwye .gt_column_spanner_outer { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: normal; text-transform: inherit; padding-top: 0; padding-bottom: 0; padding-left: 4px; padding-right: 4px; }
 #xdyesegwye .gt_column_spanner_outer:first-child { padding-left: 0; }
 #xdyesegwye .gt_column_spanner_outer:last-child { padding-right: 0; }
 #xdyesegwye .gt_column_spanner { border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; vertical-align: bottom; padding-top: 5px; padding-bottom: 5px; overflow-x: hidden; display: inline-block; width: 100%; }
 #xdyesegwye .gt_spanner_row { border-bottom-style: hidden; }
 #xdyesegwye .gt_group_heading { padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; text-transform: inherit; border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; vertical-align: middle; text-align: left; }
 #xdyesegwye .gt_empty_group_heading { padding: 0.5px; color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; vertical-align: middle; }
 #xdyesegwye .gt_from_md> :first-child { margin-top: 0; }
 #xdyesegwye .gt_from_md> :last-child { margin-bottom: 0; }
 #xdyesegwye .gt_row { padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; margin: 10px; border-top-style: solid; border-top-width: 1px; border-top-color: #D3D3D3; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; vertical-align: middle; overflow-x: hidden; }
 #xdyesegwye .gt_stub { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; text-transform: inherit; border-right-style: solid; border-right-width: 2px; border-right-color: #D3D3D3; padding-left: 5px; padding-right: 5px; }
 #xdyesegwye .gt_indent_1 { text-indent: 5px; }
 #xdyesegwye .gt_indent_2 { text-indent: calc(5px * 2); }
 #xdyesegwye .gt_indent_3 { text-indent: calc(5px * 3); }
 #xdyesegwye .gt_indent_4 { text-indent: calc(5px * 4); }
 #xdyesegwye .gt_indent_5 { text-indent: calc(5px * 5); }
 #xdyesegwye .gt_stub_row_group { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; text-transform: inherit; border-right-style: solid; border-right-width: 2px; border-right-color: #D3D3D3; padding-left: 5px; padding-right: 5px; vertical-align: top; }
 #xdyesegwye .gt_row_group_first td { border-top-width: 2px; }
 #xdyesegwye .gt_row_group_first th { border-top-width: 2px; }
 #xdyesegwye .gt_striped { color: #333333; background-color: #F4F4F4; }
 #xdyesegwye .gt_table_body { border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; }
 #xdyesegwye .gt_summary_row { color: #333333; background-color: #FFFFFF; text-transform: inherit; padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; }
 #xdyesegwye .gt_first_summary_row { border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; }
 #xdyesegwye .gt_last_summary_row_top { border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; }
 #xdyesegwye .gt_grand_summary_row { color: #333333; background-color: #FFFFFF; text-transform: inherit; padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; }
 #xdyesegwye .gt_first_grand_summary_row_bottom { border-top-style: double; border-top-width: 6px; border-top-color: #D3D3D3; }
 #xdyesegwye .gt_last_grand_summary_row_top { border-bottom-style: double; border-bottom-width: 6px; border-bottom-color: #D3D3D3; }
 #xdyesegwye .gt_sourcenotes { color: #333333; background-color: #FFFFFF; border-bottom-style: none; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; }
 #xdyesegwye .gt_sourcenote { font-size: 90%; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; text-align: left; }
 #xdyesegwye .gt_left { text-align: left; }
 #xdyesegwye .gt_center { text-align: center; }
 #xdyesegwye .gt_right { text-align: right; font-variant-numeric: tabular-nums; }
 #xdyesegwye .gt_font_normal { font-weight: normal; }
 #xdyesegwye .gt_font_bold { font-weight: bold; }
 #xdyesegwye .gt_font_italic { font-style: italic; }
 #xdyesegwye .gt_super { font-size: 65%; }
 #xdyesegwye .gt_footnotes { color: font-color(#FFFFFF); background-color: #FFFFFF; border-bottom-style: none; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; }
 #xdyesegwye .gt_footnote { margin: 0px; font-size: 90%; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; }
 #xdyesegwye .gt_sourcenotes { color: #333333; background-color: #FFFFFF; border-bottom-style: none; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; }
 #xdyesegwye .gt_sourcenote { font-size: 90%; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; text-align: left; }
 #xdyesegwye .gt_footnote_marks { font-size: 75%; vertical-align: 0.4em; position: initial; }
 #xdyesegwye .gt_asterisk { font-size: 100%; vertical-align: 0; }
 &#10;</style>

| Top 15 box BPM — 2026 (min 300 minutes) |  |  |  |  |  |  |
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
  run (compute-on-demand — no fitted artifact is stored).
- **Engine:** the WBB player-value spine in sdv-py (oracle-gated where
  trained); O/D estimated separately and summed.
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
- **Ship the coefficient vector** — publishing the fitted coefficients
  (or a per-retrain meta sidecar) would let this document show real
  coefficient importance instead of pointing at the engine.
- **Known issue:** no minutes floor is enforced in the published frame —
  consumers must filter low-minute noise themselves (the funnel figure
  above is the demonstration).
