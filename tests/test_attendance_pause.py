"""Fail-closed fallback while a primary Council attendance contract is unverified."""
from pathlib import Path
import shutil
import subprocess
import sys

import pytest
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts import refresh_councillors as refresh


def test_paused_refresh_preserves_data_and_replaces_stale_summary(tmp_path, monkeypatch):
    data = tmp_path / "councillors.yaml"
    original = (ROOT / "data/councillors.yaml").read_bytes()
    data.write_bytes(original)
    summary = tmp_path / "summary.md"
    summary.write_text("Previous successful refresh")
    monkeypatch.setattr(refresh, "SUMMARY_PATH", summary)
    monkeypatch.setattr(refresh.requests, "get", lambda *a, **kw: pytest.fail("No network during pause"))
    with pytest.raises(RuntimeError, match="Attendance refresh paused"):
        refresh.refresh(data)
    assert data.read_bytes() == original
    report = summary.read_text()
    assert "Previous successful refresh" not in report
    assert "No councillor data was updated" in report
    assert "not current" in report
    assert "CPW" in report
    assert "Council" in report


@pytest.mark.parametrize("failure", ["cpw_403", "council_404", "council_challenge"])
def test_retained_refresh_preserves_data_on_source_failure(tmp_path, monkeypatch, failure):
    """Offline reproduction of transport and HTTP-200 challenge failures."""
    data = tmp_path / "councillors.yaml"
    original = (ROOT / "data/councillors.yaml").read_bytes()
    data.write_bytes(original)
    monkeypatch.setattr(refresh, "ATTENDANCE_REFRESH_PAUSED", False)
    monkeypatch.setattr(refresh.time, "sleep", lambda seconds: None)
    monkeypatch.delenv("COUNCIL_PROXY_URL", raising=False)

    def response(url, **kwargs):
        result = refresh.requests.Response()
        result.url = url
        if "cornwallpoliticalwatch.com" in url:
            result.status_code = 403
            result._content = b"Forbidden"
        elif failure == "council_404":
            result.status_code = 404
            result._content = b"Not found"
        elif failure == "council_challenge":
            result.status_code = 200
            result._content = b"<html>User validation required: CAPTCHA</html>"
        else:
            result.status_code = 200
            result._content = (ROOT / "tests/fixtures/cornwall_member_5756_userinfo.html").read_bytes()
        return result

    monkeypatch.setattr(refresh.requests, "get", response)
    with pytest.raises(RuntimeError, match="all 3 active councillors failed"):
        refresh.refresh(data)
    assert data.read_bytes() == original


def test_public_page_does_not_present_retained_percentages_as_current(tmp_path):
    # Render the production partial with real data using a minimal Hugo shell.
    # Full-site verification additionally needs the CI Hugo/Tailwind toolchain.
    assert '{{ partial "attendance-status.html" . }}' in (
        ROOT / "layouts/councillors/list.html"
    ).read_text()
    source = tmp_path / "source"
    (source / "layouts/partials").mkdir(parents=True)
    (source / "hugo.toml").write_text('baseURL = "https://example.test/"\n')
    (source / "layouts/index.html").write_text(
        '<html><body>{{ range .Site.Data.councillors }}'
        '{{ partial "attendance-status.html" . }}{{ end }}</body></html>'
    )
    shutil.copyfile(ROOT / "layouts/partials/attendance-status.html",
                    source / "layouts/partials/attendance-status.html")
    shutil.copytree(ROOT / "data", source / "data")
    result = subprocess.run(
        ["hugo", "--source", str(source), "--destination", str(tmp_path / "site"),
         "--environment", "production"],
        cwd=ROOT, text=True, capture_output=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    html = (tmp_path / "site/index.html").read_text()
    text = BeautifulSoup(html, "html.parser").get_text(" ", strip=True)
    assert text.count("Attendance temporarily unavailable") == 3
    assert "% attendance" not in text
    assert "Council records for the current term" in text
