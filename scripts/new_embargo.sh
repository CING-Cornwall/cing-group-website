#!/usr/bin/env bash
# Scaffold a new embargoed press-release section.
#
# Usage:
#   scripts/new_embargo.sh <section-slug> <lift-datetime-iso>
#
# Example:
#   scripts/new_embargo.sh full-council-2026-06-23 2026-06-23T07:00:00+01:00
#
# Creates content/press/_incoming/<section-slug>/_index.md with a freshly
# generated preview_token (24 hex chars, ~96 bits of entropy) and the
# supplied lift datetime. Drop your release .md files alongside it.

set -euo pipefail

if [ "$#" -ne 2 ]; then
  cat >&2 <<EOF
Usage: $0 <section-slug> <lift-datetime-iso>
  e.g. $0 full-council-2026-06-23 2026-06-23T07:00:00+01:00
EOF
  exit 64
fi

slug="$1"
lift="$2"

# Sanity-check: lift datetime must be parseable.
if ! python3 -c "import datetime,sys; datetime.datetime.fromisoformat(sys.argv[1].replace('Z','+00:00'))" "$lift" >/dev/null 2>&1; then
  echo "lift-datetime $lift is not a valid ISO datetime" >&2
  exit 65
fi

dir="content/press/_incoming/$slug"
if [ -e "$dir" ]; then
  echo "$dir already exists — refusing to overwrite" >&2
  exit 1
fi

token=$(openssl rand -hex 12)
mkdir -p "$dir"

# Title fallback derived from slug: "full-council-2026-06-23" → "Full Council — 23 June 2026".
# Best-effort only; the editor should overwrite the title with the meeting's proper name.
title="$slug"

cat > "$dir/_index.md" <<EOF
---
title: "$title"
date: ${lift%T*}
publishDate: $lift
preview_token: "$token"
preview_lift: $lift
description: "Press releases relating to $title."
---

Press releases relating to $title.
EOF

cat <<EOF
Created $dir/_index.md
  preview_token: $token
  preview_lift:  $lift

Drop release .md files into $dir/ and push.
Preview URL (after first deploy):
  https://www.cingparty.uk/preview/$token/press/$slug/<release-slug>/
EOF
