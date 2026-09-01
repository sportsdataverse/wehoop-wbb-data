# WBB opponent-adjusted team ratings


Per-season opponent-adjusted team ratings publish on the `wbb_ratings`
release tag: offensive and defensive efficiency (`adj_o` / `adj_d`,
points per 100 possessions) adjusted for opponent quality, plus adjusted
tempo, a net rating (`adj_em`), and its z-score. The engine is the
sdv-py WBB prediction stack’s iterative opponent adjustment — the
em-scale fixed-point solver — so a team’s number reflects who it played,
not just what it scored. Ratings are recomputed from scratch (not
incrementally updated) on every run, so late corrections to the
underlying published pbp/box data propagate automatically.

The model deliberately has no hidden machinery to explain: it is a
fixed-point solve over the season-to-date game matrix. Its “features”
are the game results themselves, its attribution is the O/D
decomposition it publishes, and its verification is external — the
engine’s oracle gates in sdv-py hold the season ordering against
KenPom/Torvik-class references where they are trained. What this
document adds is the render-time view of the published assets a consumer
actually downloads: internal-consistency checks, the structure of the
rating surface, and identified team-level results.

## Training data

<div id="mrfavumsmw" style="padding-left:0px;padding-right:0px;padding-top:10px;padding-bottom:10px;overflow-x:auto;overflow-y:auto;width:auto;height:auto;">
<style>
#mrfavumsmw table {
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Helvetica Neue', 'Fira Sans', 'Droid Sans', Arial, sans-serif;
          -webkit-font-smoothing: antialiased;
          -moz-osx-font-smoothing: grayscale;
        }
&#10;#mrfavumsmw thead, tbody, tfoot, tr, td, th { border-style: none; }
 tr { background-color: transparent; }
#mrfavumsmw p { margin: 0; padding: 0; }
 #mrfavumsmw .gt_table { display: table; border-collapse: collapse; line-height: normal; margin-left: auto; margin-right: auto; color: #333333; font-size: 16px; font-weight: normal; font-style: normal; background-color: #FFFFFF; width: auto; border-top-style: solid; border-top-width: 2px; border-top-color: #A8A8A8; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #A8A8A8; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; }
 #mrfavumsmw .gt_caption { padding-top: 4px; padding-bottom: 4px; }
 #mrfavumsmw .gt_title { color: #333333; font-size: 125%; font-weight: initial; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; border-bottom-color: #FFFFFF; border-bottom-width: 0; }
 #mrfavumsmw .gt_subtitle { color: #333333; font-size: 85%; font-weight: initial; padding-top: 3px; padding-bottom: 5px; padding-left: 5px; padding-right: 5px; border-top-color: #FFFFFF; border-top-width: 0; }
 #mrfavumsmw .gt_heading { background-color: #FFFFFF; text-align: center; border-bottom-color: #FFFFFF; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; }
 #mrfavumsmw .gt_bottom_border { border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; }
 #mrfavumsmw .gt_col_headings { border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; }
 #mrfavumsmw .gt_col_heading { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: normal; text-transform: inherit; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; vertical-align: bottom; padding-top: 5px; padding-bottom: 5px; padding-left: 5px; padding-right: 5px; overflow-x: hidden; }
 #mrfavumsmw .gt_column_spanner_outer { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: normal; text-transform: inherit; padding-top: 0; padding-bottom: 0; padding-left: 4px; padding-right: 4px; }
 #mrfavumsmw .gt_column_spanner_outer:first-child { padding-left: 0; }
 #mrfavumsmw .gt_column_spanner_outer:last-child { padding-right: 0; }
 #mrfavumsmw .gt_column_spanner { border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; vertical-align: bottom; padding-top: 5px; padding-bottom: 5px; overflow-x: hidden; display: inline-block; width: 100%; }
 #mrfavumsmw .gt_spanner_row { border-bottom-style: hidden; }
 #mrfavumsmw .gt_group_heading { padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; text-transform: inherit; border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; vertical-align: middle; text-align: left; }
 #mrfavumsmw .gt_empty_group_heading { padding: 0.5px; color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; vertical-align: middle; }
 #mrfavumsmw .gt_from_md> :first-child { margin-top: 0; }
 #mrfavumsmw .gt_from_md> :last-child { margin-bottom: 0; }
 #mrfavumsmw .gt_row { padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; margin: 10px; border-top-style: solid; border-top-width: 1px; border-top-color: #D3D3D3; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; vertical-align: middle; overflow-x: hidden; }
 #mrfavumsmw .gt_stub { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; text-transform: inherit; border-right-style: solid; border-right-width: 2px; border-right-color: #D3D3D3; padding-left: 5px; padding-right: 5px; }
 #mrfavumsmw .gt_indent_1 { text-indent: 5px; }
 #mrfavumsmw .gt_indent_2 { text-indent: calc(5px * 2); }
 #mrfavumsmw .gt_indent_3 { text-indent: calc(5px * 3); }
 #mrfavumsmw .gt_indent_4 { text-indent: calc(5px * 4); }
 #mrfavumsmw .gt_indent_5 { text-indent: calc(5px * 5); }
 #mrfavumsmw .gt_stub_row_group { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; text-transform: inherit; border-right-style: solid; border-right-width: 2px; border-right-color: #D3D3D3; padding-left: 5px; padding-right: 5px; vertical-align: top; }
 #mrfavumsmw .gt_row_group_first td { border-top-width: 2px; }
 #mrfavumsmw .gt_row_group_first th { border-top-width: 2px; }
 #mrfavumsmw .gt_striped { color: #333333; background-color: #F4F4F4; }
 #mrfavumsmw .gt_table_body { border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; }
 #mrfavumsmw .gt_summary_row { color: #333333; background-color: #FFFFFF; text-transform: inherit; padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; }
 #mrfavumsmw .gt_first_summary_row { border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; }
 #mrfavumsmw .gt_last_summary_row_top { border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; }
 #mrfavumsmw .gt_grand_summary_row { color: #333333; background-color: #FFFFFF; text-transform: inherit; padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; }
 #mrfavumsmw .gt_first_grand_summary_row_bottom { border-top-style: double; border-top-width: 6px; border-top-color: #D3D3D3; }
 #mrfavumsmw .gt_last_grand_summary_row_top { border-bottom-style: double; border-bottom-width: 6px; border-bottom-color: #D3D3D3; }
 #mrfavumsmw .gt_sourcenotes { color: #333333; background-color: #FFFFFF; border-bottom-style: none; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; }
 #mrfavumsmw .gt_sourcenote { font-size: 90%; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; text-align: left; }
 #mrfavumsmw .gt_left { text-align: left; }
 #mrfavumsmw .gt_center { text-align: center; }
 #mrfavumsmw .gt_right { text-align: right; font-variant-numeric: tabular-nums; }
 #mrfavumsmw .gt_font_normal { font-weight: normal; }
 #mrfavumsmw .gt_font_bold { font-weight: bold; }
 #mrfavumsmw .gt_font_italic { font-style: italic; }
 #mrfavumsmw .gt_super { font-size: 65%; }
 #mrfavumsmw .gt_footnotes { color: font-color(#FFFFFF); background-color: #FFFFFF; border-bottom-style: none; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; }
 #mrfavumsmw .gt_footnote { margin: 0px; font-size: 90%; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; }
 #mrfavumsmw .gt_sourcenotes { color: #333333; background-color: #FFFFFF; border-bottom-style: none; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; }
 #mrfavumsmw .gt_sourcenote { font-size: 90%; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; text-align: left; }
 #mrfavumsmw .gt_footnote_marks { font-size: 75%; vertical-align: 0.4em; position: initial; }
 #mrfavumsmw .gt_asterisk { font-size: 100%; vertical-align: 0; }
 &#10;</style>

| Published wbb_ratings assets, by season |  |  |  |
|----|----|----|----|
| computed at render time from the release; adj_em is mean-zero by construction |  |  |  |
| season | teams | team_games | mean_adj_em |
| 2020 | 546 | 10,852 | −18.157 |
| 2021 | 433 | 7,646 | −10.773 |
| 2022 | 571 | 11,024 | −21.137 |
| 2023 | 578 | 11,630 | −20.989 |
| 2024 | 621 | 11,796 | −23.757 |
| 2025 | 618 | 11,252 | −23.438 |
| 2026 | 663 | 12,058 | −27.818 |

&#10;</div>

Inputs are the published season pbp/box assets of this repository — the
ratings sit downstream of the same daily pipeline that publishes the
data they are computed from, which is what keeps them reproducible.

## Exploratory data analysis

<img src="ratings_files/figure-commonmark/cell-4-output-1.png"
width="420" height="300"
alt="The rating surface: adjusted offense vs adjusted defense (defense lower = better), latest season." />

<img src="ratings_files/figure-commonmark/cell-5-output-1.png"
width="420" height="300"
alt="Adjustment at work: adjusted net vs raw net. Off-diagonal teams are schedule effects." />

<div id="mxpopbmllm" style="padding-left:0px;padding-right:0px;padding-top:10px;padding-bottom:10px;overflow-x:auto;overflow-y:auto;width:auto;height:auto;">
<style>
#mxpopbmllm table {
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Helvetica Neue', 'Fira Sans', 'Droid Sans', Arial, sans-serif;
          -webkit-font-smoothing: antialiased;
          -moz-osx-font-smoothing: grayscale;
        }
&#10;#mxpopbmllm thead, tbody, tfoot, tr, td, th { border-style: none; }
 tr { background-color: transparent; }
#mxpopbmllm p { margin: 0; padding: 0; }
 #mxpopbmllm .gt_table { display: table; border-collapse: collapse; line-height: normal; margin-left: auto; margin-right: auto; color: #333333; font-size: 16px; font-weight: normal; font-style: normal; background-color: #FFFFFF; width: auto; border-top-style: solid; border-top-width: 2px; border-top-color: #A8A8A8; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #A8A8A8; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; }
 #mxpopbmllm .gt_caption { padding-top: 4px; padding-bottom: 4px; }
 #mxpopbmllm .gt_title { color: #333333; font-size: 125%; font-weight: initial; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; border-bottom-color: #FFFFFF; border-bottom-width: 0; }
 #mxpopbmllm .gt_subtitle { color: #333333; font-size: 85%; font-weight: initial; padding-top: 3px; padding-bottom: 5px; padding-left: 5px; padding-right: 5px; border-top-color: #FFFFFF; border-top-width: 0; }
 #mxpopbmllm .gt_heading { background-color: #FFFFFF; text-align: center; border-bottom-color: #FFFFFF; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; }
 #mxpopbmllm .gt_bottom_border { border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; }
 #mxpopbmllm .gt_col_headings { border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; }
 #mxpopbmllm .gt_col_heading { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: normal; text-transform: inherit; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; vertical-align: bottom; padding-top: 5px; padding-bottom: 5px; padding-left: 5px; padding-right: 5px; overflow-x: hidden; }
 #mxpopbmllm .gt_column_spanner_outer { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: normal; text-transform: inherit; padding-top: 0; padding-bottom: 0; padding-left: 4px; padding-right: 4px; }
 #mxpopbmllm .gt_column_spanner_outer:first-child { padding-left: 0; }
 #mxpopbmllm .gt_column_spanner_outer:last-child { padding-right: 0; }
 #mxpopbmllm .gt_column_spanner { border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; vertical-align: bottom; padding-top: 5px; padding-bottom: 5px; overflow-x: hidden; display: inline-block; width: 100%; }
 #mxpopbmllm .gt_spanner_row { border-bottom-style: hidden; }
 #mxpopbmllm .gt_group_heading { padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; text-transform: inherit; border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; vertical-align: middle; text-align: left; }
 #mxpopbmllm .gt_empty_group_heading { padding: 0.5px; color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; vertical-align: middle; }
 #mxpopbmllm .gt_from_md> :first-child { margin-top: 0; }
 #mxpopbmllm .gt_from_md> :last-child { margin-bottom: 0; }
 #mxpopbmllm .gt_row { padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; margin: 10px; border-top-style: solid; border-top-width: 1px; border-top-color: #D3D3D3; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; vertical-align: middle; overflow-x: hidden; }
 #mxpopbmllm .gt_stub { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; text-transform: inherit; border-right-style: solid; border-right-width: 2px; border-right-color: #D3D3D3; padding-left: 5px; padding-right: 5px; }
 #mxpopbmllm .gt_indent_1 { text-indent: 5px; }
 #mxpopbmllm .gt_indent_2 { text-indent: calc(5px * 2); }
 #mxpopbmllm .gt_indent_3 { text-indent: calc(5px * 3); }
 #mxpopbmllm .gt_indent_4 { text-indent: calc(5px * 4); }
 #mxpopbmllm .gt_indent_5 { text-indent: calc(5px * 5); }
 #mxpopbmllm .gt_stub_row_group { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; text-transform: inherit; border-right-style: solid; border-right-width: 2px; border-right-color: #D3D3D3; padding-left: 5px; padding-right: 5px; vertical-align: top; }
 #mxpopbmllm .gt_row_group_first td { border-top-width: 2px; }
 #mxpopbmllm .gt_row_group_first th { border-top-width: 2px; }
 #mxpopbmllm .gt_striped { color: #333333; background-color: #F4F4F4; }
 #mxpopbmllm .gt_table_body { border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; }
 #mxpopbmllm .gt_summary_row { color: #333333; background-color: #FFFFFF; text-transform: inherit; padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; }
 #mxpopbmllm .gt_first_summary_row { border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; }
 #mxpopbmllm .gt_last_summary_row_top { border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; }
 #mxpopbmllm .gt_grand_summary_row { color: #333333; background-color: #FFFFFF; text-transform: inherit; padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; }
 #mxpopbmllm .gt_first_grand_summary_row_bottom { border-top-style: double; border-top-width: 6px; border-top-color: #D3D3D3; }
 #mxpopbmllm .gt_last_grand_summary_row_top { border-bottom-style: double; border-bottom-width: 6px; border-bottom-color: #D3D3D3; }
 #mxpopbmllm .gt_sourcenotes { color: #333333; background-color: #FFFFFF; border-bottom-style: none; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; }
 #mxpopbmllm .gt_sourcenote { font-size: 90%; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; text-align: left; }
 #mxpopbmllm .gt_left { text-align: left; }
 #mxpopbmllm .gt_center { text-align: center; }
 #mxpopbmllm .gt_right { text-align: right; font-variant-numeric: tabular-nums; }
 #mxpopbmllm .gt_font_normal { font-weight: normal; }
 #mxpopbmllm .gt_font_bold { font-weight: bold; }
 #mxpopbmllm .gt_font_italic { font-style: italic; }
 #mxpopbmllm .gt_super { font-size: 65%; }
 #mxpopbmllm .gt_footnotes { color: font-color(#FFFFFF); background-color: #FFFFFF; border-bottom-style: none; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; }
 #mxpopbmllm .gt_footnote { margin: 0px; font-size: 90%; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; }
 #mxpopbmllm .gt_sourcenotes { color: #333333; background-color: #FFFFFF; border-bottom-style: none; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; }
 #mxpopbmllm .gt_sourcenote { font-size: 90%; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; text-align: left; }
 #mxpopbmllm .gt_footnote_marks { font-size: 75%; vertical-align: 0.4em; position: initial; }
 #mxpopbmllm .gt_asterisk { font-size: 100%; vertical-align: 0; }
 &#10;</style>

| Internal consistency — 2026           |          |
|---------------------------------------|----------|
| check                                 | value    |
| mean adj_em (should be ~0)            | −27.8181 |
| corr(adj_em, raw margin)              | 0.9496   |
| corr(adj_em, adj_em_z) (should be ~1) | 1.0000   |

&#10;</div>

The vertical spread between raw and adjusted margin is the point of the
model: mid-major teams with gaudy raw margins move down,
power-conference teams with brutal schedules move up, and the
correlation between the two — strong but visibly below 1 — is the honest
measure of how much schedule matters in a 360+ team league where most
games are intra-tier.

## Evaluation

The engine’s publish gates live in sdv-py where it is trained (external
ordering checks against reference systems; the NCAA RAPM repos hold the
same family of engines to Torvik at Spearman ≥ 0.93). At the asset
level, the render-time check available without an external feed is
**predictive consistency**: within a season, adj_em should order
head-to-head margins better than raw margin does, and across seasons a
program’s rating should be sticky. The cross-season stability computed
from the published assets:

<div id="zwrrsiruwv" style="padding-left:0px;padding-right:0px;padding-top:10px;padding-bottom:10px;overflow-x:auto;overflow-y:auto;width:auto;height:auto;">
<style>
#zwrrsiruwv table {
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Helvetica Neue', 'Fira Sans', 'Droid Sans', Arial, sans-serif;
          -webkit-font-smoothing: antialiased;
          -moz-osx-font-smoothing: grayscale;
        }
&#10;#zwrrsiruwv thead, tbody, tfoot, tr, td, th { border-style: none; }
 tr { background-color: transparent; }
#zwrrsiruwv p { margin: 0; padding: 0; }
 #zwrrsiruwv .gt_table { display: table; border-collapse: collapse; line-height: normal; margin-left: auto; margin-right: auto; color: #333333; font-size: 16px; font-weight: normal; font-style: normal; background-color: #FFFFFF; width: auto; border-top-style: solid; border-top-width: 2px; border-top-color: #A8A8A8; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #A8A8A8; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; }
 #zwrrsiruwv .gt_caption { padding-top: 4px; padding-bottom: 4px; }
 #zwrrsiruwv .gt_title { color: #333333; font-size: 125%; font-weight: initial; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; border-bottom-color: #FFFFFF; border-bottom-width: 0; }
 #zwrrsiruwv .gt_subtitle { color: #333333; font-size: 85%; font-weight: initial; padding-top: 3px; padding-bottom: 5px; padding-left: 5px; padding-right: 5px; border-top-color: #FFFFFF; border-top-width: 0; }
 #zwrrsiruwv .gt_heading { background-color: #FFFFFF; text-align: center; border-bottom-color: #FFFFFF; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; }
 #zwrrsiruwv .gt_bottom_border { border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; }
 #zwrrsiruwv .gt_col_headings { border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; }
 #zwrrsiruwv .gt_col_heading { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: normal; text-transform: inherit; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; vertical-align: bottom; padding-top: 5px; padding-bottom: 5px; padding-left: 5px; padding-right: 5px; overflow-x: hidden; }
 #zwrrsiruwv .gt_column_spanner_outer { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: normal; text-transform: inherit; padding-top: 0; padding-bottom: 0; padding-left: 4px; padding-right: 4px; }
 #zwrrsiruwv .gt_column_spanner_outer:first-child { padding-left: 0; }
 #zwrrsiruwv .gt_column_spanner_outer:last-child { padding-right: 0; }
 #zwrrsiruwv .gt_column_spanner { border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; vertical-align: bottom; padding-top: 5px; padding-bottom: 5px; overflow-x: hidden; display: inline-block; width: 100%; }
 #zwrrsiruwv .gt_spanner_row { border-bottom-style: hidden; }
 #zwrrsiruwv .gt_group_heading { padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; text-transform: inherit; border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; vertical-align: middle; text-align: left; }
 #zwrrsiruwv .gt_empty_group_heading { padding: 0.5px; color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; vertical-align: middle; }
 #zwrrsiruwv .gt_from_md> :first-child { margin-top: 0; }
 #zwrrsiruwv .gt_from_md> :last-child { margin-bottom: 0; }
 #zwrrsiruwv .gt_row { padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; margin: 10px; border-top-style: solid; border-top-width: 1px; border-top-color: #D3D3D3; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; vertical-align: middle; overflow-x: hidden; }
 #zwrrsiruwv .gt_stub { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; text-transform: inherit; border-right-style: solid; border-right-width: 2px; border-right-color: #D3D3D3; padding-left: 5px; padding-right: 5px; }
 #zwrrsiruwv .gt_indent_1 { text-indent: 5px; }
 #zwrrsiruwv .gt_indent_2 { text-indent: calc(5px * 2); }
 #zwrrsiruwv .gt_indent_3 { text-indent: calc(5px * 3); }
 #zwrrsiruwv .gt_indent_4 { text-indent: calc(5px * 4); }
 #zwrrsiruwv .gt_indent_5 { text-indent: calc(5px * 5); }
 #zwrrsiruwv .gt_stub_row_group { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; text-transform: inherit; border-right-style: solid; border-right-width: 2px; border-right-color: #D3D3D3; padding-left: 5px; padding-right: 5px; vertical-align: top; }
 #zwrrsiruwv .gt_row_group_first td { border-top-width: 2px; }
 #zwrrsiruwv .gt_row_group_first th { border-top-width: 2px; }
 #zwrrsiruwv .gt_striped { color: #333333; background-color: #F4F4F4; }
 #zwrrsiruwv .gt_table_body { border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; }
 #zwrrsiruwv .gt_summary_row { color: #333333; background-color: #FFFFFF; text-transform: inherit; padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; }
 #zwrrsiruwv .gt_first_summary_row { border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; }
 #zwrrsiruwv .gt_last_summary_row_top { border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; }
 #zwrrsiruwv .gt_grand_summary_row { color: #333333; background-color: #FFFFFF; text-transform: inherit; padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; }
 #zwrrsiruwv .gt_first_grand_summary_row_bottom { border-top-style: double; border-top-width: 6px; border-top-color: #D3D3D3; }
 #zwrrsiruwv .gt_last_grand_summary_row_top { border-bottom-style: double; border-bottom-width: 6px; border-bottom-color: #D3D3D3; }
 #zwrrsiruwv .gt_sourcenotes { color: #333333; background-color: #FFFFFF; border-bottom-style: none; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; }
 #zwrrsiruwv .gt_sourcenote { font-size: 90%; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; text-align: left; }
 #zwrrsiruwv .gt_left { text-align: left; }
 #zwrrsiruwv .gt_center { text-align: center; }
 #zwrrsiruwv .gt_right { text-align: right; font-variant-numeric: tabular-nums; }
 #zwrrsiruwv .gt_font_normal { font-weight: normal; }
 #zwrrsiruwv .gt_font_bold { font-weight: bold; }
 #zwrrsiruwv .gt_font_italic { font-style: italic; }
 #zwrrsiruwv .gt_super { font-size: 65%; }
 #zwrrsiruwv .gt_footnotes { color: font-color(#FFFFFF); background-color: #FFFFFF; border-bottom-style: none; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; }
 #zwrrsiruwv .gt_footnote { margin: 0px; font-size: 90%; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; }
 #zwrrsiruwv .gt_sourcenotes { color: #333333; background-color: #FFFFFF; border-bottom-style: none; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; }
 #zwrrsiruwv .gt_sourcenote { font-size: 90%; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; text-align: left; }
 #zwrrsiruwv .gt_footnote_marks { font-size: 75%; vertical-align: 0.4em; position: initial; }
 #zwrrsiruwv .gt_asterisk { font-size: 100%; vertical-align: 0; }
 &#10;</style>

| Program stickiness — adj_em season S vs S+1, same team |  |  |
|----|----|----|
| published-asset check; programs are persistent, rosters are not — the gap is roster turnover |  |  |
| season | yoy_pearson | teams |
| 2020 | 0.878 | 376 |
| 2021 | 0.887 | 390 |
| 2022 | 0.900 | 472 |
| 2023 | 0.905 | 484 |
| 2024 | 0.886 | 496 |
| 2025 | 0.892 | 519 |

&#10;</div>

## Results

<div id="kwnllukcjf" style="padding-left:0px;padding-right:0px;padding-top:10px;padding-bottom:10px;overflow-x:auto;overflow-y:auto;width:auto;height:auto;">
<style>
#kwnllukcjf table {
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Helvetica Neue', 'Fira Sans', 'Droid Sans', Arial, sans-serif;
          -webkit-font-smoothing: antialiased;
          -moz-osx-font-smoothing: grayscale;
        }
&#10;#kwnllukcjf thead, tbody, tfoot, tr, td, th { border-style: none; }
 tr { background-color: transparent; }
#kwnllukcjf p { margin: 0; padding: 0; }
 #kwnllukcjf .gt_table { display: table; border-collapse: collapse; line-height: normal; margin-left: auto; margin-right: auto; color: #333333; font-size: 16px; font-weight: normal; font-style: normal; background-color: #FFFFFF; width: auto; border-top-style: solid; border-top-width: 2px; border-top-color: #A8A8A8; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #A8A8A8; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; }
 #kwnllukcjf .gt_caption { padding-top: 4px; padding-bottom: 4px; }
 #kwnllukcjf .gt_title { color: #333333; font-size: 125%; font-weight: initial; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; border-bottom-color: #FFFFFF; border-bottom-width: 0; }
 #kwnllukcjf .gt_subtitle { color: #333333; font-size: 85%; font-weight: initial; padding-top: 3px; padding-bottom: 5px; padding-left: 5px; padding-right: 5px; border-top-color: #FFFFFF; border-top-width: 0; }
 #kwnllukcjf .gt_heading { background-color: #FFFFFF; text-align: center; border-bottom-color: #FFFFFF; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; }
 #kwnllukcjf .gt_bottom_border { border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; }
 #kwnllukcjf .gt_col_headings { border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; }
 #kwnllukcjf .gt_col_heading { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: normal; text-transform: inherit; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; vertical-align: bottom; padding-top: 5px; padding-bottom: 5px; padding-left: 5px; padding-right: 5px; overflow-x: hidden; }
 #kwnllukcjf .gt_column_spanner_outer { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: normal; text-transform: inherit; padding-top: 0; padding-bottom: 0; padding-left: 4px; padding-right: 4px; }
 #kwnllukcjf .gt_column_spanner_outer:first-child { padding-left: 0; }
 #kwnllukcjf .gt_column_spanner_outer:last-child { padding-right: 0; }
 #kwnllukcjf .gt_column_spanner { border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; vertical-align: bottom; padding-top: 5px; padding-bottom: 5px; overflow-x: hidden; display: inline-block; width: 100%; }
 #kwnllukcjf .gt_spanner_row { border-bottom-style: hidden; }
 #kwnllukcjf .gt_group_heading { padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; text-transform: inherit; border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; vertical-align: middle; text-align: left; }
 #kwnllukcjf .gt_empty_group_heading { padding: 0.5px; color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; vertical-align: middle; }
 #kwnllukcjf .gt_from_md> :first-child { margin-top: 0; }
 #kwnllukcjf .gt_from_md> :last-child { margin-bottom: 0; }
 #kwnllukcjf .gt_row { padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; margin: 10px; border-top-style: solid; border-top-width: 1px; border-top-color: #D3D3D3; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; vertical-align: middle; overflow-x: hidden; }
 #kwnllukcjf .gt_stub { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; text-transform: inherit; border-right-style: solid; border-right-width: 2px; border-right-color: #D3D3D3; padding-left: 5px; padding-right: 5px; }
 #kwnllukcjf .gt_indent_1 { text-indent: 5px; }
 #kwnllukcjf .gt_indent_2 { text-indent: calc(5px * 2); }
 #kwnllukcjf .gt_indent_3 { text-indent: calc(5px * 3); }
 #kwnllukcjf .gt_indent_4 { text-indent: calc(5px * 4); }
 #kwnllukcjf .gt_indent_5 { text-indent: calc(5px * 5); }
 #kwnllukcjf .gt_stub_row_group { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; text-transform: inherit; border-right-style: solid; border-right-width: 2px; border-right-color: #D3D3D3; padding-left: 5px; padding-right: 5px; vertical-align: top; }
 #kwnllukcjf .gt_row_group_first td { border-top-width: 2px; }
 #kwnllukcjf .gt_row_group_first th { border-top-width: 2px; }
 #kwnllukcjf .gt_striped { color: #333333; background-color: #F4F4F4; }
 #kwnllukcjf .gt_table_body { border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; }
 #kwnllukcjf .gt_summary_row { color: #333333; background-color: #FFFFFF; text-transform: inherit; padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; }
 #kwnllukcjf .gt_first_summary_row { border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; }
 #kwnllukcjf .gt_last_summary_row_top { border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; }
 #kwnllukcjf .gt_grand_summary_row { color: #333333; background-color: #FFFFFF; text-transform: inherit; padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; }
 #kwnllukcjf .gt_first_grand_summary_row_bottom { border-top-style: double; border-top-width: 6px; border-top-color: #D3D3D3; }
 #kwnllukcjf .gt_last_grand_summary_row_top { border-bottom-style: double; border-bottom-width: 6px; border-bottom-color: #D3D3D3; }
 #kwnllukcjf .gt_sourcenotes { color: #333333; background-color: #FFFFFF; border-bottom-style: none; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; }
 #kwnllukcjf .gt_sourcenote { font-size: 90%; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; text-align: left; }
 #kwnllukcjf .gt_left { text-align: left; }
 #kwnllukcjf .gt_center { text-align: center; }
 #kwnllukcjf .gt_right { text-align: right; font-variant-numeric: tabular-nums; }
 #kwnllukcjf .gt_font_normal { font-weight: normal; }
 #kwnllukcjf .gt_font_bold { font-weight: bold; }
 #kwnllukcjf .gt_font_italic { font-style: italic; }
 #kwnllukcjf .gt_super { font-size: 65%; }
 #kwnllukcjf .gt_footnotes { color: font-color(#FFFFFF); background-color: #FFFFFF; border-bottom-style: none; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; }
 #kwnllukcjf .gt_footnote { margin: 0px; font-size: 90%; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; }
 #kwnllukcjf .gt_sourcenotes { color: #333333; background-color: #FFFFFF; border-bottom-style: none; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; }
 #kwnllukcjf .gt_sourcenote { font-size: 90%; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; text-align: left; }
 #kwnllukcjf .gt_footnote_marks { font-size: 75%; vertical-align: 0.4em; position: initial; }
 #kwnllukcjf .gt_asterisk { font-size: 100%; vertical-align: 0; }
 &#10;</style>

| Top 25 — 2026 adjusted ratings |  |  |  |  |  |  |  |
|----|----|----|----|----|----|----|----|
|  | Team | Rk | AdjO | AdjD | AdjEM | AdjT | G |
| <img src="https://a.espncdn.com/i/teamlogos/ncaa/500/41.png"
height="36" /> | UConn Huskies | 1 | 129.3 | 58.1 | 71.2 | 72.9 | 39 |
| <img src="https://a.espncdn.com/i/teamlogos/ncaa/500/26.png"
height="36" /> | UCLA Bruins | 2 | 135.1 | 63.9 | 71.1 | 68.2 | 38 |
| <img src="https://a.espncdn.com/i/teamlogos/ncaa/500/2579.png"
height="36" /> | South Carolina Gamecocks | 3 | 130.5 | 63.4 | 67.1 | 71.9 | 40 |
| <img src="https://a.espncdn.com/i/teamlogos/ncaa/500/251.png"
height="36" /> | Texas Longhorns | 4 | 127.3 | 61.3 | 66.0 | 71.8 | 39 |
| <img src="https://a.espncdn.com/i/teamlogos/ncaa/500/99.png"
height="36" /> | LSU Tigers | 5 | 130.6 | 68.4 | 62.3 | 77.0 | 35 |
| <img src="https://a.espncdn.com/i/teamlogos/ncaa/500/130.png"
height="36" /> | Michigan Wolverines | 6 | 119.7 | 66.6 | 53.1 | 74.7 | 35 |
| <img src="https://a.espncdn.com/i/teamlogos/ncaa/500/150.png"
height="36" /> | Duke Blue Devils | 7 | 115.6 | 67.1 | 48.4 | 71.4 | 36 |
| <img src="https://a.espncdn.com/i/teamlogos/ncaa/500/238.png"
height="36" /> | Vanderbilt Commodores | 8 | 124.3 | 76.7 | 47.6 | 72.8 | 34 |
| <img src="https://a.espncdn.com/i/teamlogos/ncaa/500/135.png"
height="36" /> | Minnesota Golden Gophers | 9 | 117.9 | 72.1 | 45.8 | 68.0 | 33 |
| <img src="https://a.espncdn.com/i/teamlogos/ncaa/500/97.png"
height="36" /> | Louisville Cardinals | 10 | 119.7 | 74.1 | 45.5 | 71.3 | 37 |
| <img src="https://a.espncdn.com/i/teamlogos/ncaa/500/96.png"
height="36" /> | Kentucky Wildcats | 11 | 118.3 | 72.8 | 45.5 | 68.8 | 36 |
| <img src="https://a.espncdn.com/i/teamlogos/ncaa/500/120.png"
height="36" /> | Maryland Terrapins | 12 | 119.4 | 74.2 | 45.2 | 74.0 | 33 |
| <img src="https://a.espncdn.com/i/teamlogos/ncaa/500/201.png"
height="36" /> | Oklahoma Sooners | 13 | 116.3 | 71.2 | 45.1 | 79.6 | 34 |
| <img src="https://a.espncdn.com/i/teamlogos/ncaa/500/2628.png"
height="36" /> | TCU Horned Frogs | 14 | 116.3 | 71.7 | 44.6 | 69.4 | 38 |
| <img src="https://a.espncdn.com/i/teamlogos/ncaa/500/2294.png"
height="36" /> | Iowa Hawkeyes | 15 | 116.1 | 72.2 | 43.9 | 72.2 | 34 |
| <img src="https://a.espncdn.com/i/teamlogos/ncaa/500/277.png"
height="36" /> | West Virginia Mountaineers | 16 | 114.9 | 71.3 | 43.6 | 71.5 | 35 |
| <img src="https://a.espncdn.com/i/teamlogos/ncaa/500/127.png"
height="36" /> | Michigan State Spartans | 17 | 120.3 | 76.8 | 43.5 | 72.8 | 32 |
| <img src="https://a.espncdn.com/i/teamlogos/ncaa/500/194.png"
height="36" /> | Ohio State Buckeyes | 18 | 116.5 | 74.0 | 42.6 | 75.7 | 35 |
| <img src="https://a.espncdn.com/i/teamlogos/ncaa/500/153.png"
height="36" /> | North Carolina Tar Heels | 19 | 113.8 | 71.6 | 42.2 | 70.8 | 36 |
| <img src="https://a.espncdn.com/i/teamlogos/ncaa/500/145.png"
height="36" /> | Ole Miss Rebels | 20 | 116.1 | 76.2 | 39.9 | 69.8 | 36 |
| <img src="https://a.espncdn.com/i/teamlogos/ncaa/500/87.png"
height="36" /> | Notre Dame Fighting Irish | 21 | 115.0 | 75.5 | 39.5 | 72.6 | 36 |
| <img src="https://a.espncdn.com/i/teamlogos/ncaa/500/30.png"
height="36" /> | USC Trojans | 22 | 109.4 | 70.9 | 38.5 | 71.8 | 32 |
| <img src="https://a.espncdn.com/i/teamlogos/ncaa/500/2633.png"
height="36" /> | Tennessee Lady Volunteers | 23 | 114.3 | 76.0 | 38.3 | 74.9 | 30 |
| <img src="https://a.espncdn.com/i/teamlogos/ncaa/500/158.png"
height="36" /> | Nebraska Cornhuskers | 24 | 118.2 | 79.9 | 38.3 | 71.2 | 32 |
| <img src="https://a.espncdn.com/i/teamlogos/ncaa/500/264.png"
height="36" /> | Washington Huskies | 25 | 113.5 | 75.3 | 38.2 | 69.0 | 33 |

&#10;</div>

## Provenance & reproducibility

- **Computed from:** this repository’s published season pbp/box assets,
  seasons listed in the corpus table; recomputed in full on every run.
- **Engine:** the sdv-py WBB prediction stack’s iterative opponent
  adjustment (em-scale fixed point); engine training + oracle gates live
  in sdv-py.
- **Pipeline:** `scripts/wbb_models.sh 01` → stage
  `python/wbb_model_01_ratings.py` (wired via `wbb_models_cron.yml`);
  each publish writes a card sidecar
  ([`wbb_models_eval_card.json`](wbb_models_eval_card.json)). Single
  home: `models/manifest.yaml`.
- **Rebuild this document:** `scripts/render_model_docs.sh` (Quarto →
  GFM; `uv sync --group docs`). Requires network for the release
  download and the logo CDN.

## Avenues for improvement & open issues

- **Preseason priors** — blend the recruiting/returning-production prior
  into early-season ratings instead of starting from a flat matrix.
- **Home/travel modeling** — altitude and travel distance are unmodeled.
- **Known issue:** Spearman-style external checks are scale-blind; the
  level bands that catch scale bugs live in the sdv-py gates, not here.
