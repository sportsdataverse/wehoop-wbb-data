# wehoop-wbb-data

```mermaid
  graph LR;
    A[wehoop-wbb-raw]-->B[wehoop-wbb-data];
    B[wehoop-wbb-data]-->C1[espn_womens_college_basketball_pbp];
    B[wehoop-wbb-data]-->C2[espn_womens_college_basketball_team_boxscores];
    B[wehoop-wbb-data]-->C3[espn_womens_college_basketball_player_boxscores];

```

## wehoop ESPN WBB workflow diagram

```mermaid
flowchart TB;
    subgraph A[wehoop-wbb-raw];
        direction TB;
        A1[python/scrape_wbb_schedules.py]-->A2[python/scrape_wbb_json.py];
    end;

    subgraph B[wehoop-wbb-data];
        direction TB;
        B1[R/espn_wbb_01_pbp_creation.R]-->B2[R/espn_wbb_02_team_box_creation.R];
        B2[R/espn_wbb_02_team_box_creation.R]-->B3[R/espn_wbb_03_player_box_creation.R];
    end;

    subgraph C[sportsdataverse Releases];
        direction TB;
        C1[espn_womens_college_basketball_pbp];
        C2[espn_womens_college_basketball_team_boxscores];
        C3[espn_womens_college_basketball_player_boxscores];
    end;

    A-->B;
    B-->C1;
    B-->C2;
    B-->C3;

```

## Women's Basketball Data Releases

[ESPN Women's College Basketball Schedules](https://github.com/sportsdataverse/sportsdataverse-data/releases/tag/espn_womens_college_basketball_schedules)

[ESPN Women's College Basketball PBP](https://github.com/sportsdataverse/sportsdataverse-data/releases/tag/espn_womens_college_basketball_pbp)

[ESPN Women's College Basketball Team Boxscores](https://github.com/sportsdataverse/sportsdataverse-data/releases/tag/espn_womens_college_basketball_team_boxscores)

[ESPN Women's College Basketball Player Boxscores](https://github.com/sportsdataverse/sportsdataverse-data/releases/tag/espn_womens_college_basketball_player_boxscores)

[ESPN WNBA Schedules](https://github.com/sportsdataverse/sportsdataverse-data/releases/tag/espn_wnba_schedules)

[ESPN WNBA PBP](https://github.com/sportsdataverse/sportsdataverse-data/releases/tag/espn_wnba_pbp)

[ESPN WNBA Team Boxscores](https://github.com/sportsdataverse/sportsdataverse-data/releases/tag/espn_wnba_team_boxscores)

[ESPN WNBA Player Boxscores](https://github.com/sportsdataverse/sportsdataverse-data/releases/tag/espn_wnba_player_boxscores)


## Data Repositories

[wehoop-wnba-raw data repository (source: ESPN)](https://github.com/sportsdataverse/wehoop-wnba-raw)

[wehoop-wnba-data repository (source: ESPN)](https://github.com/sportsdataverse/wehoop-wnba-data)

[wehoop-wnba-stats-data Repo (source: NBA Stats)](https://github.com/sportsdataverse/wehoop-wnba-stats-data)

[wehoop-wbb-raw data repository (source: ESPN)](https://github.com/sportsdataverse/wehoop-wbb-raw)

[wehoop-wbb-data repository (source: ESPN)](https://github.com/sportsdataverse/wehoop-wbb-data)

## Datasets

<!-- BEGIN GENERATED: datasets -->
| Script | Dataset | Release tag | Last published |
|---|---|---|---|
| [`python/espn_wbb_01_pbp_creation.py`](python/espn_wbb_01_pbp_creation.py) | [`pbp`](docs/datasets/pbp.md) | [`espn_womens_college_basketball_pbp`](https://github.com/sportsdataverse/sportsdataverse-data/releases/tag/espn_womens_college_basketball_pbp) | 2026-08-03 |
| [`python/espn_wbb_02_team_box_creation.py`](python/espn_wbb_02_team_box_creation.py) | [`team_box`](docs/datasets/team_box.md) | [`espn_womens_college_basketball_team_boxscores`](https://github.com/sportsdataverse/sportsdataverse-data/releases/tag/espn_womens_college_basketball_team_boxscores) | 2026-07-17 |
| [`python/espn_wbb_03_player_box_creation.py`](python/espn_wbb_03_player_box_creation.py) | [`player_box`](docs/datasets/player_box.md) | [`espn_womens_college_basketball_player_boxscores`](https://github.com/sportsdataverse/sportsdataverse-data/releases/tag/espn_womens_college_basketball_player_boxscores) | 2026-07-17 |
| [`python/espn_wbb_04_player_core_creation.py`](python/espn_wbb_04_player_core_creation.py) | [`player_core`](docs/datasets/player_core.md) | [`espn_womens_college_basketball_player_core`](https://github.com/sportsdataverse/sportsdataverse-data/releases/tag/espn_womens_college_basketball_player_core) | 2026-07-17 |
| [`python/espn_wbb_05_schedules_creation.py`](python/espn_wbb_05_schedules_creation.py) | [`schedules`](docs/datasets/schedules.md) | [`espn_womens_college_basketball_schedules`](https://github.com/sportsdataverse/sportsdataverse-data/releases/tag/espn_womens_college_basketball_schedules) | 2026-07-17 |
| [`python/espn_wbb_06_shots_creation.py`](python/espn_wbb_06_shots_creation.py) | [`shots`](docs/datasets/shots.md) | [`espn_womens_college_basketball_shots`](https://github.com/sportsdataverse/sportsdataverse-data/releases/tag/espn_womens_college_basketball_shots) | 2026-07-29 |
| [`python/espn_wbb_07_rosters_creation.py`](python/espn_wbb_07_rosters_creation.py) | [`rosters`](docs/datasets/rosters.md) | [`espn_womens_college_basketball_rosters`](https://github.com/sportsdataverse/sportsdataverse-data/releases/tag/espn_womens_college_basketball_rosters) | 2026-08-09 |
| [`python/espn_wbb_08_player_season_stats_creation.py`](python/espn_wbb_08_player_season_stats_creation.py) | [`player_season_stats`](docs/datasets/player_season_stats.md) | [`espn_womens_college_basketball_player_season_stats`](https://github.com/sportsdataverse/sportsdataverse-data/releases/tag/espn_womens_college_basketball_player_season_stats) | 2026-07-17 |
| [`python/espn_wbb_09_team_season_stats_creation.py`](python/espn_wbb_09_team_season_stats_creation.py) | [`team_season_stats`](docs/datasets/team_season_stats.md) | [`espn_womens_college_basketball_team_season_stats`](https://github.com/sportsdataverse/sportsdataverse-data/releases/tag/espn_womens_college_basketball_team_season_stats) | 2026-07-17 |
| [`python/espn_wbb_10_standings_creation.py`](python/espn_wbb_10_standings_creation.py) | [`standings`](docs/datasets/standings.md) | [`espn_womens_college_basketball_standings`](https://github.com/sportsdataverse/sportsdataverse-data/releases/tag/espn_womens_college_basketball_standings) | 2026-07-17 |
| [`python/espn_wbb_11_game_rosters_creation.py`](python/espn_wbb_11_game_rosters_creation.py) | [`game_rosters`](docs/datasets/game_rosters.md) | [`espn_womens_college_basketball_game_rosters`](https://github.com/sportsdataverse/sportsdataverse-data/releases/tag/espn_womens_college_basketball_game_rosters) | 2026-07-17 |
| [`python/espn_wbb_12_officials_creation.py`](python/espn_wbb_12_officials_creation.py) | [`officials`](docs/datasets/officials.md) | [`espn_womens_college_basketball_officials`](https://github.com/sportsdataverse/sportsdataverse-data/releases/tag/espn_womens_college_basketball_officials) | 2026-07-17 |
| [`python/espn_wbb_13_team_crosswalk_creation.py`](python/espn_wbb_13_team_crosswalk_creation.py) | [`team_crosswalk`](docs/datasets/team_crosswalk.md) | [`wbb_crosswalk`](https://github.com/sportsdataverse/sportsdataverse-data/releases/tag/wbb_crosswalk) | 2026-07-17 |
| [`python/espn_wbb_14_schedule_crosswalk_creation.py`](python/espn_wbb_14_schedule_crosswalk_creation.py) | [`schedule_crosswalk`](docs/datasets/schedule_crosswalk.md) | [`wbb_crosswalk`](https://github.com/sportsdataverse/sportsdataverse-data/releases/tag/wbb_crosswalk) | 2026-07-17 |
| [`python/espn_wbb_15_player_crosswalk_creation.py`](python/espn_wbb_15_player_crosswalk_creation.py) | [`player_crosswalk`](docs/datasets/player_crosswalk.md) | [`wbb_crosswalk`](https://github.com/sportsdataverse/sportsdataverse-data/releases/tag/wbb_crosswalk) | 2026-07-17 |
<!-- END GENERATED: datasets -->
