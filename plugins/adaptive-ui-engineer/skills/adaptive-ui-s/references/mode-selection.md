# Mode selection and example prompts

Use this guide when a user asks how `Adaptive-UI-S` and `Adaptive-UI-N` differ,
which one to choose, or what an invocation looks like. Answer the selection question
without inspecting a project, editing files, running tests, or starting an audit.
A mode-selection question alone does not activate either workflow; work begins only
when the user explicitly invokes S or N in the current message.

## Quick selection

| Choose | When the user needs | Completion behavior |
| --- | --- | --- |
| `Adaptive-UI-S` | A responsive UI audit, explanation, scoped refactor, or an explicitly requested final review after intermittent work. | Never adds a completion audit automatically. |
| `Adaptive-UI-N` | A UI implementation, repair, or refactor that must finish with a review of this task's changed UI files and directly related styles. | Completes its bounded post-change style audit before reporting completion. |

Choose S when the user wants analysis only, ordinary UI work, or control over whether a final review happens. Choose N when the user specifically wants the implementation to include a mandatory final style check.

## Example prompts

Use S for a read-only review:

```text
Use $adaptive-ui-s to audit the checkout page and its directly related styles for responsive, accessibility, and redundant-style issues. Do not edit files.
```

Use S for ordinary scoped implementation without an automatic completion audit:

```text
Use $adaptive-ui-s to make the card grid wrap correctly at narrow widths while preserving the existing design tokens.
```

Use N for implementation plus its required scoped audit:

```text
Use $adaptive-ui-n to simplify the dashboard breakpoint rules, remove stale style overrides, and complete the required post-change style audit.
```

## Invocation boundary

Select `@Adaptive-UI-S` or `@Adaptive-UI-N` in a supported picker, or write `$adaptive-ui-s` or `$adaptive-ui-n` in the current message. Earlier invocations, installation alone, and a matching task description do not activate either workflow. If both are explicitly invoked in the same current message, N owns the request because it includes the required post-change audit.
