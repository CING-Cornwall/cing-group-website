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

Deployment is automatic via GitHub Actions on push to `main`. No npm/Node dependencies — Hugo is the only build tool.

## Architecture

### Data-driven councillor pages

`data/councillors.yaml` is the single source for all councillor information. It drives both the `/councillors/` card grid and the `/about/` team section. Fields: `name`, `role`, `division`, `photo`, `email`, `attendance`, `bio`, `committees`, `outside_bodies`.

Access pattern in templates:
```go
{{ $councillors := index hugo.Data "councillors" }}
```

### Layout hierarchy

Custom layouts override Hugo defaults — there is no theme:

- `layouts/_default/baseof.html` — base wrapper with Tailwind config, fonts, Material Symbols
- `layouts/partials/header.html` — glassmorphism nav with mobile hamburger (vanilla JS)
- `layouts/partials/footer.html` — 3-column footer
- `layouts/index.html` — homepage (hero, principles grid, news teaser, CTA)
- `layouts/about/list.html` — hero + asymmetric story + mission grid + team bento
- `layouts/councillors/list.html` — hero + stats bar + portrait cards + quote
- `layouts/policies/policies.html` — bento grid of policy cards (not prose)
- `layouts/get-involved/list.html` — bento cards + Formspree contact form + newsletter
- `layouts/news/list.html` — featured article bento + article grid + pagination
- `layouts/news/single.html` — individual news post

Content pages that use a non-default layout specify it in front matter: `layout: "policies"` or `layout: "list"`.

### Design system

All styling uses Tailwind CSS via CDN with Material Design 3 colour tokens defined inline in `baseof.html`. Key tokens:

- Primary: `#00263b` (deep navy), Primary Container: `#003d5b`
- Tertiary: `#705d00` (gold), Tertiary Container: `#c9a900`
- Surface tiers: `surface`, `surface-container-low` through `surface-container-highest`
- Typography: `font-headline` (Manrope), `font-body` (Public Sans), `font-label` (Public Sans)
- Icons: Material Symbols Outlined from Google Fonts

Design principle: no 1px borders — sections separated by tonal surface shifts. Cards use `editorial-shadow` (ambient, 4% opacity). Councillor photos use `grayscale group-hover:grayscale-0` effect.

### Stitch design references

`.reference/` (gitignored) contains HTML snapshots exported from Google Stitch (project ID `3771371856444129928`). These are the design source of truth — the "CING Brand Update" variants are the preferred references.

### Forms

Formspree handles all form submissions. The form ID (`mvzvgdbl`) is stored in `hugo.toml` as `params.formspreeId` and used in templates:
```html
<form action="https://formspree.io/f/{{ .Site.Params.formspreeId }}" method="POST">
```

### News content

News posts live in `content/news/` as markdown files with front matter: `title`, `date`, `category`, `image`, `excerpt`. The news list template shows the first post as a featured bento layout and remaining posts in a 3-column grid.

### Councillor data

Councillor data (divisions, committees, attendance percentages) is maintained in `data/councillors.yaml`. Phase 2 plan: GitHub Actions cron to auto-refresh data at build time.
