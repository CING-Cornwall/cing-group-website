# Requirements: CING Group Website

**Defined:** 2026-04-26
**Core Value:** Publish accurate, timely, professional-grade content under the group's name without leaking embargoed material, breaking privacy promises, or misrepresenting any councillor's record.

**Source:** Derived from `.planning/codebase/CONCERNS.md` (audit 2026-04-26). Validated requirements (already shipped) live in `PROJECT.md`; this document tracks the unshipped scope.

## v1 Requirements

Requirements for the four-wave remediation programme. Each maps to exactly one phase via the Traceability table below.

### Privacy & analytics

- [ ] **PRIVACY-01**: GA `gtag/js` script must not be injected into the page until the user accepts consent via the cookie banner; rejecting consent must result in zero requests to `*.googletagmanager.com` and `*.google-analytics.com`
- [ ] **PRIVACY-02**: All H2 headings in `content/privacy/_index.md` render as headings (not literal `##` text) — markdown is well-formed
- [ ] **PRIVACY-03**: `CLAUDE.md` accurately describes the GA loading flow as it exists post-PRIVACY-01

### Embargo & press toolchain

- [ ] **EMBARGO-01**: `scripts/generate_press_pdfs.py` runs without `FileNotFoundError` against the current published press release source paths
- [x] **EMBARGO-02
**: Embargoed press release drafts never appear on `main` (or in `main`'s git history) before their `publishDate` — drafts live on a separate branch or in `_incoming/` until embargo lifts
- [x] **EMBARGO-03
**: A scheduled GitHub Actions trigger rebuilds the site at least four times daily so post-dated content publishes when its `publishDate` passes, even without a new commit

### Forms

- [x] **FORMS-01
**: Every Formspree-backed form on the site includes a hidden `_gotcha` honeypot field
- [x] **FORMS-02
**: Both newsletter forms include a `<input type="checkbox" required>` GDPR opt-in tickbox with text describing what the user is subscribing to
- [x] **FORMS-03
**: Contact, newsletter, and press-list submissions route to three separate Formspree endpoints, each ID stored under `params.formspree*Id` in `hugo.toml`

### Accessibility

- [x] **A11Y-01
**: Decorative full-bleed hero images use `alt=""` and `role="presentation"` so screen readers skip them
- [x] **A11Y-02
**: News and press article hero images use content-equivalent alt text (not duplication of the article title)
- [x] **A11Y-03
**: A branded `layouts/404.html` page exists with the CING header, footer, and a "back to home / news / councillors" choice

### Images

- [ ] **IMG-01**: Hero and landscape images are emitted as WebP variants via Hugo image processing with responsive `srcset` for at least three viewport widths
- [ ] **IMG-02**: Every `<img>` element below the initial viewport uses `loading="lazy"`
- [ ] **IMG-03**: All hero images have explicit `width` and `height` attributes to eliminate cumulative layout shift
- [ ] **IMG-04**: All councillor portraits share the same resolution, aspect ratio, and tonal treatment so the grayscale-on-hover effect renders consistently

### Councillor data

- [ ] **DATA-01**: `data/councillors.yaml` is validated against a JSON-Schema (or YAML schema) on every PR — schema check fails CI on missing/extra fields or malformed values
- [ ] **DATA-02**: Each councillor entry in `data/councillors.yaml` carries an `active: true|false` flag; only `active: true` councillors render on the public site
- [x] **DATA-03
**: Cornwall Council attendance and committee membership are refreshed weekly via a GitHub Actions cron job that opens a PR with the diff (no auto-merge)

### Build & dependencies

- [x] **BUILD-01
**: Tailwind CSS is compiled at build time (Hugo Pipes or pre-built static asset) with the Play CDN script removed from `baseof.html`
- [ ] **BUILD-02**: Python scripts in `scripts/` declare dependencies via a pinned `requirements.txt`, bundle their fonts under `scripts/fonts/`, and use repo-relative font paths
- [x] **BUILD-03
**: A `.github/dependabot.yml` configuration file opens automated PRs for Hugo and GitHub Actions version updates

### CI safety nets

- [x] **CI-01
**: A link checker (e.g. lychee) runs on every PR against the built `public/` directory and fails CI on any broken internal link
- [x] **CI-02
**: A pa11y-ci accessibility scan runs on every PR against five canonical URLs (home, about, councillors, news, get-involved) with a zero-error budget

## v2 Requirements

Deferred to a future milestone. Tracked but not in the current roadmap.

### Taxonomy

- **TAXONOMY-01**: Re-enable Hugo `category` taxonomy and add `layouts/_default/taxonomy.html` + `term.html` to provide `/topics/<slug>/` indexes — triggered when news or press archives exceed ~10 posts each

## Backlog (v2)

Tracked in `bd` (beads). The local Dolt database lives in `.beads/dolt/` (machine-local; not committed). Canonical specs preserved here for portability across machines and clones.

- **DATA-03-FIX-SOURCE** (bd: `cing-938`, P1, bug — surfaced 2026-04-27 by first cron run, PR #22 closed): Switch `scripts/refresh_councillors.py` from `democracy.cornwall.gov.uk/mg{UserInfo,Attendance}.aspx?UID=...` to `cornwallpoliticalwatch.com/councillors/{slug}`. The mgAttendance page shows only a rolling ~6-month window (5/8 = 62% for Rowland on 03/11/2025–28/04/2026) which would regress the displayed all-time attendance figures (Rowland 90 → 62, Anna 95 → 100, Karen 89 → 83). PRD §6 already mandates CPW as the source-of-truth — original DATA-03 plan's research missed this. Replace the 6 council-page fixtures with 3 CPW fixtures; preserve fail-loud parser semantics; preserve cron schedule + PR-creation flow. Once landed, "Cornwall Council" artefact in committees lists also disappears (CPW only lists actual committee memberships).
- **A11Y-04** (bd: `cing-03k`, P2, bug — surfaced 2026-04-27 by Phase 4 UAT): Resolve 9 pre-existing WCAG2AA violations the new pa11y-ci gate currently masks via per-URL ignore list in `.pa11yci.json`. Specifically: hero `<span>Local Action.</span>` contrast 2.41:1 vs primary-container background (recommend `#00060b`), email input on `/get-involved/` missing accessible name (`<label>` / `aria-label` / `aria-labelledby`), plus 6 large-text contrast violations across `/`, `/about/`, `/councillors/`. Removal procedure documented in `docs/MAINTENANCE.md`. Restore plain-string URL entries in `.pa11yci.json` once resolved. (A11Y-01..03 already used by Phase 2.)
- **TYPOGRAPHY-01** (bd: `cing-fnm`, P3, feature — deferred from Phase 4 BUILD-01 POC, 2026-04-26): Wire `@tailwindcss/typography` plugin via `@plugin` directive in `assets/css/main.css` and audit prose defaults against the brand type scale (Manrope headings + Public Sans body, defined in `assets/css/theme.css` `@theme` block). Out of scope: changing the type scale itself.
- **DATA-03-WATCH** (bd: `cing-86k`, P4, task — depends on `cing-938`): After `cing-938` lands and 4–6 weekly cron PRs have arrived, evaluate cadence, parser robustness as CPW HTML evolves, and reviewer noise level. Resolve when the cron has run cleanly without intervention for that window.

## Out of Scope

Explicitly excluded — see `PROJECT.md` for full reasoning.

| Feature | Reason |
|---------|--------|
| Server-side functionality / database | Static site is intentional; trust and auditability of a public political record matter more than interactivity |
| CMS / headless editor | Contributor count is small and technical; CMS adds attack surface, hosting cost, vendor dependency |
| SPA framework (React/Vue/Svelte) | Hugo + Tailwind already meet user needs; SPA harms SEO, accessibility, load time |
| Multilingual / Cornish-language variants | Not currently scoped; reconsider at milestone boundary |
| Visual regression testing vs Stitch | Judged overkill for current cadence; revisit if a brand audit complains |
| Paid hosting / CDN beyond GitHub Pages | Free tier fits current scale comfortably |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| PRIVACY-01 | Phase 1 | Complete |
| PRIVACY-02 | Phase 1 | Complete |
| PRIVACY-03 | Phase 1 | Complete |
| EMBARGO-01 | Phase 1 | Complete |
| EMBARGO-02 | Phase 2 | Complete |
| EMBARGO-03 | Phase 2 | Complete |
| FORMS-01 | Phase 2 | Complete |
| FORMS-02 | Phase 2 | Complete |
| FORMS-03 | Phase 2 | Complete |
| A11Y-01 | Phase 2 | Complete |
| A11Y-02 | Phase 2 | Complete |
| A11Y-03 | Phase 2 | Complete |
| IMG-01 | Phase 3 | Pending |
| IMG-02 | Phase 3 | Pending |
| IMG-03 | Phase 3 | Pending |
| IMG-04 | Phase 3 | Pending |
| BUILD-02 | Phase 3 | Pending |
| DATA-01 | Phase 3 | Pending |
| DATA-02 | Phase 3 | Pending |
| BUILD-01 | Phase 4 | Complete |
| DATA-03 | Phase 4 | Pending |
| CI-01 | Phase 4 | Pending |
| CI-02 | Phase 4 | Pending |
| BUILD-03 | Phase 4 | Pending |

**Coverage:**
- v1 requirements: 24 total
- Mapped to phases: 24
- Unmapped: 0

---
*Requirements defined: 2026-04-26*
*Last updated: 2026-04-26 after initialization*
