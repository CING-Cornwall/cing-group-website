# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Static website for the Cornish Independent NonAligned Group (CING) — a group of independent councillors on Cornwall Council. Built with Hugo, styled with Tailwind CSS (CDN), deployed to GitHub Pages at `www.cingparty.uk`.

## Commands

```bash
# Local development
hugo server --baseURL http://localhost:1313/ --disableFastRender

# Production build
hugo --gc --minify --baseURL "https://www.cingparty.uk/"

# Create a new news post
hugo new content/news/my-post-title.md
```

Deployment is automatic via GitHub Actions on push to `main`. No npm/Node dependencies — Hugo is the only build tool. (Exception: the pa11y-ci CI job uses `actions/setup-node` and `npm install --no-save` ephemerally inside a single workflow step. Node is a CI-only tool, never a project dependency — there is no `package.json` and `git clone && hugo` works on a fresh machine without Node installed.)

## Architecture

### Data-driven councillor pages

`data/councillors.yaml` is the single source for all councillor information. It drives both the `/councillors/` card grid and the `/about/` team section. Fields: `name`, `role`, `division`, `photo`, `email`, `attendance`, `bio`, `committees`, `outside_bodies`.

Access pattern in templates:
```go
{{ $councillors := index hugo.Data "councillors" }}
```

### Layout hierarchy

Custom layouts override Hugo defaults — there is no theme:

- `layouts/_default/baseof.html` — base wrapper with Tailwind config, fonts, Material Symbols, Google Analytics (consent-gated), cookie banner
- `layouts/partials/header.html` — glassmorphism nav with mobile hamburger (vanilla JS)
- `layouts/partials/footer.html` — 3-column footer
- `layouts/index.html` — homepage (hero, principles grid, news teaser, CTA)
- `layouts/about/list.html` — hero + asymmetric story + mission grid + team bento
- `layouts/councillors/list.html` — hero + stats bar + portrait cards + quote
- `layouts/policies/policies.html` — two-part manifesto page: hero, local policy bento grid, image divider, Westminster positions, CTA with PDF download
- `layouts/get-involved/list.html` — bento cards + Formspree contact form + newsletter
- `layouts/news/list.html` — featured article bento + article grid + pagination
- `layouts/news/single.html` — individual news post

Content pages that use a non-default layout specify it in front matter: `layout: "policies"` or `layout: "list"`.

### Design system

All styling uses Tailwind CSS via CDN with Material Design 3 colour tokens defined inline in `baseof.html`. Full brand documentation lives in `docs/brand/`:

- **[`docs/brand/DESIGN.md`](docs/brand/DESIGN.md)** — **Master design system** ("Kernow Horizon") from Stitch. Creative north star, philosophy, do's/don'ts. The canonical design authority.
- **[`docs/brand/colours.md`](docs/brand/colours.md)** — Complete colour token reference (primary, secondary, tertiary, surface, semantic)
- **[`docs/brand/typography.md`](docs/brand/typography.md)** — Font families (Manrope, Public Sans), type scale, icon font
- **[`docs/brand/design-principles.md`](docs/brand/design-principles.md)** — Implementation-specific layout rules, component patterns, Tailwind conventions

Key tokens (quick reference):
- Primary: `#00263b` (deep navy), Primary Container: `#003d5b`
- Tertiary: `#705d00` (gold), Tertiary Container: `#c9a900`
- Typography: `font-headline` (Manrope), `font-body` / `font-label` (Public Sans)

Design principle: no 1px borders — sections separated by tonal surface shifts. Cards use `editorial-shadow` (ambient, 4% opacity). Councillor photos use `grayscale group-hover:grayscale-0` effect.

### Stitch design references

`.reference/` (gitignored) contains HTML snapshots exported from Google Stitch (project ID `3771371856444129928`). These are the design source of truth — the "CING Brand Update" variants are the preferred references. Screen IDs and Stitch project details are documented in [`docs/brand/design-principles.md`](docs/brand/design-principles.md).

### Documentation

`docs/` contains committed reference documentation and brand standards — see [`docs/README.md`](docs/README.md) for an index. Unlike `.reference/` (gitignored Stitch exports), `docs/` is version-controlled and serves as the durable source of truth for brand guidelines and project standards.

### Forms

Formspree handles all form submissions. The form ID (`mvzvgdbl`) is stored in `hugo.toml` as `params.formspreeId` and used in templates:
```html
<form action="https://formspree.io/f/{{ .Site.Params.formspreeId }}" method="POST">
```

### News content

News posts live in `content/news/` as markdown files with front matter: `title`, `date`, `category`, `image`, `excerpt`. The news list template shows the first post as a featured bento layout and remaining posts in a 3-column grid.

### Analytics and cookie consent

Google Analytics (`G-Z1F4F1TRD0`) is loaded only in production builds (`hugo.IsProduction`) and only after the user accepts cookies via the consent banner — the `<script src="https://www.googletagmanager.com/gtag/js?...">` tag is not injected at all until consent is granted, so rejecting (or not yet choosing) results in zero requests to `googletagmanager.com` and `google-analytics.com`. The consent choice is stored in `localStorage` (key: `cing-cookies`, values: `accepted` or `rejected`). The `window.loadGtag()` function in `baseof.html` dynamically injects the gtag script and is called from two places: at page load if the stored choice is already `accepted`, and from the cookie banner's Accept button handler. The function is idempotent (a `gtagLoaded` flag prevents double-loading). The cookie banner and consent logic are both in `baseof.html`, gated behind `hugo.IsProduction` so local dev is unaffected.

### Manifesto

The full prose manifesto ("Standing Up for Cornwall") lives in `docs/manifesto/MANIFESTO.md` with a structural outline in `docs/manifesto/MANIFESTO-OUTLINE.md`. A branded PDF is at `static/documents/cing-manifesto.pdf` (generated via reportlab). The policies page links to this PDF for download.

### Councillor data

Councillor data (divisions, committees, attendance percentages) is maintained in `data/councillors.yaml`. Phase 2 plan: GitHub Actions cron to auto-refresh data at build time.
