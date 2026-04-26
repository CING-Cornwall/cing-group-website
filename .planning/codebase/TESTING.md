# Testing Patterns

**Analysis Date:** 2026-04-26

## Test Framework

**There is no automated test suite.** No unit tests, no integration tests, no E2E tests, no visual regression tests, no link checker. There is no test runner configured anywhere in the repository.

Verified absences:
- No `*.test.*`, `*.spec.*`, or `_test.go` files anywhere in the repo.
- No `package.json`, no `jest.config.*`, no `vitest.config.*`, no `playwright.config.*`, no `cypress.config.*`.
- No `pytest`, `tox.ini`, or test-specific Python configuration despite `scripts/` containing Python.
- No `tests/` directory.
- No CI step that runs `hugo --renderToMemory` for syntax validation, no HTML validator, no Lighthouse CI, no axe-core, no broken-link checker.

This is intentional for a small static site, but it has implications — see "Recommendations" below.

## Local Development Verification

Per `CLAUDE.md` and verified against `hugo.toml`:

```bash
# Local dev server with hot reload, baseURL pinned to localhost
hugo server --baseURL http://localhost:1313/ --disableFastRender
```

`--disableFastRender` is intentional: it forces full-page rebuilds on change, avoiding stale cached partials when iterating on layouts and `tailwind.config` tokens. Without it, Tailwind config changes inside `baseof.html` won't always reflect.

There is no `npm run dev`, no makefile target, no shell wrapper — Hugo is invoked directly.

## Build Verification

Production build (the same command CI runs):

```bash
hugo --gc --minify --baseURL "https://www.cingparty.uk/"
```

Flags:
- `--gc`: garbage-collect unused cache entries.
- `--minify`: minify HTML/CSS/JS in output.
- `--baseURL`: pin to the production custom domain (overrides any local override).

A successful build is the only "test" Hugo provides — it will fail loudly on:
- Template syntax errors (Go template parse failures).
- Missing data references (`hugo.Data` keys that don't exist).
- Front-matter parse errors (invalid YAML/TOML).
- Missing required `_index.md` for sections that need them.

It will **not** catch:
- Broken internal links (`relURL` always renders, even to non-existent pages).
- Missing static images (404s only show in browser).
- Tailwind class typos (CDN Tailwind silently no-ops unknown classes).
- JavaScript errors in `baseof.html` (only manifest at runtime).
- Accessibility regressions.

## GitHub Actions Checks

Workflow: `.github/workflows/hugo.yml` — single workflow for build + deploy.

**What it runs:**
- Installs Hugo Extended `0.159.1` from the official GitHub release.
- Checks out with `submodules: recursive` and `fetch-depth: 0`.
- Configures GitHub Pages.
- Runs `hugo --gc --minify --baseURL "https://www.cingparty.uk/"` with `HUGO_ENVIRONMENT=production` and `TZ=Europe/London`.
- Uploads `./public` as the Pages artifact.
- Deploys to `github-pages` environment.

**What it does NOT run:**
- No linting step (no HTML, YAML, Markdown, or shell linters).
- No test step.
- No Lighthouse, axe, pa11y, or any accessibility/perf check.
- No link checker (e.g. `lychee`, `htmltest`).
- No content validation (e.g. front-matter schema check on `data/councillors.yaml`).
- No PR-only check workflow — the workflow is gated on `push: [main]` and `workflow_dispatch` only, so PRs from forks/branches receive no automated feedback.

The pinned Hugo version (`HUGO_VERSION: 0.159.1`) is the only "test" of build determinism — local builds drift from CI if a contributor uses a different Hugo version.

## Manual UAT / Verification Checklists

**There are no documented UAT checklists** in `docs/`. The `docs/` folder contains brand and manifesto material only (`docs/brand/`, `docs/manifesto/`).

Implicit verification expectations gleaned from `CLAUDE.md`:
- Cookie banner only renders in production builds (`hugo.IsProduction`-gated, `layouts/_default/baseof.html` lines 219–263). Verify by running both `hugo server` (banner absent) and a local `hugo --environment production --baseURL http://localhost:1313/` then serving `public/` (banner present).
- Google Analytics (`G-Z1F4F1TRD0`) loads only in production and only after consent — verify the `localStorage['cing-cookies']` key is set on accept/reject and that the gtag script is/isn't injected accordingly.
- Formspree form ID (`hugo.toml` `params.formspreeId = "mvzvgdbl"`) — submission verification is manual via the live Formspree dashboard.

## Browser Testing Notes

**`.playwright-mcp/` is gitignored** (line 5 of `.gitignore`). Its presence implies one or more contributors have used the Playwright MCP server for ad-hoc browser inspection during development, but no scripted browser tests are committed.

There are no Playwright, Cypress, or Selenium fixtures in the repo. Browser verification is done manually — typically via `hugo server` and the developer's local browser.

The reference HTML in `.reference/` (also gitignored) is the Stitch design source; it is not used for any kind of visual diff testing.

## Lighthouse / Performance / Accessibility Checks

**No evidence of automated Lighthouse, axe-core, pa11y, or WebPageTest runs.** No `lighthouserc.*`, no `.axerc`, no `pa11y.json`, no entries in CI.

Performance and a11y considerations baked into the templates (rather than tested):
- Skip-to-content link (`layouts/_default/baseof.html` lines 206–208).
- `lang` attribute on `<html>` from `.Site.LanguageCode`.
- Preconnect hints for Google Fonts (lines 105–106).
- `display=swap` on Google Fonts requests.
- Material Symbols icon font is loaded as a single stylesheet — no tree-shaking; this is a known perf compromise of using Tailwind via CDN and is not currently measured.
- `aria-label="Main navigation"` on the nav, `aria-label="Cookie consent"` on the banner, `role="dialog"` on the banner — present but not validated.

These are good-faith implementations; without an automated check there is no signal when a regression is introduced.

## PDF Generation Verification

PDFs are generated by Python scripts and committed under `static/documents/`:

- `static/documents/cing-manifesto.pdf` — generated externally per `CLAUDE.md` ("via reportlab"); generation script not currently in the repo.
- `static/documents/press/2026-04-21/<slug>.pdf` — five files, generated by `scripts/generate_press_pdfs.py`.

**Verification approach** (manual):
- The script's `__main__` block iterates `RELEASES` and prints `wrote <path> (<size> KB)` for each — operator scans for non-zero sizes and the expected count (5 files).
- No assertions on page count, no PDF content validation, no diff against a golden file, no schema check.
- Source markdown in `content/press/_incoming/` is consumed but the script is **not** idempotent-safe: rerunning overwrites the output PDFs in place.
- Brand fidelity (fonts, colours, layout) is verified by opening each PDF manually.
- Commit `31178f4 Add press release hero-image and PDF generator scripts` and `94e7625 Lift embargo: publish Full Council 21 April 2026 press releases` show the workflow: generate locally, eyeball each PDF and hero, commit binaries.

The hero-image script (`scripts/generate_press_heroes.py`) follows the same pattern — generate to `static/images/press/<slug>.jpg`, eyeball, commit.

## Test Types Summary

| Test type | Status |
|-----------|--------|
| Unit tests | None |
| Integration tests | None |
| E2E / browser tests | None (ad-hoc Playwright MCP, gitignored) |
| Visual regression | None |
| Build verification | Implicit via `hugo` exit code |
| Linting | None (no eslint, no markdownlint, no yamllint, no htmlhint) |
| Link checking | None |
| Accessibility | None automated |
| Performance | None automated |
| PDF / image content | Manual eyeball |
| Schema validation for `data/councillors.yaml` | None |
| Schema validation for content front matter | None |

## Recommendations (highest leverage gaps)

Three concrete additions — in order of effort-to-value — that would meaningfully reduce regression risk:

1. **Internal link checker in CI.** Add a `lychee` or `htmltest` step after the Hugo build, scoped to `./public`. This catches the highest-frequency real-world failure mode: a renamed page leaving stale `relURL`-built links across `layouts/`, `content/`, and the manifesto. Roughly 10 lines of YAML; no per-page maintenance.

2. **Schema validation for `data/councillors.yaml` and content front matter.** Either a tiny Python script in `scripts/validate_data.py` (jsonschema or pydantic) wired into a pre-commit hook, or a lightweight `ajv-cli` step in CI. Catches missing `attendance`/`email`, malformed photo paths, and the most plausible authoring error: a press release missing `pdf:` or `image:` after a copy-paste. Pays for itself the first time a build silently renders an empty card.

3. **One Playwright smoke test per major page committed alongside the existing Playwright MCP usage.** A single `tests/smoke.spec.ts` that opens `/`, `/councillors/`, `/policies/`, `/news/`, `/press/`, `/get-involved/` and asserts (a) the page returns 200, (b) the `<h1>` is present and non-empty, (c) the cookie banner shows in production but not in dev, (d) the manifesto PDF and at least one press PDF are reachable. ~50 lines; runs against `hugo server` in CI in under a minute. This is the cheapest insurance against the "looks-built, actually-broken" failure mode that is currently invisible to the toolchain.

Beyond these, automated Lighthouse and axe runs would be useful but are lower leverage for a 6-page editorial site than the three above.

---

*Testing analysis: 2026-04-26*
