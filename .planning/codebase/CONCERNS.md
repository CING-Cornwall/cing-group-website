# Codebase Concerns

**Analysis Date:** 2026-04-26

This file catalogues risks, technical debt, and gaps specific to the CING website. The site represents an active group of councillors on Cornwall Council, so reputational, legal (UK GDPR / PECR), and editorial-integrity risks are weighted alongside engineering concerns.

---

## HIGH

### Privacy policy contradicts actual analytics behaviour

- **What:** The privacy page tells visitors "If you reject cookies, no analytics cookies are set and **no data is sent to Google**", but `baseof.html` injects the GA script unconditionally on every production page load.
- **Where:** `content/privacy/_index.md` (lines around the cookies table) vs. `layouts/_default/baseof.html:8-35`. The `<script>` block at lines 26-31 dynamically appends `https://www.googletagmanager.com/gtag/js?id=G-Z1F4F1TRD0` to `document.head` regardless of consent state. With Consent Mode v2, denying `analytics_storage` suppresses cookies but Google still receives a "cookieless ping" (URL, referrer, IP, user-agent). That is processing of personal data under UK GDPR.
- **Why it matters:** A councillor group's website making an inaccurate privacy claim is a direct ICO/PECR exposure and a political-reputation risk. Opponents could reasonably point at this.
- **Suggested action:** Either (a) move the `gtag/js` script injection inside the `if (localStorage.getItem('cing-cookies') === 'accepted')` branch so nothing leaves the browser without consent, or (b) update the privacy copy to describe Consent Mode v2 accurately ("we use Google Consent Mode — denying consent stops cookies and personalised data, but anonymous pings to Google still occur").

### `main` branch is unprotected

- **What:** The `main` branch on `CING-Cornwall/cing-group-website` has no branch protection (`"protected":false` in the GitHub API response). Anyone with write access can force-push, and any push triggers an immediate production deploy.
- **Where:** GitHub repo settings; deploy workflow `.github/workflows/hugo.yml:3-6` (push to `main` deploys live).
- **Why it matters:** A single accidental commit (e.g. an unfinished press release, a leaked draft, a typo in a councillor's name) goes straight to `www.cingparty.uk` with no review gate. For a political group whose voice is the site, "deployed-by-mistake" content is a real risk — see the recent embargo lifted by commit `94e7625`.
- **Suggested action:** Enable branch protection on `main`: require pull request before merge, require at least 1 review, require the Hugo build to pass before merge, and disallow force-push. At minimum, add the "require pull request" rule even with self-review (it preserves a deploy-preview window).

### Embargo workflow has no automated safeguard

- **What:** Embargoed press releases rely entirely on a manual `publishDate` front-matter value plus a manual commit ("Lift embargo: publish Full Council 21 April 2026 press releases"). Hugo respects `publishDate` only at *build time* — and CI builds only fire on push, so a post-dated release is *not* automatically published when the date arrives.
- **Where:** `content/press/full-council-2026-04-21/*.md` all have `publishDate: 2026-04-20T09:00:00+01:00`. The deploy workflow `.github/workflows/hugo.yml` has no `schedule:` trigger, so no nightly rebuild exists.
- **Why it matters:** Two failure modes: (1) the embargo lift is forgotten and the release sits unpublished past the embargo time; (2) more dangerously, a draft committed to `main` with a "future" `publishDate` is still part of the repo — anyone can read it via the public `git` history *before* the embargo. The current workflow protected against (1) by relying on a human commit ("Lift embargo: publish…"), which is exactly the manual gate that should not be the only safeguard.
- **Suggested action:** Two complementary fixes. (a) Keep embargoed drafts out of the main branch entirely until embargo lifts — use `content/press/_incoming/` (which already has `cascade.build.render: never`) or a separate `embargo` branch. (b) Add a `schedule: { cron: "0 7,9,12,17 * * *" }` trigger to `hugo.yml` so post-dated content automatically publishes when its `publishDate` passes, even without a new commit.

### `councillors.yaml` is hand-maintained with no refresh, no validation

- **What:** `data/councillors.yaml` is the single source of truth for councillor names, divisions, committees, attendance %, and bios — all of which change frequently in council life. There is no GitHub Action to refresh attendance from the council website, no schema validation, and no review step. CLAUDE.md explicitly notes the cron-refresh is a "Phase 2 plan" that has not landed.
- **Where:** `data/councillors.yaml` (44 lines, 3 councillors). `.github/workflows/` contains only `hugo.yml` — no refresh job. The file is consumed by `layouts/councillors/list.html:59` and `layouts/about/list.html:89`.
- **Why it matters:** Stale committee membership, attendance figures, or division names on a councillor's page is the kind of thing political opponents weaponise ("CING claims 95% attendance — actually 71%"). And if a councillor leaves the group, the YAML would still publish them as members until someone manually edits it. Karen Knight's photo (9.6 KB) also looks under-resourced compared to the other two — suggests the data ingest is informal.
- **Suggested action:** (a) Add a JSON-Schema or `dataschema/councillors.yaml` and validate on every PR. (b) Build the Phase-2 cron: a GitHub Action that scrapes Cornwall Council's committee membership and attendance pages weekly, opens a PR with the diff. (c) Add an `active: true` boolean per councillor so departures are a one-line edit.

### Tailwind Play CDN in production

- **What:** The site loads `https://cdn.tailwindcss.com?plugins=forms,container-queries` on every page. Tailwind's own docs explicitly state the Play CDN is "intended for development purposes only" and not for production.
- **Where:** `layouts/_default/baseof.html:109`. The inline `tailwind.config = {...}` block at lines 110-173 (~63 lines of MD3 colour tokens) only takes effect *after* the CDN script executes, which causes a brief FOUC (flash of unstyled content) on slow connections.
- **Why it matters:** (1) Render-blocking ~60KB JS in `<head>` on every page; (2) class generation happens client-side on every visit; (3) third-party CDN dependency for the entire visual identity — if the CDN goes down or returns 5xx, the site is unstyled; (4) the CDN itself is on notice for deprecation. For a political group whose competence judgement is partly visual, an unstyled `www.cingparty.uk` is an embarrassment.
- **Suggested action:** Move to a build-time Tailwind setup. Hugo Pipes (Hugo Modules + a small `package.json` for Tailwind CLI) or a pre-built static `assets/css/tailwind.css` compiled in CI. This also lets the MD3 tokens live in a real `tailwind.config.js` rather than an inline `<script>`.

### Unoptimised hero/landscape images (~500-700 KB each, no WebP, no responsive variants)

- **What:** `static/images/` contains 18 large landscape JPGs in the 270 KB-700 KB range, all served as-is to every device. None are output in WebP/AVIF, none have `srcset`/`<picture>`, none use `loading="lazy"`, and none have intrinsic `width`/`height` attributes (so layout shift is also a concern).
- **Where:** `static/images/granite-texture.jpg` (698 KB), `harbour-boats.jpg` (575 KB), `cornish-garden.jpg` (533 KB), plus 15 others. Reference points: `layouts/index.html:9-13` (`hero-coastline.jpg` background, no `loading`), `layouts/press/list.html:175` (granite texture as overlay). `grep` for `loading="lazy"`, `srcset`, `picture`, `webp` across `layouts/` returns nothing.
- **Why it matters:** A `/policies/` page references `cliffside-dusk.jpg`, `eco-building.jpg`, `moorland-hills.jpg`, `harbour-boats.jpg`, `dramatic-coast.jpg`, `cornish-garden.jpg`, `fishing-village.jpg` — that's ~3 MB of decorative imagery on a single page, all blocking initial paint. Mobile users on rural Cornish 4G will feel it. Largest Contentful Paint will be poor → SEO penalty. For a public-facing political site, "slow on mobile" is a tangible engagement loss.
- **Suggested action:** Use Hugo's image processing (`resources.GetMatch | .Resize | .Process "webp"`) to emit responsive `srcset` variants at build time. Add `loading="lazy"` to every `<img>` outside the initial viewport. Add explicit `width=` and `height=` to all hero images to lock CLS.

---

## MEDIUM

### Press release PDF/hero scripts have no pinned dependencies and assume host-system fonts

- **What:** `scripts/generate_press_pdfs.py` and `scripts/generate_press_heroes.py` import `reportlab` and `Pillow` with no `requirements.txt`, `pyproject.toml`, or version pins anywhere in the repo. Both also hard-code absolute font paths from a Debian-flavoured Linux system.
- **Where:** `scripts/generate_press_pdfs.py:53-61` (`/usr/share/fonts/truetype/google-fonts/Poppins-*.ttf`, `/usr/share/fonts/truetype/lato/Lato-*.ttf`); `scripts/generate_press_heroes.py:41-44` (same paths). No requirements file in repo root.
- **Why it matters:** The next person (or the same person on a different machine) cannot reproducibly regenerate the PDFs that ship in `static/documents/press/`. If the council asks for a corrected version of a release, font files might not be in those exact paths and the scripts will crash with a `FileNotFoundError` on import. The PDFs are the press-grade artefact — they need to be reproducible.
- **Suggested action:** Add `scripts/requirements.txt` with pinned `reportlab==X.Y.Z` and `Pillow==X.Y.Z`. Bundle the four required TTFs into `scripts/fonts/` (Manrope and Public Sans are SIL-OFL — redistributable). Replace the hard-coded paths with `Path(__file__).parent / "fonts" / "Poppins-Bold.ttf"`. Optionally add a tiny `make press-pdfs` target that uses `uv` or `python -m venv` for hermetic execution.

### Press scripts read from a path that no longer exists

- **What:** `generate_press_pdfs.py` reads source markdown from `content/press/_incoming/<subdir>/<file>.md`, but the published releases have already been moved into `content/press/full-council-2026-04-21/` and `_incoming/` now contains only `_index.md`.
- **Where:** `scripts/generate_press_pdfs.py:37` (`SOURCE_DIR = ROOT / "content" / "press" / "_incoming"`) and the `RELEASES` list at lines 122-163 referencing `_incoming / "11.1 Mevagissey Families" / "..."` etc. These paths do not exist in the working tree any more.
- **Why it matters:** Re-running `python scripts/generate_press_pdfs.py` *today* will fail with `FileNotFoundError` for every release. The artefact in `static/documents/press/2026-04-21/*.pdf` is locked to a snapshot of the (now-gone) source markdown. If a typo is found in any of the five live PDFs, the script can't regenerate them without first restoring the source files.
- **Suggested action:** Either (a) make the script re-read from the canonical published location (`content/press/full-council-2026-04-21/*.md`) so it stays runnable, or (b) preserve the originals in `content/press/_incoming/` (which the cascade already excludes from publishing) so the script remains the single source for PDFs.

### Privacy page has malformed markdown headings

- **What:** Multiple H2 headings in the privacy policy are missing the space after `##`, so they render as literal text instead of headings.
- **Where:** `content/privacy/_index.md` lines 9 (`##What data we collect`), 51 (`##Data retention`), 55 (`##Your rights`), 66 (`##Contact us`). Lines 16, 31, 41 are correctly formatted.
- **Why it matters:** Visitors see "##What data we collect" as plain inline text on the only legally-significant page on the site. It looks unprofessional and degrades the document's standing as an actual privacy policy.
- **Suggested action:** Insert the missing space on each affected line. Consider adding a markdown-lint pre-commit hook (`markdownlint-cli2`) to catch this class of error going forward.

### CLAUDE.md description of GA loading is wrong

- **What:** The project's own AI guidance file says GA "is loaded only in production builds … and **only after the user accepts cookies**" and refers to a "`loadGtag()` function". That function does not exist; GA loads unconditionally in production via Consent Mode v2.
- **Where:** `CLAUDE.md:89-91` vs. actual implementation at `layouts/_default/baseof.html:8-35`.
- **Why it matters:** Future AI-assisted edits will be made on a wrong mental model of the privacy posture. Combined with the privacy-page contradiction (HIGH item above), this is the kind of drift that compounds into compliance bugs. Also, when a developer fixes the privacy issue, they should fix the doc at the same time.
- **Suggested action:** Rewrite that paragraph in `CLAUDE.md` to match reality: "GA loads on every production page via the standard `gtag/js` snippet. Storage is denied by default through Google Consent Mode v2, and granted only after the user accepts via the cookie banner. Local-dev (`hugo server`) is unaffected."

### Forms have no spam protection and no GDPR consent ticks

- **What:** All four Formspree-backed forms accept submissions with no honeypot field (`_gotcha`), no captcha, and no explicit GDPR consent checkbox. The newsletter form in particular ("Subscribe") has no opt-in tickbox — UK PECR (regulation 22) requires explicit consent for marketing email.
- **Where:** Contact form `layouts/get-involved/list.html:108-143`; newsletter `layouts/get-involved/list.html:155-162`; press newsletter `layouts/press/list.html:147-164`; homepage newsletter `layouts/index.html:205`. All lack `<input type="checkbox" name="consent" required>` and `<input type="text" name="_gotcha" style="display:none">`.
- **Why it matters:** (a) Spambots will harvest these forms and fill the shared Formspree inbox. (b) Adding a subscriber to a marketing list without a recorded explicit opt-in is a PECR breach — small fines but loud reputational damage when the group's whole pitch is "we listen to residents". (c) The disclaimer "By submitting, you agree to our privacy policy" is *implied* consent, which is not sufficient for marketing under PECR.
- **Suggested action:** Add a hidden `_gotcha` honeypot to each form. Add an explicit `<input type="checkbox" name="marketing_consent" required>` to both newsletter forms with text like "I agree to receive email updates from CING". Keep the existing privacy-policy link.

### All four forms share one Formspree endpoint

- **What:** Every form on the site posts to the same `formspreeId` (`mvzvgdbl`). Contact enquiries, two newsletter subscribes, and the press-list newsletter all merge into one inbox. Only the `_subject` hidden field disambiguates them.
- **Where:** `hugo.toml:8` (single `formspreeId`); used in `layouts/get-involved/list.html:108`, `:155`, `layouts/index.html:205`, `layouts/press/list.html:147`.
- **Why it matters:** (a) "Subscribe to newsletter" submissions land in the same inbox as "general enquiry" — the office has to triage. (b) Rotating the press-distribution list means dragging individual emails out of a mixed pile. (c) Formspree's free tier is 50 submissions/month total across all four forms — easy to hit during a high-engagement week. (d) Distinct endpoints per form let you wire each to the right downstream (Mailchimp/Buttondown for newsletters, an inbox or CRM for enquiries).
- **Suggested action:** Create three Formspree forms (contact, newsletter, press list) and store the IDs as `params.formspreeContactId` / `formspreeNewsletterId` / `formspreePressId` in `hugo.toml`. For the newsletter forms specifically, consider switching to a real ESP (Buttondown or MailerLite) — Formspree → manual list curation does not scale.

### Alt text on hero images is decorative-as-content

- **What:** Many hero images use descriptive alt text ("Dramatic Cornish coastline", "Cornish Coastline", "Cornish cliffs at dusk") on what are purely *decorative* full-bleed background images. Conversely, news and press hero images use `alt="{{ $.Title }}"`, which duplicates the headline screen-reader users will have already read in `<h1>`.
- **Where:** Decorative-with-alt: `layouts/index.html:11`, `layouts/about/list.html:7`, `layouts/get-involved/list.html:25-27`, `layouts/policies/policies.html:6`, `layouts/councillors/list.html:7`, `layouts/press/list.html:7`. Title-duplicating: `layouts/news/single.html:56`, `layouts/press/single.html:28`, `layouts/_default/list.html:49`, `layouts/index.html:166`.
- **Why it matters:** WCAG 1.1.1 — decorative images should have `alt=""` so screen readers skip them, and *informative* images should have content-equivalent alt text. The current pattern is the inverse: noise on decorative images, redundancy on informative ones. Any RNIB/AbilityNet audit will flag this.
- **Suggested action:** For decorative full-bleed heroes, set `alt=""` and `role="presentation"`. For news/press hero images, write alt text describing what the image *shows* (e.g. for the dental-care release: "A child at a dental check-up"), not the article title.

### Councillor photo set is inconsistent and small

- **What:** Of three councillors, photo file sizes are 100 KB (Anna), 26 KB (Rowland), and 9.6 KB (Karen Knight) — Karen's image is almost certainly low-resolution and will look pixelated next to the others, especially when the `grayscale → grayscale-0` hover effect zooms it.
- **Where:** `static/images/councillors/anna-thomason-kenyon.jpg` (100 KB), `rowland-oconnor.jpg` (26 KB), `karen-knight.jpg` (9.6 KB). Used in `layouts/councillors/list.html:73` and `layouts/about/list.html:94, :104` plus `layouts/index.html:130` (32x32 avatar).
- **Why it matters:** A visibly lower-quality portrait of one member breaks the editorial consistency the design system aims for and looks like Karen has been treated as an afterthought — exactly the wrong signal for an "all councillors equal" group.
- **Suggested action:** Commission a fresh portrait at the same resolution and aspect ratio as Anna's (≈1024px wide, ≈100 KB JPEG quality 86). Standardise all three to the same dimensions and crop, and check them with the grayscale filter applied.

### No 404 page

- **What:** There is no `layouts/404.html`, so Hugo doesn't generate a `404.html` and GitHub Pages serves its default ("404 — File not found").
- **Where:** Absent — `ls layouts/_default/` shows only `baseof.html`, `list.html`, `single.html`, `sitemap.xml`.
- **Why it matters:** Stale press-release URLs, mistyped councillor names, and inbound social shares hitting renamed pages all land on a generic GitHub error page with no CING branding, no nav, and no "back to home" link. Visitors who land there from social media often leave.
- **Suggested action:** Add `layouts/404.html` with the CING header/footer and a "back to home / news / councillors" choice. Hugo will emit `public/404.html` and GitHub Pages serves it automatically.

---

## LOW

### No automated tests of any kind

- **What:** No unit tests, no link-checker, no HTML validator, no accessibility scan in CI. The deploy pipeline is simply `hugo --gc --minify`.
- **Where:** `.github/workflows/hugo.yml` — only build + deploy steps.
- **Why it matters:** A typo in a Hugo template (e.g. `{{ .Sit.Title }}`) breaks the build and is caught by `hugo` itself, but a broken internal link, a missing image, or a regression in colour contrast against MD3 tokens won't be. For a content-driven site this is normally acceptable, but it limits how confidently changes can be made.
- **Suggested action:** Two cheap wins: (a) add `lychee` (link checker) as a CI step on PRs only — runs in seconds against `public/`; (b) add `pa11y-ci` against five canonical URLs (home, about, councillors, news, get-involved) with a 0-error budget. No need for a full test framework.

### `disableKinds = ["taxonomy", "term"]` blocks future categorisation

- **What:** `hugo.toml:51` disables Hugo's taxonomy system. News posts have a `category` front-matter field but it's purely cosmetic — no `/category/community/` index page can be generated.
- **Where:** `hugo.toml:51`. `category` field used in `content/news/*.md` and `content/press/*/*.md`.
- **Why it matters:** Once there are 20+ news posts and 20+ press releases, "show me everything tagged Planning" or "everything tagged NHS" will be the natural reader behaviour. Re-enabling taxonomies later means rewriting URLs.
- **Suggested action:** When the news/press archive grows past ~10 posts each, re-enable the `category` taxonomy and add `layouts/_default/taxonomy.html` + `term.html`. Decide on URL scheme up-front (`/topics/planning/` is cleaner than the default `/categories/planning/`).

### Stitch reference is gitignored — no drift detection

- **What:** `.reference/` (Stitch HTML exports — the design source of truth per CLAUDE.md) is gitignored. There is no automated visual regression check between the live site and the Stitch reference.
- **Where:** `.gitignore:4` excludes `.reference/`. CLAUDE.md describes Stitch as "the design source of truth — the 'CING Brand Update' variants are the preferred references" but offers no drift-detection mechanism.
- **Why it matters:** As Tailwind classes drift across many template edits, the live site can quietly diverge from the Stitch design without anyone noticing until a stakeholder spots it. For a brand-conscious group, "looks slightly off compared to the design we approved" is a reasonable complaint.
- **Suggested action:** Either (a) commit the relevant Stitch exports under `docs/brand/stitch-snapshots/` (small HTML files — they don't bloat the repo) so the design intent is reviewable in PRs, or (b) add a Playwright visual-regression run against a handful of pages with screenshots committed alongside the layouts.

### `{{ .Site.Copyright | safeHTML }}` in the footer

- **What:** `layouts/partials/footer.html:47` renders the site copyright string with `safeHTML`, which trusts the value. It currently comes from `hugo.toml:4` so it's safe, but `safeHTML` defeats Hugo's automatic HTML escaping.
- **Where:** `layouts/partials/footer.html:47`.
- **Why it matters:** Low risk because the value is in `hugo.toml` (under repo control), but if anyone ever wires this to user input or a CMS, it becomes an XSS vector. Worth flagging because the only other `safeHTML` use (sitemap XML preamble) is genuinely necessary.
- **Suggested action:** The fallback already uses `&copy;` which Go templates would otherwise escape, hence the `safeHTML`. Replace `&copy;` with the literal `©` character in both the hugo.toml and the fallback, and drop `safeHTML`.

### Hugo version pin is exact, no Dependabot

- **What:** `.github/workflows/hugo.yml:25` pins `HUGO_VERSION: 0.159.1` exactly with no automation to bump it. Hugo regularly ships security/perf fixes.
- **Where:** `.github/workflows/hugo.yml:25`.
- **Why it matters:** Mid-tier — the pin is correct (reproducible builds) but there's nothing nudging it forward. The site will still be on 0.159 a year from now unless someone manually bumps it.
- **Suggested action:** Add `.github/dependabot.yml` with a `github-actions` ecosystem entry. Dependabot will open a PR when Hugo (and the action versions) ship updates.

### Hugo build artefact `public/` and `resources/` not in `.gitignore` consistently

- **What:** Both `public/` and `resources/` are gitignored (`.gitignore:1-2`) but `public/` exists in the working tree (per the initial `ls`). That suggests it has been accidentally tracked in the past or generated locally.
- **Where:** `.gitignore:1-2`; `public/` directory present in repo root.
- **Why it matters:** Risk of someone running `git add -A` and accidentally committing built output, which then competes with the GH-Actions deploy.
- **Suggested action:** Confirm `public/` is not tracked (`git ls-files public/`); if any files leaked, `git rm -r --cached public/`.

### `summaryLength = 30` is short

- **What:** `hugo.toml:44` sets `summaryLength = 30` (words). News-list cards will show truncated previews that feel abrupt.
- **Where:** `hugo.toml:44`.
- **Why it matters:** Cosmetic, but the news/press list templates rely on `excerpt` front matter rather than auto-summary anyway — so the setting may be ineffective and misleading. Worth either using or removing.
- **Suggested action:** Either bump to 60-70 words and use `.Summary` in `layouts/news/list.html`, or remove the setting and continue relying on `excerpt`.

---

*Concerns audit: 2026-04-26*
