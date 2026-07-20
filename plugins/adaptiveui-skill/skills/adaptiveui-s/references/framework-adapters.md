# Framework adapters

## Apply the framework-agnostic core first

Regardless of framework:

1. Preserve semantic DOM and source order.
2. Keep layout in CSS unless interaction state genuinely controls structure.
3. Reuse the project's component, token, and styling conventions.
4. Avoid introducing a second state or styling system for a localized fix.
5. Run the project's existing type checks, tests, lint, and production build after an authorized change.

Inspect the package manifest and actual source before selecting an adapter. Do not infer Next from React, Nuxt from Vue, or Tailwind from utility-looking classes alone.

## Vanilla HTML, CSS, and JavaScript

- Keep progressive enhancement: content and primary navigation should work before JavaScript.
- Use one initialization path and guard against binding the same listener twice.
- Prefer event delegation for repeated cards or navigation items.
- Store disclosure state on the controlling element and synchronize `hidden`, `aria-expanded`, and focus.
- Avoid measuring every element on resize. Use ResizeObserver only for behavior that depends on component geometry and cannot be expressed by CSS.
- Keep scripts deferred or modules unless early execution is required.

## React and Next.js

- Keep responsive styling in CSS, CSS Modules, the established utility system, or existing component primitives.
- Do not branch the rendered DOM from `window.innerWidth`; it causes server/client mismatch, resize churn, and duplicate semantics.
- If JavaScript needs a media-query state, expose one shared hook built on `matchMedia`, include cleanup, and render a usable SSR default.
- Keep keys stable and never use clone-based duplicate slides with duplicate IDs.
- Preserve component boundaries that own state; remove derived state that can be computed during render.
- In Next.js, use the existing image component correctly, but do not use `fill` without a positioned, sized parent. Verify generated image sizes rather than assuming framework optimization prevents overflow.
- Verify route transitions, focus management, streaming/loading states, and hydration at the narrow viewport.

## Vue and Nuxt

- Keep layout in scoped CSS or the established global token layer; avoid deep selectors for ordinary ownership.
- Use computed values instead of watchers for derived presentation state.
- Clean up manual listeners, observers, and timers in the matching lifecycle.
- Do not render different server/client structures from viewport width. Use CSS reflow or a hydration-safe media-query composable for behavior that cannot be CSS-only.
- Treat Teleport overlays as focus and stacking-context boundaries; verify scroll locking and restoration.
- In Nuxt, verify client-only content has a meaningful placeholder and does not shift or hide core navigation.

## Svelte and SvelteKit

- Let scoped component CSS own layout and use global selectors only for deliberate shared foundations.
- Keep reactive statements free of repeated DOM measurement where CSS or ResizeObserver is sufficient.
- Return cleanup functions for listeners and observers.
- Avoid browser globals during server rendering; use lifecycle boundaries only for true client behavior.
- Verify transitions under reduced motion and ensure an outro does not delay semantic state or focus restoration.
- Preserve a usable SSR tree for navigation and essential content.

## Tailwind CSS

- Read the installed Tailwind version and configuration before changing utility syntax.
- Use the project's named tokens and variants before arbitrary values.
- Do not accumulate near-duplicate breakpoint variants to tune individual devices.
- Treat `w-screen`, `h-screen`, `overflow-x-hidden`, `order-*`, `transition-all`, `outline-none`, `snap-mandatory`, and large arbitrary radii as review triggers, not automatic defects.
- Keep class extraction static enough for the installed compiler; do not construct arbitrary utility strings at runtime.
- Extract a component or token when repeated utility bundles encode the same semantic role.
- Preserve inline prose links instead of applying a shared button utility to every anchor.

## CSS Modules, scoped CSS, and preprocessors

- Find the owning component before moving a rule to a global stylesheet.
- Prefer tokens and mixins already present; do not add a second breakpoint map or radius scale.
- Keep selector specificity shallow. Resolve stale cascade ownership instead of adding `!important`.
- Check compiled output assumptions when using nesting, custom media, or preprocessor functions.
- Avoid leaking locally named state classes into unrelated components.

## CSS-in-JS

- Determine whether styles are extracted at build time or generated at runtime.
- Do not read viewport width during render to create pixel values.
- Use theme tokens and supported media/container-query helpers.
- Keep transient styling props out of the rendered DOM.
- Verify SSR style order, hydration, and first paint before refactoring provider or cache boundaries.
- Do not migrate CSS-in-JS to another system as part of a responsive fix unless the user explicitly requests the migration.

## Framework change boundary

A responsive request does not authorize dependency upgrades, routing changes, state-library migration, component-library replacement, or build-system rewrites. Report a framework limitation when it genuinely blocks the target behavior, then request the expanded scope separately.
