# Accessibility and interaction

## Preserve semantic and reading order

Build the DOM in the order users should read and operate it. CSS layout may change columns, but major regions must not rely on `order`, reverse flex directions, or duplicate markup to create a different visual sequence. Verify the accessibility tree and keyboard path after any structural rearrangement.

Use native elements first:

- links for navigation;
- buttons for actions and disclosures;
- headings for section structure;
- lists for related repeated items;
- form controls with programmatic labels;
- `details`/`summary` for simple disclosure when its behavior fits.

Do not add a redundant role to a native control. Add ARIA only to expose state or relationships that native semantics do not already provide.

## Make navigation discoverable

Desktop navigation must remain visible or have an explicit labeled trigger. Mobile navigation needs a real button with an accessible name, `aria-expanded`, and `aria-controls` where supported by the implementation. Move focus only when the interaction model requires it, restore focus after modal-style navigation closes, and support Escape for dismissible overlays.

Do not make hover the only way to reveal or operate essential content. Hover menus need equivalent focus behavior and a path that tolerates pointer movement. Avoid navigation that appears only after scrolling in a particular direction unless a persistent alternative remains available.

## Keep focus visible and unobscured

Never remove `outline` without a visible replacement on the same interactive state. Prefer `:focus-visible` for a tailored keyboard indicator while retaining a safe `:focus` fallback where needed.

Check that:

- focus follows a logical sequence;
- no component traps focus unintentionally;
- sticky headers, cookie notices, drawers, and floating controls do not fully obscure the focused target;
- focus is restored to the invoking control after a modal or disclosure closes;
- hidden content is removed from both interaction and accessibility exposure.

WCAG 2.2 includes Focus Not Obscured (Minimum): <https://www.w3.org/WAI/WCAG22/Understanding/focus-not-obscured-minimum.html>.

## Size pointer targets accurately

WCAG 2.2 Success Criterion 2.5.8 at Level AA defines a 24-by-24 CSS pixel minimum or sufficient spacing, with exceptions for inline text, equivalent controls, user-agent controls, and essential presentation. It does not require every inline link to become a 44px button: <https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html>.

Use approximately 44-by-44 CSS pixels as an ergonomic design target for primary touch controls, not as a false statement of the AA minimum. Measure the active target, not only the visible icon. Preserve readable line height for inline links rather than inflating every anchor.

## Respect zoom, text settings, and reflow

- Verify text resizing to 200% without loss of content or function: <https://www.w3.org/WAI/WCAG22/Understanding/resize-text.html>.
- Verify reflow around 320 CSS pixels for horizontal writing, except content that genuinely requires two-dimensional layout: <https://www.w3.org/WAI/WCAG22/Understanding/reflow.html>.
- Test 400% browser zoom on a 1280 CSS pixel-wide desktop viewport as a practical route to the 320 CSS pixel reflow condition.
- Test user text-spacing overrides, including increased line, paragraph, letter, and word spacing.
- Do not disable zoom or replace browser zoom with application-specific scaling.

## Treat motion as state, not decoration

Use motion only when it communicates hierarchy, continuity, or state. Under `prefers-reduced-motion: reduce`:

- remove non-essential entrance, parallax, and looping animation;
- make scrolling immediate when smooth motion is not essential;
- retain state changes instead of hiding them behind near-zero animation;
- ensure carousels and media do not begin advancing automatically.

Do not globally set every animation to an infinitesimal duration without testing; applications can rely on animation events, and a blanket rule can create rapid flashing or broken state. Target owned motion components.

## Preserve native scrolling

Content sites should not intercept global `wheel`, `touchmove`, arrow keys, Page Up/Down, or Space to simulate slides. Mandatory scroll snapping can make zoomed or partially visible content unreachable. Use proximity snapping only for a justified component and verify keyboard, touch, trackpad, zoom, and reduced-motion behavior.

When a modal intentionally prevents background scrolling, scope the lock to the modal lifecycle, preserve the previous scroll position, and restore it on every close path.

## Verify contrast and forced colors

- Check text and non-text contrast in every interactive state, not only the resting state.
- Do not encode status by color alone.
- In `forced-colors: active`, allow the user agent to map colors unless a specific graphic would lose meaning.
- Use system color keywords for custom focus and borders when forced colors requires an override.
- Test selected, disabled, error, and hover/focus states separately.

## Keep forms and disclosures robust

- Associate every control with a persistent label; placeholders are hints, not labels.
- Connect errors and help text programmatically and announce asynchronous errors appropriately.
- Do not clear user input on validation failure or responsive re-render.
- Keep disclosure state in one source of truth and synchronize visual, DOM, and ARIA state.
- Make icon-only controls discoverable through an accessible name and visible affordance.

## Review third-party widgets explicitly

Treat embedded chat, consent, maps, video, and analytics UI as part of the user experience. Verify keyboard access, focus obstruction, zoom overlap, target size, loading failure, and privacy boundaries. Do not claim full accessibility merely because the first-party DOM passes static checks.
