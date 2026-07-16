<p align="center">
  <img src="plugins/adaptive-ui-engineer/assets/logo.svg" width="144" height="144" alt="Adaptive UI Engineer logo">
</p>

# Adaptive UI Engineer

**Two portable, explicit-only Agent Skills for auditing, implementing, and verifying resilient responsive web interfaces.**

[简体中文](README.zh-CN.md) · [Agent Skills specification](https://agentskills.io/specification) · [Apache-2.0](LICENSE) · [Disclaimer](DISCLAIMER.md)

Adaptive UI Engineer turns responsive UI work into an evidence-based workflow. It covers layout reflow, overflow, viewport units, semantic radius systems, keyboard and touch interaction, accessibility settings, cross-browser fallbacks, and unnecessary JavaScript complexity. It does not generate a separate design for every screen resolution and does not hide defects behind global clipping.

<p align="center">
  <img src="docs/images/adaptive-ui-engineer-workflow.png" width="100%" alt="Adaptive UI Engineer audits interface issues, repairs root causes, and verifies responsive layouts across mobile, tablet, and desktop widths.">
</p>

<p align="center"><sub>Audit the evidence, repair the root cause, and verify resilient reflow.</sub></p>

The repository contains two framework-agnostic companion Agent Skills and a thin Codex plugin wrapper. The Skills remain the single source of workflow truth: `Adaptive-UI-S` is the standard workflow, while `Adaptive-UI-N` adds a required, scoped post-change style audit.

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

- `Adaptive-UI-S`: standard audit-only, implementation, and verification work, plus a user-requested final audit after intermittent work.
- `Adaptive-UI-N`: UI implementation followed by a mandatory audit of this task's changed files and directly related styles.
- Explicit-only activation: an installed Skill, a matching request, or a previous invocation never enables either Skill for a later message.
- Responsive layout review for containers, grid, flex, intrinsic sizing, overflow, zoom, media, tables, and viewport behavior.
- Optional visual-hierarchy guidance when component radius consistency is in scope; existing design tokens win.
- Keyboard, focus, navigation, target-size, motion, forced-color, and text-spacing checks.
- JavaScript simplification: remove viewport-driven sizing, scroll interception, duplicate rendering, autoplay, stale listeners, and unnecessary state.
- Adapters for Vanilla HTML/CSS/JS, React/Next, Vue/Nuxt, SvelteKit, Tailwind, scoped CSS, CSS Modules, preprocessors, and CSS-in-JS.
- A zero-dependency Python auditor with stable rule IDs, confidence labels, suppressions, JSON output, and CI thresholds.
- A standard-library, fail-open update scheduler with absolute next-check times and detailed post-task reminders; no automatic updates.
- Optional browser evidence when the host already provides browser control; no mandatory Playwright installation.

## Package layout

```text
.agents/plugins/marketplace.json
plugins/adaptive-ui-engineer/
├── .codex-plugin/plugin.json
├── assets/
├── hooks/hooks.json
└── skills/
    ├── adaptive-ui-s/
    │   ├── SKILL.md
    │   ├── agents/openai.yaml
    │   ├── release.json
    │   ├── scripts/
    │   │   ├── audit_ui.py
    │   │   └── check_update.py
    │   ├── references/
    │   └── assets/
    └── adaptive-ui-n/
        ├── SKILL.md
        └── agents/openai.yaml
tests/
```

Human-facing project documentation stays at the repository root. `Adaptive-UI-N` deliberately reuses the auditor, update scheduler, release metadata, and references from its sibling `adaptive-ui-s` directory, so the two directories are one installable bundle.

## Installation

### Any Agent Skills-compatible client

Install or copy both directories using the client's supported Skill mechanism, preserving them as siblings:

```text
plugins/adaptive-ui-engineer/skills/adaptive-ui-s
plugins/adaptive-ui-engineer/skills/adaptive-ui-n
```

For clients that scan `$HOME/.agents/skills`, copy both directories there. Do not install `adaptive-ui-n` by itself.

PowerShell:

```powershell
Copy-Item -Recurse -Force `
  .\plugins\adaptive-ui-engineer\skills\adaptive-ui-s `
  "$HOME\.agents\skills\adaptive-ui-s"
Copy-Item -Recurse -Force `
  .\plugins\adaptive-ui-engineer\skills\adaptive-ui-n `
  "$HOME\.agents\skills\adaptive-ui-n"
```

macOS/Linux:

```sh
cp -R plugins/adaptive-ui-engineer/skills/adaptive-ui-s \
  "$HOME/.agents/skills/adaptive-ui-s"
cp -R plugins/adaptive-ui-engineer/skills/adaptive-ui-n \
  "$HOME/.agents/skills/adaptive-ui-n"
```

Client discovery and invocation details vary. A client may discover a Skill from `SKILL.md`; in a manual installation, keep the `adaptive-ui-s` and `adaptive-ui-n` directories together so N can find the bundled auditor, references, and assets in S. When that sibling auditor is absent, N must not claim enhanced completion. `agents/openai.yaml` is an optional Codex presentation extension.

### Codex plugin after the repository is published

```text
codex plugin marketplace add ksukie/adaptive-ui-engineer
codex plugin add adaptive-ui-engineer@adaptive-ui-engineer
```

For local plugin development, add the absolute repository directory as a non-default marketplace, then install the same plugin name. Start a new task after installation so the updated Skill is discovered.

The plugin adds no MCP server, connector, or service credential. It bundles a `UserPromptSubmit` hook only to run the rate-limited update scheduler for an explicit S or N invocation. Codex requires users to review and trust plugin hooks before they run; marketplace installation may also follow the host's normal authentication policy.

## Update

Choose the matching update path. A ZIP download or manually copied Skill does not update itself.

| Previous installation | Update |
| --- | --- |
| Git clone | From the repository directory, run `git pull --ff-only origin main`. Preserve or commit local changes first if Git reports that the worktree is not clean. |
| ZIP download or manual copy | Download or copy the current version, then replace both sibling directories: `plugins/adaptive-ui-engineer/skills/adaptive-ui-s` and `plugins/adaptive-ui-engineer/skills/adaptive-ui-n`. Do not replace only `SKILL.md`. |
| Codex plugin marketplace | Refresh the marketplace, remove the cached plugin, reinstall it, then start a new Codex task. |

For a Codex plugin installed from this marketplace:

```text
codex plugin marketplace upgrade adaptive-ui-engineer
codex plugin remove adaptive-ui-engineer@adaptive-ui-engineer
codex plugin add adaptive-ui-engineer@adaptive-ui-engineer
```

If the marketplace has not been configured yet, run `codex plugin marketplace add ksukie/adaptive-ui-engineer` before installing the plugin.

### Optional update notices

Each explicit S or N invocation can run a non-blocking update scheduler. The first repository check is eligible 72 hours after the installed release time. After a successful check with no newer version, the next check is scheduled 72 hours later. When a newer stable release is found, the task completes first and then reports the installed and latest versions, release dates, subsequent stable-release count, latest bilingual summary, prior/current/next check times, and update guide. The first follow-up is scheduled after 36 hours; each later successful confirmation while the local version remains behind shortens the prior interval by 20% to a 12-hour floor.

`next_check_at` is an earliest eligible time, not a background timer. If the Skill is not used at that time, the check occurs on the first later explicit invocation and the next schedule is based on that actual check time. A failed request does not count as “no update,” does not shorten the reminder interval, and retries silently after 12 hours.

The Codex plugin stores scheduler state in its writable plugin-data directory. A manually copied Skill uses the user's platform state directory when it is writable. The checker sends only a bounded HTTPS GET to the fixed raw release-metadata URL; it does not send prompts, source code, project paths, credentials, or a stable user identifier. It never updates files automatically and never blocks the requested UI task. Set `ADAPTIVE_UI_UPDATE_CHECK=0` or explicitly ask to skip the check to disable it.

### v1.0.0 migration

v1.0.0 replaces the former single `$adaptive-ui-engineer` invocation with two explicit choices. For a manual upgrade from v0.2.1, replace the old `adaptive-ui-engineer` directory rather than leaving it alongside the two new directories; otherwise an outdated third Skill can remain discoverable.

| Former invocation | v1.0.0 replacement |
| --- | --- |
| `$adaptive-ui-engineer` for normal audit, refactor, or a final manual review | `$adaptive-ui-s` |
| `$adaptive-ui-engineer` for UI implementation that must always finish with a scoped style audit | `$adaptive-ui-n` |

## Explicit invocation and modes

In Codex, select one of the bundled Skill labels: `@Adaptive-UI-S` or `@Adaptive-UI-N`. In text-based clients, invoke `$adaptive-ui-s` or `$adaptive-ui-n` in the current message. Some hosts may also show the `Adaptive UI Engineer` plugin parent; it is a container, not a third workflow, so select S or N when the workflow distinction matters.

| Skill | Use it for | Completion behavior |
| --- | --- | --- |
| `Adaptive-UI-S` | Standard responsive UI audits, implementation, refactoring, and a final audit explicitly requested after intermittent work. | Never adds a final audit automatically. A later, explicit S request can audit the named task scope read-only. |
| `Adaptive-UI-N` | A UI implementation, repair, or refactor that must include a final review. | Before reporting completion, audits this task's changed UI files and directly related styles. It does not scan or repair unrelated historical work. |

Both Skills declare explicit-only invocation. In Codex, `allow_implicit_invocation: false` prevents prompt-based implicit invocation; their instructions also reject carrying a past invocation into a later message. After each installation or update, verify the intended per-message contract in a fresh chat: invoke S or N once, then send a matching UI request without `@` or `$` and confirm no implicit Skill is used. If the current message explicitly names both Skills, N takes precedence.

For the canonical S/N comparison and example prompts, consult the bundled
[mode-selection guide](plugins/adaptive-ui-engineer/skills/adaptive-ui-s/references/mode-selection.md).
A question about the modes alone does not activate either workflow or authorize project work.

Examples:

```text
Use $adaptive-ui-s to audit this page for responsive and accessibility issues. Do not edit files.
```

```text
Use $adaptive-ui-s to review the completed checkout task's changed files and directly related styles. Do not edit files.
```

```text
Use $adaptive-ui-n to normalize the card radius hierarchy and remove viewport-driven layout JavaScript, then complete the required post-change style audit.
```

## Static auditor

The auditor is read-only unless `--output` is explicitly supplied.

On Windows, use `py -3` in place of `python` when the `python` command is not registered.

```text
python plugins/adaptive-ui-engineer/skills/adaptive-ui-s/scripts/audit_ui.py <target>
  [--format text|json]
  [--config <file>]
  [--fail-on P0|P1|P2|P3|none]
  [--absolute-paths]
  [--redact-evidence]
  [--output <file>]
```

Examples:

```text
python plugins/adaptive-ui-engineer/skills/adaptive-ui-s/scripts/audit_ui.py ./src --format text --fail-on none
python plugins/adaptive-ui-engineer/skills/adaptive-ui-s/scripts/audit_ui.py ./src --format json --fail-on P1
python plugins/adaptive-ui-engineer/skills/adaptive-ui-s/scripts/audit_ui.py ./src --format json --redact-evidence --output audit.json
```

Exit codes:

| Code | Meaning |
| ---: | --- |
| 0 | Scan completed and the selected threshold was not breached |
| 1 | Scan completed and a finding met the selected threshold |
| 2 | Invalid input, configuration, or output operation |

JSON output uses `schema_version: 2`. Each finding includes `rule_id`, `priority`, `confidence`, `evidence_level`, `validation_state`, `category`, `path`, `line`, `message`, `evidence`, and `recommendation`. `confidence` describes rule certainty, `evidence_level` identifies the evidence origin, and `validation_state` records whether additional validation applies and its outcome. The normative contract is [audit-report.schema.json](plugins/adaptive-ui-engineer/skills/adaptive-ui-s/assets/audit-report.schema.json). Report metadata uses paths relative to the audit root by default; `--absolute-paths` is an explicit opt-in. Evidence can contain short source excerpts, so use `--redact-evidence` before sharing a report when source disclosure is not authorized.

Document-level semantic checks apply to `.html` and `.htm`. Framework component files receive source triage for CSS, scripts, and known utility patterns; rendered semantic behavior still needs runtime verification.

### Configuration

Place `.adaptive-ui-engineer.json` at the audited root or pass `--config`:

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

The bundled schema is at `plugins/adaptive-ui-engineer/skills/adaptive-ui-s/assets/audit-config.schema.json`. Suppressions require a narrow path and a reason; they are counted in output.

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

### Evidence status for 1.1.0

- Locally validated on Windows with Python 3.9, 3.10, and 3.11.
- Unit tests and package checks cover cross-platform path behavior, absolute next-check scheduling, 72-hour no-update intervals, 36-hour update reminders, 20% decay, the 12-hour floor, and failure retries. The repository CI workflow is configured for Windows, macOS, Linux, and Python 3.9–3.13.
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

Read the complete [English disclaimer](DISCLAIMER.md) or [Simplified Chinese translation](DISCLAIMER.zh-CN.md). Adaptive UI Engineer is an independent community project. It is not affiliated with or endorsed by OpenAI, W3C, browser vendors, or the framework vendors named in this documentation. Product names and trademarks belong to their respective owners.
