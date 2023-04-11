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

[wehoop-wnba-raw data repository (source: ESPN)](https://github.com/sportsdataverse/wehoop-wnba-raw)

[wehoop-wnba-data repository (source: ESPN)](https://github.com/sportsdataverse/wehoop-wnba-data)

[wehoop-wnba-stats-data Repo (source: WNBA Stats)](https://github.com/sportsdataverse/wehoop-wnba-stats-data)

[wehoop-wbb-raw data repository (source: ESPN)](https://github.com/sportsdataverse/wehoop-wbb-raw)

[wehoop-wbb-data repository (source: ESPN)](https://github.com/sportsdataverse/wehoop-wbb-data)