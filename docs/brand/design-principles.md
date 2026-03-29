# CING Design Principles

> **See also**: [`DESIGN.md`](DESIGN.md) — the master Stitch design system document ("Kernow Horizon"). This file provides implementation-specific guidance for the Hugo/Tailwind codebase; DESIGN.md is the creative authority.

Core design principles governing the CING website, derived from the Stitch design system and Material Design 3.

## Visual language

### Editorial high-end aesthetic

The site uses a political editorial aesthetic — clean, authoritative, spacious. Think broadsheet newspaper meets modern political campaign site. Avoid anything that feels "templated" or generic.

### Cornish identity

- **St Piran's Gold** (`tertiary` tokens) references Cornwall's mining heritage and the St Piran flag
- **Deep navy** (`primary`) evokes Cornwall's Atlantic coastline
- **Granite grey** (`secondary`) reflects Cornwall's stone landscape
- Imagery: Cornish landscapes, community scenes (AI-generated, sourced from Stitch project)

## Layout principles

### Surface layering, not borders

Sections are separated by tonal surface shifts — **never 1px borders**. Use the surface tier system:

```
surface-container-lowest  →  surface-container-low  →  surface-container  →  surface-container-high  →  surface-container-highest
```

Alternate between surface tiers for visual rhythm without dividers.

### Generous negative space

- Large padding between sections
- Content should breathe — avoid cramming elements
- Editorial feel requires restraint

### Bento grid layouts

Key pages use bento-style card grids — asymmetric, varied-size cards that create visual interest without rigidity. Used on: homepage, policies, news listing, get-involved.

## Component patterns

### Cards

- Background: `surface-container-lowest` (white)
- Shadow: `editorial-shadow` — `box-shadow: 0 8px 40px rgba(23, 28, 32, 0.04)`
- No visible borders
- Rounded corners: `lg` (0.25rem) for cards, `xl` (0.5rem) for larger containers

### Buttons

- Rounded corners: `md` (0.375rem) for standard buttons
- Primary CTA: `primary` background, `on-primary` text
- Gold CTA: `tertiary` background for prestige actions (Join, Donate)
- Pill shape: only for chips and tags

### Navigation

- Glassmorphism effect on desktop nav
- Mobile: hamburger menu (vanilla JS, no framework)
- Fixed/sticky header

### Councillor photos

- Greyscale by default
- Colour on hover: `grayscale group-hover:grayscale-0` transition
- Creates editorial "newspaper" feel

### Border radius scale

```
DEFAULT: 0.125rem  (subtle rounding)
lg:      0.25rem   (cards)
xl:      0.5rem    (large containers)
full:    0.75rem   (pills/chips)
```

## Stitch design reference

- **Project**: "Get Involved — Cornish Nonaligned Group"
- **Project ID**: `3771371856444129928`
- **Preferred variants**: "CING Brand Update" screens
- **Screen IDs**:
  - Home: `e476779951c5430ebc7e39ea3bf5b8b4`
  - Our Policies: `6245bd86799b40198ffe69462f02f5ec`
  - Latest News: `81cd485d74de4d2d9a16c01e6dddcdea`
  - Get Involved: `b6dae3baeedb429eac11748775fc2004`

HTML snapshots from Stitch are stored in `.reference/` (gitignored) when available.
