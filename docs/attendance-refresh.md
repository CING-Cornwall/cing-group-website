# Attendance refresh: explicit unavailable fallback

## Current operational contract

The public attendance metric is being moved from CPW's historical all-time
aggregate to **primary Cornwall Council records for the current council term**.
That change is not complete: no date-range query, denominator, or current-term
result has been verified. Do not label a rolling-window figure as current-term.

Until that verification is possible:

- `ATTENDANCE_REFRESH_PAUSED = True` is a deliberate code-level circuit breaker.
  `refresh()` overwrites `.refresh-summary.md` with an explicit unavailable
  report, exits non-zero, and performs **no HTTP requests or councillor YAML
  writes**. A leftover success summary cannot be mistaken for a fresh run.
- The weekly workflow stops at the failed refresh step, before the create-PR
  step. Its schedule and production secrets have not been changed.
- The councillor-page attendance partial displays **Attendance temporarily
  unavailable**, explains the verification gap, and does not show the stored
  percentages or a misleading success tick.
- `data/councillors.yaml` remains byte-for-byte unchanged. Existing percentages
  are historical values, not fresh primary Council evidence. They are retained
  for audit/rollback, not used as a replacement for a failed fetch.
- This pauses the **whole combined refresh**, including committee/outside-body
  updates. That is intentional: no partial data PR should imply that attendance
  has been restored. Existing membership/legacy parsing code is retained for
  offline regression coverage only; it is not an authorised CPW fallback.
- Do not switch the pause off, merge an older attendance-data PR, use CAPTCHA
  automation, proxy CPW, or change any anonymity infrastructure to clear an alert.

## Reconciled evidence (8 October 2026)

- GitHub run `37318950342`, 5 October: all three CPW attendance URLs returned
  HTTP 403; the script raised `all 3 active councillors failed to refresh`.
- Last observed successful scheduled refresh: `36425603526`, 28 September.
  Data PR #67 predates the failure and is not evidence of recovery.
- Proxy PR #66, commit `9ff48b0c4c6889120b892249205a2aaf7a33c844`, remains
  unmerged. It only proxies Council membership requests, not CPW attendance.
  This branch builds on it rather than recreating its changes.
- Read-only probe of the public Council attendance URL
  `https://democracy.cornwall.gov.uk/mgAttendance.aspx?UID=5756`:
  the already authorised Council proxy returned HTTP 200 with a **validation /
  CAPTCHA page**, not attendance data; direct access returned HTTP 404.
  No challenge was solved and no perimeter/configuration changes were made.
  This establishes that the tested paths did not yield attendance, not that
  the Council lacks the underlying records or date-range support.

## Recovery requirements

A separately reviewed source implementation must:

1. Retrieve ordinary public Council attendance records using an authorised path.
   Verify the councillor identity and source-reported start/end dates. Establish
   the current term's exact start and reject silently clamped/default windows.
2. Define attended/expected counts, substitutions, cancellations, and rounding;
   preserve counts and provenance rather than only an unexplained percentage.
3. Store source URL, reporting dates and checked-at timestamp per councillor.
   Show these dates publicly. Never set a fresh timestamp on retained old data.
4. Test 403/404, HTTP-200 challenge pages, malformed/empty data, zero expected
   meetings, wrong councillor/period, partial failure, and unchanged counts.
   Keep last known good data on failure; show an explicit stale/unavailable state.
5. Successfully retrieve and verify all three councillors without publication,
   then replace the legacy CPW code and pause together with the dated display.
6. Obtain separate live authorisation before any publication, merge/deploy,
   hosted refresh, external contact or production configuration change.

## Verification and limits

Run `uv venv .venv`, then
`uv pip install --python .venv/bin/python -r scripts/requirements.txt` and
`.venv/bin/python -m pytest -q` (Hugo required for the partial-render test).

The Hugo test renders the actual attendance partial with repository data and
checks its inclusion in the councillor template. It is **not** a complete site
build: the local Hugo is 0.131.0, while CI pins 0.159.1; compiled Tailwind CSS is
also absent. The attempted Tailwind download/build command was denied by the
local command policy and was not retried or bypassed. Full CI-toolchain site
verification remains required before publication. No hosted workflow was run.

Rollback: review a revert of this fallback commit; it would restore the CPW
refresh/display and therefore also restore the original source/freshness risks.
Prefer leaving the unavailable display in place until primary data is verified.
No data migration, secret rotation, DNS, or infrastructure rollback is needed.
