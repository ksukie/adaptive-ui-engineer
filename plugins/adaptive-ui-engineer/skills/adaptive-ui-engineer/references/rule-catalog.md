# Static audit rule catalog

The auditor performs deterministic triage with the Python standard library. It is not a browser engine, CSS parser, accessibility conformance tool, or replacement for human review.

## Priorities

- **P0:** blocks a core task or a fundamental accessibility capability.
- **P1:** major responsive, semantic, focus, navigation, or resource failure.
- **P2:** material compatibility, interaction, visual-system, or maintainability risk.
- **P3:** low-impact robustness or maintenance issue.

## Confidence

- **High:** the source pattern directly establishes the reported condition.
- **Medium:** the pattern is risky but may have a justified local context or compensating behavior.
- **Low:** the pattern is a weak lead that requires substantial manual confirmation.

## Rules

| Rule | Default | Confidence | Meaning and review boundary |
| --- | --- | --- | --- |
| AUI001 | P1 | High | HTML document lacks viewport metadata. Add a normal mobile viewport without disabling zoom. |
| AUI002 | P0 | High | Viewport metadata disables or materially restricts zoom. Remove the restriction unless a separately governed native wrapper requires it. |
| AUI003 | P1 | High/Medium | Root CSS or body utility hides horizontal overflow. Confirm whether it conceals a defect, focus ring, or drawer. |
| AUI004 | P2 | Medium | `100vw` or `w-screen` is used for ordinary width. Confirm intentional full-bleed behavior before changing it. |
| AUI005 | P2 | Medium | Fixed viewport height lacks a modern mobile viewport fallback. Natural content height may be the better repair. |
| AUI006 | P1 | High/Medium | CSS or utilities alter visual order. Verify DOM, keyboard, and accessibility-tree order. |
| AUI007 | P1 | High/Medium | Mandatory scroll snapping is present. Verify zoom, keyboard, touch, and partially visible content. |
| AUI008 | P2 | Medium | A stylesheet declares motion without a reduced-motion branch in that file. A shared global policy may satisfy it. |
| AUI009 | P2 | High/Medium | `transition: all` or `transition-all` animates unrelated properties. Replace with an explicit property list. |
| AUI010 | P1 | Medium | Source removes an outline. Confirm an equivalent visible focus indicator exists on the same state. |
| AUI011 | P2 | High | A stylesheet has at least three `!important` declarations. Resolve cascade ownership before adding more. |
| AUI012 | P2 | Medium | More than six distinct viewport breakpoints occur in one stylesheet. Consolidate only after mapping structural needs. |
| AUI013 | P2 | Medium | At least six literal, non-token radius values occur in one stylesheet. Map them to semantic roles. |
| AUI014 | P1 | Medium | A wheel/touchmove listener appears with `preventDefault`. Confirm scope, escape behavior, and passive-listener intent. |
| AUI015 | P2 | Medium | JavaScript reads viewport width and writes layout styles. Move continuous sizing to CSS where possible. |
| AUI016 | P2 | High | DOM content is cloned. Check duplicate IDs, repeated announcements, focus, and carousel complexity. |
| AUI017 | P2 | Medium | Carousel-like code advances on an interval. Require pause, focus/hover pause, and motion controls. |
| AUI018 | P2 | High | HTML lacks a non-empty document language. Set the correct BCP 47 language tag. |
| AUI019 | P1 | High | Duplicate HTML IDs can break fragments, labels, and ARIA relationships. Make IDs unique and update references. |
| AUI020 | P1 | High | An image omits the `alt` attribute. Use descriptive text or an intentionally empty alt for decoration. |
| AUI021 | P1 | High | An iframe lacks a title. Identify the embedded content concisely. |
| AUI022 | P1 | High | A statically resolvable local media/script/stylesheet path does not exist. Dynamic aliases and template expressions are skipped. |
| AUI023 | P3 | High | A source file is not valid UTF-8. Convert carefully and inspect visible text. |

## Suppressions

Suppress a finding only through `.adaptive-ui-engineer.json` with the narrowest path pattern and a concrete reason:

```json
{
  "ignore": [
    {
      "rule": "AUI004",
      "paths": ["src/styles/full-bleed.css"],
      "reason": "The gallery background intentionally spans the visual viewport."
    }
  ],
  "fail_on": "P1"
}
```

Suppressions remove matching findings from output and increment `summary.suppressed`. Review suppressions when layout ownership, browser support, or product intent changes.

## Non-goals

The auditor does not compute layout, color contrast, accessible names, focus order, hit areas, CSS cascade, framework render trees, hydration, media-query results, or browser support. Use the runtime verification protocol for those claims.
