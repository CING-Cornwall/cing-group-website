# Roadmap: CING Group Website

## Overview

A four-phase remediation programme for the CING website, derived from the codebase audit in `.planning/codebase/CONCERNS.md`. The site itself is healthy and shipped — this roadmap addresses the 17 known concerns identified in that audit, sequenced by blast radius and dependency rather than raw severity. Phase 1 closes immediate legal/reputational exposure; Phase 2 hardens the operational gates around publication; Phase 3 raises trust and performance signals; Phase 4 tackles the structural issues whose payoff is real but whose effort is heaviest.

Branch protection on `main` (the prerequisite for safely shipping any of this) was the first thing landed and is reflected in `PROJECT.md` Validated requirements.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3, 4): Planned remediation waves
- Decimal phases (e.g. 2.1) reserved for urgent insertions if they arise

- [x] **Phase 1: Privacy & press toolchain** — Make the privacy claims true and unblock the press release pipeline
- [ ] **Phase 2: Operational safety** — Embargo safeguards, form compliance, accessibility table-stakes
- [ ] **Phase 3: Trust & performance** — Image pipeline, councillor data validation, reproducible scripts
- [ ] **Phase 4: Structural** — Tailwind build pipeline, councillor data automation, CI safety nets

## Phase Details

### Phase 1: Privacy & press toolchain
**Goal:** Eliminate the active legal/reputational exposure (privacy-policy contradiction, malformed privacy markdown, broken press-PDF script) so the site stops publicly misrepresenting its own behaviour and the press toolchain remains operable.
**Depends on:** Nothing (branch protection prerequisite already shipped)
**Requirements:** PRIVACY-01, PRIVACY-02, PRIVACY-03, EMBARGO-01
**Success Criteria** (what must be TRUE):
  1. A visitor who clicks "Reject" in the cookie banner triggers zero requests to `googletagmanager.com` or `google-analytics.com` (verifiable in browser DevTools Network tab on the production site)
  2. The privacy page at `/privacy/` renders all H2 sections as actual headings (verifiable by inspecting the rendered HTML — `<h2>` tags, not `<p>##...</p>`)
  3. The privacy section of `CLAUDE.md` correctly describes the post-fix GA loading flow (no references to a non-existent `loadGtag()` function)
  4. Running `python scripts/generate_press_pdfs.py` from a clean checkout regenerates all five existing 2026-04-21 PDFs without `FileNotFoundError`
**Plans:** TBD (estimated 2 plans)

Plans:
- [ ] 01-01: Privacy & analytics consent gating (PRIVACY-01, PRIVACY-02, PRIVACY-03 — bundled because they share mental model and reviewer context)
- [ ] 01-02: Press PDF script path repointing (EMBARGO-01 — independent of the privacy work, can ship in parallel)

### Phase 2: Operational safety
**Goal:** Close the operational gates that protect editorial integrity (embargo safety) and legal posture (form consent, accessibility). After this phase, an embargoed press release cannot accidentally appear early, marketing emails carry recorded GDPR consent, and the site survives a basic accessibility audit.
**Depends on:** Phase 1
**Requirements:** EMBARGO-02, EMBARGO-03, FORMS-01, FORMS-02, FORMS-03, A11Y-01, A11Y-02, A11Y-03
**Success Criteria** (what must be TRUE):
  1. An embargoed press release with a future `publishDate` does not exist on `main` (verifiable: `git log` shows no commit adding it before its embargo date)
  2. A scheduled GitHub Actions trigger fires at least four times daily and rebuilds the site, publishing post-dated content when its time arrives (verifiable in Actions history)
  3. Every form on the site has a `_gotcha` honeypot field (verifiable by inspecting page source)
  4. Both newsletter forms refuse submission without an explicit opt-in tickbox checked
  5. Contact, newsletter, and press-list submissions arrive at three distinct Formspree inboxes
  6. Decorative hero images present `alt=""` to screen readers; news/press article images present content-equivalent alt text
  7. A 404 hit on the production site renders the CING header, footer, and a navigation choice instead of GitHub's default error
**Plans:** 4 plans

Plans:
- [ ] 02-01-PLAN.md — Embargo workflow safeguard: schedule trigger + CI guard for future-dated press (EMBARGO-02, EMBARGO-03)
- [ ] 02-02-PLAN.md — Form compliance: honeypot on all four forms + PECR consent on newsletters/press + three-way Formspree endpoint split (FORMS-01, FORMS-02, FORMS-03)
- [ ] 02-03-PLAN.md — Accessibility: decorative-hero alt inversion + article-hero imageAlt pattern + 8-post backfill (A11Y-01, A11Y-02)
- [x] 02-04-PLAN.md — Branded 404 layout: editorial header + three CTAs, inherits CING chrome (A11Y-03)

### Phase 3: Trust & performance
**Goal:** Raise the trust signals visitors and search engines use to judge the site — fast, sharp, validated. Image weight comes down by ~80%, councillor data gains a schema gate, the press toolchain becomes reproducible across machines.
**Depends on:** Phase 2
**Requirements:** IMG-01, IMG-02, IMG-03, IMG-04, BUILD-02, DATA-01, DATA-02
**Success Criteria** (what must be TRUE):
  1. Hero and landscape images are served as WebP with responsive `srcset` covering at least 480px / 1024px / 1920px viewports
  2. All `<img>` elements outside the initial viewport carry `loading="lazy"`
  3. All hero images have explicit `width` and `height` attributes (CLS budget remains green)
  4. All three councillor portraits render at the same resolution, aspect ratio, and visual weight; the grayscale-on-hover effect looks consistent across all three cards
  5. `data/councillors.yaml` is validated against a schema in CI; introducing a malformed entry fails the build
  6. Each councillor entry has an `active` boolean; setting `active: false` removes that councillor from `/councillors/` and `/about/` without other edits
  7. `python scripts/generate_press_pdfs.py` runs successfully on a clean checkout where `/usr/share/fonts/...` does not exist
**Plans:** 3 plans

Plans:
- [x] 03-01-PLAN.md — Image pipeline: assets/ migration + responsive-image partial + 10 templates + CI cache (IMG-01, IMG-02, IMG-03)
- [x] 03-02-PLAN.md — Councillor portrait parity (1024×1024) + JSON Schema gate + active flag (IMG-04, DATA-01, DATA-02)
- [x] 03-03-PLAN.md — Press script reproducibility: requirements.txt + bundled SIL-OFL fonts + repo-relative paths (BUILD-02)

### Phase 4: Structural
**Goal:** Replace the two structural shortcuts (Tailwind Play CDN, hand-maintained councillor data) with build-time and automation-time solutions, and add the CI safety nets that prevent regression on everything shipped in Phases 1-3.
**Depends on:** Phase 3
**Requirements:** BUILD-01, DATA-03, CI-01, CI-02, BUILD-03
**Success Criteria** (what must be TRUE):
  1. The Play CDN script tag is removed from `baseof.html`; CSS is served as a built static asset and the site renders identically with no flash of unstyled content
  2. A weekly cron job opens a PR proposing diffs to `data/councillors.yaml` based on Cornwall Council source pages (no auto-merge)
  3. Lychee runs on every PR and fails on broken internal links
  4. pa11y-ci runs on every PR against the five canonical URLs with a zero-error budget
  5. Dependabot opens PRs for Hugo and GitHub Actions version bumps automatically
**Plans:** TBD (estimated 3 plans)

Plans:
- [ ] 04-01: Tailwind build pipeline (BUILD-01)
- [ ] 04-02: Councillor data refresh cron (DATA-03)
- [ ] 04-03: CI safety nets — link check + a11y scan + dependabot (CI-01, CI-02, BUILD-03)

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Privacy & press toolchain | 2/2 | Complete | 2026-04-26 |
| 2. Operational safety | 0/4 | Not started | - |
| 3. Trust & performance | 3/3 | Plans complete (verifying) | - |
| 4. Structural | 0/3 | Not started | - |

---
*Roadmap created: 2026-04-26*
