# Phase 2: Operational safety - Context

**Gathered:** 2026-04-26
**Status:** Ready for planning

<domain>
## Phase Boundary

Close the operational gates that protect editorial integrity (embargo safety) and legal posture (form consent, accessibility). After this phase:
- An embargoed press release cannot accidentally appear early on `www.cingparty.uk`.
- Marketing emails carry recorded GDPR consent.
- The site survives a basic accessibility audit on hero-image alt-text.
- A 404 hit renders branded CING chrome, not GitHub's default error.

**In scope (8 REQ-IDs):** EMBARGO-02, EMBARGO-03, FORMS-01, FORMS-02, FORMS-03, A11Y-01, A11Y-02, A11Y-03.

**Not in this phase (deferred to Wave 3+):** Image optimisation pipeline (IMG-01..04), councillor data validation/refresh (DATA-01..03), Tailwind build-time compile (BUILD-01), accessibility CI scans (CI-02). The alt-text work here is *content-correctness only* — wiring pa11y-ci is Phase 4.

</domain>

<decisions>
## Implementation Decisions

### Embargo storage & safeguards (EMBARGO-02, EMBARGO-03)

- **D-01:** Embargoed drafts live in `content/press/_incoming/<slug>.md` using the existing `cascade.build.render: never` mechanism. The threat model is *display-time leak* only — markdown source readability in `main`'s git history is acceptable for this phase. This softens REQ EMBARGO-02's literal "or in main's git history" clause; downstream agents should read REQ EMBARGO-02 as "drafts are not *rendered* on `main`."
- **D-02:** Add a CI guard that scans `content/press/**` excluding `_incoming/` and fails the build if any file has a `publishDate` in the future. This prevents the bypass case where someone puts a future-dated draft directly in `content/press/full-council-YYYY-MM-DD/`. Implementation can be a small shell/Python step in `hugo.yml` before `hugo build`.
- **D-03:** GitHub Actions cron schedule: `0 7,9,12,17 * * *` with `TZ: Europe/London` (already set on the workflow). Four rebuilds daily — 07:00, 09:00, 12:00, 17:00 — weighted to UK morning press windows. The cron must trigger the same `build → deploy` jobs as the existing push trigger (no separate workflow file).

### Form compliance (FORMS-01, FORMS-02, FORMS-03)

- **D-04:** Both newsletter forms (`layouts/get-involved/list.html` newsletter section, `layouts/index.html` homepage newsletter) use this opt-in label verbatim:
  > I agree to receive occasional email updates from CING. You can unsubscribe at any time. See our [privacy policy](/privacy/).

  Implemented as `<input type="checkbox" name="marketing_consent" required>` with the label text including a markdown-rendered link to `/privacy/`. The checkbox is unticked by default (PECR explicit-consent rule).
- **D-05:** The press list form on `/press/` carries the same explicit-opt-in pattern with adapted wording:
  > I'm a journalist or press contact and would like to receive CING press releases.

  Same `required` checkbox mechanism; same privacy-policy link convention.
- **Claude's discretion (FORMS-01 honeypot):** Add `<input type="text" name="_gotcha" style="display:none" tabindex="-1" autocomplete="off">` to all four Formspree-backed forms. The four forms are at `layouts/get-involved/list.html:108` (contact), `:155` (newsletter), `layouts/index.html:205` (homepage newsletter), `layouts/press/list.html:147` (press list).
- **Claude's discretion (FORMS-03 endpoint split):** Three Formspree endpoints, IDs stored as `params.formspreeContactId`, `params.formspreeNewsletterId`, `params.formspreePressId` in `hugo.toml`. Forms map: contact form → contact ID; both newsletter forms → newsletter ID; press list → press ID. **Manual prerequisite:** the maintainer must create the three new forms in the Formspree dashboard and copy the new IDs into `hugo.toml` before merge. The plan should surface this as a non-autonomous task. The legacy `params.formspreeId` may stay as an alias for the contact form during the migration if useful, but the four `<form action>` attributes must reference the new params after the change.

### Accessibility — alt text (A11Y-01, A11Y-02)

- **D-06:** News and press article hero-image alt text is supplied via a new `imageAlt:` front-matter field on each post. Templates emit `alt="{{ .Params.imageAlt }}"` if the field is set; if missing, fall back to `alt=""` (treat as decorative — *not* the title). This forces authors to opt in to descriptive alt text and prevents silent regression to title-duplication. Update the news archetype (`archetypes/default.md` and any press-specific archetype if it exists) to include `imageAlt: ""` as a stub with a comment instructing the author to fill it in.
- **D-07:** Backfill all 8 existing posts' `imageAlt:` field this phase: 3 news posts (`community-engagement-events.md`, `spring-council-session-update.md`, `welcome-to-our-new-website.md`) and 5 press releases under `content/press/full-council-2026-04-21/`. Alt text should describe what the image *shows* (e.g., "A child at a dental check-up" for the NHS dental release), not the headline.
- **Claude's discretion (A11Y-01 decorative heroes):** For full-bleed decorative hero images, set `alt=""` and add `role="presentation"`. Affected templates per CONCERNS.md: `layouts/index.html:11`, `layouts/about/list.html:7`, `layouts/get-involved/list.html:25-27`, `layouts/policies/policies.html:6`, `layouts/councillors/list.html:7`, `layouts/press/list.html:7`. Verify each one is genuinely decorative (full-bleed background, not communicating content) before applying.

### Branded 404 (A11Y-03)

- **D-08:** `layouts/404.html` contains: standard CING header partial (`{{ partial "header.html" . }}`), brief apology message, three primary CTAs to `/`, `/news/`, `/councillors/`, and the standard footer partial. No search box, no recent-news teaser, no group-introduction blurb — those would be scope creep or belong on a different surface.
- **D-09:** 404 tone: branded confident with Cornish flavour. Example register (executor picks exact wording, but stay in this band): *"This page has wandered off the map. Try one of these."* Avoid generic "Sorry, page not found" and avoid deadpan "404". The voice should be consistent with the rest of the site's political confidence.

### Claude's Discretion (summary)

- FORMS-01 honeypot mechanics (D above)
- FORMS-03 endpoint split mechanics (D above)
- A11Y-01 decorative-hero alt fix (D above)
- 404 page exact wording within the tone band (D-09)
- CI guard implementation language (Hugo shortcode-based check, shell `find + awk`, or small Python script — pick what fits `hugo.yml` cleanly)
- Cron job: implement as a `schedule:` trigger on the existing `hugo.yml` workflow rather than a separate file (preserves single-workflow conventions).

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope & requirements
- `.planning/ROADMAP.md` §"Phase 2: Operational safety" — phase goal, success criteria, requirement IDs
- `.planning/REQUIREMENTS.md` §"Embargo & press toolchain", §"Forms", §"Accessibility" — full text of REQ-IDs EMBARGO-02/03, FORMS-01/02/03, A11Y-01/02/03
- `.planning/codebase/CONCERNS.md` §HIGH ("Embargo workflow has no automated safeguard"), §MEDIUM ("Forms have no spam protection and no GDPR consent ticks", "All four forms share one Formspree endpoint", "Alt text on hero images is decorative-as-content", "No 404 page") — the source-of-truth analysis for why each requirement exists, including specific file paths and line numbers

### Codebase context
- `.planning/codebase/INTEGRATIONS.md` §"APIs & External Services" → Formspree, §"CI/CD & Deployment" → GitHub Actions, §"Cookie Consent" — current integration shape including form-action URLs and workflow trigger config
- `.planning/codebase/STRUCTURE.md` §"Layouts Directory Breakdown", §"Content Directory Breakdown" — file inventory for the templates and posts being modified
- `.planning/codebase/CONVENTIONS.md` — code patterns and conventions (referenced by all phases)

### Project standards
- `CLAUDE.md` — project guidance, especially §"Architecture", §"Forms", §"News content"
- `.planning/PROJECT.md` §"Constraints" — UK GDPR/PECR compliance, performance budget, single-maintainer reality

### Brand standards (for 404 page)
- `docs/brand/DESIGN.md` — master design system "Kernow Horizon"; canonical authority for visual decisions
- `docs/brand/colours.md` — MD3 colour token reference
- `docs/brand/typography.md` — Manrope (`font-headline`) and Public Sans (`font-body` / `font-label`) usage
- `docs/brand/design-principles.md` — layout rules, component patterns, Tailwind conventions; used to keep the 404 visually consistent with the rest of the site

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- **`content/press/_incoming/_index.md`** — cascade `build.render: never` already configured. EMBARGO-02 implementation is a workflow convention shift, not a new mechanism.
- **`layouts/_default/baseof.html`** — base shell with Tailwind config, MD3 tokens, fonts, header/footer partials. The 404 layout inherits from this via `{{ define "main" }}`.
- **`layouts/partials/header.html` (123 lines), `layouts/partials/footer.html` (52 lines)** — drop into 404 for branded chrome. No new partials needed.
- **`.github/workflows/hugo.yml`** — single workflow. Add `schedule:` next to `push` and `workflow_dispatch` triggers; no new workflow file needed.
- **`hugo.toml`** — `params.formspreeId = "mvzvgdbl"` lives at line ~8; the FORMS-03 split adds two more keys alongside.
- **`archetypes/default.md`** — base archetype; extending with `imageAlt: ""` propagates to all `hugo new` invocations. A press-specific archetype may also exist; check `archetypes/` directory before assuming.

### Established Patterns

- **Form action URL pattern:** `<form action="https://formspree.io/f/{{ .Site.Params.formspreeId }}" method="POST">`. Replicate per-form with the new endpoint params.
- **Production-only gating:** GA + cookie banner are wrapped in `{{ if hugo.IsProduction }}`. The 404 page does NOT need this gate — it's content, not analytics.
- **Layout file convention:** `layouts/<section>/list.html` for section indexes; `layouts/404.html` (no subdirectory) is the Hugo-special path for the error page.
- **Cookie consent storage:** `localStorage['cing-cookies'] === 'accepted'|'rejected'`. Form work does NOT need to interact with this; the consent checkbox is form-local, not session-wide.

### Integration Points

- **Embargo storage** connects to: existing `_incoming/` cascade + `scripts/generate_press_pdfs.py` (already repointed to live source paths in Phase 1, so press script regeneration is unaffected by this phase).
- **Cron trigger** connects to: existing `build` job in `hugo.yml`. Verify branch protection's required `build` status check still satisfies cron-triggered runs (it should — same job name).
- **Formspree endpoint split** connects to: maintainer's Formspree dashboard. The plan must include a step where the maintainer creates the three forms manually and provides their IDs; downstream tasks block until those IDs are in `hugo.toml`.
- **404 page** connects to: GitHub Pages — Hugo emits `public/404.html`, GH Pages serves it automatically on any 404. No GitHub Pages config change needed.

</code_context>

<specifics>
## Specific Ideas

- **404 example copy:** "This page has wandered off the map. Try one of these." — illustrative register; the executor may choose alternative wording in the same band (branded confident, light Cornish flavour, not gimmicky).
- **CI guard logic:** for each `*.md` under `content/press/**` excluding `content/press/_incoming/**`, parse the `publishDate:` front-matter field; fail if it's later than the build's current time. A 10-line shell/awk step in `hugo.yml` is sufficient — no new tool.
- **PECR compliance precedent:** Phase 1's GA gating uses script-load denial (not Consent Mode v2 default-deny). This phase's form-consent work should follow the same "explicit positive action required" stance — pre-ticked boxes are forbidden, "by submitting you agree" is forbidden.
- **Alt-text examples to mirror:** for the 5 press releases on 2026-04-21 — children's dental → "A child at a dental check-up"; glyphosate → "A worker spraying weedkiller at a roadside"; etc. Concrete imagery, not abstract.

</specifics>

<deferred>
## Deferred Ideas

- **Site search on 404 page** — would help stale-link recovery but requires Lunr/Pagefind integration. Belongs in a future phase, not Phase 2.
- **Recent-news teaser on 404** — small enhancement; can be added in a later iteration without re-planning the whole page.
- **Captcha on forms (vs honeypot)** — honeypot is sufficient at current traffic; captcha (hCaptcha/Turnstile) only needed if honeypot proves insufficient. Defer until evidence of bypass.
- **Switch newsletter to a real ESP** (Buttondown / MailerLite) — CONCERNS.md §"All four forms share one Formspree endpoint" suggests this; deferred because it's a vendor change beyond the operational-safety phase scope.
- **Embargo via separate `embargo` branch** — full git-history leak prevention. Reconsider in a future phase if a journalist surfacing a pre-embargo draft becomes a real risk.
- **Required-`imageAlt:` build failure** — strictest mechanism; deferred in favour of empty-fallback. Reconsider if title-duplication regressions appear.
- **markdownlint pre-commit hook** — CONCERNS suggested this for the privacy-page malformed headings; Phase 1 fixed the symptom, the hook itself is a CI/tooling concern for a later phase.

</deferred>

---

*Phase: 02-operational-safety*
*Context gathered: 2026-04-26*
