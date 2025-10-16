import pytest
import requests
from contributors.Luch1f3rchoCR.ex04_testing.app.services import validate_monster_index, fetch_monster

def test_validate_monster_index_ok():
    validate_monster_index("dragon")

@pytest.mark.parametrize("bad", ["", "   ", None, 123])
def test_validate_monster_index_fail(bad):
    with pytest.raises(ValueError, match="Invalid monster index"):
        validate_monster_index(bad)

def test_fetch_monster_uses_requests(monkeypatch):
    class _Resp:
        def raise_for_status(self): pass
        def json(self): return {"name": "Ancient Red Dragon", "type": "dragon"}
    def fake_get(url, timeout=5):
        assert url.endswith("/dragon")
        return _Resp()
    monkeypatch.setattr(requests, "get", fake_get)
    data = fetch_monster("dragon")
    assert data == {"name": "Ancient Red Dragon", "type": "dragon"}

def test_fetch_monster_http_error(monkeypatch):
    class _Resp:
        def raise_for_status(self): raise requests.HTTPError("boom")
        def json(self): return {}
    monkeypatch.setattr(requests, "get", lambda *a, **k: _Resp())
    with pytest.raises(requests.HTTPError):
        fetch_monster("dragon")