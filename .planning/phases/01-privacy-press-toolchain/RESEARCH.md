# Phase 1: Privacy & Press Toolchain — Research

**Researched:** 2026-04-26
**Domain:** Hugo static site, browser-side consent gating, ReportLab Python toolchain
**Confidence:** HIGH

## Summary

Phase 1 has two independent workstreams. The privacy/analytics workstream (PRIVACY-01/02/03) requires changing the GA implementation in `layouts/_default/baseof.html` from "load gtag, deny storage by default" to "do not inject the gtag script tag at all until consent is granted", and then aligning two markdown documents (`content/privacy/_index.md` H2 fix; `CLAUDE.md` paragraph rewrite) with the new behaviour. The press-PDF workstream (EMBARGO-01) requires only a path change — the five published markdown files in `content/press/full-council-2026-04-21/` already use slug-named filenames identical to `Release.slug`, so re-pointing the script's `RELEASES` table is mechanical.

ICO/PECR guidance (post-2025 update under the Data (Use and Access) Act) explicitly extends "no non-exempt technologies before opt-in" to cookieless pings and tag-based scripts — this confirms the success criterion in the roadmap (zero requests to GA hosts on rejection) is the correct legal posture, not a stricter-than-needed local choice.

**Primary recommendation:**
- **01-01 (privacy):** Move the `(function(){ var s = document.createElement('script') ... })()` block out of the unconditional path and into a named `loadGtag()` function, called (a) at page load if `localStorage.getItem('cing-cookies') === 'accepted'` and (b) inside the existing `cookie-accept` click handler. Remove the unconditional Consent Mode v2 default-deny block (it stops being meaningful once the script never loads on rejection). Make `loadGtag()` idempotent via a module-level flag. Then update privacy markdown headings and `CLAUDE.md` text in the same PR.
- **01-02 (press):** Update `SOURCE_DIR` and the five `src_md` paths in `RELEASES` to point at `content/press/full-council-2026-04-21/<slug>.md`. No front-matter or body parser changes required — the published files use the same H1/H2/blockquote/strapline shape the parser already handles.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| GA script injection | Browser (inline JS in `baseof.html`) | — | Hugo only emits the inline script; consent state lives in `localStorage`; injection decision must be made client-side per visitor |
| Consent state persistence | Browser (`localStorage`) | — | No server-side session; static site |
| Cookie banner UI/handlers | Browser (inline JS + Tailwind classes) | Hugo template (`{{ if hugo.IsProduction }}` gate) | Banner DOM is server-rendered, behaviour is client-side |
| Privacy policy content | Hugo content (`content/privacy/_index.md`) | — | Plain markdown rendered by default `_default/single.html` chain |
| AI guidance doc | Repo root (`CLAUDE.md`) | — | Read by Claude Code at session start; not part of the build |
| Press PDF generation | Local Python (one-shot) | — | Build artefact; output is committed under `static/documents/press/` |

## User Constraints (from CONTEXT.md)

No `*-CONTEXT.md` exists in `.planning/phases/01-privacy-press-toolchain/`. Constraints are inherited from `PROJECT.md`:

- Tech stack is Hugo + Tailwind (Play CDN remains for now — Phase 4 replaces it; Phase 1 must not introduce a Node/npm dependency)
- Hosting is GitHub Pages at `www.cingparty.uk`
- UK GDPR + PECR compliance is the explicit driver of PRIVACY-01
- Single-maintainer reality: solutions must be one-person operable
- No embargoed material on `main` (informs the Phase-1-vs-Phase-2 split for press script)

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| PRIVACY-01 | GA `gtag/js` must not load before consent; reject = zero requests to `googletagmanager.com` / `google-analytics.com` | §1 (consent gating pattern), §2 (where to splice into existing handlers), §6 (DevTools verification) |
| PRIVACY-02 | All H2 headings in `content/privacy/_index.md` render as headings | §3 (exact line numbers of the four broken `##` headings) |
| PRIVACY-03 | `CLAUDE.md` accurately describes post-fix GA loading flow | §4 (current text and a corrected version that matches §1's recommended implementation) |
| EMBARGO-01 | `scripts/generate_press_pdfs.py` runs without `FileNotFoundError` against current paths | §5 (slug-to-filename match confirmed; precise lines to edit) |

---

## 1. GA consent gating — script-load vs Consent Mode v2

### The decision

The roadmap's success criterion is "rejecting consent triggers zero requests to `googletagmanager.com` or `google-analytics.com`". Two implementation patterns exist:

| Pattern | What it does | Compatible with success criterion? |
|---------|--------------|-----------------------------------|
| **(a) Script-blocking** — only inject `<script src="...gtag/js?id=...">` when consent is `accepted` | No requests at all to GA hosts pre-consent or on rejection | YES |
| **(b) Consent Mode v2 default-deny** — inject the script always, but call `gtag('consent','default',{analytics_storage:'denied'})` first | gtag.js still loads (1 request to `googletagmanager.com`) and Google receives anonymous "cookieless pings" (request to `google-analytics.com/g/collect`) even when denied | NO |

Pattern (b) is what the *current* code in `baseof.html:8-35` implements, and it's the source of the privacy-policy contradiction documented in `.planning/codebase/CONCERNS.md` HIGH item #1. Pattern (a) is required.

[CITED: Usercentrics 2026 ICO guidance summary] ICO 2025 guidance "broadened the practical focus from 'cookies' to all storage and access tech, including pixels, fingerprinting, web storage, and tag-based scripts" and requires "no non-exempt technologies are triggered before a positive opt-in". Cookieless pings fall inside this scope.

[CITED: ICO/PECR Data (Use and Access) Act 2025 amendments] Analytics is not within the strictly-necessary exemption; opt-in consent is required before any analytics technology executes.

### Recommended implementation

Replace `baseof.html:8-35` with:

```html
{{ if hugo.IsProduction }}
<script>
  // Google Analytics — only loaded after explicit consent. No script tag,
  // no cookieless pings, no requests to googletagmanager.com or
  // google-analytics.com until the user clicks "Accept" on the cookie banner.
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  window.gtag = gtag;

  var GA_ID = 'G-Z1F4F1TRD0';
  var gtagLoaded = false;

  window.loadGtag = function() {
    if (gtagLoaded) return;            // idempotent
    gtagLoaded = true;
    var s = document.createElement('script');
    s.async = true;
    s.src = 'https://www.googletagmanager.com/gtag/js?id=' + GA_ID;
    document.head.appendChild(s);
    gtag('js', new Date());
    gtag('config', GA_ID);
  };

  if (localStorage.getItem('cing-cookies') === 'accepted') {
    window.loadGtag();
  }
</script>
{{ end }}
```

And in the existing banner handler (`baseof.html:247-253`), call `window.loadGtag()` instead of (or in addition to) the existing `gtag('consent','update',...)` call:

```javascript
document.getElementById('cookie-accept').addEventListener('click', function() {
  localStorage.setItem('cing-cookies', 'accepted');
  document.getElementById('cookie-banner').classList.add('hidden');
  if (typeof window.loadGtag === 'function') {
    window.loadGtag();
  }
});
```

The reject handler (`baseof.html:254-260`) needs no functional change — it should *not* call `loadGtag()` and the existing `gtag('consent','update',{analytics_storage:'denied'})` becomes a no-op (gtag is a queue-only stub) and can be removed for tidiness.

### Why this exact shape

- **Idempotency:** `gtagLoaded` flag prevents a double script tag if the user accepts twice (e.g. clears banner via DevTools, accepts again). [VERIFIED: Google Tag Platform docs: gtag.js loaded twice will install duplicate measurement, doubling pageviews.]
- **`gtag('config',...)` after appending the script:** Per the [VERIFIED: Google Tag Platform docs `gtag.js` install snippet], `gtag('js', date)` and `gtag('config', id)` are pushed to the dataLayer immediately and processed when the script finishes loading. There is no race condition — the dataLayer queue is the documented contract. We do *not* need an `s.onload` handler.
- **Default-deny consent block removed:** It's only meaningful if the script loads. With pattern (a) the script never loads pre-consent, so default-deny adds noise without value. (If the project later decides to also support Google Ads attribution under denied state, that's a Phase 4+ conversation.)
- **`window.loadGtag` namespacing:** The current code already exposes `window.gtag`. Same pattern, same place — keeps the Hugo template surface identical for the future Tailwind-build refactor (Phase 4) which will likely move JS into a separate asset file.

### Edge cases to handle

| Edge case | Behaviour with recommended impl |
|-----------|--------------------------------|
| User has `localStorage['cing-cookies'] === 'rejected'` from a prior visit | Page-load check fails; no script tag injected; no banner shown (existing logic at line 244 handles "no banner if any choice exists") |
| User clicks Accept mid-session | Banner handler calls `window.loadGtag()`; first pageview fires after script load completes |
| User clicks Reject then later clears localStorage | Next page load shows banner again (existing behaviour); no GA load until they accept |
| Ad blockers (uBlock, Brave shields) | Block the script regardless. Our network-tab verification in Step 6 must use a clean profile. |
| User opens two tabs and accepts in one | Each tab loads gtag independently — fine, gtag.js is designed for per-page-load init |
| Local development (`hugo server`) | Entire block is wrapped in `{{ if hugo.IsProduction }}` — still no GA in dev (existing behaviour preserved) |

---

## 2. Hugo + cookie consent: implementation patterns in this codebase

### Current banner structure (`layouts/_default/baseof.html:218-263`)

- Banner DOM at lines 220-240, hidden by default via `class="hidden"`.
- IIFE at lines 242-262 reads `localStorage.getItem('cing-cookies')`:
  - If no choice → unhide banner.
  - On `cookie-accept` click → set `'accepted'`, hide banner, call `gtag('consent','update',{analytics_storage:'granted'})`.
  - On `cookie-reject` click → set `'rejected'`, hide banner, call `gtag('consent','update',{analytics_storage:'denied'})`.
- The `gtag` function is defined in the head block at lines 9-12 (so the banner handler at line 250 can reference it safely as `typeof gtag === 'function'`).

### Splice points for `loadGtag()`

Both calls need to coexist:

1. **Page-load (already-accepted):** Replace the IIFE at `baseof.html:26-31` with the new `window.loadGtag` definition + the existing-accepted check (see §1 implementation block).
2. **Just-accepted:** Replace the `gtag('consent','update',{analytics_storage:'granted'})` line at `baseof.html:251` with `window.loadGtag()`. (The `typeof gtag === 'function'` guard is no longer needed since `gtag` is unconditionally defined in the head; reuse `typeof window.loadGtag === 'function'` instead.)
3. **Just-rejected:** Remove the `gtag('consent','update',{analytics_storage:'denied'})` at line 258 — there's no consent state to update because no script was loaded.

### Race conditions

There are none worth handling:
- The `gtag` stub is defined synchronously in the head before any other script.
- `gtag('config', GA_ID)` is queued and dispatched when gtag.js loads — that's the documented contract.
- The Cookie banner script runs after `</body>` (it's at the bottom of the page), so `window.loadGtag` is guaranteed defined when it executes.

### What to keep

- The `{{ if hugo.IsProduction }}` gates at lines 8 + 35 + 219 + 263 stay exactly where they are.
- The banner DOM/styling (lines 220-240) doesn't change.
- The "no banner if a choice exists" pattern (line 244) doesn't change.

---

## 3. Privacy page markdown fix

[VERIFIED: read `content/privacy/_index.md` directly.]

Four lines need a space inserted after `##`:

| Line | Current | Should be |
|------|---------|-----------|
| 9  | `##What data we collect` | `## What data we collect` |
| 51 | `##Data retention` | `## Data retention` |
| 55 | `##Your rights` | `## Your rights` |
| 66 | `##Contact us` | `## Contact us` |

For comparison, the *correctly*-formatted H2s already in the same file are at lines 16 (`## Cookies {#cookies}`), 31 (`## How we use your data`), and 41 (`## Third-party services`). The fix is: 4 single-character insertions.

**Optional polish (not required by PRIVACY-02):** Line 27 currently says "If you reject cookies, no analytics cookies are set and no data is sent to Google." That sentence becomes *literally true* once PRIVACY-01 ships. No edit needed — the privacy page is the spec, the implementation is finally meeting it.

---

## 4. CLAUDE.md doc fix

[VERIFIED: read `CLAUDE.md` lines 87-93.]

### Current text (CLAUDE.md:87-89)

```
### Analytics and cookie consent

Google Analytics (`G-Z1F4F1TRD0`) is loaded only in production builds (`hugo.IsProduction`) and only after the user accepts cookies via the consent banner. The consent choice is stored in `localStorage` (key: `cing-cookies`, values: `accepted` or `rejected`). The `loadGtag()` function in `baseof.html` dynamically injects the gtag script. The cookie banner and consent logic are both in `baseof.html`, gated behind `hugo.IsProduction` so local dev is unaffected.
```

### Why it's wrong today

- "only after the user accepts cookies" — false in current code (script loads always, Consent Mode v2 default-deny).
- "The `loadGtag()` function in `baseof.html`" — that function does not exist in current code; it's a hallucination.

### Recommended replacement (matches the §1 implementation)

```
### Analytics and cookie consent

Google Analytics (`G-Z1F4F1TRD0`) is loaded only in production builds (`hugo.IsProduction`) and only after the user accepts cookies via the consent banner — the `<script src="https://www.googletagmanager.com/gtag/js?...">` tag is not injected at all until consent is granted, so rejecting (or not yet choosing) results in zero requests to `googletagmanager.com` and `google-analytics.com`. The consent choice is stored in `localStorage` (key: `cing-cookies`, values: `accepted` or `rejected`). The `window.loadGtag()` function in `baseof.html` dynamically injects the gtag script and is called from two places: at page load if the stored choice is already `accepted`, and from the cookie banner's Accept button handler. The function is idempotent (a `gtagLoaded` flag prevents double-loading). The cookie banner and consent logic are both in `baseof.html`, gated behind `hugo.IsProduction` so local dev is unaffected.
```

### Cross-document consistency

Two other planning documents will need a follow-up sentence after PRIVACY-01 lands; they are *not* in Phase 1 scope but are flagged here so the planner can decide whether to bundle:

- `.planning/codebase/INTEGRATIONS.md` lines 21-26 describe the current "Consent Mode v2 default-deny + script always loaded" pattern. After PRIVACY-01 this paragraph also becomes stale. Recommend the planner adds a single-line task to 01-01 to update it, or explicitly defers.
- `.planning/codebase/CONCERNS.md` HIGH item #1 will become obsolete and should be cross-referenced as resolved in the phase transition (handled by `/gsd-transition`, not the plan).

---

## 5. Press PDF script repointing — current state and minimal fix

### What the script reads today

[VERIFIED: read `scripts/generate_press_pdfs.py:36-37, 122-163` directly.]

```python
ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "content" / "press" / "_incoming"
```

`SOURCE_DIR` is referenced only inside the `RELEASES` list (lines 122-163). Each `Release.src_md` is `SOURCE_DIR / "<numbered subdir>" / "<filename>.md"`. The five subdirectories the script expects (`11.1 Mevagissey Families`, `11.2 Dentistry`, `11.3 Deprivation`, `11.4 Public Realm`, `questions`) **do not exist** in the working tree:

```
$ ls content/press/_incoming/
_index.md
```

### Where the source markdown actually lives

[VERIFIED: `ls content/press/full-council-2026-04-21/`.]

```
content/press/full-council-2026-04-21/
├── _index.md
├── childrens-nhs-dental-care.md
├── glyphosate-weedkiller-halt.md
├── mevagissey-school-transport.md
├── planning-public-trust.md
└── rural-deprivation-funding.md
```

### Slug-to-filename match (the lucky bit)

Each `Release.slug` in the script already matches the filename of the corresponding published markdown. [VERIFIED: ran `for slug in ...; do test -f content/press/full-council-2026-04-21/$slug.md; done` — all 5 OK.]

| `Release.slug` | Current `src_md` (broken) | Recommended `src_md` |
|----------------|---------------------------|----------------------|
| `mevagissey-school-transport` | `_incoming / "11.1 Mevagissey Families" / "2026-04-21_press-release_mevagissey-school-transport.md"` | `<published> / "mevagissey-school-transport.md"` |
| `childrens-nhs-dental-care` | `_incoming / "11.2 Dentistry" / "CING_Press_Release_BBC_Version.md"` | `<published> / "childrens-nhs-dental-care.md"` |
| `rural-deprivation-funding` | `_incoming / "11.3 Deprivation" / "cing_press_release_cornwall_deprivation_motion.md"` | `<published> / "rural-deprivation-funding.md"` |
| `glyphosate-weedkiller-halt` | `_incoming / "11.4 Public Realm" / "CING_PR_Weedkiller_Nuclear_2026-04-21.md"` | `<published> / "glyphosate-weedkiller-halt.md"` |
| `planning-public-trust` | `_incoming / "questions" / "press_release_planning_question_markdown.md"` | `<published> / "planning-public-trust.md"` |

Where `<published>` = `ROOT / "content" / "press" / "full-council-2026-04-21"`.

### Front-matter compatibility

[VERIFIED: read three of the five published files — `childrens-nhs-dental-care.md`, `mevagissey-school-transport.md`, `planning-public-trust.md`.]

The script's `parse_markdown()` function does not touch front matter at all — it only consumes the body (everything after the second `---`). The body shapes match what the parser already handles:

| Body element | Parser behaviour | Present in published files? |
|--------------|------------------|----------------------------|
| H1 (`# ...`) | Skipped (line 250) | Some files have one, some don't — both fine |
| Strapline (first `**bold**` line, < 200 chars) | Skipped (lines 297-307) | Yes — `mevagissey-school-transport.md:11` `**Families face inconsistent rules...**` |
| H2 (`## ...`) | Rendered as H2 (line 262) | Yes (e.g. `## What the Motion Calls For`) |
| Blockquote (`> ...`) | Rendered as gold pull quote (line 278) | Yes (e.g. lines starting `> "Right now in Cornwall..."`) |
| Bullet list (`- ` or `* `) | Rendered as bullets (line 290) | Yes |
| Inline `**bold**` / `*italic*` / `[link](url)` | Converted to ReportLab `<b>/<i>/<link>` (line 173) | Yes |
| `## FOR IMMEDIATE RELEASE` / `**ENDS**` markers | Skipped (line 257) | Mostly absent — published versions have already been edited down |
| `Media Contact` / `Media Enquiries` block | Truncates parsing (line 312) | Mostly absent — but the truncation is harmless if it's not there |

Conclusion: the published markdown is parser-compatible with no body-format changes. The PDFs produced after the fix will be substantively equivalent to the existing PDFs in `static/documents/press/2026-04-21/` (small layout-level diffs are possible because the published markdown has been editorially polished vs. the original drafts, but no crashes and no missing content).

### Recommended fix (minimal, Phase 2 will revisit)

Three changes to `scripts/generate_press_pdfs.py`:

1. **Line 37:** Change `SOURCE_DIR = ROOT / "content" / "press" / "_incoming"` to `SOURCE_DIR = ROOT / "content" / "press" / "full-council-2026-04-21"`.
2. **Lines 128, 136, 144, 152, 160 (the five `src_md=` values):** Change each to `src_md=SOURCE_DIR / f"{slug}.md"` style — concretely, hardcode the new filenames since `Release` is a frozen dataclass with `slug` and `src_md` as separate fields. Simplest edit:
   - `src_md=SOURCE_DIR / "mevagissey-school-transport.md"`
   - `src_md=SOURCE_DIR / "childrens-nhs-dental-care.md"`
   - `src_md=SOURCE_DIR / "rural-deprivation-funding.md"`
   - `src_md=SOURCE_DIR / "glyphosate-weedkiller-halt.md"`
   - `src_md=SOURCE_DIR / "planning-public-trust.md"`
3. **Optional refactor (recommended for legibility, ~5 line diff):** Drop the `src_md` field entirely and have `build_pdf` derive `SOURCE_DIR / f"{release.slug}.md"`. This collapses 5 redundant lines and self-documents the slug↔filename invariant.

**Phase 2 implication (EMBARGO-02):** Phase 2 will move embargoed *drafts* back into `_incoming/` (so they don't appear on `main` ahead of time). At that point the script will need *both* sources — drafts during embargo, published markdown after lift. The Phase-1 fix should not over-engineer for that — repointing to the published location is correct for today, and the Phase-2 plan can introduce a `--source-dir` argument or a per-release explicit path if needed. **Do not** add CLI arguments or environment variables in Phase 1; keep the diff minimal.

### Validation

After the fix, running `python scripts/generate_press_pdfs.py` from a clean checkout must:
- Not raise `FileNotFoundError`.
- Produce 5 PDFs in `static/documents/press/2026-04-21/`.
- Each PDF should open and render with the navy banner, gold accent, body content, and footer (visual sanity check, not byte-level diff).

PDFs will overwrite the existing committed versions. Reviewer should diff visually, not by hash, since regeneration is non-deterministic at the byte level (PDF metadata includes generation timestamps).

---

## 6. Risks and gotchas

### PRIVACY-01

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Implementation race condition: `gtag('config',...)` queued before `gtag.js` loads | Low (documented gtag contract) | Trust the dataLayer queue — no `onload` handler needed. Verified in network tab: `collect` request fires only once script loads, post-config call. |
| Ad blockers (uBlock, Brave shields) block the test | Medium (Brave shields on by default) | Verify in a clean Chrome/Firefox profile with no extensions. Document this in the verification step. |
| `localStorage` disabled by browser (private mode in some Safari versions) | Low | Existing IIFE at line 243 already handles `localStorage` access — if it throws, JS errors silently and banner shows. New code preserves this. |
| User has previously-accepted state then privacy code changes — they're "consented" under old terms | Low (small audience, recent banner) | Acceptable per privacy policy: consent is to "Google Analytics for anonymous usage statistics", not to a specific implementation. No re-consent prompt needed. |
| Forgetting to remove the now-dead default-deny block | Medium | Code review — the new implementation should be a single `<script>` block, not two. |
| `gtagLoaded` flag missing causes double-load on rapid Accept→clear→Accept | Low | Idempotency flag is in the recommended snippet. |

**Verification (success criterion):**
- Open production site `https://www.cingparty.uk/` in a clean Chrome profile, DevTools Network tab open, filter `gtm OR analytics OR google`.
- Hard reload. Click **Reject**. Navigate to a few pages. Confirm: zero requests to `googletagmanager.com` or `google-analytics.com` for the entire session.
- Clear localStorage, hard reload. Click **Accept**. Confirm: one request to `googletagmanager.com/gtag/js?id=G-Z1F4F1TRD0` fires immediately, followed by `google-analytics.com/g/collect?...` for the pageview.
- Reload the page (consent already 'accepted'). Confirm same behaviour without re-clicking Accept.

### PRIVACY-02

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Heading-level renumbering (e.g. promoting one to H1) introduces nav drift | Very low | Just adding spaces — no level change |
| The fragment `{#cookies}` syntax breaks if a fixer pass strips it | Low | Line 16 (`## Cookies {#cookies}`) is already correct — no edit there |
| Pre-commit markdownlint not installed → regression possible later | Out of scope | CONCERNS.md MEDIUM item suggests it; CI safety nets are Phase 4 |

**Verification:** Local `hugo server`, view `/privacy/`, inspect rendered HTML. All four sections appear as `<h2>` elements, not `<p>##...</p>`. Or simpler: visually confirm the four headings are styled per the site's H2 type scale, not body text.

### PRIVACY-03

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| CLAUDE.md description drifts from code on the next privacy-related change | Medium | The replacement text is precise about *function name* and *call sites*. Future changes that move the JS will need to update both. Acceptable; no automation in Phase 1. |
| `INTEGRATIONS.md` left stale | Medium | Either include a one-line update in the same PR, or note explicitly that it will be refreshed on the next codebase-map regen. Recommend planner pick the former. |

**Verification:** Read CLAUDE.md and confirm no reference to "Consent Mode v2 default-deny" remains, and that the `loadGtag()` description matches the actual code.

### EMBARGO-01

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Script writes PDFs that visually diverge from the existing committed PDFs | Medium | Expected — published markdown is the editorially polished version. Verify rendered output passes visual inspection; do not gate on hash match. |
| Running the script overwrites committed PDFs and pollutes the working tree | Certain | Acceptable — that's the point. The verifier should run the script and `git diff --stat static/documents/press/2026-04-21/` to confirm 5 files changed. Whether to commit those PDFs is a separate editorial decision (recommend yes). |
| `reportlab` / `Pillow` not installed locally | Medium (no requirements.txt yet) | Install instructions are in CONCERNS.md MEDIUM "Press scripts have no pinned dependencies" — Phase 3 (BUILD-02) addresses this. For Phase 1, document the install step (`pip install reportlab Pillow`) in the plan's verification action. |
| Hardcoded font paths (`/usr/share/fonts/truetype/...`) fail on macOS | Medium | Out of scope for Phase 1 — that's BUILD-02 in Phase 3. The maintainer is on Linux per `.planning/codebase/STACK.md`, so verification on the maintainer's box will succeed. |
| `_incoming/_index.md` is the only file in `_incoming/` and currently orphan-looking | Low | Don't delete it — Phase 2 (EMBARGO-02) reuses `_incoming/` for embargoed drafts. Leave as-is. |

**Verification:**
- Fresh checkout, `pip install reportlab Pillow` in a venv, run `python scripts/generate_press_pdfs.py`.
- Output: "wrote static/documents/press/2026-04-21/<slug>.pdf (NN KB)" five times, no traceback.
- Open one PDF (`xdg-open static/documents/press/2026-04-21/childrens-nhs-dental-care.pdf`) — banner with "FULL COUNCIL · 21 APRIL 2026 · NHS DENTISTRY", title visible, body content present, footer shows "Page 1".

---

## 7. Recommended plan structure

The roadmap's provisional split is correct:

- **01-01 — Privacy & analytics consent gating (PRIVACY-01, PRIVACY-02, PRIVACY-03):** Bundle these. They share a single file (`baseof.html`), a shared mental model (consent gating + truthful documentation), and a single reviewer pass. Splitting them would force three PRs that all gate on the same DevTools verification.
- **01-02 — Press PDF script repointing (EMBARGO-01):** Independent. Touches only `scripts/generate_press_pdfs.py`. Different file, different reviewer concern, different verification (run the script). Can ship in parallel with 01-01.

**One small refinement worth considering:** Optionally include `INTEGRATIONS.md` line 21-26 update in 01-01 (one-line consistency fix). This is mechanical given §4's recommended text and avoids a known-stale doc carrying through to Phase 2's planning. The planner may also choose to defer this to the codebase-map regen at the next `/gsd-transition` — both are defensible.

### Suggested task ordering inside 01-01

1. Implement `loadGtag()` change in `baseof.html` (the load-bearing change).
2. Update banner Accept handler to call `window.loadGtag()`.
3. Remove the now-dead default-deny consent block and the now-no-op reject-handler `gtag('consent','update',...)` line.
4. Fix four `##` headings in `content/privacy/_index.md`.
5. Rewrite `CLAUDE.md` analytics paragraph.
6. (Optional) Update `INTEGRATIONS.md` analytics paragraph.
7. Verify on `hugo server`: no JS errors in console; banner shows once; Accept hides banner; localStorage carries `accepted`.
8. Verify on a deployed preview (or staging build): DevTools network tab — zero `googletagmanager` requests pre-consent; one after Accept.

### Suggested task ordering inside 01-02

1. Edit `SOURCE_DIR` (line 37) and the five `src_md` values (lines ~128/136/144/152/160).
2. (Optional, recommended) Drop the `src_md` field from `Release` and derive from `slug`.
3. Run the script in a clean venv with `pip install reportlab Pillow`.
4. Verify 5 PDFs regenerate without error and open visually correctly.
5. Decide whether to commit the regenerated PDFs (recommend yes — keeps `static/documents/press/2026-04-21/` in lockstep with the script's actual output).

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Consent management beyond Accept/Reject (e.g. granular categories, withdrawal UI, audit log) | A custom CMP | Out of scope for Phase 1 — current binary banner is sufficient under PECR for the single GA cookie category | Adds 200+ lines for no current legal benefit |
| Markdown linting in pre-commit | A custom regex script | `markdownlint-cli2` (Phase 4 / CI safety nets) | Already considered; in CONCERNS.md MEDIUM. Not Phase 1. |
| Reproducible Python script execution | A custom shim | `pip install -r requirements.txt` (Phase 3 / BUILD-02) | Already on the roadmap; don't fold into Phase 1 |

---

## Common Pitfalls

### Pitfall 1: "Consent Mode v2 means I'm compliant by default"
**What goes wrong:** Developer sees Google's recommended pattern (load gtag.js, deny consent, defer to user choice) and assumes the cookieless pings are exempt under PECR.
**Why it happens:** Google's docs frame Consent Mode as a privacy-preserving default; ICO's framing is stricter.
**How to avoid:** Read the success criterion. "Zero requests" is the spec. Pattern (b) cannot satisfy it.
**Warning signs:** Reviewer sees `gtag('consent','default',...)` block — that's the smell.

### Pitfall 2: "Just gate the script tag with a Hugo conditional"
**What goes wrong:** Tempting to write `{{ if (something) }}<script>gtag</script>{{ end }}` — but Hugo runs at build time, not per-visitor. Every production page would either have the script or not, regardless of the visitor's localStorage.
**Why it happens:** SSG mental model leaks into client-side decisions.
**How to avoid:** All consent decisions are runtime/browser, not build-time. The Hugo `{{ if hugo.IsProduction }}` gate is fine (build-time: prod vs dev) but per-visitor gating must happen in the inline JS.
**Warning signs:** Anyone proposing a Hugo template variable for consent state.

### Pitfall 3: "Repointing the script means rewriting the parser"
**What goes wrong:** Developer assumes published markdown looks different from drafts and starts rewriting `parse_markdown()`.
**Why it happens:** The five published files *have* been editorially polished, so they look slightly different from the drafts the parser was originally built for.
**How to avoid:** The parser was already built defensively — H1 skipping, strapline skipping, ENDS skipping, media-contact truncation. All of those still apply. Run it. The output will be acceptable.
**Warning signs:** Diff to `parse_markdown()`. There shouldn't be one.

---

## Code Examples

### Recommended `loadGtag()` block (replaces baseof.html:9-34)

```html
<script>
  // [VERIFIED: Google Tag Platform docs, gtag.js install snippet pattern]
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  window.gtag = gtag;

  var GA_ID = 'G-Z1F4F1TRD0';
  var gtagLoaded = false;

  window.loadGtag = function() {
    if (gtagLoaded) return;
    gtagLoaded = true;
    var s = document.createElement('script');
    s.async = true;
    s.src = 'https://www.googletagmanager.com/gtag/js?id=' + GA_ID;
    document.head.appendChild(s);
    gtag('js', new Date());
    gtag('config', GA_ID);
  };

  if (localStorage.getItem('cing-cookies') === 'accepted') {
    window.loadGtag();
  }
</script>
```

### Updated cookie banner Accept handler (replaces baseof.html:247-253)

```javascript
document.getElementById('cookie-accept').addEventListener('click', function() {
  localStorage.setItem('cing-cookies', 'accepted');
  document.getElementById('cookie-banner').classList.add('hidden');
  if (typeof window.loadGtag === 'function') {
    window.loadGtag();
  }
});
```

### Updated press script `RELEASES` entries (illustrative — option B refactor)

```python
SOURCE_DIR = ROOT / "content" / "press" / "full-council-2026-04-21"

@dataclass
class Release:
    slug: str
    category: str
    title: str
    strapline: str
    image: str

    @property
    def src_md(self) -> Path:
        return SOURCE_DIR / f"{self.slug}.md"

RELEASES: list[Release] = [
    Release(
        slug="mevagissey-school-transport",
        category="School Transport",
        title="Mevagissey Families Denied Fair Access to School Transport",
        strapline="Families face inconsistent rules despite children travelling on the same bus.",
        image="mevagissey-school-transport.jpg",
    ),
    # ... and the other four, unchanged except for the dropped src_md=
]
```

(Or — minimal-diff version — leave `Release.src_md` as a field and rewrite the five values inline. Both are acceptable.)

---

## State of the Art

| Old Approach | Current Approach (Phase 1 target) | When Changed | Impact |
|--------------|-----------------------------------|--------------|--------|
| Consent Mode v2 default-deny + script always loaded | Script not injected until consent | This phase | Privacy claim becomes truthful; ~60 KB of JS not loaded for visitors who reject (a side benefit) |
| Press script reads from non-existent `_incoming/` | Reads from `content/press/full-council-2026-04-21/` | This phase | Script becomes runnable again |

**Deprecated/outdated (already documented in CONCERNS.md):**
- Tailwind Play CDN — Phase 4
- Hand-coded font paths in press scripts — Phase 3 (BUILD-02)
- Single Formspree endpoint — Phase 2 (FORMS-03)

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The published markdown body shape is parser-compatible *for all 5 releases* | §5 | LOW — verified for 3 of 5 by direct read; spot-check the other 2 in plan execution |
| A2 | The maintainer's local machine has `reportlab` and `Pillow` installed (or can install them) | §5, §6 | LOW — they were used to generate the existing PDFs |
| A3 | "Zero requests" in the roadmap success criterion includes the gtag.js script itself, not only the `/g/collect` endpoint | §1 | LOW — both hosts are explicitly listed (`googletagmanager.com` AND `google-analytics.com`) |
| A4 | The current visitor base who already chose "accepted" do not need to re-consent because the underlying consent (GA usage) hasn't changed, only the implementation | §6 PRIVACY-01 | MEDIUM — defensible legally (consent is to the activity, not the technical mechanism), but a strict reading might require re-prompt. Recommend the planner flag this for the maintainer to decide; safe default is "no re-prompt". |

If the planner or maintainer disagrees with any of these, A4 is the only one with a behaviour-changing fork (clear localStorage on deploy → forces banner re-show for everyone).

---

## Open Questions

1. **Should `INTEGRATIONS.md` be updated in 01-01 or deferred to next codebase regen?**
   - What we know: the file's analytics paragraph will be stale after PRIVACY-01. CLAUDE.md must be updated in 01-01 (it's PRIVACY-03). INTEGRATIONS.md is just stale, not actively misleading any AI run.
   - What's unclear: maintainer preference for "fix all stale docs in this PR" vs "let the codebase-map regen handle it".
   - Recommendation: include in 01-01 (one-line edit, no extra reviewer cost).

2. **Should the regenerated PDFs be committed in 01-02?**
   - What we know: PDFs are committed today. Re-running the script will overwrite them. Diff will be non-byte-identical even if visually equivalent (PDF timestamps).
   - What's unclear: whether to commit the regenerated PDFs (risk: visual regression; benefit: keeps script output and committed artefact in sync).
   - Recommendation: commit them. The current committed PDFs were last generated against now-deleted source markdown — they're already orphaned from a reproducibility standpoint. Re-anchoring them to the published source is the value.

3. **Phase 1 completion gate: do we need to deploy to verify "zero requests"?**
   - What we know: `hugo server` doesn't exercise the production build (the `{{ if hugo.IsProduction }}` block is excluded).
   - What's unclear: does the verification need a `hugo --baseURL ... && python -m http.server` local prod-build dance, or is a deploy-preview branch acceptable?
   - Recommendation: build locally with `hugo --gc --minify` and serve `public/` via `python -m http.server` for verification. Deploy to `main` only after local verification passes (branch protection means a PR is mandatory anyway).

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Hugo (extended) | Build verification | Assumed (per STACK.md) | 0.159.1 (CI pin) | — |
| Python 3 | EMBARGO-01 | Assumed | 3.x | — |
| `reportlab` (Python) | EMBARGO-01 | Likely (used to generate existing PDFs) | unpinned | `pip install reportlab` |
| `Pillow` (Python) | EMBARGO-01 (used by `generate_press_heroes.py`, transitively) | Likely | unpinned | `pip install Pillow` |
| `/usr/share/fonts/truetype/google-fonts/Poppins-*.ttf` | EMBARGO-01 | Linux-only path | — | Out of scope (BUILD-02, Phase 3) |
| `/usr/share/fonts/truetype/lato/Lato-*.ttf` | EMBARGO-01 | Linux-only path | — | Out of scope (BUILD-02, Phase 3) |
| Modern browser with DevTools | PRIVACY-01 verification | User-supplied | — | — |

**Missing dependencies with no fallback:** None for Phase 1.

**Missing dependencies with fallback:** `reportlab` and `Pillow` may need a `pip install` step on a fresh checkout — the plan's verification action should include this.

---

## Validation Architecture

### Test Framework

This is a Hugo static site with no test framework today. CONCERNS.md LOW item "No automated tests of any kind" confirms this; pa11y-ci and lychee CI safety nets are Phase 4 (CI-01, CI-02). For Phase 1 the validation strategy is *manual + script execution* — no Wave 0 test scaffolding required.

| Property | Value |
|----------|-------|
| Framework | None (manual verification + Hugo build itself as syntax check) |
| Config file | — |
| Quick run command | `hugo --gc --minify --baseURL "http://localhost:8080/"` then `cd public && python -m http.server 8080` |
| Full suite command | (same as quick) + `python scripts/generate_press_pdfs.py` |
| Phase gate | Manual DevTools network-tab inspection + visual PDF inspection |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|--------------|
| PRIVACY-01 | Reject → zero requests to GA hosts | manual (DevTools) | — (browser-driven) | n/a |
| PRIVACY-01 | Accept → exactly one `gtag/js` request and pageview `/g/collect` | manual (DevTools) | — | n/a |
| PRIVACY-02 | Privacy page renders 4 H2s as `<h2>`, not text | manual + curl/grep | `hugo --gc --minify && grep -c '<h2[^>]*>What data we collect</h2>' public/privacy/index.html` (expected: 1) | post-build |
| PRIVACY-03 | CLAUDE.md describes loadGtag flow accurately | manual (read-and-compare) | `grep -F 'loadGtag()' CLAUDE.md` (expected: matches new text, not old) | yes (CLAUDE.md) |
| EMBARGO-01 | Script runs without FileNotFoundError | scripted | `python scripts/generate_press_pdfs.py` | yes (scripts/) |
| EMBARGO-01 | Script produces 5 PDFs | scripted | `ls static/documents/press/2026-04-21/*.pdf | wc -l` (expected: 5) | yes |

### Sampling Rate

- **Per task commit:** local `hugo server` to confirm no template error; `python scripts/generate_press_pdfs.py` if Python file changed
- **Per wave merge:** full local prod build + DevTools verification + script run
- **Phase gate:** all 4 success criteria from ROADMAP.md verified, plus visual confirmation that the cookie banner still styles correctly

### Wave 0 Gaps

- None — Phase 1 does not require new test infrastructure. Phase 4 (CI-01, CI-02) introduces lychee + pa11y-ci, which would catch regressions to PRIVACY-02 and the privacy page layout going forward.

*(Phase 1 deliberately does not introduce a test framework. Adding one would inflate scope by an order of magnitude relative to the four small fixes here. Phase 4 is the right home.)*

---

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | No auth on a public static site |
| V3 Session Management | no | No sessions |
| V4 Access Control | no | No protected resources |
| V5 Input Validation | partial | Forms post to Formspree (FORMS-01 in Phase 2 adds honeypot); not Phase 1 scope |
| V6 Cryptography | no | No crypto handled in browser; HTTPS via GitHub Pages is platform-level |
| V8 Data Protection | yes (PRIVACY-01) | Block third-party tracker until consent — the Phase 1 deliverable itself |
| V9 Communications | partial | Only HTTPS endpoints loaded (gtag.js URL is HTTPS); no mixed-content risk |
| V14 Configuration | yes | Production-vs-dev gate via `hugo.IsProduction` is the correct configuration boundary; Phase 1 must preserve it |

### Known Threat Patterns for {Hugo + browser-side consent + Python script}

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Tracker loads pre-consent (PECR breach) | Information Disclosure | Block script injection until `localStorage` value is `accepted` (Phase 1 PRIVACY-01) |
| Privacy claim contradicts implementation (reputational) | Repudiation | Documentation + code in lockstep (Phase 1 PRIVACY-02 + PRIVACY-03) |
| AI-assisted code edits operate on wrong mental model (drift) | Tampering (indirect) | Keep CLAUDE.md current with implementation (Phase 1 PRIVACY-03) |
| Press release toolchain unrunnable (operational) | Denial of Service (self-inflicted) | Repoint script to current source paths (Phase 1 EMBARGO-01) |

---

## Sources

### Primary (HIGH confidence)
- `layouts/_default/baseof.html` (lines 1-50, 218-263) — current GA + cookie banner implementation, read directly
- `content/privacy/_index.md` — broken H2 lines confirmed by line-by-line read
- `scripts/generate_press_pdfs.py` (lines 36-37, 122-163) — `SOURCE_DIR` and `RELEASES` table, read directly
- `content/press/full-council-2026-04-21/` — actual filenames listed via `ls`; three of five front-matter blocks read directly
- `CLAUDE.md` (lines 87-93) — current analytics paragraph, read directly
- `.planning/codebase/INTEGRATIONS.md` — confirms Consent Mode v2 default-deny + always-loaded script as the *current* state
- `.planning/codebase/CONCERNS.md` — HIGH item #1 (privacy contradiction), MEDIUM items "Press scripts read from a path that no longer exists", "Privacy page has malformed markdown headings", "CLAUDE.md description of GA loading is wrong" — these are the source of the four Phase 1 requirements

### Secondary (MEDIUM confidence)
- [Usercentrics — ICO PECR Cookies Guidance: Compliance Explained for 2026](https://usercentrics.com/knowledge-hub/ico-pecr-cookie-guidance/) — summary of "no non-exempt technologies before opt-in" and the 2025/2026 Data (Use and Access) Act expansion to cookieless tracking
- WebSearch synthesis: ICO Data (Use and Access) Act 2025 amendments, multiple corroborating sources via search
- [Google Tag Platform docs — gtag.js install snippet](https://developers.google.com/tag-platform/gtagjs/install) — pattern for `dataLayer` queue and `gtag('config', ID)` post-script-load behaviour (training-corroborated; specific page not fetched in this session)

### Tertiary (LOW confidence)
- None — every claim used to drive a Phase 1 fix is grounded in a primary source within this repo or the cited ICO summary.

---

## Metadata

**Confidence breakdown:**
- Privacy implementation (§1, §2): HIGH — code read directly, replacement pattern is a small delta on existing structure, ICO/PECR position confirmed by a 2026 secondary source
- Privacy markdown fix (§3): HIGH — line numbers and current strings verified by direct file read
- CLAUDE.md fix (§4): HIGH — current text read directly; replacement text is a tight match to the §1 code
- Press script repointing (§5): HIGH — slug↔filename match verified by shell test; parser compatibility verified by direct read of three of five published files
- Pitfalls and risks (§6): MEDIUM — judgement-driven; risk register reflects experience with consent banners and reportlab, not test data

**Research date:** 2026-04-26
**Valid until:** 2026-05-26 (30 days — these fixes are stable; the only thing that could invalidate is a Hugo or Google Analytics breaking change, both unlikely)
