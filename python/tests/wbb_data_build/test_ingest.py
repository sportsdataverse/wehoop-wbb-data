import polars as pl

from wbb_data_build import ingest


def test_read_final_missing_returns_none(tmp_path):
    assert ingest.read_final(999, raw_root=tmp_path) is None


def test_season_game_ids_filters_game_json(tmp_path):
    sched_dir = tmp_path / "wbb" / "schedules" / "parquet"
    sched_dir.mkdir(parents=True)
    pl.DataFrame({"game_id": [1, 2, 3], "game_json": [True, False, True]}).write_parquet(
        sched_dir / "wbb_schedule_2025.parquet"
    )
    assert ingest.season_game_ids(2025, raw_root=tmp_path) == [1, 3]


class _FakeResp:
    def __init__(self, status, content=b"", headers=None):
        self.status_code = status
        self.content = content
        self.headers = headers or {}


def _patch_http(monkeypatch, responses):
    """requests.get returns the scripted responses in order; records sleeps."""
    import requests

    calls = {"urls": [], "sleeps": []}
    seq = iter(responses)
    monkeypatch.setattr(
        requests, "get", lambda url, **kw: (calls["urls"].append(url), next(seq))[1]
    )
    import time

    monkeypatch.setattr(time, "sleep", lambda s: calls["sleeps"].append(s))
    return calls


def test_http_get_bytes_retries_throttling_then_succeeds(monkeypatch):
    """A 429 is throttling, not absence -- the original any-non-200 -> None
    silently compiled throttled seasons to ~40 games."""
    calls = _patch_http(
        monkeypatch,
        [_FakeResp(429, headers={"Retry-After": "0"}), _FakeResp(503), _FakeResp(200, b"body")],
    )

    assert ingest._http_get_bytes("https://raw.example/x.json") == b"body"
    assert len(calls["urls"]) == 3
    assert len(calls["sleeps"]) == 2


def test_http_get_bytes_404_is_immediate_none(monkeypatch):
    calls = _patch_http(monkeypatch, [_FakeResp(404)])

    assert ingest._http_get_bytes("https://raw.example/x.json") is None
    assert len(calls["urls"]) == 1  # genuinely absent: no retry
    assert calls["sleeps"] == []


def test_http_get_bytes_gives_up_after_exhausting_retries(monkeypatch):
    calls = _patch_http(monkeypatch, [_FakeResp(429)] * ingest._RETRY_ATTEMPTS)

    assert ingest._http_get_bytes("https://raw.example/x.json") is None
    assert len(calls["urls"]) == ingest._RETRY_ATTEMPTS
