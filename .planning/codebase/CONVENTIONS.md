# Coding Conventions

**Analysis Date:** 2026-04-26

## Naming Patterns

**Layout files (`layouts/`):**
- Lowercase, kebab-case section names matching `content/` (e.g. `councillors/list.html`, `get-involved/list.html`).
- Hugo defaults: `_default/baseof.html`, `_default/list.html`, `_default/single.html`.
- Section list pages use `list.html`; section single pages use `single.html`.
- Custom non-default layouts are given descriptive filenames and selected via front matter, e.g. `layouts/policies/policies.html` is invoked by `layout: "policies"` in `content/policies/_index.md`.
- Partials live in `layouts/partials/` (e.g. `header.html`, `footer.html`).

**Content files (`content/`):**
- News slugs: lowercase, kebab-case, descriptive — e.g. `content/news/welcome-to-our-new-website.md`, `content/news/spring-council-session-update.md`.
- Press release slugs: kebab-case, topic-led — e.g. `content/press/full-council-2026-04-21/planning-public-trust.md`.
- Press release sets are grouped under a meeting-dated bundle directory: `content/press/full-council-2026-04-21/`.
- Section index files: `_index.md` (e.g. `content/news/_index.md`, `content/press/_index.md`).
- A staging directory `content/press/_incoming/` holds raw source markdown (consumed by `scripts/generate_press_pdfs.py`); leading underscore keeps it as a Hugo headless bundle.

**Data files (`data/`):**
- `data/councillors.yaml` is the single source of truth for councillor information. Files are lowercase, snake-or-kebab-case (currently only one).

**Images (`static/images/`):**
- Councillor portraits: `static/images/councillors/<firstname>-<lastname>.jpg`.
- Press hero images: `static/images/press/<slug>.jpg` (slug matches the press release content slug).
- Generated PDFs: `static/documents/press/<meeting-date>/<slug>.pdf` plus the manifesto at `static/documents/cing-manifesto.pdf`.

**Tailwind colour tokens:**
- Material Design 3 naming: `primary`, `on-primary`, `primary-container`, `surface-container-lowest`, `tertiary-fixed-dim`, etc. Defined in the inline `tailwind.config` block of `layouts/_default/baseof.html` (lines 115–162).

## Hugo Templating Conventions

**Data access:**
```go
{{ $councillors := index hugo.Data "councillors" }}
{{ with $councillors }}
  {{ range . }}
    {{ $councillor := . }}
    ...
  {{ end }}
{{ end }}
```
Pattern used in `layouts/councillors/list.html` (line 59) and `layouts/about/list.html`.

**URL helpers:**
- All asset references go through `relURL`: `{{ "/images/foo.jpg" | relURL }}`, `{{ .RelPermalink }}` for page links.
- Absolute URLs for OG tags use `absURL`: `{{ . | absURL }}` (see `layouts/_default/baseof.html` lines 61, 68).

**Front matter access:**
- Custom params via `.Params.<field>`: `{{ .Params.image }}`, `{{ .Params.category }}`, `{{ .Params.excerpt }}`.
- Standard fields direct: `{{ .Title }}`, `{{ .Date }}`, `{{ .Content }}`, `{{ .Description }}`.

**Conditional rendering:**
- `{{ with .Params.image }}…{{ else }}…{{ end }}` is the preferred guarded-render pattern (see `layouts/news/list.html` lines 21–30, `layouts/news/single.html` lines 51–60).
- Site params via `.Site.Params.formspreeId`, `.Site.Params.description`, etc.

**Production-only blocks:**
```go
{{ if hugo.IsProduction }}
  …analytics / cookie banner…
{{ end }}
```
Used in `layouts/_default/baseof.html` for Google Analytics (lines 8–35) and the cookie banner (lines 219–263).

**Comments:**
- Use `{{/* … */}}` for template comments (consistently used to label sections in `baseof.html`, `news/single.html`, `index.html`).
- Section banners with rule lines for major blocks, e.g. `{{/* ============================================ HERO SECTION … ============================================ */}}` in `layouts/index.html` lines 3–5.

**Date formatting:**
- Use Go's reference date: `{{ .Date.Format "January 2, 2006" }}` for human-readable, `{{ .Date.Format "2006-01-02" }}` for `datetime` attributes, `{{ .Date.Format "2006-01-02T15:04:05Z07:00" }}` for ISO 8601 in JSON-LD (`layouts/news/single.html` lines 8–9, 38–40).

**Sorting / pagination:**
- Reverse-chronological news listing: `{{ $pages := .Pages.ByDate.Reverse }}`, then `first 1` for featured + `after 1` for the rest (`layouts/news/list.html` line 12).
- Pagination size set in `hugo.toml` via `[pagination] pagerSize = 9`.

## Tailwind & CSS Conventions

**Custom utilities (defined in `layouts/_default/baseof.html` `<style>` block, lines 179–201):**
- `.editorial-shadow` — ambient elevation: `box-shadow: 0 8px 40px rgba(23, 28, 32, 0.04)` (4% opacity, never use harsher drop shadows).
- `.text-editorial-balance` — `text-wrap: balance` for headline typography.
- `.line-clamp-2`, `.line-clamp-3` — webkit line clamping for excerpts.

**Signature class patterns:**
- Councillor portraits: `grayscale group-hover:grayscale-0 transition-all duration-700 scale-105 group-hover:scale-100` — greyscale by default, colour and de-zoom on group hover (`layouts/councillors/list.html` line 73).
- Card containers: `bg-surface-container-lowest rounded-xl overflow-hidden editorial-shadow` (homepage, news bento, councillor cards).
- Hero overlines: `inline-block px-3 py-1 bg-tertiary text-on-tertiary font-headline font-bold text-[10px] tracking-[0.2em] uppercase mb-6 rounded-sm` — a recurring "kicker" pattern across `index.html`, `about/list.html`, `councillors/list.html`.
- Hero images use a navy gradient overlay: `bg-gradient-to-r from-primary/85 via-primary/50 to-transparent` (varies by page; pattern stays the same).

**Type classes:**
- Headlines: `font-headline font-extrabold tracking-tight` (or `tracking-tighter` for display sizes).
- Body prose: `font-body text-lg leading-relaxed` for editorial body, `text-on-surface-variant` for muted prose.
- Labels / overlines: `font-label … uppercase tracking-widest text-sm font-bold` (see `layouts/news/list.html` line 6).

**Border radius:**
- Custom scale (in `tailwind.config`): `DEFAULT: 0.125rem`, `lg: 0.25rem`, `xl: 0.5rem`, `full: 0.75rem`.
- Cards use `rounded-lg` or `rounded-xl`; pills/chips use `rounded-full`; buttons use `rounded-md` (Tailwind default 0.375rem, untouched).

**Prose styling:**
- Markdown article bodies use Tailwind arbitrary-variant child selectors instead of `@tailwindcss/typography`. See `layouts/news/single.html` lines 64–76 — `[&>h2]:font-headline [&>h2]:font-bold …`. Replicate this pattern when styling `{{ .Content }}` blocks in new layouts.

## Design Rules (Canonical)

These are mandatory and originate in `docs/brand/DESIGN.md` and `docs/brand/design-principles.md`.

- **No 1px borders for section separation.** Use tonal surface shifts (`surface-container-lowest` → `surface-container-low` → `surface-container` → `surface-container-high`). The "No-Line Rule" is explicit in `DESIGN.md` §2.
- **Ambient shadow only** at 4% opacity. Use `.editorial-shadow`, not `shadow-xl`/`shadow-2xl` for editorial cards. Stronger shadows are reserved for floating CTAs and hero callouts.
- **Greyscale councillor photos** by default with hover colour transition.
- **Bento grids** for major listing pages (homepage, policies, news, get-involved, about team). Asymmetric, varied-size cards.
- **Generous negative space**: spacing scale `16` and `20` between major content blocks; `py-24` is the standard section vertical padding.
- **Glassmorphism** only for the fixed nav overlay and overlay cards (`backdrop-blur-md` + `bg-opacity-90`).
- **No "pure" black** — use `on-background` (`#171c20`) for text.
- **Pill shape (`rounded-full`)** is for chips and tags only; buttons stay `rounded-md`; cards stay `rounded-lg`/`rounded-xl`.
- **Tertiary gold (`#705d00` / `#c9a900`)** is a prestige accent — use sparingly, primarily for "Join", "Donate", and primary CTAs that warrant emphasis.

## Front-Matter Conventions

**News posts (`content/news/*.md`):**
```yaml
---
title: "…"
date: 2026-03-27           # ISO date (no time) acceptable
category: "Announcement"   # free-form string, displayed as a chip
image: "/images/…jpg"      # optional; absolute path under static/
excerpt: "…"               # short summary; falls back to .Plain | truncate 200
---
```

**Press releases (`content/press/full-council-2026-04-21/*.md`):**
```yaml
---
title: "…"
date: 2026-04-21T09:00:00+01:00      # full ISO with TZ; press is timezone-sensitive
publishDate: 2026-04-20T09:00:00+01:00  # used for embargo handling
category: "Planning & Democracy"
excerpt: "…"
image: "/images/press/<slug>.jpg"
pdf: "/documents/press/2026-04-21/<slug>.pdf"
---
```

**Section index pages (`_index.md`):**
- Always include `title` and `description`. Add `layout: "<custom>"` only when overriding the default list template (e.g. policies).

**Archetype:** `archetypes/default.md` produces:
```toml
+++
date = '{{ .Date }}'
draft = true
title = '{{ replace .File.ContentBaseName "-" " " | title }}'
+++
```
Note: archetype uses TOML front matter, but existing content uses YAML — prefer YAML for consistency with the rest of the corpus.

## Data File Conventions (`data/councillors.yaml`)

Top-level is a YAML list. Each councillor entry expects:

| Field | Type | Notes |
|-------|------|-------|
| `name` | string | Full display name, including any hyphenated surnames |
| `role` | string | "Group Leader", "Deputy Leader", "Member" — used to drive ordering and badges |
| `division` | string | Cornwall Council electoral division name |
| `photo` | string | `/images/councillors/<firstname>-<lastname>.jpg` |
| `email` | string | `cllr.<firstname>.<lastname>@cornwall.gov.uk` |
| `attendance` | int | Whole-number percentage |
| `bio` | string | One-paragraph editorial bio (~2 sentences) |
| `committees` | list[string] | Cornwall Council committee names, full official spelling |
| `outside_bodies` | list[string] | Optional; external bodies the councillor sits on |

**Ordering:** Group Leader first, Deputy Leader second, then Members. Maintain this when adding new councillors so card grids render in seniority order without a sort step in templates.

## Commit Message Style

From `git log --oneline -25`:

- Lowercase, imperative-mood, present-tense verb leads (`add`, `update`, `fix`, `remove`, `replace`, `lift`).
- Short, single-line subject (no body in most commits). Examples:
  - `add cookie consent banner and update privacy policy`
  - `fix sitemap to include all pages and individual posts`
  - `replace all mailto links with get-involved page links`
  - `update About page with real CING content`
- Some commits use a Conventional-Commits-ish prefix (`fix:`) but this is inconsistent — do not enforce it.
- Multi-element subjects join with `and` rather than commas.
- Capitalised "Add" appears in newer press-release commits (`Add fifth press release: …`) — both casings exist; lowercase is the dominant style.
- No emoji, no trailers (no `Co-Authored-By` lines), no scope tags.

## Python Script Conventions (`scripts/`)

Two scripts exist: `generate_press_heroes.py` and `generate_press_pdfs.py`.

- **Shebang + module docstring**: `#!/usr/bin/env python3` followed by a triple-quoted docstring naming the brand system ("Kernow Horizon — Modern Monolith") and listing brand tokens used.
- **`from __future__ import annotations`** at the top.
- **Path discovery**: derive `ROOT = Path(__file__).resolve().parents[1]` and build all paths relative to it; never hardcode `/home/...`.
- **Brand-token constants** are declared at module top in a `# ---------- Brand palette ----------` (PIL: RGB tuples) or `# ---------- Brand tokens ----------` (reportlab: `HexColor`) section. Constant names mirror the Tailwind tokens: `NAVY_DEEP`, `GOLD`, `IVORY`, `STONE`, `ON_SURFACE_VARIANT`.
- **Section banners** in source: `# ---------- Section ----------` comment headers throughout.
- **Dataclasses** for content models: `@dataclass` `Release` in `generate_press_pdfs.py` (lines 112–119).
- **Output paths**: write to `static/documents/press/<date>/<slug>.pdf` and `static/images/press/<slug>.jpg`. Always `OUT_DIR.mkdir(parents=True, exist_ok=True)`.
- **Fonts**: Poppins (as Manrope proxy) and Lato (as Public Sans proxy) loaded from system paths (`/usr/share/fonts/truetype/google-fonts`, `/usr/share/fonts/truetype/lato`). Documented in the docstring as "Manrope proxy" / "Public Sans proxy" — these scripts assume those system fonts are present.
- **No virtualenv / requirements.txt**: dependencies (`reportlab`, `Pillow`) are assumed available in the host environment. There is no Python packaging story.
- **Type hints** used pragmatically (`list[Release]`, `list: []` for reportlab flowables).
- Run as `python3 scripts/generate_press_pdfs.py` from repo root; `__main__` block iterates the `RELEASES` list and prints `wrote <path> (<size> KB)`.

## Forms

Formspree submissions only. Form ID `mvzvgdbl` lives in `hugo.toml` under `[params].formspreeId` and is referenced in templates via:
```html
<form action="https://formspree.io/f/{{ .Site.Params.formspreeId }}" method="POST">
```
Do not hardcode the form ID in templates; always read from site params.

## Branding & Voice

Per `docs/brand/DESIGN.md` and the published copy:

- **Tone**: editorial, authoritative, plainspoken. Think broadsheet news, not campaign flyer.
- **Cornwall-first**: name Cornwall, named places (Mevagissey, Camborne West, Constantine), and Cornish identity (St Piran's flag, granite, Atlantic) in copy. Avoid generic UK-political language.
- **Independent positioning**: copy consistently distinguishes CING from political parties — "no whips", "no national agenda", "free from party politics", "non-aligned".
- **Councillor titles**: "Cllr" abbreviation in body copy; full name with role in headlines. Email pattern is `cllr.<first>.<last>@cornwall.gov.uk`.
- **Headline rhythm**: short two-part hero headlines split by `<br/>` with the second line in tertiary or contrast colour — "Local Voice. / Local Action.", "Grounded in Granite. / Focused on Horizon.", "Standing for / Cornwall." Maintain this cadence on new section heroes.
- **Pull quotes**: blockquotes in news/press content are styled with a left border in tertiary gold and italic secondary text (`layouts/news/single.html` line 72). Use them sparingly for direct quotation.

---

*Convention analysis: 2026-04-26*
