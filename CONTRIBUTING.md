# Contributing

Thank you for improving AdaptiveUI-SKILL. Contributions should make responsive-interface work more evidence-based, portable, or maintainable without turning the skill into a framework migration tool.

## Development requirements

- Python 3.9 or later for the static auditor and tests.
- No runtime Python packages are required.
- An Agent Skills validator is recommended for structural changes.
- Codex's plugin validator is recommended for plugin manifest changes.

On Windows where `python` is not registered, substitute `py -3` in the commands below.

Run the local suite from the repository root:

```text
python -m unittest discover -s tests -v
```

The reference Agent Skills validator and JSON Schema report validator are CI-only. The Agent Skills source commit and archive digest are fixed in `.github/scripts/run_skills_ref.py`, and all CI-only dependencies are version- and hash-locked in `.github/requirements/skills-ref.txt`; do not add these packages to the runtime auditor. When updating the Agent Skills validator, review the upstream diff and update the commit, archive digest, expected source manifest, tests, and changelog together. Never replace the pin with a branch or mutable tag.

For every stable package release, update `adaptiveui-s/release.json` together with the plugin and auditor versions. Increment `release_sequence` exactly once, use a UTC `released_at` value, keep both summaries to one display-only line, and run the update-scheduler tests before publishing the Raw metadata from the default branch.

Run the auditor manually against a fixture:

```text
python plugins/adaptiveui-skill/skills/adaptiveui-s/scripts/audit_ui.py tests/fixtures/bad --format json --fail-on none
```

## Contribution rules

### Skill instructions

- Keep each `SKILL.md` imperative, focused, and below 500 lines.
- Put detailed domain knowledge in one-level-deep reference files.
- Link every bundled reference, script, or asset from `SKILL.md` or product metadata.
- Keep the description precise enough for positive and negative trigger cases.
- Preserve the explicit-only activation boundary: neither Skill may activate from a matching request or a prior conversation invocation.
- Keep `adaptiveui-n` bounded to task-owned changes and directly related styles; it must not become a whole-repository audit.
- When N edits a file with pre-existing changes, preserve the hunk-level distinction between baseline work and task-owned work in the audit report.

### Auditor rules

Every new rule must include:

- a stable unused `AUI###` identifier;
- a default priority and confidence;
- a bounded source pattern with documented false-positive conditions;
- evidence and a specific recommendation;
- a catalog entry;
- positive, negative, JSON-contract, suppression, and threshold tests.

Do not add a static rule for behavior that can only be established by computed layout, accessibility-tree inspection, or user interaction. Route that requirement to the verification protocol instead.

Treat fixture trees as untrusted input. New filesystem behavior must preserve the audit-root boundary, reject or skip links and reparse points, avoid leaking absolute paths in default reports, cap reads, and keep explicit output safe. Add positive and negative security regression tests for every boundary change.

### Compatibility guidance

- Prefer semantic HTML, resilient CSS, and progressive enhancement.
- Do not add a hard dependency on a framework, browser controller, Node, or network service.
- Keep Windows, macOS, and Linux path handling portable.
- Distinguish designed support, automated tests, manual tests, and untested environments.

### Documentation

Update both `README.md` and `README.en.md` when public behavior changes. Update `CHANGELOG.md` for user-visible changes. Cite primary standards or official framework documentation for normative claims.

### Contribution license and provenance

By submitting a contribution, you agree that it is licensed under the repository's Apache License 2.0. Submit only work that you have the right to license. Identify copied or adapted third-party material, preserve required notices, and do not contribute private source, credentials, generated reports, or assets with unclear rights.

## Review checklist

- The change stays within the skill's responsive UI scope.
- The standard-library auditor remains read-only by default.
- Text and JSON outputs remain deterministic and backward compatible, or the schema version changes.
- Unit tests and package validation pass.
- Release metadata, plugin version, auditor version, scheduler user agent, schema URLs, documentation, and changelog agree.
- No generated caches, reports, browser binaries, credentials, or user project files are included.
- No workflow uses a mutable action tag, and new CI packages are fixed with cryptographic hashes.
- Compatibility and accessibility claims match actual evidence.
