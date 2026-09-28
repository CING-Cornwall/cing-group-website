"""Council proxy routing and credential-safe failures."""
import pytest
from scripts import refresh_councillors as module


def test_council_only_proxy(monkeypatch):
    calls = []
    class Response:
        text = '<span>88%</span><span>overall attendance</span>'
        def raise_for_status(self):
            pass
    def get(url, **kwargs):
        calls.append((url, kwargs))
        return Response()
    monkeypatch.setenv('COUNCIL_PROXY_URL', 'http://user:secret@proxy:3128')
    monkeypatch.setattr(module.requests, 'get', get)
    monkeypatch.setattr(module, 'parse_committees_and_bodies', lambda html, uid: (['Committee'], []))
    module.fetch_committees_and_bodies(5756)
    assert module.fetch_attendance_percentage('rowland-oconnor') == 88
    assert calls[0][1]['proxies'] == {'https': 'http://user:secret@proxy:3128'}
    assert 'proxies' not in calls[1][1]


def test_no_proxy_preserves_direct_mode(monkeypatch):
    monkeypatch.delenv('COUNCIL_PROXY_URL', raising=False)
    def get(url, **kwargs):
        assert 'proxies' not in kwargs
        raise module.requests.ConnectionError('direct failure')
    monkeypatch.setattr(module.requests, 'get', get)
    with pytest.raises(module.requests.RequestException):
        module.fetch_committees_and_bodies(5756)


def test_proxy_error_does_not_expose_credentials(monkeypatch):
    import traceback
    monkeypatch.setenv('COUNCIL_PROXY_URL', 'http://user:secret@proxy:3128')
    def get(*args, **kwargs):
        raise module.requests.exceptions.ProxyError('http://user:secret@proxy:3128')
    monkeypatch.setattr(module.requests, 'get', get)
    with pytest.raises(module.requests.RequestException) as exc:
        module.fetch_committees_and_bodies(5756)
    assert 'secret' not in ''.join(traceback.format_exception(exc.type, exc.value, exc.tb))
