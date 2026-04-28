#!/usr/bin/env python3
"""Weekly refresh of councillor data.

Hybrid sources (cing-938, 2026-04-28):

  - **Attendance %** comes from Cornwall Political Watch
    (`cornwallpoliticalwatch.com/councillors/{slug}`). CPW reports the
    all-time aggregate ("X% overall attendance"), which is what the YAML
    represents and what the public site shows. The Cornwall Council
    `mgAttendance.aspx` page only reports a rolling ~6-month window
    (5/8 = 62% for Rowland on 03/11/2025–28/04/2026 at the time of
    cing-938) — the wrong figure for a long-term scorecard.

  - **Committees + outside bodies** come from Cornwall Council
    `mgUserInfo.aspx?UID={uid}`. CPW's per-committee table is
    "meetings attended", which includes meetings the councillor
    attended as an observer (e.g. Cabinet) — not their official
    memberships. The council page is the source-of-truth for memberships,
    with expired-membership filtering already in place.

  - "Cornwall Council" itself, listed as a committee on the council page
    headline body, is filtered out — it's not a meaningful "committee".

PRD §6 ("Use CPW data directly on the CING site") motivated this hybrid:
DATA-03's original plan put council site as source-of-truth for everything,
which was correct for memberships but wrong for the displayed attendance
figure. PR #22 (first cron run) made the divergence visible.

Reads `data/councillors.yaml` and writes back ONLY the three refreshable
fields (attendance, committees, outside_bodies). All other fields are
preserved verbatim via a ruamel.yaml round-trip that also keeps comments,
quoting, and key order intact.

Cron schedule: weekly Monday 06:00 UTC
(see .github/workflows/refresh-councillors.yml).

Failure mode: fail loud (D-09). Any parser miss raises RuntimeError → script
exits non-zero → GitHub Actions emails the workflow author.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import List, Tuple

import requests
from bs4 import BeautifulSoup
from ruamel.yaml import YAML

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "councillors.yaml"

# ---------- Cornwall Council UIDs (one-time bootstrap, D-13) ----------
# Verified against democracy.cornwall.gov.uk/mgMemberIndex.aspx 2026-04-26.
# Used for committees + outside bodies (mgUserInfo.aspx?UID=...).
UIDS_BY_NAME = {
    "Rowland O'Connor": 5756,
    "Anna Thomason-Kenyon": 6351,
    "Karen Knight": 6345,
}

# ---------- Cornwall Political Watch slugs (cing-938, 2026-04-28) ----------
# Used for attendance % (cornwallpoliticalwatch.com/councillors/{slug}).
# CPW URLs verified 2026-04-28.
CPW_SLUGS_BY_NAME = {
    "Rowland O'Connor": "rowland-oconnor",
    "Anna Thomason-Kenyon": "anna-thomason-kenyon",
    "Karen Knight": "karen-knight",
}

# Committee names filtered from the council-page committees list.
# "Cornwall Council" is the headline body each councillor sits on; it appears
# in the council's own committee-appointments markup but isn't a "committee"
# in the colloquial sense the YAML represents.
_COMMITTEE_FILTER = {"Cornwall Council"}

UA = "CING refresh-bot (+https://www.cingparty.uk/) requests/python"
HEADERS = {"User-Agent": UA}
TIMEOUT = 30  # seconds

# Class marker on <li> elements representing expired memberships. Cornwall
# Council renders both current and expired entries in the same <ul>, hiding
# expired ones via `class="mgExpiredMembershipEntryC"` (or ...EntryE for
# outside bodies) + inline `display: none`. The "Current appointments"
# button is a CSS toggle — there's no separate <h3> section. We must filter
# expired entries server-side or we'd ship stale roles in the YAML.
_EXPIRED_CLASS_RE = re.compile(r"\bmgExpiredMembershipEntry[A-Z]?\b")


# ---------- HTML parsing helpers ----------

def _find_current_appointments_ul(soup: BeautifulSoup, heading_text: str):
    """Find the <h2> matching `heading_text`, then return the next
    <ul class="mgBulletList"> sibling-or-descendant before any later <h2>.

    Cornwall Council's mgUserInfo page structure (verified 2026-04-27):

        <h2 class="mgSectionTitle">Committee appointments</h2>
        <button class="mgCommitteeCurrentAppointments" ...>Current appointments</button>
        <button class="mgCommitteeAllAppointments"     ...>All appointments</button>
        <ul class="mgBulletList">
            <li>...current entry...</li>
            <li class="mgExpiredMembershipEntryC" style="display: none;">...expired...</li>
            ...
        </ul>
        <h2 class="mgSectionTitle">Appointments to outside bodies</h2>

    There is NO <h3>Current appointments</h3> — the section toggle is a
    JavaScript-driven CSS class on the <li>s themselves. So "current
    appointments" = mgBulletList <li>s WITHOUT mgExpiredMembershipEntry*.
    """
    h2 = soup.find(
        "h2", string=re.compile(rf"^\s*{re.escape(heading_text)}\s*$")
    )
    if h2 is None:
        return None
    cursor = h2
    while True:
        cursor = cursor.find_next(["h2", "ul"])
        if cursor is None:
            return None
        if cursor.name == "h2":
            return None
        # cursor.name == "ul"
        classes = cursor.get("class") or []
        if "mgBulletList" in classes:
            return cursor
        # Some other <ul> — keep scanning.


def _extract_appointment_names(ul) -> List[str]:
    """Extract clean appointment names from a mgBulletList <ul>.

    - Skips <li>s whose class marks them as expired memberships.
    - Uses the inner <a> text (committee name) rather than the whole <li>
      text, because the <li> trailing text contains role suffixes and date
      ranges (e.g. ` (Substitutes)<strong> (02/06/2025 - 09/10/2025)</strong>`).
    - Strips a single parenthetical suffix from the <a> text in case the
      role marker is appended inside the <a> on some pages (defensive —
      observed Cornwall pages keep them outside the <a>, but the inline
      test in test_parse_committees_strips_role_suffix relies on this).
    - Deduplicates while preserving first-seen order (a single committee
      can occasionally appear twice if there's both a substantive seat and
      a substitute seat among current memberships).
    """
    if ul is None:
        return []
    seen: set = set()
    items: List[str] = []
    for li in ul.find_all("li", recursive=False):
        li_classes = " ".join(li.get("class") or [])
        if _EXPIRED_CLASS_RE.search(li_classes):
            continue
        a = li.find("a")
        text = (a.get_text() if a else li.get_text()).strip()
        text = re.sub(r"\s*\([^)]*\)\s*$", "", text).strip()
        if not text or text in seen:
            continue
        seen.add(text)
        items.append(text)
    return items


def parse_committees_and_bodies(html: str, uid: int) -> Tuple[List[str], List[str]]:
    """Pure-function parser — accepts raw HTML. Used by cron AND fixture tests.

    Filters _COMMITTEE_FILTER (currently {"Cornwall Council"}) from the
    committees list — these are headline-body entries on the council site
    that aren't meaningful committee memberships. Outside bodies are NOT
    filtered.
    """
    soup = BeautifulSoup(html, "html.parser")
    committees_raw = _extract_appointment_names(
        _find_current_appointments_ul(soup, "Committee appointments")
    )
    committees = [c for c in committees_raw if c not in _COMMITTEE_FILTER]
    outside_bodies = _extract_appointment_names(
        _find_current_appointments_ul(soup, "Appointments to outside bodies")
    )
    if not committees:
        raise RuntimeError(
            f"UID={uid}: no current committees found — page structure may have changed"
        )
    return committees, outside_bodies


# CPW renders the headline attendance via React: a span carrying the integer
# percentage, immediately followed by an empty React comment node, then the
# `%` literal, then a sibling span carrying the label. Concrete shape:
#
#   <span class="... tabular-nums text-...">91<!-- -->%</span>
#   <span class="text-sm text-muted">overall attendance</span>
#
# We anchor on the literal "overall attendance" label (stable user-facing
# text) and look back to the preceding "<int><!-- -->%</span>" for the value.
_CPW_ATTENDANCE_RE = re.compile(
    r'<span[^>]*>(\d+)<!--\s*-->%</span>\s*<span[^>]*>overall attendance</span>'
)


def parse_attendance_percentage(html: str, slug: str) -> int:
    """Pure-function parser for the all-time attendance % from a CPW page."""
    m = _CPW_ATTENDANCE_RE.search(html)
    if m is None:
        raise RuntimeError(
            f"slug={slug}: 'overall attendance' span not found in CPW page — "
            "page structure may have changed"
        )
    return int(m.group(1))


# ---------- HTTP fetch wrappers ----------

def fetch_committees_and_bodies(uid: int) -> Tuple[List[str], List[str]]:
    url = f"https://democracy.cornwall.gov.uk/mgUserInfo.aspx?UID={uid}"
    resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    resp.raise_for_status()
    return parse_committees_and_bodies(resp.text, uid)


def fetch_attendance_percentage(slug: str) -> int:
    url = f"https://cornwallpoliticalwatch.com/councillors/{slug}"
    resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    resp.raise_for_status()
    return parse_attendance_percentage(resp.text, slug)


# ---------- Round-trip refresh ----------

SUMMARY_PATH = ROOT / ".refresh-summary.md"


def _summarise_list(items):
    """Render a YAML list as a compact comma-separated string for the diff table."""
    if not items:
        return "_(none)_"
    return ", ".join(items)


def write_summary(rows, summary_path: Path = SUMMARY_PATH) -> None:
    """Emit a markdown summary table consumed by peter-evans/create-pull-request
    via `body-path: .refresh-summary.md` (D-08).

    `rows` is a list of dicts with keys:
      name, attendance_before, attendance_after,
      committees_before, committees_after,
      outside_bodies_before, outside_bodies_after
    """
    lines = [
        "Automated weekly refresh of councillor data.",
        "",
        "**Scope of refresh:** `attendance`, `committees`, `outside_bodies`.",
        "**Sources** (cing-938 hybrid):",
        "- attendance % from `cornwallpoliticalwatch.com/councillors/{slug}` (all-time aggregate)",
        "- committees + outside bodies from `democracy.cornwall.gov.uk/mgUserInfo.aspx?UID={uid}` (official memberships, expired-filtered)",
        "",
        "### Per-councillor diff",
        "",
        "| Councillor | Attendance (before → after) | Committees (before → after) | Outside bodies (before → after) |",
        "|------------|------------------------------|------------------------------|---------------------------------|",
    ]
    for r in rows:
        att = (
            f"{r['attendance_before']}% → **{r['attendance_after']}%**"
            if r["attendance_before"] != r["attendance_after"]
            else f"{r['attendance_after']}% _(unchanged)_"
        )
        com_b = _summarise_list(r["committees_before"])
        com_a = _summarise_list(r["committees_after"])
        com = (
            f"{com_b}<br>↓<br>**{com_a}**"
            if r["committees_before"] != r["committees_after"]
            else f"{com_a} _(unchanged)_"
        )
        ob_b = _summarise_list(r["outside_bodies_before"])
        ob_a = _summarise_list(r["outside_bodies_after"])
        ob = (
            f"{ob_b}<br>↓<br>**{ob_a}**"
            if r["outside_bodies_before"] != r["outside_bodies_after"]
            else f"{ob_a} _(unchanged)_"
        )
        lines.append(f"| {r['name']} | {att} | {com} | {ob} |")
    lines += [
        "",
        "### How to review",
        "1. Read the diff in `data/councillors.yaml`.",
        "2. For any unexpected attendance change, open `cornwallpoliticalwatch.com/councillors/{slug}` and confirm CPW agrees.",
        "3. For any unexpected committee or outside-body change, open `democracy.cornwall.gov.uk/mgUserInfo.aspx?UID={uid}` and confirm the council site agrees.",
        "4. If the diff matches both sources, approve and merge.",
        "5. If the diff is wrong (e.g. CPW reporting lag, or HTML structure changed on either site), close the PR; either wait for next week or investigate `scripts/refresh_councillors.py`.",
        "",
        "**No auto-merge** — public political site, regression visibility matters.",
    ]
    summary_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {summary_path.relative_to(ROOT)}")


def refresh(data_path: Path = DATA_PATH) -> None:
    """Read councillors.yaml, refresh attendance/committees/outside_bodies for
    each active councillor, write back, and emit `.refresh-summary.md` with a
    per-councillor before/after markdown table (consumed by the cron PR body
    via `body-path` — D-08). Preserves all other fields, comments, and key
    order via ruamel.yaml typ="rt".
    """
    yaml = YAML(typ="rt")
    yaml.preserve_quotes = True
    yaml.indent(mapping=2, sequence=4, offset=2)
    # Disable line wrapping — bio strings would otherwise be wrapped at 80 cols
    # on first run, producing a noisy diff that obscures the actual data
    # changes. With width=4096 the round-trip becomes idempotent (verified by
    # tests/test_refresh_councillors.py::test_round_trip_is_idempotent).
    yaml.width = 4096

    with data_path.open("r", encoding="utf-8") as f:
        data = yaml.load(f)

    summary_rows = []
    for entry in data:
        if entry.get("active") is not True:
            continue
        name = entry["name"]
        if name not in UIDS_BY_NAME:
            raise RuntimeError(
                f"councillors.yaml entry '{name}' has no UID mapping in "
                "UIDS_BY_NAME — add it before enabling refresh for this councillor"
            )
        if name not in CPW_SLUGS_BY_NAME:
            raise RuntimeError(
                f"councillors.yaml entry '{name}' has no CPW slug mapping in "
                "CPW_SLUGS_BY_NAME — add it before enabling refresh for this councillor"
            )
        uid = UIDS_BY_NAME[name]
        cpw_slug = CPW_SLUGS_BY_NAME[name]

        # Capture BEFORE state for the diff table.
        attendance_before = entry.get("attendance")
        committees_before = list(entry.get("committees") or [])
        outside_bodies_before = list(entry.get("outside_bodies") or [])

        # Hybrid sources (cing-938): committees + outside bodies from
        # council mgUserInfo (official memberships); attendance % from
        # CPW (all-time aggregate, what the public site shows).
        committees, outside_bodies = fetch_committees_and_bodies(uid)
        attendance = fetch_attendance_percentage(cpw_slug)

        entry["attendance"] = attendance
        entry["committees"] = committees

        # Outside-bodies policy:
        #   - council returned bodies → write them
        #   - council returned no bodies AND key already exists → write empty list
        #   - council returned no bodies AND key missing → leave entry unchanged
        if outside_bodies:
            entry["outside_bodies"] = outside_bodies
        elif "outside_bodies" in entry:
            entry["outside_bodies"] = []
        # else: do nothing — preserves Anna's no-key shape

        summary_rows.append({
            "name": name,
            "attendance_before": attendance_before,
            "attendance_after": attendance,
            "committees_before": committees_before,
            "committees_after": committees,
            "outside_bodies_before": outside_bodies_before,
            "outside_bodies_after": outside_bodies,
        })

        print(
            f"  refreshed {name} (UID={uid}): attendance={attendance}%, "
            f"{len(committees)} committees, {len(outside_bodies)} outside_bodies"
        )

    with data_path.open("w", encoding="utf-8") as f:
        yaml.dump(data, f)
    print(f"wrote {data_path.relative_to(ROOT)}")

    write_summary(summary_rows)


if __name__ == "__main__":
    refresh()
