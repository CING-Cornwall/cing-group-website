# Phase 2: Operational safety - Pattern Map

**Mapped:** 2026-04-26
**Files analyzed:** 17 (4 templates with form changes, 6 hero alt-text fixes, 3 article-template alt-text fixes, 1 new layout, 1 workflow, 1 config, 1 archetype, 8 content backfills)
**Analogs found:** 17 / 17 — all changes are reapplications of patterns that already exist on disk.

---

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `.github/workflows/hugo.yml` | CI workflow (modify) | event-driven + scheduled | self — extend existing triggers | self-extension |
| `hugo.toml` | site config (modify) | static config | self — `params.formspreeId` line 8 | self-extension |
| `layouts/get-involved/list.html` (form `:108` contact) | template (modify) | request-response (POST → Formspree) | self — same form lines 108-143 | exact |
| `layouts/get-involved/list.html` (form `:155` newsletter) | template (modify) | request-response | self — same form, plus `layouts/index.html:205` | exact |
| `layouts/index.html` (form `:205` + hero `:11`) | template (modify) | request-response + decorative hero | self — `:205` form, `:9-13` hero | exact |
| `layouts/press/list.html` (form `:147` + hero `:7`) | template (modify) | request-response + decorative hero | self — same file | exact |
| `layouts/about/list.html` (hero `:7`) | template (modify) | decorative hero | self — `:5-9` block | exact |
| `layouts/policies/policies.html` (hero `:6`) | template (modify) | decorative hero | self — `:4-8` block | exact |
| `layouts/councillors/list.html` (hero `:7`) | template (modify) | decorative hero | self — `:5-9` block | exact |
| `layouts/news/list.html` (article hero, two `<img>`) | template (modify) | content image | self — lines 22-25 (featured) and 65-69 (grid) | exact |
| `layouts/news/single.html` (article hero `:54-58`) | template (modify) | content image | self — same block | exact |
| `layouts/press/single.html` (article hero `:28`) | template (modify) | content image | self — same block | exact |
| `layouts/404.html` | NEW template | request-response (error path) | `layouts/_default/baseof.html` `{{ define "main" }}` shell + `layouts/get-involved/list.html` bento CTAs + `layouts/index.html` CTA section | role-match (no existing 404) |
| `archetypes/default.md` | scaffold (modify) | static template | self — current TOML body | exact |
| `content/news/*.md` (×3) | content (modify) | static front matter | self — existing YAML front matter | exact |
| `content/press/full-council-2026-04-21/*.md` (×5) | content (modify) | static front matter | self — existing YAML front matter | exact |

---

## Pattern Assignments

### 1. `.github/workflows/hugo.yml` — CI workflow extension (D-02 guard, D-03 cron)

**Analog:** itself — `.github/workflows/hugo.yml`

**Existing trigger block** (lines 1-8):
```yaml
name: Deploy Hugo site to GitHub Pages

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  workflow_dispatch:
```

→ **Add `schedule:` block** alongside the three existing triggers. CONTEXT D-03 specifies cron `0 7,9,12,17 * * *`. `TZ: Europe/London` is already set on the build env at line 45, so cron expressions interpret as UTC (Hugo respects `TZ` at build time but GitHub Actions cron is always UTC) — schedule using UTC offsets that match the intended UK times, or document the UK-time interpretation in a comment.

**Recommended addition** (after line 8 `workflow_dispatch:`):
```yaml
  schedule:
    # UK morning press windows: 07:00, 09:00, 12:00, 17:00 Europe/London
    # GitHub Actions cron is UTC; adjust if/when DST behaviour matters.
    - cron: "0 7,9,12,17 * * *"
```

**Existing build env** (lines 42-45) — guard step inserts here, before the `Build with Hugo` step:
```yaml
      - name: Build with Hugo
        env:
          HUGO_CACHEDIR: ${{ runner.temp }}/hugo_cache
          HUGO_ENVIRONMENT: production
          TZ: Europe/London
```

**CI guard pattern** (D-02, executor's choice — Python or shell). Insert as a step *before* `Build with Hugo`:

```yaml
      - name: Embargo guard — fail on future-dated press in non-_incoming paths
        run: |
          set -euo pipefail
          python3 - <<'PY'
          import datetime, pathlib, re, sys
          now = datetime.datetime.now(datetime.timezone.utc)
          root = pathlib.Path("content/press")
          violations = []
          for md in root.rglob("*.md"):
              if "_incoming" in md.parts:
                  continue
              text = md.read_text(encoding="utf-8")
              m = re.search(r"^publishDate:\s*(\S+)", text, re.MULTILINE)
              if not m:
                  continue
              try:
                  pd = datetime.datetime.fromisoformat(m.group(1).replace("Z", "+00:00"))
              except ValueError:
                  continue
              if pd.tzinfo is None:
                  pd = pd.replace(tzinfo=datetime.timezone.utc)
              if pd > now:
                  violations.append(f"{md}: publishDate {pd.isoformat()} is in the future")
          if violations:
              print("Embargo guard failed:", file=sys.stderr)
              for v in violations: print("  " + v, file=sys.stderr)
              sys.exit(1)
          print("Embargo guard: no future-dated press files outside _incoming/.")
          PY
```

A pure-bash variant using `awk` is acceptable too; Python is preferred because runners always have `python3` and ISO-8601 parsing is fiddly in awk.

**Cron-trigger compatibility note:** the existing `deploy` job is gated `if: github.event_name == 'push'` (line 57). Cron-triggered runs use `event_name == 'schedule'`. To allow scheduled rebuilds to *deploy* (the whole point of D-03), broaden the gate:
```yaml
    if: github.event_name == 'push' || github.event_name == 'schedule'
```

---

### 2. `hugo.toml` — endpoint split (D-05/FORMS-03)

**Analog:** itself — `hugo.toml:6-9`

**Existing block** (lines 6-9):
```toml
[params]
  description = "The Cornish Independent NonAligned Group — independent councillors serving Cornwall's unique needs on Cornwall Council."
  formspreeId = "mvzvgdbl"
  ogImage = "/images/og-default.jpg"
```

→ **Add three new keys.** Maintainer must populate the IDs from the Formspree dashboard (D-05 manual prerequisite). Keep `formspreeId` as legacy alias during migration:

```toml
[params]
  description = "The Cornish Independent NonAligned Group — independent councillors serving Cornwall's unique needs on Cornwall Council."
  # Formspree endpoints. Three forms in the dashboard, three IDs here.
  # Legacy single-endpoint id retained as alias until migration completes.
  formspreeId = "mvzvgdbl"
  formspreeContactId = "REPLACE_WITH_CONTACT_FORM_ID"
  formspreeNewsletterId = "REPLACE_WITH_NEWSLETTER_FORM_ID"
  formspreePressId = "REPLACE_WITH_PRESS_FORM_ID"
  ogImage = "/images/og-default.jpg"
```

---

### 3. Form pattern — honeypot + consent + endpoint swap (D-04/FORMS-01/02/03)

**Analog (canonical "rich" form):** `layouts/get-involved/list.html:108-143` (contact form).

**Existing rich form, contact** (lines 108-143):
```html
<form action="https://formspree.io/f/{{ .Site.Params.formspreeId }}" method="POST" class="space-y-6">
  <div class="grid grid-cols-1 sm:grid-cols-2 gap-6">
    <div>
      <label for="name" class="block text-sm font-bold text-primary mb-2">Name</label>
      <input type="text" id="name" name="name" required
        class="w-full bg-surface-container-low border-none focus:ring-2 focus:ring-primary rounded-md p-4 text-primary" />
    </div>
    ...
  </div>
  ...
  <button type="submit"
    class="w-full bg-primary text-white py-4 font-bold rounded-md hover:bg-primary-container transition-colors text-lg">
    Send Message
  </button>
  <p class="text-xs text-on-surface-variant text-center opacity-70">
    By submitting, you agree to our <a href="{{ "/privacy/" | relURL }}" class="underline">privacy policy</a>. We never sell your data.
  </p>
</form>
```

**Existing slim form, newsletter** (`layouts/get-involved/list.html:155-162`, mirrored at `layouts/index.html:205-215` and `layouts/press/list.html:147-152`):
```html
<form action="https://formspree.io/f/{{ .Site.Params.formspreeId }}" method="POST" class="flex flex-col sm:flex-row gap-4 max-w-lg mx-auto">
  <input type="hidden" name="_subject" value="Newsletter signup" />
  <input type="email" name="email" required placeholder="Your email address"
    class="flex-grow bg-white/10 border-none focus:ring-2 focus:ring-tertiary rounded-md p-4 text-white placeholder:text-slate-400" />
  <button type="submit" class="bg-tertiary text-on-tertiary px-8 py-4 rounded-md font-bold hover:bg-tertiary-container transition-colors whitespace-nowrap">
    Subscribe
  </button>
</form>
```

**Pattern to apply, all four forms.** Three additions: (a) endpoint param swap, (b) honeypot, (c) PECR consent checkbox (newsletter + press only — the contact form does not need a marketing-consent checkbox because it's transactional, but should still get the honeypot). Per CONTEXT D-04/D-05/discretion notes:

```html
{{/* CONTACT FORM (layouts/get-involved/list.html:108) */}}
<form action="https://formspree.io/f/{{ .Site.Params.formspreeContactId }}" method="POST" class="space-y-6">
  {{/* Honeypot — bots fill this; real users never see it */}}
  <input type="text" name="_gotcha" style="display:none" tabindex="-1" autocomplete="off" aria-hidden="true" />
  ...existing fields unchanged...
</form>
```

```html
{{/* NEWSLETTER FORM — get-involved :155 AND index.html :205 */}}
<form action="https://formspree.io/f/{{ .Site.Params.formspreeNewsletterId }}" method="POST" class="...existing classes...">
  <input type="hidden" name="_subject" value="Newsletter signup" />
  <input type="text" name="_gotcha" style="display:none" tabindex="-1" autocomplete="off" aria-hidden="true" />
  <input type="email" name="email" required placeholder="Your email address" class="..." />

  {{/* PECR explicit-consent — checkbox unticked by default, required to submit */}}
  <label class="flex items-start gap-3 text-sm text-white/90 max-w-lg mx-auto">
    <input type="checkbox" name="marketing_consent" value="yes" required
      class="mt-1 shrink-0 rounded border-white/30 bg-white/10 focus:ring-tertiary" />
    <span>
      I agree to receive occasional email updates from CING. You can unsubscribe at any time.
      See our <a href="{{ "/privacy/" | relURL }}" class="underline text-tertiary-fixed">privacy policy</a>.
    </span>
  </label>

  <button type="submit" class="...">Subscribe</button>
</form>
```

```html
{{/* PRESS LIST FORM (layouts/press/list.html:147) */}}
<form class="space-y-4" action="https://formspree.io/f/{{ .Site.Params.formspreePressId }}" method="POST">
  <input type="hidden" name="_subject" value="Press newsletter signup" />
  <input type="text" name="_gotcha" style="display:none" tabindex="-1" autocomplete="off" aria-hidden="true" />
  <input class="..." placeholder="Email Address" type="email" name="email" required />

  <label class="flex items-start gap-3 text-sm text-on-surface-variant">
    <input type="checkbox" name="marketing_consent" value="yes" required class="mt-1 shrink-0" />
    <span>
      I'm a journalist or press contact and would like to receive CING press releases.
      See our <a href="{{ "/privacy/" | relURL }}" class="underline">privacy policy</a>.
    </span>
  </label>

  <button class="..." type="submit">Subscribe</button>
</form>
```

**Per-form endpoint mapping (D-05):**

| File:line | Form | New endpoint param |
|-----------|------|-------------------|
| `layouts/get-involved/list.html:108` | contact | `formspreeContactId` |
| `layouts/get-involved/list.html:155` | newsletter | `formspreeNewsletterId` |
| `layouts/index.html:205` | homepage newsletter | `formspreeNewsletterId` |
| `layouts/press/list.html:147` | press list | `formspreePressId` |

**Honeypot styling note:** the inline `style="display:none"` matches the project convention of inline styles in templates (used in `baseof.html:178` for material-symbols variation). Keep `tabindex="-1"` so keyboard users skip it; `aria-hidden="true"` keeps screen readers off it.

---

### 4. Decorative hero alt-text pattern (A11Y-01, D-discretion)

**Analog (canonical decorative hero):** `layouts/about/list.html:5-9`.

**Existing pattern** (`layouts/about/list.html:5-9`):
```html
<section class="relative h-[80vh] min-h-[600px] flex items-center overflow-hidden">
  <div class="absolute inset-0 z-0">
    <img alt="Cornish Coastline" class="w-full h-full object-cover" src="{{ "/images/about-hero-cliffs.jpg" | relURL }}" />
    <div class="absolute inset-0 bg-gradient-to-r from-primary/80 via-primary/40 to-transparent"></div>
  </div>
```

**Pattern to apply (decorative full-bleed background):**
```html
<img alt="" role="presentation" class="w-full h-full object-cover" src="{{ "/images/about-hero-cliffs.jpg" | relURL }}" />
```

**Per-file mapping:**

| File | Existing alt | Replacement |
|------|--------------|-------------|
| `layouts/index.html:11` | `alt="Dramatic Cornish coastline"` | `alt=""` + `role="presentation"` |
| `layouts/about/list.html:7` | `alt="Cornish Coastline"` | `alt=""` + `role="presentation"` |
| `layouts/policies/policies.html:6` | `alt="Cornish cliffs at dusk"` | `alt=""` + `role="presentation"` |
| `layouts/councillors/list.html:7` | `alt="Cornwall aerial coastline"` | `alt=""` + `role="presentation"` |
| `layouts/press/list.html:7` | `alt="Cornish Coastline"` | `alt=""` + `role="presentation"` |
| `layouts/get-involved/list.html:25-27` | `alt="Cornwall coastline"` (overlay on bento card) | Verify bento card is genuinely decorative; if overlay-only with text on top, set `alt=""` + `role="presentation"` |
| `layouts/press/list.html:175` (granite texture) | `alt="Granite Texture"` | `alt=""` + `role="presentation"` (overlay decorative) |

**Note on `index.html:11`:** the hero is full-bleed background with foreground text. It is decorative — the heading "Standing for Cornwall." carries the meaning. Setting `alt=""` is correct.

**`layouts/index.html:130`** (32×32 councillor avatar in quote section, `alt="Rowland O'Connor"`) — keep current alt; this is informative (identifies the quote attributor).

**`layouts/index.html:223`** (rotated card in CTA, `alt="Cornwall landscape"`) — decorative; replace with `alt=""` + `role="presentation"`.

**`layouts/index.html:95`** (in get-involved we already noted; in `layouts/get-involved/list.html:95` there's `alt="Community members in discussion"`) — this one is **informative** (illustrates what the section is about). Keep descriptive alt; do not blank out. Verify per-file before applying.

---

### 5. Article-image `imageAlt` pattern (A11Y-02, D-06)

**Analog:** `layouts/news/single.html:51-60` (current title-duplicating pattern).

**Existing pattern** (lines 51-60):
```go-html
{{/* Hero image */}}
{{ with .Params.image }}
<div class="max-w-4xl mx-auto px-6 lg:px-8 mb-12">
  <div class="aspect-[16/9] overflow-hidden rounded-xl">
    <img
      src="{{ . | relURL }}"
      alt="{{ $.Title }}"
      class="w-full h-full object-cover" />
  </div>
</div>
{{ end }}
```

**Pattern to apply (D-06: front-matter-driven, empty fallback = decorative, never the title):**
```go-html
{{ with .Params.image }}
<div class="max-w-4xl mx-auto px-6 lg:px-8 mb-12">
  <div class="aspect-[16/9] overflow-hidden rounded-xl">
    <img
      src="{{ . | relURL }}"
      alt="{{ with $.Params.imageAlt }}{{ . }}{{ end }}"
      class="w-full h-full object-cover" />
  </div>
</div>
{{ end }}
```

Rationale: when `imageAlt` is unset or empty, `{{ with }}` emits nothing → `alt=""` (decorative; screen readers skip). When set, descriptive text is rendered. CONTEXT D-06 prohibits silent fallback to `.Title`.

**Per-file/per-line mapping:**

| File:line | Existing | Replacement |
|-----------|----------|-------------|
| `layouts/news/single.html:56` | `alt="{{ $.Title }}"` | `alt="{{ with $.Params.imageAlt }}{{ . }}{{ end }}"` |
| `layouts/press/single.html:28` | `alt="{{ $.Title }}"` | `alt="{{ with $.Params.imageAlt }}{{ . }}{{ end }}"` |
| `layouts/news/list.html:24` (featured) | `alt="{{ $pageTitle }}"` | `alt="{{ with .Params.imageAlt }}{{ . }}{{ end }}"` (uses outer `.` from `range`) |
| `layouts/news/list.html:68` (grid) | `alt="{{ $pageTitle }}"` | `alt="{{ with .Params.imageAlt }}{{ . }}{{ end }}"` |
| `layouts/index.html:166` (homepage news teaser) | `alt="{{ $pageTitle }}"` | `alt="{{ with .Params.imageAlt }}{{ . }}{{ end }}"` |
| `layouts/_default/list.html:49` (CONCERNS reference) | `alt="{{ $.Title }}"` | If reachable, apply same swap. Verify in execution. |

**Note on Hugo scoping:** in `range` blocks the dot `.` is the page being iterated. The existing `$pageTitle := .Title` shim isn't needed for `imageAlt` because we just use `.Params.imageAlt` directly inside the loop.

---

### 6. `archetypes/default.md` — front-matter scaffold (D-06)

**Analog:** itself — current file uses TOML.

**Existing** (lines 1-5):
```toml
+++
date = '{{ .Date }}'
draft = true
title = '{{ replace .File.ContentBaseName "-" " " | title }}'
+++
```

**Caveat from CONVENTIONS.md:** archetype is TOML but corpus is YAML. Two viable approaches:

(a) **Add `imageAlt` to the existing TOML scaffold** (simplest, single file):
```toml
+++
date = '{{ .Date }}'
draft = true
title = '{{ replace .File.ContentBaseName "-" " " | title }}'
# imageAlt: describe what the hero image *shows* (e.g. "A child at a dental check-up").
# Leave empty string for decorative images. Never duplicate the title.
imageAlt = ''
+++
```

(b) **Switch the archetype to YAML** to match content corpus (preferred long-term but out of phase scope):
```yaml
---
date: '{{ .Date }}'
draft: true
title: '{{ replace .File.ContentBaseName "-" " " | title }}'
# imageAlt: describe what the hero image *shows* (e.g. "A child at a dental check-up").
# Leave empty for decorative images. Never duplicate the title.
imageAlt: ""
---
```

**Recommendation for plan:** stay with TOML for this phase (option a) — minimum scope, no corpus migration. Conversion to YAML is a separate concern.

---

### 7. Content backfill (D-07) — `imageAlt:` on 8 existing posts

**Analog:** existing front matter in `content/press/full-council-2026-04-21/childrens-nhs-dental-care.md:1-9`:
```yaml
---
title: "Access to NHS Dental Care for Children in Cornwall"
date: 2026-04-21T09:00:00+01:00
publishDate: 2026-04-20T09:00:00+01:00
category: "NHS Dentistry"
excerpt: "Cllr Rowland O'Connor warns…"
image: "/images/press/childrens-nhs-dental-care.jpg"
pdf: "/documents/press/2026-04-21/childrens-nhs-dental-care.pdf"
---
```

**Pattern to apply:** insert one new YAML key, conventionally adjacent to `image:`. Suggested alt text per CONTEXT D-07/specifics:

| File | Suggested `imageAlt` |
|------|---------------------|
| `content/news/community-engagement-events.md` | (executor: describe the actual photo content — e.g. "Residents at a CING community drop-in event") |
| `content/news/spring-council-session-update.md` | (executor: describe — e.g. "Cornwall Council chamber during a full council session") |
| `content/news/welcome-to-our-new-website.md` | image is `/images/st-pirans-flag.jpg` → "St Piran's flag flying against a Cornish sky" |
| `content/press/full-council-2026-04-21/childrens-nhs-dental-care.md` | "A child at a dental check-up" |
| `content/press/full-council-2026-04-21/glyphosate-weedkiller-halt.md` | "A worker spraying weedkiller at a roadside" |
| `content/press/full-council-2026-04-21/mevagissey-school-transport.md` | "A school bus on a narrow Cornish lane" (executor verifies against the actual hero image) |
| `content/press/full-council-2026-04-21/planning-public-trust.md` | "Construction site on the edge of a Cornish village" (executor verifies) |
| `content/press/full-council-2026-04-21/rural-deprivation-funding.md` | "A quiet lane in a rural Cornish hamlet" (executor verifies) |

Concrete alt text must be verified by executor against the actual hero JPGs in `static/images/press/`. CONTEXT specifies *describe what the image shows, not the headline*.

**Insertion location:** immediately after the `image:` line (groups image-related front matter together). Example for the dental-care release:
```yaml
image: "/images/press/childrens-nhs-dental-care.jpg"
imageAlt: "A child at a dental check-up"
pdf: "/documents/press/2026-04-21/childrens-nhs-dental-care.pdf"
```

---

### 8. `layouts/404.html` — branded error page (D-08, D-09)

**No exact analog exists** (CONCERNS confirms `layouts/_default/` lacks a 404). Composite from three existing patterns:

**Pattern 1 — Hugo template shell** (from `layouts/index.html:1, 236`):
```go-html
{{ define "main" }}

… page content …

{{ end }}
```
The `header.html` and `footer.html` partials are auto-included by `baseof.html:207` and `:213`. A 404 layout that simply uses `{{ define "main" }}` inherits all branded chrome for free.

**Pattern 2 — Editorial header / hero copy block** (from `layouts/get-involved/list.html:5-19` — editorial heading without full-bleed image, fits a 404 better than a coastline hero):
```html
<header class="max-w-screen-2xl mx-auto px-6 lg:px-8 mb-20">
  <div class="flex flex-col md:flex-row gap-12 items-end">
    <div class="max-w-3xl">
      <span class="font-label text-tertiary uppercase tracking-widest text-sm font-bold block mb-4">404 — Not Found</span>
      <h1 class="font-headline text-4xl md:text-6xl lg:text-8xl font-extrabold tracking-tight text-primary leading-[0.9]">
        This page has<br/>wandered off<br/><span class="text-tertiary">the map.</span>
      </h1>
    </div>
    <div class="pb-4">
      <p class="text-on-surface-variant max-w-md font-body leading-relaxed text-lg">
        The link may be old, or the page may have moved. Try one of these instead.
      </p>
    </div>
  </div>
</header>
```
Uses the `Local Voice. / Local Action.` two-part headline cadence (CONVENTIONS §"Headline rhythm") and the tertiary-gold accent on the second line.

**Pattern 3 — Three CTAs** (from `layouts/index.html:108-114` gold CTA card pattern, simplified):
```html
<section class="max-w-screen-2xl mx-auto px-6 lg:px-8 grid grid-cols-1 md:grid-cols-3 gap-6 mt-12">
  <a href="{{ "/" | relURL }}" class="bg-primary text-white p-8 rounded-xl flex flex-col justify-between min-h-[180px] hover:bg-primary-container transition-colors group">
    <span class="material-symbols-outlined text-tertiary-fixed text-4xl">home</span>
    <div>
      <h2 class="font-headline font-bold text-2xl mb-1">Home</h2>
      <p class="text-on-primary-container text-sm">Back to the front page.</p>
    </div>
  </a>
  <a href="{{ "/news/" | relURL }}" class="bg-surface-container-lowest editorial-shadow p-8 rounded-xl flex flex-col justify-between min-h-[180px] hover:bg-surface-container transition-colors">
    <span class="material-symbols-outlined text-primary text-4xl">newspaper</span>
    <div>
      <h2 class="font-headline font-bold text-2xl text-primary mb-1">Latest News</h2>
      <p class="text-on-surface-variant text-sm">What CING councillors are working on.</p>
    </div>
  </a>
  <a href="{{ "/councillors/" | relURL }}" class="bg-tertiary-container p-8 rounded-xl flex flex-col justify-between min-h-[180px] hover:bg-tertiary hover:text-white transition-colors">
    <span class="material-symbols-outlined text-on-tertiary-container text-4xl">groups</span>
    <div>
      <h2 class="font-headline font-bold text-2xl text-on-tertiary-container mb-1">Your Councillors</h2>
      <p class="text-on-tertiary-container text-sm">Meet the independent voices for Cornwall.</p>
    </div>
  </a>
</section>
```
Three cards: navy primary, surface-lowest, tertiary-container — same colour rhythm as the homepage principles bento. Uses `editorial-shadow` (CONVENTIONS) and Material Symbols icons (already loaded in `baseof.html:174`).

**Composite skeleton** (`layouts/404.html`):
```go-html
{{ define "main" }}

<div class="pt-32 pb-20">
  <header class="max-w-screen-2xl mx-auto px-6 lg:px-8 mb-12">
    <div class="flex flex-col md:flex-row gap-12 items-end">
      <div class="max-w-3xl">
        <span class="font-label text-tertiary uppercase tracking-widest text-sm font-bold block mb-4">404 — Not Found</span>
        <h1 class="font-headline text-4xl md:text-6xl lg:text-8xl font-extrabold tracking-tight text-primary leading-[0.9]">
          This page has<br/>wandered off<br/><span class="text-tertiary">the map.</span>
        </h1>
      </div>
      <div class="pb-4">
        <p class="text-on-surface-variant max-w-md font-body leading-relaxed text-lg">
          The link may be old, or the page may have moved. Try one of these instead.
        </p>
      </div>
    </div>
  </header>

  {{/* Three CTAs (D-08): home, news, councillors */}}
  <section class="max-w-screen-2xl mx-auto px-6 lg:px-8 grid grid-cols-1 md:grid-cols-3 gap-6">
    {{/* …three cards as above… */}}
  </section>
</div>

{{ end }}
```

**Tone-band reminder (D-09):** "branded confident with Cornish flavour", not generic "Sorry, page not found", not deadpan "404". Example wording is illustrative; executor may adjust within band.

**No `hugo.IsProduction` gate:** 404 is content, not analytics. CONTEXT §"Established Patterns" explicit on this.

**Hugo file convention:** `layouts/404.html` (not `layouts/_default/404.html`) — Hugo emits `public/404.html` automatically; GitHub Pages serves it on any 404. `pt-32` matches the fixed-nav offset pattern used by `layouts/get-involved/list.html:3` and `layouts/news/list.html:3`.

---

## Shared Patterns

### Form action URL (CONVENTIONS §Forms)
**Source:** `layouts/get-involved/list.html:108`, `:155`; `layouts/index.html:205`; `layouts/press/list.html:147`.
**Apply to:** all four forms after FORMS-03 endpoint split.
```html
<form action="https://formspree.io/f/{{ .Site.Params.<endpointParam> }}" method="POST">
```
Never hardcode the Formspree ID; always read from `.Site.Params`.

### Privacy-policy link in form footers
**Source:** `layouts/get-involved/list.html:140-142`, `layouts/index.html:216-218`.
```html
<a href="{{ "/privacy/" | relURL }}" class="underline">privacy policy</a>
```
Use `relURL` for internal links throughout. Pattern recurs in cookie banner (`baseof.html:224`) and footer.

### Decorative-image accessibility
**Source:** WCAG 1.1.1 / CONCERNS §"Alt text on hero images is decorative-as-content".
**Apply to:** all decorative full-bleed background images and overlay textures.
```html
<img alt="" role="presentation" src="…" class="…" />
```
The `role="presentation"` is belt-and-braces — modern AT honours empty `alt` alone, but the explicit role survives copy-paste mistakes.

### Hugo guarded-render with `{{ with }}`
**Source:** CONVENTIONS §"Conditional rendering"; `layouts/news/list.html:21-30`, `:65-74`.
```go-html
{{ with .Params.image }}
  <img src="{{ . | relURL }}" alt="{{ with $.Params.imageAlt }}{{ . }}{{ end }}" />
{{ end }}
```
**Apply to:** all article hero blocks. Inner `with $.Params.imageAlt` (note the `$` to escape the outer scope) emits nothing on empty/missing → `alt=""` decorative fallback (D-06).

### Tailwind colour rhythm for CTA cards
**Source:** `layouts/index.html:65-115` (principles bento).
**Apply to:** 404 page CTAs.
- Primary CTA: `bg-primary text-white` with `text-tertiary-fixed` icon
- Surface CTA: `bg-surface-container-lowest editorial-shadow` with `text-primary` icon and `text-on-surface-variant` body
- Gold/prestige CTA: `bg-tertiary-container text-on-tertiary-container` (use sparingly; CONVENTIONS §"Tertiary gold")

### Production-only gating (NOT applied this phase)
**Source:** `layouts/_default/baseof.html:8`, `:216`.
The 404 page must NOT be wrapped in `{{ if hugo.IsProduction }}` — content surfaces are universal; the gate is reserved for analytics/banner.

---

## No Analog Found

None — every change in Phase 2 reapplies a pattern that already exists in the codebase. The 404 layout is the only "new file" but it composes three existing patterns (template shell, editorial header, bento CTA cards) rather than inventing one.

---

## Metadata

**Analog search scope:**
- `.github/workflows/`
- `archetypes/`
- `content/news/`, `content/press/`
- `layouts/` (all 15 templates + partials)
- `hugo.toml`

**Files scanned:** 15 templates, 1 workflow, 1 config, 1 archetype, 8 content files, 5 codebase mapping docs.
**Pattern extraction date:** 2026-04-26.
