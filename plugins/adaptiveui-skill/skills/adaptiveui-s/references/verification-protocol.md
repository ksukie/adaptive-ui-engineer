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

## 3. Verify preview character encoding

Treat source bytes, HTML declarations, HTTP metadata, and the browser's effective decoding as separate evidence. A valid UTF-8 source file alone does not prove that a served preview is decoded as UTF-8.

- Preserve the project's documented encoding and generated-file conventions. Default new serialized HTML, CSS, and JavaScript source to UTF-8, but do not silently migrate an established non-UTF-8 file as part of an unrelated UI change.
- For a standalone serialized HTML document, keep the actual bytes UTF-8 and use one `<meta charset="utf-8">` declaration fully within the first 1024 bytes unless verified HTTP `Content-Type` metadata or a UTF-8 BOM supplies the encoding. Prefer the early `meta` declaration as a portable fallback for local-file preview. Do not add it inside `iframe[srcdoc]` or XML, and do not add obsolete `charset` attributes to `script` elements or a CSS `@charset` rule by default.
- Preview through the project's existing HTTP development server when production uses HTTP. A `file://` preview cannot verify response headers, routing, asset MIME types, or server/header conflicts.
- For an HTTP preview, inspect the main document response and expect `Content-Type: text/html; charset=utf-8` when the server supplies a character set. Treat a non-UTF-8 header or a conflict among the HTTP header, BOM, and `meta` declaration as a failure; transport metadata overrides an in-document declaration except when a BOM takes precedence.
- In the rendered page, record the effective decoding without mutating the document:

```js
({
  characterSet: document.characterSet,
  contentType: document.contentType,
  replacementCharacters:
    (document.body?.innerText.match(/\uFFFD/g) ?? []).length,
});
```

Require `characterSet` to normalize to `UTF-8`. Treat replacement characters as a review signal because U+FFFD can be intentional. Verify real project content that exercises non-ASCII text, such as Chinese, emoji, combining marks, or translated labels; do not inject or rewrite product content without authorization.

A missing in-document declaration is not by itself a runtime failure when a verified UTF-8 HTTP header or BOM exists. Report which layer supplied the encoding and distinguish a static AUI024 finding from an observed rendering failure.

## 4. Use a representative viewport matrix

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

## 5. Measure runtime geometry

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

## 6. Verify keyboard and focus

Use Tab and Shift+Tab from the browser chrome into the page. Exercise Enter, Space, arrow keys, and Escape according to each control's native pattern.

Confirm:

- every interactive control is reachable exactly as intended;
- focus order follows the visual and reading order;
- a visible focus indicator is not clipped;
- disclosures expose the correct state and content;
- menus, dialogs, and drawers close and restore focus correctly;
- no fixed layer fully obscures the focused element;
- hidden or duplicate carousel content is not reachable.

## 7. Verify zoom and user settings

- Test text resize or browser zoom at 200%.
- Test 400% zoom on a sufficiently wide desktop viewport to exercise approximately 320 CSS pixel reflow.
- Increase browser default font size when possible.
- Test reduced motion before reload and during interaction.
- Test forced colors or a high-contrast environment when available.
- Apply user text-spacing overrides for content-heavy interfaces.

Record exceptions for maps, diagrams, data tables, and other genuinely two-dimensional content. Their surrounding instructions and controls must still reflow.

## 8. Capture trustworthy visual evidence

- Wait for fonts, images, route transitions, skeletons, dialogs, and animations to settle.
- Capture viewport screenshots at the tested state and width.
- Prefer section or viewport captures for sticky/fixed/composited layers; full-page stitching can duplicate, omit, or misplace them.
- Include the relevant interaction state, not only the landing state.
- Reject screenshots that are blank, stale, dimmed by an overlay, clipped, or captured before content is ready.
- Pair screenshots with DOM measurements for overflow and obstruction claims.

## 9. Grade evidence

Use these labels:

- **Verified:** directly observed in the named browser/environment with repeatable steps.
- **Static pass:** source or automated static check supports the claim, but no rendered browser result exists.
- **Inferred:** a reasoned expectation that still needs runtime confirmation.
- **Not run:** environment or data unavailable.
- **Failed:** the expected behavior did not hold.

Do not promote an inference to “verified.” Report the browser engine and whether it was a real browser, automation engine, emulator, or physical device.

## 10. Complete the change

Compare before and after behavior. Re-run the static auditor and project checks. Confirm that only authorized files changed. Summarize passes, failures, suppressions, unsupported browsers, and untested baseline environments.
