# Phase 1 Plan Check

**Date:** 2026-04-26
**Checker:** Claude (gsd-plan-checker)
**Plans verified:** `01-01-PLAN.md`, `01-02-PLAN.md`
**Method:** Goal-backward verification against ROADMAP.md success criteria, with mechanical spot-checks against the live working tree.

---

## Plan 01-01: Privacy & analytics consent gating

**Verdict:** PASS WITH NITS

### Per-dimension findings

#### 1. Goal coverage

The plan covers Phase 1 success criteria 1, 2, and 3 (PRIVACY-01, PRIVACY-02, PRIVACY-03). Each criterion is mapped to specific tasks and a verification step:

- **Criterion 1** (Reject → zero requests to GA hosts) — Tasks 2-3 modify the head block and banner handlers; Task 4 is a clean-profile DevTools verification that explicitly checks both hosts; Verification §1 reproduces this in detail. The "no script tag created at parse time" framing in Task 2's outcome is the right test of the gating decision.
- **Criterion 2** (privacy H2 rendering) — Task 6 fixes four lines; Verification §2 greps the rendered HTML for both `<h2>...</h2>` (expected: 1 each) and `<p>##` (expected: 0). This is a stronger test than visual inspection and directly proves the rendered shape.
- **Criterion 3** (CLAUDE.md accuracy) — Task 8 rewrites lines 87-89; Verification §3 greps for `window.loadGtag()` (positive), and `consent mode v2` / `default-deny` (negative). Plus a manual read-and-compare for the "zero requests" claim.

The plan also explicitly disclaims criterion 4 (delivered by 01-02) — correct scope discipline.

#### 2. Mechanical correctness

Spot-checked all four cited regions in the live tree:

- `baseof.html` lines 8-35: GA head block confirmed. Line 7 is a Hugo comment, line 8 is `{{ if hugo.IsProduction }}`, line 14 is `gtag('consent', 'default', {...})`, lines 26-31 are the IIFE that injects the script, line 35 is `{{ end }}`. **Plan says "lines 7-35" — technically the comment at line 7 is part of the block; this is fine but slightly imprecise.**
- `baseof.html` lines 247-253: Accept handler confirmed exactly as plan describes. Reject handler at 254-260 confirmed.
- `content/privacy/_index.md` lines 9, 51, 55, 66: All four lines confirmed as `##X` (no space). Lines 16, 31, 41 confirmed as correctly formatted (`## X`).
- `CLAUDE.md` lines 87-89: Confirmed. The current text already mentions "the `loadGtag()` function in `baseof.html`" — a hallucination, since no such function exists in the current code. The plan's framing of this as part of PRIVACY-03 is correct.
- `INTEGRATIONS.md` lines 19-24: Confirmed. The current text describes Consent Mode v2 default-deny + always-loaded script. Bullet header is at line 20, content runs to line 24.

No drift between plan and tree. The Task 1 "verify drift before editing" step is a sensible safety net but not load-bearing for the current state.

#### 3. Verification rigour

Strong overall. Verification §1 specifies a clean browser profile, a specific filter, the exact request URLs (`googletagmanager.com/gtag/js?id=G-Z1F4F1TRD0` and `google-analytics.com/g/collect`), the navigation paths, and the no-double-load condition. A reviewer with no inside knowledge can execute this.

Verification §2 uses literal grep counts on the built HTML for both positive (`<h2>` present) and negative (`<p>##` absent) cases — this proves the rendering, not just that the file was edited.

Verification §3 has a small gap: it states the analytics paragraph "must state explicitly that 'rejecting (or not yet choosing) results in zero requests'" but RESEARCH.md §4's recommended replacement says "rejecting (or not yet choosing) results in zero requests to `googletagmanager.com` and `google-analytics.com`" — slightly different wording. This is minor, but a reviewer running the grep will need to check the exact phrase, and the "If that exact phrase is missing, the doc is incomplete" wording sets a brittle bar. **Nit:** soften to "the paragraph must include both host names and the rejected-or-undecided framing".

#### 4. Atomicity

Three commits, each one logical change, each builds cleanly:

- Commit 1: `baseof.html` only — gating change.
- Commit 2: `content/privacy/_index.md` only — four single-character insertions.
- Commit 3: `CLAUDE.md` + `INTEGRATIONS.md` — both are doc-sync.

The boundary is clean. Bundling the doc-sync edits in one commit (3) is defensible because they are a single atomic concept ("documentation describes new flow"). Splitting them would create no value.

#### 5. Risk coverage

Strong. Specifically:

- **Accept-then-reject mid-session:** not explicitly listed, but the existing banner logic at line 244 only shows the banner if no choice exists, so once a user has clicked anything the banner does not return without manual `localStorage.clear()`. This is current behaviour preserved by the plan, not introduced by it. Worth noting but not a real risk.
- **Accept-then-reject in same session:** with the new code, the script is injected on Accept and stays loaded — clicking Reject afterwards would leave gtag.js running until next page load. This is an edge case the plan doesn't discuss explicitly. Since the banner doesn't re-show after a choice is made (line 244), the user has no UI path to do this without DevTools, so it's a theoretical-only concern. **Nit:** add a one-line risk row noting this is a known limitation of the localStorage-only model.
- **Private browsing / localStorage unavailable:** the existing IIFE at line 243 already catches this (would throw, banner shows by default). The new code's `localStorage.getItem('cing-cookies') === 'accepted'` check would also throw silently in some Safari versions, but the surrounding `<script>` tag has no try/catch. **Nit:** consider wrapping the page-load check in `try { ... } catch (e) {}` so a localStorage exception doesn't break the page. RESEARCH.md §6 marks this as Low likelihood; defensible to leave as-is.
- **Ad blockers:** explicitly listed and the verification step calls for a clean profile. Strong.
- **Idempotency:** explicitly listed; the `gtagLoaded` flag is in the recommended snippet.
- **Production gate accidentally removed:** explicitly listed with a `hugo server` verification.

#### 6. Scope discipline

Stays inside Phase 1. Does not pre-empt Phase 2 (no embargo work, no test framework introduction, no Tailwind build changes). The optional `INTEGRATIONS.md` rewrite was explicitly raised in RESEARCH.md §4 as a borderline call and the plan picks the "include for consistency" option — that's a fair call, single-paragraph edit, and both `CLAUDE.md` and `INTEGRATIONS.md` are AI-guidance docs that benefit from being in lockstep.

#### 7. Independence claim

Plan 01-01 touches: `layouts/_default/baseof.html`, `content/privacy/_index.md`, `CLAUDE.md`, `.planning/codebase/INTEGRATIONS.md`. None of these are touched by Plan 01-02. No CI workflow changes. No shared sections in `CLAUDE.md` (the analytics block is a discrete section under `### Analytics and cookie consent`). Independence holds.

### Verdict reasoning

Every success criterion in scope is delivered by named tasks; every task has reproducible verification; line numbers and file regions match the working tree exactly; commit boundary is clean. Two minor improvements would tighten the plan but none are blocking.

### Nits (optional)

1. Verification §3 wording for CLAUDE.md is slightly brittle ("If that exact phrase is missing, the doc is incomplete"). Soften to "must include both host names and the rejected-or-not-chosen framing".
2. Risks table could add one row noting the "Accept-then-Reject in same session" edge case is a known limitation of the localStorage-only model (not introduced by this plan, but worth flagging for the maintainer).
3. Optional but cheap: wrap the page-load `localStorage.getItem(...)` check in a try/catch to silently no-op in private-browsing modes that throw on storage access. RESEARCH.md §6 rates this Low; the plan can defensibly leave it as-is.

---

## Plan 01-02: Press PDF script repointing

**Verdict:** PASS WITH NITS

### Per-dimension findings

#### 1. Goal coverage

Covers Phase 1 success criterion 4 (EMBARGO-01) in full. The script's `SOURCE_DIR` is repointed and the five `src_md=` values are rewritten to use the published-markdown filenames. Verification §1 runs the script in a clean venv and asserts no traceback; Verification §2 asserts five PDFs land at the expected paths.

#### 2. Mechanical correctness

Spot-checked against the live tree:

- `scripts/generate_press_pdfs.py:37` confirmed: `SOURCE_DIR = ROOT / "content" / "press" / "_incoming"` ✓
- Lines 128, 136, 144, 152, 160 are exactly the five `src_md=` values, in the order the plan lists them (mevagissey, dental, deprivation, glyphosate, planning) ✓
- `content/press/full-council-2026-04-21/` contains exactly the five expected slug-named markdown files plus `_index.md` ✓
- `content/press/_incoming/` contains only `_index.md` (the script's expected subdirectories don't exist — confirmed FileNotFoundError surface) ✓
- `static/documents/press/2026-04-21/` already contains the five committed PDFs that the script would overwrite ✓

All citations accurate.

#### 3. Verification rigour

Verification §1 (no FileNotFoundError) is a direct test of the success criterion. Verification §2 (`ls ... | wc -l` = 5 plus per-file enumeration) confirms output completeness.

**Nit:** Verification §3 (visual sanity-check of one PDF) is reviewer-subjective. The plan acknowledges in its Risks table that "regenerated PDFs differ visually from the committed ones because the published markdown was editorially polished" — so a visual diff against the committed PDFs is *expected* to differ. The plan asks the reviewer to check that "body content [is] present" without specifying *what* content — a reviewer with no inside knowledge has nothing concrete to compare against.

A stronger test: spot-check that the PDF text contains a known-distinctive phrase from each source markdown. For instance, `pdftotext static/documents/press/2026-04-21/childrens-nhs-dental-care.pdf - | grep -F "NHS dental"` should match. This proves structural integrity (parser ran end-to-end, content survived) without requiring visual judgement. The user's question explicitly raised this — "is 'no FileNotFoundError' actually sufficient?" — and the answer is: it proves runnability but not output correctness. The current plan leans on visual inspection for output correctness, which is fine for a single-maintainer site but not as rigorous as a `pdftotext | grep` pipeline would be.

This is a nit, not a blocker, because: (a) the existing committed PDFs are the authoritative artefacts and are not being replaced by this PR (locked Q2 decision), and (b) a structural break in the regenerated PDFs would not affect any shipped artefact — only the maintainer's confidence that the script still works.

#### 4. Atomicity

One commit: `scripts/generate_press_pdfs.py` only, six lines changed (one `SOURCE_DIR`, five `src_md`). Cleanest possible boundary.

#### 5. Risk coverage

Mostly strong. Covers:

- Missing reportlab/Pillow (mitigation: Task 4 includes `pip install`).
- Hardcoded font paths fail on macOS (correctly deferred to Phase 3 BUILD-02).
- Parser crash on unread published files (mitigation: Task 4 surfaces it; if it occurs, edit the markdown not the parser).
- Visual divergence from committed PDFs (acknowledged as expected).
- Future contributor accidentally commits regenerated PDFs (correctly deferred to Phase 4 CI safety nets).
- Phase 2 EMBARGO-02 needing `_incoming/` again (mitigation: minimum-change keeps Phase 2's design space open — explicit and correct).

**Gap:** the plan does not address the user's specific concern about silent output divergence — i.e. the script runs without crashing but produces structurally *different* PDFs from the committed ones (paragraph wrapping shifts, missing pull quotes from a markdown shape the parser handles incorrectly, etc.). The plan's Verification §3 ("body content present") is the only check, and it's qualitative. **Nit:** add a `pdftotext | grep` check on a known phrase per release as a smoke test of structural fidelity. This is ~5 lines added to Verification.

#### 6. Scope discipline

Excellent. The plan explicitly forgoes the optional `Release.src_md` → `slug`-derived refactor (recommended in RESEARCH.md §5 as a 5-line cleanup) on the explicit grounds that Phase 2 (EMBARGO-02) will likely need a different sourcing mechanism (CLI flag or per-release explicit paths) and bundling the cleanup here would lock in design decisions Phase 2 needs to revisit. This is exactly the right call — the plan deliberately stays minimum-change and Phase 2's design space stays open. Risks table line "Optional `Release.src_md` → derived-from-slug refactor leaks into this plan as scope creep" reinforces this discipline.

The plan also correctly flags that committed PDFs are *not* updated by this PR, per the locked Q2 decision in RESEARCH.md §7. This avoids re-publishing artefacts that already shipped on 21 April.

#### 7. Independence claim

Plan 01-02 touches `scripts/generate_press_pdfs.py` only. No overlap with 01-01's files. No CI workflow changes. The Hugo `build` check in CI is trivially affected (the script is not invoked by Hugo), so 01-02's PR will pass branch protection trivially. Independence holds.

### Verdict reasoning

The plan delivers the EMBARGO-01 success criterion exactly and stays inside Phase 1 scope with admirable discipline. Mechanical correctness verified. The one substantive gap is that the verification proves "the script runs" but not "the script produces correct output" — the user explicitly flagged this concern and it is a real, if minor, improvement opportunity. Adding a `pdftotext | grep` smoke test would close it without inflating scope.

### Nits (optional)

1. Verification §3 currently asks for visual inspection only. Add `pdftotext static/documents/press/2026-04-21/<slug>.pdf - | grep -F "<distinctive phrase>"` for at least 2-3 of the 5 releases as a structural smoke test. This proves the parser ran end-to-end and content survived the markdown→PDF pipeline, without needing the reviewer to compare against the committed PDFs.
2. Task 4's `pip install reportlab Pillow` is unpinned — Phase 3 BUILD-02 covers this. The plan correctly defers but it might be worth noting in the PR body's "verification done" paragraph that the install was unpinned-and-current-as-of-2026-04-26, so any future reviewer rerunning the verification has a starting point.

---

## Cross-plan checks

### Independence claim verified?

**Yes.** File-ownership analysis:

| Plan | Files touched |
|------|---------------|
| 01-01 | `layouts/_default/baseof.html`, `content/privacy/_index.md`, `CLAUDE.md`, `.planning/codebase/INTEGRATIONS.md` |
| 01-02 | `scripts/generate_press_pdfs.py` |

Disjoint sets. No shared CI workflow files. No semantic dependency: 01-02's script does not reference any of 01-01's files; 01-01's privacy/banner code does not reference the press toolchain. Either can ship first; both can ship in parallel without merge conflicts.

The only theoretical interaction is via `CLAUDE.md` if Plan 01-02 later decides to update press-toolchain documentation there — but it does not, and the plan's commit boundary is `scripts/generate_press_pdfs.py` only. Confirmed independent.

### Goal coverage when both plans execute together?

**Yes.** All four ROADMAP.md success criteria are covered:

| # | Criterion | Plan | Verification |
|---|-----------|------|--------------|
| 1 | Reject → zero requests to GA hosts | 01-01 | DevTools network tab in clean profile |
| 2 | `/privacy/` renders all H2s as `<h2>` | 01-01 | grep on built HTML |
| 3 | `CLAUDE.md` describes post-fix flow accurately | 01-01 | grep + read-and-compare |
| 4 | Press PDF script runs without `FileNotFoundError` | 01-02 | clean-venv script run |

No gaps. All four PRIVACY-0x / EMBARGO-01 requirements from REQUIREMENTS.md are mapped to specific tasks with reproducible verifications.

---

## Recommendation

**Proceed to execution.** Both plans are sound; the nits identified are quality-of-life improvements (not gaps that prevent goal achievement) and the maintainer can fold them into execution at their discretion. The strongest of the nits — adding `pdftotext | grep` smoke tests to 01-02's verification — would close a genuine but low-likelihood gap in proving structural output fidelity without inflating Phase 1 scope.
