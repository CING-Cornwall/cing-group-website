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
- [ ] **DATA-03**: Cornwall Council attendance and committee membership are refreshed weekly via a GitHub Actions cron job that opens a PR with the diff (no auto-merge)

### Build & dependencies

- [ ] **BUILD-01**: Tailwind CSS is compiled at build time (Hugo Pipes or pre-built static asset) with the Play CDN script removed from `baseof.html`
- [ ] **BUILD-02**: Python scripts in `scripts/` declare dependencies via a pinned `requirements.txt`, bundle their fonts under `scripts/fonts/`, and use repo-relative font paths
- [ ] **BUILD-03**: A `.github/dependabot.yml` configuration file opens automated PRs for Hugo and GitHub Actions version updates

### CI safety nets

- [ ] **CI-01**: A link checker (e.g. lychee) runs on every PR against the built `public/` directory and fails CI on any broken internal link
- [ ] **CI-02**: A pa11y-ci accessibility scan runs on every PR against five canonical URLs (home, about, councillors, news, get-involved) with a zero-error budget

## v2 Requirements

Deferred to a future milestone. Tracked but not in the current roadmap.

### Taxonomy

- **TAXONOMY-01**: Re-enable Hugo `category` taxonomy and add `layouts/_default/taxonomy.html` + `term.html` to provide `/topics/<slug>/` indexes — triggered when news or press archives exceed ~10 posts each

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
| EMBARGO-02 | Phase 2 | Pending |
| EMBARGO-03 | Phase 2 | Pending |
| FORMS-01 | Phase 2 | Pending |
| FORMS-02 | Phase 2 | Pending |
| FORMS-03 | Phase 2 | Pending |
| A11Y-01 | Phase 2 | Pending |
| A11Y-02 | Phase 2 | Pending |
| A11Y-03 | Phase 2 | Complete |
| IMG-01 | Phase 3 | Pending |
| IMG-02 | Phase 3 | Pending |
| IMG-03 | Phase 3 | Pending |
| IMG-04 | Phase 3 | Pending |
| BUILD-02 | Phase 3 | Pending |
| DATA-01 | Phase 3 | Pending |
| DATA-02 | Phase 3 | Pending |
| BUILD-01 | Phase 4 | Pending |
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
