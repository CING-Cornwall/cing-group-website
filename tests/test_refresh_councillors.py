"""Offline tests for scripts/refresh_councillors.py.

Uses captured HTML fixtures under tests/fixtures/ — no network required.
Run via: pytest tests/test_refresh_councillors.py -q
"""

from __future__ import annotations

import io
import sys
import time
from pathlib import Path

import pytest
from ruamel.yaml import YAML

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import scripts.refresh_councillors as refresh_module  # noqa: E402
from scripts.refresh_councillors import (  # noqa: E402
    CPW_SLUGS_BY_NAME,
    UIDS_BY_NAME,
    parse_attendance_percentage,
    parse_committees_and_bodies,
)

FIXTURES = ROOT / "tests" / "fixtures"
DATA_PATH = ROOT / "data" / "councillors.yaml"

NON_REFRESHABLE_KEYS = ("name", "role", "division", "photo", "email", "bio", "active")


def _make_yaml():
    yaml = YAML(typ="rt")
    yaml.preserve_quotes = True
    yaml.indent(mapping=2, sequence=4, offset=2)
    yaml.width = 4096
    return yaml


# ---------- Round-trip integrity ----------

def test_round_trip_is_idempotent():
    """ruamel round-trip must be a fixed point: load + dump + load + dump
    produces a byte-identical second pass.

    NOTE: The on-disk councillors.yaml uses an inconsistent block-sequence
    style (top-level dashes at column 0, nested dashes at column 4) that
    cannot be reproduced byte-for-byte by any single ruamel `indent(...)`
    setting. The first cron run normalises formatting; the operator reviews
    that as part of the bootstrap PR (Task 5). What we *can* and DO
    guarantee is that subsequent runs are stable — no formatting churn on
    runs that don't change refreshable values. This test enforces that
    stability.
    """
    yaml = _make_yaml()

    orig_text = DATA_PATH.read_text(encoding="utf-8")
    data = yaml.load(io.StringIO(orig_text))

    buf1 = io.StringIO()
    yaml.dump(data, buf1)
    once = buf1.getvalue()

    data2 = yaml.load(io.StringIO(once))
    buf2 = io.StringIO()
    yaml.dump(data2, buf2)
    twice = buf2.getvalue()

    assert once == twice, (
        "ruamel round-trip is not idempotent — running the cron twice in a "
        "row would produce churn. This breaks the silent-success contract "
        "(D-08: no PR if no diff)."
    )


def test_round_trip_preserves_non_refreshable_fields():
    """The truths invariant: name, role, division, photo, email, bio, active
    survive a load → dump cycle byte-identical at the field-value level.
    Whitespace/formatting may shift on the first run; field VALUES must not.
    """
    yaml = _make_yaml()

    orig = yaml.load(DATA_PATH.read_text(encoding="utf-8"))
    buf = io.StringIO()
    yaml.dump(orig, buf)
    round_tripped = yaml.load(io.StringIO(buf.getvalue()))

    assert len(orig) == len(round_tripped)
    for src, dst in zip(orig, round_tripped):
        for key in NON_REFRESHABLE_KEYS:
            if key in src:
                assert key in dst, f"{src['name']}: lost key {key} on round-trip"
                assert src[key] == dst[key], (
                    f"{src['name']}: {key} value drifted on round-trip "
                    f"(src={src[key]!r}, dst={dst[key]!r})"
                )
            else:
                assert key not in dst, (
                    f"{src['name']}: spurious key {key} introduced on round-trip"
                )


def test_round_trip_preserves_karen_todo_comment():
    """ruamel `typ='rt'` must preserve the `# TODO(IMG-04-stage-2)` comment
    above Karen's entry. Comments are part of the contract — they're how
    deferred work stays visible in the YAML."""
    yaml = _make_yaml()
    orig = yaml.load(DATA_PATH.read_text(encoding="utf-8"))
    buf = io.StringIO()
    yaml.dump(orig, buf)
    assert "TODO(IMG-04-stage-2)" in buf.getvalue(), (
        "Karen's IMG-04-stage-2 TODO comment was lost on ruamel round-trip"
    )


def test_round_trip_preserves_current_outside_body_assignments():
    """Round-trip must retain the current generated outside-body ownership."""
    yaml = _make_yaml()
    data = yaml.load(DATA_PATH.read_text(encoding="utf-8"))
    anna = next(e for e in data if e["name"] == "Anna Thomason-Kenyon")
    karen = next(e for e in data if e["name"] == "Karen Knight")
    assert anna["outside_bodies"] == ["Fifth Nation Members’ Working Group"]
    assert "outside_bodies" not in karen


def test_uid_constants_match_data_yaml():
    """Every active councillor in YAML must have a UID mapping."""
    yaml = YAML(typ="safe")
    data = yaml.load(DATA_PATH.read_text(encoding="utf-8"))
    active_names = {entry["name"] for entry in data if entry.get("active") is True}
    missing = active_names - set(UIDS_BY_NAME.keys())
    assert not missing, f"Active councillors without UID mapping: {missing}"


def test_cpw_slug_constants_match_data_yaml():
    """Every active councillor in YAML must have a CPW slug mapping (cing-938)."""
    yaml = YAML(typ="safe")
    data = yaml.load(DATA_PATH.read_text(encoding="utf-8"))
    active_names = {entry["name"] for entry in data if entry.get("active") is True}
    missing = active_names - set(CPW_SLUGS_BY_NAME.keys())
    assert not missing, f"Active councillors without CPW slug mapping: {missing}"


# ---------- Committee/body parsing ----------

def test_parse_committees_5756_rowland():
    """Rowland's fixture must yield non-empty committees including
    'Standards Committee' (verified-current as of 2026-04-27 fixture
    capture). NOTE: 'Audit Committee' is currently expired on Rowland's
    page — the parser must filter that out via mgExpiredMembershipEntryC."""
    html = (FIXTURES / "cornwall_member_5756_userinfo.html").read_text(encoding="utf-8")
    committees, _ = parse_committees_and_bodies(html, 5756)
    assert committees, "Rowland's fixture must yield non-empty committee list"
    assert any("Standards Committee" in c for c in committees), (
        f"Expected 'Standards Committee' in Rowland's current committees; got {committees!r}"
    )


def test_parse_committees_5756_excludes_expired():
    """Expired memberships must be filtered. 'Audit Committee' is expired
    on Rowland's page (mgExpiredMembershipEntryC). The parser must NOT
    return it in current committees, otherwise stale roles ship to the
    public site."""
    html = (FIXTURES / "cornwall_member_5756_userinfo.html").read_text(encoding="utf-8")
    committees, _ = parse_committees_and_bodies(html, 5756)
    assert not any(c == "Audit Committee" for c in committees), (
        f"'Audit Committee' is expired on Rowland's page and must not be returned; "
        f"got {committees!r}"
    )


def test_parse_committees_strips_role_suffix():
    """Selector helper must strip '(Vice-Chair)', '(Substitutes)', etc.
    when the role marker appears inside the <a> text."""
    html = """
    <html><body>
      <h2>Committee appointments</h2>
      <ul class="mgBulletList">
        <li><a href="x">Audit Committee (Vice-Chair)</a></li>
        <li><a href="y">Standards Committee (Substitutes)</a></li>
        <li><a href="z">Plain Committee</a></li>
      </ul>
    </body></html>
    """
    committees, _ = parse_committees_and_bodies(html, 0)
    assert committees == ["Audit Committee", "Standards Committee", "Plain Committee"], committees


def test_parse_committees_filters_cornwall_council():
    """The headline 'Cornwall Council' entry on a councillor's mgUserInfo
    page is filtered from the committees list (cing-938). It's not a
    meaningful 'committee' — it's the body each councillor sits on, which
    appears in the council site's committee-appointments markup but isn't
    what the YAML's `committees` field is meant to represent."""
    html = """
    <html><body>
      <h2>Committee appointments</h2>
      <ul class="mgBulletList">
        <li><a href="x">Audit Committee</a></li>
        <li><a href="y">Cornwall Council</a></li>
        <li><a href="z">Standards Committee</a></li>
      </ul>
    </body></html>
    """
    committees, _ = parse_committees_and_bodies(html, 0)
    assert "Cornwall Council" not in committees, (
        f"'Cornwall Council' must be filtered from committees; got {committees!r}"
    )
    assert committees == ["Audit Committee", "Standards Committee"], committees


def test_parse_anna_outside_bodies_handling():
    """Anna's fixture has NO 'Appointments to outside bodies' section
    (verified 2026-04-27). The parser must return an empty list (not
    raise), so the refresh policy can preserve her no-key YAML shape."""
    html = (FIXTURES / "cornwall_member_6351_userinfo.html").read_text(encoding="utf-8")
    committees, outside_bodies = parse_committees_and_bodies(html, 6351)
    assert committees, "Anna must have at least one current committee"
    assert isinstance(outside_bodies, list)
    assert outside_bodies == [], (
        f"Anna's fixture has no outside-bodies section; expected []; got {outside_bodies!r}"
    )


# ---------- Attendance parsing (CPW source — cing-938) ----------

def test_parse_attendance_rowland_cpw():
    """CPW shows 'X% overall attendance' for Rowland — must extract the
    integer headline figure, not a per-committee or rolling-window number."""
    html = (FIXTURES / "cpw_rowland_oconnor.html").read_text(encoding="utf-8")
    pct = parse_attendance_percentage(html, "rowland-oconnor")
    assert pct == 91, (
        f"Rowland's CPW headline shows 91% as of fixture capture (2026-04-28); "
        f"got {pct}"
    )


def test_parse_attendance_anna_cpw():
    html = (FIXTURES / "cpw_anna_thomason_kenyon.html").read_text(encoding="utf-8")
    pct = parse_attendance_percentage(html, "anna-thomason-kenyon")
    assert pct == 95, f"Anna's CPW headline shows 95% as of fixture capture; got {pct}"


def test_parse_attendance_karen_cpw():
    html = (FIXTURES / "cpw_karen_knight.html").read_text(encoding="utf-8")
    pct = parse_attendance_percentage(html, "karen-knight")
    assert pct == 89, f"Karen's CPW headline shows 89% as of fixture capture; got {pct}"


def test_parse_attendance_picks_overall_not_per_committee():
    """CPW pages contain BOTH the headline 'X% overall attendance' AND
    per-committee attendance rates (e.g. 'Audit Committee 3 2 67 %').
    The parser must anchor on the 'overall attendance' label, not the first
    percentage in the document, otherwise it would pick a per-committee
    rate which has no general meaning."""
    # Synthetic page with a per-committee 67% appearing FIRST in document
    # order, then the headline 91% later.
    html = """
    <html><body>
      <table><tr><td>Audit Committee</td><td>3</td><td>2</td><td>67%</td></tr></table>
      <span class="text-positive">91<!-- -->%</span><span class="text-muted">overall attendance</span>
    </body></html>
    """
    pct = parse_attendance_percentage(html, "synthetic")
    assert pct == 91, f"Parser must pick the 'overall attendance' value (91), not 67; got {pct}"


def test_parse_attendance_accepts_plain_percentage_without_react_comment():
    """CPW may server-render the headline without React's empty comment node."""
    html = (
        '<span class="text-positive">88%</span>'
        '<span class="text-muted">overall attendance</span>'
    )
    assert parse_attendance_percentage(html, "plain-render") == 88


class _StubResponse:
    def __init__(self, text):
        self.text = text

    def raise_for_status(self):
        return None


def test_fetch_attendance_retries_transient_parse_failure(monkeypatch):
    responses = iter([
        _StubResponse("<html><body>Temporary incomplete page</body></html>"),
        _StubResponse(
            '<span>91<!-- -->%</span><span>overall attendance</span>'
        ),
    ])
    calls = []
    sleeps = []

    def fake_get(url, *, headers, timeout):
        calls.append((url, headers, timeout))
        return next(responses)

    monkeypatch.setattr(refresh_module.requests, "get", fake_get)
    monkeypatch.setattr(time, "sleep", sleeps.append)

    assert refresh_module.fetch_attendance_percentage("rowland-oconnor") == 91
    assert len(calls) == 2
    assert all(call[1] == refresh_module.HEADERS for call in calls)
    assert all(call[2] == refresh_module.TIMEOUT for call in calls)
    assert sleeps == [1]


def test_fetch_attendance_retries_request_failure_three_times(monkeypatch):
    calls = []
    sleeps = []

    def fail_get(url, *, headers, timeout):
        calls.append((url, headers, timeout))
        raise refresh_module.requests.ConnectionError("temporary connection failure")

    monkeypatch.setattr(refresh_module.requests, "get", fail_get)
    monkeypatch.setattr(time, "sleep", sleeps.append)

    with pytest.raises(refresh_module.requests.ConnectionError):
        refresh_module.fetch_attendance_percentage("rowland-oconnor")

    assert len(calls) == 3
    assert sleeps == [1, 2]


# ---------- Fail-loud contract (D-09) ----------

def test_fail_loud_on_missing_committees_section():
    html = "<html><body><h1>Some other page</h1></body></html>"
    with pytest.raises(RuntimeError, match="no current committees"):
        parse_committees_and_bodies(html, 9999)


def test_fail_loud_on_missing_overall_attendance_span():
    """If CPW restructures the headline span (loses the 'overall attendance'
    label), the parser must raise rather than silently fall back to 0 or to
    a per-committee rate."""
    html = "<html><body><p>No CPW headline span here.</p></body></html>"
    with pytest.raises(RuntimeError, match="overall attendance"):
        parse_attendance_percentage(html, "missing-slug")


def _write_active_councillors(path):
    path.write_text(
        """\
- name: "Rowland O'Connor"
  active: true
  attendance: 10
  committees: [Old Rowland committee]
- name: "Anna Thomason-Kenyon"
  active: true
  attendance: 20
  committees: [Old Anna committee]
- name: "Karen Knight"
  active: true
  attendance: 30
  committees: [Old Karen committee]
""",
        encoding="utf-8",
    )


def test_refresh_continues_after_one_councillor_failure(tmp_path, monkeypatch, capsys):
    data_path = tmp_path / "councillors.yaml"
    _write_active_councillors(data_path)
    attendance_calls = []
    summary = {}

    monkeypatch.setattr(refresh_module, "ROOT", tmp_path)
    monkeypatch.setattr(
        refresh_module,
        "fetch_committees_and_bodies",
        lambda uid: ([f"Current committee {uid}"], []),
    )

    def fake_attendance(slug):
        attendance_calls.append(slug)
        if slug == "rowland-oconnor":
            raise RuntimeError("transient CPW page")
        return 88

    monkeypatch.setattr(refresh_module, "fetch_attendance_percentage", fake_attendance)

    def capture_summary(rows, failures=()):
        summary["rows"] = rows
        summary["failures"] = failures

    monkeypatch.setattr(refresh_module, "write_summary", capture_summary)

    refresh_module.refresh(data_path)

    data = YAML(typ="safe").load(data_path.read_text(encoding="utf-8"))
    by_name = {entry["name"]: entry for entry in data}
    assert by_name["Rowland O'Connor"]["attendance"] == 10
    assert by_name["Rowland O'Connor"]["committees"] == ["Old Rowland committee"]
    assert by_name["Anna Thomason-Kenyon"]["attendance"] == 88
    assert by_name["Karen Knight"]["attendance"] == 88
    assert attendance_calls == [
        "rowland-oconnor",
        "anna-thomason-kenyon",
        "karen-knight",
    ]
    assert [row["name"] for row in summary["rows"]] == [
        "Anna Thomason-Kenyon",
        "Karen Knight",
    ]
    assert [name for name, _ in summary["failures"]] == ["Rowland O'Connor"]
    assert "Rowland O'Connor" in capsys.readouterr().err


def test_refresh_continues_after_council_request_failure(tmp_path, monkeypatch):
    data_path = tmp_path / "councillors.yaml"
    _write_active_councillors(data_path)
    summary = {}

    monkeypatch.setattr(refresh_module, "ROOT", tmp_path)

    def fake_committees(uid):
        if uid == UIDS_BY_NAME["Rowland O'Connor"]:
            raise refresh_module.requests.ConnectionError("temporary council failure")
        return [f"Current committee {uid}"], []

    def capture_summary(rows, failures=()):
        summary["rows"] = rows
        summary["failures"] = failures

    monkeypatch.setattr(refresh_module, "fetch_committees_and_bodies", fake_committees)
    monkeypatch.setattr(refresh_module, "fetch_attendance_percentage", lambda slug: 88)
    monkeypatch.setattr(refresh_module, "write_summary", capture_summary)

    refresh_module.refresh(data_path)

    data = YAML(typ="safe").load(data_path.read_text(encoding="utf-8"))
    by_name = {entry["name"]: entry for entry in data}
    assert by_name["Rowland O'Connor"]["attendance"] == 10
    assert by_name["Anna Thomason-Kenyon"]["attendance"] == 88
    assert by_name["Karen Knight"]["attendance"] == 88
    assert [row["name"] for row in summary["rows"]] == [
        "Anna Thomason-Kenyon",
        "Karen Knight",
    ]
    assert [name for name, _ in summary["failures"]] == ["Rowland O'Connor"]


def test_refresh_fails_without_writing_when_all_councillors_fail(tmp_path, monkeypatch):
    data_path = tmp_path / "councillors.yaml"
    _write_active_councillors(data_path)
    original = data_path.read_bytes()
    attendance_calls = []

    monkeypatch.setattr(refresh_module, "ROOT", tmp_path)
    monkeypatch.setattr(
        refresh_module,
        "fetch_committees_and_bodies",
        lambda uid: ([f"Current committee {uid}"], []),
    )

    def fail_attendance(slug):
        attendance_calls.append(slug)
        raise RuntimeError("transient CPW page")

    monkeypatch.setattr(refresh_module, "fetch_attendance_percentage", fail_attendance)
    monkeypatch.setattr(
        refresh_module,
        "write_summary",
        lambda rows, failures=(): pytest.fail(
            "summary must not be written when all councillors fail"
        ),
    )

    with pytest.raises(RuntimeError, match="all 3 active councillors failed"):
        refresh_module.refresh(data_path)

    assert attendance_calls == [
        "rowland-oconnor",
        "anna-thomason-kenyon",
        "karen-knight",
    ]
    assert data_path.read_bytes() == original


def test_write_summary_surfaces_partial_refresh_failure(tmp_path, monkeypatch):
    summary_path = tmp_path / "summary.md"
    monkeypatch.setattr(refresh_module, "ROOT", tmp_path)

    refresh_module.write_summary(
        [],
        summary_path=summary_path,
        failures=[("Rowland O'Connor", RuntimeError("transient CPW page"))],
    )

    summary = summary_path.read_text(encoding="utf-8")
    assert "### Refresh warnings" in summary
    assert "**Rowland O'Connor** was not updated: transient CPW page" in summary
