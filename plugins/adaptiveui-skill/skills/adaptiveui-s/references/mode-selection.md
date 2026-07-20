# Mode selection and example prompts

Use this guide when a user asks how `AdaptiveUI-S` and `AdaptiveUI-N` differ,
which one to choose, or what an invocation looks like. Answer the selection question
without inspecting a project, editing files, running tests, or starting an audit.
A mode-selection question alone does not activate either workflow; work begins only
when the user explicitly invokes S or N in the current message.

## Quick selection

| Choose | When the user needs | Completion behavior |
| --- | --- | --- |
| `AdaptiveUI-S` | A responsive UI audit, explanation, ordinary scoped implementation, or an explicitly requested final review after intermittent work. The request may describe product behavior without naming UI. | Derives only in-scope adaptive UI effects. Never adds a completion audit automatically. |
| `AdaptiveUI-N` | A product implementation, repair, or refactor whose derived adaptive UI changes must finish with a review of every task-owned UI-affecting change and its directly related styles. | Implements only in-scope adaptive UI effects, then completes its bounded post-change style audit. |

Choose S when the user wants analysis only, ordinary UI work, or control over whether a final review happens. Choose N when the user specifically wants the implementation to include a mandatory final style check.

The user does not need to repeat UI terminology after explicitly invoking a Skill. Each Skill derives the user-visible surfaces, flows, states, content constraints, and adaptive behavior implied by the product request. It treats a nominally non-UI fact as relevant only when the request or project shows a concrete user-visible consequence. Database, server, deployment, and other non-UI details do not shape the AdaptiveUI scope merely because they appear in the same prompt.

Explicit invocation starts the relevance gate; it does not make every UI request adaptive UI work. Standalone copywriting, typo-only edits, and cosmetic-only changes remain outside scope when they do not affect hierarchy, contrast, state, reflow, accessibility, browser compatibility, or rendered character encoding. This boundary partitions AdaptiveUI work without canceling or authorizing broader work. A clear broader request in the same message can be handled under other applicable instructions; a background fact or Skill invocation alone cannot authorize it.

If only N is invoked for an explicitly read-only request, N stops without project inspection or edits and asks for a current-message S invocation. If both Skills are explicitly invoked, S owns an explicitly read-only request and N owns an implementation request.

## Example prompts

Use S for a read-only review:

```text
Use $adaptiveui-s to audit the checkout page and its directly related styles for responsive, accessibility, and redundant-style issues. Do not edit files.
```

Use S for ordinary scoped implementation without an automatic completion audit:

```text
Use $adaptiveui-s to make the card grid wrap correctly at narrow widths while preserving the existing design tokens.
```

Use N for implementation plus its required scoped audit:

```text
Use $adaptiveui-n to simplify the dashboard breakpoint rules, remove stale style overrides, and complete the required post-change style audit.
```

Use N when the request names only product behavior:

```text
Use $adaptiveui-n to add workspace invitations with owner, editor, and viewer roles.
```

N derives the invitation entry, form, role controls, pending, success, and error UI without requiring the prompt to mention UI. Storage, email delivery, and deployment remain outside the AdaptiveUI scope unless they impose a concrete user-visible state or constraint.

## Invocation boundary

Select `@AdaptiveUI-S` or `@AdaptiveUI-N` in a supported picker, or write `$adaptiveui-s` or `$adaptiveui-n` in the current message. Earlier invocations, installation alone, and a matching task description do not activate either workflow. A valid current-message invocation activates the chosen relevance gate regardless of whether the remaining text contains UI terminology. If both are explicitly invoked, S owns an explicitly read-only request; otherwise N owns the implementation and required post-change audit.
