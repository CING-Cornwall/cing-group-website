# Architecture

**Analysis Date:** 2026-04-26

## Pattern Overview

**Overall:** Static-site generation with Hugo. No server, no database, no JavaScript framework. Content is markdown + YAML data; templates are Go HTML templates; output is a fully prerendered set of HTML files served from GitHub Pages.

**Key Characteristics:**
- Hugo 0.159.1 extended (pinned in `.github/workflows/*.yml`) is the sole build tool — no Node/npm
- Custom layouts only — no Hugo theme; everything lives under `layouts/`
- Tailwind CSS via CDN with Material Design 3 colour tokens declared inline in `layouts/_default/baseof.html`
- Single-source data file (`data/councillors.yaml`) drives multiple pages
- Optional Python utility scripts under `scripts/` produce branded press release assets (PDFs and hero images) into `static/`
- Privacy-aware analytics: Google Analytics is gated behind both `hugo.IsProduction` and a localStorage consent flag

## Layers

**Configuration layer:**
- Purpose: Site-level configuration, menus, params, output formats
- Location: `hugo.toml`
- Contains: `baseURL`, menus (Home, About, Councillors, Policies, News, Press, Get Involved), `params.formspreeId`, pagination, markup settings (`unsafe = true` for goldmark), `disableKinds = ["taxonomy", "term"]`
- Used by: every template via `.Site.Params.*` and `hugo.*` accessors

**Data layer:**
- Purpose: Structured, source-of-truth data shared across pages
- Location: `data/councillors.yaml`
- Contains: list of councillors with `name`, `role`, `division`, `photo`, `email`, `attendance`, `bio`, `committees`, `outside_bodies`
- Accessed via: `{{ $councillors := index hugo.Data "councillors" }}`
- Consumed by: `layouts/councillors/list.html` and `layouts/about/list.html`

**Content layer:**
- Purpose: Page-level prose and section indexes
- Location: `content/`
- Contains: `_index.md` files for each section (about, councillors, get-involved, news, policies, press, privacy, brand) and individual post markdown files for `news/` and `press/`
- Front matter selects layout (e.g. `layout: "policies"`), declares `title`, `description`, `date`, `category`, `image`, `excerpt`, etc.

**Layout layer:**
- Purpose: Render content into HTML pages
- Location: `layouts/`
- Hierarchy:
  - `_default/baseof.html` — base wrapper (head, fonts, Tailwind config, MD3 tokens, GA + cookie banner, header/footer partial includes)
  - Page-type templates inherit from `baseof.html` via `{{ define "main" }}` blocks
  - `partials/header.html` (glassmorphism nav, mobile hamburger) and `partials/footer.html` (3-col footer) are included by `baseof.html`

**Static asset layer:**
- Purpose: Files copied verbatim to the published site root
- Location: `static/`
- Contains: favicon set, `CNAME` (custom domain), `robots.txt`, `images/` (hero photography, councillor portraits, press hero images), `documents/` (manifesto PDF and per-release press PDFs)

**Build/deploy layer:**
- Purpose: Compile content + layouts → static HTML and deploy
- Location: `.github/workflows/`
- Pipeline: GitHub Actions runner installs Hugo, runs `hugo --gc --minify --baseURL "https://www.cingparty.uk/"`, uploads `./public` as a Pages artifact, deploys to `github-pages` environment

## Data Flow

**Build pipeline (push → live site):**

1. Developer pushes to `main` (or triggers `workflow_dispatch`)
2. `.github/workflows/*.yml` job `build` runs on `ubuntu-latest`:
   - Installs Hugo extended `0.159.1`
   - Checks out repo with submodules + full history
   - Runs `hugo --gc --minify --baseURL "https://www.cingparty.uk/"` with `HUGO_ENVIRONMENT=production`, `TZ=Europe/London`
   - Hugo reads `hugo.toml`, walks `content/`, merges with `data/`, applies `layouts/`, emits to `public/`
   - Uploads `./public` as a Pages artifact
3. Job `deploy` publishes the artifact to the `github-pages` environment
4. GitHub Pages serves `www.cingparty.uk` via the `static/CNAME` mapping

**Councillor data flow:**

1. `data/councillors.yaml` lists councillors as YAML records
2. `layouts/councillors/list.html` reads via `index hugo.Data "councillors"` and renders the stats bar, portrait card grid, and biography blocks
3. `layouts/about/list.html` reuses the same data to render the "team bento" section
4. Photos referenced via the `photo` field resolve to `/images/councillors/<slug>.jpg` under `static/images/councillors/`

**News flow:**

1. Markdown files under `content/news/*.md` declare front matter (`title`, `date`, `category`, `image`, `excerpt`)
2. `layouts/news/list.html` paginates posts (pagerSize=9 in `hugo.toml`); first post is rendered as a featured bento, remainder in a 3-column grid
3. `layouts/news/single.html` renders an individual post with JSON-LD schema for SEO

**Press release flow:**

1. Releases are nested by meeting under `content/press/full-council-<date>/`
2. `_incoming/` holds raw drafts (`cascade.build` in its `_index.md` keeps the section unpublished)
3. `layouts/press/list.html` renders the press section landing; `layouts/press/single.html` renders individual releases
4. Each release links to a downloadable branded PDF at `/documents/press/<date>/<slug>.pdf` and uses a hero image at `/images/press/<slug>.jpg`

**State management:**
- Build-time only — there is no runtime state. The only client-side persistent state is the cookie consent flag in `localStorage` (`cing-cookies` = `accepted` | `rejected`).

## Key Abstractions

**Section template:**
- Purpose: Render a Hugo "section" (a top-level content folder)
- Examples: `layouts/about/list.html`, `layouts/councillors/list.html`, `layouts/news/list.html`, `layouts/press/list.html`, `layouts/get-involved/list.html`
- Pattern: Each section folder may declare its own `list.html` overriding `_default/list.html`; pages opt in via `_index.md` front matter

**Custom-named layout:**
- Purpose: Allow a single content file to use a non-section layout
- Examples: `layouts/policies/policies.html` referenced from `content/policies/_index.md` via `layout: "policies"`
- Pattern: Front matter `layout` key maps to `layouts/<type>/<name>.html`

**Base template + main block:**
- Purpose: Shared chrome (head, header, footer, GA, cookie banner) without duplication
- Location: `layouts/_default/baseof.html`
- Pattern: Page-level templates begin with `{{ define "main" }} ... {{ end }}` and inherit the surrounding shell

## Entry Points

**HTML entry point (homepage):**
- Location: `layouts/index.html` (236 lines) backed by `content/_index.md`
- Triggers: requests to `/`
- Responsibilities: hero, principles grid, news teaser, CTA

**Section entry points:**
- `/about/` → `layouts/about/list.html`
- `/councillors/` → `layouts/councillors/list.html`
- `/policies/` → `layouts/policies/policies.html` (selected via front matter)
- `/news/` → `layouts/news/list.html` (+ `single.html` per post)
- `/press/` → `layouts/press/list.html` (+ `single.html` per release)
- `/get-involved/` → `layouts/get-involved/list.html`
- `/brand/` → `layouts/brand/list.html` (internal brand reference page)

**Build entry point:**
- Location: `.github/workflows/*.yml` (single workflow file)
- Triggered by: push to `main` or manual `workflow_dispatch`

**Asset generation entry points (manual, not in CI):**
- `scripts/generate_press_heroes.py` — produces hero images per release into `static/images/press/`
- `scripts/generate_press_pdfs.py` — produces branded PDFs into `static/documents/press/<date>/`

## Analytics & Cookie Consent

Defined entirely in `layouts/_default/baseof.html`:

1. The gtag bootstrap (`window.dataLayer`, `gtag()`, default `denied` consent) and the dynamic `loadGtag()` script injector are wrapped in `{{ if hugo.IsProduction }}` (line 8)
2. On page load, if `localStorage.getItem('cing-cookies') === 'accepted'`, `loadGtag()` is invoked immediately (line 22)
3. The cookie banner markup + accept/reject buttons are rendered only in production (line 219)
4. Accept → `localStorage.setItem('cing-cookies', 'accepted')` then call `loadGtag()` (line 248)
5. Reject → `localStorage.setItem('cing-cookies', 'rejected')` and GA is never loaded (line 255)
6. Local development sees neither the banner nor analytics, since `hugo.IsProduction` is false outside the GitHub Actions build with `HUGO_ENVIRONMENT=production`

## PDF & Hero Image Generation Pipeline

Out-of-band Python tooling for press releases (run manually before commit; outputs are committed under `static/`):

**`scripts/generate_press_heroes.py`:**
- Uses `Pillow` (PIL) to draw 1600×800 (2:1) navy gradient hero images
- Applies brand tokens directly (Primary navy `#00263b`, Primary container `#003d5b`, Tertiary gold `#705d00`/`#c9a900`)
- Adds gold accent strip, overline label, display headline, topic motif, and CING wordmark
- Per-release record (`slug`, headline, overline, motif) defined inline as a list of dataclasses
- Writes `static/images/press/<slug>.jpg`

**`scripts/generate_press_pdfs.py`:**
- Uses `reportlab` (`BaseDocTemplate`, `Frame`, `Paragraph`, `pdfmetrics`/`TTFont`) to typeset multi-page A4 PDFs
- Reads source markdown for each release from a configured `SOURCE_DIR`
- Embeds Poppins (Manrope proxy) and Lato (Public Sans proxy) TTFs for brand-true type
- Generates first-page banner with embargo strap, body with pull quotes, and contact footer
- Writes `static/documents/press/2026-04-21/<slug>.pdf`

**Manifesto PDF:**
- A separate, branded manifesto PDF is committed at `static/documents/cing-manifesto.pdf` (generated previously via reportlab; source prose under `docs/manifesto/`)

## Error Handling

**Strategy:** Build-time failure model. Any template, content, or asset error fails the GitHub Actions `build` job and aborts deployment, leaving the previous live site in place.

**Patterns:**
- Hugo strict mode is implicit through `--gc --minify`; broken references typically surface as warnings or empty values
- Forms POST directly to Formspree (`https://formspree.io/f/{{ .Site.Params.formspreeId }}`); error UX is delegated to Formspree
- Client-side JS is minimal (mobile hamburger, cookie banner) and uses guarded DOM lookups

## Cross-Cutting Concerns

**Logging:** None at runtime (static site). Build logs surface in GitHub Actions.

**Validation:** None server-side. Form validation falls to native HTML attributes and Formspree.

**Authentication:** Not applicable — site is fully public. There are no protected pages.

**Internationalisation:** Single locale (`en-gb` in `hugo.toml`).

**SEO:** `og:image` default in `params.ogImage`; per-page `description` in front matter; news single template emits JSON-LD schema; `outputs` includes RSS for home and section pages plus a `sitemap`.

## Mental Model

```
                                 ┌──────────────────────────────────┐
                                 │  Author edits markdown / YAML    │
                                 │  - content/**/*.md               │
                                 │  - data/councillors.yaml         │
                                 │  - layouts/**/*.html             │
                                 │  (optional) scripts/*.py to (re)  │
                                 │   build static/{images,documents} │
                                 └────────────────┬─────────────────┘
                                                  │ git push (main)
                                                  ▼
                          ┌────────────────────────────────────────────────┐
                          │  GitHub Actions  (.github/workflows/*.yml)     │
                          │  ┌──────────────────────────────────────────┐  │
                          │  │ install hugo_extended 0.159.1            │  │
                          │  │ HUGO_ENVIRONMENT=production              │  │
                          │  │ hugo --gc --minify --baseURL=…           │  │
                          │  │   reads: hugo.toml, content/, data/,     │  │
                          │  │          layouts/, static/               │  │
                          │  │   writes: ./public                       │  │
                          │  │ upload-pages-artifact ./public           │  │
                          │  └──────────────────────────────────────────┘  │
                          │                  ▼                              │
                          │           deploy-pages                          │
                          └────────────────────────────────────────────────┘
                                                  │
                                                  ▼
                          ┌────────────────────────────────────────────────┐
                          │  GitHub Pages  →  www.cingparty.uk             │
                          │  (CNAME from static/CNAME)                     │
                          └────────────────────────────────────────────────┘

  Runtime (in browser):
      load page  ─►  baseof.html sets MD3 tokens, Tailwind CDN, fonts
                  ─►  if hugo.IsProduction:
                          show cookie banner
                          if localStorage.cing-cookies == "accepted":
                              loadGtag() → GA G-Z1F4F1TRD0
                  ─►  Formspree handles contact + newsletter POSTs
```

```
Layouts inheritance
───────────────────
layouts/_default/baseof.html              (chrome: head, fonts, MD3 tokens,
        │                                  GA + consent banner, header/footer)
        │
        ├── layouts/index.html                          (/)
        ├── layouts/about/list.html                     (/about/)
        ├── layouts/councillors/list.html               (/councillors/)
        ├── layouts/policies/policies.html              (/policies/, via front matter)
        ├── layouts/news/list.html ─┐
        │                           └── layouts/news/single.html
        ├── layouts/press/list.html ─┐
        │                            └── layouts/press/single.html
        ├── layouts/get-involved/list.html              (/get-involved/)
        ├── layouts/brand/list.html                     (/brand/, internal)
        └── layouts/_default/{list,single}.html         (fallbacks)

Partials included by baseof.html:
    layouts/partials/header.html  (glass nav, mobile hamburger)
    layouts/partials/footer.html  (3-col footer)
```

---

*Architecture analysis: 2026-04-26*
