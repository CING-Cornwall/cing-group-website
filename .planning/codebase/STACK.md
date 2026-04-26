# Technology Stack

**Analysis Date:** 2026-04-26

## Languages

**Primary:**
- Go templating (Hugo HTML templates) - All site rendering, located under `layouts/`
- HTML5 - Markup inside templates (`layouts/_default/baseof.html`, partials, page layouts)
- Markdown - Content authoring in `content/` (news posts, press releases, page content)
- YAML - Structured data; canonical councillor source at `data/councillors.yaml`
- TOML - Hugo site configuration in `hugo.toml`

**Secondary:**
- JavaScript (vanilla, inline) - Cookie banner, mobile nav hamburger, gtag bootstrap (inline in `layouts/_default/baseof.html` and `layouts/partials/header.html`)
- Python 3 - Build-time asset generation scripts in `scripts/`

## Runtime

**Build environment:**
- Hugo (extended) `0.159.1` - Pinned in CI at `.github/workflows/hugo.yml:25` via `HUGO_VERSION: 0.159.1`. Installed from the official `.deb` release in CI; locally invoked via `hugo` CLI.
- Browser - Final delivery target; no Node/JS runtime in production.
- Python 3 (local-only, ad hoc) - Used to run `scripts/generate_press_heroes.py` and `scripts/generate_press_pdfs.py` when refreshing press assets. Not invoked by CI.

**Package Manager:**
- None for the website itself. No `package.json`, `requirements.txt`, `Pipfile`, or lockfile is committed.
- Python script dependencies (Pillow, reportlab) are expected to be installed system-wide or in a developer's local virtualenv.

## Frameworks

**Core (site generation):**
- Hugo `0.159.1` extended - Static site generator. Custom layouts override defaults; no theme is used.
  - Config: `hugo.toml`
  - Output formats configured: `HTML`, `RSS`, `sitemap` (`hugo.toml:53-56`)
  - Pagination: 9 items per page (`hugo.toml:41-42`)
  - Goldmark renderer with `unsafe = true` for raw HTML in markdown (`hugo.toml:46-49`)
  - Taxonomy/term kinds disabled (`hugo.toml:51`)

**CSS framework:**
- Tailwind CSS via CDN (Play CDN, latest, unpinned) - Loaded at `layouts/_default/baseof.html:109`:
  - `<script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>`
  - Plugins enabled inline: `forms`, `container-queries`
  - Theme extended inline (`layouts/_default/baseof.html:110-173`) with Material Design 3 colour tokens, custom `fontFamily` (`headline: Manrope`, `body/label: Public Sans`), and a custom `borderRadius` scale.
  - Note: The Play CDN is intended for prototyping; there is no PostCSS/JIT build step.

**Testing:**
- None. No test framework, no `*.test.*` / `*.spec.*` files anywhere in the repository.

**Build/Dev:**
- Hugo CLI - Single command runs both dev server (`hugo server --baseURL http://localhost:1313/ --disableFastRender`) and production build (`hugo --gc --minify --baseURL "https://www.cingparty.uk/"`).
- GitHub Actions - Build + deploy orchestration (`.github/workflows/hugo.yml`).

## Key Dependencies

**Critical (runtime / browser):**
- Tailwind CDN - `https://cdn.tailwindcss.com` (`layouts/_default/baseof.html:109`). Without this, the site is unstyled.
- Google Fonts - `Manrope` (weights 400/700/800) and `Public Sans` (weights 300/400/500/600) loaded from `fonts.googleapis.com` (`layouts/_default/baseof.html:176`).
- Material Symbols Outlined - Google Fonts variable icon font loaded at `layouts/_default/baseof.html:177` with variation axes `wght`, `FILL`. Default settings applied via inline CSS at `layouts/_default/baseof.html:180-182`.
- Google Tag Manager / gtag.js - Loaded only in production and only after consent (`layouts/_default/baseof.html:7-35`).

**Critical (build-time, Python — local only):**
- `Pillow` (PIL) - Used by `scripts/generate_press_heroes.py:25` (`from PIL import Image, ImageDraw, ImageFilter, ImageFont`) to render press release hero JPEGs into `static/images/press/`.
- `reportlab` - Used by `scripts/generate_press_pdfs.py:21-34` to produce branded press release PDFs into `static/documents/press/2026-04-21/`.
- System TTF fonts - Hard-coded absolute paths in `scripts/generate_press_heroes.py:41-44` (`/usr/share/fonts/truetype/google-fonts/Poppins-*.ttf`, `/usr/share/fonts/truetype/lato/Lato-*.ttf`). Scripts will fail on machines without those packages installed.

**Infrastructure:**
- GitHub Pages - Hosting target.
- GitHub Actions Marketplace actions used in `.github/workflows/hugo.yml`:
  - `actions/checkout@v4` (line 32)
  - `actions/configure-pages@v5` (line 38)
  - `actions/upload-pages-artifact@v3` (line 50)
  - `actions/deploy-pages@v4` (line 63)

## Configuration

**Site config:**
- `hugo.toml` - baseURL, language (`en-gb`), site title, copyright, params (`description`, `formspreeId = "mvzvgdbl"`, `ogImage`), main menu definitions (Home, About, Councillors, Policies, News, Press, Get Involved), pagination, and Goldmark settings.

**Environment / secrets:**
- No `.env*` files present in the repository.
- No runtime environment variables consumed by the site (it is a fully static build).
- CI exports build-time env: `HUGO_CACHEDIR`, `HUGO_ENVIRONMENT=production`, `TZ=Europe/London` (`.github/workflows/hugo.yml:40-43`).

**Build:**
- `.github/workflows/hugo.yml` - The single CI workflow; builds with `--gc --minify` and `--baseURL "https://www.cingparty.uk/"`.
- `hugo.toml` `[outputs]` - Controls per-kind output formats.

**Robots / SEO:**
- `static/robots.txt` - Allows all crawlers, points to `https://www.cingparty.uk/sitemap.xml`.
- Sitemap auto-generated by Hugo (declared in `hugo.toml [outputs]`).
- Open Graph, Twitter Card, canonical, and JSON-LD `Organization` / `WebSite` schemas emitted from `layouts/_default/baseof.html:56-102`.

## Platform Requirements

**Development:**
- Hugo extended `>=0.159.1` on PATH (Linux, macOS, or Windows).
- Optional: Python 3 with `Pillow` and `reportlab` for regenerating press hero images and PDFs.
- No Node.js or npm required.
- Internet connection at runtime to load Tailwind CDN, Google Fonts, and Material Symbols (no local fallback bundled).

**Production:**
- GitHub Pages with custom domain `www.cingparty.uk` (`static/CNAME:1`).
- HTTPS provided by GitHub Pages.
- Deploy environment: `github-pages` (`.github/workflows/hugo.yml:55-57`).
- Trigger: push to `main` or manual `workflow_dispatch`.

## Repository Layout (build-relevant)

- `layouts/` - Hugo templates (no theme).
- `content/` - Markdown content (`news/`, `press/`, page bundles).
- `data/councillors.yaml` - Single source of truth for councillor data, consumed via `index hugo.Data "councillors"`.
- `static/` - Copied verbatim into the build output (`CNAME`, `robots.txt`, favicons, `documents/`, `images/`).
- `archetypes/` - Hugo content scaffolds.
- `scripts/` - Local Python utilities (not invoked by CI).
- `docs/` - Committed brand and project documentation.
- `.reference/` - Gitignored Stitch HTML exports.
- `public/`, `resources/`, `.hugo_build.lock` - Gitignored Hugo build artefacts.

---

*Stack analysis: 2026-04-26*
