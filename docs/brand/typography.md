# CING Brand Typography

> **See also**: [`DESIGN.md`](DESIGN.md) — the master Stitch design system document ("Kernow Horizon") with creative direction for type usage.

Typography system derived from the Stitch design system, using Material Design 3 type scale conventions.

## Font families

| Role | Font | Source | Weights |
|------|------|--------|---------|
| **Display / Headline** | [Manrope](https://fonts.google.com/specimen/Manrope) | Google Fonts | 400, 700, 800 |
| **Body / Label** | [Public Sans](https://fonts.google.com/specimen/Public+Sans) | Google Fonts | 300, 400, 500, 600 |

### Tailwind config classes

```
font-headline → Manrope
font-body    → Public Sans
font-label   → Public Sans
```

## Type scale

### Display (editorial statements, hero text)

| Variant | Font | Usage |
|---------|------|-------|
| Display Large | Manrope 800 | Hero headlines, full-width statements |
| Display Medium | Manrope 700 | Section-level editorial statements |
| Display Small | Manrope 700 | Smaller editorial emphasis |

### Headline / Title (section headings, page titles)

| Variant | Font | Usage |
|---------|------|-------|
| Headline Large | Manrope 700 | Page titles |
| Headline Medium | Manrope 700 | Section headings |
| Title Large | Manrope 700 | Card titles, subsections |
| Title Medium | Manrope 400 | Minor headings |

### Body (prose content)

| Variant | Font | Usage |
|---------|------|-------|
| Body Large | Public Sans 400, 1rem | Standard body text |
| Body Medium | Public Sans 400 | Secondary prose, descriptions |
| Body Small | Public Sans 300 | Fine print, captions |

### Label (metadata, navigation)

| Variant | Font | Usage |
|---------|------|-------|
| Label Large | Public Sans 600 | Navigation items, button text |
| Label Medium | Public Sans 500 | Metadata, overlines, tags |
| Label Small | Public Sans 500 | Supporting metadata |

## Icon font

- **Material Symbols Outlined** (Google Fonts, variable)
- Default settings: `'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24`
- Class: `material-symbols-outlined`

## Loading strategy

Fonts loaded via Google Fonts CDN with preconnect hints:

```html
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;700;800&family=Public+Sans:wght@300;400;500;600&display=swap" rel="stylesheet" />
```

Phase 2 plan: migrate to self-hosted fonts for improved performance.
