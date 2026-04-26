---
phase: 02-operational-safety
plan: 03
subsystem: hugo-templates-and-content
tags:
  - accessibility
  - alt-text
  - wcag
  - hugo-templates
requires:
  - 02-02
provides:
  - decorative-hero-presentation-role
  - article-hero-imageAlt-driven
  - imageAlt-archetype-scaffold
affects:
  - layouts/news/single.html
  - layouts/news/list.html
  - layouts/press/single.html
  - layouts/index.html
  - layouts/about/list.html
  - layouts/policies/policies.html
  - layouts/councillors/list.html
  - layouts/press/list.html
  - layouts/get-involved/list.html
  - archetypes/default.md
  - content/news/*.md
  - content/press/full-council-2026-04-21/*.md
tech-stack:
  added: []
  patterns:
    - "{{ with $.Params.imageAlt }}{{ . }}{{ end }}  (article hero alt with empty fallback)"
    - "{{ $pageImageAlt := .Params.imageAlt }}  then  {{ with $pageImageAlt }}...{{ end }}  (capture-before-with-image pattern in range loops)"
    - 'alt="" role="presentation"  (decorative img signal — minifier collapses to  alt role=presentation, semantically equivalent per HTML5)'
key-files:
  created: []
  modified:
    - archetypes/default.md
    - layouts/news/single.html
    - layouts/news/list.html
    - layouts/press/single.html
    - layouts/index.html
    - layouts/about/list.html
    - layouts/policies/policies.html
    - layouts/councillors/list.html
    - layouts/press/list.html
    - layouts/get-involved/list.html
    - content/news/community-engagement-events.md
    - content/news/spring-council-session-update.md
    - content/news/welcome-to-our-new-website.md
    - content/press/full-council-2026-04-21/childrens-nhs-dental-care.md
    - content/press/full-council-2026-04-21/glyphosate-weedkiller-halt.md
    - content/press/full-council-2026-04-21/mevagissey-school-transport.md
    - content/press/full-council-2026-04-21/planning-public-trust.md
    - content/press/full-council-2026-04-21/rural-deprivation-funding.md
decisions:
  - "Article hero templates wrap .Params.imageAlt in {{ with }} so missing values render alt=\"\" (decorative) instead of falling back to the title — fulfils CONTEXT D-06 forbidding silent title-fallback."
  - "In list/index range loops, the imageAlt is captured into $pageImageAlt before entering {{ with .Params.image }} (which rebinds .) — without this capture the inner expression cannot reach the iterated page's params and Hugo errors with \"can't evaluate field Params in type string\". Plan §5 line-replacement guidance assumed the inner . was the page; build error proved otherwise, fix applied as Rule 3 deviation."
  - "Archetype kept as TOML (not migrated to YAML) per PATTERNS §6 option (a) — corpus stays YAML; archetype-vs-corpus split is intentional minimum-scope this phase."
  - "Press hero JPGs are CING-branded title cards (text rendered ON the image) rather than literal scenes. CONTEXT specifics mandated 'A child at a dental check-up' / 'A worker spraying weedkiller at a roadside' verbatim, so those strings are written even though they describe the press-release theme rather than what the image literally shows. The remaining three press images get analogous theme-scene wording per PATTERNS §7. Reviewer should decide whether to refresh these to literal-card descriptions in a follow-up."
  - "News hero images are real photographs and are described literally (harbour at dusk; residents around a table; St Piran's flag rippling). PATTERNS §7's generic suggestions for the news set were superseded by what the actual JPGs show."
metrics:
  duration: ~50 minutes
  tasks_completed: 5
  commits: 4
  files_modified: 18
  completed_date: 2026-04-26
---

# Phase 02 Plan 03: Alt-Text Inversion Summary

Two opposing alt-text inversions across nine Hugo layouts and eight content posts: decorative hero imgs swapped from descriptive alt → `alt=""` + `role="presentation"`; article hero imgs swapped from `alt="{{ .Title }}"` → imageAlt-front-matter-driven with empty fallback. Closes REQ A11Y-01 and A11Y-02 (WCAG 1.1.1 / UK PSBAR). Image weight optimisation deferred to Phase 3 (REQ IMG-01..03).

## Outcome

- 8 decorative img tags across 6 layouts now signal "decorative" to assistive tech (`alt=""` + `role="presentation"` — minifier collapses to bare `alt role=presentation`, semantically equivalent per HTML5).
- 5 article-hero img tags across 4 layouts read alt from `.Params.imageAlt` with empty fallback. None can ever fall back to the page title.
- 8 existing posts (3 news + 5 press) carry populated `imageAlt:` front-matter values.
- `archetypes/default.md` prompts authors with two comment lines + `imageAlt = ''`.
- 3 informative imgs preserved verbatim: Rowland O'Connor avatar, "Community members in discussion" illustrative bento, all councillor portraits driven by `councillors.yaml`.
- Hugo build clean throughout. End-to-end round-trip proven: `alt="A child at a dental check-up"` renders in `public/press/full-council-2026-04-21/childrens-nhs-dental-care/index.html`.

## Tasks

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | imageAlt scaffold added to archetype | 7f4dd4c | archetypes/default.md |
| 2 | Article hero alt now imageAlt-driven (with empty fallback) | e204d90 | layouts/news/single.html, layouts/news/list.html, layouts/press/single.html, layouts/index.html |
| 3 | Decorative hero alt swapped to `alt="" role="presentation"` | 4cc668a | layouts/index.html, layouts/about/list.html, layouts/policies/policies.html, layouts/councillors/list.html, layouts/press/list.html, layouts/get-involved/list.html |
| 4 | Backfilled imageAlt on 8 content files | 929f888 | 3 news + 5 press posts |
| 5 | Cross-check rendered output | (verification only — no commit) | (audited public/) |

## Plan Questions Asked in Output Spec

### Was there a press-specific archetype?
No. `ls archetypes/` returned only `default.md`. Only that file was modified.

### Was `layouts/_default/list.html:49` modified or skipped?
**Skipped.** The plan said "if reachable, apply same swap" but PATTERNS §5 already noted it's only conditional. On inspection (file not even loaded for this phase) it is a generic section-list fallback that does not host an article hero img — there's nothing matching the article-hero alt pattern in it. No swap needed; no risk of regression.

### Was `layouts/get-involved/list.html:25-27` (bento overlay) modified or skipped?
**Modified.** Read confirmed the img sits behind text "Join CING" with `opacity-40 mix-blend-overlay` — pure decorative wash. Applied `alt="" role="presentation"`. The other img on that page at line 95 (`alt="Community members in discussion"`) was preserved per the plan's informative-img list.

### The 8 imageAlt values written

| File | imageAlt value | Words | Notes |
|------|----------------|-------|-------|
| content/news/community-engagement-events.md | A Cornish harbour at dusk with lit-up village houses | 10 | describes actual hero photo (fishing-village.jpg shows a lit harbour at dusk) |
| content/news/spring-council-session-update.md | Residents reviewing maps around a table at a community meeting | 10 | describes actual hero photo (community-meeting.jpg shows residents around a planning table) |
| content/news/welcome-to-our-new-website.md | Saint Piran's flag, the white cross of Cornwall, rippling in the wind | 13 | describes actual hero photo (st-pirans-flag.jpg shows the rippling flag) |
| content/press/full-council-2026-04-21/childrens-nhs-dental-care.md | A child at a dental check-up | 7 | CONTEXT-mandated verbatim |
| content/press/full-council-2026-04-21/glyphosate-weedkiller-halt.md | A worker spraying weedkiller at a roadside | 7 | CONTEXT-mandated verbatim |
| content/press/full-council-2026-04-21/mevagissey-school-transport.md | A school bus on a narrow Cornish lane | 8 | PATTERNS-suggested theme-scene wording |
| content/press/full-council-2026-04-21/planning-public-trust.md | A construction site on the edge of a Cornish village | 10 | PATTERNS-suggested theme-scene wording |
| content/press/full-council-2026-04-21/rural-deprivation-funding.md | A quiet lane in a rural Cornish hamlet | 8 | PATTERNS-suggested theme-scene wording |

**No alt text duplicates the corresponding page title.** All values are 5–15 words. None ends with a full stop.

### Spot-check output (Task 5 step 3) — proves no title-duplication

```
[welcome-to-our-new-website]
  title=Welcome to the New CING Website | CING
  hero-alts=alt="Saint Piran's flag, the white cross of Cornwall, rippling in the wind"
[spring-council-session-update]
  title=Spring Council Session: Key Highlights | CING
  hero-alts=alt="Residents reviewing maps around a table at a community meeting"
[community-engagement-events]
  title=Upcoming Community Engagement Events | CING
  hero-alts=alt="A Cornish harbour at dusk with lit-up village houses"
```

Each rendered hero alt is clearly distinct from the page title — no duplication regression.

### Decorative-alt regression scan (all zero hits — clean)

```
alt="Cornish Coastline":         0 hits
alt="Cornish coastline":         0 hits
alt="Dramatic Cornish coastline":0 hits
alt="Cornish cliffs at dusk":    0 hits
alt="Cornwall aerial coastline": 0 hits
alt="Cornwall landscape":        0 hits
alt="Granite Texture":           0 hits
```

### Decorative pattern presence in rendered output

Hugo's HTML minifier collapses `alt=""` to bare `alt` and unquotes attribute values, so `alt="" role="presentation"` becomes `alt role=presentation`. This is HTML5-equivalent (omitted-value attribute = empty string per spec; assistive tech treats both as "decorative"). Per-page count using `(alt="" role=presentation|alt role=presentation)` regex:

```
public/index.html:           2  (hero + rotated CTA card)
public/about/index.html:     1  (hero)
public/policies/index.html:  1  (hero)
public/councillors/index.html: 1 (hero)
public/press/index.html:     2  (hero + granite-texture overlay)
public/get-involved/index.html: 1 (Join CING bento overlay)
```

5 distinct rendered pages exceed the plan's "≥ 5 distinct pages" threshold; get-involved adds a sixth.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Captured imageAlt before `{{ with .Params.image }}` in list/index loops**
- **Found during:** Task 2 verification (Hugo build failed)
- **Issue:** Plan §5 instructed `alt="{{ with .Params.imageAlt }}{{ . }}{{ end }}"` literally inside `{{ with .Params.image }}...{{ end }}`. But `{{ with .Params.image }}` rebinds `.` to the image-path string, so `.Params.imageAlt` cannot resolve from a string. Hugo error: `can't evaluate field Params in type string` in `layouts/news/list.html:24` and `layouts/index.html:166`.
- **Fix:** Capture `{{ $pageImageAlt := .Params.imageAlt }}` immediately after the existing `$pageTitle` capture (before entering the image `with`), then reference `{{ with $pageImageAlt }}{{ . }}{{ end }}` in the inner alt expression. Pattern matches PATTERNS §5's "outside `range`, the pattern with `.` (no `$`) also works" caveat.
- **Files modified:** `layouts/news/list.html` (two img blocks: featured @ line 24, grid @ line 68), `layouts/index.html` (homepage news teaser @ line 166)
- **Commit:** e204d90
- **In `layouts/news/single.html` and `layouts/press/single.html` the original `$.Params.imageAlt` form was correct as written**, because those pages have a top-level scope (`$` resolves to the page) and the alt expression sits inside `{{ with .Params.image }}` only — `$` survives that.

### Auth gates

None — all work was on local files.

### Notes for the verifier / reviewer

- **Press images are CING-branded title cards, not photos.** The five press hero JPGs at `static/images/press/*.jpg` render as illustrated dark-blue title cards with the headline text inside the image (visual review during Task 4 confirmed). The plan's CONTEXT specifics mandate the verbatim alt strings "A child at a dental check-up" and "A worker spraying weedkiller at a roadside" for two of them; those describe the *theme* of the press release, not what the title card literally depicts. The remaining three press images received analogous theme-scene wording per PATTERNS §7 suggestions. If the project's preference is for literal-card descriptions (e.g. "Press release card titled 'Every Child Deserves a Dentist'"), a follow-up content edit would refresh them — out of scope for this plan.
- **Build minifier collapses `alt=""` to bare `alt`.** This is Hugo/HTML5 minifier behaviour and HTML5-compliant (empty alt and omitted-value alt both signal "decorative"). The plan's verification commands grepped for `alt="" role="presentation"`; the actual rendered form is `alt role=presentation`. Both unminified source and minified output are correct; only the regex needed adjustment.
- **`$pageTitle` variable is now unused** in `layouts/news/list.html` and `layouts/index.html` (it was only used for the title-duplicating alt). The variable definitions were left in place to keep the diff minimal and avoid unrelated cleanup; a follow-up could remove them.
- **`layouts/_default/list.html:49`** — not loaded, not modified. Out of scope per the plan's "if reachable" caveat. No article hero img exists at that location.

## Self-Check: PASSED

Created files exist (none — no new files this plan).

Commits exist:
- 7f4dd4c — feat(02-03): add imageAlt scaffold to archetype — FOUND
- e204d90 — feat(02-03): drive article hero alt from imageAlt front matter — FOUND
- 4cc668a — feat(02-03): mark decorative hero images as presentation — FOUND
- 929f888 — docs(02-03): backfill imageAlt on 8 news and press posts — FOUND

Plan-wide verification (per PLAN <verification> block):
- (1) `grep -F "imageAlt = ''" archetypes/default.md` exits 0 — PASS
- (2) `grep -rF '.Params.imageAlt'` across 4 layout files returns 5+ hits — PASS (1 + 1 + 2 + 1 = 5)
- (3) `grep -rE 'alt="\{\{ \$\.Title' layouts/news/ layouts/press/single.html` returns 0 — PASS
- (4) `grep -lF 'alt="" role="presentation"' …5 files` returns all 5 — PASS (and a 6th, get-involved)
- (5) All 8 content files have `^imageAlt:` — PASS
- (6) `grep -F 'alt="A child at a dental check-up"' public/.../childrens-nhs-dental-care/index.html` exits 0 — PASS
