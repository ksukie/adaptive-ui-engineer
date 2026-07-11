# Responsive layout and visual hierarchy

## Start from constraints, not device labels

A CSS pixel is an abstract, density-independent unit. Physical resolution, monitor size, device-pixel ratio, operating-system scaling, browser zoom, browser chrome, and embedding context all affect the available CSS viewport. Do not create separate designs for 1080p, 1440p, or 4K displays.

Define behavior for three constraint states instead:

- **Narrow:** content must remain readable and operable without page-level horizontal scrolling.
- **Intermediate:** navigation, cards, or metadata may need wrapping or structural reflow.
- **Wide:** cap reading measure and organize related content without stretching prose.

Add a viewport breakpoint only where a real component cannot preserve its intended hierarchy. Prefer a container query when the component can appear in differently sized parents, but keep a non-container-query fallback for the supported baseline.

## Build from intrinsic layout

Use these patterns before adding breakpoints:

```css
.shell {
  inline-size: min(100% - 2 * var(--gutter), 72rem);
  margin-inline: auto;
}

.reading {
  max-inline-size: 70ch;
}

.cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(100%, 18rem), 1fr));
  gap: clamp(1rem, 0.75rem + 1vw, 2rem);
}

.layout > * {
  min-inline-size: 0;
}
```

Apply `minmax(0, 1fr)` when a flexible grid track contains long words, code, media, or intrinsic controls. Apply `min-inline-size: 0` to flex and grid children that must shrink. Use logical properties so the same constraints work in left-to-right, right-to-left, and vertical writing modes.

Do not use `width: 100vw` for ordinary containers. A viewport unit is appropriate for deliberate full-bleed or viewport-relative artwork, not as a substitute for `100%` of a containing block.

## Diagnose overflow at its source

Do not begin with `html, body { overflow-x: hidden; }`. Global clipping can hide focus rings, off-canvas controls, positioned content, and the element that caused the defect.

Inspect in this order:

1. Compare `document.documentElement.scrollWidth` with `clientWidth`.
2. Find elements whose bounding rectangle extends beyond the viewport.
3. Check fixed widths, minimum widths, transforms, negative margins, positioned children, long unbroken text, and intrinsic media.
4. Check grid `1fr` tracks and flex children that lack a zero minimum.
5. Check `100vw`, full-bleed calculations, and scrollbar assumptions.
6. Fix or intentionally contain the specific component.

Use a local scrolling region for data that is intrinsically two-dimensional, such as a wide comparison table. Give that region an accessible label when its purpose is not obvious. Do not turn the entire page into a horizontal scroller.

## Use viewport height deliberately

Content pages normally need natural document height. Use viewport height only for an intentional application shell, modal, stage, or minimum-height footer layout.

```css
.stage {
  min-block-size: 100vh;
  min-block-size: 100dvh;
}
```

Choose `svh` when content must fit inside the smallest visible mobile viewport without browser-chrome obstruction. Choose `dvh` when the component should track dynamic browser chrome. Keep `vh` first as the fallback. Avoid fixed `height` when `min-height` permits content growth.

Use safe-area insets only when the page deliberately extends into those areas, commonly with `viewport-fit=cover`. Provide a fallback value and combine it with the design gutter rather than replacing the gutter.

## Preserve zoom and typography

- Keep the viewport meta to `width=device-width, initial-scale=1` unless the application has a documented native-wrapper requirement.
- Do not set `user-scalable=no` or a restrictive `maximum-scale`.
- Use `rem` for user-scalable typography and spacing that follows text.
- Bound fluid typography with `clamp()` and test it at 200% and 400% zoom.
- Do not make essential text fit by reducing its size at a breakpoint.
- Test user-supplied text spacing, large browser default fonts, CJK punctuation, mixed scripts, long URLs, and translated labels.

Use `overflow-wrap: anywhere` on content that may contain unbreakable strings. Avoid applying `word-break: break-all` to all prose because it harms readability. Keep code blocks in `white-space: pre` with their own overflow region; do not globally convert code to wrapped prose.

## Size media and embedded content by type

- Images and video: constrain inline size and keep automatic block size unless deliberate cropping is part of the design.
- SVG: provide a `viewBox`; do not assume `height: auto` can infer an aspect ratio without intrinsic dimensions.
- Iframes: define an intentional size or aspect ratio and include a title. Do not apply `height: auto` as a generic media reset.
- Canvas: resizing CSS dimensions does not resize its drawing buffer; update both only when the visualization requires it.
- Tables: preserve header relationships. Prefer a labeled scrolling wrapper before converting rows into cards; a card conversion can destroy table semantics.

## Use a semantic radius scale

Map existing design tokens first. If no radius system exists, use this starting hierarchy:

| Role | Baseline | Purpose |
| --- | ---: | --- |
| Control | 10px | Inputs, compact toggles, small fields |
| Button | 12px | Primary and secondary controls |
| Card | 18px | Repeated peer content |
| Panel | 24px | Large grouped regions |
| Showcase | 32px | Hero media or a dominant feature frame |
| Pill | 999px | Chips and status labels with variable width |
| Circle | 50% | Avatars and truly square icon controls |

The scale expresses hierarchy, not decoration. Use one radius per semantic role, allow nested surfaces to step down, and avoid breakpoint-specific radius changes unless the component changes role or shape. Ensure thick borders and small rounded controls still contain the required target area; a 24px circular diameter does not contain a 24-by-24 CSS pixel square.

## Review common baseline mistakes

- Reset `box-sizing` globally, but reset margins and typography intentionally rather than erasing every element default without a replacement rhythm.
- Do not apply button dimensions and padding to every `a`; inline text links are explicitly different interaction geometry.
- Do not hide every `nav` or `footer` in print; hide only controls and repeated regions that do not carry print-relevant content.
- Do not force images to preserve color in forced-colors mode without a concrete failure; meaningful bitmap content already needs separate contrast review.
- Do not declare that every personal site needs zero breakpoints. A simple article may need none; a portfolio grid, language switcher, or navigation system may require structural reflow.
