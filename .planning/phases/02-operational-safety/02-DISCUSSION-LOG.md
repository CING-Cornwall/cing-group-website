# Phase 2: Operational safety - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-26
**Phase:** 02-operational-safety
**Areas discussed:** Embargo storage strategy, Newsletter GDPR consent copy, Article image alt-text mechanism, 404 page content & tone

---

## Embargo storage strategy

**Q1: Where should embargoed press release drafts live before their publishDate?**

| Option | Description | Selected |
|--------|-------------|----------|
| Keep in `_incoming/` only | Use existing `cascade.build.render: never`. Markdown source readable in `main`'s git history before embargo — solves display-time leak only. | ✓ |
| Use a separate `embargo` branch | Drafts on dedicated branch. Full leak prevention, more workflow overhead, cron on `main` won't see drafts until merge. | |
| Both: drafts on branch, `_incoming/` as transit | Maximum safety; most workflow steps. | |

**User's choice:** Keep in `_incoming/` only.
**Notes:** Resolves the internal contradiction in REQ EMBARGO-02 by softening the "git history" wording — threat model is display-time leak, not journalist-cloning-the-repo leak.

---

**Q2: Should CI actively guard against future-dated drafts in published folders?**

| Option | Description | Selected |
|--------|-------------|----------|
| Yes — fail the build (Recommended) | CI scans `content/press/**` excluding `_incoming/` and fails if any file has a future `publishDate`. | ✓ |
| No — trust the convention | Rely on maintainer discipline. | |

**User's choice:** Yes — fail the build (Recommended).
**Notes:** Catches the bypass case where someone puts a future-dated draft directly in `content/press/full-council-YYYY-MM-DD/` instead of `_incoming/`.

---

**Q3: What schedule should the GitHub Actions cron use?**

| Option | Description | Selected |
|--------|-------------|----------|
| `0 7,9,12,17 * * *` (Recommended) | 07:00, 09:00, 12:00, 17:00 Europe/London — weighted to morning press windows. | ✓ |
| `0 */6 * * *` | Every 6 hours UTC; misalignment with UK winter time. | |
| `0 8,12,17,21 * * *` | Better evening coverage; less morning weight. | |

**User's choice:** `0 7,9,12,17 * * *` (Recommended).
**Notes:** TZ already set to Europe/London on the workflow.

---

## Newsletter GDPR consent copy

**Q4: Which consent-tickbox label feels right for both newsletter forms?**

| Option | Description | Selected |
|--------|-------------|----------|
| Lean | "I agree to receive occasional email updates from CING. You can unsubscribe at any time. See our [privacy policy](/privacy/)." | ✓ |
| Specific | Names monthly cadence, news/statements/campaign topics, one-click unsubscribe. | |
| Plain & political | "Yes — keep me posted on what CING councillors are doing on Cornwall Council. Email only, no more than monthly. Unsubscribe any time." | |

**User's choice:** Lean.
**Notes:** Names controller (CING), unsubscribe right, privacy link — the three PECR-explicit-consent essentials in the shortest form.

---

**Q5: Should the press list form on `/press/` carry a different consent treatment?**

| Option | Description | Selected |
|--------|-------------|----------|
| Same template, adapted wording (Recommended) | Apply same explicit-opt-in pattern with press-appropriate copy. Consistent UX, defensible compliance. | ✓ |
| Lighter — implied consent for press | Treat as B2B/legitimate-interest list (no tickbox). Less defensible if challenged. | |
| Same as newsletter — copy and all | Use newsletter copy verbatim; "news updates" fits poorly for a press release distribution list. | |

**User's choice:** Same template, adapted wording.
**Notes:** Press list copy: "I'm a journalist or press contact and would like to receive CING press releases."

---

## Article image alt-text mechanism

**Q6: How should authors supply alt text for news/press article hero images?**

| Option | Description | Selected |
|--------|-------------|----------|
| `imageAlt:` front-matter field, fallback to empty (Recommended) | Authors fill in the field; missing means `alt=""` (decorative). Forces opt-in to descriptive alt; prevents silent regression to title-duplication. | ✓ |
| `imageAlt:` field, fallback to title | Backward compatible; missing falls back to title, re-introducing duplication risk. | |
| `imageAlt:` field, required — build fails if missing | Strictest; explicit `imageAlt: ""` required for decorative. | |

**User's choice:** `imageAlt:` front-matter field, fallback to empty (Recommended).
**Notes:** Better silent failure mode — empty alt is the lesser evil compared to duplicating headlines.

---

**Q7: Should we backfill alt text for existing posts now or just enable the mechanism?**

| Option | Description | Selected |
|--------|-------------|----------|
| Backfill all 8 now (Recommended) | Write content-equivalent alt for each existing post's hero this phase. | ✓ |
| Just the mechanism — backfill on next edit | Lighter scope; existing posts get fallback until next edited. | |
| Backfill heroes that depict people/events; skip abstract heroes | Selective backfill. | |

**User's choice:** Backfill all 8 now.
**Notes:** 3 news posts + 5 press releases under `content/press/full-council-2026-04-21/`.

---

## 404 page content & tone

**Q8: What should the branded 404 page contain?** (multi-select)

| Option | Description | Selected |
|--------|-------------|----------|
| Header + footer + apology + nav choice (Recommended) | Standard CING shell, brief message, three CTAs to /, /news/, /councillors/. | ✓ |
| Search-the-site box | Requires implementing client-side search — scope creep. | |
| Recent news teaser | Helps stale-link visitors. | |
| Manifesto / what is CING blurb | Re-introduces the group for visitors arriving from social. | |

**User's choice:** Header + footer + apology + nav choice (Recommended) — only.
**Notes:** Search, news teaser, and intro blurb deferred to future phases.

---

**Q9: What tone should the 404 carry?**

| Option | Description | Selected |
|--------|-------------|----------|
| Branded confident — Cornish flavour (Recommended) | "This page has wandered off the map. Try one of these." | ✓ |
| Neutral apologetic | "Sorry, we can't find that page." Standard, anonymous. | |
| Deadpan / minimal | "404 — not found." Risk: feels generic against the rest of the site. | |

**User's choice:** Branded confident — Cornish flavour.
**Notes:** Executor picks exact wording within this register.

---

## Claude's Discretion

The user explicitly delegated these mechanical items to Claude:
- FORMS-01 honeypot wiring (4 forms × hidden `_gotcha` input)
- FORMS-03 Formspree-endpoint-split naming convention (`formspreeContactId/NewsletterId/PressId`)
- A11Y-01 decorative full-bleed hero alt-text fix (6 layout files)
- 404 page exact wording within the chosen tone band
- CI guard implementation language (shell, Python, or Hugo shortcode — fit `hugo.yml` cleanly)
- Cron job structural placement (extend `hugo.yml` triggers vs new workflow file — chose extend)

## Deferred Ideas

- Site search on 404 page (scope creep — needs Lunr/Pagefind)
- Recent-news teaser on 404 (small enhancement; later iteration)
- Captcha on forms (defer until honeypot proves insufficient)
- Switch newsletter to a real ESP (vendor change beyond Phase 2 scope)
- Embargo via separate `embargo` branch (full git-history leak prevention; reconsider if needed)
- Required-`imageAlt:` build failure (strictest mechanism; deferred in favour of empty-fallback)
- markdownlint pre-commit hook (CI/tooling concern for a later phase)
