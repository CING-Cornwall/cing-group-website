# External Integrations

**Analysis Date:** 2026-04-26

## APIs & External Services

**Form handling:**
- **Formspree** - Handles all contact and newsletter form submissions for the static site (no backend needed).
  - Form ID `mvzvgdbl` defined once at `hugo.toml:8` (`params.formspreeId = "mvzvgdbl"`).
  - Endpoint pattern: `https://formspree.io/f/{{ .Site.Params.formspreeId }}` (POST).
  - Used in:
    - `layouts/get-involved/list.html:108` - main contact form.
    - `layouts/get-involved/list.html:155` - newsletter signup on Get Involved page.
    - `layouts/index.html:205` - homepage newsletter form.
    - `layouts/press/list.html:147` - press page enquiry form.
  - SDK/Client: None - plain HTML `<form action method="POST">`.
  - Auth: None client-side; the form ID itself routes submissions to the Formspree account.

**Analytics:**
- **Google Analytics 4 (gtag.js)** - Privacy-aware, consent-gated traffic analytics.
  - Measurement ID `G-Z1F4F1TRD0`, declared once as a `GA_ID` constant inside the `window.loadGtag()` function in `layouts/_default/baseof.html` and used both as the `<script>` src parameter and the `gtag('config', ...)` argument.
  - Implementation: strict script-load gating. The `gtag/js` `<script>` tag is not injected at all until the visitor clicks Accept on the cookie banner — pre-consent (and after Reject) the page makes zero requests to `googletagmanager.com` or `google-analytics.com`. `loadGtag()` is called from two places: at page load if `localStorage.getItem('cing-cookies') === 'accepted'`, and from the cookie banner's Accept handler. A `gtagLoaded` flag makes the function idempotent.
  - Production-only: entire snippet wrapped in `{{ if hugo.IsProduction }}`, so local `hugo server` builds never load gtag at all.

**Fonts (third-party CDNs):**
- **Google Fonts (Manrope, Public Sans)** - Headline and body typography.
  - Loaded at `layouts/_default/baseof.html:176`: `https://fonts.googleapis.com/css2?family=Manrope:wght@400;700;800&family=Public+Sans:wght@300;400;500;600&display=swap`.
  - Preconnect hints at `layouts/_default/baseof.html:105-106` (`fonts.googleapis.com`, `fonts.gstatic.com`).
- **Google Fonts (Material Symbols Outlined)** - Icon font (variable, axes `wght`, `FILL`).
  - Loaded at `layouts/_default/baseof.html:177`.
  - Default rendering settings via `.material-symbols-outlined` rule at `layouts/_default/baseof.html:180-182`.

**CSS framework CDN:**
- **Tailwind Play CDN** - JIT Tailwind compiled in the browser.
  - URL: `https://cdn.tailwindcss.com?plugins=forms,container-queries` (`layouts/_default/baseof.html:109`).
  - Configuration injected inline immediately after at `layouts/_default/baseof.html:110-173` (theme tokens, fonts, radii). No version is pinned.

## Data Storage

**Databases:** None. The site is fully static.

**Structured data sources (build-time, file-based):**
- `data/councillors.yaml` - Read by templates via `{{ $councillors := index hugo.Data "councillors" }}`. Drives `/councillors/` and `/about/` pages.
- `content/news/*.md` - News post markdown.
- `content/press/**` (incl. `_incoming/` consumed by `scripts/generate_press_pdfs.py:37`) - Press release content.

**File storage:** Local filesystem only. Static assets live under `static/` and are copied verbatim to `public/` at build time (favicons, hero images, PDFs at `static/documents/press/2026-04-21/`, etc.).

**Caching:**
- Hugo build cache: `HUGO_CACHEDIR: ${{ runner.temp }}/hugo_cache` (`.github/workflows/hugo.yml:41`).
- Browser caching is governed by GitHub Pages defaults; no custom cache headers configured.

## Authentication & Identity

- None. The site has no user accounts, no admin area, and no authenticated routes.
- The only "identity" surface is form submission via Formspree, which uses no client-side auth.

## Monitoring & Observability

- **Error tracking:** None. No Sentry, Rollbar, or equivalent integration is wired up.
- **Logs:** None client-side beyond the browser console; no structured logging.
- **Uptime monitoring:** Not configured in repository.

## CI/CD & Deployment

**Hosting:**
- **GitHub Pages** - Custom domain `www.cingparty.uk` declared in `static/CNAME:1` (Hugo copies this to the root of the deployed site).
- HTTPS handled automatically by GitHub Pages.

**CI Pipeline:**
- **GitHub Actions** - Single workflow `.github/workflows/hugo.yml`.
  - Triggers: `push` to `main`, plus `workflow_dispatch` (`.github/workflows/hugo.yml:3-6`).
  - `build` job: installs Hugo `0.159.1` from the official `.deb`, checks out with `submodules: recursive` and `fetch-depth: 0`, runs `hugo --gc --minify --baseURL "https://www.cingparty.uk/"`, uploads `./public` as a Pages artefact.
  - `deploy` job: deploys via `actions/deploy-pages@v4` to environment `github-pages` (`.github/workflows/hugo.yml:54-63`).
  - Concurrency group `pages` with `cancel-in-progress: false` prevents overlapping deploys (`.github/workflows/hugo.yml:13-15`).
  - No scheduled / cron workflows are present (the planned councillor data auto-refresh in the project README is not yet implemented).

## Environment Configuration

**Required env vars:**
- None at runtime (static site).
- CI-only: `HUGO_VERSION` (`.github/workflows/hugo.yml:25`), `HUGO_CACHEDIR`, `HUGO_ENVIRONMENT=production`, `TZ=Europe/London` (`.github/workflows/hugo.yml:40-43`).

**Secrets location:**
- None. No `.env*` files, no `secrets.*`, no GitHub Actions `${{ secrets.* }}` references in workflows. All third-party identifiers (Formspree form ID, GA measurement ID) are public-by-design and committed to source.

## Webhooks & Callbacks

- **Incoming:** None. The site has no server endpoints to receive webhooks.
- **Outgoing:** Form submissions POST to `https://formspree.io/f/mvzvgdbl`. Formspree itself can be configured (in its dashboard, outside this repo) to forward via email or webhook, but no such configuration lives in the codebase.

## Cookie Consent

- **Mechanism:** First-party cookie banner rendered by `layouts/_default/baseof.html:218-262`, gated by `{{ if hugo.IsProduction }}` so it never appears in local development.
- **Storage key:** `cing-cookies` in `localStorage`.
  - Read on page load: `localStorage.getItem('cing-cookies')` at `layouts/_default/baseof.html:22` and `:243`.
  - Values: `accepted` or `rejected`, written at `baseof.html:248` and `:255`.
- **Effect on GA:** Choosing "Accept" calls `gtag('consent', 'update', { 'analytics_storage': 'granted' })` (`baseof.html:250-252`); "Reject" calls the same with `'denied'` (`baseof.html:257-259`). The banner hides on either choice and does not reappear unless the key is cleared.
- **Cookie policy link:** `/privacy/#cookies` (`baseof.html:227`).

## Design Tooling (External, Non-Runtime)

- **Google Stitch** - Source of design references.
  - Project ID `3771371856444129928` (documented in `CLAUDE.md` and `docs/brand/design-principles.md`).
  - HTML exports stored in gitignored `.reference/` (see `.gitignore:4`). Not accessed at build or runtime.

## Build-Time External Resources (Local Scripts Only)

- **System font files** consumed by Python press-asset generators:
  - `/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf`, `Poppins-Medium.ttf` (`scripts/generate_press_heroes.py:41-42`).
  - `/usr/share/fonts/truetype/lato/Lato-Bold.ttf`, `Lato-Regular.ttf` (`scripts/generate_press_heroes.py:43-44`).
  - These are local OS resources, not network calls; the scripts are not invoked by CI.

---

*Integration audit: 2026-04-26*
