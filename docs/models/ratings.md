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
rating surface, identified team-level results, and the absolute level
gate that guards the scale a rank check cannot see.

## Training data

<div id="hjqdgjthyg" style="padding-left:0px;padding-right:0px;padding-top:10px;padding-bottom:10px;overflow-x:auto;overflow-y:auto;width:auto;height:auto;">
<style>
#hjqdgjthyg table {
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Helvetica Neue', 'Fira Sans', 'Droid Sans', Arial, sans-serif;
          -webkit-font-smoothing: antialiased;
          -moz-osx-font-smoothing: grayscale;
        }
&#10;#hjqdgjthyg thead, tbody, tfoot, tr, td, th { border-style: none; }
 tr { background-color: transparent; }
#hjqdgjthyg p { margin: 0; padding: 0; }
 #hjqdgjthyg .gt_table { display: table; border-collapse: collapse; line-height: normal; margin-left: auto; margin-right: auto; color: #333333; font-size: 16px; font-weight: normal; font-style: normal; background-color: #FFFFFF; width: auto; border-top-style: solid; border-top-width: 2px; border-top-color: #A8A8A8; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #A8A8A8; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; }
 #hjqdgjthyg .gt_caption { padding-top: 4px; padding-bottom: 4px; }
 #hjqdgjthyg .gt_title { color: #333333; font-size: 125%; font-weight: initial; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; border-bottom-color: #FFFFFF; border-bottom-width: 0; }
 #hjqdgjthyg .gt_subtitle { color: #333333; font-size: 85%; font-weight: initial; padding-top: 3px; padding-bottom: 5px; padding-left: 5px; padding-right: 5px; border-top-color: #FFFFFF; border-top-width: 0; }
 #hjqdgjthyg .gt_heading { background-color: #FFFFFF; text-align: center; border-bottom-color: #FFFFFF; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; }
 #hjqdgjthyg .gt_bottom_border { border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; }
 #hjqdgjthyg .gt_col_headings { border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; }
 #hjqdgjthyg .gt_col_heading { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: normal; text-transform: inherit; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; vertical-align: bottom; padding-top: 5px; padding-bottom: 5px; padding-left: 5px; padding-right: 5px; overflow-x: hidden; }
 #hjqdgjthyg .gt_column_spanner_outer { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: normal; text-transform: inherit; padding-top: 0; padding-bottom: 0; padding-left: 4px; padding-right: 4px; }
 #hjqdgjthyg .gt_column_spanner_outer:first-child { padding-left: 0; }
 #hjqdgjthyg .gt_column_spanner_outer:last-child { padding-right: 0; }
 #hjqdgjthyg .gt_column_spanner { border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; vertical-align: bottom; padding-top: 5px; padding-bottom: 5px; overflow-x: hidden; display: inline-block; width: 100%; }
 #hjqdgjthyg .gt_spanner_row { border-bottom-style: hidden; }
 #hjqdgjthyg .gt_group_heading { padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; text-transform: inherit; border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; vertical-align: middle; text-align: left; }
 #hjqdgjthyg .gt_empty_group_heading { padding: 0.5px; color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; vertical-align: middle; }
 #hjqdgjthyg .gt_from_md> :first-child { margin-top: 0; }
 #hjqdgjthyg .gt_from_md> :last-child { margin-bottom: 0; }
 #hjqdgjthyg .gt_row { padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; margin: 10px; border-top-style: solid; border-top-width: 1px; border-top-color: #D3D3D3; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; vertical-align: middle; overflow-x: hidden; }
 #hjqdgjthyg .gt_stub { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; text-transform: inherit; border-right-style: solid; border-right-width: 2px; border-right-color: #D3D3D3; padding-left: 5px; padding-right: 5px; }
 #hjqdgjthyg .gt_indent_1 { text-indent: 5px; }
 #hjqdgjthyg .gt_indent_2 { text-indent: calc(5px * 2); }
 #hjqdgjthyg .gt_indent_3 { text-indent: calc(5px * 3); }
 #hjqdgjthyg .gt_indent_4 { text-indent: calc(5px * 4); }
 #hjqdgjthyg .gt_indent_5 { text-indent: calc(5px * 5); }
 #hjqdgjthyg .gt_stub_row_group { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; text-transform: inherit; border-right-style: solid; border-right-width: 2px; border-right-color: #D3D3D3; padding-left: 5px; padding-right: 5px; vertical-align: top; }
 #hjqdgjthyg .gt_row_group_first td { border-top-width: 2px; }
 #hjqdgjthyg .gt_row_group_first th { border-top-width: 2px; }
 #hjqdgjthyg .gt_striped { color: #333333; background-color: #F4F4F4; }
 #hjqdgjthyg .gt_table_body { border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; }
 #hjqdgjthyg .gt_summary_row { color: #333333; background-color: #FFFFFF; text-transform: inherit; padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; }
 #hjqdgjthyg .gt_first_summary_row { border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; }
 #hjqdgjthyg .gt_last_summary_row_top { border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; }
 #hjqdgjthyg .gt_grand_summary_row { color: #333333; background-color: #FFFFFF; text-transform: inherit; padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; }
 #hjqdgjthyg .gt_first_grand_summary_row_bottom { border-top-style: double; border-top-width: 6px; border-top-color: #D3D3D3; }
 #hjqdgjthyg .gt_last_grand_summary_row_top { border-bottom-style: double; border-bottom-width: 6px; border-bottom-color: #D3D3D3; }
 #hjqdgjthyg .gt_sourcenotes { color: #333333; background-color: #FFFFFF; border-bottom-style: none; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; }
 #hjqdgjthyg .gt_sourcenote { font-size: 90%; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; text-align: left; }
 #hjqdgjthyg .gt_left { text-align: left; }
 #hjqdgjthyg .gt_center { text-align: center; }
 #hjqdgjthyg .gt_right { text-align: right; font-variant-numeric: tabular-nums; }
 #hjqdgjthyg .gt_font_normal { font-weight: normal; }
 #hjqdgjthyg .gt_font_bold { font-weight: bold; }
 #hjqdgjthyg .gt_font_italic { font-style: italic; }
 #hjqdgjthyg .gt_super { font-size: 65%; }
 #hjqdgjthyg .gt_footnotes { color: font-color(#FFFFFF); background-color: #FFFFFF; border-bottom-style: none; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; }
 #hjqdgjthyg .gt_footnote { margin: 0px; font-size: 90%; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; }
 #hjqdgjthyg .gt_sourcenotes { color: #333333; background-color: #FFFFFF; border-bottom-style: none; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; }
 #hjqdgjthyg .gt_sourcenote { font-size: 90%; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; text-align: left; }
 #hjqdgjthyg .gt_footnote_marks { font-size: 75%; vertical-align: 0.4em; position: initial; }
 #hjqdgjthyg .gt_asterisk { font-size: 100%; vertical-align: 0; }
 &#10;</style>

| Published wbb_ratings assets, by season |  |  |  |  |  |
|----|----|----|----|----|----|
| the full frame carries every opponent ever seen (few-game non-D1 teams pull its mean far negative); the core -- teams with 10+ games -- sits near zero |  |  |  |  |  |
| season | teams | teams_10plus_games | team_games | mean_adj_em_all | mean_adj_em_core |
| 2008 | 354 | 158 | 3,522 | −11.87 | 3.12 |
| 2009 | 343 | 71 | 2,590 | −21.19 | 11.51 |
| 2010 | 301 | 66 | 1,850 | −23.98 | 7.50 |
| 2011 | 240 | 45 | 1,462 | −24.82 | 9.41 |
| 2012 | 336 | 78 | 2,884 | −20.75 | 9.33 |
| 2013 | 348 | 101 | 3,662 | −13.05 | 6.97 |
| 2014 | 340 | 83 | 3,444 | −16.42 | 7.26 |
| 2015 | 335 | 78 | 3,186 | <na> | <na> |
| 2016 | 345 | 84 | 3,584 | −15.54 | 7.70 |
| 2017 | 365 | 349 | 10,484 | −3.49 | −1.23 |
| 2018 | 356 | 349 | 10,566 | −2.65 | −1.19 |
| 2019 | 360 | 351 | 10,732 | −2.35 | −1.17 |
| 2020 | 546 | 351 | 10,852 | −18.16 | 1.00 |
| 2021 | 433 | 333 | 7,646 | −10.77 | −0.83 |
| 2022 | 571 | 356 | 11,024 | −21.14 | 0.70 |
| 2023 | 578 | 361 | 11,630 | −20.99 | 0.59 |
| 2024 | 621 | 360 | 11,796 | −23.76 | 0.84 |
| 2025 | 618 | 362 | 11,252 | −23.44 | 0.78 |
| 2026 | 663 | 363 | 12,058 | −27.82 | 1.35 |

&#10;</div>

Inputs are the published season pbp/box assets of this repository — the
ratings sit downstream of the same daily pipeline that publishes the
data they are computed from, which is what keeps them reproducible. A
season row whose means are blank is a published asset the fixed point
never converged on (every rating NaN); the level gate below now refuses
such a season at publish time.

## Exploratory data analysis

<img src="ratings_files/figure-commonmark/cell-4-output-1.png"
width="420" height="300"
alt="The rating surface: adjusted offense vs adjusted defense (defense lower = better), latest season." />

<img src="ratings_files/figure-commonmark/cell-5-output-1.png"
width="420" height="300"
alt="Adjustment at work: adjusted net vs raw net. Off-diagonal teams are schedule effects." />

<div id="ckabseemut" style="padding-left:0px;padding-right:0px;padding-top:10px;padding-bottom:10px;overflow-x:auto;overflow-y:auto;width:auto;height:auto;">
<style>
#ckabseemut table {
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Helvetica Neue', 'Fira Sans', 'Droid Sans', Arial, sans-serif;
          -webkit-font-smoothing: antialiased;
          -moz-osx-font-smoothing: grayscale;
        }
&#10;#ckabseemut thead, tbody, tfoot, tr, td, th { border-style: none; }
 tr { background-color: transparent; }
#ckabseemut p { margin: 0; padding: 0; }
 #ckabseemut .gt_table { display: table; border-collapse: collapse; line-height: normal; margin-left: auto; margin-right: auto; color: #333333; font-size: 16px; font-weight: normal; font-style: normal; background-color: #FFFFFF; width: auto; border-top-style: solid; border-top-width: 2px; border-top-color: #A8A8A8; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #A8A8A8; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; }
 #ckabseemut .gt_caption { padding-top: 4px; padding-bottom: 4px; }
 #ckabseemut .gt_title { color: #333333; font-size: 125%; font-weight: initial; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; border-bottom-color: #FFFFFF; border-bottom-width: 0; }
 #ckabseemut .gt_subtitle { color: #333333; font-size: 85%; font-weight: initial; padding-top: 3px; padding-bottom: 5px; padding-left: 5px; padding-right: 5px; border-top-color: #FFFFFF; border-top-width: 0; }
 #ckabseemut .gt_heading { background-color: #FFFFFF; text-align: center; border-bottom-color: #FFFFFF; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; }
 #ckabseemut .gt_bottom_border { border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; }
 #ckabseemut .gt_col_headings { border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; }
 #ckabseemut .gt_col_heading { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: normal; text-transform: inherit; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; vertical-align: bottom; padding-top: 5px; padding-bottom: 5px; padding-left: 5px; padding-right: 5px; overflow-x: hidden; }
 #ckabseemut .gt_column_spanner_outer { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: normal; text-transform: inherit; padding-top: 0; padding-bottom: 0; padding-left: 4px; padding-right: 4px; }
 #ckabseemut .gt_column_spanner_outer:first-child { padding-left: 0; }
 #ckabseemut .gt_column_spanner_outer:last-child { padding-right: 0; }
 #ckabseemut .gt_column_spanner { border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; vertical-align: bottom; padding-top: 5px; padding-bottom: 5px; overflow-x: hidden; display: inline-block; width: 100%; }
 #ckabseemut .gt_spanner_row { border-bottom-style: hidden; }
 #ckabseemut .gt_group_heading { padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; text-transform: inherit; border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; vertical-align: middle; text-align: left; }
 #ckabseemut .gt_empty_group_heading { padding: 0.5px; color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; vertical-align: middle; }
 #ckabseemut .gt_from_md> :first-child { margin-top: 0; }
 #ckabseemut .gt_from_md> :last-child { margin-bottom: 0; }
 #ckabseemut .gt_row { padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; margin: 10px; border-top-style: solid; border-top-width: 1px; border-top-color: #D3D3D3; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; vertical-align: middle; overflow-x: hidden; }
 #ckabseemut .gt_stub { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; text-transform: inherit; border-right-style: solid; border-right-width: 2px; border-right-color: #D3D3D3; padding-left: 5px; padding-right: 5px; }
 #ckabseemut .gt_indent_1 { text-indent: 5px; }
 #ckabseemut .gt_indent_2 { text-indent: calc(5px * 2); }
 #ckabseemut .gt_indent_3 { text-indent: calc(5px * 3); }
 #ckabseemut .gt_indent_4 { text-indent: calc(5px * 4); }
 #ckabseemut .gt_indent_5 { text-indent: calc(5px * 5); }
 #ckabseemut .gt_stub_row_group { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; text-transform: inherit; border-right-style: solid; border-right-width: 2px; border-right-color: #D3D3D3; padding-left: 5px; padding-right: 5px; vertical-align: top; }
 #ckabseemut .gt_row_group_first td { border-top-width: 2px; }
 #ckabseemut .gt_row_group_first th { border-top-width: 2px; }
 #ckabseemut .gt_striped { color: #333333; background-color: #F4F4F4; }
 #ckabseemut .gt_table_body { border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; }
 #ckabseemut .gt_summary_row { color: #333333; background-color: #FFFFFF; text-transform: inherit; padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; }
 #ckabseemut .gt_first_summary_row { border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; }
 #ckabseemut .gt_last_summary_row_top { border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; }
 #ckabseemut .gt_grand_summary_row { color: #333333; background-color: #FFFFFF; text-transform: inherit; padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; }
 #ckabseemut .gt_first_grand_summary_row_bottom { border-top-style: double; border-top-width: 6px; border-top-color: #D3D3D3; }
 #ckabseemut .gt_last_grand_summary_row_top { border-bottom-style: double; border-bottom-width: 6px; border-bottom-color: #D3D3D3; }
 #ckabseemut .gt_sourcenotes { color: #333333; background-color: #FFFFFF; border-bottom-style: none; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; }
 #ckabseemut .gt_sourcenote { font-size: 90%; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; text-align: left; }
 #ckabseemut .gt_left { text-align: left; }
 #ckabseemut .gt_center { text-align: center; }
 #ckabseemut .gt_right { text-align: right; font-variant-numeric: tabular-nums; }
 #ckabseemut .gt_font_normal { font-weight: normal; }
 #ckabseemut .gt_font_bold { font-weight: bold; }
 #ckabseemut .gt_font_italic { font-style: italic; }
 #ckabseemut .gt_super { font-size: 65%; }
 #ckabseemut .gt_footnotes { color: font-color(#FFFFFF); background-color: #FFFFFF; border-bottom-style: none; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; }
 #ckabseemut .gt_footnote { margin: 0px; font-size: 90%; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; }
 #ckabseemut .gt_sourcenotes { color: #333333; background-color: #FFFFFF; border-bottom-style: none; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; }
 #ckabseemut .gt_sourcenote { font-size: 90%; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; text-align: left; }
 #ckabseemut .gt_footnote_marks { font-size: 75%; vertical-align: 0.4em; position: initial; }
 #ckabseemut .gt_asterisk { font-size: 100%; vertical-align: 0; }
 &#10;</style>

| Internal consistency — 2026                      |        |
|--------------------------------------------------|--------|
| check                                            | value  |
| mean adj_em, teams with 10+ games (should be ~0) | 1.3497 |
| corr(adj_em, raw margin)                         | 0.9496 |
| corr(adj_em, adj_em_z) (should be ~1)            | 1.0000 |

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

<div id="tdbupuawwc" style="padding-left:0px;padding-right:0px;padding-top:10px;padding-bottom:10px;overflow-x:auto;overflow-y:auto;width:auto;height:auto;">
<style>
#tdbupuawwc table {
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Helvetica Neue', 'Fira Sans', 'Droid Sans', Arial, sans-serif;
          -webkit-font-smoothing: antialiased;
          -moz-osx-font-smoothing: grayscale;
        }
&#10;#tdbupuawwc thead, tbody, tfoot, tr, td, th { border-style: none; }
 tr { background-color: transparent; }
#tdbupuawwc p { margin: 0; padding: 0; }
 #tdbupuawwc .gt_table { display: table; border-collapse: collapse; line-height: normal; margin-left: auto; margin-right: auto; color: #333333; font-size: 16px; font-weight: normal; font-style: normal; background-color: #FFFFFF; width: auto; border-top-style: solid; border-top-width: 2px; border-top-color: #A8A8A8; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #A8A8A8; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; }
 #tdbupuawwc .gt_caption { padding-top: 4px; padding-bottom: 4px; }
 #tdbupuawwc .gt_title { color: #333333; font-size: 125%; font-weight: initial; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; border-bottom-color: #FFFFFF; border-bottom-width: 0; }
 #tdbupuawwc .gt_subtitle { color: #333333; font-size: 85%; font-weight: initial; padding-top: 3px; padding-bottom: 5px; padding-left: 5px; padding-right: 5px; border-top-color: #FFFFFF; border-top-width: 0; }
 #tdbupuawwc .gt_heading { background-color: #FFFFFF; text-align: center; border-bottom-color: #FFFFFF; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; }
 #tdbupuawwc .gt_bottom_border { border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; }
 #tdbupuawwc .gt_col_headings { border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; }
 #tdbupuawwc .gt_col_heading { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: normal; text-transform: inherit; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; vertical-align: bottom; padding-top: 5px; padding-bottom: 5px; padding-left: 5px; padding-right: 5px; overflow-x: hidden; }
 #tdbupuawwc .gt_column_spanner_outer { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: normal; text-transform: inherit; padding-top: 0; padding-bottom: 0; padding-left: 4px; padding-right: 4px; }
 #tdbupuawwc .gt_column_spanner_outer:first-child { padding-left: 0; }
 #tdbupuawwc .gt_column_spanner_outer:last-child { padding-right: 0; }
 #tdbupuawwc .gt_column_spanner { border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; vertical-align: bottom; padding-top: 5px; padding-bottom: 5px; overflow-x: hidden; display: inline-block; width: 100%; }
 #tdbupuawwc .gt_spanner_row { border-bottom-style: hidden; }
 #tdbupuawwc .gt_group_heading { padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; text-transform: inherit; border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; vertical-align: middle; text-align: left; }
 #tdbupuawwc .gt_empty_group_heading { padding: 0.5px; color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; vertical-align: middle; }
 #tdbupuawwc .gt_from_md> :first-child { margin-top: 0; }
 #tdbupuawwc .gt_from_md> :last-child { margin-bottom: 0; }
 #tdbupuawwc .gt_row { padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; margin: 10px; border-top-style: solid; border-top-width: 1px; border-top-color: #D3D3D3; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; vertical-align: middle; overflow-x: hidden; }
 #tdbupuawwc .gt_stub { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; text-transform: inherit; border-right-style: solid; border-right-width: 2px; border-right-color: #D3D3D3; padding-left: 5px; padding-right: 5px; }
 #tdbupuawwc .gt_indent_1 { text-indent: 5px; }
 #tdbupuawwc .gt_indent_2 { text-indent: calc(5px * 2); }
 #tdbupuawwc .gt_indent_3 { text-indent: calc(5px * 3); }
 #tdbupuawwc .gt_indent_4 { text-indent: calc(5px * 4); }
 #tdbupuawwc .gt_indent_5 { text-indent: calc(5px * 5); }
 #tdbupuawwc .gt_stub_row_group { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; text-transform: inherit; border-right-style: solid; border-right-width: 2px; border-right-color: #D3D3D3; padding-left: 5px; padding-right: 5px; vertical-align: top; }
 #tdbupuawwc .gt_row_group_first td { border-top-width: 2px; }
 #tdbupuawwc .gt_row_group_first th { border-top-width: 2px; }
 #tdbupuawwc .gt_striped { color: #333333; background-color: #F4F4F4; }
 #tdbupuawwc .gt_table_body { border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; }
 #tdbupuawwc .gt_summary_row { color: #333333; background-color: #FFFFFF; text-transform: inherit; padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; }
 #tdbupuawwc .gt_first_summary_row { border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; }
 #tdbupuawwc .gt_last_summary_row_top { border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; }
 #tdbupuawwc .gt_grand_summary_row { color: #333333; background-color: #FFFFFF; text-transform: inherit; padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; }
 #tdbupuawwc .gt_first_grand_summary_row_bottom { border-top-style: double; border-top-width: 6px; border-top-color: #D3D3D3; }
 #tdbupuawwc .gt_last_grand_summary_row_top { border-bottom-style: double; border-bottom-width: 6px; border-bottom-color: #D3D3D3; }
 #tdbupuawwc .gt_sourcenotes { color: #333333; background-color: #FFFFFF; border-bottom-style: none; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; }
 #tdbupuawwc .gt_sourcenote { font-size: 90%; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; text-align: left; }
 #tdbupuawwc .gt_left { text-align: left; }
 #tdbupuawwc .gt_center { text-align: center; }
 #tdbupuawwc .gt_right { text-align: right; font-variant-numeric: tabular-nums; }
 #tdbupuawwc .gt_font_normal { font-weight: normal; }
 #tdbupuawwc .gt_font_bold { font-weight: bold; }
 #tdbupuawwc .gt_font_italic { font-style: italic; }
 #tdbupuawwc .gt_super { font-size: 65%; }
 #tdbupuawwc .gt_footnotes { color: font-color(#FFFFFF); background-color: #FFFFFF; border-bottom-style: none; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; }
 #tdbupuawwc .gt_footnote { margin: 0px; font-size: 90%; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; }
 #tdbupuawwc .gt_sourcenotes { color: #333333; background-color: #FFFFFF; border-bottom-style: none; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; }
 #tdbupuawwc .gt_sourcenote { font-size: 90%; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; text-align: left; }
 #tdbupuawwc .gt_footnote_marks { font-size: 75%; vertical-align: 0.4em; position: initial; }
 #tdbupuawwc .gt_asterisk { font-size: 100%; vertical-align: 0; }
 &#10;</style>

| Program stickiness — adj_em season S vs S+1, same team |  |  |
|----|----|----|
| published-asset check; programs are persistent, rosters are not — the gap is roster turnover |  |  |
| season | yoy_pearson | teams |
| 2008 | 0.729 | 332 |
| 2009 | 0.656 | 291 |
| 2010 | 0.613 | 226 |
| 2011 | 0.686 | 235 |
| 2012 | 0.729 | 330 |
| 2013 | 0.765 | 334 |
| 2014 | <na> | 317 |
| 2015 | <na> | 323 |
| 2016 | 0.803 | 344 |
| 2017 | 0.870 | 353 |
| 2018 | 0.881 | 351 |
| 2019 | 0.836 | 355 |
| 2020 | 0.878 | 376 |
| 2021 | 0.887 | 390 |
| 2022 | 0.900 | 472 |
| 2023 | 0.905 | 484 |
| 2024 | 0.886 | 496 |
| 2025 | 0.892 | 519 |

&#10;</div>

## Level gate — the scale check a rank gate cannot do

Spearman is invariant to a **common strictly increasing** rescale:
multiply every rating by 100, or divide them all by the same constant,
and the rank correlation against KenPom or Torvik does not move. That is
how a ratings scale bug ships past a rank-only gate (it happened in this
ecosystem’s CFB ratings). Two errors it *does* see: a sign flip reverses
the order, so a positive rank correlation turns negative, and dividing
each team by its OWN games count is not a common transform, so it can
reorder teams too. The rank gate is the sign-and-order check; the level
gate is what catches an absolute-scale error that leaves the order alone
– a sign flip of a small mean `adj_em` lands well inside the band, so
neither gate is redundant. The publish path of this repository therefore
carries an **absolute level gate** beside the engine’s rank gates: over
the core — teams with at least `MIN_GAMES_GATED` games — the season’s
mean `adj_o`, `adj_d`, `adj_em` and `adj_tempo` and the spread of
`adj_em` must sit inside bands set from the observed published seasons
and in-season snapshots, with no non-finite value; it applies once
`MIN_GATED_TEAMS` teams qualify and logs, rather than pretends, before
that. The table is the gate re-run at render time on the assets
consumers download.

<div id="zuahdbjrjr" style="padding-left:0px;padding-right:0px;padding-top:10px;padding-bottom:10px;overflow-x:auto;overflow-y:auto;width:auto;height:auto;">
<style>
#zuahdbjrjr table {
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Helvetica Neue', 'Fira Sans', 'Droid Sans', Arial, sans-serif;
          -webkit-font-smoothing: antialiased;
          -moz-osx-font-smoothing: grayscale;
        }
&#10;#zuahdbjrjr thead, tbody, tfoot, tr, td, th { border-style: none; }
 tr { background-color: transparent; }
#zuahdbjrjr p { margin: 0; padding: 0; }
 #zuahdbjrjr .gt_table { display: table; border-collapse: collapse; line-height: normal; margin-left: auto; margin-right: auto; color: #333333; font-size: 16px; font-weight: normal; font-style: normal; background-color: #FFFFFF; width: auto; border-top-style: solid; border-top-width: 2px; border-top-color: #A8A8A8; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #A8A8A8; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; }
 #zuahdbjrjr .gt_caption { padding-top: 4px; padding-bottom: 4px; }
 #zuahdbjrjr .gt_title { color: #333333; font-size: 125%; font-weight: initial; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; border-bottom-color: #FFFFFF; border-bottom-width: 0; }
 #zuahdbjrjr .gt_subtitle { color: #333333; font-size: 85%; font-weight: initial; padding-top: 3px; padding-bottom: 5px; padding-left: 5px; padding-right: 5px; border-top-color: #FFFFFF; border-top-width: 0; }
 #zuahdbjrjr .gt_heading { background-color: #FFFFFF; text-align: center; border-bottom-color: #FFFFFF; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; }
 #zuahdbjrjr .gt_bottom_border { border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; }
 #zuahdbjrjr .gt_col_headings { border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; }
 #zuahdbjrjr .gt_col_heading { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: normal; text-transform: inherit; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; vertical-align: bottom; padding-top: 5px; padding-bottom: 5px; padding-left: 5px; padding-right: 5px; overflow-x: hidden; }
 #zuahdbjrjr .gt_column_spanner_outer { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: normal; text-transform: inherit; padding-top: 0; padding-bottom: 0; padding-left: 4px; padding-right: 4px; }
 #zuahdbjrjr .gt_column_spanner_outer:first-child { padding-left: 0; }
 #zuahdbjrjr .gt_column_spanner_outer:last-child { padding-right: 0; }
 #zuahdbjrjr .gt_column_spanner { border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; vertical-align: bottom; padding-top: 5px; padding-bottom: 5px; overflow-x: hidden; display: inline-block; width: 100%; }
 #zuahdbjrjr .gt_spanner_row { border-bottom-style: hidden; }
 #zuahdbjrjr .gt_group_heading { padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; text-transform: inherit; border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; vertical-align: middle; text-align: left; }
 #zuahdbjrjr .gt_empty_group_heading { padding: 0.5px; color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; vertical-align: middle; }
 #zuahdbjrjr .gt_from_md> :first-child { margin-top: 0; }
 #zuahdbjrjr .gt_from_md> :last-child { margin-bottom: 0; }
 #zuahdbjrjr .gt_row { padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; margin: 10px; border-top-style: solid; border-top-width: 1px; border-top-color: #D3D3D3; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; vertical-align: middle; overflow-x: hidden; }
 #zuahdbjrjr .gt_stub { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; text-transform: inherit; border-right-style: solid; border-right-width: 2px; border-right-color: #D3D3D3; padding-left: 5px; padding-right: 5px; }
 #zuahdbjrjr .gt_indent_1 { text-indent: 5px; }
 #zuahdbjrjr .gt_indent_2 { text-indent: calc(5px * 2); }
 #zuahdbjrjr .gt_indent_3 { text-indent: calc(5px * 3); }
 #zuahdbjrjr .gt_indent_4 { text-indent: calc(5px * 4); }
 #zuahdbjrjr .gt_indent_5 { text-indent: calc(5px * 5); }
 #zuahdbjrjr .gt_stub_row_group { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; text-transform: inherit; border-right-style: solid; border-right-width: 2px; border-right-color: #D3D3D3; padding-left: 5px; padding-right: 5px; vertical-align: top; }
 #zuahdbjrjr .gt_row_group_first td { border-top-width: 2px; }
 #zuahdbjrjr .gt_row_group_first th { border-top-width: 2px; }
 #zuahdbjrjr .gt_striped { color: #333333; background-color: #F4F4F4; }
 #zuahdbjrjr .gt_table_body { border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; }
 #zuahdbjrjr .gt_summary_row { color: #333333; background-color: #FFFFFF; text-transform: inherit; padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; }
 #zuahdbjrjr .gt_first_summary_row { border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; }
 #zuahdbjrjr .gt_last_summary_row_top { border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; }
 #zuahdbjrjr .gt_grand_summary_row { color: #333333; background-color: #FFFFFF; text-transform: inherit; padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; }
 #zuahdbjrjr .gt_first_grand_summary_row_bottom { border-top-style: double; border-top-width: 6px; border-top-color: #D3D3D3; }
 #zuahdbjrjr .gt_last_grand_summary_row_top { border-bottom-style: double; border-bottom-width: 6px; border-bottom-color: #D3D3D3; }
 #zuahdbjrjr .gt_sourcenotes { color: #333333; background-color: #FFFFFF; border-bottom-style: none; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; }
 #zuahdbjrjr .gt_sourcenote { font-size: 90%; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; text-align: left; }
 #zuahdbjrjr .gt_left { text-align: left; }
 #zuahdbjrjr .gt_center { text-align: center; }
 #zuahdbjrjr .gt_right { text-align: right; font-variant-numeric: tabular-nums; }
 #zuahdbjrjr .gt_font_normal { font-weight: normal; }
 #zuahdbjrjr .gt_font_bold { font-weight: bold; }
 #zuahdbjrjr .gt_font_italic { font-style: italic; }
 #zuahdbjrjr .gt_super { font-size: 65%; }
 #zuahdbjrjr .gt_footnotes { color: font-color(#FFFFFF); background-color: #FFFFFF; border-bottom-style: none; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; }
 #zuahdbjrjr .gt_footnote { margin: 0px; font-size: 90%; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; }
 #zuahdbjrjr .gt_sourcenotes { color: #333333; background-color: #FFFFFF; border-bottom-style: none; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; }
 #zuahdbjrjr .gt_sourcenote { font-size: 90%; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; text-align: left; }
 #zuahdbjrjr .gt_footnote_marks { font-size: 75%; vertical-align: 0.4em; position: initial; }
 #zuahdbjrjr .gt_asterisk { font-size: 100%; vertical-align: 0; }
 &#10;</style>

| Level gate re-run on the published assets (teams with 10+ games; applies at 150+ such teams) |  |  |  |  |  |  |  |  |
|----|----|----|----|----|----|----|----|----|
| bands: mean adj_o in \[85, 105\], mean adj_d in \[80, 100\], mean adj_em in \[-12, 12\], mean adj_tempo in \[64, 78\], sd adj_em in \[14, 28\] |  |  |  |  |  |  |  |  |
| season | core_teams | non_finite | mean_adj_o | mean_adj_d | mean_adj_em | mean_adj_tempo | sd_adj_em | verdict |
| 2008 | 158 | 0 | 119.37 | 116.26 | 3.12 | 54.52 | 23.30 | REFUSED: out of band |
| 2009 | 71 | 0 | 122.97 | 111.47 | 11.51 | 54.35 | 15.90 | not applied (too few core teams) |
| 2010 | 66 | 0 | 120.52 | 113.02 | 7.50 | 55.09 | 16.14 | not applied (too few core teams) |
| 2011 | 45 | 0 | 123.13 | 113.72 | 9.41 | 55.57 | 16.06 | not applied (too few core teams) |
| 2012 | 78 | 0 | 119.75 | 110.41 | 9.33 | 54.59 | 18.23 | not applied (too few core teams) |
| 2013 | 101 | 0 | 91.85 | 84.88 | 6.97 | 70.77 | 14.94 | not applied (too few core teams) |
| 2014 | 83 | 0 | 98.79 | 91.52 | 7.26 | 71.30 | 12.57 | not applied (too few core teams) |
| 2015 | 78 | 78 | <na> | <na> | <na> | <na> | <na> | REFUSED: non-finite ratings |
| 2016 | 84 | 0 | 96.88 | 89.18 | 7.70 | 70.33 | 13.47 | not applied (too few core teams) |
| 2017 | 349 | 0 | 91.86 | 93.09 | −1.23 | 69.90 | 19.00 | pass |
| 2018 | 349 | 0 | 93.04 | 94.23 | −1.19 | 70.00 | 18.91 | pass |
| 2019 | 351 | 0 | 92.01 | 93.18 | −1.17 | 70.24 | 19.10 | pass |
| 2020 | 351 | 0 | 92.20 | 91.20 | 1.00 | 70.79 | 18.12 | pass |
| 2021 | 333 | 0 | 92.12 | 92.96 | −0.83 | 70.67 | 20.08 | pass |
| 2022 | 356 | 0 | 91.88 | 91.18 | 0.70 | 70.12 | 18.53 | pass |
| 2023 | 361 | 0 | 92.56 | 91.97 | 0.59 | 70.35 | 19.66 | pass |
| 2024 | 360 | 0 | 92.97 | 92.12 | 0.84 | 70.39 | 19.95 | pass |
| 2025 | 362 | 0 | 93.04 | 92.27 | 0.78 | 70.41 | 20.73 | pass |
| 2026 | 363 | 0 | 93.15 | 91.80 | 1.35 | 70.82 | 21.03 | pass |

&#10;</div>

The bands were set on 2026-09-01 from the published 2017–2026 assets —
the full-coverage era — plus in-season engine snapshots (2024, 2025 and
2026 from Dec 10 to season end): core teams 333–363 at season end and
151+ from about Dec 10–20; mean adj_o 91.9–97.6; mean adj_d 86.95–94.2;
mean adj_em −1.2 to 10.6 (the high end is mid-December, when the core is
small and unbalanced; ≤ 1.4 at season end); sd adj_em 18.1–23.1; mean
adj_tempo 69.9–72.6. Each band is the observed range padded so a real
season never trips it while a unit or scale error does — per-game
instead of per-100 divides every level by ~1.5, a sign flip mirrors
adj_em, and an un-converged fixed point (the published 2015 asset, every
team NaN) fails the finiteness check.

Two archive-era consequences are deliberate, and are recorded rather
than papered over by widening the band. The 2008 asset sits on a
different scale (158 core teams, mean adj_o 119.4, mean adj_tempo 54.5 —
the pre-2013 box schema under-counts possessions) and is **refused**;
2009–2016 carry 45–101 core teams, below the applicability floor, so the
gate reports that it did not apply rather than pretending to. Both are
inputs to repair, not reasons to lower a gate.

## Results

<div id="xnhvlbutnl" style="padding-left:0px;padding-right:0px;padding-top:10px;padding-bottom:10px;overflow-x:auto;overflow-y:auto;width:auto;height:auto;">
<style>
#xnhvlbutnl table {
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Helvetica Neue', 'Fira Sans', 'Droid Sans', Arial, sans-serif;
          -webkit-font-smoothing: antialiased;
          -moz-osx-font-smoothing: grayscale;
        }
&#10;#xnhvlbutnl thead, tbody, tfoot, tr, td, th { border-style: none; }
 tr { background-color: transparent; }
#xnhvlbutnl p { margin: 0; padding: 0; }
 #xnhvlbutnl .gt_table { display: table; border-collapse: collapse; line-height: normal; margin-left: auto; margin-right: auto; color: #333333; font-size: 16px; font-weight: normal; font-style: normal; background-color: #FFFFFF; width: auto; border-top-style: solid; border-top-width: 2px; border-top-color: #A8A8A8; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #A8A8A8; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; }
 #xnhvlbutnl .gt_caption { padding-top: 4px; padding-bottom: 4px; }
 #xnhvlbutnl .gt_title { color: #333333; font-size: 125%; font-weight: initial; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; border-bottom-color: #FFFFFF; border-bottom-width: 0; }
 #xnhvlbutnl .gt_subtitle { color: #333333; font-size: 85%; font-weight: initial; padding-top: 3px; padding-bottom: 5px; padding-left: 5px; padding-right: 5px; border-top-color: #FFFFFF; border-top-width: 0; }
 #xnhvlbutnl .gt_heading { background-color: #FFFFFF; text-align: center; border-bottom-color: #FFFFFF; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; }
 #xnhvlbutnl .gt_bottom_border { border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; }
 #xnhvlbutnl .gt_col_headings { border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; }
 #xnhvlbutnl .gt_col_heading { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: normal; text-transform: inherit; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; vertical-align: bottom; padding-top: 5px; padding-bottom: 5px; padding-left: 5px; padding-right: 5px; overflow-x: hidden; }
 #xnhvlbutnl .gt_column_spanner_outer { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: normal; text-transform: inherit; padding-top: 0; padding-bottom: 0; padding-left: 4px; padding-right: 4px; }
 #xnhvlbutnl .gt_column_spanner_outer:first-child { padding-left: 0; }
 #xnhvlbutnl .gt_column_spanner_outer:last-child { padding-right: 0; }
 #xnhvlbutnl .gt_column_spanner { border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; vertical-align: bottom; padding-top: 5px; padding-bottom: 5px; overflow-x: hidden; display: inline-block; width: 100%; }
 #xnhvlbutnl .gt_spanner_row { border-bottom-style: hidden; }
 #xnhvlbutnl .gt_group_heading { padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; text-transform: inherit; border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; vertical-align: middle; text-align: left; }
 #xnhvlbutnl .gt_empty_group_heading { padding: 0.5px; color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; vertical-align: middle; }
 #xnhvlbutnl .gt_from_md> :first-child { margin-top: 0; }
 #xnhvlbutnl .gt_from_md> :last-child { margin-bottom: 0; }
 #xnhvlbutnl .gt_row { padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; margin: 10px; border-top-style: solid; border-top-width: 1px; border-top-color: #D3D3D3; border-left-style: none; border-left-width: 1px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 1px; border-right-color: #D3D3D3; vertical-align: middle; overflow-x: hidden; }
 #xnhvlbutnl .gt_stub { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; text-transform: inherit; border-right-style: solid; border-right-width: 2px; border-right-color: #D3D3D3; padding-left: 5px; padding-right: 5px; }
 #xnhvlbutnl .gt_indent_1 { text-indent: 5px; }
 #xnhvlbutnl .gt_indent_2 { text-indent: calc(5px * 2); }
 #xnhvlbutnl .gt_indent_3 { text-indent: calc(5px * 3); }
 #xnhvlbutnl .gt_indent_4 { text-indent: calc(5px * 4); }
 #xnhvlbutnl .gt_indent_5 { text-indent: calc(5px * 5); }
 #xnhvlbutnl .gt_stub_row_group { color: #333333; background-color: #FFFFFF; font-size: 100%; font-weight: initial; text-transform: inherit; border-right-style: solid; border-right-width: 2px; border-right-color: #D3D3D3; padding-left: 5px; padding-right: 5px; vertical-align: top; }
 #xnhvlbutnl .gt_row_group_first td { border-top-width: 2px; }
 #xnhvlbutnl .gt_row_group_first th { border-top-width: 2px; }
 #xnhvlbutnl .gt_striped { color: #333333; background-color: #F4F4F4; }
 #xnhvlbutnl .gt_table_body { border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; }
 #xnhvlbutnl .gt_summary_row { color: #333333; background-color: #FFFFFF; text-transform: inherit; padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; }
 #xnhvlbutnl .gt_first_summary_row { border-top-style: solid; border-top-width: 2px; border-top-color: #D3D3D3; }
 #xnhvlbutnl .gt_last_summary_row_top { border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: #D3D3D3; }
 #xnhvlbutnl .gt_grand_summary_row { color: #333333; background-color: #FFFFFF; text-transform: inherit; padding-top: 8px; padding-bottom: 8px; padding-left: 5px; padding-right: 5px; }
 #xnhvlbutnl .gt_first_grand_summary_row_bottom { border-top-style: double; border-top-width: 6px; border-top-color: #D3D3D3; }
 #xnhvlbutnl .gt_last_grand_summary_row_top { border-bottom-style: double; border-bottom-width: 6px; border-bottom-color: #D3D3D3; }
 #xnhvlbutnl .gt_sourcenotes { color: #333333; background-color: #FFFFFF; border-bottom-style: none; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; }
 #xnhvlbutnl .gt_sourcenote { font-size: 90%; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; text-align: left; }
 #xnhvlbutnl .gt_left { text-align: left; }
 #xnhvlbutnl .gt_center { text-align: center; }
 #xnhvlbutnl .gt_right { text-align: right; font-variant-numeric: tabular-nums; }
 #xnhvlbutnl .gt_font_normal { font-weight: normal; }
 #xnhvlbutnl .gt_font_bold { font-weight: bold; }
 #xnhvlbutnl .gt_font_italic { font-style: italic; }
 #xnhvlbutnl .gt_super { font-size: 65%; }
 #xnhvlbutnl .gt_footnotes { color: font-color(#FFFFFF); background-color: #FFFFFF; border-bottom-style: none; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; }
 #xnhvlbutnl .gt_footnote { margin: 0px; font-size: 90%; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; }
 #xnhvlbutnl .gt_sourcenotes { color: #333333; background-color: #FFFFFF; border-bottom-style: none; border-bottom-width: 2px; border-bottom-color: #D3D3D3; border-left-style: none; border-left-width: 2px; border-left-color: #D3D3D3; border-right-style: none; border-right-width: 2px; border-right-color: #D3D3D3; }
 #xnhvlbutnl .gt_sourcenote { font-size: 90%; padding-top: 4px; padding-bottom: 4px; padding-left: 5px; padding-right: 5px; text-align: left; }
 #xnhvlbutnl .gt_footnote_marks { font-size: 75%; vertical-align: 0.4em; position: initial; }
 #xnhvlbutnl .gt_asterisk { font-size: 100%; vertical-align: 0; }
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
  adjustment (em-scale fixed point); engine training + oracle (rank)
  gates live in sdv-py.
- **Level gate:**
  `python/wbb_model_publish/builders.py::assert_ratings_level` (bands,
  floor and observations recorded in `models/REGISTRY.md`); its
  per-season record is written into the `wbb_ratings_card.json` sidecar.
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
- **Resolved (2026-09-01, PR \#32):** the scale-blindness of the
  Spearman-style checks is closed in this repository by the absolute
  level gate above (`assert_ratings_level`), run at publish beside
  sdv-py’s rank gates and re-run on the published assets in this
  document.
- **Known issue:** the published `wbb_ratings_2015.parquet` is entirely
  NaN (335/335 teams; the fixed point did not converge on that season’s
  inputs), which is also what makes every 2015 row of `wbb_player_value`
  NaN. The level gate refuses it, so the repair is upstream in the
  engine/inputs, then a republish.
- **Known issue:** the 2008–2016 archive seasons have thin `team_box`
  coverage (45–158 teams with 10+ games) and the pre-2013 seasons sit on
  a different possession scale; they are published but sit outside (or
  below) the level gate’s applicability.
