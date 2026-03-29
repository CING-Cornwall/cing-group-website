# CING Brand Colours

> **See also**: [`DESIGN.md`](DESIGN.md) — the master Stitch design system document ("Kernow Horizon") with creative intent and naming conventions (e.g. "The Deep Sea", "The Granite", "St Piran's Gold").

Colour system based on Material Design 3 tokens, derived from the Stitch design system ("CING Brand Update" variants, project ID `3771371856444129928`).

## Primary palette

| Token | Hex | RGB | Usage |
|-------|-----|-----|-------|
| `primary` | `#00263b` | 0, 38, 59 | Headers, high-authority elements, nav bar |
| `primary-container` | `#003d5b` | 0, 61, 91 | Hero backgrounds, Community Anchor sections |
| `primary-fixed` | `#cae6ff` | 202, 230, 255 | Light-fill areas with primary association |
| `primary-fixed-dim` | `#9eccf0` | 158, 204, 240 | Dimmed primary-fixed variant |
| `on-primary` | `#ffffff` | 255, 255, 255 | Text/icons on primary backgrounds |
| `on-primary-container` | `#7ba8cb` | 123, 168, 203 | Text/icons on primary-container backgrounds |
| `on-primary-fixed` | `#001e2f` | 0, 30, 47 | Text on primary-fixed backgrounds |
| `on-primary-fixed-variant` | `#184b6a` | 24, 75, 106 | Secondary text on primary-fixed |
| `inverse-primary` | `#9eccf0` | 158, 204, 240 | Primary for dark/inverse contexts |

## Secondary palette

| Token | Hex | RGB | Usage |
|-------|-----|-----|-------|
| `secondary` | `#595f64` | 89, 95, 100 | Secondary actions, subtle text |
| `secondary-container` | `#dbe0e6` | 219, 224, 230 | Card backgrounds, chips |
| `secondary-fixed` | `#dee3e9` | 222, 227, 233 | Fixed secondary fills |
| `secondary-fixed-dim` | `#c1c7cd` | 193, 199, 205 | Dimmed secondary-fixed |
| `on-secondary` | `#ffffff` | 255, 255, 255 | Text on secondary backgrounds |
| `on-secondary-container` | `#5d6368` | 93, 99, 104 | Text on secondary-container |
| `on-secondary-fixed` | `#161c21` | 22, 28, 33 | Text on secondary-fixed |
| `on-secondary-fixed-variant` | `#41474c` | 65, 71, 76 | Secondary text on secondary-fixed |

## Tertiary palette (St Piran's Gold)

| Token | Hex | RGB | Usage |
|-------|-----|-----|-------|
| `tertiary` | `#705d00` | 112, 93, 0 | Prestige accent — Join/Donate CTAs |
| `tertiary-container` | `#c9a900` | 201, 169, 0 | Gold accent backgrounds, badges |
| `tertiary-fixed` | `#ffe16d` | 255, 225, 109 | Light gold fills |
| `tertiary-fixed-dim` | `#e9c400` | 233, 196, 0 | Dimmed gold |
| `on-tertiary` | `#ffffff` | 255, 255, 255 | Text on tertiary backgrounds |
| `on-tertiary-container` | `#4c3f00` | 76, 63, 0 | Text on tertiary-container |
| `on-tertiary-fixed` | `#221b00` | 34, 27, 0 | Text on tertiary-fixed |
| `on-tertiary-fixed-variant` | `#544600` | 84, 70, 0 | Secondary text on tertiary-fixed |

## Surface palette

| Token | Hex | RGB | Usage |
|-------|-----|-----|-------|
| `surface` | `#f6faff` | 246, 250, 255 | Default page background |
| `surface-bright` | `#f6faff` | 246, 250, 255 | Brightest surface variant |
| `surface-dim` | `#d6dadf` | 214, 218, 223 | Dimmed/muted backgrounds |
| `surface-container-lowest` | `#ffffff` | 255, 255, 255 | Card backgrounds, overlays |
| `surface-container-low` | `#f0f4f9` | 240, 244, 249 | Alternating section backgrounds |
| `surface-container` | `#eaeef3` | 234, 238, 243 | Standard container fills |
| `surface-container-high` | `#e4e9ed` | 228, 233, 237 | Elevated containers |
| `surface-container-highest` | `#dfe3e8` | 223, 227, 232 | Highest-elevation containers |
| `surface-variant` | `#dfe3e8` | 223, 227, 232 | Alternative surface |
| `surface-tint` | `#346383` | 52, 99, 131 | Tint overlay for elevation |

## Semantic colours

| Token | Hex | RGB | Usage |
|-------|-----|-----|-------|
| `on-surface` | `#171c20` | 23, 28, 32 | Primary text (never pure black) |
| `on-surface-variant` | `#41474d` | 65, 71, 77 | Secondary/supporting text |
| `on-background` | `#171c20` | 23, 28, 32 | Body text on background |
| `background` | `#f6faff` | 246, 250, 255 | Full page background |
| `outline` | `#72787e` | 114, 120, 126 | Borders, dividers |
| `outline-variant` | `#c1c7ce` | 193, 199, 206 | Ghost borders (use at 20% opacity) |
| `inverse-surface` | `#2c3135` | 44, 49, 53 | Dark surface for inverse elements |
| `inverse-on-surface` | `#edf1f6` | 237, 241, 246 | Text on inverse surfaces |

## Error colours

| Token | Hex | Usage |
|-------|-----|-------|
| `error` | `#ba1a1a` | Error states, destructive actions |
| `error-container` | `#ffdad6` | Error background fills |
| `on-error` | `#ffffff` | Text on error backgrounds |
| `on-error-container` | `#93000a` | Text on error-container |

## Design principles

- **No 1px borders** — sections separated by tonal surface shifts
- **Never pure black text** — use `on-surface` (`#171c20`) or `on-background`
- **Elevation via layering** — surface tiers, not drop shadows
- **Editorial shadow** — when needed, use `box-shadow: 0 8px 40px rgba(23, 28, 32, 0.04)` (ambient, 4% opacity)
- **Gold accent sparingly** — reserve `tertiary` tokens for high-value CTAs and prestige elements
