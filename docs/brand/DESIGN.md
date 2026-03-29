# Design System Document: Editorial Grounding

> **Source**: Stitch design system "Kernow Horizon" — project ID `3771371856444129928`
> This is the canonical design authority for the CING website, exported from Google Stitch.

## 1. Overview & Creative North Star

### The Creative North Star: "The Modern Monolith"
This design system moves away from the "flyer-style" aesthetics of traditional political branding. Instead, it adopts the persona of **The Modern Monolith**: a digital experience that feels as permanent as Cornish granite and as fluid as the Atlantic. We reject the cluttered, boxy layouts of 2010s web design in favor of an **Editorial-High-End** approach.

We achieve this through:
* **Intentional Asymmetry:** Using the spacing scale (e.g., `24` vs `8`) to create rhythmic tension that feels human, not robotic.
* **Atmospheric Depth:** Utilizing the landscape-inspired palette to create a sense of place through layering rather than lines.
* **Stark Typography:** Leveraging massive `display-lg` scales against intimate `body-md` text to create an authoritative, trustworthy hierarchy.

---

## 2. Colors

The palette is a direct translation of the Cornish environment. We prioritize deep, sophisticated tones over "internet-primary" colors.

### The Palette
* **Primary (`#00263b`) & Primary Container (`#003d5b`):** The Deep Sea. These are our anchors. Use these for high-authority moments and headers.
* **Secondary (`#595f64`):** The Granite. Used for secondary actions and subtle text elements.
* **Tertiary (`#705d00`):** The St Piran's Gold. A "prestige" accent. Use sparingly for critical CTAs or high-level highlights.
* **Surface Tiers:** From `surface-container-lowest` (#ffffff) to `surface-dim` (#d6dadf), these represent the varying light on a coastal day.

### The "No-Line" Rule
**Strict Mandate:** Designers are prohibited from using 1px solid borders to define sections. We define space through "Tonal Shifts."
* *Example:* A `surface-container-low` (#f0f4f9) section should sit directly against a `surface` (#f6faff) background. The subtle change in hex value is enough to signify a boundary without "trapping" the content in a box.

### Signature Textures & Glass
To evoke the mist and spray of the coast, use **Glassmorphism** for floating navigation or overlay cards. Use `surface-container-lowest` at 80% opacity with a `backdrop-blur` of 12px. This ensures the "Deep Sea" or "Granite" backgrounds bleed through, creating a cohesive, integrated feel.

---

## 3. Typography

The system uses a pairing of **Manrope** (Display/Headline) and **Public Sans** (Body/Label) to balance forward-thinking modernism with clear, accessible communication.

* **Display (`display-lg` to `display-sm`):** Set in Manrope. These are your "Editorial Statements." Use tight letter-spacing (-0.02em) to make them feel authoritative and solid.
* **Headlines & Titles:** Manrope. These should feel like news headings—urgent but stable.
* **Body (`body-lg` to `body-sm`):** Set in Public Sans. We prioritize readability for a diverse regional demographic. Use `body-lg` (1rem) for all standard prose to ensure accessibility.
* **Labels:** Public Sans. Used for metadata and overlines. Always set in `label-md` or `label-sm` to maintain a clear contrast between content and "signposts."

---

## 4. Elevation & Depth

We convey trust through stability. Avoid high-contrast drop shadows which feel "cheap" or "app-like."

* **The Layering Principle:** Depth is achieved by stacking. A `surface-container-highest` card placed on a `surface` background provides all the "lift" required.
* **Ambient Shadows:** If a floating element (like a mobile FAB or a modal) is necessary, use an ambient shadow: `blur: 40px`, `y: 8px`, `color: on-surface` at **4% opacity**. It should feel like a natural light source, not a glow.
* **The "Ghost Border" Fallback:** If a border is required for accessibility in input fields, use `outline-variant` (#c1c7ce) at **20% opacity**. This creates a "suggestion" of a container rather than a hard cage.

---

## 5. Components

### Buttons
* **Primary:** Background: `primary`. Text: `on-primary`. Shape: `md` (0.375rem). No border.
* **Secondary:** Background: `secondary-container`. Text: `on-secondary-container`.
* **Tertiary (The "Gold" Action):** Background: `tertiary-container`. Text: `on-tertiary-container`. Use this exclusively for "Join" or "Donate" actions.

### Cards & Lists
* **Forbid Dividers:** Never use a horizontal line to separate list items. Use spacing `4` (1rem) or a subtle background shift to `surface-container-low`.
* **Editorial Cards:** Use `surface-container-lowest` with a `lg` (0.5rem) corner radius. Elements inside should be flush to the edges or use generous `6` (1.5rem) internal padding.

### Input Fields
* **The Grounded Input:** Use `surface-container-high` as the background for input fields. Instead of a 4-sided border, use a 2px bottom-border of `primary` when focused. This feels "forward-looking" and bespoke.

### Signature Component: The "Community Anchor"
A large, full-bleed container using a gradient from `primary` (#00263b) to `primary-container` (#003d5b). This component is used for regional manifestos, featuring `display-md` typography to create a high-impact, trustworthy message.

---

## 6. Do's and Don'ts

### Do:
* **Embrace Negative Space:** Use spacing `16` and `20` to separate major content blocks. Let the "Granite" breathe.
* **Use Intentional Asymmetry:** Align text to the left but allow imagery to bleed off the right edge of the grid.
* **Prioritize Accessibility:** Ensure all text on `primary` or `tertiary` containers uses the designated `on-` color tokens to maintain AA/AAA contrast.

### Don't:
* **Don't use "Pure" Black:** Always use `on-background` (#171c20) for text to maintain the "Deep Sea/Granite" tonal profile.
* **Don't use Rounded-Full for everything:** Use `full` (pill-shape) only for Chips/Tags. Buttons and Cards must remain `md` or `lg` to feel grounded and "architectural."
* **Don't crowd the interface:** If a layout feels busy, remove a background color and increase the spacing scale rather than adding a divider.
