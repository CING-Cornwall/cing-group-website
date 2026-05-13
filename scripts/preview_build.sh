#!/usr/bin/env bash
# Build a preview site for every embargoed section in content/press/_incoming/<section>/
# that carries a `preview_token` in its _index.md front matter.
#
# For each section, a scratch source tree is assembled under $RUNNER_TEMP
# (or $TMPDIR locally) by copying the section's content into a clean
# content/press/ tree and symlinking the rest of the Hugo source. Hugo is
# then invoked against that scratch tree, with --baseURL pointing at
# /preview/<token>/ and the preview config overlay. Output is written
# into $GITHUB_WORKSPACE/public/preview/<token>/.
#
# The scratch-tree approach is deliberate: copying _incoming/<section>/ into
# the live `content/press/` tree would expose embargoed content to the main
# build and trip the existing Embargo guard. Doing it in scratch keeps the
# repo's working tree untouched.
#
# Usage:
#   PUBLIC_BASE="https://www.cingparty.uk" scripts/preview_build.sh
#
# Required tools: bash, openssl, rsync, hugo (already in PATH on CI; install
# locally if testing).

set -euo pipefail

PUBLIC_BASE="${PUBLIC_BASE:-https://www.cingparty.uk}"
WORKSPACE="${GITHUB_WORKSPACE:-$PWD}"
SCRATCH_ROOT="${RUNNER_TEMP:-${TMPDIR:-/tmp}}/cing-preview-$$"
SUMMARY_FILE="${GITHUB_STEP_SUMMARY:-/dev/null}"

INCOMING="$WORKSPACE/content/press/_incoming"
if [ ! -d "$INCOMING" ]; then
  echo "No _incoming/ directory; nothing to preview." >&2
  exit 0
fi

# extract_field <key> <file> — returns the value of a flat front-matter key,
# stripping surrounding quotes. Empty string if absent.
extract_field() {
  local key="$1" file="$2"
  awk -v k="$key" '
    /^---[[:space:]]*$/ { in_fm = !in_fm; next }
    in_fm {
      sub(/^[[:space:]]+/, "")
      if (index($0, k ":") == 1) {
        sub("^" k "[[:space:]]*:[[:space:]]*", "")
        gsub(/^["'"'"']|["'"'"']$/, "")
        print
        exit
      }
    }
  ' "$file"
}

built=0
summary_lines=()
mkdir -p "$WORKSPACE/public/preview"

for section_dir in "$INCOMING"/*/; do
  [ -d "$section_dir" ] || continue
  section_name=$(basename "$section_dir")
  idx="$section_dir/_index.md"

  if [ ! -f "$idx" ]; then
    echo "skip: $section_name has no _index.md" >&2
    continue
  fi

  token=$(extract_field "preview_token" "$idx")
  if [ -z "$token" ]; then
    echo "skip: $section_name has no preview_token (run scripts/preview_guard.py to enforce)" >&2
    continue
  fi

  scratch="$SCRATCH_ROOT/$token"
  mkdir -p "$scratch/content/press/$section_name"

  # Copy ONLY this section into the scratch tree. The cascade lives on
  # _incoming/_index.md (not copied), so build.render:never doesn't follow.
  # cp -a preserves attributes and works on minimal environments (no rsync needed).
  cp -a "$section_dir/." "$scratch/content/press/$section_name/"

  # Symlink the rest of the Hugo source. Layouts/assets/static/data/i18n
  # and the top-level config files all live in $WORKSPACE.
  for d in layouts assets static data i18n config archetypes; do
    [ -e "$WORKSPACE/$d" ] && ln -sf "$WORKSPACE/$d" "$scratch/$d"
  done
  for f in hugo.toml hugo.yaml hugo.yml config.toml; do
    [ -e "$WORKSPACE/$f" ] && ln -sf "$WORKSPACE/$f" "$scratch/$f"
  done

  dest="$WORKSPACE/public/preview/$token"
  rm -rf "$dest"
  echo "::group::Preview build — $section_name → /preview/$token/"
  # --buildFuture is essential: embargoed sections have publishDate in the
  # future (that's how they're embargoed); without --buildFuture, Hugo
  # excludes them entirely and the preview is empty.
  hugo \
    --source "$scratch" \
    --destination "$dest" \
    --baseURL "$PUBLIC_BASE/preview/$token/" \
    --environment preview \
    --config "hugo.toml,config/preview/config.toml" \
    --buildFuture \
    --gc --minify
  echo "::endgroup::"

  # Surface the URL in the workflow run summary.
  release_url=""
  # Pick a representative release page to surface (the first .md that isn't _index).
  first_release=""
  for f in "$section_dir"*.md; do
    base=$(basename "$f" .md)
    if [ "$base" != "_index" ]; then
      first_release="$base"
      break
    fi
  done
  if [ -n "$first_release" ]; then
    release_url="$PUBLIC_BASE/preview/$token/press/$section_name/$first_release/"
  else
    release_url="$PUBLIC_BASE/preview/$token/press/$section_name/"
  fi
  summary_lines+=("- **$section_name** — [$release_url]($release_url)")

  built=$((built + 1))
done

# Clean up scratch trees.
rm -rf "$SCRATCH_ROOT"

if [ "$built" -gt 0 ]; then
  echo "Preview build: $built section(s) rendered."
  {
    echo "## Embargo preview URLs"
    echo
    echo "Stable, unguessable URLs for pre-embargo review. Share only under embargo."
    echo
    for line in "${summary_lines[@]}"; do echo "$line"; done
  } >> "$SUMMARY_FILE"
else
  echo "Preview build: no sections to render."
fi
