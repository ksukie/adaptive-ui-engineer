# Changelog

All notable changes to this project will be documented in this file. The format follows Keep a Changelog, and versions follow Semantic Versioning.

## [Unreleased]

## [0.1.0] - 2026-07-11

### Added

- Framework-agnostic responsive UI audit, refactor, and verification workflow.
- Codex skill-only plugin and repository marketplace packaging.
- Zero-dependency Python static auditor with stable rule IDs and JSON output.
- Responsive layout, accessibility, compatibility, framework, and verification references.
- Conservative CSS foundation, report template, configuration schema, and brand assets.
- English and Simplified Chinese documentation, test fixtures, and future CI workflow.
- Complete English and Simplified Chinese project disclaimers covering warranties, professional advice, certification, privacy, third-party services, trademarks, and user responsibilities.
- First-public-release checklist, Dependabot configuration, and CodeQL workflow.

### Security

- Confined scans to regular files under the audit root by rejecting linked targets and configurations, skipping symbolic links and Windows reparse points, and preventing local resource traversal outside the root.
- Made report metadata root-relative by default, added opt-in evidence redaction and absolute paths, sanitized skipped-file errors, and made explicit output atomic with linked-destination and linked-parent refusal.
- Pinned GitHub Actions to immutable commits, authenticated the fixed Agent Skills validator source archive by SHA-256, and locked every CI-only Python dependency by version and hash.

[Unreleased]: https://github.com/ksukie/adaptive-ui-engineer/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/ksukie/adaptive-ui-engineer/releases/tag/v0.1.0
