<p align="center">
  <img src="plugins/adaptiveui-skill/assets/logo.svg" width="144" height="144" alt="AdaptiveUI-SKILL logo">
</p>

# AdaptiveUI-SKILL

**Two portable, explicit-only Agent Skills for auditing, implementing, and verifying resilient responsive web interfaces.**

[简体中文](README.md) · [Agent Skills specification](https://agentskills.io/specification) · [Apache-2.0](LICENSE) · [Disclaimer](DISCLAIMER.md)

AdaptiveUI-SKILL turns responsive UI work into an evidence-based workflow. It covers layout reflow, overflow, viewport units, semantic radius systems, keyboard and touch interaction, accessibility settings, cross-browser fallbacks, and unnecessary JavaScript complexity. It does not generate a separate design for every screen resolution and does not hide defects behind global clipping.

<p align="center">
  <img src="docs/images/adaptiveui-skill-workflow.png" width="100%" alt="Adaptive UI SKILL audits interface issues, repairs root causes, and verifies responsive layouts across mobile, tablet, and desktop widths.">
</p>

<p align="center"><sub>Audit the evidence, repair the root cause, and verify resilient reflow.</sub></p>

The repository contains two framework-agnostic companion Agent Skills and a thin Codex plugin wrapper. The Skills remain the single source of workflow truth: `AdaptiveUI-S` is the standard workflow, while `AdaptiveUI-N` adds a required, scoped post-change style audit.

## Why this exists

Common “responsive baselines” often mix good primitives with damaging global patches:

- `overflow-x: hidden` conceals the overflowing element and can clip focus or drawers.
- assigning 44px dimensions and padding to every link breaks inline prose;
- `pre, code { white-space: pre-wrap }` changes code semantics;
- `iframe { height: auto }` does not establish a useful embedded aspect ratio;
- more device breakpoints do not compensate for missing intrinsic layout;
- a static scan cannot prove browser behavior or WCAG conformance.

This Skill replaces those shortcuts with root-cause diagnosis, constrained implementation, and explicit verification evidence.

## Capabilities

- `AdaptiveUI-S`: standard audit-only, implementation, and verification work, plus a user-requested final audit after intermittent work.
- `AdaptiveUI-N`: UI implementation followed by a mandatory audit of this task's changed files and directly related styles.
- Explicit-only activation: an installed Skill, a matching request, or a previous invocation never enables either Skill for a later message.
- Adaptive UI-relevance gating: after an explicit invocation, each Skill derives in-scope adaptive UI effects even when the request names only product behavior; cosmetic-only, copy-only, and unrelated non-UI details cannot shape or expand that scope.
- Responsive layout review for containers, grid, flex, intrinsic sizing, overflow, zoom, media, tables, and viewport behavior.
- Optional visual-hierarchy guidance when component radius consistency is in scope; existing design tokens win.
- Keyboard, focus, navigation, target-size, motion, forced-color, and text-spacing checks.
- JavaScript simplification: remove viewport-driven sizing, scroll interception, duplicate rendering, autoplay, stale listeners, and unnecessary state.
- Adapters for Vanilla HTML/CSS/JS, React/Next, Vue/Nuxt, SvelteKit, Tailwind, scoped CSS, CSS Modules, preprocessors, and CSS-in-JS.
- A zero-dependency Python auditor with stable rule IDs, confidence labels, suppressions, JSON output, and CI thresholds.
- A standard-library, fail-open update scheduler with absolute next-check times and detailed post-task reminders; no automatic updates.
- Optional browser evidence when the host already provides browser control; no mandatory Playwright installation.
- Browser-preview encoding verification that separates source UTF-8 validity, the HTML declaration, HTTP `Content-Type`, and the browser's effective `document.characterSet`.

## Package layout

```text
.agents/plugins/marketplace.json
plugins/adaptiveui-skill/
├── .codex-plugin/plugin.json
├── assets/
├── hooks/hooks.json
└── skills/
    ├── adaptiveui-s/
    │   ├── SKILL.md
    │   ├── agents/openai.yaml
    │   ├── release.json
    │   ├── scripts/
    │   │   ├── audit_ui.py
    │   │   └── check_update.py
    │   ├── references/
    │   └── assets/
    └── adaptiveui-n/
        ├── SKILL.md
        └── agents/openai.yaml
tests/
```

Human-facing project documentation stays at the repository root. `AdaptiveUI-N` deliberately reuses the auditor, update scheduler, release metadata, and references from its sibling `adaptiveui-s` directory, so the two directories are one installable bundle.

## Installation

### Any Agent Skills-compatible client

Install or copy both directories using the client's supported Skill mechanism, preserving them as siblings:

```text
plugins/adaptiveui-skill/skills/adaptiveui-s
plugins/adaptiveui-skill/skills/adaptiveui-n
```

For clients that scan `$HOME/.agents/skills`, copy both directories there. Do not install `adaptiveui-n` by itself.

PowerShell:

```powershell
Copy-Item -Recurse -Force `
  .\plugins\adaptiveui-skill\skills\adaptiveui-s `
  "$HOME\.agents\skills\adaptiveui-s"
Copy-Item -Recurse -Force `
  .\plugins\adaptiveui-skill\skills\adaptiveui-n `
  "$HOME\.agents\skills\adaptiveui-n"
```

macOS/Linux:

```sh
cp -R plugins/adaptiveui-skill/skills/adaptiveui-s \
  "$HOME/.agents/skills/adaptiveui-s"
cp -R plugins/adaptiveui-skill/skills/adaptiveui-n \
  "$HOME/.agents/skills/adaptiveui-n"
```

Client discovery and invocation details vary. A client may discover a Skill from `SKILL.md`; in a manual installation, keep the `adaptiveui-s` and `adaptiveui-n` directories together so N can find the bundled auditor, references, and assets in S. When that sibling auditor is absent, N must not claim enhanced completion. `agents/openai.yaml` is an optional Codex presentation extension.

### Codex plugin after the repository is published

```text
codex plugin marketplace add ksukie/AdaptiveUI-SKILL
codex plugin add adaptiveui-skill@adaptiveui-skill
```

For local plugin development, add the absolute repository directory as a non-default marketplace, then install the same plugin name. Start a new task after installation so the updated Skill is discovered.

The plugin adds no MCP server, connector, or service credential. It bundles a `UserPromptSubmit` hook only to run the rate-limited update scheduler for an explicit S or N invocation. Codex requires users to review and trust plugin hooks before they run; marketplace installation may also follow the host's normal authentication policy.

## Update

Choose the matching update path. A ZIP download or manually copied Skill does not update itself.

| Previous installation | Update |
| --- | --- |
| Git clone | From the repository directory, run `git pull --ff-only origin main`. Preserve or commit local changes first if Git reports that the worktree is not clean. |
| ZIP download or manual copy | Download or copy the current version, then replace both sibling directories: `plugins/adaptiveui-skill/skills/adaptiveui-s` and `plugins/adaptiveui-skill/skills/adaptiveui-n`. Do not replace only `SKILL.md`. |
| Codex plugin marketplace | Refresh the marketplace, remove the cached plugin, reinstall it, then start a new Codex task. |

For a Codex plugin installed from this marketplace:

```text
codex plugin marketplace upgrade adaptiveui-skill
codex plugin remove adaptiveui-skill@adaptiveui-skill
codex plugin add adaptiveui-skill@adaptiveui-skill
```

If the marketplace has not been configured yet, run `codex plugin marketplace add ksukie/AdaptiveUI-SKILL` before installing the plugin.

### Optional update notices

Each explicit S or N invocation can run a non-blocking update scheduler. The first repository check is eligible 72 hours after the installed release time. After a successful check with no newer version, the next check is scheduled 72 hours later. When a newer stable release is found, the task completes first and then reports the installed and latest versions, release dates, subsequent stable-release count, latest bilingual summary, prior/current/next check times, and update guide. The first follow-up is scheduled after 36 hours; each later successful confirmation while the local version remains behind shortens the prior interval by 20% to a 12-hour floor.

`next_check_at` is an earliest eligible time, not a background timer. If the Skill is not used at that time, the check occurs on the first later explicit invocation and the next schedule is based on that actual check time. A failed request does not count as “no update,” does not shorten the reminder interval, and retries silently after 12 hours.

The Codex plugin stores scheduler state in its writable plugin-data directory. A manually copied Skill uses the user's platform state directory when it is writable. The checker sends only a bounded HTTPS GET to the fixed raw release-metadata URL; it does not send prompts, source code, project paths, credentials, or a stable user identifier. It never updates files automatically and never blocks the requested UI task. Set `ADAPTIVE_UI_UPDATE_CHECK=0` or explicitly ask to skip the check to disable it.

### v2.0.0 migration

v2.0.0 moves the project, plugin, both Skills, and their invocation identifiers to the `AdaptiveUI-SKILL` naming scheme. This is a breaking rename: an old installation does not automatically become the new plugin, and manually copied old Skill directories must not remain beside the new directories.

| Item | v1.1.0 and earlier | v2.0.0 |
| --- | --- | --- |
| Repository | `ksukie/adaptive-ui-engineer` | `ksukie/AdaptiveUI-SKILL` |
| Codex plugin | `adaptive-ui-engineer@adaptive-ui-engineer` | `adaptiveui-skill@adaptiveui-skill` |
| Standard Skill | `Adaptive-UI-S` / `$adaptive-ui-s` | `AdaptiveUI-S` / `$adaptiveui-s` |
| Enhanced Skill | `Adaptive-UI-N` / `$adaptive-ui-n` | `AdaptiveUI-N` / `$adaptiveui-n` |
| Configuration file | `.adaptive-ui-engineer.json` | `.adaptiveui-skill.json` |

Codex users should remove the old plugin, add the new marketplace address, and install the new plugin. Manual installations should remove the old `adaptive-ui-s` and `adaptive-ui-n` directories before copying `adaptiveui-s` and `adaptiveui-n`. Earlier migration history remains available in [CHANGELOG.md](CHANGELOG.md).

## Explicit invocation and modes

In Codex, select one of the bundled Skill labels: `@AdaptiveUI-S` or `@AdaptiveUI-N`. In text-based clients, invoke `$adaptiveui-s` or `$adaptiveui-n` in the current message. Some hosts may also show the `AdaptiveUI-SKILL` plugin parent; it is a container, not a third workflow, so select S or N when the workflow distinction matters.

| Skill | Use it for | Completion behavior |
| --- | --- | --- |
| `AdaptiveUI-S` | Standard responsive UI audits, ordinary implementation, refactoring, and a final audit explicitly requested after intermittent work. The request may name only product behavior. | Derives only in-scope adaptive UI effects and never adds a final audit automatically. |
| `AdaptiveUI-N` | Product implementation, repair, or refactoring whose derived adaptive UI changes must include a final review. | Implements only in-scope adaptive UI effects, then audits every task-owned UI-affecting change and its directly related styles. |

Both Skills declare explicit-only invocation. In Codex, `allow_implicit_invocation: false` prevents prompt-based implicit invocation; their instructions also reject carrying a past invocation into a later message. A valid current-message invocation starts the relevance gate even when the remaining prompt does not mention UI. Roles, states, content length, target users, and supported platforms can constrain adaptive UI when they have a concrete user-visible effect. Standalone copywriting, typo-only work, cosmetic-only changes without an adaptive consequence, and unrelated database, server, deployment, or infrastructure choices stay outside scope. This partition neither cancels nor authorizes broader work: a clear broader request in the same message can be handled under other applicable instructions, while a background fact or Skill invocation alone cannot authorize it. After each installation or update, verify the per-message contract in a fresh chat: invoke S or N once, then send a matching UI request without `@` or `$` and confirm no implicit Skill is used. If both Skills are explicitly named, S owns an explicitly read-only request; otherwise N owns the implementation request.

For the canonical S/N comparison and example prompts, consult the bundled
[mode-selection guide](plugins/adaptiveui-skill/skills/adaptiveui-s/references/mode-selection.md).
A question about the modes alone does not activate either workflow or authorize project work.

Examples:

```text
Use $adaptiveui-s to audit this page for responsive and accessibility issues. Do not edit files.
```

```text
Use $adaptiveui-s to review the completed checkout task's changed files and directly related styles. Do not edit files.
```

```text
Use $adaptiveui-n to normalize the card radius hierarchy and remove viewport-driven layout JavaScript, then complete the required post-change style audit.
```

```text
Use $adaptiveui-n to add workspace invitations with owner, editor, and viewer roles.
```

The last prompt never mentions UI. N still derives and implements the relevant invitation entry, form, role controls, feedback states, and responsive behavior. Storage and delivery details remain outside the AdaptiveUI scope unless they create a concrete user-visible constraint.

An N-only request that explicitly forbids edits stops without project inspection and asks for a current-message S invocation. N never silently activates S.

## Static auditor

The auditor is read-only unless `--output` is explicitly supplied.

On Windows, use `py -3` in place of `python` when the `python` command is not registered.

```text
python plugins/adaptiveui-skill/skills/adaptiveui-s/scripts/audit_ui.py <target>
  [--format text|json]
  [--config <file>]
  [--fail-on P0|P1|P2|P3|none]
  [--absolute-paths]
  [--redact-evidence]
  [--output <file>]
```

Examples:

```text
python plugins/adaptiveui-skill/skills/adaptiveui-s/scripts/audit_ui.py ./src --format text --fail-on none
python plugins/adaptiveui-skill/skills/adaptiveui-s/scripts/audit_ui.py ./src --format json --fail-on P1
python plugins/adaptiveui-skill/skills/adaptiveui-s/scripts/audit_ui.py ./src --format json --redact-evidence --output audit.json
```

Exit codes:

| Code | Meaning |
| ---: | --- |
| 0 | Scan completed and the selected threshold was not breached |
| 1 | Scan completed and a finding met the selected threshold |
| 2 | Invalid input, configuration, or output operation |

JSON output uses `schema_version: 3`. Each finding includes `rule_id`, `priority`, `confidence`, `evidence_level`, `validation_state`, `category`, `path`, `line`, `message`, `evidence`, and `recommendation`. `confidence` describes rule certainty, `evidence_level` identifies the evidence origin, and `validation_state` records whether additional validation applies and its outcome. The normative contract is [audit-report.schema.json](plugins/adaptiveui-skill/skills/adaptiveui-s/assets/audit-report.schema.json). Report metadata uses paths relative to the audit root by default; `--absolute-paths` is an explicit opt-in. Evidence can contain short source excerpts, so use `--redact-evidence` before sharing a report when source disclosure is not authorized.

AUI023 reports source that is not valid UTF-8. AUI024 separately reviews serialized HTML encoding declarations: a missing declaration requires HTTP-header confirmation, while non-UTF-8, duplicate, or declarations ending after the first 1024 bytes are reported directly. Runtime preview verification still checks the main-document `Content-Type` and `document.characterSet`; static source evidence cannot prove browser decoding.

Document-level semantic checks apply to `.html` and `.htm`. Framework component files receive source triage for CSS, scripts, and known utility patterns; rendered semantic behavior still needs runtime verification.

### Configuration

Place `.adaptiveui-skill.json` at the audited root or pass `--config`:

```json
{
  "exclude": ["public/vendor/**", "legacy/generated/**"],
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

The bundled schema is at `plugins/adaptiveui-skill/skills/adaptiveui-s/assets/audit-config.schema.json`. Suppressions require a narrow path and a reason; they are counted in output.

## Design principles

- Target CSS constraints and content pressure, not physical device resolutions.
- Keep semantic DOM, reading order, visual order, and focus order aligned.
- Prefer intrinsic CSS and native behavior over JavaScript layout calculations.
- Repair the source of horizontal overflow rather than clipping the page.
- Use breakpoints only for genuine structural changes.
- Treat modern CSS as progressive enhancement when core content depends on it.
- Separate the WCAG 2.2 AA 24 CSS pixel target requirement and exceptions from the ergonomic 44px touch recommendation.
- Report tested evidence, static evidence, inference, and untested environments separately.

## Compatibility policy

### Designed baseline

| Environment | Policy |
| --- | --- |
| Chrome, Edge, Firefox | Current and previous two stable releases |
| Safari and iOS Safari | 16.4 and later |
| Chrome Android and Android WebView | Modern maintained releases |
| IE11 and Safari below 16.4 | Unsupported; core semantic degradation is still preferred |
| Python auditor and optional update scheduler | Python 3.9+ on Windows, macOS, and Linux |

### Evidence status for 2.0.0

- Locally validated on Windows with Python 3.9, 3.10, and 3.11.
- Unit tests and package checks cover the explicit-invocation relevance gate, deterministic S/N routing, AUI024 HTML declaration checks, browser-preview encoding guidance, cross-platform path behavior, and update scheduling. The repository CI workflow is configured for Windows, macOS, Linux, and Python 3.9–3.13.
- The package does not claim that a generated or audited website passes untested browsers, assistive technologies, or WCAG conformance.

## Development and validation

```text
python -m unittest discover -s tests -v
```

Open Agent Skills validation uses a fixed source commit, verifies the downloaded archive by SHA-256, and hash-locks every CI-only Python dependency. GitHub Actions are pinned to immutable commits. Codex authors should additionally run the current Skill Creator and Plugin Creator validators before release.

See [CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md), [DISCLAIMER.md](DISCLAIMER.md), [RELEASE_CHECKLIST.md](RELEASE_CHECKLIST.md), and [CHANGELOG.md](CHANGELOG.md).

## Security and open-source posture

- The runtime auditor uses only the Python standard library. It does not execute scanned code, access the network, or install packages.
- The separate standard-library update scheduler accesses only the fixed release-metadata endpoint when a stored check is due, bounds and validates the response, treats summaries as display-only data, writes only scheduler state, and fails open without changing user projects.
- Symbolic links and Windows reparse points inside the audit tree are skipped; a linked target or configuration is rejected. Local resource checks cannot escape the audit root.
- Reports are read-only by default. Explicit file output is written atomically and refuses a linked destination or linked parent path.
- Runtime users have no third-party Python dependencies. CI-only actions use immutable commit pins; the Agent Skills validator source archive and dependency graph are cryptographically locked.
- The repository includes an Apache-2.0 license, contribution terms, a private vulnerability-reporting path, automated security analysis, and a first-release checklist.

These controls are defense in depth, not a claim of formal penetration testing, legal review, WCAG certification, or security certification. Read the complete [security policy](SECURITY.md) before processing confidential source code.

## License

Apache License 2.0. See [LICENSE](LICENSE).

## Disclaimer

Read the complete [English disclaimer](DISCLAIMER.md) or [Simplified Chinese translation](DISCLAIMER.zh-CN.md). AdaptiveUI-SKILL is an independent community project. It is not affiliated with or endorsed by OpenAI, W3C, browser vendors, or the framework vendors named in this documentation. Product names and trademarks belong to their respective owners.
