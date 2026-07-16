# Changelog

All notable changes to this project will be documented in this file. The format follows Keep a Changelog, and versions follow Semantic Versioning.

## [Unreleased]

## [1.1.0] - 2026-07-16

### Added

- Added a standard-library update scheduler shared by Adaptive-UI-S and Adaptive-UI-N. It checks no earlier than the stored absolute next-check time, uses 72-hour no-update intervals, starts update reminders at 36 hours, and shortens later confirmed-reminder intervals by 20% to a 12-hour floor.
- Added compact bilingual release metadata with a stable release sequence so completion notices can report the installed and latest versions, subsequent stable-release count, latest summary, and next scheduled check.
- Added a plugin-bundled `UserPromptSubmit` hook and a portable manual-Skill fallback. Update checks fail open, never update files automatically, and can be disabled with `ADAPTIVE_UI_UPDATE_CHECK=0`.

## [1.0.3] - 2026-07-15

### Added

- Added a shared in-plugin mode-selection guide with S/N comparisons and invocation examples, without adding a third Skill.

## [1.0.2] - 2026-07-15

### Changed

- Made repository-writing and GitHub-publication actions explicit opt-in for both Skills. Completion stays silent about the default unless the user asks or publication status is a real blocker.

## [1.0.1] - 2026-07-15

### Fixed

- Shortened the `Adaptive-UI-N` UI description to the supported metadata length.
- Made N preserve task-owned hunks inside pre-existing modified files instead of excluding the whole file from its required post-change audit.
- Made N stop and request the complete companion bundle when its sibling S auditor is unavailable.

### Changed

- Clarified that the two bundled Skill labels and per-message invocation contract require a live Codex acceptance check after installation or update.

## [1.0.0] - 2026-07-15

### Added

- Added `Adaptive-UI-N`, an explicit-only UI implementation workflow that requires a bounded post-change audit of task-owned files and directly related styles before completion.
- Added a documented v0.2.1-to-v1.0.0 migration path for manual copies and Codex plugin installations.

### Changed

- Replaced the single `Adaptive UI Engineer` Skill with `Adaptive-UI-S` for standard work and `Adaptive-UI-N` for enhanced implementation-and-review work.
- Made both Skills explicit-only per current message; installation, task matching, and earlier conversation invocations no longer activate either workflow.
- Renamed the standard Skill invocation from `$adaptive-ui-engineer` to `$adaptive-ui-s`; `$adaptive-ui-n` is the new enhanced invocation.

## [0.2.1] - 2026-07-15

### Fixed

- Made bundled-auditor instructions resolve the Skill root instead of assuming the caller's working directory.
- Prevented focus-outline decimal values and scoped reduced-motion overrides from producing avoidable static-auditor findings.
- Corrected the configuration-schema identifier and current release documentation.

### Changed

- Documented update paths for Git clones, manual Skill copies, and Codex marketplace installations.

## [0.2.0] - 2026-07-12

### Changed

- Added `confidence`, `evidence_level`, and `validation_state` as separate finding dimensions, with a normative audit-report JSON schema and synchronized text output, rule metadata, documentation, and tests.
- Bumped the audit report schema to version 2.
- Restricted the static auditor to static evidence and validation states, added full Draft 2020-12 report validation in CI, and locked rule-catalog metadata to the implementation.

## [0.1.0] - 2026-07-11

### Added

- Framework-agnostic responsive UI audit, refactor, and verification workflow.
- Codex skill-only plugin and repository marketplace packaging.
- Zero-dependency Python static auditor with stable rule IDs and JSON output.
- Responsive layout, accessibility, compatibility, framework, and verification references.
- Conservative CSS foundation, report template, configuration schema, and brand assets.
- English and Simplified Chinese documentation, test fixtures, and CI workflow configuration.
- Complete English and Simplified Chinese project disclaimers covering warranties, professional advice, certification, privacy, third-party services, trademarks, and user responsibilities.
- First-public-release checklist, Dependabot configuration, and CodeQL workflow.

### Security

- Confined scans to regular files under the audit root by rejecting linked targets and configurations, skipping symbolic links and Windows reparse points, and preventing local resource traversal outside the root.
- Made report metadata root-relative by default, added opt-in evidence redaction and absolute paths, sanitized skipped-file errors, and made explicit output atomic with linked-destination and linked-parent refusal.
- Pinned GitHub Actions to immutable commits, authenticated the fixed Agent Skills validator source archive by SHA-256, and locked every CI-only Python dependency by version and hash.

[Unreleased]: https://github.com/ksukie/adaptive-ui-engineer/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/ksukie/adaptive-ui-engineer/compare/v1.0.3...v1.1.0
[1.0.3]: https://github.com/ksukie/adaptive-ui-engineer/compare/v1.0.2...v1.0.3
[1.0.2]: https://github.com/ksukie/adaptive-ui-engineer/compare/v1.0.1...v1.0.2
[1.0.1]: https://github.com/ksukie/adaptive-ui-engineer/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/ksukie/adaptive-ui-engineer/compare/v0.2.1...v1.0.0
[0.2.1]: https://github.com/ksukie/adaptive-ui-engineer/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/ksukie/adaptive-ui-engineer/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/ksukie/adaptive-ui-engineer/releases/tag/v0.1.0
