#!/usr/bin/env python3
"""Generate CING-branded PDFs for 21 April 2026 Full Council press releases.

Brand system: Kernow Horizon ("Modern Monolith")
    Primary navy       #00263b
    Primary container  #003d5b
    Tertiary gold      #c9a900 / #705d00
    Typography         Poppins (Manrope proxy) + Lato (Public Sans proxy)

For each release in `RELEASES`, the script produces a polished multi-page PDF
with a branded first-page banner, embargo strap, pull quotes, and contact
footer. Output: static/documents/press/2026-04-21/<slug>.pdf
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from reportlab.lib.colors import Color, HexColor
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    NextPageTemplate,
    PageTemplate,
    Paragraph,
    Spacer,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "content" / "press" / "full-council-2026-04-21"
OUT_DIR = ROOT / "static" / "documents" / "press" / "2026-04-21"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ---------- Brand tokens ----------
NAVY_DEEP = HexColor("#00263b")
NAVY = HexColor("#003d5b")
GOLD = HexColor("#c9a900")
GOLD_DEEP = HexColor("#705d00")
STONE = HexColor("#5c6268")
STONE_LIGHT = HexColor("#c1c7ce")
IVORY = HexColor("#f6faff")
ON_SURFACE = HexColor("#171c20")
ON_SURFACE_VARIANT = HexColor("#41474d")

# ---------- Fonts ----------
# Face names kept as-is (Poppins*/Lato) for compatibility with downstream
# ParagraphStyle / canvas.setFont references; files are now Manrope (Bold/Regular)
# and Public Sans (Bold/Regular/Italic), both SIL-OFL 1.1, bundled under
# scripts/fonts/. Do not "tidy" the face-name mismatch without also updating
# every fontName= reference in this file. See scripts/README.md.
FONTS = Path(__file__).parent / "fonts"

pdfmetrics.registerFont(TTFont("Poppins-Black",   str(FONTS / "Manrope-Bold.ttf")))
pdfmetrics.registerFont(TTFont("Poppins-Medium",  str(FONTS / "Manrope-Regular.ttf")))
pdfmetrics.registerFont(TTFont("Poppins-Regular", str(FONTS / "Manrope-Regular.ttf")))
pdfmetrics.registerFont(TTFont("Lato",            str(FONTS / "PublicSans-Regular.ttf")))
pdfmetrics.registerFont(TTFont("Lato-Bold",       str(FONTS / "PublicSans-Bold.ttf")))
pdfmetrics.registerFont(TTFont("Lato-Italic",     str(FONTS / "PublicSans-Italic.ttf")))


# ---------- Styles ----------
BODY = ParagraphStyle(
    name="body",
    fontName="Lato",
    fontSize=10.5,
    leading=16,
    textColor=ON_SURFACE,
    spaceAfter=8,
)
BODY_LEAD = ParagraphStyle(
    name="lead",
    parent=BODY,
    fontSize=12,
    leading=19,
    textColor=ON_SURFACE_VARIANT,
    spaceAfter=14,
)
H2 = ParagraphStyle(
    name="h2",
    fontName="Poppins-Black",
    fontSize=15,
    leading=20,
    textColor=NAVY_DEEP,
    spaceBefore=18,
    spaceAfter=6,
)
QUOTE = ParagraphStyle(
    name="quote",
    fontName="Lato-Italic",
    fontSize=12.5,
    leading=19,
    textColor=NAVY_DEEP,
    leftIndent=18,
    spaceBefore=8,
    spaceAfter=10,
    borderPadding=0,
)
BULLET = ParagraphStyle(
    name="bullet",
    parent=BODY,
    leftIndent=16,
    bulletIndent=4,
    spaceAfter=4,
)


# ---------- Press release content ----------

@dataclass
class Release:
    slug: str
    category: str
    title: str
    strapline: str
    src_md: Path
    image: str  # relative image filename under static/images/press/


RELEASES: list[Release] = [
    Release(
        slug="mevagissey-school-transport",
        category="School Transport",
        title="Mevagissey Families Denied Fair Access to School Transport",
        strapline="Families face inconsistent rules despite children travelling on the same bus.",
        src_md=SOURCE_DIR / "mevagissey-school-transport.md",
        image="mevagissey-school-transport.jpg",
    ),
    Release(
        slug="childrens-nhs-dental-care",
        category="NHS Dentistry",
        title="Access to NHS Dental Care for Children in Cornwall",
        strapline="Cllr O'Connor warns too many children are going without routine dental care.",
        src_md=SOURCE_DIR / "childrens-nhs-dental-care.md",
        image="childrens-nhs-dental-care.jpg",
    ),
    Release(
        slug="rural-deprivation-funding",
        category="Funding & Rural Equity",
        title="Cornwall Must Not Be Overlooked: Councillors Unite to Challenge \"Hidden Deprivation\" Funding Failure",
        strapline="Not a single Cornish community has received funding from the £5.8bn \"Pride in Place\" programme.",
        src_md=SOURCE_DIR / "rural-deprivation-funding.md",
        image="rural-deprivation-funding.jpg",
    ),
    Release(
        slug="glyphosate-weedkiller-halt",
        category="Environment & Public Health",
        title="\"Poison on Our Streets\" Row Erupts as Council Pushes Weedkiller Return",
        strapline="Cornwall Council faces growing backlash over plans to reintroduce glyphosate.",
        src_md=SOURCE_DIR / "glyphosate-weedkiller-halt.md",
        image="glyphosate-weedkiller-halt.jpg",
    ),
    Release(
        slug="planning-public-trust",
        category="Planning & Democracy",
        title="Planning Decisions Must Command Public Trust",
        strapline="Cllr Rowland O'Connor challenges Cornwall Council on transparency, consistency, and the weight given to local voices.",
        src_md=SOURCE_DIR / "planning-public-trust.md",
        image="planning-public-trust.jpg",
    ),
]


# ---------- Markdown → story conversion ----------

BOLD_RE = re.compile(r"\*\*(.+?)\*\*")
ITALIC_RE = re.compile(r"(?<![\*_])\*(?!\s)(.+?)\*(?![\*_])")
LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


def md_inline_to_rl(text: str) -> str:
    """Minimal markdown inline -> reportlab Paragraph markup."""
    text = text.strip()
    text = LINK_RE.sub(lambda m: f'<link href="{m.group(2)}" color="#003d5b">{m.group(1)}</link>', text)
    text = BOLD_RE.sub(r"<b>\1</b>", text)
    text = ITALIC_RE.sub(r"<i>\1</i>", text)
    return text


def parse_markdown(md: str) -> list:
    """Return a list of reportlab flowables from a simple markdown body.

    Supports: H1 (skipped — title is in banner), H2, H3, paragraphs, bullet lists,
    blockquote pull quotes, bold/italic inline, and hr `---`.
    """
    story: list = []
    lines = md.splitlines()
    i = 0

    # leading blank-line skip
    while i < len(lines) and lines[i].strip() == "":
        i += 1

    bullet_buffer: list[str] = []
    quote_buffer: list[str] = []
    paragraph_buffer: list[str] = []

    def flush_paragraph():
        if paragraph_buffer:
            text = " ".join(paragraph_buffer).strip()
            if text:
                story.append(Paragraph(md_inline_to_rl(text), BODY))
            paragraph_buffer.clear()

    def flush_bullets():
        if bullet_buffer:
            for b in bullet_buffer:
                story.append(
                    Paragraph("• " + md_inline_to_rl(b), BULLET)
                )
            story.append(Spacer(1, 4))
            bullet_buffer.clear()

    def flush_quote():
        if quote_buffer:
            text = " ".join(quote_buffer).strip()
            rl = md_inline_to_rl(text)
            story.append(
                Paragraph(f'<font color="#c9a900" size="24">“</font> {rl}', QUOTE)
            )
            quote_buffer.clear()

    skip_first_bold_strap = True

    while i < len(lines):
        raw = lines[i]
        stripped = raw.strip()

        # blank line ends current paragraph block
        if stripped == "":
            flush_paragraph()
            flush_bullets()
            flush_quote()
            i += 1
            continue

        # horizontal rule / divider
        if stripped in {"---", "***", "___"}:
            flush_paragraph()
            flush_bullets()
            flush_quote()
            story.append(Spacer(1, 6))
            i += 1
            continue

        # skip any H1 — the article title is already in the banner, so H1s in the
        # body are editorial cruft (e.g. "# PRESS RELEASE", "# Planning decisions must command public trust")
        if stripped.startswith("# "):
            i += 1
            continue

        # skip ENDS / FOR IMMEDIATE RELEASE in any heading level or bold form
        # (matches "## FOR IMMEDIATE RELEASE", "**ENDS**", "FOR IMMEDIATE RELEASE", etc.)
        _norm_header = stripped.upper().lstrip("#").strip(" *")
        if _norm_header in {"FOR IMMEDIATE RELEASE", "ENDS"}:
            i += 1
            continue

        # H2
        if stripped.startswith("## "):
            flush_paragraph()
            flush_bullets()
            flush_quote()
            story.append(Paragraph(md_inline_to_rl(stripped[3:]), H2))
            i += 1
            continue
        if stripped.startswith("### "):
            flush_paragraph()
            flush_bullets()
            flush_quote()
            story.append(Paragraph(md_inline_to_rl(stripped[4:]), H2))
            i += 1
            continue

        # blockquote
        if stripped.startswith(">"):
            flush_paragraph()
            flush_bullets()
            content = stripped.lstrip("> ").strip()
            if content:
                quote_buffer.append(content)
            else:
                flush_quote()
            i += 1
            continue

        # bullet
        if stripped.startswith("* ") or stripped.startswith("- "):
            flush_paragraph()
            flush_quote()
            bullet_buffer.append(stripped[2:])
            i += 1
            continue

        # skip the strapline if it matches the overline (first bold-only line near top)
        if (
            skip_first_bold_strap
            and stripped.startswith("**")
            and stripped.endswith("**")
            and "FOR IMMEDIATE RELEASE" not in stripped.upper()
            and len(stripped) < 200
        ):
            skip_first_bold_strap = False
            i += 1
            continue

        skip_first_bold_strap = False

        # skip media contact block (starts with "Media Contact" or "Media Enquiries")
        if (
            "Media Contact" in stripped
            or "Media Enquiries" in stripped
            or stripped.startswith("**Media ")
        ):
            # swallow the rest — we put contact block in footer
            break

        paragraph_buffer.append(stripped)
        i += 1

    flush_paragraph()
    flush_bullets()
    flush_quote()
    return story


# ---------- Page template: banner + footer ----------

PAGE_W, PAGE_H = A4  # 595 x 842 pt
MARGIN_X = 20 * mm
BANNER_H = 82 * mm  # first page only
FOOTER_H = 22 * mm


def draw_first_page(canvas, doc, release: Release):
    canvas.saveState()
    # Navy banner block
    canvas.setFillColor(NAVY_DEEP)
    canvas.rect(0, PAGE_H - BANNER_H, PAGE_W, BANNER_H, fill=1, stroke=0)

    # Subtle gradient strip (lighter navy at bottom edge)
    canvas.setFillColor(NAVY)
    canvas.rect(0, PAGE_H - BANNER_H, PAGE_W, 4, fill=1, stroke=0)

    # Gold accent vertical bar
    canvas.setFillColor(GOLD)
    canvas.rect(MARGIN_X, PAGE_H - BANNER_H + 12 * mm, 1.5 * mm, BANNER_H - 24 * mm, fill=1, stroke=0)

    # Overline
    canvas.setFillColor(GOLD)
    canvas.setFont("Poppins-Medium", 8)
    canvas.drawString(
        MARGIN_X + 6 * mm,
        PAGE_H - 14 * mm,
        f"FULL COUNCIL  ·  21 APRIL 2026  ·  {release.category.upper()}",
    )

    # Title (wrap to max 3 lines, shrink if long).
    # Keep title to left ~65% of page so it doesn't collide with the CING wordmark
    # that sits in the top-right of the banner.
    canvas.setFillColor(IVORY)
    title_size = 22
    title_font = "Poppins-Black"
    max_w = PAGE_W * 0.66 - MARGIN_X - 8 * mm
    # naive wrap
    words = release.title.split()
    lines: list[str] = []
    current = ""
    while title_size > 12:
        canvas.setFont(title_font, title_size)
        lines = []
        current = ""
        for w in words:
            probe = (current + " " + w).strip()
            if canvas.stringWidth(probe, title_font, title_size) > max_w:
                if current:
                    lines.append(current)
                current = w
            else:
                current = probe
        if current:
            lines.append(current)
        if len(lines) <= 3:
            break
        title_size -= 1
    y = PAGE_H - 26 * mm
    for line in lines:
        canvas.drawString(MARGIN_X + 6 * mm, y, line)
        y -= title_size + 6

    # Strapline
    canvas.setFillColor(HexColor("#9eccf0"))
    canvas.setFont("Poppins-Medium", 10.5)
    # wrap strapline too
    strap_words = release.strapline.split()
    current = ""
    y -= 6
    for w in strap_words:
        probe = (current + " " + w).strip()
        if canvas.stringWidth(probe, "Poppins-Medium", 10.5) > max_w:
            canvas.drawString(MARGIN_X + 6 * mm, y, current)
            y -= 14
            current = w
        else:
            current = probe
    if current:
        canvas.drawString(MARGIN_X + 6 * mm, y, current)

    # CING wordmark bottom-right of banner
    canvas.setFillColor(IVORY)
    canvas.setFont("Poppins-Black", 14)
    canvas.drawRightString(PAGE_W - MARGIN_X, PAGE_H - 16 * mm, "CING")
    canvas.setFillColor(STONE_LIGHT)
    canvas.setFont("Poppins-Medium", 7)
    canvas.drawRightString(PAGE_W - MARGIN_X, PAGE_H - 20 * mm, "Cornish Independent NonAligned Group")

    # Footer
    _draw_footer(canvas)
    canvas.restoreState()


def draw_later_page(canvas, doc, release: Release):
    canvas.saveState()
    # Thin navy header bar
    canvas.setFillColor(NAVY_DEEP)
    canvas.rect(0, PAGE_H - 10 * mm, PAGE_W, 10 * mm, fill=1, stroke=0)
    canvas.setFillColor(IVORY)
    canvas.setFont("Poppins-Black", 9)
    canvas.drawString(MARGIN_X, PAGE_H - 7 * mm, "CING  ·  PRESS RELEASE")
    canvas.setFillColor(GOLD)
    canvas.setFont("Poppins-Medium", 8)
    canvas.drawRightString(PAGE_W - MARGIN_X, PAGE_H - 7 * mm, "21 APRIL 2026")
    _draw_footer(canvas)
    canvas.restoreState()


def _draw_footer(canvas):
    # gold separator
    canvas.setFillColor(GOLD)
    canvas.rect(MARGIN_X, FOOTER_H, 14 * mm, 1, fill=1, stroke=0)

    canvas.setFillColor(NAVY_DEEP)
    canvas.setFont("Poppins-Black", 8)
    canvas.drawString(MARGIN_X, FOOTER_H - 5 * mm, "MEDIA ENQUIRIES")

    canvas.setFillColor(ON_SURFACE_VARIANT)
    canvas.setFont("Lato", 8)
    canvas.drawString(MARGIN_X, FOOTER_H - 9 * mm, "CING Media Office   ·   cllr.rowland.oconnor@cornwall.gov.uk   ·   +44 (0)7732 079611")
    canvas.drawString(MARGIN_X, FOOTER_H - 13 * mm, "www.cingparty.uk   ·   Cornish Independent NonAligned Group, Cornwall Council")

    # Page number
    canvas.setFillColor(STONE)
    canvas.setFont("Poppins-Medium", 7)
    canvas.drawRightString(PAGE_W - MARGIN_X, FOOTER_H - 9 * mm, f"Page {canvas.getPageNumber()}")


# ---------- Build ----------

def build_pdf(release: Release) -> Path:
    out_path = OUT_DIR / f"{release.slug}.pdf"
    md_text = release.src_md.read_text(encoding="utf-8")

    doc = BaseDocTemplate(
        str(out_path),
        pagesize=A4,
        leftMargin=MARGIN_X,
        rightMargin=MARGIN_X,
        topMargin=BANNER_H + 8 * mm,   # first page: below banner
        bottomMargin=FOOTER_H + 8 * mm,
        title=release.title,
        author="Cornish Independent NonAligned Group",
        subject=f"CING Press Release · 21 April 2026 · {release.category}",
        keywords="CING, press release, Cornwall Council, Full Council, 21 April 2026",
    )

    first_frame = Frame(
        MARGIN_X,
        FOOTER_H + 8 * mm,
        PAGE_W - 2 * MARGIN_X,
        PAGE_H - BANNER_H - FOOTER_H - 16 * mm,
        id="first",
        leftPadding=0,
        rightPadding=0,
        topPadding=0,
        bottomPadding=0,
    )
    later_frame = Frame(
        MARGIN_X,
        FOOTER_H + 8 * mm,
        PAGE_W - 2 * MARGIN_X,
        PAGE_H - 10 * mm - FOOTER_H - 16 * mm,
        id="later",
        leftPadding=0,
        rightPadding=0,
        topPadding=0,
        bottomPadding=0,
    )

    doc.addPageTemplates([
        PageTemplate(
            id="first",
            frames=[first_frame],
            onPage=lambda c, d: draw_first_page(c, d, release),
        ),
        PageTemplate(
            id="later",
            frames=[later_frame],
            onPage=lambda c, d: draw_later_page(c, d, release),
        ),
    ])

    # Build story — switch to "later" template after the first page
    story: list = [NextPageTemplate("later")]

    # lead paragraph in larger type (first real paragraph of the body)
    body_story = parse_markdown(md_text)
    # If the first flowable is a Paragraph styled BODY, swap to BODY_LEAD
    if body_story and isinstance(body_story[0], Paragraph) and body_story[0].style == BODY:
        lead = body_story[0]
        body_story[0] = Paragraph(lead.text, BODY_LEAD)

    story.extend(body_story)

    # Tail: ENDS marker + standfirst
    story.append(Spacer(1, 10))
    story.append(
        Paragraph(
            '<font color="#c9a900"><b>— ENDS —</b></font>',
            ParagraphStyle(
                "ends", parent=BODY, alignment=1, spaceBefore=6, textColor=GOLD_DEEP
            ),
        )
    )

    doc.build(story)
    return out_path


if __name__ == "__main__":
    for rel in RELEASES:
        p = build_pdf(rel)
        size_kb = p.stat().st_size // 1024
        print(f"  wrote {p.relative_to(ROOT)}  ({size_kb} KB)")
