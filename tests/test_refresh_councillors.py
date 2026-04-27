"""Offline tests for scripts/refresh_councillors.py.

Uses captured HTML fixtures under tests/fixtures/ — no network required.
Run via: pytest tests/test_refresh_councillors.py -q
"""

from __future__ import annotations

import io
import sys
from pathlib import Path

import pytest
from ruamel.yaml import YAML

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.refresh_councillors import (  # noqa: E402
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


def test_round_trip_preserves_anna_no_outside_bodies_key():
    """Anna's entry has NO `outside_bodies` key on disk. The round-trip must
    not introduce one (otherwise the policy in refresh() — 'leave entry
    unchanged when key missing AND council returns no bodies' — would break
    on first run)."""
    yaml = _make_yaml()
    data = yaml.load(DATA_PATH.read_text(encoding="utf-8"))
    anna = next(e for e in data if e["name"] == "Anna Thomason-Kenyon")
    assert "outside_bodies" not in anna, (
        "Anna's entry must not have an outside_bodies key on disk — "
        "the refresh policy depends on it"
    )


def test_uid_constants_match_data_yaml():
    """Every active councillor in YAML must have a UID mapping."""
    yaml = YAML(typ="safe")
    data = yaml.load(DATA_PATH.read_text(encoding="utf-8"))
    active_names = {entry["name"] for entry in data if entry.get("active") is True}
    missing = active_names - set(UIDS_BY_NAME.keys())
    assert not missing, f"Active councillors without UID mapping: {missing}"


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


# ---------- Attendance parsing ----------

def test_parse_attendance_5756_rowland():
    html = (FIXTURES / "cornwall_member_5756_attendance.html").read_text(encoding="utf-8")
    pct = parse_attendance_percentage(html, 5756)
    assert isinstance(pct, int)
    assert 0 <= pct <= 100


def test_parse_attendance_6345_karen():
    """Closes RESEARCH Open Question #4 — Karen's page wasn't directly probed in research."""
    html = (FIXTURES / "cornwall_member_6345_attendance.html").read_text(encoding="utf-8")
    pct = parse_attendance_percentage(html, 6345)
    assert isinstance(pct, int)
    assert 0 <= pct <= 100


# ---------- Fail-loud contract (D-09) ----------

def test_fail_loud_on_missing_committees_section():
    html = "<html><body><h1>Some other page</h1></body></html>"
    with pytest.raises(RuntimeError, match="no current committees"):
        parse_committees_and_bodies(html, 9999)


def test_fail_loud_on_missing_attendance_row():
    html = "<html><body><table><tr><td>Other row</td></tr></table></body></html>"
    with pytest.raises(RuntimeError, match="not found"):
        parse_attendance_percentage(html, 9999)
