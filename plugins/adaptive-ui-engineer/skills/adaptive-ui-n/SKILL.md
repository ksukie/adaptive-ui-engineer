---
name: adaptive-ui-n
description: Enhanced, explicitly invoked responsive UI implementation workflow with a mandatory scoped post-change style audit. Use only when the current user message explicitly invokes Adaptive-UI-N. Never activate implicitly or carry an invocation into later messages. Do not use for a read-only audit or a task that does not require UI changes.
---

# Adaptive-UI-N

Implement the requested responsive UI change, then complete a bounded review of the changes made for that task and their directly related styles before reporting completion.

## Activation and scope boundary

- Activate only when the current user message explicitly invokes this Skill: `@Adaptive-UI-N` in a supported picker or `$adaptive-ui-n` in a text-based client.
- Do not activate from a matching task description, an installed state, an earlier message, or an earlier invocation in the same conversation. If the current message names neither Adaptive-UI-S nor Adaptive-UI-N, use neither Skill.
- If both Skills are explicitly invoked in the same current message, use Adaptive-UI-N only.
- Use this Skill only for a request that authorizes UI implementation, repair, or refactoring. For a read-only review, use Adaptive-UI-S.
- Stay within the user's named files, component, page, or product scope. Preserve behavior, semantic DOM order, URLs, analytics hooks, and the existing framework or styling system unless the request changes them.

## Shared companion resources

Adaptive-UI-N is a companion to `adaptive-ui-s`; both directories must be installed as siblings. Resolve `<n-skill-root>` as the directory containing this file, then resolve `<s-skill-root>` as its parent directory plus `adaptive-ui-s`. Reuse the bundled auditor at `<s-skill-root>/scripts/audit_ui.py` and only the relevant material under `<s-skill-root>/references/` and `<s-skill-root>/assets/`. Before editing, confirm that the sibling auditor exists. If it is missing, explain that the complete S-and-N bundle is required; do not claim an N completion, and ask the user to reinstall the bundle or explicitly choose S. Do not install a dependency solely for this workflow.

## Repository-publication boundary

- Keep repository-writing and GitHub-publication actions opt-in. Do not stage, commit, push, tag, open or update a pull request, or create a GitHub release unless the current user request explicitly asks for that specific action.
- A request to commit authorizes only the requested commit; do not infer a push, tag, pull request, release, history rewrite, or another remote action. Preserve any existing staged state unless the request explicitly changes it.
- Do not proactively mention this default in the completion report. Mention repository-publication state only when the user asks or when it is needed to explain a real blocker.

## Required workflow

### 1. Establish a task baseline before editing

1. Record the requested scope, allowed and forbidden files, preserved behavior, target users, and verification limits.
2. Inspect the affected component, its entry point, styles, imports, existing tests, package metadata, and local instructions.
3. When Git is available, inspect `git status --short` and the relevant diff before editing. Record pre-existing modified or untracked paths as a baseline and never claim their existing hunks as task-owned. If this task must edit a baseline-modified path, keep that file in scope: identify the task-owned hunk separately, audit it and its direct style surface, and label untouched baseline hunks as excluded. Never reset, stash, discard, or silently absorb those changes.
4. Identify the narrow target for static auditing and the directly related style surface: imported CSS, CSS Modules, scoped styles, CSS-in-JS, utilities, tokens used by the changed component, and necessary layout wrappers.

### 2. Implement the smallest coherent change

- Prefer semantic HTML, CSS, native controls, existing tokens, and progressive enhancement before JavaScript or new dependencies.
- Repair overflow at its source. Do not use global clipping, device-specific pixel rules, hidden duplicate content, or unrelated framework migration as a shortcut.
- Keep reading order, keyboard order, focus visibility, reduced-motion behavior, and supported-browser fallbacks intact.
- Remove stale overrides, dead branches, duplicate listeners, or generated sizing only when they are part of the task's changed scope.

### 3. Complete the mandatory post-change style audit

This review is required before claiming the task is complete, even if the implementation itself appears small.

1. Determine the task-owned changes made after the baseline, including a task-owned hunk inside a pre-existing modified file. Do not claim ownership of pre-existing edits merely because they are present in the working tree.
2. Inspect every changed UI file and its directly related style surface. Review reflow, intrinsic sizing, overflow, viewport units, content priority, typography, visual hierarchy, radius and spacing consistency when relevant, focus and keyboard behavior, motion, and compatibility-sensitive enhancements.
3. Do not turn this into a whole-repository audit. Do not fix or report historical, unrelated findings except to name a concrete blocking interaction with the requested change.
4. Run the bundled static auditor against the narrow affected target when Python 3.9+ is available:

```text
python "<s-skill-root>/scripts/audit_ui.py" <target> --format text --fail-on none
```

Treat its output as triage, not proof of runtime behavior. Read the relevant companion references before acting on medium-confidence findings. If Python is unavailable, perform the applicable checks manually and say so.

### 4. Verify proportionally

- Run relevant existing tests and builds for the changed scope.
- When the page and browser tooling are already available, verify representative narrow, middle, and wide containers; keyboard operation; visible focus; long content; reduced motion; and zoom or reflow appropriate to the change.
- Do not install Playwright, a browser, or another dependency without authorization. Do not claim unperformed browser or assistive-technology verification.

### 5. Required completion report

Lead with the result and include all of the following:

1. task scope and files changed;
2. baseline exclusions, including any untouched pre-existing hunks in an in-scope file;
3. post-change style-audit scope, findings, and fixes, or an explicit statement that no directly related style file applied;
4. static, test, build, and browser verification with pass/fail/not-run status;
5. residual risks, unverified environments, and intentionally untouched unrelated findings.

## Quality invariants

- Keep readable content free of horizontal page scrolling at supported reflow widths.
- Preserve user zoom, font settings, logical keyboard order, and visible focus.
- Keep primary actions usable without hover and touch targets appropriate to the product goal.
- Keep interaction complexity proportional to the user goal and distinguish static evidence from runtime evidence.
- Keep the post-change audit bounded to this task; the required gate is thorough within scope, not a mandate to scan the repository.
