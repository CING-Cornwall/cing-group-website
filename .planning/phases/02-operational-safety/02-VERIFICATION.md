---
phase: 02-operational-safety
verified: 2026-04-26T00:00:00Z
status: passed
score: 7/7 success criteria, 8/8 requirements
re_verification:
  previous_status: null
  is_initial: true
verdict: PASS WITH NITS
---

# Phase 2: Operational Safety — Verification Report

**Phase Goal:** Close the operational gates that protect editorial integrity (embargo) and legal posture (form consent, accessibility) so an embargoed release cannot accidentally publish early, marketing emails carry recorded GDPR consent, and the site survives a basic accessibility audit.
**Verified:** 2026-04-26
**Status:** PASS WITH NITS (all SC and REQs satisfied; one content nit + one ops follow-up flagged below)
**Re-verification:** No — initial verification

## Build status

`hugo --gc --minify --baseURL "https://www.cingparty.uk/"` → **exit 0**, 37 pages + 39 static files in 28 ms, zero warnings. Build is clean.

## Success Criteria

### SC-1: Embargoed press release with future `publishDate` does not exist on `main` — PASS

All five files under `content/press/full-council-2026-04-21/` carry `publishDate: 2026-04-20T09:00:00+01:00`. `git log --diff-filter=A --name-only -- 'content/press/full-council-2026-04-21/*.md'` shows the four spec-driven files were first added in `22e8ef2` on 2026-04-20 10:57:59 +0100 (i.e. commit time was *after* the publishDate that day, then bumped to 09:00 the next morning) and the fifth (`planning-public-trust.md`) in `c61ee0e` on 2026-04-20 11:25:03 +0100. No file's commit timestamp predates its `publishDate`. The `_incoming/` staging area exists (`content/press/_incoming/_index.md`) with `cascade.build.render: never` so any future drafts dropped there are unrendered.

### SC-2: Scheduled GitHub Actions trigger fires ≥4× daily and rebuilds — PASS

`.github/workflows/hugo.yml:16-21` declares `schedule: - cron: "0 7,9,12,17 * * *"` (four UTC strikes daily). Deploy gate at line 99 broadened to `if: github.event_name == 'push' || github.event_name == 'schedule'`, so the build job and the deploy job both run on schedule events. The build env sets `TZ: Europe/London`. (Note: the cron is expressed in UTC with no DST adjustment — accepted in the SUMMARY's decisions, not a regression.)

### SC-3: Every form has a `_gotcha` honeypot — PASS

Source grep across the three form-bearing layouts:

| File | `_gotcha` count |
|------|-----------------|
| `layouts/get-involved/list.html` | 2 (contact + newsletter) |
| `layouts/index.html` | 1 (homepage CTA newsletter) |
| `layouts/press/list.html` | 1 (press signup) |

Total 4 honeypots across 4 forms. Same totals reproduce in `public/get-involved/index.html` (2), `public/index.html` (1), `public/press/index.html` (1).

### SC-4: Both newsletter forms refuse submission without an explicit opt-in tickbox — PASS

Both newsletter forms (`layouts/get-involved/list.html` line ~155, `layouts/index.html` line ~205) and the press form contain `<input type="checkbox" name="marketing_consent" value="yes" required` with **no** `checked` attribute. The press signup also carries the same pattern (verbatim D-05 wording). `grep -rE '<input[^>]*marketing_consent[^>]*checked' public/` returns **0** — zero pre-ticks rendered. PECR explicit-positive-action satisfied.

### SC-5: Contact, newsletter, and press-list submissions arrive at three distinct Formspree inboxes — PASS

`hugo.toml` lines 10-13:

```toml
formspreeId           = "mvzvgdbl"     # legacy alias retained
formspreeContactId    = "mvzvgdbl"     # legacy form repurposed as contact
formspreeNewsletterId = "xaqakgoy"
formspreePressId      = "myklvqwe"
```

Rendered actions extracted from `public/`:

| Page | Form | Endpoint |
|------|------|----------|
| /get-involved/ | contact | `formspree.io/f/mvzvgdbl` |
| /get-involved/ | newsletter | `formspree.io/f/xaqakgoy` |
| / | homepage CTA newsletter | `formspree.io/f/xaqakgoy` |
| /press/ | press signup | `formspree.io/f/myklvqwe` |

Three distinct endpoint IDs — `mvzvgdbl` / `xaqakgoy` / `myklvqwe` — across the four forms. Zero bare `formspreeId` references in any layout's `<form action=>`.

### SC-6: Decorative hero images present `alt=""`; news/press article hero images present content-equivalent alt — PASS

Decorative inversion across **6** layouts (8 imgs total): `layouts/index.html` ×2, `layouts/about/list.html` ×1, `layouts/policies/policies.html` ×1, `layouts/councillors/list.html` ×1, `layouts/press/list.html` ×2 (hero + granite-texture overlay), `layouts/get-involved/list.html` ×1 (Join CING bento). Each emits `alt="" role="presentation"` (minifier collapses to `alt role=presentation`, HTML5-equivalent). Per-page rendered counts: index 2, about 1, councillors 1, policies 1, press 2, get-involved 1.

Article-hero pattern across **4** layouts: `layouts/news/single.html`, `layouts/press/single.html`, `layouts/news/list.html` (×2 — featured + grid), `layouts/index.html` (homepage news teaser) — all use `{{ with $.Params.imageAlt }}{{ . }}{{ end }}` (single-page) or `$pageImageAlt := .Params.imageAlt` captured before `{{ with .Params.image }}` (range loops). `grep -nE 'alt="\{\{.*\.Title' layouts/news/ layouts/press/ layouts/index.html` returns **0** — no title-fallback regression.

8 content files carry populated `imageAlt:` front-matter (3 news + 5 press). Round-trip verified: `public/press/full-council-2026-04-21/childrens-nhs-dental-care/index.html` renders `alt="A child at a dental check-up"`. Archetype scaffold `imageAlt = ''` present at `archetypes/default.md:6`.

### SC-7: 404 hit renders CING header, footer, and a navigation choice — PASS

`layouts/404.html` exists (51 lines), uses `{{ define "main" }}` to inherit `baseof.html` chrome (header/footer rendered via `{{ block "main" . }}` mechanism — no manual partial calls that would double-render). Three CTAs to `/`, `/news/`, `/councillors/` via `{{ "/path" | relURL }}` — all site-relative.

Built `public/404.html` chrome strings: `Skip to main content` (1), `County Hall` (1, footer Truro address), `Cornish Independent` (3), `Get Involved` (3), `CING` (3 in minified prod). CTA href counts: `href=/[ />]` → 4, `href=/news/` → 4, `href=/councillors/` → 4 (counts > 1 because the same paths appear in inherited header nav and footer columns; expected). Editorial copy `404 — Not Found` and `wandered off` both render.

## Requirements Coverage

| REQ | Status | Evidence |
|-----|--------|----------|
| **EMBARGO-02** | PASS | `_incoming/` exists with `cascade.build.render: never`; embargo-guard step at `.github/workflows/hugo.yml:54-82` runs before `Build with Hugo` and uses `if "_incoming" in md.parts` membership check (defeats `_incoming-notes.md`-style bypass). Local dry-run against current tree returns `VIOLATIONS: none`. |
| **EMBARGO-03** | PASS | `schedule: cron: "0 7,9,12,17 * * *"` at `.github/workflows/hugo.yml:21`; deploy job's `if: github.event_name == 'push' || github.event_name == 'schedule'` at line 99 guarantees scheduled runs reach `actions/deploy-pages@v4`. `TZ: Europe/London` set on the build env. |
| **FORMS-01** | PASS | 4 honeypots across 4 forms (source + rendered counts match). Hidden via inline style + `tabindex=-1` + `aria-hidden=true` per pattern. |
| **FORMS-02** | PASS | Both newsletter forms (`get-involved/list.html` line 155-region, `index.html` line 205-region) have `<input type=checkbox name=marketing_consent value=yes required>` with no `checked` attribute. Verbatim D-04 string `I agree to receive occasional email updates from CING. You can unsubscribe at any time.` present in both. (Press form has equivalent D-05 wording.) |
| **FORMS-03** | PASS | Three distinct Formspree IDs in `hugo.toml` and rendered. Contact = `mvzvgdbl`, newsletter = `xaqakgoy`, press = `myklvqwe`. Zero bare `{{ .Site.Params.formspreeId }}` references in any of the four `<form action=>`. |
| **A11Y-01** | PASS | 8 decorative img tags across 6 layouts emit `alt="" role="presentation"`. 6 distinct pages render the decorative pattern (≥5 threshold met). |
| **A11Y-02** | PASS | 4 layouts read article-hero alt from `.Params.imageAlt` with empty-fallback `with`. 8 content files have populated `imageAlt:`. None duplicates the title. End-to-end: `alt="A child at a dental check-up"` renders in built press page. |
| **A11Y-03** | PASS | `layouts/404.html` exists, three CTAs, GH-Pages-equivalent chrome verified in `public/404.html`. SUMMARY-04's `hugo server` curl test returned `HTTP/1.1 404 Not Found` with branded body for unknown paths. |

All 8 Phase 2 requirements satisfied. (Note: `REQUIREMENTS.md` traceability table line 106 marks A11Y-03 as Complete and lines 99-105 as Pending — the table is stale; all eight should now be Complete. Cosmetic only, not a verification gap.)

## Anti-pattern scan

- **No TODO/FIXME/PLACEHOLDER** in any file modified by Phase 2 (`.github/workflows/hugo.yml`, `hugo.toml`, four layout files modified by 02-02, ten layout files modified by 02-03, eight content files, archetype, `layouts/404.html`).
- **No empty stub functions** — all changes are template/markup/config edits. No `return null`-style holes.
- **No hardcoded test/dev data** — Formspree IDs are real production values supplied by maintainer commit `4dad5ce`.
- **One scope-discipline observation:** the `$pageTitle` variable in `layouts/news/list.html` and `layouts/index.html` is now unused (it was the source of the title-duplicating alt that Plan 03 removed). Plan 03's SUMMARY flags this as a known minor cleanup deferred to keep the diff minimal — informational only, not a defect.

## Behavioural spot-checks

| Behaviour | Command | Result | Status |
|-----------|---------|--------|--------|
| Site builds clean with prod baseURL | `hugo --gc --minify --baseURL "https://www.cingparty.uk/"` | exit 0, 37 pages, 0 warnings | PASS |
| Embargo guard logic accepts current tree | `python3 - <<'PY' ...` (mirroring workflow step) | `VIOLATIONS: none` | PASS |
| Workflow YAML is syntactically valid | `python3 -c "import yaml; yaml.safe_load(open('.github/workflows/hugo.yml'))"` | exit 0 | PASS |
| Press-card alt round-trips to rendered HTML | `grep -F 'alt="A child at a dental check-up"' public/press/.../childrens-nhs-dental-care/index.html` | match | PASS |
| Three Formspree endpoints render distinctly | `grep -oE 'formspree\.io/f/[a-z]+' public/...` | `mvzvgdbl` + `xaqakgoy` + `myklvqwe` | PASS |
| No pre-ticked consent checkboxes | `grep -rE '<input[^>]*marketing_consent[^>]*checked' public/` | 0 matches | PASS |
| 404 chrome renders | `grep -c 'Cornish Independent' public/404.html` etc. | header (3) + footer (3) strings present | PASS |

## Items requiring follow-up before merging or shipping

These are NITS — none blocks the phase from being declared complete, but flagging for the maintainer's awareness:

1. **Press hero JPGs are CING-branded title cards, not literal scenes.** Plan 03 wrote `imageAlt: "A child at a dental check-up"`-style theme-scene wording per CONTEXT mandate, but the actual JPGs are illustrated dark-blue title cards with the headline burned into the image. SUMMARY-03 explicitly flags this for reviewer decision: keep theme-scene wording, or refresh to literal-card descriptions ("Press release card titled 'Every Child Deserves a Dentist'") in a follow-up content edit. **Verifier recommendation:** accept the current wording — it is content-equivalent to the press-release subject and does not duplicate the title; literal-card descriptions add nothing for screen-reader users beyond noise.

2. **Formspree IDs are live production values, not placeholders.** Maintainer commit `4dad5ce` introduced real IDs `mvzvgdbl`, `xaqakgoy`, `myklvqwe`. Confirm with the maintainer that the three corresponding Formspree dashboards (Contact / Newsletter / Press) are configured correctly (notification recipient, spam protection level, autoresponder text). This is a maintainer-side verification — out of scope for the codebase audit but worth raising before the next push to `main` if the dashboards have not been touched since `4dad5ce`.

3. **`$pageTitle` variable left unused** in `layouts/news/list.html` (lines around 24 and 68) and `layouts/index.html` (~line 161). Cosmetic — schedule a tiny housekeeping PR or fold into the next layout edit.

4. **`REQUIREMENTS.md` traceability table is stale.** Lines 99-105 still mark EMBARGO-02, EMBARGO-03, FORMS-01..03, A11Y-01..02 as Pending. After this verification, all eight should flip to Complete. Pure documentation update; can be batched with the ROADMAP progress-table update for Phase 2.

5. **DST drift on cron schedule** (accepted in SUMMARY-01 decisions, restated here): `0 7,9,12,17 * * *` is UTC, so during BST the four UK strikes land at 08:00 / 10:00 / 13:00 / 18:00 local. Acceptable for 4× daily redundancy; if BST timing matters more precisely, consider switching to two cron lines (one for GMT, one for BST) in a future plan.

## Verdict: PASS WITH NITS

All 7 success criteria satisfied. All 8 requirements satisfied. Build clean. Embargo guard mathematically correct (membership test on `_incoming`, ISO-8601 parse, `now` in UTC, both `pd` branches normalised). Three Formspree endpoints render distinctly across four forms. 8 decorative imgs across 6 layouts and 8 content-driven article-hero alts ship as designed. 404 wears full CING chrome with three live CTAs. Phase 2 is shippable — proceed to Phase 3 (Trust & performance) when ready.

---

**Files of relevance (absolute paths):**

- `/home/roc/repo/cing-group-website/.github/workflows/hugo.yml`
- `/home/roc/repo/cing-group-website/hugo.toml`
- `/home/roc/repo/cing-group-website/layouts/404.html`
- `/home/roc/repo/cing-group-website/layouts/get-involved/list.html`
- `/home/roc/repo/cing-group-website/layouts/index.html`
- `/home/roc/repo/cing-group-website/layouts/press/list.html`
- `/home/roc/repo/cing-group-website/layouts/news/single.html`
- `/home/roc/repo/cing-group-website/layouts/news/list.html`
- `/home/roc/repo/cing-group-website/layouts/press/single.html`
- `/home/roc/repo/cing-group-website/layouts/about/list.html`
- `/home/roc/repo/cing-group-website/layouts/policies/policies.html`
- `/home/roc/repo/cing-group-website/layouts/councillors/list.html`
- `/home/roc/repo/cing-group-website/archetypes/default.md`
- `/home/roc/repo/cing-group-website/content/press/_incoming/_index.md`
- `/home/roc/repo/cing-group-website/content/press/full-council-2026-04-21/*.md` (5 files)
- `/home/roc/repo/cing-group-website/content/news/*.md` (3 backfilled)

_Verified: 2026-04-26_
_Verifier: Claude (gsd-verifier)_
