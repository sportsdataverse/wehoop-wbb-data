"""HTTP ingest mode: raw_root as the raw.githubusercontent base URL.

The 58GB wehoop-wbb-raw repo cannot be checked out in CI, so ingest mirrors
what the R pipeline always did — per-file HTTP reads — with a per-run local
cache. Tests are hermetic: the transport (``ingest._http_get_bytes``) is
monkeypatched to serve the committed fixture bytes.
"""

import json
from pathlib import Path

from wbb_data_build import ingest

FX = Path(__file__).parent.parent / "fixtures"
BASE = "https://raw.example.test/wehoop-wbb-raw/main"


def _fake_transport(monkeypatch, mapping):
    def fake(url):
        return mapping.get(url)

    monkeypatch.setattr(ingest, "_http_get_bytes", fake)


def test_read_final_http_fetches_and_caches(monkeypatch, tmp_path):
    monkeypatch.setenv("WEHOOP_WBB_CACHE", str(tmp_path / "cache"))
    body = (FX / "raw" / "wbb" / "json" / "final" / "401700473.json").read_bytes()
    _fake_transport(monkeypatch, {f"{BASE}/wbb/json/final/401700473.json": body})
    d = ingest.read_final(401700473, raw_root=BASE)
    assert d["header"]["id"] == "401700473"
    # second read must hit the cache (transport now returns None for everything)
    _fake_transport(monkeypatch, {})
    assert ingest.read_final(401700473, raw_root=BASE)["header"]["id"] == "401700473"


def test_read_final_http_missing_returns_none(monkeypatch, tmp_path):
    monkeypatch.setenv("WEHOOP_WBB_CACHE", str(tmp_path / "cache"))
    _fake_transport(monkeypatch, {})
    assert ingest.read_final(999, raw_root=BASE) is None


def test_season_game_ids_http(monkeypatch, tmp_path):
    monkeypatch.setenv("WEHOOP_WBB_CACHE", str(tmp_path / "cache"))
    body = (FX / "raw" / "wbb" / "schedules" / "parquet" / "wbb_schedule_2025.parquet").read_bytes()
    _fake_transport(monkeypatch, {f"{BASE}/wbb/schedules/parquet/wbb_schedule_2025.parquet": body})
    # HTTP mode must be indistinguishable from the disk mode (same rows, same order).
    assert ingest.season_game_ids(2025, raw_root=BASE) == ingest.season_game_ids(
        2025, raw_root=FX / "raw"
    )
    assert sorted(ingest.season_game_ids(2025, raw_root=BASE)) == [
        401700473,
        401700474,
        401700475,
    ]


def test_season_game_ids_http_missing_schedule(monkeypatch, tmp_path):
    _fake_transport(monkeypatch, {})
    assert ingest.season_game_ids(1999, raw_root=BASE) == []


def test_season_dir_ids_http_contents_api(monkeypatch, tmp_path):
    listing = json.dumps([{"name": "197.json"}, {"name": "2429.json"}, {"name": "README.md"}])
    _fake_transport(
        monkeypatch,
        {
            "https://api.github.com/repos/sportsdataverse/wehoop-wbb-raw/contents/wbb/team_rosters/json/2026": listing.encode()
        },
    )
    assert ingest.season_dir_ids("team_rosters", 2026, raw_root=BASE) == [197, 2429]
