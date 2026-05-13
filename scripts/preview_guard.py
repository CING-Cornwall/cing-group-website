#!/usr/bin/env python3
"""Preview-token guard for embargoed press releases.

Mirrors the inline "Embargo guard" Python in .github/workflows/hugo.yml.
Run before any preview build step.

Rules (per section _index.md anywhere under content/press/ that carries a
`preview_token` field):

  1. `preview_token` must be a non-empty hex string of at least 24 chars
     (~96 bits of entropy — `openssl rand -hex 12` produces this).
  2. `preview_lift` must be present and a parseable ISO datetime.
  3. Tokens must be globally unique across all sections (incoming AND lifted).
  4. For _incoming/ sections: `preview_lift` must equal the maximum
     `publishDate` found among release files within the section
     (catches token/embargo desync).

The script exits 0 on success, 1 on any violation. All violations are
printed; we don't bail on first.
"""
from __future__ import annotations

import datetime as dt
import pathlib
import re
import sys


HEX_RE = re.compile(r"^[0-9a-fA-F]{24,}$")
PRESS_ROOT = pathlib.Path("content/press")


def parse_front_matter(md: pathlib.Path) -> dict[str, str]:
    """Tiny TOML/YAML-front-matter scrape — just enough to read flat
    string/scalar fields. Avoids a YAML dependency for guard-time use."""
    text = md.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end < 0:
        return {}
    out: dict[str, str] = {}
    for line in text[3:end].splitlines():
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\s*:\s*(.+?)\s*$", line)
        if not m:
            continue
        key, val = m.group(1), m.group(2)
        if (val.startswith('"') and val.endswith('"')) or (
            val.startswith("'") and val.endswith("'")
        ):
            val = val[1:-1]
        out[key] = val
    return out


def parse_dt(s: str) -> dt.datetime | None:
    try:
        d = dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return None
    if d.tzinfo is None:
        d = d.replace(tzinfo=dt.timezone.utc)
    return d


def main() -> int:
    if not PRESS_ROOT.is_dir():
        print(f"no {PRESS_ROOT}/ directory found", file=sys.stderr)
        return 1

    violations: list[str] = []
    tokens: dict[str, pathlib.Path] = {}  # token → first section that used it

    for idx in PRESS_ROOT.rglob("_index.md"):
        fm = parse_front_matter(idx)
        token = fm.get("preview_token")
        if not token:
            continue

        # Rule 1: format
        if not HEX_RE.match(token):
            violations.append(
                f"{idx}: preview_token {token!r} must be hex, >=24 chars"
            )

        # Rule 3: uniqueness
        if token in tokens:
            violations.append(
                f"{idx}: preview_token {token!r} also used by {tokens[token]}"
            )
        else:
            tokens[token] = idx

        # Rule 2: preview_lift present + parseable
        lift = fm.get("preview_lift")
        if not lift:
            violations.append(f"{idx}: preview_lift missing")
        elif parse_dt(lift) is None:
            violations.append(f"{idx}: preview_lift {lift!r} not parseable")

        # Rule 4: for _incoming sections only, lift must match max publishDate
        if "_incoming" in idx.parts and lift and parse_dt(lift):
            max_pd = None
            for sub in idx.parent.glob("*.md"):
                if sub == idx:
                    continue
                sub_fm = parse_front_matter(sub)
                pd_str = sub_fm.get("publishDate")
                if not pd_str:
                    continue
                pd = parse_dt(pd_str)
                if pd and (max_pd is None or pd > max_pd):
                    max_pd = pd
            if max_pd is not None and parse_dt(lift) != max_pd:
                violations.append(
                    f"{idx}: preview_lift {lift} != max(publishDate) {max_pd.isoformat()}"
                )

    if violations:
        print("Preview-token guard failed:", file=sys.stderr)
        for v in violations:
            print("  " + v, file=sys.stderr)
        return 1

    if tokens:
        print(f"Preview-token guard: {len(tokens)} token(s) validated.")
    else:
        print("Preview-token guard: no tokens to validate.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
