---
name: Meko or Lily
description: The cats' record book — a warm paper Pet Passport that stamps who is in frame.
colors:
  paper: "#f3ead9"
  paper-2: "#eadcc2"
  ink: "#1e2a24"
  ink-soft: "rgba(30,42,36,0.80)"
  ink-faint: "rgba(30,42,36,0.68)"
  green: "#2e6b4f"
  green-deep: "#1f4f3a"
  gold: "#5f5230"
  gold-soft: "#8a7a5c"
  red-ink: "#b04a2f"
  meko-box: "#38b04a"
  lily-box: "#ff9d2e"
  visitor-box: "#a9a89f"
typography:
  scale:
    micro: "0.66rem"
    small: "0.72rem"
    legend: "0.74rem"
    caption: "0.78rem"
    note: "0.8rem"
    foot: "0.85rem"
    plate: "0.86rem"
    sub: "0.92rem"
    body: "1rem"
    title: "1.05rem"
    denied-min: "1.15rem"
    denied-max: "1.75rem"
    stamp: "2.05rem"
  display:
    fontFamily: "Archivo, 'Segoe UI', Arial, sans-serif"
    fontSize: "2.35rem"
    fontWeight: 700
    lineHeight: 1.15
    letterSpacing: "0.02em"
  body:
    fontFamily: "'Source Serif 4', Georgia, 'Times New Roman', serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.55
  label:
    fontFamily: "Archivo, 'Segoe UI', Arial, sans-serif"
    fontSize: "0.72rem"
    fontWeight: 600
    letterSpacing: "0.22em"
    textTransform: "uppercase"
rounded:
  sm: "2px"
  thumb: "6px"
spacing:
  sm: "8px"
  md: "16px"
  lg: "24px"
components:
  stamp-name:
    backgroundColor: "transparent"
    textColor: "{colors.green-deep}"
    typography: "{typography.display}"
    padding: "0.55rem 1.05rem"
  stamp-denied:
    backgroundColor: "transparent"
    textColor: "{colors.red-ink}"
    typography: "{typography.display}"
    padding: "0.55rem 1.05rem"
  stamp-doubt:
    backgroundColor: "transparent"
    textColor: "{colors.ink}"
    typography: "{typography.display}"
    padding: "0.55rem 1.05rem"
  plate:
    backgroundColor: "transparent"
    textColor: "{colors.ink}"
  tab-selected:
    backgroundColor: "{colors.green}"
    textColor: "{colors.paper}"
    typography: "{typography.label}"
    padding: "0.55rem 0.5rem"
  tab-default:
    backgroundColor: "transparent"
    textColor: "{colors.ink-soft}"
    typography: "{typography.label}"
    padding: "0.55rem 0.5rem"
---

# Design System: Meko or Lily

## Overview

**Creative North Star: "The Cats' Record Book"**

Meko or Lily is a Pet Passport, not a classifier card. The whole surface is a cream ruled ledger that Meko and Lily live in: the left page carries the photo as a corner-pinned record, the right page carries the authoritative verdict, and a single inked stamp seats who is in frame. The system's job is to make a machine judgment feel like a trusted clerk stamping an official record — official, warm, a little dry, never clinical.

The density is low and unhurried. One large headline, one spread of two paper plates, one stamp. Warm paper (never white), blue-black ink (never pure black), an official registry green for acceptance, a single maroon-red ink reserved for refusals. Everything the stock Streamlit chrome would draw as a rounded widget is restitched as inked chrome: the source selector is a row of spine tabs, the photo frame is a mounted page with corner pins, the per-class numbers sit in a quiet ruled ledger beneath the stamp. Contrast is engineered, not hoped for — every text tier clears 4.5:1 on its ground.

**Key Characteristics:**
- Paper-first: one warm ground, panel-plates in a slightly deeper tone, no shadows or gradients as decoration.
- One stamp, one verdict — the stamp is the only large display moment, and it lands with a mechanical clack.
- Two-page spread metaphor: evidence left, verdict right, bound by a short gold stitch tie.
- Inked chrome: every stock widget restyled to the world's materials.
- Honesty as decoration: privacy and uncertainty are stated plainly, never hidden.

## Colors

A warm official palette: paper and ink rule, one registry green carries acceptance, maroon-red is rationed to refusals, and gold is the decorative finding ink for form labels and stitching.

### Primary
- **Registry Green** (#2e6b4f): acceptance. The selected source tab, the stamped name verdict, the live trace's seat. Dark sibling **Registry Green Deep** (#1f4f3a) is the stamp text/ring and focus outline.
- **Maroon Red** (#b04a2f): the refusal ink. Used only for "Not registered" stamps and the live pulse dot. Its rarity is the point — a red stamp means denied, nothing else.

### Secondary
- **Binding Gold** (#5f5230): form labels and plate labels (THE VERDICT), upper-case track-that-earns-a-label rather than a heading.
- **Finding Gold** (#8a7a5c): decorative only — corner pins, the spine seam, the flap chevron. Never text.

### Neutral
- **Felt Paper** (#f3ead9): the page ground and app background.
- **Stock Paper** (#eadcc2): the panel plates the columns sit on — depth through tone alone.
- **Record Ink** (#1e2a24): headings, stamps, primary type (blue-black, never pure black).
- **Ink Soft** (rgba(30,42,36,0.80)): secondary text (≥6.9:1 on paper).
- **Ink Faint** (rgba(30,42,36,0.68)): tertiary text — footer, blank-page placeholders (≥4.8:1 on paper).
- **Box Green** (#38b04a), **Box Orange** (#ff9d2e), **Box Grey** (#a9a89f): the live-draw annotation colors from `vision.py`, mirrored verbatim by the legend swatches — the on-page promise of what a boxed cat means.

### Named Rules
**The Rarity Rule.** Red ink appears only on refusals; gold-soft only as decoration; a color's meaning never crosses worlds.
**The Readable-Ink Rule.** Every text tier clears 4.5:1 on the ground it actually sits on; the faint tier was deliberately raised to stay legible.
**The Split-Gold Rule.** Gold text and gold decoration are separate tokens so a single color never fails both roles at once.

## Typography

**Display Font:** Archivo (with Segoe UI / Arial fallback)
**Body Font:** Source Serif 4 (with Georgia / Times New Roman fallback)

**Character:** An engineered sans for the registry's record-keeping, paired with a book serif for the owner's reading voice. The display face carries the stamps, the tabs, and the labels in tight uppercase tracking; the serif carries explanation, hints, and notes in italic where the book speaks.

### Hierarchy
- **Display** (700, 2.35rem, 1.15): the book title "Meko or Lily?" — the only large heading.
- **Title** (700, 1.05rem, 0.28em tracking): the nameplate — always MEKO · LILY, one line.
- **Body** (400, 1rem, 1.55): explanations, notes under the stamp, camera guidance. Keep near 40–45 chars via `max-width: 34ch` on ink-notes for the wrapped stamp notes.
- **Label** (600, 0.72rem, 0.22em, uppercase): plate labels (THE VERDICT), tab text, kicker-free small captions.

### Named Rules
**The One-Headline Rule.** There is exactly one display headline on the page; everything else is a stamp, a tab, or body text. A heading circle earns its own weight; labels are never stacked above headings.
**The Stamp-Word Rule.** Verdicts are stamped words, not sentences: "Meko", "Lily", "Not registered", or the split "Meko / Lily" seam. Explanation lives in the note under the stamp.

## Layout

A single centered column (Streamlit `layout="centered"`). Inside it: masthead (title + sub + a 2px binding rule), the source tab row as a spine, then a two-page spread via `st.columns([5, 6])` — left page is the photo mount + nameplate + legend, right page is the verdict plate. Between the plates, at the top of the spread, a short 2px gold binding tie is anchored to the left plate's edge and centered in the gap; below 720px the spread stacks column-first (photo page, then verdict) and the tie disappears. The live camera branch replaces the spread with the viewing window, a live trace line, legend, and footer.

Spacing rhythm is generous between plates and tight within them (0.55–1.05rem padding in stamps, ~1.05rem plate padding). More space above a block than below it.

## Elevation & Depth

No shadows, no gradients-as-decoration, no blur. Depth is conveyed entirely by tonal paper layering (paper ground vs. stock paper plates vs. the raised inset stamp ring) and by the 1px rule accents. A plate looks pressed in, not floating. The stamp's depth is a double-border ring with a soft inset inner ring — an inked die impression, not a drop shadow. Motion is a single authored moment: the verdict stamp clacks and seats (`cubic-bezier(.22,1,.36,1)`, ~0.32s), with a reduced-motion reset that freezes it in place.

### Named Rules
**The Flat-By-Default Rule.** No drop shadows, ever; depth is tone-on-tone paper only.
**The One-Moment Rule.** One stamp clack is the page's only entrance; nothing else animates in. (The live dot pulses — it is a status light, not an entrance.)

## Shapes

Sharp-cornered and ruled. Nearly all corners are square or 2px; nothing rounds past a nudge. The photo mount is a flat page with four thin corner pins (L-shaped gold ticks). The stamp is a double-border rectangle with optional rotation (models at rest, seats true; denials sit at a slight turn). The seam is a vertical dashed rule, not a box. No geometry is used as a mask or badge; a circle appears exactly once (the 9px live status dot).

## Components

### Source Tabs (radio)
- **Style:** Streamlit's radio restitched as a spine row; labels are equal-flex uppercase cells with a 2px bottom rule.
- **Selected:** Registry Green fill, paper text, deep-green bottom border. **Unselected:** transparent, ink-soft text, faint bottom rule.
- **Structure:** retargeted to Streamlit 1.64's real DOM (`[data-testid="stRadioGroup"]` / `[data-testid="stRadioOption"]`), the input visually suppressed.
- **State:** hover warms text to Registry Green Deep.

### Verdict Stamp
- **Shape:** 3px double border, 2px inset ring, uppercase display, 0.18em tracking. Long words never wrap (nowrap ink); the denied stamp tightens tracking and clamps size so "NOT REGISTERED" always seats.
- **States:** `stamp-name` (green-deep, seats level); `stamp-denied` (red-ink, −3.5° tilt); `stamp-doubt` (ink, 92% opacity, seats with a wobble); `stamp-seam` (two green-deep halves split by a 2px×2 vertical double-bar divider echoing the frame) for a near-tie that refuses to guess.
- **Entrance:** one clack animation (`keyframes stamp-clack`), disabled under reduced motion.

### Photo Mount
- **Shape:** flat paper page, 1px border, four L-shaped gold-soft corner pins, min-height 230px, centered image. Empty state reads "The page is blank. Add a photo or open the camera."

### Ledger
- **Style:** an always-visible ruled ledger under the verdict note, opened by a dashed top rule and a small gold "THE LEDGER" label. The verdict still leads — the ledger is quieter in size and ink.
- **Contents:** one per-class row — name, a 5px bar filled to the class probability (always green-filled, no click needed to reveal), and the percent in tabular numerals.

### Legend
- **Style:** three uppercase cells with 11px swatch squares: green Meko, orange Lily, grey "A visitor" — the same colors the live video draw boxes skinned in.

### Live Camera
- **Style:** viewing window with a lit vertical trace bar (red→gold→green gradient) while stamping; a 9px pulsing red dot + "Live — stamping now" while the feed plays. Camera-denied guidance names the problem and offers the two working alternatives.

### Focus & Selection
- Focus visible: 2px Registry Green Deep outline, 2px offset. Selection: deep-green fill with paper text. Caret, scrollbar thumb, and table numerals all themed from the palette.

## Do's and Don'ts

### Do:
- **Do** keep the page to one headline, one spread, one stamp — the record-book calm is the brand.
- **Do** reach for the binding tie and the corner pins before reaching for a shadow or a rounded card.
- **Do** keep the numbers smaller than the verdict in a quiet ruled ledger — a probability is a footnote, not the verdict.
- **Do** place any text tier on a ground where it clears 4.5:1 — when a tier can't, raise the ink rather than "fixing" it with size.

### Don't:
- **Don't** use red ink for anything that isn't a refusal.
- **Don't** place a label (kicker/eyebrow) above a heading; the heading carries its own weight.
- **Don't** restyle a widget halfway — every stock control (tabs, uploader, camera, details) is either restitched to the world or deliberately left, never half-mixed.
- **Don't** reintroduce ghost shadows, gradient text, or rounded-12px UI; the paper world is flat and ruled.
- **Don't** put dev-ops or training language on the page — the book speaks, not the notebook.