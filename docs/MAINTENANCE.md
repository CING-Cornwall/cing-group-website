# Maintenance

Operational notes for items not handled automatically (Dependabot doesn't track these).

## Manual version bumps (quarterly)

These are external binaries pinned in `.github/workflows/hugo.yml`. Bump every
quarter (or sooner if a security advisory lands), then verify locally before
merging.

### Hugo

- **File:** `.github/workflows/hugo.yml` — `env: HUGO_VERSION:`
- **Source:** https://github.com/gohugoio/hugo/releases
- **Verify:** `hugo version` after install matches the new pin.

### Tailwind CSS standalone CLI

- **File:** `.github/workflows/hugo.yml` — `env: TAILWIND_VERSION:` and `TAILWIND_SHA256:`
- **Source:** https://github.com/tailwindlabs/tailwindcss/releases
- **SHA:** Download `sha256sums.txt` from the release page; copy the
  `tailwindcss-linux-x64` row into `TAILWIND_SHA256`.
- **Verify locally:**
  ```bash
  curl -fsSL -o /tmp/tailwindcss \
    "https://github.com/tailwindlabs/tailwindcss/releases/download/v${TAILWIND_VERSION}/tailwindcss-linux-x64"
  sha256sum /tmp/tailwindcss   # must match TAILWIND_SHA256
  ```

## Local development workflow

Phase 4 BUILD-01 replaces the Tailwind Play CDN with a build-time-compiled
static asset. `hugo server` will not work alone — it expects
`assets/css/compiled.css` to exist (built by the Tailwind CLI).

**Two-terminal pattern:**

Terminal 1 (CSS watch — auto-recompiles on `assets/css/*.css` edits):

```bash
# macOS arm64: download once from https://github.com/tailwindlabs/tailwindcss/releases
# Linux x64:   curl -fsSL -o tailwindcss https://github.com/tailwindlabs/tailwindcss/releases/download/v4.2.4/tailwindcss-linux-x64
chmod +x tailwindcss
./tailwindcss -i assets/css/main.css -o assets/css/compiled.css --watch
```

Terminal 2 (Hugo server — picks up the watched CSS via Hugo Pipes):

```bash
hugo server --baseURL http://localhost:1313/ --disableFastRender
```

`assets/css/compiled.css` is gitignored — it is a build artefact, never committed.

## Phase 3 carry-forward (from press toolchain)

- **`scripts/requirements.txt` Python pins** are tracked by Dependabot (pip
  ecosystem). No manual action needed.
- **Bundled fonts (`scripts/fonts/*.ttf`)** are SIL-OFL 1.1 vendored copies;
  manual bump only if Manrope or Public Sans ships a face change.

## Phase 4 carry-forward — CI safety net tools

The Phase 4 BUILD-03 plan added Dependabot tracking for `github-actions` and
`pip` ecosystems. Two CI-only tools are NOT tracked by Dependabot because
they're consumed via `npm install --no-save` from inside the workflow (no
`package.json` exists in this repo by design — see CLAUDE.md). They need
manual review when CI surfaces breakage:

| Tool | Pinned in | Review trigger |
|------|-----------|----------------|
| `lycheeverse/lychee-action` | `.github/workflows/hugo.yml` (`@v2` floating major) | If CI fails with "lychee" in the step name and dependabot has bumped the action version |
| `pa11y-ci` (npm) | `.github/workflows/hugo.yml` (`@^4.1.0`) | If CI fails with "pa11y" in the step name; check https://github.com/pa11y/pa11y-ci/releases |
| `http-server` (npm) | `.github/workflows/hugo.yml` (`@^14`) | Rare — only relevant if the `npx http-server` step fails to start |
| `actions/setup-node` | `.github/workflows/hugo.yml` (`@v4` floating major) | Tracked by Dependabot github-actions ecosystem |

**Why pa11y-ci/http-server aren't in dependabot:** They are installed via
`npm install --no-save` ephemerally in CI; there is no `package.json` for
Dependabot to read. The floating SemVer caret (`^4.1.0`) lets `npm install`
pull the latest compatible patch on each run; majors require manual review.

**Cron timing map (Monday UTC):**
- `06:00` — DATA-03 councillor refresh (`.github/workflows/refresh-councillors.yml`)
- `06:30` — Dependabot opens its weekly batch (`.github/dependabot.yml`)
- `07:00` — Embargo cron earliest fire (`.github/workflows/hugo.yml`)

Operator's Monday review session covers all three within ~30 minutes typically.
