# Security policy

## Supported versions

Security fixes are applied to the latest released minor version. Pre-release versions may receive fixes without backward-compatibility guarantees.

## Reporting a vulnerability

Do not disclose a suspected vulnerability, exploit, private fixture, or credential in a public issue. After this repository is published, use [GitHub's private security advisory flow](https://github.com/ksukie/adaptive-ui-engineer/security/advisories/new) and include:

- the affected version and file;
- a minimal reproduction or malicious input;
- the expected and observed behavior;
- the security impact;
- any proposed mitigation.

If the private advisory flow is unavailable, open a public issue that asks the maintainer to establish private contact, but include no vulnerability details. Maintainers aim to acknowledge a private report within seven days and provide a status update after triage. Do not treat this target as a guaranteed service-level agreement.

## Auditor security boundaries

The bundled auditor:

- is read-only unless the caller explicitly supplies `--output`;
- does not execute scanned code, import project modules, access the network, install packages, or render untrusted HTML;
- scans only regular files with supported interface extensions and a maximum size of 2 MiB;
- rejects a linked target or configuration, skips symbolic links and Windows reparse points inside the tree, and confines local resource checks to the audit root;
- emits root-relative report metadata by default and exposes absolute paths only with `--absolute-paths`;
- writes an explicit output atomically and refuses a linked output destination or existing linked parent component.

Treat generated reports as potentially sensitive. Finding evidence can contain short source excerpts even when paths are relative. Use `--redact-evidence` before sharing a report unless the recipient is authorized to receive the scanned source. Review the result manually because messages, filenames, and recommendations can still reveal project structure.

Do not run third-party project build scripts, browser tests, or package installation merely because the static auditor found an issue. Those actions remain subject to the host agent's permissions and the user's scope.

## Update scheduler security boundaries

The update scheduler is separate from the auditor and runs only for a current explicit Adaptive-UI-S or Adaptive-UI-N invocation when it has not been disabled. The Codex plugin path uses a reviewed `UserPromptSubmit` hook; manually copied Skills can invoke the same standard-library script from their workflow.

The scheduler:

- sends only a bounded HTTPS GET to the fixed Raw GitHub release-metadata path when the persisted absolute next-check time is due;
- does not send prompts, source code, project paths, credentials, machine identifiers, or a stable user identifier;
- accepts only stable `x.y.z` versions, timezone-aware release timestamps, positive release sequences, and one-line bilingual summaries of at most 240 characters;
- treats all remote summaries as display-only data rather than instructions and uses a locally fixed update-guide URL;
- writes update state atomically to the host-provided plugin-data directory or the user's platform state directory, never to the inspected project;
- never downloads executable content, changes installed files, or updates the plugin automatically;
- fails open when state, Python, permissions, or the network is unavailable, without blocking the requested UI task.

Set `ADAPTIVE_UI_UPDATE_CHECK=0` or explicitly ask to skip the check to disable outbound update requests. Plugin-bundled hooks remain subject to the host's review, trust, sandbox, and network controls.

## Threat model and limitations

The boundary controls are designed to prevent an ordinary scanned project from using filesystem links or resource paths to pull unrelated local source into a report. The auditor also avoids shell execution, dynamic evaluation, deserialization formats that construct objects, and runtime network access.

The auditor is not a sandbox. It assumes the Python interpreter and operating system are trusted, and it cannot defend against an administrator or another privileged process that mutates the filesystem concurrently. Its heuristic findings do not prove exploitability, browser behavior, WCAG conformance, or the absence of vulnerabilities.

CI dependencies are not runtime dependencies. Workflow actions are pinned to immutable commits. The CI-only Agent Skills validator is fetched from one source commit, its archive is checked against a fixed SHA-256 digest before extraction, and all transitive Python packages are version- and hash-locked. Dependabot configuration is provided so maintainers can review updates instead of silently following mutable tags.

## Before the first public release

Complete [RELEASE_CHECKLIST.md](RELEASE_CHECKLIST.md), then enable GitHub private vulnerability reporting, Dependabot alerts, secret scanning or push protection when available, and read-only default workflow permissions. Confirm that CodeQL is active after the first workflow run.

This policy and the automated checks are not a formal penetration test, independent security audit, legal opinion, or certification. See the project [Disclaimer](DISCLAIMER.md) for the complete warranty, professional-review, privacy, third-party, and user-responsibility boundaries.
