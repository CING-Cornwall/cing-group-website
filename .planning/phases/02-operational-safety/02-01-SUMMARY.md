---
phase: 02-operational-safety
plan: 01
subsystem: ci/embargo
tags:
  - ci
  - github-actions
  - embargo
  - press
  - schedule
requires: []
provides:
  - "Schedule trigger (4x daily UTC) on hugo.yml"
  - "Embargo guard CI step that fails build on future-dated press outside _incoming/"
  - "Deploy job fires on schedule events too"
affects:
  - .github/workflows/hugo.yml
tech_stack_added: []
patterns_used:
  - "GitHub Actions schedule: trigger (UTC cron)"
  - "Inline python3 heredoc step on ubuntu-latest runner"
  - "md.parts membership exclusion (not substring) for trusted-staging directories"
key_files_created: []
key_files_modified:
  - .github/workflows/hugo.yml
decisions:
  - "Cron expressed in UTC (0 7,9,12,17 * * *) with TZ: Europe/London on the build env so Hugo's publishDate comparisons read in UK time. DST drift accepted for 4x-daily cadence."
  - "Embargo guard implemented as inline python3 heredoc (no actions/setup-python) — runners ship python3 and ISO-8601 parsing is fiddly in awk."
  - "Guard uses 'if \"_incoming\" in md.parts' rather than substring match so a sibling file like '_incoming-notes.md' cannot bypass."
  - "Deploy gate broadened to push || schedule (not push || schedule || pull_request) — PR builds remain build-only."
metrics:
  duration_minutes: 6
  tasks_completed: 3
  files_touched: 1
  commits: 3
  completed_date: "2026-04-26"
requirements_completed:
  - EMBARGO-02
  - EMBARGO-03
---

# Phase 2 Plan 01: Embargo Workflow CI Hardening Summary

Added a 4x-daily cron trigger and a Python embargo-guard step to `.github/workflows/hugo.yml` so future-dated press files outside `content/press/_incoming/` fail CI, and so post-dated press publishes automatically when its `publishDate` passes — no human commit required.

## Files Modified

- `.github/workflows/hugo.yml` (3 edits across 3 commits)

No new files. CONTEXT D-discretion explicitly required staying within the existing single-workflow file.

## Tasks Completed

### Task 1 — Schedule trigger + broadened deploy gate

**Commit:** `32db0c2` — `ci(02-01): add schedule trigger and broaden deploy gate`

Acceptance proofs:

```
$ grep -E '^\s+schedule:' .github/workflows/hugo.yml
  schedule:

$ grep -F 'cron: "0 7,9,12,17 * * *"' .github/workflows/hugo.yml
    - cron: "0 7,9,12,17 * * *"

$ grep -F "github.event_name == 'push' || github.event_name == 'schedule'" .github/workflows/hugo.yml
    if: github.event_name == 'push' || github.event_name == 'schedule'

$ python3 -c "import yaml; yaml.safe_load(open('.github/workflows/hugo.yml'))"
(exit 0)
```

`schedule:` is nested under `on:` alongside `push:`, `pull_request:`, `workflow_dispatch:` (verified by reading the file). All Task 1 acceptance criteria pass.

### Task 2 — Embargo guard step

**Commit:** `b1ed4cc` — `ci(02-01): add embargo guard step before Build with Hugo`

Acceptance proofs:

```
$ grep -c 'Embargo guard' .github/workflows/hugo.yml
3                # 1 step name, 1 stderr message, 1 success message

$ python3 -c "import yaml; yaml.safe_load(open('.github/workflows/hugo.yml'))"
(exit 0)

$ grep -F '"_incoming" in md.parts' .github/workflows/hugo.yml
              if "_incoming" in md.parts:
```

**Dry-run against current tree:**

```
$ python3 - <<'PY'
... full guard logic ...
print("OK" if not violations else f"VIOLATIONS: {violations}")
PY
OK

$ # plan-style strict assertion
$ python3 -c "...assert not v..."
clean
```

The five existing `content/press/full-council-2026-04-21/*.md` files all have `publishDate: 2026-04-20T09:00:00+01:00` (in the past on 2026-04-26), and `_incoming/` is excluded — guard returns clean.

**Step-ordering proof (deviation note below):**

```
$ awk '/- name: Embargo guard/{e=NR} /- name: Build with Hugo/{b=NR} END{print e, b}' .github/workflows/hugo.yml
47 76

$ sed -n '/- name: Embargo guard/,/- name: Build with Hugo/p' .github/workflows/hugo.yml | grep -c '^      - name:'
2                # only the guard step and the Build step appear in this range
```

No other step appears between them — the guard IS the immediate predecessor step.

### Task 3 — Top-of-file embargo workflow comment + YAML validation

**Commit:** `9429763` — `docs(02-01): document embargo workflow at top of hugo.yml`

Acceptance proofs:

```
$ python3 -c "import yaml; yaml.safe_load(open('.github/workflows/hugo.yml'))"
(exit 0)

$ grep -c '^# Embargo workflow:' .github/workflows/hugo.yml
1

$ actionlint .github/workflows/hugo.yml
/usr/bin/bash: line 1: actionlint: command not found
```

**actionlint availability:** NOT installed locally (verified via `which actionlint` → exit 1). Per the plan, this is acceptable; falling back to `python3 -c yaml.safe_load(...)` for syntactic validation. CI itself will surface any GitHub-Actions-specific issues on the next push.

File order verified by reading lines 1–25:

1. `name: Deploy Hugo site to GitHub Pages`
2. *(blank)*
3. `# Embargo workflow:` block (6 comment lines)
4. *(blank)*
5. `on:` (with `push`, `pull_request`, `workflow_dispatch`, `schedule`)

Matches the plan's required order exactly.

## Final Verification (plan `<verification>` block)

| # | Check | Result |
|---|-------|--------|
| 1 | Schedule trigger present (`grep cron`) | PASS |
| 2 | Deploy gate broadened (`grep push \|\| schedule`) | PASS |
| 3 | Guard step exists (3 occurrences of "Embargo guard") | PASS |
| 4 | YAML valid (`python3 -c yaml.safe_load`) | PASS |
| 5 | Guard dry-run prints `clean` | PASS |

## Deviations from Plan

### 1. [Rule 1 — Plan glitch] Step-ordering acceptance criterion was unsatisfiable as literally written

**Found during:** Task 2 verification.

**Issue:** The plan's acceptance criterion `grep -B1 'Build with Hugo' .github/workflows/hugo.yml | grep -c 'Embargo guard'` returns 1 expects the line *immediately above* `Build with Hugo` to contain "Embargo guard". But because the guard step uses an inline `python3 - <<'PY'` heredoc, the line immediately above `- name: Build with Hugo` is `PY` (the heredoc terminator), not the guard step's `name:` line. The literal grep returns 0.

**Fix:** Confirmed correct ordering with a structural proof instead — `sed -n '/- name: Embargo guard/,/- name: Build with Hugo/p' | grep -c '^      - name:'` returns 2, meaning only the guard step's `name:` and the `Build with Hugo` step's `name:` appear in that range. There is no intervening step. The guard IS immediately before Build with Hugo as a step.

**No file change required** — this is a documentation deviation, not a code deviation.

**Files modified:** None.

**Commit:** N/A (proof only).

## Threat Surface Scan

No new threat surface introduced. The plan's threat register (T-02-01-01..05) is implemented as designed:

- T-02-01-01 (misnamed-file bypass): mitigated via `md.parts` membership check (verified present in committed file).
- T-02-01-02 (future-dated press leak): mitigated — guard runs before `Build with Hugo`, so violation prevents artifact production.
- T-02-01-03 (silent embargo lift): mitigated — schedule fires 4x daily; deploy gate broadened to fire on schedule events.
- T-02-01-04 (manual write to main): accepted (pre-existing branch protection, guard runs in required `build` check).
- T-02-01-05 (cron unreliability): accepted (4x redundancy; visible in Actions tab).

No new endpoints, auth paths, or trust boundaries.

## Known Stubs

None — this is a pure CI-infrastructure plan. No UI, no runtime data flow.

## Self-Check: PASSED

**Files claimed:** `.github/workflows/hugo.yml`
- FOUND: `.github/workflows/hugo.yml` (modified, 79 lines)

**Commits claimed:**
- FOUND: `32db0c2` (ci(02-01): add schedule trigger and broaden deploy gate)
- FOUND: `b1ed4cc` (ci(02-01): add embargo guard step before Build with Hugo)
- FOUND: `9429763` (docs(02-01): document embargo workflow at top of hugo.yml)

All artefacts and commits verified present in git history.
