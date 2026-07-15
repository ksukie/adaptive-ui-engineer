# Adaptive UI Audit

## Outcome

State the current usability outcome and the most important decision in two or three sentences.

## Scope

- Target:
- Operation: audit-only / implementation / verification
- Preserved behavior:
- Excluded files or surfaces:
- Compatibility baseline:
- Distribution: private / shareable with evidence / shareable with evidence redacted

## Finding field semantics

- `confidence`: `high` / `medium` / `low`; certainty of the rule's source assessment.
- `evidence_level`: `source_observed` / `static_inferred` / `runtime_observed`; origin of the evidence.
- `validation_state`: `not_applicable` / `not_run` / `reproduced` / `not_reproduced` / `manual_review_needed`; outcome of additional validation.

Do not use `not_run` when the source fact is sufficient and no extra validation is needed. Do not use `runtime_observed`, `reproduced`, or `not_reproduced` without an actual rendered-interface check.

## Findings and decisions

| Priority | Confidence | Evidence level | Validation state | Evidence | User impact | Decision |
| --- | --- | --- | --- | --- | --- | --- |
| P1 | high | `source_observed` | `not_applicable` | `path:line` and excerpt | Describe the affected task or user | Describe the minimal change |

## Verification

| Check | Environment | Result | Evidence |
| --- | --- | --- | --- |
| Static audit | Tool/version | Pass / Fail | Rule IDs or report path |
| Reflow | Viewport/zoom | Pass / Fail / Not run | Measurement or screenshot |
| Keyboard | Browser | Pass / Fail / Not run | Focus path and controls |
| Motion/contrast | Browser setting | Pass / Fail / Not run | Observed behavior |

## Residual risk

List suppressions, intentionally unsupported environments, unverified behavior, and follow-up work. Do not describe an untested environment as passing.

Before distributing this report, confirm that its paths, filenames, screenshots, and evidence excerpts are authorized for the intended recipients. Prefer auditor output created with `--redact-evidence` when source disclosure is unnecessary.
