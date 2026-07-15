# Verification protocol

## 1. Establish the evidence boundary

Record the target route, local start command, browser engines available, authentication state, seed data, and files allowed to change. Reuse existing test and browser infrastructure. Do not install Playwright, browser binaries, extensions, or services without authorization.

If a page cannot be run, perform static verification and label runtime checks “not run.”

## 2. Run static triage

Resolve `skill-root` as the directory containing `SKILL.md`, then invoke the bundled auditor by its resolved path. Replace `<skill-root>` with that quoted path:

```text
python "<skill-root>/scripts/audit_ui.py" <target> --format text --fail-on none
```

For CI or machine processing:

```text
python "<skill-root>/scripts/audit_ui.py" <target> --format json --fail-on P1
```

Review medium-confidence results in context. Record a suppression only with a rule, narrow path pattern, and concrete reason. Do not suppress a rule merely to make CI green.

Document-level semantic checks apply to `.html` and `.htm`. Framework component files receive source triage for CSS, scripts, and known utility patterns; rendered semantic behavior still needs runtime verification.

Also run project-native type checks, lint, unit tests, accessibility tests, and production builds relevant to the authorized scope.

## 3. Use a representative viewport matrix

Use these starting viewport sizes unless the product documents a different matrix:

| Width | Suggested height | Purpose |
| ---: | ---: | --- |
| 320 | 568 | WCAG-oriented narrow reflow and long-label pressure |
| 390 | 844 | Common modern phone portrait behavior |
| 768 | 1024 | Tablet/intermediate structure |
| 1024 | 768 | Compact desktop or landscape transition |
| 1440 | 900 | Wide layout, measure, hierarchy, and density |

These are CSS viewport sizes, not device claims. Add a breakpoint-adjacent check just below and above every structural breakpoint touched by the change.

At each width verify:

- no page-level horizontal scrolling except a documented two-dimensional region;
- navigation and primary actions remain discoverable;
- text, controls, media, and cards do not overlap or clip;
- reading measure and hierarchy remain intentional;
- fixed and sticky layers do not hide content or focused controls;
- long labels, long URLs, translated strings, empty states, and error states remain usable.

## 4. Measure runtime geometry

When browser evaluation is available, begin with:

```js
const root = document.documentElement;
({
  clientWidth: root.clientWidth,
  scrollWidth: root.scrollWidth,
  overflow: Math.max(0, root.scrollWidth - root.clientWidth),
});
```

Locate likely overflow sources without changing the page:

```js
const vw = document.documentElement.clientWidth;
[...document.querySelectorAll('body *')]
  .map((element) => ({ element, rect: element.getBoundingClientRect() }))
  .filter(({ rect }) => rect.right > vw + 1 || rect.left < -1)
  .map(({ element, rect }) => ({
    tag: element.tagName,
    id: element.id,
    className: String(element.className).slice(0, 120),
    left: rect.left,
    right: rect.right,
    width: rect.width,
  }));
```

Treat transformed decoration, visually hidden content, open drawers, and intentional full-bleed media as review cases rather than automatic defects.

## 5. Verify keyboard and focus

Use Tab and Shift+Tab from the browser chrome into the page. Exercise Enter, Space, arrow keys, and Escape according to each control's native pattern.

Confirm:

- every interactive control is reachable exactly as intended;
- focus order follows the visual and reading order;
- a visible focus indicator is not clipped;
- disclosures expose the correct state and content;
- menus, dialogs, and drawers close and restore focus correctly;
- no fixed layer fully obscures the focused element;
- hidden or duplicate carousel content is not reachable.

## 6. Verify zoom and user settings

- Test text resize or browser zoom at 200%.
- Test 400% zoom on a sufficiently wide desktop viewport to exercise approximately 320 CSS pixel reflow.
- Increase browser default font size when possible.
- Test reduced motion before reload and during interaction.
- Test forced colors or a high-contrast environment when available.
- Apply user text-spacing overrides for content-heavy interfaces.

Record exceptions for maps, diagrams, data tables, and other genuinely two-dimensional content. Their surrounding instructions and controls must still reflow.

## 7. Capture trustworthy visual evidence

- Wait for fonts, images, route transitions, skeletons, dialogs, and animations to settle.
- Capture viewport screenshots at the tested state and width.
- Prefer section or viewport captures for sticky/fixed/composited layers; full-page stitching can duplicate, omit, or misplace them.
- Include the relevant interaction state, not only the landing state.
- Reject screenshots that are blank, stale, dimmed by an overlay, clipped, or captured before content is ready.
- Pair screenshots with DOM measurements for overflow and obstruction claims.

## 8. Grade evidence

Use these labels:

- **Verified:** directly observed in the named browser/environment with repeatable steps.
- **Static pass:** source or automated static check supports the claim, but no rendered browser result exists.
- **Inferred:** a reasoned expectation that still needs runtime confirmation.
- **Not run:** environment or data unavailable.
- **Failed:** the expected behavior did not hold.

Do not promote an inference to “verified.” Report the browser engine and whether it was a real browser, automation engine, emulator, or physical device.

## 9. Complete the change

Compare before and after behavior. Re-run the static auditor and project checks. Confirm that only authorized files changed. Summarize passes, failures, suppressions, unsupported browsers, and untested baseline environments.
