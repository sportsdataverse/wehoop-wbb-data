"""Hermetic tests for the wbb model-publish builders.

The sdv-py compute seams are stubbed, so these assert *orchestration* --
season ordering, the empty-frame refusal, the floor, the card sidecars, and
per-file upload -- not the ratings/BPM math (gated in sdv-py's oracle suites).
"""

from __future__ import annotations

import json

import polars as pl
import pytest
from wbb_model_publish.artifacts import upload_artifacts
from wbb_model_publish.builders import (
    ADJ_EM_SD_BAND,
    MIN_GATED_TEAMS,
    QUALIFIED_MIN_MINUTES,
    RATINGS_LEVEL_BANDS,
    assert_ratings_level,
    build_player_value,
    build_ratings,
    write_player_value_card,
    write_player_value_coefficients,
    write_ratings_card,
)
from wbb_model_publish.cli import _seasons, main


def _fake_ratings(season: int) -> pl.DataFrame:
    return pl.DataFrame(
        {
            "season": [season, season],
            "team_id": ["52", "150"],
            "adj_o": [118.2, 112.4],
            "adj_d": [93.5, 96.1],
            "adj_em": [24.7, 16.3],
            "adj_tempo": [68.0, 70.5],
            "games": [31, 30],
            "rank": [1, 2],
        }
    )


def _fake_bpm(season: int) -> pl.DataFrame:
    return pl.DataFrame(
        {
            "player_id": ["4433137", "4592971"],
            "season": [season, season],
            "team_id": ["52", "150"],
            "min": [812.0, 140.0],
            "box_bpm": [8.4, 6.1],
        }
    )


def test_build_ratings_writes_one_parquet_per_season_in_order(tmp_path):
    results = build_ratings([2024, 2025], tmp_path, compute=_fake_ratings)

    assert [r["season"] for r in results] == [2024, 2025]
    for season in (2024, 2025):
        path = tmp_path / f"wbb_ratings_{season}.parquet"
        assert path.exists()
        assert pl.read_parquet(path)["season"].unique().to_list() == [season]


def test_build_player_value_writes_per_season(tmp_path):
    results = build_player_value([2025], tmp_path, compute=_fake_bpm)

    assert [r["rows"] for r in results] == [2]
    assert (tmp_path / "wbb_player_value_2025.parquet").exists()


def test_builders_refuse_an_empty_season(tmp_path):
    empty = pl.DataFrame(schema={"season": pl.Int64, "team_id": pl.Utf8})

    with pytest.raises(ValueError, match="0 rows"):
        build_ratings([2025], tmp_path, compute=lambda s: empty)
    with pytest.raises(ValueError, match="0 rows"):
        build_player_value([2025], tmp_path, compute=lambda s: empty)


def test_builders_reject_seasons_below_the_floor(tmp_path):
    from wbb_model_publish.builders import MIN_SEASON_PLAYER_VALUE, MIN_SEASON_RATINGS

    with pytest.raises(ValueError, match=str(MIN_SEASON_RATINGS)):
        build_ratings([MIN_SEASON_RATINGS - 1], tmp_path, compute=_fake_ratings)
    with pytest.raises(ValueError, match=str(MIN_SEASON_PLAYER_VALUE)):
        build_player_value([MIN_SEASON_PLAYER_VALUE - 1], tmp_path, compute=_fake_bpm)
    # ratings' wider floor must NOT gate player-value's builder and vice versa
    assert MIN_SEASON_RATINGS < MIN_SEASON_PLAYER_VALUE


def test_cards_carry_tag_and_seasons(tmp_path):
    r = build_ratings([2025], tmp_path, compute=_fake_ratings)
    card = json.loads(write_ratings_card(r, tmp_path).read_text(encoding="utf-8"))
    assert card["tag"] == "wbb_ratings"
    assert card["rows_by_season"] == {"2025": 2}

    v = build_player_value([2025], tmp_path, compute=_fake_bpm)
    card = json.loads(write_player_value_card(v, tmp_path).read_text(encoding="utf-8"))
    assert card["tag"] == "wbb_player_value"
    assert card["seasons"] == [2025]


def test_upload_pattern_selects_parquet_and_card(tmp_path):
    (tmp_path / "wbb_ratings_2025.parquet").write_bytes(b"x")
    (tmp_path / "wbb_ratings_card.json").write_text("{}")
    (tmp_path / "unrelated.txt").write_text("no")

    calls: list = []
    res = upload_artifacts(
        tmp_path,
        "wbb_ratings",
        "sportsdataverse/sportsdataverse-data",
        pattern="wbb_ratings_*.*",
        runner=lambda args: calls.append(args),
        exists_check=lambda tag, repo: True,
    )

    names = sorted(p.rsplit("\\", 1)[-1].rsplit("/", 1)[-1] for p in res["files"])
    assert names == ["wbb_ratings_2025.parquet", "wbb_ratings_card.json"]
    assert res["uploaded"] == 2
    assert all("--clobber" in c for c in calls)


def test_seasons_parses_range_and_single():
    assert _seasons("2025") == [2025]
    assert _seasons("2002:2005") == [2002, 2003, 2004, 2005]


def test_cli_build_only_writes_files_and_skips_upload(tmp_path, monkeypatch):
    import wbb_model_publish.cli as cli

    monkeypatch.setattr(
        cli,
        "build_ratings",
        lambda seasons, out, **kw: build_ratings(seasons, out, compute=_fake_ratings),
    )
    monkeypatch.setattr(
        cli,
        "upload_artifacts",
        lambda *a, **k: pytest.fail("--build-only must not upload"),
    )

    rc = main(["ratings", "--seasons", "2025", "--out", str(tmp_path), "--build-only"])

    assert rc == 0
    assert (tmp_path / "wbb_ratings_2025.parquet").exists()
    assert (tmp_path / "wbb_ratings_card.json").exists()


def test_publish_merges_the_new_season_into_the_released_card(tmp_path, monkeypatch):
    """A daily 2027 run must not drop the published 2025 season or its gate record."""
    import wbb_model_publish.cli as cli

    gate_2025 = {"applied": True, "teams": 360, "adj_em_sd": 19.8}
    gate_2027 = {"applied": True, "teams": 362, "adj_em_sd": 20.1}
    released = {
        "tag": "wbb_ratings",
        "seasons": [2025],
        "rows_by_season": {"2025": 362},
        "gates_by_season": {"2025": gate_2025},
    }
    fetched = []

    def fake_fetch(tag, repo, name):
        fetched.append((tag, repo, name))
        return released

    monkeypatch.setattr(cli, "fetch_release_card", fake_fetch)
    monkeypatch.setattr(
        cli,
        "build_ratings",
        lambda seasons, out, **kw: [
            {"season": 2027, "rows": 364, "path": "x.parquet", "gate": gate_2027}
        ],
    )
    monkeypatch.setattr(
        cli, "upload_artifacts", lambda *a, **k: {"uploaded": 0, "tag": "wbb_ratings"}
    )

    rc = main(["ratings", "--seasons", "2027", "--out", str(tmp_path)])

    assert rc == 0
    assert fetched == [
        ("wbb_ratings", "sportsdataverse/sportsdataverse-data", "wbb_ratings_card.json")
    ]
    card = json.loads((tmp_path / "wbb_ratings_card.json").read_text(encoding="utf-8"))
    assert card["seasons"] == [2025, 2027]
    assert card["rows_by_season"] == {"2025": 362, "2027": 364}
    assert card["gates_by_season"] == {"2025": gate_2025, "2027": gate_2027}


class _Resp:
    def __init__(self, status_code: int, body: dict | None = None):
        self.status_code, self._body = status_code, body

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")

    def json(self):
        return self._body


def test_fetch_release_card_404_means_a_fresh_card():
    from wbb_model_publish.artifacts import fetch_release_card

    urls = []

    def get(url, timeout):
        urls.append(url)
        return _Resp(404)

    assert fetch_release_card("wbb_ratings", "o/r", "wbb_ratings_card.json", get=get) is None
    assert urls == ["https://github.com/o/r/releases/download/wbb_ratings/wbb_ratings_card.json"]


@pytest.mark.parametrize("status", [401, 403, 500, 503])
def test_fetch_release_card_raises_on_any_other_failure(status):
    # a fresh card here would overwrite every published season with this run's
    from wbb_model_publish.artifacts import fetch_release_card

    with pytest.raises(RuntimeError, match=str(status)):
        fetch_release_card("t", "o/r", "c.json", get=lambda url, timeout: _Resp(status))


def test_fetch_release_card_returns_the_parsed_card():
    from wbb_model_publish.artifacts import fetch_release_card

    card = {"tag": "wbb_ratings", "seasons": [2025]}
    assert (
        fetch_release_card("t", "o/r", "c.json", get=lambda url, timeout: _Resp(200, card)) == card
    )


def test_rebuilding_a_released_season_replaces_it_and_keeps_the_others(tmp_path):
    old = {"applied": True, "teams": 300}
    new = {"applied": True, "teams": 362}
    released = {
        "seasons": [2024, 2025],
        "rows_by_season": {"2024": 350, "2025": 300},
        "gates_by_season": {"2024": {"applied": True, "teams": 350}, "2025": old},
    }
    results = [{"season": 2025, "rows": 362, "path": "x.parquet", "gate": new}]
    path = write_ratings_card(results, tmp_path, existing=released)
    card = json.loads(path.read_text(encoding="utf-8"))
    assert card["seasons"] == [2024, 2025]
    assert card["rows_by_season"] == {"2024": 350, "2025": 362}
    assert card["gates_by_season"] == {"2024": {"applied": True, "teams": 350}, "2025": new}


def _league_like_ratings(
    n: int = MIN_GATED_TEAMS, *, em_scale: float = 1.0, games: int = 30
) -> pl.DataFrame:
    """A plausible WBB D1-core season: adj_em symmetric around ~1 with sd ~20, per-100 levels ~93."""
    import numpy as np

    rng = np.random.default_rng(7)
    em = rng.normal(1.0, 20.0, n) * em_scale
    adj_o = 93.0 + em / 2
    return pl.DataFrame(
        {
            "season": [2025] * n,
            "team_id": [str(i) for i in range(n)],
            "adj_o": adj_o,
            "adj_d": adj_o - em,
            "adj_em": em,
            "adj_tempo": rng.normal(70.0, 3.0, n),
            "games": [games] * n,
        }
    )


# ---- player_value: the additive `qualified` flag ---------------------------------


def test_player_value_appends_qualified_without_dropping_rows(tmp_path):
    build_player_value([2025], tmp_path, compute=_fake_bpm)
    out = pl.read_parquet(tmp_path / "wbb_player_value_2025.parquet")
    assert out.height == 2  # never a filter
    assert set(_fake_bpm(2025).columns) <= set(out.columns)  # every published column preserved
    assert out["qualified"].to_list() == [
        812.0 >= QUALIFIED_MIN_MINUTES,
        140.0 >= QUALIFIED_MIN_MINUTES,
    ]
    assert out["qualified"].to_list() == [True, False]


def test_player_value_refuses_a_frame_without_minutes(tmp_path):
    with pytest.raises(ValueError, match="'min'"):
        build_player_value([2025], tmp_path, compute=lambda s: _fake_bpm(s).drop("min"))


# ---- ratings: the absolute level-band gate beside the rank gates -----------------


def test_ratings_level_gate_passes_a_league_shaped_season_and_records_it(tmp_path):
    results = build_ratings([2025], tmp_path, compute=lambda s: _league_like_ratings())
    gate = results[0]["gate"]
    assert gate["applied"] is True and gate["teams"] == MIN_GATED_TEAMS
    lo, hi = RATINGS_LEVEL_BANDS["adj_o"]
    assert lo <= gate["mean_adj_o"] <= hi
    assert ADJ_EM_SD_BAND[0] <= gate["sd_adj_em"] <= ADJ_EM_SD_BAND[1]
    card = json.loads(write_ratings_card(results, tmp_path).read_text(encoding="utf-8"))
    assert card["gates_by_season"]["2025"]["applied"] is True


def test_ratings_level_gate_refuses_a_rescaled_season_the_rank_gate_would_pass():
    # x100 keeps every rank identical (Spearman = 1.0 vs the true ratings) -- the
    # scale-blind failure -- and must be refused on level alone.
    with pytest.raises(ValueError, match="level band violated"):
        assert_ratings_level(_league_like_ratings(em_scale=100.0), 2025)
    # per-game instead of per-100 (everything / 1.5): ranks intact, levels off.
    perg = _league_like_ratings().with_columns(
        pl.col("adj_o") / 1.5, pl.col("adj_d") / 1.5, pl.col("adj_em") / 1.5
    )
    with pytest.raises(ValueError, match="level band violated"):
        assert_ratings_level(perg, 2025)


def test_ratings_level_gate_refuses_a_nan_fixed_point():
    # The published wbb_ratings_2015 asset is 335/335 NaN; NaN is not null in polars.
    nan = _league_like_ratings().with_columns(pl.lit(float("nan")).alias("adj_em"))
    with pytest.raises(ValueError, match="non-finite adj_em"):
        assert_ratings_level(nan, 2015)


def test_ratings_level_gate_refuses_infinite_ratings():
    # is_nan() does NOT match +/-inf in polars: on [1.0, nan, inf, -inf, null] the
    # old is_null()|is_nan() predicate caught 2 of the 4 bad values (polars 1.42.1),
    # so an infinite fixed point would have published. Both signs must be refused.
    for value in (float("inf"), float("-inf")):
        bad = _league_like_ratings().with_columns(pl.lit(value).alias("adj_em"))
        with pytest.raises(ValueError, match="non-finite adj_em"):
            assert_ratings_level(bad, 2011)


def test_ratings_level_gate_does_not_apply_to_a_season_too_young_to_have_a_level():
    rec = assert_ratings_level(_league_like_ratings(n=40), 2026)  # early November
    assert rec == {"applied": False, "teams": 40}
    rec = assert_ratings_level(_league_like_ratings(games=3), 2026)  # nobody has 10 games yet
    assert rec["applied"] is False and rec["teams"] == 0


# ---- player_value: the shipped coefficient vector --------------------------------


def test_player_value_coefficients_sidecar_ships_the_artifact_with_provenance(tmp_path):
    art = {
        "league": "womens",
        "feature_cols": ["usage", "ts_pct"],
        "obpm_coef": [-4.1, 1.9, 0.3],
        "dbpm_coef": [2.5, -0.1, 0.2],
        "feature_mean": {"usage": 0.2, "ts_pct": 0.5},
        "feature_sd": {"usage": 0.05, "ts_pct": 0.06},
        "min_minutes": 150.0,
        "train_seasons": [2025, 2026],
    }
    path = write_player_value_coefficients(tmp_path, load=lambda: art)
    assert (
        path.name == "wbb_player_value_coefficients.json"
    )  # matches the wbb_player_value_*.* upload glob
    out = json.loads(path.read_text(encoding="utf-8"))
    assert out["feature_cols"] == art["feature_cols"]
    assert len(out["obpm_coef"]) == len(out["feature_cols"]) + 1  # intercept + slopes
    assert out["artifact_sha256"] and out["written"] and "sportsdataverse_version" in out
