---
gsd_state_version: 1.0
milestone: v4.2.4
milestone_name: milestone
status: verifying
last_updated: "2026-04-27T07:24:46.761Z"
last_activity: 2026-04-27
progress:
  total_phases: 4
  completed_phases: 3
  total_plans: 12
  completed_plans: 10
  percent: 83
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-04-26)

**Core value:** Publish accurate, timely, professional-grade content under the group's name without leaking embargoed material, breaking privacy promises, or misrepresenting any councillor's record.
**Current focus:** Phase 04 — structural

## Current Position

Phase: 04 (structural) — EXECUTING
Next: 03 (trust-performance) — ready to plan
Plan: 3 of 3
Status: Phase complete — ready for verification
Last activity: 2026-04-27

Progress: [████████░░] 83%

## Performance Metrics

**Velocity:**

- Total plans completed: 9 (Phase 1: 01-01, 01-02; Phase 2: 02-01..04; Phase 3: 03-01, 03-02, 03-03)
- Average duration: ~17 min per plan (Phase 3 plans averaged ~14 min: 03-01 35min image pipeline, 03-02 5min portraits+schema+active, 03-03 4min font bundling)
- Total execution time: Phase 1 ~1 hour; Phase 2 ~70 min; Phase 3 ~45 min wall-clock (Wave 1 parallel: 35min, Wave 2 sequential: 5min, plus verification + review)

**By Phase:**

| Phase | Plans | Status |
|-------|-------|--------|
| 1. Privacy & press toolchain | 2/2 | Complete (verified PASS 2026-04-26, PRs #6 #7 #8 merged) |
| 2. Operational safety | 4/4 | Complete (verified PASS WITH NITS 2026-04-26, PR #9 merged squashed → 901af9d) |
| 3. Trust & performance | 3/3 | Complete (verified human_needed → approved 2026-04-26; HUMAN-UAT.md pending visual checks; SC-1 partial-by-design pending IMG-05 photography procurement) |
| 4. Structural | 0/3 | Ready to plan |

**Recent Trend:**

- Phase 2 shipped one all-in PR (vs Phase 1's split PRs) because plans 02-02 and 02-03 shared files (`layouts/index.html`, `layouts/get-involved/list.html`, `layouts/press/list.html`); cherry-picking would have produced non-buildable intermediate states.
- All four Phase 2 plans passed first-attempt verification; one Rule-3 deviation logged in 02-03 (the `with .Params.image` block rebinds `.` to a string, requiring `$pageImageAlt` capture before entering it).
- Cumulative trend across 6 plans: smooth — every plan landed PASS or PASS WITH NITS at verification, no FAIL, no remedial fix-plans needed.

*Updated after each plan completion*

**Plan execution log (this milestone):**

| Plan | Duration | Tasks | Files | Notes |
|------|----------|-------|-------|-------|
| 01-01 | ~25 min | 3 | (privacy bundle) | shipped via PR #6 |
| 01-02 | ~10 min | 1 | (press script) | shipped via PR #7 |
| 02-01 | ~6 min | 3 | 1 | embargo guard + cron schedule |
| 02-04 | ~4 min | 2 | 1 | branded 404 page |
| 02-02 | ~8 min | 3 | 3 | forms compliance (tasks 1-2 pre-satisfied by `4dad5ce`) |
| 02-03 | ~50 min | 5 | 18 | alt-text inversion (largest plan in milestone) |
| 03-01 | ~35 min | 3 | 14 | image pipeline: 26 images migrated, responsive-image partial, 10 templates rewired, CI cache |
| 03-03 | ~4 min | 2 | 9 | press script reproducibility: bundled fonts + pinned deps (parallel with 03-01) |
| 03-02 | ~5 min | 3 | 8 | portrait parity (1024×1024) + JSON Schema CI gate + active flag |
| Phase 04 P01 | 5min | 8 tasks | 8 files |
| Phase 04-structural P02 | 8min | 5 tasks | 13 files |
| Phase 04-structural P03 | 3min | 4 of 5 (T5 deferred) tasks | 5 files |

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table. Recent decisions affecting current work:

- Phase 1: GA gating uses script-load denial (not Consent Mode v2 default-deny) — required by the "zero requests" success criterion under UK PECR/ICO 2025-2026 guidance
- Phase 1: Press script repointing kept minimum-change to leave Phase 2's EMBARGO-02 source-of-truth question open
- Phase 1: Regenerated PDFs deliberately not committed — existing PDFs are the authoritative shipped artefacts
- Initialization: Bootstrap GSD over the existing brownfield site rather than rebuild
- Initialization: Organise active requirements by 4 delivery waves rather than 17 micro-phases
- Pre-init: Branch protection on `main` with `build` required, admin-enforced, 0 approvals — shipped before initialization
- Phase 2 Plan 01: Cron expressed in UTC with TZ: Europe/London on build env; DST drift accepted for 4x-daily cadence
- Phase 2 Plan 01: Embargo guard uses md.parts membership check (not substring) to prevent _incoming-prefix bypass
- Phase 2 Plan 04: Branded 404 inherits chrome via {{ define "main" }} + baseof.html block — never inline-call header/footer partials in layouts that already use baseof. Pattern reusable for any future Hugo special-path surface.
- Phase 2 Plan 04: 404 page is content (not analytics) — no hugo.IsProduction gate. Verified by running --environment development build, which produces an equivalent public/404.html.
- Phase 2 Plan 02: Tasks 1-2 (Formspree dashboard + hugo.toml params) pre-satisfied by commit 4dad5ce; executor proceeded without checkpoint pause despite plan's stale autonomous: false flag
- Phase 2 Plan 02: get-involved newsletter uses dark-section variant (text-white/90); homepage CTA newsletter uses light-surface variant (text-on-surface-variant); press signup uses light-surface — chosen by reading actual section background classes per PLAN.md rule, contradicting prompt instructions in 2 of 3 cases
- Phase 2 Plan 02: contact form's formspreeContactId resolves to 'mvzvgdbl' (legacy form repurposed as contact endpoint by maintainer); FORMS-03 satisfied by three distinct values (mvzvgdbl, xaqakgoy, myklvqwe) across the four forms
- Article hero templates wrap .Params.imageAlt in {{ with }} so missing values render alt="" (decorative) instead of falling back to the title — fulfils CONTEXT D-06.
- List/index range loops capture imageAlt into $pageImageAlt before entering {{ with .Params.image }} — required because the image with rebinds . to a string.
- Archetype kept as TOML per PATTERNS §6 option (a); corpus stays YAML.
- Phase 4 BUILD-01: Tailwind v4.2.4 standalone binary in CI (SHA-pinned cabeef04...bdec); Hugo Pipes serves fingerprinted /css/compiled.<sha>.css with integrity=sha256-... SRI; tokens relocated verbatim to assets/css/theme.css (47 MD3 colours, 3 fonts, 4 radii). No Node introduced.
- Phase 4 BUILD-01: @tailwindcss/typography deferred to v2 backlog as TYPOGRAPHY-01 — D-04 POC requires visual-baseline diff that auto-mode cannot perform; conservative defer preserves D-03 byte-identity contract.
- Phase 4 plan 02: Parser uses mgBulletList <ul> + mgExpiredMembershipEntry[A-Z] class filter (NOT <h3>Current appointments> heading) — Cornwall Council uses JS-toggled buttons + class-based hide on expired entries. Without the filter, stale roles like 'Audit Committee (Vice-Chair)' would ship to the public site.
- Phase 4 plan 02: ruamel.yaml round-trip uses width=4096 + indent(mapping=2, sequence=4, offset=2) — first cron run normalises top-level dash indentation as a one-time formatting PR; subsequent runs are byte-stable and produce no PR if no refreshable values changed (idempotency contract enforced by test_round_trip_is_idempotent).
- Phase 4 plan 02: Closes Phase 3 review WR-01 in same PR — actions/setup-python@v5 + pip install -r scripts/requirements.txt replaces the inline try/except ImportError + subprocess.run pip install pyyaml shim in hugo.yml. jsonschema and PyYAML now flow from the same pinned-deps file as the press toolchain.
- Phase 4 plan 02: Task 5 bootstrap (live workflow_dispatch + reviewable PR) deferred to operator per plan's checkpoint protocol — auto-mode does NOT auto-approve production-state operations (real PR creation, real GitHub Actions trigger). Documented in 04-02-SUMMARY.md 'Pending Operator Action'.
- Phase 4 plan 03 (CI safety nets): Lychee --offline + pa11y-ci WCAG2AA htmlcs against 5 canonical URLs + Dependabot (gha + pip /scripts) Mon 06:30 UTC. CLAUDE.md 'no Node' invariant preserved via npm install --no-save (no package.json). Hugo NOT tracked by Dependabot — manual quarterly bump in MAINTENANCE.md. Cron timing 06:00/06:30/07:00 UTC Mon — no collisions.
- Phase 4 plan 03 Task 5 (CI gate negative tests, autonomous: false): DEFERRED per checkpoint protocol — running negative tests requires real branches+PRs+CI consumption against the live repo (production-state operation). Same precedent as Plan 04-02 Task 5. Static config inspection confirms fail-on-error wiring (lychee fail: true; pa11y exit $PA11Y_EXIT). First real broken-link/a11y violation in a future PR will exercise the gates.

### Pending Todos

None — captured concerns live in `.planning/codebase/CONCERNS.md` and are mapped to requirements in `REQUIREMENTS.md`.

## Codebase Map

See: `.planning/codebase/` (mapped 2026-04-26)

- ARCHITECTURE.md, STRUCTURE.md — system shape
- STACK.md, INTEGRATIONS.md — tech stack and external services
- CONVENTIONS.md, TESTING.md — code and verification practices
- CONCERNS.md — 17 prioritised concerns (source for the active roadmap)

## Configuration

See: `.planning/config.json`

- Mode: YOLO (auto-approve at each step)
- Granularity: Coarse (4 phases)
- Parallelization: Plans run in parallel where independent
- Workflow agents: research + plan-check + verifier all enabled
- Model profile: Balanced (Sonnet for planning agents)

---
*State initialized: 2026-04-26*

**Planned Phase:** 04 (Structural) — 3 plans — 2026-04-26T22:48:37.885Z
**Shipped Phase:** 02 (operational-safety) — squashed merge `901af9d` (PR #9) — 2026-04-26
