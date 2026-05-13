#!/usr/bin/env python3
"""Generate CING-branded hero images for 21 April 2026 Full Council press releases.

Design system: Kernow Horizon ("Modern Monolith")
- Primary navy  #00263b  -> deeper navy background
- Primary container #003d5b -> gradient partner
- Tertiary gold #705d00 / container #c9a900 -> accents
- Typography: Poppins Black / Poppins SemiBold as Manrope proxy

Each image:
- 1600x800 (2:1) navy gradient
- Gold accent strip, overline label, display headline, topic motif
- Small CING wordmark bottom-left

Output: assets/images/press/<slug>.jpg
  (Hugo's responsive-image.html partial uses `resources.Get`, which reads
  from assets/ — not static/. Files dropped in static/ would serve at the
  same URL via Hugo's static-passthrough, but would bypass the responsive
  picture/webp pipeline and the press/single.html partial wouldn't find them.)
"""

from __future__ import annotations

import math
import os
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "assets" / "images" / "press"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ---------- Brand palette ----------
NAVY_DEEP = (0, 38, 59)          # primary       #00263b
NAVY = (0, 61, 91)               # primary-container #003d5b
NAVY_BRIGHT = (26, 90, 128)      # near on-primary-fixed-variant
GOLD = (201, 169, 0)             # tertiary-container #c9a900
GOLD_DEEP = (112, 93, 0)         # tertiary #705d00
IVORY = (246, 250, 255)          # surface #f6faff
STONE = (193, 199, 206)          # outline-variant

# ---------- Fonts ----------
# Fonts bundled under scripts/fonts/ (SIL-OFL 1.1).
# Constant names kept; only the right-hand-side paths change.
_F = Path(__file__).parent / "fonts"
POPPINS_BLACK  = str(_F / "Manrope-Bold.ttf")
POPPINS_MEDIUM = str(_F / "Manrope-Regular.ttf")
LATO_BOLD      = str(_F / "PublicSans-Bold.ttf")
LATO_REG       = str(_F / "PublicSans-Regular.ttf")


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size=size)


# ---------- Gradient background ----------

def make_gradient(width: int, height: int) -> Image.Image:
    """Top-left NAVY_DEEP -> bottom-right NAVY radial-ish linear gradient."""
    base = Image.new("RGB", (width, height), NAVY_DEEP)
    draw = ImageDraw.Draw(base)
    for y in range(height):
        t = y / height
        r = int(NAVY_DEEP[0] + (NAVY[0] - NAVY_DEEP[0]) * t)
        g = int(NAVY_DEEP[1] + (NAVY[1] - NAVY_DEEP[1]) * t)
        b = int(NAVY_DEEP[2] + (NAVY[2] - NAVY_DEEP[2]) * t)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # subtle diagonal lightening from lower-right
    glow = Image.new("RGB", (width, height), (0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    cx, cy = int(width * 0.85), int(height * 0.95)
    max_r = int(math.hypot(width, height) * 0.9)
    for r in range(max_r, 0, -6):
        alpha = max(0, int(40 * (1 - r / max_r)))
        glow_draw.ellipse(
            [cx - r, cy - r, cx + r, cy + r],
            fill=(alpha, alpha, alpha),
        )
    glow = glow.filter(ImageFilter.GaussianBlur(radius=60))
    base = Image.composite(
        Image.new("RGB", (width, height), NAVY_BRIGHT),
        base,
        glow.convert("L"),
    )

    # very light noise for texture (via speckle on alpha layer)
    return base


# ---------- Topic motifs (single-colour vector-style) ----------

def motif_bus(draw: ImageDraw.ImageDraw, cx: int, cy: int, scale: float = 1.0):
    s = scale
    # abstract "route" curves + schoolbag chip
    gold = GOLD
    for i, dy in enumerate([-40, 0, 40, 80]):
        y = cy + dy * s
        draw.arc(
            [cx - int(260 * s), int(y - 120 * s),
             cx + int(260 * s), int(y + 120 * s)],
            start=200 + i * 4, end=340 - i * 4,
            fill=gold, width=max(2, int(6 * s)),
        )
    # schoolbook / bag rectangle
    draw.rectangle(
        [cx - int(90 * s), cy + int(110 * s),
         cx + int(90 * s), cy + int(240 * s)],
        outline=gold, width=max(2, int(7 * s)),
    )
    # bus windows chips
    for i in range(3):
        x0 = cx - int(60 * s) + i * int(55 * s)
        draw.rectangle(
            [x0, cy + int(140 * s), x0 + int(36 * s), cy + int(180 * s)],
            fill=gold,
        )


def motif_tooth(draw: ImageDraw.ImageDraw, cx: int, cy: int, scale: float = 1.0):
    s = scale
    gold = GOLD
    # stylized molar silhouette (two cusps + twin roots)
    # top lobes
    draw.ellipse(
        [cx - int(170 * s), cy - int(170 * s),
         cx - int(10 * s), cy + int(20 * s)], outline=gold, width=max(3, int(7 * s)),
    )
    draw.ellipse(
        [cx + int(10 * s), cy - int(170 * s),
         cx + int(170 * s), cy + int(20 * s)], outline=gold, width=max(3, int(7 * s)),
    )
    # connector band
    draw.rectangle(
        [cx - int(120 * s), cy - int(40 * s),
         cx + int(120 * s), cy + int(40 * s)], outline=gold, width=max(3, int(7 * s)),
    )
    # roots
    draw.polygon(
        [
            (cx - int(110 * s), cy + int(40 * s)),
            (cx - int(60 * s), cy + int(40 * s)),
            (cx - int(80 * s), cy + int(220 * s)),
        ],
        outline=gold,
    )
    draw.polygon(
        [
            (cx + int(60 * s), cy + int(40 * s)),
            (cx + int(110 * s), cy + int(40 * s)),
            (cx + int(80 * s), cy + int(220 * s)),
        ],
        outline=gold,
    )
    # sparkle highlight
    hx, hy = cx + int(130 * s), cy - int(150 * s)
    for r in (10, 26, 42):
        draw.arc(
            [hx - r, hy - r, hx + r, hy + r],
            start=210, end=330, fill=gold, width=max(2, int(4 * s)),
        )


def motif_cornwall(draw: ImageDraw.ImageDraw, cx: int, cy: int, scale: float = 1.0):
    """Stylized Cornish peninsula + gold pin."""
    s = scale
    gold = GOLD
    # abstract peninsula outline — elongated pointing SW
    pts = [
        (cx - 220, cy - 40),
        (cx - 160, cy - 90),
        (cx - 60,  cy - 100),
        (cx + 40,  cy - 70),
        (cx + 140, cy - 30),
        (cx + 220, cy + 10),
        (cx + 180, cy + 60),
        (cx + 80,  cy + 50),
        (cx - 30,  cy + 80),
        (cx - 130, cy + 70),
        (cx - 210, cy + 30),
    ]
    pts = [(int(cx + (x - cx) * s), int(cy + (y - cy) * s)) for (x, y) in pts]
    draw.line(pts + [pts[0]], fill=gold, width=max(3, int(7 * s)), joint="curve")

    # gold pins dotted across peninsula (neighbourhoods)
    for (px, py) in [
        (cx - 160, cy - 40),
        (cx - 60, cy - 50),
        (cx + 60, cy - 20),
        (cx + 150, cy + 20),
        (cx - 100, cy + 30),
    ]:
        r = int(10 * s)
        px = int(cx + (px - cx) * s)
        py = int(cy + (py - cy) * s)
        draw.ellipse([px - r, py - r, px + r, py + r], fill=gold)


def motif_leaf(draw: ImageDraw.ImageDraw, cx: int, cy: int, scale: float = 1.0):
    s = scale
    gold = GOLD
    # stylised leaf (ogive)
    pts = [
        (cx,              cy - int(220 * s)),
        (cx + int(140 * s), cy - int(80 * s)),
        (cx + int(180 * s), cy + int(60 * s)),
        (cx + int(60 * s),  cy + int(200 * s)),
        (cx,               cy + int(230 * s)),
        (cx - int(60 * s),  cy + int(200 * s)),
        (cx - int(180 * s), cy + int(60 * s)),
        (cx - int(140 * s), cy - int(80 * s)),
    ]
    draw.polygon(pts, outline=gold)
    # central vein
    draw.line(
        [(cx, cy - int(220 * s)), (cx, cy + int(230 * s))],
        fill=gold, width=max(2, int(5 * s)),
    )
    # side veins
    for dy in (-140, -60, 20, 100):
        y = cy + int(dy * s)
        draw.line(
            [(cx, y), (cx + int(110 * s), y + int(40 * s))],
            fill=gold, width=max(1, int(3 * s)),
        )
        draw.line(
            [(cx, y), (cx - int(110 * s), y + int(40 * s))],
            fill=gold, width=max(1, int(3 * s)),
        )
    # caution "drop" top-right
    dx, dy = cx + int(180 * s), cy - int(220 * s)
    r = int(28 * s)
    draw.polygon(
        [(dx, dy - r * 2), (dx - r, dy), (dx, dy + r), (dx + r, dy)],
        fill=gold,
    )


def motif_house(draw: ImageDraw.ImageDraw, cx: int, cy: int, scale: float = 1.0):
    """Stylised terrace of three houses + 'plan' grid behind — trust/planning motif."""
    s = scale
    gold = GOLD
    w = max(2, int(6 * s))

    # faint grid behind (blueprint feel)
    grid = GOLD_DEEP
    for i in range(-3, 4):
        x = cx + int(i * 70 * s)
        draw.line(
            [(x, cy - int(220 * s)), (x, cy + int(220 * s))],
            fill=grid, width=max(1, int(2 * s)),
        )
    for j in range(-3, 4):
        y = cy + int(j * 60 * s)
        draw.line(
            [(cx - int(250 * s), y), (cx + int(250 * s), y)],
            fill=grid, width=max(1, int(2 * s)),
        )

    # three house silhouettes forming a short terrace
    # each house: base rectangle + triangular roof
    # centre house is tallest, flanking houses step down
    def house(ox: int, base_w: int, base_h: int, roof_h: int):
        x0 = cx + int(ox * s) - int(base_w * s) // 2
        x1 = x0 + int(base_w * s)
        y1 = cy + int(120 * s)
        y0 = y1 - int(base_h * s)
        # walls
        draw.rectangle([x0, y0, x1, y1], outline=gold, width=w)
        # roof
        apex = ((x0 + x1) // 2, y0 - int(roof_h * s))
        draw.polygon([(x0, y0), apex, (x1, y0)], outline=gold)
        # door
        dw = int(22 * s)
        dh = int(46 * s)
        dx0 = (x0 + x1) // 2 - dw // 2
        draw.rectangle([dx0, y1 - dh, dx0 + dw, y1], outline=gold, width=max(2, int(4 * s)))
        # window
        ww = int(20 * s)
        wh = int(20 * s)
        wx0 = x0 + int(18 * s)
        wy0 = y0 + int(22 * s)
        draw.rectangle([wx0, wy0, wx0 + ww, wy0 + wh], outline=gold, width=max(2, int(3 * s)))
        wx1 = x1 - int(18 * s) - ww
        draw.rectangle([wx1, wy0, wx1 + ww, wy0 + wh], outline=gold, width=max(2, int(3 * s)))

    house(ox=-180, base_w=150, base_h=140, roof_h=60)
    house(ox=0,    base_w=170, base_h=180, roof_h=80)
    house(ox=180,  base_w=150, base_h=140, roof_h=60)


def motif_road(draw: ImageDraw.ImageDraw, cx: int, cy: int, scale: float = 1.0):
    """Receding carriageway with dashed centre line — highways / road markings."""
    s = scale
    gold = GOLD
    grid = GOLD_DEEP
    w = max(3, int(7 * s))
    top_y = cy - int(220 * s)
    bot_y = cy + int(220 * s)
    top_w = int(40 * s)   # narrow at horizon
    bot_w = int(220 * s)  # wide in foreground
    # Faint horizon line (grid colour) behind the road
    draw.line(
        [(cx - int(280 * s), top_y - int(8 * s)),
         (cx + int(280 * s), top_y - int(8 * s))],
        fill=grid, width=max(1, int(2 * s)),
    )
    # Carriageway edges (perspective)
    draw.line([(cx - bot_w, bot_y), (cx - top_w, top_y)], fill=gold, width=w)
    draw.line([(cx + bot_w, bot_y), (cx + top_w, top_y)], fill=gold, width=w)
    # Dashed centre line — dashes grow with perspective.
    dashes = 6
    for i in range(dashes):
        t0 = i / dashes
        t1 = t0 + 0.55 / dashes
        y0 = top_y + int((bot_y - top_y) * t0)
        y1 = top_y + int((bot_y - top_y) * t1)
        # Centre x interpolated (just cx since road is symmetric)
        dash_w = int((4 + (t0 + t1) * 14) * s)
        draw.rectangle([cx - dash_w // 2, y0, cx + dash_w // 2, y1], fill=gold)
    # Yellow-line accent at the right kerb — alludes to the budget line in the release
    kerb_w = max(2, int(4 * s))
    draw.line(
        [(cx + bot_w + int(20 * s), bot_y),
         (cx + top_w + int(8 * s), top_y + int(60 * s))],
        fill=gold, width=kerb_w,
    )


def motif_book_heart(draw: ImageDraw.ImageDraw, cx: int, cy: int, scale: float = 1.0):
    """Open book with a heart hovering above — wellbeing / SEND / schools."""
    s = scale
    gold = GOLD
    w_outline = max(3, int(6 * s))
    # Open book — two facing pages with a centre spine sag.
    left_page = [
        (cx - int(240 * s), cy + int(40 * s)),
        (cx - int(210 * s), cy - int(90 * s)),
        (cx - int(20 * s),  cy - int(40 * s)),
        (cx,                cy + int(120 * s)),
    ]
    right_page = [
        (cx,                cy + int(120 * s)),
        (cx + int(20 * s),  cy - int(40 * s)),
        (cx + int(210 * s), cy - int(90 * s)),
        (cx + int(240 * s), cy + int(40 * s)),
    ]
    draw.polygon(left_page, outline=gold)
    draw.polygon(right_page, outline=gold)
    # Page lines (rule lines suggesting text).
    for dy in (-50, -20, 10, 40):
        draw.line(
            [(cx - int(190 * s), cy + int(dy * s)),
             (cx - int(30 * s),  cy + int(dy * s) + int(6 * s))],
            fill=gold, width=max(1, int(3 * s)),
        )
        draw.line(
            [(cx + int(30 * s), cy + int(dy * s) + int(6 * s)),
             (cx + int(190 * s), cy + int(dy * s))],
            fill=gold, width=max(1, int(3 * s)),
        )
    # Heart hovering above the spine.
    hr = int(46 * s)
    hx, hy = cx, cy - int(170 * s)
    # Two lobes (circles) + bottom triangle, filled gold for emphasis.
    draw.ellipse([hx - hr, hy - hr, hx, hy + int(hr * 0.1)], fill=gold)
    draw.ellipse([hx, hy - hr, hx + hr, hy + int(hr * 0.1)], fill=gold)
    draw.polygon([
        (hx - hr, hy - int(hr * 0.1)),
        (hx + hr, hy - int(hr * 0.1)),
        (hx, hy + int(hr * 1.25)),
    ], fill=gold)


def motif_microphone(draw: ImageDraw.ImageDraw, cx: int, cy: int, scale: float = 1.0):
    """Studio microphone with sound waves — free speech / expression."""
    s = scale
    gold = GOLD
    w = max(3, int(7 * s))
    # Mic capsule (rounded rectangle approximation: ellipse).
    cap_left  = cx - int(80 * s)
    cap_right = cx + int(80 * s)
    cap_top   = cy - int(220 * s)
    cap_bot   = cy + int(10 * s)
    draw.ellipse([cap_left, cap_top, cap_right, cap_bot], outline=gold, width=w)
    # Grille lines inside capsule.
    for dy in (-60, -25, 10, 45):
        y = cy - int(100 * s) + int(dy * s)
        draw.line(
            [(cap_left + int(18 * s), y), (cap_right - int(18 * s), y)],
            fill=gold, width=max(1, int(3 * s)),
        )
    # U-shaped shock-mount arc below the capsule.
    arc_left  = cx - int(150 * s)
    arc_right = cx + int(150 * s)
    draw.arc(
        [arc_left, cy - int(80 * s), arc_right, cy + int(170 * s)],
        start=0, end=180, fill=gold, width=w,
    )
    # Vertical stem from arc base to mic stand.
    stem_top = cy + int(140 * s)
    stem_bot = cy + int(210 * s)
    draw.line([(cx, stem_top), (cx, stem_bot)], fill=gold, width=w)
    # Horizontal base.
    base_half = int(120 * s)
    draw.line(
        [(cx - base_half, stem_bot), (cx + base_half, stem_bot)],
        fill=gold, width=w + 2,
    )
    # Sound-wave arcs on the right — three concentric arcs opening outward.
    centre_x = cx + int(40 * s)
    centre_y = cy - int(110 * s)
    for r in (int(110 * s), int(160 * s), int(210 * s)):
        draw.arc(
            [centre_x - r, centre_y - r, centre_x + r, centre_y + r],
            start=310, end=50, fill=gold, width=max(2, int(4 * s)),
        )


MOTIFS = {
    "bus": motif_bus,
    "tooth": motif_tooth,
    "cornwall": motif_cornwall,
    "leaf": motif_leaf,
    "house": motif_house,
    "road": motif_road,
    "book_heart": motif_book_heart,
    "microphone": motif_microphone,
}


# ---------- Text helpers ----------

def wrap_text(text: str, max_chars: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    line: list[str] = []
    for w in words:
        probe = (" ".join(line + [w])).strip()
        if len(probe) > max_chars and line:
            lines.append(" ".join(line))
            line = [w]
        else:
            line.append(w)
    if line:
        lines.append(" ".join(line))
    return lines


def draw_overline(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    color=GOLD,
):
    fnt = font(POPPINS_MEDIUM, 24)
    # tracked-out letter spacing approx by rendering char-by-char
    x, y = xy
    tracked = " ".join(list(text.upper()))
    draw.text((x, y), tracked, fill=color, font=fnt)


def draw_wordmark(
    draw: ImageDraw.ImageDraw, xy: tuple[int, int], subtitle: str | None = None
):
    x, y = xy
    draw.text(
        (x, y),
        "CING",
        fill=IVORY,
        font=font(POPPINS_BLACK, 40),
    )
    if subtitle:
        draw.text(
            (x, y + 50),
            subtitle,
            fill=STONE,
            font=font(POPPINS_MEDIUM, 16),
        )


# ---------- Composition ----------

@dataclass
class Release:
    slug: str
    overline: str
    headline: str
    motif: str
    kicker: str = "PRESS RELEASE  ·  FULL COUNCIL  ·  21 APRIL 2026"


def render(release: Release) -> Path:
    W, H = 1600, 800
    img = make_gradient(W, H)
    draw = ImageDraw.Draw(img)

    # ---- gold vertical accent bar (left) ----
    draw.rectangle([64, 96, 72, H - 96], fill=GOLD)

    # ---- kicker (overline) ----
    draw_overline(draw, (100, 100), release.kicker, color=GOLD)

    # ---- headline ----
    hl_size = 96
    hl_font = font(POPPINS_BLACK, hl_size)
    # widen/narrow based on length
    lines = wrap_text(release.headline, max_chars=24)
    if len(lines) > 3:
        hl_size = 82
        hl_font = font(POPPINS_BLACK, hl_size)
        lines = wrap_text(release.headline, max_chars=26)

    y = 180
    for line in lines:
        draw.text((100, y), line, fill=IVORY, font=hl_font)
        y += hl_size + 10

    # ---- overline below headline ----
    sub_font = font(POPPINS_MEDIUM, 26)
    draw.text(
        (100, y + 20),
        release.overline,
        fill=(158, 204, 240),  # primary-fixed-dim
        font=sub_font,
    )

    # ---- motif (right side, pulled inward from edge) ----
    motif_fn = MOTIFS[release.motif]
    motif_fn(draw, cx=int(W * 0.78), cy=int(H * 0.48), scale=0.75)

    # ---- wordmark ----
    draw_wordmark(
        draw,
        (100, H - 140),
        subtitle="Cornish Independent NonAligned Group",
    )

    # ---- thin gold line (divider above wordmark) ----
    draw.line([(100, H - 160), (260, H - 160)], fill=GOLD, width=3)

    out = OUT_DIR / f"{release.slug}.jpg"
    img.convert("RGB").save(out, "JPEG", quality=86, optimize=True, progressive=True)
    return out


RELEASES: list[Release] = [
    Release(
        slug="mevagissey-school-transport",
        overline="Joint designation for Penrice & Poltair Schools",
        headline="Fair School Transport for Rural Families",
        motif="bus",
    ),
    Release(
        slug="childrens-nhs-dental-care",
        overline="Motion on access to NHS dentistry",
        headline="Every Child Deserves a Dentist",
        motif="tooth",
    ),
    Release(
        slug="rural-deprivation-funding",
        overline="Cornwall excluded from £5.8bn Pride in Place fund",
        headline="Cornwall's Hidden Deprivation",
        motif="cornwall",
    ),
    Release(
        slug="glyphosate-weedkiller-halt",
        overline="Motion to pause the chemical rollout",
        headline="Poison on Our Streets",
        motif="leaf",
    ),
    Release(
        slug="planning-public-trust",
        overline="Question on planning transparency & parish voice",
        headline="Planning Must Earn Public Trust",
        motif="house",
    ),
    # ---- 19 May 2026 Full Council ----
    Release(
        slug="mental-health-wellbeing-schools",
        overline="Motion for a Cabinet Advisory Group on schools, SEND & wellbeing",
        headline="No Child Should Break Down First",
        motif="book_heart",
        kicker="PRESS RELEASE  ·  FULL COUNCIL  ·  19 MAY 2026",
    ),
    Release(
        slug="freedom-of-expression-fair-process",
        overline="Motion on freedom of expression and fair council process",
        headline="Free Speech Underpins Democracy",
        motif="microphone",
        kicker="PRESS RELEASE  ·  FULL COUNCIL  ·  19 MAY 2026",
    ),
    Release(
        slug="road-markings-renewal-motion",
        overline="Caution on the road markings & parking enforcement motion",
        headline="Frontline Repairs Come First",
        motif="road",
        kicker="PRESS RELEASE  ·  FULL COUNCIL  ·  19 MAY 2026",
    ),
]


if __name__ == "__main__":
    for rel in RELEASES:
        p = render(rel)
        size_kb = os.path.getsize(p) // 1024
        print(f"  wrote {p.relative_to(ROOT)}  ({size_kb} KB)")
