# CING Group Website

## What This Is

The public-facing website for the Cornish Independent NonAligned Group (CING) — a group of independent councillors on Cornwall Council. It introduces the group, lists its councillors and their committee work, publishes news and press releases, sets out policy positions, and provides a contact channel for residents. The audience is Cornish residents, journalists, and political observers; the site is the group's primary public voice between elections.

## Core Value

The site must publish accurate, timely, professional-grade content under the group's name without ever leaking embargoed material, breaking the privacy promises it makes to visitors, or misrepresenting any councillor's record.

## Requirements

### Validated

<!-- Shipped and confirmed valuable. Inferred from existing code per /gsd-map-codebase. -->

- ✓ Hugo static site building from `content/`, `data/`, and custom `layouts/` to GitHub Pages — existing
- ✓ Data-driven councillor pages from `data/councillors.yaml` (single source for `/councillors/` and `/about/`) — existing
- ✓ News section with featured bento + grid + pagination — existing
- ✓ Press releases section with embargo support via `publishDate` and `_incoming/` cascade — existing
- ✓ Policies page with manifesto PDF download — existing
- ✓ Get Involved page with Formspree contact + newsletter forms — existing
- ✓ Material Design 3 colour token system + Manrope/Public Sans typography (Stitch-derived) — existing
- ✓ Cookie consent banner with localStorage persistence (production only) — existing
- ✓ Press release branded PDF + hero image generation pipeline (Python/reportlab/Pillow) — existing
- ✓ Custom domain `www.cingparty.uk` via GitHub Pages CNAME — existing
- ✓ CI build on every push and pull request to `main`; deploy gated to push events; branch protection enforcing `build` status check — existing (this milestone)
- ✓ GA `gtag/js` script gated on consent acceptance; rejecting (or no choice) results in zero requests to `googletagmanager.com` / `google-analytics.com` — Phase 1 (PRIVACY-01)
- ✓ Privacy policy markdown renders all H2 sections as actual headings — Phase 1 (PRIVACY-02)
- ✓ `scripts/generate_press_pdfs.py` runnable against published press release source paths — Phase 1 (EMBARGO-01)
- ✓ `CLAUDE.md` and `INTEGRATIONS.md` describe the post-fix GA loading flow accurately — Phase 1 (PRIVACY-03)
- ✓ Hugo Pipes responsive image pipeline: `responsive-image.html` partial emits `<picture>` with WebP+JPEG sources, explicit `width`/`height`, `loading="lazy"` outside the LCP slot; 26 images migrated to `assets/`; CI image cache via `actions/cache@v4` — Phase 3 (IMG-01, IMG-02, IMG-03)
- ✓ Councillor portrait parity at 1024×1024 JPEG q86 with consistent headshot crop bias (Karen Knight flagged for IMG-04 stage 2 — visible upscale softness pending higher-resolution source) — Phase 3 (IMG-04 stage 1)
- ✓ JSON Schema (Draft-07) gate for `data/councillors.yaml` validated in CI between embargo guard and Hugo build; `additionalProperties: false`, boolean `active` enforced — Phase 3 (DATA-01)
- ✓ Per-councillor `active` boolean drives a `where ... "active" true` filter in `councillors/list.html` and `about/list.html`; setting `active: false` hides without deletion — Phase 3 (DATA-02)
- ✓ Press script reproducibility: `scripts/requirements.txt` pins `reportlab==4.4.10` and `Pillow==12.2.0`; SIL-OFL Manrope + Public Sans bundled at `scripts/fonts/`; both scripts run from clean checkouts without `/usr/share/fonts/` — Phase 3 (BUILD-02)

### Active

<!-- Current scope. Drawn from .planning/codebase/CONCERNS.md, organised by Wave. -->

**Wave 2 — Operational safety (next 2 weeks)**

- [ ] Embargo workflow safeguard: keep drafts off `main` + add `schedule:` cron to `hugo.yml` so post-dated content auto-publishes — HIGH
- [ ] Forms: honeypot + GDPR consent tickbox on newsletters + split Formspree endpoints — MEDIUM (×2)
- [ ] Branded `layouts/404.html` page — MEDIUM
- [ ] Alt-text audit (decorative heroes get `alt=""`, news/press images get content-equivalent text) — MEDIUM

**Wave 3 — Trust & performance (shipped 2026-04-26 — see Validated above)**

- [x] Image optimisation pipeline — Phase 3 (IMG-01, IMG-02, IMG-03)
- [x] Councillor portrait parity at 1024×1024 (Stage 1; IMG-04 Stage 2 deferred pending higher-resolution source for Karen Knight)
- [x] `councillors.yaml` JSON-Schema validation in CI + `active` flag — Phase 3 (DATA-01, DATA-02)
- [x] Press script reproducibility — Phase 3 (BUILD-02)
- [ ] IMG-05 (new backlog from 03-01): Procure ≥1920px hero photography to unlock the full responsive srcset curve — pipeline is ready, source assets are 512px placeholders

**Wave 4 — Structural (next quarter)**

- [ ] Tailwind Play CDN → build-time Tailwind (Hugo Pipes or compiled CSS asset) — HIGH
- [ ] Phase-2 councillor data cron: scrape Cornwall Council attendance/committees weekly, open PR with diff — HIGH
- [ ] Lychee link-check + pa11y-ci accessibility scan in CI — LOW
- [ ] Re-enable taxonomies for category indexing once archive grows past ~10 posts — LOW
- [ ] Dependabot for Hugo + GitHub Actions versions — LOW

### Out of Scope

<!-- Explicit boundaries. Includes reasoning to prevent re-adding. -->

- Server-side functionality (auth, databases, dynamic search) — site is intentionally static; trust/auditability of a public political record matters more than interactivity
- CMS or headless editor for non-technical contributors — current contributor count is small and technical; introducing a CMS adds attack surface, hosting cost, and another vendor dependency
- Single-page application / framework (React, Vue, Svelte) — Hugo + Tailwind already meet every documented user need; SPA would harm SEO, accessibility, and load time
- Multilingual / Cornish-language variants — not currently scoped; would be reconsidered at milestone boundary if the group prioritises it
- Visual regression testing against live Stitch designs — judged overkill for current cadence in CONCERNS.md (LOW); revisit if a brand audit complains
- Paid hosting / CDN beyond GitHub Pages — current scale fits free tier comfortably; cost/effort to migrate not justified

## Context

**Political context.** CING is an active group of three independent councillors (Anna Thomason-Kenyon, Rowland O'Connor, Karen Knight). The website is their public voice between elections; reputational risk from broken pages, stale councillor data, leaked embargoed press, or compliance gaffes is real and immediate. The site exists in a UK regulatory environment — UK GDPR / PECR for analytics and email marketing, ICO oversight for privacy claims.

**Technical context.** Hugo 0.159.1 extended, no Node/npm, no theme — all layouts are custom under `layouts/`. Tailwind is loaded via the Play CDN with Material Design 3 colour tokens declared inline in `baseof.html`. Stitch HTML exports under `.reference/` (gitignored) are the canonical design source per `docs/brand/DESIGN.md`. Branch protection is now active on `main` requiring the `build` status check; admins are subject to the rules. Branch protection was the first piece of infrastructure shipped under this initiative — every subsequent change goes through a PR.

**Maintenance context.** The single technical maintainer is Rowland O'Connor (also a councillor). PRs are typically self-merged through CI. The contributor model is "one engineer + occasional non-technical input from other councillors on copy", so CI safety nets and codebase legibility matter more than team-coordination tooling.

**Documentation depth.** The repo has unusually mature documentation for a small site: `docs/brand/` contains the full Stitch-derived design system, `docs/manifesto/` the source prose, and `.planning/codebase/` (added 2026-04-26) the seven-document codebase map. Use these as the authoritative inputs to planning, not assumed defaults.

**Active issues.** A complete catalogue of known issues lives in `.planning/codebase/CONCERNS.md` (six HIGH, ten MEDIUM, eight LOW concerns identified 2026-04-26). The Active requirements above are derived from that file, organised into four delivery waves.

## Constraints

- **Tech stack:** Hugo (no other static site generator), Tailwind for utility CSS — these are non-negotiable for this milestone; Tailwind delivery mechanism may change but Tailwind itself stays
- **Hosting:** GitHub Pages with custom domain `www.cingparty.uk` — switching providers is out of scope
- **Build tooling:** No Node/npm dependency in the steady state — if Wave 4 introduces a Tailwind build step, it must be a single-step CI pipeline with no local Node requirement for non-CSS work
- **Compliance:** UK GDPR + PECR — privacy policy must accurately describe analytics behaviour; marketing email subscription requires explicit opt-in
- **Editorial integrity:** No embargoed material may exist on `main` ahead of its publish time, even via git history — this rules out approaches that store unpublished press in `content/press/<dated-slug>/` with a future `publishDate`
- **Performance budget (informal):** Mobile-rural-Cornwall 4G must remain a usable experience — eliminates "ship 3 MB of decorative imagery per page" patterns
- **Single-maintainer reality:** Solutions must be operable by one technical person who is also a councillor — rules out heavy review processes, complex multi-stage deploys, or anything requiring a team rota

## Key Decisions

<!-- Decisions made during initialization. Add throughout project lifecycle. -->

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Bootstrap GSD over the existing brownfield site rather than rebuild | Codebase is healthy and brand-consistent; CONCERNS.md is the catalyst, not architectural rot | — Pending |
| Organise active requirements by 4 delivery waves rather than 17 micro-phases | Single maintainer, small site — wave granularity keeps planning overhead proportional to delivery effort | — Pending |
| Branch protection on `main` with `build` required, admin-enforced, 0 approvals | Single technical maintainer; PR + CI gate is the discipline value, requiring a human approver would block all work | ✓ Good |
| Codebase map produced before project initialization | Brownfield site with non-obvious editorial concerns (embargo, councillor data freshness); planning needs that grounding | ✓ Good |
| Skip server-side functionality, CMS, and SPA frameworks | Static site delivers all current user needs; complexity would add attack surface and vendor dependency without offsetting benefit | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-04-26 after initialization*
