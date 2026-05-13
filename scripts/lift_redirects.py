#!/usr/bin/env python3
"""Generate meta-refresh redirect stubs for lifted embargo previews.

Background: every embargoed press-release section carries a `preview_token`
in its `_index.md` front matter, which gives it a stable unguessable URL
under /preview/<token>/ for pre-embargo sharing. When the section moves out
of `content/press/_incoming/` to its public home, the preview build stops
emitting that path — leaving any bookmarked preview URL 404'ing.

This script walks every lifted section (`_index.md` outside `_incoming/`
that still carries a `preview_token`), enumerates the rendered HTML pages
under the public output for that section, and writes a tiny redirect stub
under `public/preview/<token>/...` for each. Journalists' bookmarks resolve
to the canonical URL via meta-refresh + JS, with a visible link as the last
line of defence.

Must run AFTER the main Hugo build (it needs `public/press/<section>/...`
to exist). Best-effort: failures here must not block deploy.
"""
from __future__ import annotations

import pathlib
import re
import sys


PRESS_ROOT = pathlib.Path("content/press")
PUBLIC = pathlib.Path("public")
SITE_BASE = "https://www.cingparty.uk"


def parse_token(md: pathlib.Path) -> str | None:
    """Cheap front-matter scrape — preview_token only."""
    if not md.is_file():
        return None
    text = md.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end < 0:
        return None
    m = re.search(
        r"^preview_token:\s*[\"']?([0-9a-fA-F]+)[\"']?\s*$",
        text[3:end],
        re.MULTILINE,
    )
    return m.group(1) if m else None


def redirect_html(target: str) -> str:
    # Inline minimal styling so the fallback page looks intentional rather
    # than broken on the (rare) browser without meta-refresh + JS.
    return f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="robots" content="noindex,nofollow,noarchive">
<meta name="referrer" content="no-referrer">
<title>Redirecting to the published press release</title>
<meta http-equiv="refresh" content="0; url={target}">
<link rel="canonical" href="{target}">
<style>
  body {{ font: 16px/1.5 system-ui, -apple-system, "Segoe UI", sans-serif; max-width: 36em; margin: 4em auto; padding: 0 1.5em; color: #00263b; }}
  h1   {{ font-size: 1.4em; margin: 0 0 1em; }}
  p    {{ margin: 0 0 1em; }}
  a    {{ color: #003d5b; word-break: break-all; }}
</style>
</head><body>
<h1>This embargo has lifted.</h1>
<p>The press release is now live. If your browser doesn't redirect automatically, please follow this link:</p>
<p><a href="{target}">{target}</a></p>
<script>location.replace({target!r});</script>
</body></html>
"""


def write_stub(path: pathlib.Path, target: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(redirect_html(target), encoding="utf-8")


def main() -> int:
    if not PUBLIC.is_dir():
        print(f"{PUBLIC}/ not found — run the Hugo build first.", file=sys.stderr)
        return 1
    if not PRESS_ROOT.is_dir():
        print(f"no {PRESS_ROOT}/ directory", file=sys.stderr)
        return 0  # nothing to do

    written = 0
    for idx in PRESS_ROOT.rglob("_index.md"):
        if "_incoming" in idx.parts:
            continue
        token = parse_token(idx)
        if not token:
            continue

        # Section under public/: content/press/<section>/_index.md → public/press/<section>/
        section_rel = idx.parent.relative_to("content")
        prod_section_dir = PUBLIC / section_rel
        if not prod_section_dir.is_dir():
            print(
                f"warning: lifted section {section_rel} not yet in public/ — skipping",
                file=sys.stderr,
            )
            continue

        # Stub every index.html under the section (release pages, paginated indexes, etc.)
        for html in prod_section_dir.rglob("index.html"):
            rel = html.parent.relative_to(PUBLIC).as_posix()
            target = f"{SITE_BASE}/{rel}/"
            stub = PUBLIC / "preview" / token / rel / "index.html"
            write_stub(stub, target)
            written += 1

        # Top-level /preview/<token>/ → /press/<section>/
        section_url = f"{SITE_BASE}/{section_rel.as_posix()}/"
        write_stub(PUBLIC / "preview" / token / "index.html", section_url)
        written += 1

    if written:
        print(f"Lift redirects: wrote {written} stub(s).")
    else:
        print("Lift redirects: no lifted sections with preview_token to stub.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
