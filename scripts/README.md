# Press Toolchain — Local Reproducibility

The `generate_press_pdfs.py` and `generate_press_heroes.py` scripts produce
branded PDFs and JPEG hero images for press releases. Both depend on a small
set of pinned Python packages and bundled SIL-OFL fonts.

## Setup

From the repo root:

    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r scripts/requirements.txt

No system font installation is required. Fonts are bundled under
`scripts/fonts/` (Manrope and Public Sans, both SIL-OFL 1.1 licensed).

## Run

    python scripts/generate_press_heroes.py   # writes hero JPGs to static/images/press/
    python scripts/generate_press_pdfs.py     # writes branded PDFs to static/documents/press/

## Note for maintainers

The scripts register fonts under their original face names (`"Poppins-Black"`,
`"Lato"`, `"Lato-Italic"`, etc.) for compatibility — only the underlying file
paths point to Manrope/Public Sans now. This is intentional; do not "tidy up"
the face-name vs file-name mismatch unless you also update every
`fontName=` reference in the scripts.

Outputs (PDFs and hero JPGs) are git-tracked artefacts; the existing
committed PDFs are the authoritative shipped versions.
