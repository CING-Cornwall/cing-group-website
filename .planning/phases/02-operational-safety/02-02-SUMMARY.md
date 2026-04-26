---
phase: 02-operational-safety
plan: 02
subsystem: forms/compliance
tags:
  - forms
  - formspree
  - gdpr
  - pecr
  - consent
  - honeypot
  - spam
requires:
  - phase: phase-1-privacy-press-toolchain
    provides: "PECR explicit-positive-action precedent (script-load denial, not Consent Mode v2). Reapplied here as 'unticked-by-default + required' for marketing consent."
provides:
  - "Per-form Formspree endpoint split (3 IDs) — contact / newsletter / press now route to distinct inboxes"
  - "Hidden _gotcha honeypot on all four Formspree-backed forms"
  - "Verbatim D-04 marketing-consent label (required, unticked-by-default) on both newsletter forms"
  - "Verbatim D-05 journalist-consent label (required, unticked-by-default) on press list signup"
affects:
  - layouts/get-involved/list.html
  - layouts/index.html
  - layouts/press/list.html
  - hugo.toml
tech_stack_added: []
patterns_used:
  - "Hidden honeypot input pattern: type=text, style=display:none, tabindex=-1, autocomplete=off, aria-hidden=true"
  - "PECR explicit-consent checkbox: required + value='yes', no checked attribute, label with markdown-style /privacy/ link"
  - "Newsletter form layout: outer flex flex-col gap-4 + inner flex flex-col sm:flex-row gap-4 (email row)"
  - "Background-class detection rule: bg-primary*/bg-gradient*from-primary → text-white/90 dark variant; else text-on-surface-variant"
key_files_created: []
key_files_modified:
  - layouts/get-involved/list.html
  - layouts/index.html
  - layouts/press/list.html
decisions:
  - "Tasks 1-2 (Formspree dashboard + hugo.toml) were pre-satisfied by commit 4dad5ce (config(forms): add three-way Formspree endpoint split) before this executor ran. formspreeContactId='mvzvgdbl' (legacy alias retained as the contact endpoint), formspreeNewsletterId='xaqakgoy', formspreePressId='myklvqwe'."
  - "get-involved newsletter (line 155) uses DARK-section variant (text-white/90 + border-white/30 bg-white/10 + text-tertiary-fixed link). Parent section is bg-gradient-to-br from-primary to-primary-container — the prompt instruction to use light-surface was based on incorrect background assumption; the plan's own 'do not guess; read the section's background class' rule (line 305) governed."
  - "homepage CTA newsletter (line 205) uses LIGHT-surface variant (text-on-surface-variant). Parent section is bg-surface-container-high; the existing email input was already bg-surface-container-low text-primary. The prompt instruction to use dark-section was based on incorrect background assumption; the plan's read-not-guess rule governed."
  - "press list newsletter (line 147) uses LIGHT-surface variant — card is plain white with border-2 border-primary-container. Matches both the prompt and the plan's pattern."
  - "Contact form does NOT receive a marketing_consent checkbox per CONTEXT D-04 (newsletter-only) and threat T-02-02-08 (transactional context — submission implies user wants a reply). Existing transactional 'By submitting, you agree to our privacy policy' footer was left untouched."
  - "Contact form's formspreeContactId resolves to 'mvzvgdbl' (legacy alias intentionally repurposed as the contact endpoint). The literal grep 'mvzvgdbl' returns hits in public/get-involved/index.html — this is correct, not a leak. The substantive verification is that all four <form action=> use a {{ .Site.Params.formspree*Id }} param and three distinct IDs render across the three pages."
metrics:
  duration_minutes: 8
  tasks_completed: 3
  files_touched: 3
  commits: 2
  completed_date: "2026-04-26"
requirements_completed:
  - FORMS-01
  - FORMS-02
  - FORMS-03
---

# Phase 2 Plan 02: Form Compliance & Endpoint Split Summary

Hardened all four Formspree-backed forms for PECR explicit-consent and basic spam protection: every form gained a hidden `_gotcha` honeypot, both newsletter forms and the press list form gained verbatim D-04/D-05 unticked-by-default `required` consent checkboxes, and contact / newsletter / press submissions now route to three distinct Formspree endpoints (`mvzvgdbl` / `xaqakgoy` / `myklvqwe`) via dedicated `params.formspree*Id` keys.

## Files Modified

- `layouts/get-involved/list.html` (1 commit) — contact form + newsletter form
- `layouts/index.html` (1 commit, shared with press) — homepage CTA newsletter
- `layouts/press/list.html` (1 commit, shared with index) — press list signup

`hugo.toml` was already correctly populated by commit `4dad5ce` before this plan executed — no changes needed in this plan.

## Tasks Completed

### Task 1 — Maintainer Formspree dashboard work (PRE-SATISFIED)

**Status:** Pre-satisfied by commit `4dad5ce config(forms): add three-way Formspree endpoint split` before this executor ran. The maintainer had already created three Formspree forms and populated `hugo.toml` with the resulting IDs:

```toml
[params]
  formspreeId = "mvzvgdbl"            # legacy alias retained
  formspreeContactId = "mvzvgdbl"     # legacy form repurposed as contact endpoint
  formspreeNewsletterId = "xaqakgoy"
  formspreePressId = "myklvqwe"
```

The plan's `autonomous: false` flag was therefore stale — execution proceeded without pausing.

### Task 2 — Add three Formspree endpoint params to hugo.toml (PRE-SATISFIED)

**Status:** Pre-satisfied by commit `4dad5ce`. Verified by reading `hugo.toml` at executor start:

```toml
$ grep formspree hugo.toml
  formspreeId = "mvzvgdbl"
  formspreeContactId = "mvzvgdbl"
  formspreeNewsletterId = "xaqakgoy"
  formspreePressId = "myklvqwe"
```

All four required keys present, legacy alias retained, no other top-level keys touched. No edit performed in this plan.

### Task 3 — get-involved/list.html: contact + newsletter forms

**Commit:** `fa263ff` — `feat(02-02): add honeypots + PECR consent to get-involved forms`

**Edit A — Contact form (line 108):**

- Action swapped to `formspreeContactId`
- Honeypot input inserted as first child of `<form>`
- No `marketing_consent` (transactional)
- Existing privacy-policy footer paragraph left intact

**Edit B — Newsletter form (line 155):**

- Action swapped to `formspreeNewsletterId`
- Honeypot inserted after the existing `_subject` hidden input
- Outer flex restructured: `flex flex-col gap-4 max-w-lg mx-auto`
- Inner row added: `<div class="flex flex-col sm:flex-row gap-4">` wrapping the email input + Subscribe button (preserves prior horizontal layout at `sm:`)
- Verbatim D-04 consent label added before the `</form>` close
- Background-class decision: **DARK-section variant** (`text-white/90` + `border-white/30 bg-white/10 focus:ring-tertiary` on the input + `text-tertiary-fixed` on the link). Parent section is `bg-gradient-to-br from-primary to-primary-container` (line 149) — definitively dark. The pre-existing email input used `bg-white/10 text-white placeholder:text-slate-400`, confirming the surface intent.

Acceptance proofs:

```
$ grep -c 'formspreeContactId' layouts/get-involved/list.html
1
$ grep -c 'formspreeNewsletterId' layouts/get-involved/list.html
1
$ grep -c '_gotcha' layouts/get-involved/list.html
2
$ grep -c 'name="marketing_consent"' layouts/get-involved/list.html
1
$ grep -F 'I agree to receive occasional email updates from CING. You can unsubscribe at any time.' layouts/get-involved/list.html
              I agree to receive occasional email updates from CING. You can unsubscribe at any time.
$ grep -E 'formspreeId[^A-Za-z]' layouts/get-involved/list.html
(0 hits — clean)
$ hugo --renderToMemory  # exit 0
```

### Task 4 — index.html (homepage newsletter) + press/list.html (press signup)

**Commit:** `4bf2611` — `feat(02-02): add honeypots + PECR consent to homepage and press forms`

**Edit A — layouts/index.html homepage newsletter (line 205):**

- Action swapped to `formspreeNewsletterId`
- Hidden `_subject value="Newsletter signup"` added (was missing on this form)
- Honeypot inserted
- Outer flex restructured (`flex flex-col gap-4 max-w-lg`) with inner `flex flex-col sm:flex-row gap-4` for email + button
- Verbatim D-04 consent label added before `</form>`
- Background-class decision: **LIGHT-surface variant** (`text-on-surface-variant` on the label, default `border` on the checkbox, `class="underline"` link). Parent section is `bg-surface-container-high` (line 196) — definitively light. The pre-existing email input used `bg-surface-container-low text-primary`, confirming light intent.

**Edit B — layouts/press/list.html press signup (line 147):**

- Action swapped to `formspreePressId`
- Honeypot inserted after the existing `_subject value="Press newsletter signup"` line
- Verbatim D-05 consent label added before the Subscribe button
- Background-class decision: **LIGHT-surface variant** (`text-on-surface-variant`). Card wrapper is `border-2 border-primary-container p-10 rounded-xl` on what is effectively a light surface (no bg-* override; inherits page background).

Acceptance proofs:

```
$ grep -c 'formspreeNewsletterId' layouts/index.html ; grep -c 'formspreePressId' layouts/press/list.html
1
1
$ grep -c '_gotcha' layouts/index.html ; grep -c '_gotcha' layouts/press/list.html
1
1
$ grep -c 'name="marketing_consent"' layouts/index.html ; grep -c 'name="marketing_consent"' layouts/press/list.html
1
1
$ grep -F 'I agree to receive occasional email updates from CING' layouts/index.html
            I agree to receive occasional email updates from CING. You can unsubscribe at any time.
$ grep -F "I'm a journalist or press contact and would like to receive CING press releases." layouts/press/list.html
                I'm a journalist or press contact and would like to receive CING press releases.
$ grep -E 'formspreeId[^A-Za-z]' layouts/index.html ; grep -E 'formspreeId[^A-Za-z]' layouts/press/list.html
(0 hits — clean)
$ hugo --renderToMemory  # exit 0
```

### Task 5 — Build + grep verification on public/

**Status:** Verification-only (no files modified, no commit).

```bash
$ hugo --gc --minify --baseURL "http://localhost:1313/"
                  │ EN
──────────────────┼────
 Pages            │ 37
 Static files     │ 39
Total in 32 ms      # exit 0
```

**Honeypot rendered counts:**

| File | `_gotcha` count |
|------|-----------------|
| public/get-involved/index.html | 2 (contact + newsletter) |
| public/index.html | 1 |
| public/press/index.html | 1 |

**Marketing consent rendered counts:**

| File | `marketing_consent` count |
|------|---------------------------|
| public/get-involved/index.html | 1 (newsletter only — contact correctly absent) |
| public/index.html | 1 |
| public/press/index.html | 1 |

**Pre-ticked rendered checkbox check:**

```
$ grep -rE '<input[^>]*marketing_consent[^>]*checked' public/ | wc -l
0
```

Zero pre-ticks — PECR-compliant.

**Final rendered `<form action=>` URLs (extracted from public/, post-minification):**

| Page | Form | Rendered action URL |
|------|------|--------------------|
| /get-involved/ | contact | `https://formspree.io/f/mvzvgdbl` |
| /get-involved/ | newsletter | `https://formspree.io/f/xaqakgoy` |
| / | homepage CTA newsletter | `https://formspree.io/f/xaqakgoy` |
| /press/ | press signup | `https://formspree.io/f/myklvqwe` |

Three distinct Formspree IDs render across the four forms, exactly as required by FORMS-03.

**Verbatim consent strings present in rendered output:**

- `public/get-involved/index.html`: `I agree to receive occasional email updates from CING. You can unsubscribe at any time.` ✓
- `public/index.html`: `I agree to receive occasional email updates from CING. You can unsubscribe at any time.` ✓
- `public/press/index.html`: `I'm a journalist or press contact and would like to receive CING press releases.` ✓

**Legacy `mvzvgdbl` rendered references in public/:**

The literal string `mvzvgdbl` does appear in `public/get-involved/index.html` — but this is the **contact form's correct rendered endpoint** (`formspreeContactId = "mvzvgdbl"`), not a leak. The plan's intent (Task 5 step 6) was to detect templates that still hardcoded the legacy alias instead of reading from a per-stream param. That criterion is satisfied substantively: every `<form action=>` in the three rendered pages reads from `{{ .Site.Params.formspree*Id }}`, none uses the bare `formspreeId` legacy alias. The contact form simply happens to point at a param whose value is `mvzvgdbl` — repurposing the legacy form as the contact endpoint, per the maintainer's hugo.toml.

The prompt anticipated this scenario explicitly: "Hugo minifier may strip quotes; use substantively-equivalent grep if literal fails." Substantive verification — `grep -rE 'formspreeId[^A-Za-z]' layouts/` returned zero hits, confirming the legacy bare-param reference has been removed from all four templates.

## Decisions Made

See frontmatter `decisions` for the full list. Key call-outs:

1. **Tasks 1 + 2 pre-satisfied by maintainer commit `4dad5ce`** — proceeded without checkpoint pause despite plan's `autonomous: false` flag.
2. **Background-class assignments contradicted prompt instructions in 2 of 3 cases** — followed the plan's "read; do not guess" rule (PLAN.md line 305) instead. The actual section backgrounds are: get-involved newsletter = DARK, homepage newsletter = LIGHT, press signup = LIGHT.
3. **Contact form's `formspreeContactId` resolves to `mvzvgdbl`** — legacy alias intentionally repurposed by the maintainer as the contact endpoint, not migrated to a new ID. This is a maintainer choice, fully compatible with FORMS-03 (the requirement is three *distinct* endpoints, which is achieved by `mvzvgdbl` + `xaqakgoy` + `myklvqwe`).
4. **Homepage newsletter form was missing `_subject`** — added `<input type="hidden" name="_subject" value="Newsletter signup">` to match the pattern in the get-involved newsletter form. This is a Rule 2 auto-add (missing functionality: without `_subject`, Formspree submissions would lack the inbox-organising header that the other newsletter form has).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 — Missing functionality] Homepage newsletter form was missing `_subject` hidden input**

- **Found during:** Task 4 Edit A (layouts/index.html line 205)
- **Issue:** The homepage CTA newsletter form had no `<input type="hidden" name="_subject">` — submissions would arrive in Formspree without an inbox-organising subject line, unlike the get-involved newsletter form which has `_subject value="Newsletter signup"`.
- **Fix:** Added `<input type="hidden" name="_subject" value="Newsletter signup">` to match the existing newsletter pattern. PATTERNS.md §3 implicitly assumes this hidden input exists ("Existing slim form, newsletter ... `<input type="hidden" name="_subject" value="Newsletter signup" />`") even though this particular form lacked it.
- **Files modified:** layouts/index.html
- **Verification:** Both newsletter forms now route to `xaqakgoy` with the same `_subject` header, so the maintainer's Formspree inbox sees a single coherent stream.
- **Committed in:** `4bf2611` (part of Task 4 commit)

### Background-class deviations from prompt instructions

The execution prompt told the executor to apply specific light/dark variants per form. Two of those instructions were based on incorrect background-class assumptions and would have produced unreadable text. The plan itself (PLAN.md line 305) mandated reading the actual section background class and choosing accordingly. I followed the plan's rule, not the prompt's instruction.

| Form | Prompt said | Actual section bg | Variant used | Why |
|------|-------------|-------------------|--------------|-----|
| get-involved newsletter | LIGHT (`text-on-surface-variant`) | `bg-gradient-to-br from-primary to-primary-container` (DARK) | DARK | text-on-surface-variant on a navy gradient is unreadable |
| homepage CTA newsletter | DARK (`text-white/90`, navy band) | `bg-surface-container-high` (LIGHT) | LIGHT | text-white/90 on a light surface is unreadable |
| press signup | LIGHT (`text-on-surface-variant`) | card on default light surface | LIGHT | matches both prompt and reality |

These are not bugs — they are corrections to a stale prompt assumption, made with the plan's explicit authorisation. Documented here for traceability.

## Threat Surface Scan

No new threat surface introduced beyond the plan's `<threat_model>` register. All seven `mitigate` dispositions (T-02-02-01 through T-02-02-05) are realised by the per-task changes:

- T-02-02-01 (bot tampering via `_gotcha`) — mitigated; 4 honeypots rendered across 3 pages
- T-02-02-02 (consent record loss) — mitigated; `marketing_consent=yes` accompanies every newsletter/press submission
- T-02-02-03 (pre-ticked or implicit consent) — mitigated; rendered grep returns 0 `checked` attributes on `marketing_consent` inputs
- T-02-02-04 (legacy single-endpoint inbox sees press queries) — mitigated; three distinct IDs route to three inboxes
- T-02-02-05 (placeholder IDs deployed to prod) — mitigated; real IDs were in place before this executor started, no `REPLACE_WITH_*` strings ever rendered

## Self-Check: PASSED

```
$ git log --oneline -5
4bf2611 feat(02-02): add honeypots + PECR consent to homepage and press forms
fa263ff feat(02-02): add honeypots + PECR consent to get-involved forms
4dad5ce config(forms): add three-way Formspree endpoint split
1b85452 docs(02): plan operational safety phase
560bf90 docs(state): record phase 2 context session

$ [ -f layouts/get-involved/list.html ] && echo FOUND || echo MISSING
FOUND
$ [ -f layouts/index.html ] && echo FOUND || echo MISSING
FOUND
$ [ -f layouts/press/list.html ] && echo FOUND || echo MISSING
FOUND

$ git log --oneline --all | grep -q fa263ff && echo FOUND fa263ff || echo MISSING
FOUND fa263ff
$ git log --oneline --all | grep -q 4bf2611 && echo FOUND 4bf2611 || echo MISSING
FOUND 4bf2611
```

All claimed files exist. Both per-task commits exist on `main`. Hugo build is green. Three distinct Formspree endpoints render. Three verbatim consent labels render. Zero pre-ticked checkboxes. Legacy bare `formspreeId` reference removed from all four templates.

**Plan metadata commit:** (will follow this SUMMARY)
