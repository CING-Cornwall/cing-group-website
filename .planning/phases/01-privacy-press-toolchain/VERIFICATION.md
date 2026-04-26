# Phase 1 Verification

**Date:** 2026-04-26
**Commits verified:** 5e4f6be (PR #6), 45d3a00 (PR #7)
**Repo HEAD:** 45d3a00 on `main`

## Success criteria

### Criterion 1 — Reject triggers zero GA requests
**Verdict: PASS**

Empirical evidence from `layouts/_default/baseof.html` on current `main`:

- The Consent Mode v2 default-deny block (`gtag('consent', 'default', { ... })`) is gone — `grep -c "gtag('consent', 'default'" public/index.html` returns **0**, and no such call appears anywhere in `baseof.html`.
- `window.loadGtag()` is defined inside the `{{ if hugo.IsProduction }}` block at `baseof.html:8-32`.
- Idempotency flag `gtagLoaded` declared at `baseof.html:15`, guarded at `baseof.html:18-19` (`if (gtagLoaded) return; gtagLoaded = true;`).
- Page-load auto-load gated on accepted consent at `baseof.html:28-30` (`if (localStorage.getItem('cing-cookies') === 'accepted') { window.loadGtag(); }`).
- Accept handler calls `window.loadGtag()` at `baseof.html:247-249`.
- Reject handler at `baseof.html:251-254` only writes `localStorage.setItem('cing-cookies', 'rejected')` and hides the banner — no `gtag('consent', 'update', ...)`, no script injection, no analytics calls.
- The previous unconditional script-injection IIFE (`(function() { var s = document.createElement... })()`) is gone — the only script-injection path is the gated `window.loadGtag` body.
- Production build confirms gating: `grep -c "loadGtag" public/index.html` = **2** (definition + Accept-handler call), and the gtag script tag is conspicuously absent until `loadGtag()` runs.

### Criterion 2 — Privacy page H2s render correctly
**Verdict: PASS**

`content/privacy/_index.md` contains zero literal `##X` (no-space) heading lines (`grep -cE '^##[A-Za-z]' content/privacy/_index.md` = **0**). Every `##` is followed by a space.

Production-built HTML at `public/privacy/index.html`:

| Heading                | `<h2>…</h2>` count |
| ---------------------- | ------------------ |
| What data we collect   | 1                  |
| Data retention         | 1                  |
| Your rights            | 1                  |
| Contact us             | 1                  |

Plus: `grep -c '<p>##' public/privacy/index.html` = **0** and `grep -cE '##[A-Za-z]' public/privacy/index.html` = **0** (no literal `##` text bleeding through into rendered paragraphs).

### Criterion 3 — CLAUDE.md describes post-fix flow
**Verdict: PASS**

`CLAUDE.md` `### Analytics and cookie consent` section (line 87 onward):

- Mentions `window.loadGtag()` by name as the function in `baseof.html` that injects gtag.
- Explicitly states: "rejecting (or not yet choosing) results in zero requests to `googletagmanager.com` and `google-analytics.com`."
- Describes both invocation sites (page-load when stored choice is `accepted`, and the cookie banner Accept handler) and notes the `gtagLoaded` idempotency flag.
- `grep -in -E "consent mode v2|default.deny" CLAUDE.md` returns **no matches** — no stale Consent Mode v2 / default-deny narrative remains.

### Criterion 4 — Press script no FileNotFoundError on markdown
**Verdict: PASS**

`scripts/generate_press_pdfs.py:37`: `SOURCE_DIR = ROOT / "content" / "press" / "full-council-2026-04-21"` — points at the live publish path, not `_incoming`.

Each of the five `Release.src_md` values is `SOURCE_DIR / "<slug>.md"` and the slug is identical to the `Release.slug` field (lines 122-163). All five source paths exist on disk under `content/press/full-council-2026-04-21/`:

| Slug                          | `src_md` exists |
| ----------------------------- | --------------- |
| `mevagissey-school-transport` | yes             |
| `childrens-nhs-dental-care`   | yes             |
| `rural-deprivation-funding`   | yes             |
| `glyphosate-weedkiller-halt`  | yes             |
| `planning-public-trust`       | yes             |

Static analysis confirms the previous `FileNotFoundError` failure mode is no longer reachable for the markdown read in `build_pdf` (`release.src_md.read_text(...)` at line 463). NB: a runtime execution of the script was not performed in this verification because the Lato/Poppins TTF assets at `/usr/share/fonts/truetype/lato` and `/usr/share/fonts/truetype/google-fonts` are an environmental dependency of the verifier host rather than something Phase 1 was scoped to address — see Notes below.

## Cross-document consistency

`.planning/codebase/INTEGRATIONS.md` analytics section (lines 21-22) references `window.loadGtag()` as the gating function and describes the pre-consent / post-Reject zero-request behaviour. `grep -in -E "consent mode v2|default.deny|gtag\\('consent', 'default'" .planning/codebase/INTEGRATIONS.md` returns no matches. Documentation is internally consistent across `CLAUDE.md`, `INTEGRATIONS.md`, and the implementation in `baseof.html`.

## Build verification

Production build (`HUGO_ENVIRONMENT=production hugo --gc --minify --baseURL "http://localhost:8888/" --quiet`): exit code **0**, no errors.

Post-build greps:

- `grep -c "loadGtag" public/index.html` → **2** (≥ 1 required) ✓
- `grep -c "gtag('consent', 'default'" public/index.html` → **0** (must be 0) ✓
- Privacy page H2 counts (4 expected names, each = 1) — all ✓
- `grep -c '<p>##' public/privacy/index.html` → **0** ✓

Optional dev-mode sanity check: `hugo --quiet --environment development --destination /tmp/cing-dev-verify2` produces an `index.html` with `grep -c "loadGtag"` = **0**. (Note: bare `hugo` without an explicit environment defaults to `production` in Hugo 0.160.1, which is why the simpler invocation in the original verification spec yields a non-zero count — this is Hugo's default behaviour, not a regression. The production gate `{{ if hugo.IsProduction }}` is functioning correctly.)

## Phase verdict

**PASS**

All four success criteria are satisfied with empirical evidence: the GA script is now strictly gated behind cookie consent (with no Consent Mode v2 default-deny pre-load and no unconditional injection), the privacy page renders four well-formed `<h2>` sections instead of literal `##` text, `CLAUDE.md` and `INTEGRATIONS.md` describe the post-fix flow accurately and consistently, and the press-PDF generator points at the canonical content directory with all five markdown source files present on disk. The production build completes cleanly, and the production gate keeps `loadGtag` out of true development builds. The active legal/reputational exposure identified at the start of Phase 1 has been eliminated.

## Notes

- **Press script runtime not executed.** Criterion 4 was verified by static analysis (path correctness + file-existence checks for all five `src_md` paths). A live run was not attempted because the script depends on Lato and Poppins TTF assets at `/usr/share/fonts/truetype/lato` and `/usr/share/fonts/truetype/google-fonts`, which is an environment-provisioning concern that the project roadmap allocates to Phase 3 (BUILD-02 — package press-PDF generation reproducibly). Phase 1's contractual obligation was to remove the `FileNotFoundError` on the markdown path itself, which is done.
- **Optional dev-mode check reframed.** The verification spec's `hugo --quiet --destination /tmp/cing-dev-verify` invocation does inject `loadGtag` because Hugo treats non-`server` runs as `production` by default. The semantic intent — "production gate keeps GA out of dev builds" — is satisfied when the environment is explicitly set to `development`, which has been confirmed.
- **No regressions surfaced** in headers/templates touched by Phase 1; both the privacy page and homepage build cleanly under `--minify`.
