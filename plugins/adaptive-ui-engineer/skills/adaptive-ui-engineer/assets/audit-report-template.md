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

## Findings and decisions

| Priority | Evidence | User impact | Root cause | Decision | Verification |
| --- | --- | --- | --- | --- | --- |
| P1 | `path:line` | Describe the affected task or user | Describe the underlying constraint | Describe the minimal change | Pass / Fail / Not run |

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
