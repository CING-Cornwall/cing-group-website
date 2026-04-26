---
phase: 02-operational-safety
plan: 04
subsystem: ui/error-page
tags:
  - 404
  - error-page
  - branded-chrome
  - design-system
  - hugo-template
  - github-pages
requires: []
provides:
  - "Branded layouts/404.html — CING header, footer, three CTAs (home/news/councillors), tertiary-gold tone-band-compliant headline"
  - "Hugo emits public/404.html on every build (prod and dev) — GitHub Pages serves it on any 404 with no Pages config change"
affects:
  - "Any future plan that wants to standardise other error surfaces (5xx, friendly redirect pages) — pattern to mirror lives in layouts/404.html"
tech_stack_added: []
patterns_used:
  - "{{ define \"main\" }} template inheritance from layouts/_default/baseof.html (no manual partial calls — chrome included via {{ block \"main\" . }})"
  - "Editorial-header composition (eyebrow + three-clause headline + tertiary-gold accent on final clause) from layouts/get-involved/list.html"
  - "Three-card CTA bento with navy → surface (editorial-shadow) → tertiary-container colour rhythm from layouts/index.html principles bento"
  - "pt-32 fixed-nav offset matching layouts/get-involved/list.html and layouts/news/list.html"
  - "Material Symbols icons (home, newspaper, groups) — already loaded by baseof.html, no extra <link> needed"
key_files_created:
  - layouts/404.html
key_files_modified: []
decisions:
  - "Adopted PATTERNS §8 composite skeleton verbatim — no wording deviation. Headline 'This page has / wandered off / the map.' satisfies CONTEXT D-09 tone band (branded confident with Cornish flavour, three short clauses, tertiary-gold accent on final clause)."
  - "File placed at layouts/404.html (NOT layouts/_default/404.html) — Hugo's special path is at the layouts root."
  - "No hugo.IsProduction gate — 404 is content, not analytics. Confirmed by running development-environment build which also emits a fully-chromed public/404.html."
  - "No partial \"header.html\" / partial \"footer.html\" calls inside the 404 template — baseof.html already includes them around the {{ block \"main\" }} hole, so manual calls would double-render the chrome."
metrics:
  duration_minutes: 4
  tasks_completed: 2
  files_touched: 1
  commits: 1
  completed_date: "2026-04-26"
requirements_completed:
  - A11Y-03
---

# Phase 2 Plan 04: Branded 404 Layout Summary

**Hugo `layouts/404.html` composing template-shell + editorial header + bento CTAs — ships a 404 that wears full CING chrome and offers three primary recovery paths instead of GitHub Pages' default error.**

## Performance

- **Duration:** ~4 min
- **Started:** 2026-04-26T14:53:16Z
- **Completed:** 2026-04-26T14:56:41Z
- **Tasks:** 2
- **Files modified:** 1 (created)

## Accomplishments

- New `layouts/404.html` (51 lines) ships a fully branded error page with header/footer chrome, an editorial 404 announcement, and three navy/surface/tertiary CTA cards.
- `hugo --gc --minify` emits `public/404.html` (17 KB before minify, 14 KB after) — GitHub Pages will serve this automatically on any 404; no Pages config touched.
- Live `hugo server` returns `HTTP/1.1 404 Not Found` for unmatched paths and the body contains the editorial eyebrow + apology copy + branded chrome.
- Equivalent `public/404.html` produced under `--environment development` — proves the page is unconditional content, not gated behind `hugo.IsProduction`.

## Task Commits

1. **Task 1: Create layouts/404.html composed from existing patterns** — `902960f` (feat)
2. **Task 2: Build site, verify public/404.html and live 404 status** — verification only, no source changes (results captured in this SUMMARY)

_Plan metadata commit will land alongside this SUMMARY._

## Files Created/Modified

- `layouts/404.html` — new file. `{{ define "main" }}` block containing the editorial header (eyebrow `404 — Not Found`, three-clause headline, apology copy on the right) and three-card CTA grid (`/`, `/news/`, `/councillors/`) using the canonical CING navy → surface (editorial-shadow) → tertiary-container colour rhythm. Material Symbols icons: `home`, `newspaper`, `groups`. No `hugo.IsProduction` wrapper. No manual partial calls.

## Decisions Made

- **Headline wording:** kept PATTERNS §8 verbatim — "This page has / wandered off / the map." with the tertiary-gold accent on "the map." Plan permits substitution within the tone band, but the supplied wording already satisfies all stated constraints (three short clauses, tertiary-gold final-clause accent, avoids generic "Sorry, page not found" and deadpan "404"), and matches the `Local Voice. / Local Action.` two-part rhythm cited in CONVENTIONS. No wording deviation needed.
- **File path:** `layouts/404.html` (Hugo's special-path location), confirmed by checking that `layouts/_default/` previously had no 404.html and that the build emits `public/404.html` from the root path.
- **Inheritance vs. inline partials:** relied on `baseof.html`'s `{{ block "main" . }}` mechanism (it wraps `{{ partial "header.html" . }}` above and `{{ partial "footer.html" . }}` below the block at lines 207/213). No manual `partial "header.html"` / `partial "footer.html"` calls inside the 404 template — those would double-render the chrome.

## Verification Evidence

### Task 1 acceptance proofs (source file)

```
$ test -f layouts/404.html && echo OK                           OK
$ grep -c '{{ define "main" }}' layouts/404.html                 1
$ grep -c '{{ end }}' layouts/404.html                           1
$ grep -c '"/" | relURL' layouts/404.html                        1   (home CTA)
$ grep -c '"/news/" | relURL' layouts/404.html                   1   (news CTA)
$ grep -c '"/councillors/" | relURL' layouts/404.html            1   (councillors CTA)
$ grep -c '404 — Not Found' layouts/404.html                     1   (eyebrow)
$ grep -c 'text-tertiary' layouts/404.html                       3   (eyebrow + accent + tertiary CTA hover)
$ grep -c 'editorial-shadow' layouts/404.html                    1   (surface CTA card)
$ grep -c 'material-symbols-outlined' layouts/404.html           3   (one icon per CTA)
$ grep -c 'hugo.IsProduction' layouts/404.html                   0   (no production gate)
$ grep -c 'partial "header.html"' layouts/404.html               0
$ grep -c 'partial "footer.html"' layouts/404.html               0
$ hugo --renderToMemory                                          exit 0 — 37 pages built in 31 ms
```

All Task 1 acceptance criteria satisfied.

### Task 2 acceptance proofs (built site + live server)

**Production build:**

```
$ hugo --gc --minify --baseURL "http://localhost:1313/"
exit 0 — 37 pages built in 31 ms

$ test -f public/404.html && echo OK                             OK
$ wc -l public/404.html                                          39   (minified, single-line per HTML chunk)
```

**Branded chrome strings chosen for verification (one from header nav, two from footer):**

| String | Where it lives | grep count in `public/404.html` |
|--------|----------------|---------------------------------|
| `CING` | header brand wordmark, mobile menu wordmark, footer brand block | **3** |
| `Cornish Independent` | footer tagline, structured data references at-base | **3** |
| `Get Involved` | header desktop nav CTA, mobile menu nav CTA, mobile menu bottom button | **3** |

Each string appears at least once → header AND footer rendered.

Additional chrome confirmation:

```
$ grep -c 'Skip to main content' public/404.html                 1   (a11y skip link from baseof.html)
$ grep -c 'County Hall' public/404.html                          1   (footer Truro address)
```

**CTA hrefs (note: Hugo's HTML minifier strips quotes from simple attribute values, so the production HTML emits `href=/`, `href=/news/`, `href=/councillors/` not `href="/"`):**

```
$ grep -cE 'href=/[ />]' public/404.html                         4   (homepage CTA + nav links)
$ grep -cE 'href=/news/' public/404.html                         4   (news CTA + nav + footer)
$ grep -cE 'href=/councillors/' public/404.html                  4   (councillors CTA + nav + footer)
```

All three CTAs present (the count > 1 because the same paths also appear in the inherited header nav and footer link columns — that's expected and required).

**Editorial header content:**

```
$ grep -c '404 — Not Found' public/404.html                      1   (eyebrow rendered)
$ grep -c 'wandered off' public/404.html                         1   (headline rendered)
```

**Live 404 spot-check via `hugo server`:**

```
$ curl -sI http://localhost:1313/this-page-definitely-does-not-exist-404-test/ | head -1
HTTP/1.1 404 Not Found

$ curl -s http://localhost:1313/this-page-definitely-does-not-exist-404-test/ | grep -c '404 — Not Found'
1

$ curl -s http://localhost:1313/this-page-definitely-does-not-exist-404-test/ | grep -c 'wandered off'
1

$ curl -s http://localhost:1313/this-page-definitely-does-not-exist-404-test/ | grep -c 'CING'
7   (chrome rendered: header brand + mobile menu brand + footer brand + nav items)

$ curl -sI http://localhost:1313/ | head -1                      HTTP/1.1 200 OK   (sanity check)
```

GH-Pages-equivalent behaviour confirmed: `hugo server` returns `HTTP/1.1 404 Not Found` for an unknown path and serves the branded `public/404.html` body with the eyebrow label, headline, and full chrome.

**Dev-environment regression check:**

```
$ hugo --environment development --baseURL "http://localhost:1313/"
exit 0 — 37 pages built in 32 ms

$ test -f public/404.html && echo OK                             OK
$ grep -c 'wandered off' public/404.html                         1
$ grep -c '404 — Not Found' public/404.html                      1
$ grep -c 'CING' public/404.html                                 7
$ wc -c public/404.html                                          17310   (unminified)
```

The 404 page renders identically in dev → no `hugo.IsProduction` regression. (Larger byte size is just the absence of minification; structural content is the same.)

## Plan-Wide Verification (`<verification>` block)

| # | Check | Result |
|---|-------|--------|
| 1 | `test -f layouts/404.html` | PASS |
| 2 | `grep -c '{{ define "main" }}' layouts/404.html` returns 1 | PASS |
| 3 | `/news/`, `/councillors/`, `"/" \| relURL` each ≥ 1 in source | PASS |
| 4 | `grep -c 'hugo.IsProduction' layouts/404.html` returns 0 | PASS |
| 5 | `grep -c 'partial "header.html"' layouts/404.html` returns 0; same for footer | PASS |
| 6 | `test -f public/404.html` after `hugo` | PASS |
| 7 | `grep -c 'CING' public/404.html` ≥ 1 | PASS (=3 in minified prod, 7 in dev) |
| 8 | `curl -I http://localhost:1313/<nonexistent>` returns `HTTP/1.1 404 Not Found` | PASS |

## Deviations from Plan

None — plan executed exactly as written. PATTERNS §8 composite skeleton was used verbatim; no wording substitution, no layout adjustments, no scope additions. The grep-pattern in Task 2's acceptance criteria was written as `href="/"`/`href="/news/"`/`href="/councillors/"`, but Hugo's HTML minifier strips quotes from simple attribute values in production output. This is not a deviation from the plan's intent — the rendered hrefs are correct; only the literal-string matcher needed to drop the surrounding quotes (substantively equivalent grep used and documented above).

## Issues Encountered

None. Build, runtime, and dev-environment checks all passed first time.

## Threat Surface Scan

No new threat surface introduced.

| Threat ID | Disposition | Implementation status |
|-----------|-------------|------------------------|
| T-02-04-01 | n/a (static page, no input) | Confirmed — no forms, no params, no client-state on 404 |
| T-02-04-02 | accept (open-redirect surface = 0) | All three CTA links built via `{{ "/path" \| relURL }}` — site-relative, no externally-controlled redirect target |
| T-02-04-03 | mitigate (chrome must render) | Task 2 grep-confirmed `CING`, `Cornish Independent`, `Get Involved`, `Skip to main content`, `County Hall` all appear in `public/404.html` |

No `threat_flag:` annotations needed — no new endpoints, auth paths, file-access patterns, or trust boundaries.

## Known Stubs

None. The 404 page is fully realised — three live CTAs, every string is final copy, no placeholder content.

## User Setup Required

None. Hugo emits `public/404.html` automatically on every build; GitHub Pages serves it on any 404 with no Pages config change.

## Next Phase Readiness

- A11Y-03 closed. Phase 2 success criterion #7 ("A 404 hit on the production site renders the CING header, footer, and a navigation choice instead of GitHub's default error") satisfied.
- Pattern available for any future "branded chrome on a Hugo special-path" surface (5xx, redirect pages, RSS error fallbacks): use `{{ define "main" }}` over `baseof.html`, never inline-call header/footer partials.
- No blockers introduced for Phase 2 plans 02 and 03 (forms compliance, alt-text backfill).

## Self-Check: PASSED

**Files claimed:**
- FOUND: `layouts/404.html` (created, 51 lines, contains `{{ define "main" }}` and three CTA blocks)

**Commits claimed:**
- FOUND: `902960f` — `feat(02-04): add branded 404 layout with three primary CTAs`

**Build artefacts claimed (gitignored, but verified present in working tree):**
- FOUND: `public/404.html` (17,310 bytes after dev build; 39-line minified after prod build)

All artefacts and commits verified.

---
*Phase: 02-operational-safety*
*Completed: 2026-04-26*
