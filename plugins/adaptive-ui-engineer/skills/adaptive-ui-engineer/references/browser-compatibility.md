# Browser compatibility and progressive enhancement

## Default baseline

Use this baseline only when the project has no stronger documented support policy:

| Family | Target |
| --- | --- |
| Chrome | Current and previous two stable releases |
| Edge | Current and previous two stable releases |
| Firefox | Current and previous two stable releases |
| Safari on macOS | 16.4 and later |
| Safari on iOS/iPadOS | 16.4 and later |
| Chrome Android | Current and previous two major releases |
| Android System WebView | Modern maintained releases aligned with Chrome |

Do not promise IE11 or Safari below 16.4. Unsupported does not mean intentionally broken: keep semantic content, navigation, and core actions available whenever the platform can render the underlying HTML.

Project configuration wins. Inspect Browserslist, build targets, transpiler settings, framework documentation, analytics, and contractual requirements before applying this default.

## Layer behavior by criticality

Use three layers:

1. **Core:** semantic HTML, readable source order, forms, links, buttons, natural scrolling, and essential content.
2. **Resilient layout:** broadly supported flex/grid, intrinsic sizing, wrapping, media constraints, and basic media queries.
3. **Enhancement:** container queries, `:has()`, Subgrid, Popover, View Transitions, advanced color, or animation.

An unsupported enhancement may reduce polish, never erase core content or its only control path.

## Apply feature-specific fallbacks

| Feature | Safe approach |
| --- | --- |
| Dynamic viewport units | Declare `vh` first, then the chosen `dvh` or `svh`; use natural height when possible. |
| Safe-area environment variables | Include fallback values and use only with an intentional edge-to-edge layout. |
| Container queries | Keep a single-column or wrapping base; add container-query refinements inside `@supports` when necessary. |
| `:has()` | Keep semantics and operation independent of ancestor styling; add a class/state fallback if the style is essential. |
| Subgrid | Define a readable ordinary grid first; use Subgrid to align, not to expose content. |
| Popover | Preserve a button, explicit state, focus behavior, and a dialog/disclosure fallback where needed. |
| View Transitions | Treat as cosmetic; navigation and state must complete without it. |
| `scrollbar-gutter` | Use as layout stabilization only; never as a fix for actual horizontal overflow. |
| `color-mix()` and modern color | Put a conventional color first and the enhanced value second. |

Do not add prefixes by hand without evidence. Use the project's existing PostCSS/Autoprefixer or compiler policy. A manually prefixed one-off can hide that the unprefixed behavior is not supported or not tested.

## Keep JavaScript compatibility proportional

- Prefer platform APIs already covered by the baseline.
- Use feature detection, not user-agent sniffing.
- Load a polyfill only when an essential feature lacks an acceptable native fallback and the project accepts the cost.
- Avoid shipping a broad legacy bundle to support an undocumented browser.
- Check SSR and hydration before reading `window`, viewport size, or media queries.
- Use `matchMedia` for interaction state only when CSS alone cannot provide the needed behavior; keep the DOM usable before hydration.

## Test representative engines

Chromium-only testing is not cross-browser testing. At minimum, run material layout or interaction changes in one Chromium browser, Firefox, and Safari/WebKit when those environments are available. Use a real iOS Safari check for safe-area, virtual keyboard, browser chrome, or fixed-position behavior that materially affects the task.

Automated WebKit is useful but is not identical to Safari on Apple hardware. Label it accurately in evidence.

## Write compatibility claims professionally

Use these labels in README and audit reports:

- **Designed for:** the documented baseline and fallbacks implemented in code.
- **Automated test:** engine, version, operating system, viewport, and date when known.
- **Manual test:** real browser/device and scenario performed.
- **Not tested:** an environment in the baseline that was unavailable.
- **Unsupported:** an environment outside the declared policy.

Do not write “works on all devices,” “fully compatible,” or “WCAG compliant” from a static scan. Report observed evidence and remaining uncertainty.
