#!/usr/bin/env python3
"""Weekly refresh of councillor data from Cornwall Council member pages.

Reads `data/councillors.yaml`, scrapes the official mgUserInfo + mgAttendance
pages on `democracy.cornwall.gov.uk` for each active councillor, and writes
back ONLY the three refreshable fields (attendance, committees,
outside_bodies). All other fields are preserved verbatim via a ruamel.yaml
round-trip that also keeps comments, quoting, and key order intact.

Phase 4 DATA-03. Cron schedule: weekly Monday 06:00 UTC (see
.github/workflows/refresh-councillors.yml).

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
UIDS_BY_NAME = {
    "Rowland O'Connor": 5756,
    "Anna Thomason-Kenyon": 6351,
    "Karen Knight": 6345,
}

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
    """Pure-function parser — accepts raw HTML. Used by cron AND fixture tests."""
    soup = BeautifulSoup(html, "html.parser")
    committees = _extract_appointment_names(
        _find_current_appointments_ul(soup, "Committee appointments")
    )
    outside_bodies = _extract_appointment_names(
        _find_current_appointments_ul(soup, "Appointments to outside bodies")
    )
    if not committees:
        raise RuntimeError(
            f"UID={uid}: no current committees found — page structure may have changed"
        )
    return committees, outside_bodies


def parse_attendance_percentage(html: str, uid: int) -> int:
    """Pure-function parser for attendance %."""
    soup = BeautifulSoup(html, "html.parser")
    for tr in soup.find_all("tr"):
        cells = [td.get_text(strip=True) for td in tr.find_all(["td", "th"])]
        if not cells:
            continue
        if "Present as expected" in cells[0]:
            for cell in cells:
                m = re.search(r"(\d+)\s*%", cell)
                if m:
                    return int(m.group(1))
    raise RuntimeError(
        f"UID={uid}: 'Present as expected' attendance row not found — "
        "page structure may have changed"
    )


# ---------- HTTP fetch wrappers ----------

def fetch_committees_and_bodies(uid: int) -> Tuple[List[str], List[str]]:
    url = f"https://democracy.cornwall.gov.uk/mgUserInfo.aspx?UID={uid}"
    resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    resp.raise_for_status()
    return parse_committees_and_bodies(resp.text, uid)


def fetch_attendance_percentage(uid: int) -> int:
    url = f"https://democracy.cornwall.gov.uk/mgAttendance.aspx?UID={uid}"
    resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    resp.raise_for_status()
    return parse_attendance_percentage(resp.text, uid)


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
        "Automated weekly refresh from Cornwall Council member pages.",
        "",
        "**Scope of refresh:** `attendance`, `committees`, `outside_bodies`.",
        "**Source:** democracy.cornwall.gov.uk/{mgUserInfo,mgAttendance}.aspx",
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
        "2. For any unexpected change, open the councillor's mgUserInfo / mgAttendance page and confirm the council site agrees.",
        "3. If the diff matches council source, approve and merge — D-10 (\"council source is truth\") permits acceptance once verified.",
        "4. If the diff is wrong (e.g. council page reporting lag, or HTML structure changed), close the PR; either wait for next week or investigate `scripts/refresh_councillors.py`.",
        "",
        "**No auto-merge** — public political site, regression visibility matters (CONTEXT D-10).",
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
        uid = UIDS_BY_NAME[name]

        # Capture BEFORE state for the diff table.
        attendance_before = entry.get("attendance")
        committees_before = list(entry.get("committees") or [])
        outside_bodies_before = list(entry.get("outside_bodies") or [])

        committees, outside_bodies = fetch_committees_and_bodies(uid)
        attendance = fetch_attendance_percentage(uid)

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
